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
`high`, must bring a report, and gets `identified_on` (kept if already set). `report` is copied to
`fragments/<id>/README.md`; `assisted` is saved as the source-assisted reading `<batch>-source-assisted`,
linked to the first reading `<batch>-image-only`. Paths are relative to the results file. Reports
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

ROOT = Path(__file__).resolve().parents[1]
STATUS = {"identified": {"high"}, "partial": {"medium", "low"}, "unidentified": {"none"}}
LOCAL = re.compile(r"/Users/|/home/|/tmp/|/private/")


def apply(root, results, base, batch, reader, today):
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
            shutil.copy(base / result["report"], root / "fragments" / fid / "README.md")
        row.update(status=status, confidence=confidence, identification=result["identification"],
                   note=result["note"], verify=result.get("verify") or row["record"], examined=today,
                   identified_on=(row.get("identified_on") or today) if status == "identified" else None)
        print(fid, status, confidence)
    ledger_path.write_text(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("results", type=Path)
    ap.add_argument("--batch", required=True, help="reading-name prefix, e.g. batch-2026-10-12b")
    ap.add_argument("--reader", default="research reader with the source at hand")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    a = ap.parse_args()
    apply(ROOT, json.loads(a.results.read_text(encoding="utf-8")), a.results.parent, a.batch, a.reader, a.date)


if __name__ == "__main__":
    main()
