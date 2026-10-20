#!/usr/bin/env python3
"""Look up liturgical chant in Cantus Index and the Cantus Database.

For melody-only fragments use cantus_melody.py (see tools/MELODY.md).

    uv run python tools/cantus.py text 'laetare jerusalem'        # standard texts -> Cantus IDs
    uv run python tools/cantus.py cid g00776 [--sources]          # where a chant is used
    uv run python tools/cantus.py next g00776                     # chants that usually follow it
    uv run python tools/cantus.py seq g00800 g00801 g00803        # inventories that have a whole run
    uv run python tools/cantus.py ms 'et conventum facite' [--op starts_with] [--page 2]

Cantus Index gives each chant (antiphon, responsory, introit, gradual, hymn, sequence ...) a
Cantus ID and a standard text. `text` searches those texts: chants that begin with the words
first, then, when that gives fewer than fifty, chants that contain them anywhere. Search whole
words in standard spelling (ae, j, Jerusalem); a word cut at the edge of a strip will not match.

`cid` collects every manuscript in the Cantus Index network (Cantus Database, MMMO, Cantus
Bohemiae, the Austrian, Spanish and other inventories) that has the chant, and counts its
feasts, services and genres. That is how a chant places a fragment: the feast, whether the book
was for the Mass or the Office (MI, M, L, V ...), and how widely the chant was used. `--sources`
lists the manuscripts with folio, century and a link. `next` gives the chants that usually come
after one, for testing what a following line or initial could be. `seq` takes the Cantus IDs of a
run of chants read on a fragment and counts the inventories that have all of them, with their
folios, and those that lack some. A run that hundreds of books share places only the feast; a run
that few share, or a variant some lack, is a lead to a use or region worth comparing on the page.

`ms` searches the manuscript readings entered in the Cantus Database itself (not the rest of the
network), in their own spelling, so it can find a reading that the standard text does not have.

Liturgy is local: most chants occur in many books and many uses, so a chant usually identifies a
feast and kind of book, not a manuscript. Only an unusual chant or a sequence of chants matched
against one inventory narrows the use. Standard library only, no key.
"""
import argparse
import collections
import html
import json
import re
import urllib.parse
import urllib.request

INDEX = "https://cantusindex.org"
DATABASE = "https://cantusdatabase.org"
UA = {"User-Agent": "Mozilla/5.0 (fragmentarium tools)"}


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as response:
        return response.read().decode("utf-8-sig")


def index_json(endpoint, value):
    """A Cantus Index JSON endpoint; the server prefixes its JSON with a byte-order mark."""
    body = fetch(f"{INDEX}/{endpoint}/{urllib.parse.quote(value, safe='')}").lstrip("﻿").strip()
    return json.loads(body) if body else None


def summary(chants):
    """Counts of feast, service and genre over a list of concordance rows."""
    count = lambda key: collections.Counter((row.get(key) or "?").strip() or "?" for row in chants)
    return {"feast": count("feast"), "service": count("office"), "genre": count("genre"), "db": count("db")}


