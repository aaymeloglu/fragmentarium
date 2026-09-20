#!/usr/bin/env python3
"""Google Books full-text search, phrase-anchored, for locating a fragment's text in printed editions.

Usage:
    GOOGLE_BOOKS_API_KEY=... python3 tools/gbsearch.py '"phrase one" "phrase two"' ['"next query"' ...]

Prints totalItems and up to 15 hits (title | authors | year | volume id) with the API's snippet.
Snippets carry no page numbers; for a public-domain hit, look for an archive.org mirror of the
same scan (often identifier bub_gb_<volume id>) and check the passage in its OCR.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

KEY = os.environ.get("GOOGLE_BOOKS_API_KEY")
if not KEY:
    sys.exit("set GOOGLE_BOOKS_API_KEY (Google Cloud console: enable the Books API, create an API key)")

for q in sys.argv[1:]:
    url = "https://www.googleapis.com/books/v1/volumes?maxResults=15&key=" + KEY + "&q=" + urllib.parse.quote(q)
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=40))
    except urllib.error.HTTPError as e:
        print("ERR", q, e.code)
        time.sleep(5)
        continue
    print("\n##", q, "->", d.get("totalItems"))
    for it in d.get("items", [])[:15]:
        v = it["volumeInfo"]
        s = it.get("searchInfo", {}).get("textSnippet", "")
        print(" -", v.get("title", "")[:80], "|", ", ".join(v.get("authors", []))[:40], "|", v.get("publishedDate", "")[:4], "|", it.get("id"))
        if s:
            print("     ", s[:300])
    time.sleep(2.5)
