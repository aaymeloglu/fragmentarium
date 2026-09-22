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


def test_snapshots_preserve_pages_and_internal_navigation():
    ids = {row["id"] for row in json.loads((ROOT / "data/fragments.json").read_text())}
    runs = ROOT / "docs/runs"
    for slug in ("before-2026-09-22", "after-2026-09-22"):
        directory = runs / slug
        manifest = json.loads((directory / "snapshot.json").read_text())
        assert ids == {path.stem for path in directory.glob("F-*.html")}
        assert len(ids) == 22
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
                assert all(f"{fid}.html" in links.hrefs for fid in ids)