def cell(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def database_rows(page):
    """(siglum, folio, incipit, full text, feast, service, genre, Cantus ID, chant link) per row."""
    body = page[page.find("<tbody"):page.find("</tbody>")]
    for row in re.findall(r"<tr>(.*?)</tr>", body, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if len(cells) < 8:
            continue
        chant = re.search(r'href="(/chant/\d+/)"[^>]*>(.*?)</a>', cells[2], re.S)
        full = re.search(r"<div>(.*?)</div>", cells[2], re.S)
        yield (cell(cells[0]), cell(cells[1]), cell(chant.group(2)) if chant else cell(cells[2]),
               cell(full.group(1)) if full else "", cell(cells[3]), cell(cells[4]), cell(cells[5]),
               cell(cells[7]), DATABASE + chant.group(1) if chant else "")


def text(args):
    for chant in index_json("json-text", args.phrase) or []:
        if args.genre and chant.get("genre") != args.genre:
            continue
        print(f"{chant['cid']}\t{chant.get('genre') or '?'}\t{chant.get('fulltext')}")


def cid(args):
    result = index_json("json-cid", args.cid) or {}
    info, chants = result.get("info") or {}, result.get("chants") or []
    print(f"{args.cid}\t{info.get('field_genre')}\t{info.get('field_feast')}\t{info.get('field_full_text')}")
    print(f"{len(chants)} manuscript entries")
    for key, counts in summary(chants).items():
        print(f"{key}: " + "; ".join(f"{name} {n}" for name, n in counts.most_common(args.top)))
    if args.sources:
        for row in sorted(chants, key=lambda r: (r.get("century") or "99", r.get("siglum") or "")):
            print(f"* {row.get('siglum')} {row.get('folio')} ({row.get('century') or '?'}. c.) "
                  f"{row.get('feast')} {row.get('office') or ''} {row.get('genre')}: {row.get('fulltext') or row.get('incipit')}"
                  f"\n  {row.get('chantlink')}")


def following(args):
    for chant in index_json("json-nextchants", args.cid) or []:
        info = chant.get("info") or {}
        print(f"{chant['cid']}\t{chant.get('count')}\t{info.get('field_genre')}\t{info.get('field_feast')}\t"
              f"{(info.get('field_full_text') or '').strip()}")


def holdings(cids):
    """{siglum: {cid: [folio, ...]}} over the network, with each siglum's source link."""
    held, links = collections.defaultdict(lambda: collections.defaultdict(list)), {}
    for chant_id in cids:
        for row in (index_json("json-cid", chant_id) or {}).get("chants") or []:
            held[row.get("siglum")][chant_id].append(row.get("folio") or "?")
            links.setdefault(row.get("siglum"), row.get("srclink"))
    return held, links


def sequence(args):
    held, links = holdings(args.cids)
    full = sorted(siglum for siglum, chants in held.items() if len(chants) == len(args.cids))
    print(f"{len(held)} inventories have at least one; {len(full)} have all {len(args.cids)}")
    counts = collections.Counter(len(chants) for chants in held.values())
    print("inventories by number held: " + "; ".join(f"{n}: {counts[n]}" for n in sorted(counts, reverse=True)))
    lacking = collections.Counter(c for chants in held.values() if len(chants) >= len(args.cids) - 1
                                  for c in args.cids if c not in chants)
    if lacking:
        print("missing from inventories that lack only one: " + "; ".join(f"{c} {n}" for c, n in lacking.most_common()))
    for siglum in full[:args.show]:
        print(f"* {siglum}: " + " ".join("/".join(held[siglum][c]) for c in args.cids) + f"\n  {links[siglum]}")


def manuscripts(args):
    query = {"keyword": args.phrase, "op": args.op}
    if args.page > 1:
        query["page"] = args.page
    rows = list(database_rows(fetch(f"{DATABASE}/chant-search/?{urllib.parse.urlencode(query)}")))
    print(f"{len(rows)} rows (page {args.page})")
    for siglum, folio, incipit, full, feast, service, genre, chant_id, link in rows:
        print(f"* {siglum} {folio}\t{feast}\t{service}\t{genre}\t{chant_id}\n  {full or incipit}\n  {link}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    one = commands.add_parser("text", help="standard chant texts beginning with or containing the words")
    one.add_argument("phrase")
    one.add_argument("--genre", help="keep one genre code only (A, R, V, H, In, Gr ...)")
    one.set_defaults(run=text)
    one = commands.add_parser("cid", help="manuscripts in the network that have a chant")
    one.add_argument("cid")
    one.add_argument("--sources", action="store_true")
    one.add_argument("--top", type=int, default=8)
    one.set_defaults(run=cid)
    one = commands.add_parser("next", help="chants that usually follow a chant")
    one.add_argument("cid")
    one.set_defaults(run=following)
    one = commands.add_parser("seq", help="inventories that have a whole run of chants")
    one.add_argument("cids", nargs="+")
    one.add_argument("--show", type=int, default=10, help="inventories with all of them to list")
    one.set_defaults(run=sequence)
    one = commands.add_parser("ms", help="manuscript readings in the Cantus Database")
    one.add_argument("phrase")
    one.add_argument("--op", choices=["contains", "starts_with"], default="contains")
    one.add_argument("--page", type=int, default=1)
    one.set_defaults(run=manuscripts)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
