"""Kleiner gecachter Client für die deadcells.wiki.gg MediaWiki-API."""
import hashlib, json, time
from pathlib import Path
import requests

API = "https://deadcells.wiki.gg/api.php"
UA = {"User-Agent": "Mozilla/5.0 (DeadCellsFanGuide research)"}
_last = [0.0]


def _throttle():
    dt = time.time() - _last[0]
    if dt < 0.55:
        time.sleep(0.55 - dt)
    _last[0] = time.time()


def get(url, params=None, binary=False, tries=5):
    for i in range(tries):
        _throttle()
        r = requests.get(url, params=params, headers=UA, timeout=60)
        if r.status_code == 429:
            time.sleep(float(r.headers.get("Retry-After", "5")))
            continue
        if r.status_code >= 500:
            time.sleep(2 * (i + 1))
            continue
        r.raise_for_status()
        return r.content if binary else r.json()
    raise RuntimeError(f"failed: {url} {params}")


def api(cache_dir, params):
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    p = dict(params, format="json", formatversion="2")
    key = hashlib.sha1(json.dumps(p, sort_keys=True).encode()).hexdigest()[:16]
    f = cache_dir / f"api_{key}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    data = get(API, p)
    f.write_text(json.dumps({"params": p, "data": data}, ensure_ascii=False), encoding="utf-8")
    return {"params": p, "data": data}


def wikitext(cache_dir, title):
    d = api(cache_dir, {"action": "parse", "page": title, "prop": "wikitext", "redirects": "1"})["data"]
    if "error" in d:
        return None
    return d["parse"]["wikitext"]


def category(cache_dir, cat):
    d = api(cache_dir, {"action": "query", "list": "categorymembers", "cmtitle": cat, "cmlimit": "500"})["data"]
    return [m["title"] for m in d["query"]["categorymembers"]]


def imageurl(cache_dir, filename):
    d = api(cache_dir, {"action": "query", "titles": f"File:{filename}", "prop": "imageinfo", "iiprop": "url|mime|size"})["data"]
    pages = d["query"]["pages"]
    for pg in pages:
        if pg.get("imageinfo"):
            return pg["imageinfo"][0]
    return None
