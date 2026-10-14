"""Lädt Mechanik-Seiten vom deadcells.wiki.gg (gecacht) und speichert Wikitext als .txt."""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import wikiapi

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "research" / "cache" / "mechanics"
OUT = CACHE / "pages"
OUT.mkdir(parents=True, exist_ok=True)

def search(q, n=10):
    d = wikiapi.api(CACHE, {"action": "query", "list": "search", "srsearch": q, "srlimit": str(n)})["data"]
    return [h["title"] for h in d["query"]["search"]]

def fetch(title):
    wt = wikiapi.wikitext(CACHE, title)
    if wt is None:
        print("MISSING", title); return None
    fn = OUT / (re.sub(r"[^A-Za-z0-9]+", "_", title) + ".txt")
    fn.write_text(wt, encoding="utf-8")
    print("OK", title, len(wt))
    return wt

if __name__ == "__main__":
    mode = sys.argv[1]
    args = sys.argv[2:]
    if mode == "search":
        for q in args:
            print(q, "->", search(q))
    elif mode == "cat":
        for c in args:
            print(c, "->", wikiapi.category(CACHE, c))
    else:
        for t in args:
            fetch(t)
