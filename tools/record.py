#!/usr/bin/env python3
"""Record research results in the ledger, and install the report of an identification.

    uv run python tools/record.py results.json --batch batch-2026-10-12b --reader 'model, role'

`results.json` maps fragment ids to results:

    {"F-xxxx": {"status": "partial", "confidence": "medium",
                "identification": "...", "note": "...", "verify": "https://..."},
     "F-yyyy": {"status": "identified", "confidence": "high", "identification": "...", "note": "...",
                "verify": "https://...", "report": "F-yyyy.README.md", "assisted": "F-yyyy.assisted.txt",
                "sources": ["Edition, pp. 1-2"], "reason": "why the reading was revised with the source"}}

Every result updates the fragment's ledger row and sets `examined`. An identified result must be
`high`, must bring a report and a `kind` (one of `KINDS`, the site's filter; an archival document is
`document`), and gets `identified_on` (kept if already set). `report` is copied to
`fragments/<id>/README.md`; `assisted` is saved as the source-assisted reading `<batch>-source-assisted`,
linked to the first reading `<batch>-image-only`. An identified result whose identification the
scholarship had already published for this fragment carries `known_from` (the citation): it is
recorded like any other and kept off the site and out of its count. An archival document carries
`"document": true` (its `verify` is a record of the act, labelled as such on the site). `thumbnail_canvas`
points the thumbnail at that canvas of the manifest (cached by `acquire_batch.py`, else fetched),
for records whose first canvas is the back. A report already at `fragments/<id>/README.md` is left
in place. Paths are relative to the results file. Reports
and readings are refused if they contain a local path. Rebuild the site afterwards
(`docs/_build_site.py`). Standard library only.
"""
import argparse
import datetime
import json
import re
import shutil
from pathlib import Path

import readings
import register

ROOT = Path(__file__).resolve().parents[1]
STATUS = {"identified": {"high"}, "partial": {"medium", "low"}, "unidentified": {"none"}}
KINDS = {"theology", "law", "science", "arts", "liturgy", "document"}
LOCAL = re.compile(r"/Users/|/home/|/tmp/|/private/")


def manifest_of(fid, row, cache):
    path = Path(cache) / fid / "manifest.json" if cache else None
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    import urllib.request
    with urllib.request.urlopen(row["manifest"], timeout=60) as r:
        return json.load(r)


def apply(root, results, base, batch, reader, today, cache=None):
    ledger_path = root / "data" / "fragments.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in ledger}
    for fid, result in results.items():
        row = rows[fid]
        status, confidence = result["status"], result["confidence"]
        if confidence not in STATUS[status]:
            raise ValueError(f"{fid}: {status} cannot have confidence {confidence}")
        if status == "identified" and not result.get("report"):
            raise ValueError(f"{fid}: an identification needs a report")
        kind = "document" if result.get("document") else result.get("kind")
        if status == "identified" and kind not in KINDS:
            raise ValueError(f"{fid}: an identification needs a kind, one of {sorted(KINDS)}")
        for key in ("report", "assisted"):
            if result.get(key) and LOCAL.search((base / result[key]).read_text(encoding="utf-8")):
                raise ValueError(f"{fid}: {key} contains a local path")
        if result.get("assisted"):
            target = root / "fragments" / fid / "readings" / f"{batch}-source-assisted.json"
            if not target.exists():
                readings.revise(root, argparse.Namespace(
                    fragment=fid, name=f"{batch}-source-assisted", first=f"{batch}-image-only",
                    text=base / result["assisted"], reader=reader,
                    source=result["sources"], reason=result["reason"]))
        if result.get("report"):
            (root / "fragments" / fid).mkdir(parents=True, exist_ok=True)
            target = root / "fragments" / fid / "README.md"
            if not (target.exists() and target.resolve() == (base / result["report"]).resolve()):
                shutil.copy(base / result["report"], target)
        row.update(status=status, confidence=confidence, identification=result["identification"],
                   note=result["note"], verify=result.get("verify") or row["record"], examined=today,
                   identified_on=(row.get("identified_on") or today) if status == "identified" else None)
        if status == "identified":
            row["kind"] = kind
        else:
            row.pop("kind", None)
        if result.get("document"):
            row["document"] = True
        elif "document" in result:
            row.pop("document", None)
        if result.get("thumbnail_canvas") is not None:
            row["thumbnail"] = register.thumbnail(manifest_of(fid, row, cache), result["thumbnail_canvas"])
        if status == "identified" and result.get("known_from"):
            row["known_from"] = result["known_from"]
        else:
            row.pop("known_from", None)
        print(fid, status, confidence)
    ledger_path.write_text(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("results", type=Path)
    ap.add_argument("--batch", required=True, help="reading-name prefix, e.g. batch-2026-10-12b")
    ap.add_argument("--reader", default="research reader with the source at hand")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--cache", help="image cache holding manifests (default: the shared image cache)")
    a = ap.parse_args()
    if not a.cache:
        import iiif
        a.cache = str(iiif.cache_dir())
    apply(ROOT, json.loads(a.results.read_text(encoding="utf-8")), a.results.parent, a.batch, a.reader, a.date,
          a.cache)


if __name__ == "__main__":
    main()
