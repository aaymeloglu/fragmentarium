#!/usr/bin/env python3
"""Search inside one Google Books volume and print the printed page number of each hit.

Usage:
    python3 tools/gbwithin.py VOLUME_ID '"phrase one"' ['"phrase two"' ...] [--save responses.json]

The search service's `/gb` endpoint (`tools/searchd.py`) finds which volume holds a phrase; this asks that volume where. It works on
snippet-view books still in copyright, where neither page images nor a full text can be had, and
needs no API key. Each hit gives a page number and about forty words, so a passage can be followed
through an edition by searching again for the last words of the previous snippet. Quote a phrase to
match it exactly; the index keeps the edition's spelling (u for v, e for ae). On a no-preview
volume the service still gives page numbers but empty snippets.

--save writes the raw responses, so a report can cite what the service returned on the day.
A snippet is evidence of the printed wording and page, not a reading of the page: say so.
"""
import argparse
import html
import json
import re
import time
import urllib.parse
import urllib.request

ENDPOINT = "https://books.google.com/books"


def url(volume, query):
    return ENDPOINT + "?" + urllib.parse.urlencode(
        {"id": volume, "q": query, "jscmd": "SearchWithinVolume", "pg": "PP1"})


def clean(snippet):
    """The service marks hits with <b> and escapes quotes as entities; return plain text."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", snippet)).split())


def hits(response):
    """(page number, snippet) for each result; page is '' where the service gives none."""
    return [(str(r.get("page_number", "")), clean(r.get("snippet_text", "")))
            for r in response.get("search_results", [])]


def fetch(volume, query):
    req = urllib.request.Request(url(volume, query), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        kind, body = r.headers.get_content_type(), r.read()
    if kind != "application/json":
        raise SystemExit(f"gbwithin: expected JSON from {ENDPOINT}, got {kind}; "
                         "the service has changed its interface")
    return json.loads(body)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("volume", help="Google Books volume id, e.g. tWdJAAAAYAAJ")
    ap.add_argument("queries", nargs="+")
    ap.add_argument("--save", help="write the raw responses to this JSON file")
    a = ap.parse_args()
    saved = []
    for i, q in enumerate(a.queries):
        if i:
            time.sleep(1.5)
        d = fetch(a.volume, q)
        saved.append({"query": q, "response": d})
        print(f"\n## {q} -> {d.get('number_of_results', 0)}")
        for (page, text), r in zip(hits(d), d.get("search_results", [])):
            where = f"p. {page}" if page else f"leaf {r.get('page_id', '?')}"
            print(f"  {where} | {text or '(no snippet)'}")
    if a.save:
        record = {"volume": a.volume, "endpoint": ENDPOINT,
                  "retrieved": time.strftime("%Y-%m-%d", time.gmtime()), "results": saved}
        with open(a.save, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=1)
            f.write("\n")


if __name__ == "__main__":
    main()
