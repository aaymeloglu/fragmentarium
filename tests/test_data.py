"""Checks that keep data/fragments.json, the fragment folders and the built site consistent."""
import json
from datetime import date
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "fragments.json").read_text())

STATUSES = {"identified", "partial", "unidentified"}
CONFIDENCE = {"high", "medium", "low", "none"}
REQUIRED = {"id", "institution", "shelfmark", "catalogue_title", "catalogue_date", "status", "confidence",
            "identification", "note", "verify", "record", "manifest", "thumbnail", "order", "examined", "identified_on"}


def test_fields_and_vocabulary():
    for r in DATA:
        assert REQUIRED <= set(r), (r["id"], REQUIRED - set(r))
        assert re.fullmatch(r"F-[a-z0-9]{4}", r["id"]), r["id"]
        assert r["status"] in STATUSES, r["id"]
        assert r["confidence"] in CONFIDENCE, r["id"]
        if r["status"] == "identified":
            assert date.fromisoformat(r["identified_on"]) <= date.fromisoformat(r["examined"])
            assert r["confidence"] == "high", (r["id"], "identified requires high confidence in a sustained textual match")
        else:
            assert r["identified_on"] is None, r["id"]
            assert "known_from" not in r, (r["id"], "known_from belongs to an identified row")
        if r["status"] == "unidentified":
            assert r["confidence"] == "none", r["id"]
        for k in ("verify", "record", "manifest", "thumbnail"):
            assert r[k].startswith("https://"), (r["id"], k)
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["examined"]), (r["id"], "examined must be YYYY-MM-DD")


def test_ids_unique_and_ordered():
    ids = [r["id"] for r in DATA]
    assert len(ids) == len(set(ids))
    assert [r["order"] for r in DATA] == sorted(r["order"] for r in DATA)


def test_published_identifications_have_reports():
    for r in DATA:
        if r["status"] != "identified":
            continue
        readme = ROOT / "fragments" / r["id"] / "README.md"
        assert readme.exists(), readme
        text = readme.read_text()
        assert r["id"] in text
    for folder in (ROOT / "fragments").iterdir():
        if folder.is_dir():
            assert folder.name in {r["id"] for r in DATA}, f"{folder.name} has no data row"


def test_no_local_paths_or_secrets():
    bad = re.compile(r"/Users/|AIza[0-9A-Za-z_-]{20,}|\.mcp\.json")
    for p in (list((ROOT / "fragments").rglob("*.md"))
              + list((ROOT / "fragments").glob("*/readings/*.json"))
              + list((ROOT / "prompts").glob("*.md"))
              + [ROOT / "README.md", ROOT / "METHOD.md", ROOT / "CONVENTIONS.md",
                 ROOT / "AGENTS.md", ROOT / "FIRST_READINGS.md", ROOT / "RETRIEVAL.md"]):
        assert not bad.search(p.read_text()), p


def test_site_is_up_to_date():
    """docs/ must equal a fresh build. Builds into a temp copy so the check is the same locally and in CI."""
    import shutil
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "repo"
        shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache"))
        subprocess.run([sys.executable, str(work / "docs" / "_build_site.py")], check=True, capture_output=True)
        assert (work / "README.md").read_text() == (ROOT / "README.md").read_text(), \
            "README.md is stale: run python3 docs/_build_site.py and commit"
        for p in (work / "docs").glob("*.html"):
            committed = ROOT / "docs" / p.name
            assert committed.exists() and committed.read_text() == p.read_text(), f"docs/{p.name} is stale: run python3 docs/_build_site.py and commit"
    expected = {f"{r['id']}.html" for r in DATA if r['status'] == 'identified' and not r.get('known_from')}
    assert {p.name for p in (ROOT / 'docs').glob('F-*.html')} == expected
    assert not (ROOT / 'docs/review.html').exists()


def test_burndown_page_lists_corpus_and_marks_done():
    import csv
    page = (ROOT / "docs" / "burndown.html").read_text()
    sweeps = sorted((ROOT / "data").glob("unidentified-*.csv"))
    with sweeps[-1].open() as f:
        listed = {r["fragmentarium_id"] for r in csv.DictReader(f) if r.get("scope", "title") == "title"}
    listed |= {r["id"] for r in DATA}  # worked records stay listed after the catalogue retitles them
    assert page.count("<tr>") == len(listed) + 1
    for r in DATA:
        link = f'href="{r["id"]}.html"'
        if r['status'] == 'identified' and not r.get('known_from'):
            assert link in page, r['id']
        else:
            assert link not in page, r['id']
            row = next(row for row in page.split('<tr>') if f'>{r["id"]}</a>' in row)
            assert ('Examined; already identified in the literature' if r.get('known_from')
                    else 'Examined; not identified') in row
    assert 'href="burndown.html"' in (ROOT / "docs" / "index.html").read_text()


def test_tools_parse():
    import ast
    for p in (ROOT / "tools").glob("*.py"):
        ast.parse(p.read_text(), filename=str(p))
