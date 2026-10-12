#!/usr/bin/env python3
"""Search the Corpus Middelnederlands (Dutch Language Institute) for a phrase.

    uv run python tools/mnlsearch.py 'versamenden sanghe' [--n 25] [--context 40]
    uv run python tools/mnlsearch.py --cql '"eendrachtigh.*" []{0,2} "sangh?e"'

The corpus holds the texts of the CD-ROM Middelnederlands, about 370 Middle Dutch works in verse
and prose (romances, saints' lives, Bible translations, devotional and practical texts), and is
searched word by word. A plain phrase is turned into a sequence of exact words; put `.*` in a word
for an unknown ending or beginning (`sachtmo.*`), and use --cql for gaps and alternatives in the
server's own query language (Corpus Query Language: one quoted pattern per word, `[]` for any
word, `{0,2}` for a count).

Spelling is not normalised: search the manuscript's spelling and the likely variants (ij/y, c/k,
gh/g, uu/w, ae/a). Each hit gives the work's title and the words around the match. A hit is a
lead; no hit shows only that the wording is not in these editions. Standard library only, no key.
"""
import argparse
import json
import urllib.parse
import urllib.request

API = "https://corpusmiddelnederlands.ivdnt.org/blacklab-server/MNL/hits"
UA = {"User-Agent": "Mozilla/5.0 (fragmentarium tools)"}


def cql(phrase):
    """A plain phrase as a sequence of whole words, case ignored; `.*` and other regex pass through."""
    words = phrase.replace('"', " ").split()
    if not words:
        raise ValueError("empty phrase")
    return " ".join('"(?i)%s"' % word for word in words)


def search(pattern, number=25, context=40):
    query = urllib.parse.urlencode({"patt": pattern, "outputformat": "json", "number": number, "wordsaroundhit": context})
    with urllib.request.urlopen(urllib.request.Request(f"{API}?{query}", headers=UA), timeout=90) as response:
        return json.load(response)


def rows(result):
    """(title, left, match, right) for each hit of a server response."""
    docs = result.get("docInfos", {})
    words = lambda part: " ".join(part.get("word", []))
    for hit in result.get("hits", []):
        info = docs.get(hit.get("docPid"), {})
        title = (info.get("title") or info.get("titleLevel1") or [""])[0]
        yield title, words(hit.get("left", {})), words(hit.get("match", {})), words(hit.get("right", {}))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("phrase", nargs="?")
    parser.add_argument("--cql", help="a query in Corpus Query Language, used as given")
    parser.add_argument("--n", type=int, default=25)
    parser.add_argument("--context", type=int, default=40, help="words shown on each side")
    args = parser.parse_args()
    if bool(args.phrase) == bool(args.cql):
        parser.error("give a phrase or --cql, not both")
    pattern = args.cql or cql(args.phrase)
    result = search(pattern, args.n, args.context)
    if "error" in result:
        raise SystemExit(f"{pattern}\n{result['error']}")
    print(pattern)
    print("hits:", result.get("summary", {}).get("numberOfHits"))
    for title, left, match, right in rows(result):
        print(f"* {title}\n  {left} [[{match}]] {right}")


if __name__ == "__main__":
    main()
