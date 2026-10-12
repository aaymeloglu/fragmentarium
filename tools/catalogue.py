#!/usr/bin/env python3
"""What Fragmentarium's catalogue already says about a record, as plain text.

    uv run python tools/catalogue.py F-xxxx [F-yyyy ...]

Prints the record's summary fields (title, shelfmark, dimensions, date, reconstruction summary,
canvas labels) from its IIIF manifest and then the full description linked from the record page,
when there is one. The linked description is not in the manifest: a record titled "unidentified"
can have a description that already names its texts, cites an edition or lists sibling records.
Read this before choosing a record and again before research; the result must be about what the
catalogue did not know.

`acquire_batch.py` saves the same text as `catalogue.txt` beside each record's images.
Standard library only.
"""
import html
import json
import re
import sys
import urllib.request

import iiif

SITE = "https://fragmentarium.ms"
SKIP = {"Persistent URL", "Rights", "License"}
MENU = {"Overview", "Facsimile", "Description", "Show TEI/XML", "Download TEI/XML", "Print Description"}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=iiif.UA), timeout=60).read()


def plain(markup):
    """Visible text of an HTML fragment, one line per block."""
    markup = re.sub(r"(?is)<(script|style|nav|header|footer)\b.*?</\1>", " ", markup)
    markup = re.sub(r"(?i)<(br|/p|/div|/li|/tr|/h[1-6]|/dt|/dd)\b[^>]*>", "\n", markup)
    text = html.unescape(re.sub(r"(?s)<[^>]+>", " ", markup))
    lines = [re.sub(r"[ \t\r\f\v]+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line)


def summary(manifest):
    """The manifest's catalogue fields and canvas labels as text."""
    out = [str(manifest.get("label") or "")]
    for item in manifest.get("metadata", []):
        label, value = item.get("label"), item.get("value")
        if label in SKIP:
            continue
        value = plain(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False))
        if value:
            out.append(f"{label}: {' '.join(value.split())}")
    labels = [str(c.get("label")) for c in manifest["sequences"][0]["canvases"]]
    out.append(f"Images ({len(labels)}): " + "; ".join(labels))
    return "\n".join(out)


def description_links(fid, overview_html):
    """Addresses of full descriptions linked from a record page, in page order, without repeats."""
    found = re.findall(r'href="((?:https?://fragmentarium\.ms)?/description/' + re.escape(fid) + r'/\d+)"', overview_html)
    links = []
    for link in found:
        link = link if link.startswith("http") else SITE + link
        if link not in links:
            links.append(link)
    return links


def description_text(page_html):
    """Text of a description page without the site's navigation."""
    body = re.search(r"(?is)<body\b.*", page_html)
    lines = plain(body.group(0) if body else page_html).split("\n")
    return "\n".join(line for line in lines if line not in MENU)


def record(fid, manifest=None, fetch=get):
    """Summary fields plus any linked description, ready to save or print."""
    manifest = manifest or json.loads(fetch(f"{SITE}/metadata/iiif/{fid}/manifest.json"))
    parts = [f"Record: {SITE}/overview/{fid}", summary(manifest)]
    try:
        links = description_links(fid, fetch(f"{SITE}/overview/{fid}").decode("utf-8", "replace"))
    except Exception as error:  # the record page is a convenience; say so and go on
        return "\n\n".join(parts + [f"Linked description: not checked ({error})"])
    if not links:
        parts.append("Linked description: none")
    for link in links:
        try:
            parts.append(f"Linked description: {link}\n" + description_text(fetch(link).decode("utf-8", "replace")))
        except Exception as error:
            parts.append(f"Linked description: {link}\nnot fetched ({error})")
    return "\n\n".join(parts) + "\n"


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        sys.exit(__doc__)
    for fid in argv:
        print(record(fid))


if __name__ == "__main__":
    main(sys.argv[1:])
