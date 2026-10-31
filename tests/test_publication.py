"""Publication gate, stale-page cleanup and identification date semantics."""
import html
import importlib.util
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("site_builder", ROOT / "docs/_build_site.py")
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


def test_publication_requires_identification_and_high_confidence():
    for status in ('identified', 'partial', 'unidentified'):
        for confidence in ('high', 'medium', 'low', 'none'):
            assert site.publishable(dict(status=status, confidence=confidence)) == (
                status == 'identified' and confidence == 'high')


def test_identifications_already_in_the_literature_are_not_published():
    row = dict(status='identified', confidence='high')
    assert site.publishable(row)
    assert not site.publishable(dict(row, known_from='Edition, 2010'))


def test_index_has_only_identifications_and_original_dates():
    data = json.loads((ROOT / 'data/fragments.json').read_text())
    page = (ROOT / 'docs/index.html').read_text()
    assert 'Date identified' in page
    assert 'Confidence' not in page
    assert 'confidence' not in page
    for row in data:
        link = f'href="{row["id"]}.html"'
        assert (link in page) == site.publishable(row)
        if site.publishable(row):
            rendered = next(part for part in page.split('<tr') if link in part)
            assert f'data-sort="{row["identified_on"]}"' in rendered
            assert f'datetime="{row["identified_on"]}"' in rendered
    assert '<button class="sort" type="button">Date identified' in page


def test_index_rows_are_short_and_filterable():
    data = json.loads((ROOT / 'data/fragments.json').read_text())
    page = (ROOT / 'docs/index.html').read_text()
    assert 'id="q"' in page and 'id="holding"' in page and 'id="kind"' in page
    for row in filter(site.publishable, data):
        rendered = next(part for part in page.split('<tr') if f'href="{row["id"]}.html"' in part)
        assert f'data-kind="{row["kind"]}"' in rendered
        # The evidence note belongs to the report page, not the index.
        assert html.escape(row['note']) not in page
        assert html.escape(row['note']) in (ROOT / f'docs/{row["id"]}.html').read_text()


def test_rebuild_removes_withdrawn_pages_and_allows_ledger_only_attempt(tmp_path, monkeypatch):
    shutil.copytree(ROOT / 'data', tmp_path / 'data')
    shutil.copytree(ROOT / 'fragments', tmp_path / 'fragments')
    docs = tmp_path / 'docs'
    docs.mkdir()
    data_path = tmp_path / 'data/fragments.json'
    data = json.loads(data_path.read_text())
    published = [r for r in data if site.publishable(r)]
    # Distinct dates ensure the initial order is chronological, not report order.
    for i, row in enumerate(published):
        row['identified_on'] = f'2026-09-{i + 1:02d}'
    data_path.write_text(json.dumps(data))
    monkeypatch.setattr(site, 'ROOT', tmp_path)
    monkeypatch.setattr(site, 'DOCS', docs)
    site.build()
    index = (docs / 'index.html').read_text()
    positions = [index.index(f'href="{r["id"]}.html"') for r in reversed(published)]
    assert positions == sorted(positions)

    withdrawn = published[0]
    old_page = docs / f'{withdrawn["id"]}.html'
    assert old_page.exists()
    withdrawn.update(status='partial', confidence='medium', identified_on=None)
    # Neither an unresolved attempt nor a new attempt needs a folder/report.
    shutil.rmtree(tmp_path / 'fragments' / withdrawn['id'])
    data.append(dict(withdrawn, id='F-zzzz', order=999))
    data_path.write_text(json.dumps(data))
    stale = docs / 'F-zzzz.html'
    stale.write_text('obsolete report')
    (docs / 'review.html').write_text('old review links')
    archive = docs / 'runs/before/F-zzzz.html'
    archive.parent.mkdir(parents=True)
    archive.write_text('historical artifact')
    site.build()
    assert not old_page.exists()
    assert not stale.exists()
    assert not (docs / 'review.html').exists()
    assert archive.read_text() == 'historical artifact'
    for page in docs.glob('*.html'):
        assert f'href="{withdrawn["id"]}.html"' not in page.read_text()
