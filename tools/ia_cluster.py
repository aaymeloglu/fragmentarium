#!/usr/bin/env python3
"""Find ordered anchor passages in an archive.org volume's OCR.

    python3 tools/ia_cluster.py IDENTIFIER "phrase one" "phrase two" --show
    python3 tools/ia_cluster.py IDENTIFIER --query query.json --max-edits 1 --json

Uses the shared Latin retrieval engine; see RETRIEVAL.md. Scores select candidates,
not identifications. --window bounds the complete original-text passage span.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import latin_search

CACHE = Path.home() / ".cache" / "fragmentarium"
UA = {"User-Agent": "Mozilla/5.0 (fragmentarium tools)"}


def ocr_text(ident, cache=CACHE):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", ident):
        raise ValueError("Invalid Internet Archive identifier")
    p = cache / f"{ident}.txt"
    if p.exists() and p.stat().st_size > 1000:
        return p.read_bytes().decode("utf-8", "replace")
    files = json.load(urllib.request.urlopen(urllib.request.Request(f"https://archive.org/metadata/{ident}/files", headers=UA), timeout=60))["result"]
    names = [f["name"] for f in files if f["name"].endswith("_djvu.txt")]
    if not names:
        sys.exit(f"{ident}: no _djvu.txt (OCR missing or access-restricted)")
    url = f"https://archive.org/download/{ident}/{urllib.parse.quote(names[0])}"
    data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600).read()
    if len(data) < 1000 or b"<html" in data[:200].lower():
        sys.exit(f"{ident}: OCR download refused ({len(data)} bytes); volume may be lending-only")
    cache.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return data.decode("utf-8", "replace")



def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('identifier')
    parser.add_argument('phrases', nargs='*')
    parser.add_argument('--query', type=Path)
    parser.add_argument('--window', type=int, default=6000)
    parser.add_argument('--max-edits', type=int, default=0)
    parser.add_argument('--ocr-long-s', action='store_true')
    parser.add_argument('--limit', type=int, default=3)
    parser.add_argument('--cache-dir', type=Path, default=CACHE)
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    if bool(args.phrases) == bool(args.query):
        parser.error('Supply phrases or --query, but not both')
    try:
        query = json.loads(latin_search.read_utf8(args.query)) if args.query else latin_search.literal_query(args.phrases)
        text = ocr_text(args.identifier, args.cache_dir)
        result = latin_search.search([{'id': args.identifier, 'source': f'https://archive.org/details/{args.identifier}',
                                       'text': text}], query, args.max_edits, args.window, args.limit, args.ocr_long_s)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        doc = result['documents'][0]
        for anchor in query['anchors']:
            suffix = ' (common; excluded from ranking)' if anchor.get('common') else ''
            print(f"{doc['hit_counts'][anchor['id']]:4d}  {anchor['id']}{suffix}")
        for passage in doc['passages']:
            print(f"@{passage['start']}:{passage['end']}: ordered coverage "
                  f"{passage['matched']}/{passage['diagnostic_total']}; retrieval score {passage['score']}")
            for match in passage['matches']:
                print(f"  {match['anchor']} variant {match['variant']}: {match['mode']}, "
                      f"edits={match['edits']}, line={match['line']}, @{match['start']}:{match['end']}")
            if args.show:
                print(text[passage['start']:passage['end']])
        if not doc['passages']:
            print('No diagnostic passage found; this does not exclude the work.')
        print('Candidate retrieval only: inspect the manuscript and edition images.')
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
