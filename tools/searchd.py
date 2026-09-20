#!/usr/bin/env python3
"""Local search service for fragment identification. Holds the Google Books key in one process
and answers on localhost, so worker sessions never touch the key.

    GOOGLE_BOOKS_API_KEY=... python3 tools/searchd.py [--port 8790]

Endpoints (GET, JSON back):
    /gb?q=<quoted phrases>            Google Books full text: totalItems + hits (title, authors, year, id, snippet)
    /ia?q=<quoted phrases>            archive.org full-text search: identifiers + highlights
    /cc?q=<sphinx query>&index=p      Corpus Corporum (mlat.uzh.ch), supports NEAR/N; sentence index 's' or paragraph 'p'
    /health

Pacing: Google Books calls are spaced 2.5 s apart process-wide; results are cached in memory for
the life of the process. Binds to 127.0.0.1 only. Standard library only.
"""
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

KEY = os.environ.get("GOOGLE_BOOKS_API_KEY")
UA = {"User-Agent": "Mozilla/5.0 (fragmentarium searchd)"}
LOCK = threading.Lock()
LAST_GB = [0.0]
CACHE = {}


def get_json(url, timeout=60):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout))


def gb(q):
    if not KEY:
        return {"error": "GOOGLE_BOOKS_API_KEY not set in the service process"}
    with LOCK:
        wait = 2.5 - (time.time() - LAST_GB[0])
        if wait > 0:
            time.sleep(wait)
        LAST_GB[0] = time.time()
    d = get_json("https://www.googleapis.com/books/v1/volumes?maxResults=15&key=" + KEY + "&q=" + urllib.parse.quote(q))
    hits = []
    for it in d.get("items", []):
        v = it["volumeInfo"]
        hits.append({"title": v.get("title", "")[:120], "authors": v.get("authors", []), "year": v.get("publishedDate", "")[:4],
                     "id": it.get("id"), "snippet": it.get("searchInfo", {}).get("textSnippet", "")})
    return {"query": q, "totalItems": d.get("totalItems", 0), "hits": hits}


def ia(q):
    d = get_json("https://be-api.us.archive.org/fts/v1/search?q=" + urllib.parse.quote(q) + "&size=15", timeout=90)
    hits = []
    for h in d.get("hits", {}).get("hits", []):
        f = h.get("fields", {})
        hits.append({"identifier": f.get("identifier"), "title": f.get("title"), "highlights": h.get("highlight", {}).get("text", [])[:3]})
    return {"query": q, "total": d.get("hits", {}).get("total"), "hits": hits}


def cc(q, index="p"):
    url = ("https://mlat.uzh.ch/php_modules/fulltext_search.php?&query=" + urllib.parse.quote(q)
           + "&offset=0&limit=30&order_by=&index_type=" + index)
    t = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read().decode("utf-8", "replace")
    total = re.search(r"<total>(\d+)</total>", t)
    hits = []
    for r in re.findall(r'<search_result n="\d+">(.*?)</search_result>', t, re.S):
        names = re.findall(r"<name>(.*?)</name>", r, re.S)
        year = re.search(r"<decisive_year>(.*?)</decisive_year>", r)
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", " ".join(re.findall(r"<sentence[^>]*>(.*?)</sentence>", r, re.S))))
        hits.append({"author": names[0] if names else None, "work": names[1] if len(names) > 1 else None,
                     "year": year.group(1) if year else None, "text": txt[:400]})
    return {"query": q, "index": index, "total": int(total.group(1)) if total else None, "hits": hits}


class H(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002
        sys.stderr.write("%s %s\n" % (time.strftime("%H:%M:%S"), format % args))

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(u.query)
        q = (qs.get("q") or [""])[0]
        key = (u.path, q, (qs.get("index") or ["p"])[0])
        try:
            if u.path == "/health":
                body = {"ok": True, "google_books_key": bool(KEY)}
            elif key in CACHE:
                body = CACHE[key]
            elif u.path == "/gb":
                body = CACHE[key] = gb(q)
            elif u.path == "/ia":
                body = CACHE[key] = ia(q)
            elif u.path == "/cc":
                body = CACHE[key] = cc(q, key[2])
            else:
                self.send_error(404)
                return
            data = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:  # report upstream failures as JSON, keep serving
            data = json.dumps({"error": str(e)[:300], "query": q}).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)


if __name__ == "__main__":
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8790
    print(f"searchd on http://127.0.0.1:{port}  (google books key: {'yes' if KEY else 'NO'})", file=sys.stderr)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
