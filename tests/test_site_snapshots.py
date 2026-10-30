"""Saved research results must survive later rebuilds without drifting."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.hrefs.extend(value for name, value in attrs if name == "href")


def test_before_snapshot_preserves_pages_and_internal_navigation():
    ids = {row["id"] for row in json.loads((ROOT / "data/fragments.json").read_text())}
    directory = ROOT / "docs/runs/before-2026-09-22"
    manifest = json.loads((directory / "snapshot.json").read_text())
    snapshot_ids = {path.stem for path in directory.glob("F-*.html")}
    assert snapshot_ids <= ids
    assert len(snapshot_ids) == 22
    assert set(manifest["files"]) == {path.name for path in directory.glob("*.html")}
    for name, hashes in manifest["files"].items():
        path = directory / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == hashes["snapshot_sha256"], path
        text = path.read_text()
        assert "/blob/main/" not in text and "/tree/main/" not in text
        links = Links()
        links.feed(text)
        for href in links.hrefs:
            parsed = urlsplit(href)
            if not parsed.scheme and parsed.path:
                assert (directory / parsed.path).resolve().is_file(), (path, href)
        if name == "index.html":
            assert all(f"{fid}.html" in links.hrefs for fid in snapshot_ids)


def test_markdown_links_tables_and_lists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_site", Path(__file__).resolve().parent.parent / "docs" / "_build_site.py")
    site = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(site)
    out = site.inline("[fol. [1]r](https://x.org/a.jpg) and [W](https://w.org/M_(gest._1523))")
    assert out == '<a href="https://x.org/a.jpg">fol. [1]r</a> and <a href="https://w.org/M_(gest._1523)">W</a>'
    out = site.inline("[FIRST_READINGS.md](../../FIRST_READINGS.md), reading [1601](?)", "fragments/F-xxxx")
    assert out == f'<a href="{site.REPO}/blob/main/FIRST_READINGS.md">FIRST_READINGS.md</a>, reading [1601](?)'
    table = site.md_to_html("| a | b |\n|---|---|\n| x | sac\\|rum |")
    assert table.count("<td>") == 2 and "sac|rum" in table
    nested = site.md_to_html("- top\n  - sub\n- next")
    assert nested == "<ul><li>top<ul><li>sub</li></ul></li><li>next</li></ul>"
