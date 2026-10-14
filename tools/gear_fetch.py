"""Fetch-/Cache-Schicht für build_gear.py (deadcells.wiki.gg MediaWiki-API).

Alles wird unter research/cache/gear/ abgelegt; erneute Läufe laden nichts neu.
Aufruf nur indirekt über tools/build_gear.py (python -I tools/build_gear.py).
"""
import hashlib
import json
import re
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "research" / "cache" / "gear"
API = "https://deadcells.wiki.gg/api.php"
UA = {"User-Agent": "Mozilla/5.0 (DeadCellsFanGuide research)"}
_last = [0.0]
MIN_GAP = 1.0  # Sekunden zwischen Anfragen (andere Agenten nutzen die API parallel)


def _throttle():
    dt = time.time() - _last[0]
    if dt < MIN_GAP:
        time.sleep(MIN_GAP - dt)
    _last[0] = time.time()


def http_get(url, params=None, binary=False, tries=8):
    for i in range(tries):
        _throttle()
        try:
            r = requests.get(url, params=params, headers=UA, timeout=60)
        except requests.RequestException:
            time.sleep(3 * (i + 1))
            continue
        if r.status_code == 429:
            wait = float(r.headers.get("Retry-After", "10") or 10)
            print(f"  429 -> warte {wait}s", flush=True)
            time.sleep(wait + 1)
            continue
        if r.status_code >= 500:
            time.sleep(3 * (i + 1))
            continue
        r.raise_for_status()
        if binary:
            return r.content, r.headers.get("Content-Type", "")
        data = r.json()
        if isinstance(data, dict) and data.get("error", {}).get("code") == "ratelimited":
            print("  ratelimited (json) -> warte 30s", flush=True)
            time.sleep(30)
            continue
        return data
    raise RuntimeError(f"failed: {url} {params}")


def api(params, sub="api"):
    d = CACHE / sub
    d.mkdir(parents=True, exist_ok=True)
    p = dict(params, format="json", formatversion="2")
    key = hashlib.sha1(json.dumps(p, sort_keys=True).encode()).hexdigest()[:16]
    f = d / f"{key}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))["data"]
    data = http_get(API, p)
    f.write_text(json.dumps({"params": p, "data": data}, ensure_ascii=False), encoding="utf-8")
    return data


def safe_name(title):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", title)[:120]


def wikitexts(titles, sub="pages"):
    """Wikitext mehrerer Seiten (Batch à 40, Redirects aufgelöst).
    Rückgabe: {angefragter Titel: (finaler Titel, wikitext|None)}; Cache je Seite."""
    d = CACHE / sub
    d.mkdir(parents=True, exist_ok=True)
    out, todo = {}, []
    for t in dict.fromkeys(titles):
        f = d / (safe_name(t) + ".json")
        if f.exists():
            j = json.loads(f.read_text(encoding="utf-8"))
            out[t] = (j["final"], j["text"])
        else:
            todo.append(t)
    for i in range(0, len(todo), 40):
        chunk = todo[i:i + 40]
        print(f"  lade {len(chunk)} Seiten ({sub}) …", flush=True)
        data = http_get(API, {
            "action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main",
            "titles": "|".join(chunk), "redirects": "1", "format": "json", "formatversion": "2"})
        q = data["query"]
        norm = {n["from"]: n["to"] for n in q.get("normalized", [])}
        redir = {n["from"]: n["to"] for n in q.get("redirects", [])}
        pages = {p["title"]: p for p in q.get("pages", [])}
        for t in chunk:
            fin = norm.get(t, t)
            fin = redir.get(fin, fin)
            pg = pages.get(fin, {})
            text = None
            if pg.get("revisions"):
                text = pg["revisions"][0]["slots"]["main"]["content"]
            out[t] = (fin, text)
            (d / (safe_name(t) + ".json")).write_text(
                json.dumps({"title": t, "final": fin, "text": text}, ensure_ascii=False), encoding="utf-8")
    return out


def resolve_titles(titles):
    """{Titel: kanonischer Titel nach Normalisierung/Redirect (oder None, falls Seite fehlt)}."""
    f = CACHE / "titles.json"
    cache = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    todo = [t for t in dict.fromkeys(titles) if t not in cache]
    for i in range(0, len(todo), 40):
        chunk = todo[i:i + 40]
        print(f"  löse {len(chunk)} Titel auf …", flush=True)
        data = http_get(API, {"action": "query", "titles": "|".join(chunk), "redirects": "1",
                              "format": "json", "formatversion": "2"})
        q = data["query"]
        norm = {n["from"]: n["to"] for n in q.get("normalized", [])}
        redir = {n["from"]: n["to"] for n in q.get("redirects", [])}
        pages = {p["title"]: p for p in q.get("pages", [])}
        for t in chunk:
            fin = norm.get(t, t)
            fin = redir.get(fin, fin)
            pg = pages.get(fin, {})
            cache[t] = None if pg.get("missing") or pg.get("invalid") else fin
        f.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return {t: cache.get(t) for t in titles}


def imageinfos(filenames):
    """{Dateiname: {url, mime, size}|None}; Batch à 40; Cache in imageinfo.json."""
    f = CACHE / "imageinfo.json"
    cache = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    todo = [n for n in dict.fromkeys(filenames) if n not in cache]
    for i in range(0, len(todo), 40):
        chunk = todo[i:i + 40]
        print(f"  imageinfo für {len(chunk)} Dateien …", flush=True)
        data = http_get(API, {
            "action": "query", "prop": "imageinfo", "iiprop": "url|mime|size",
            "titles": "|".join("File:" + n for n in chunk), "redirects": "1",
            "format": "json", "formatversion": "2"})
        q = data["query"]
        norm = {n["from"]: n["to"] for n in q.get("normalized", [])}
        redir = {n["from"]: n["to"] for n in q.get("redirects", [])}
        pages = {p["title"]: p for p in q.get("pages", [])}
        for n in chunk:
            t = "File:" + n
            t = norm.get(t, t)
            t = redir.get(t, t)
            pg = pages.get(t, {})
            ii = pg.get("imageinfo")
            cache[n] = ii[0] if ii else None
        f.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return {n: cache.get(n) for n in filenames}


def download(url):
    content, ctype = http_get(url, binary=True)
    return content, ctype
