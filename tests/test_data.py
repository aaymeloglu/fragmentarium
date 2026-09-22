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
            "identification", "note", "verify", "record", "manifest", "thumbnail", "order", "examined"}


def test_fields_and_vocabulary():
    for r in DATA:
        assert REQUIRED <= set(r), (r["id"], REQUIRED - set(r))
        assert re.fullmatch(r"F-[a-z0-9]{4}", r["id"]), r["id"]
        assert r["status"] in STATUSES, r["id"]
        assert r["confidence"] in CONFIDENCE, r["id"]
        if r["status"] == "identified":
            assert r["confidence"] == "high", (r["id"], "identified requires high confidence in a sustained textual match")
        if r["status"] == "unidentified":
            assert r["confidence"] == "none", r["id"]
        for k in ("verify", "record", "manifest", "thumbnail"):
            assert r[k].startswith("https://"), (r["id"], k)
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["examined"]), (r["id"], "examined must be YYYY-MM-DD")


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
    for p in (list((ROOT / "fragments").rglob("*.md"))
              + list((ROOT / "fragments").glob("*/readings/*.json"))
              + list((ROOT / "prompts").glob("*.md"))
              + [ROOT / "README.md", ROOT / "METHOD.md", ROOT / "CONVENTIONS.md",
                 ROOT / "REVIEW.md", ROOT / "AGENTS.md", ROOT / "FIRST_READINGS.md", ROOT / "HTR.md"]):
        assert not bad.search(p.read_text()), p


def test_site_is_up_to_date():
    """docs/ must equal a fresh build. Builds into a temp copy so the check is the same locally and in CI."""
    import shutil
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "repo"
        shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache"))
        subprocess.run([sys.executable, str(work / "docs" / "_build_site.py")], check=True, capture_output=True)
        for p in (work / "docs").glob("*.html"):
            committed = ROOT / "docs" / p.name
            assert committed.exists() and committed.read_text() == p.read_text(), f"docs/{p.name} is stale: run python3 docs/_build_site.py and commit"
    for r in DATA:
        assert (ROOT / "docs" / f"{r['id']}.html").exists()


def test_burndown_page_lists_corpus_and_marks_done():
    import csv
    page = (ROOT / "docs" / "burndown.html").read_text()
    with sorted((ROOT / "data").glob("unidentified-*.csv"))[-1].open() as f:
        csv_rows = list(csv.DictReader(f))
    assert page.count("<tr>") == len(csv_rows) + 1
    for r in DATA:
        assert f'href="{r["id"]}.html"' in page, (r["id"], "worked fragment not marked on burndown")
    assert 'href="burndown.html"' in (ROOT / "docs" / "index.html").read_text()


def test_tools_parse():
    import ast
    for p in (ROOT / "tools").glob("*.py"):
        ast.parse(p.read_text(), filename=str(p))
