"""Checks that keep data/fragments.json, the fragment folders and the built site consistent."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "fragments.json").read_text())

STATUSES = {"identified", "partial", "unidentified"}
CONFIDENCE = {"high", "medium", "low", "none"}
REQUIRED = {"id", "institution", "shelfmark", "catalogue_title", "catalogue_date", "status", "confidence",
            "identification", "note", "verify", "record", "manifest", "thumbnail", "order"}


def test_fields_and_vocabulary():
    for r in DATA:
        assert REQUIRED <= set(r), (r["id"], REQUIRED - set(r))
        assert re.fullmatch(r"F-[a-z0-9]{4}", r["id"]), r["id"]
        assert r["status"] in STATUSES, r["id"]
        assert r["confidence"] in CONFIDENCE, r["id"]
        if r["status"] == "identified":
            assert r["confidence"] == "high", (r["id"], "identified means verified line by line")
        if r["status"] == "unidentified":
            assert r["confidence"] == "none", r["id"]
        for k in ("verify", "record", "manifest", "thumbnail"):
            assert r[k].startswith("https://"), (r["id"], k)


def test_ids_unique_and_ordered():
    ids = [r["id"] for r in DATA]
    assert len(ids) == len(set(ids))
    assert [r["order"] for r in DATA] == sorted(r["order"] for r in DATA)


def test_every_fragment_has_a_folder_and_readme():
    for r in DATA:
        readme = ROOT / "fragments" / r["id"] / "README.md"
        assert readme.exists(), readme
        text = readme.read_text()
        assert r["id"] in text
        assert len(text) > 1500, (r["id"], "README too short to hold a transcription and comparison")
    for folder in (ROOT / "fragments").iterdir():
        if folder.is_dir():
            assert folder.name in {r["id"] for r in DATA}, f"{folder.name} has no data row"


def test_no_local_paths_or_secrets():
    bad = re.compile(r"/Users/|AIza[0-9A-Za-z_-]{20,}|\.mcp\.json")
    for p in list((ROOT / "fragments").rglob("*.md")) + [ROOT / "README.md", ROOT / "METHOD.md", ROOT / "CONVENTIONS.md"]:
        assert not bad.search(p.read_text()), p


def test_site_is_up_to_date():
    subprocess.run([sys.executable, str(ROOT / "docs" / "_build_site.py")], check=True, capture_output=True)
    diff = subprocess.run(["git", "diff", "--exit-code", "--", "docs/"], cwd=ROOT, capture_output=True)
    assert diff.returncode == 0, "docs/ is stale: run python3 docs/_build_site.py and commit"
    for r in DATA:
        assert (ROOT / "docs" / f"{r['id']}.html").exists()
