"""HTR provenance and raw/derived text boundaries; no model download in ordinary CI."""
import argparse
import json
from pathlib import Path
import sys
from xml.sax.saxutils import escape

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import htr
import readings


def page_xml(text='q\u0303  test', with_line=True):
    line = (f'<TextLine id="line-a"><Coords points="0,0 10,0 10,10 0,10"/>'
            f'<Word><TextEquiv><Unicode>do not duplicate</Unicode></TextEquiv></Word>'
            f'<TextEquiv><Unicode>{escape(text)}</Unicode></TextEquiv></TextLine>') if with_line else ''
    return ('<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15">'
            '<Page imageFilename="image-001.jpg" imageWidth="20" imageHeight="20">'
            f'<TextRegion>{line}</TextRegion></Page></PcGts>')


def sample_run(raw=None):
    raw = page_xml() if raw is None else raw
    page = {'name': 'image-001.jpg', 'image_sha256': 'a' * 64,
            'page_xml': raw, 'xml_sha256': readings.sha(raw.encode())}
    run = {'format': 'kraken-catmus-v1', 'created_at': '2026-09-22T00:00:00+00:00',
           'engine': {'kraken': '7.1.1', 'python': '3.13', 'platform': 'test', 'machine': 'test',
                      'packages': {'kraken': '7.1.1'}},
           'settings': {'device': 'cpu', 'threads': 1, 'segmentation': 'baseline',
                        'subline_segmentation': False, 'preprocessing': 'none'},
           'models': htr.model_lock(), 'pages': [page], 'warnings': []}
    run['text'] = htr.transcript(run['pages'])
    return run


def test_raw_line_text_preserved_without_word_duplication():
    run = sample_run()
    htr.validate_run(run)
    assert run['text'] == 'image-001.jpg:L001: q\u0303  test\n'
    assert htr.lines(run['pages'][0])[0]['xml_id'] == 'line-a'


@pytest.mark.parametrize('change', ['xml', 'text', 'image', 'version'])
def test_inconsistent_run_is_rejected(change):
    run = sample_run()
    if change == 'xml':
        run['pages'][0]['page_xml'] = page_xml('replaced')
    elif change == 'text':
        run['text'] = 'silently expanded'
    elif change == 'image':
        run['pages'][0]['name'] = 'image-002.jpg'
    else:
        run['engine']['kraken'] = 'different version'
    with pytest.raises(ValueError):
        htr.validate_run(run)


def make_fragment(root):
    folder = root / 'fragments' / 'F-test'
    folder.mkdir(parents=True)
    (folder / 'README.md').write_text('# F-test')


def test_htr_freezes_without_false_llm_attestation_and_revises(tmp_path):
    make_fragment(tmp_path)
    run = tmp_path / 'run.json'
    run.write_bytes(readings.encoded(sample_run()))
    args = argparse.Namespace(fragment='F-test', name='htr-01', run=run,
                             purpose='tool-validation', image_source=['https://example.org/image.jpg'])
    saved = readings.freeze_htr(tmp_path, args)
    original = saved.read_bytes()
    record = json.loads(original)
    assert record['kind'] == 'htr' and 'isolation_attested' not in record
    assert record['htr']['pages'][0]['page_xml'] == page_xml()
    with pytest.raises(FileExistsError):
        readings.freeze_htr(tmp_path, args)
    response = tmp_path / 'assisted.txt'
    response.write_text('quod [proposed expansion]')
    readings.revise(tmp_path, argparse.Namespace(fragment='F-test', name='assisted-01', first='htr-01',
                    text=response, reader='test reviewer', source=['Test edition'], reason='Expansion'))
    assert readings.check(tmp_path) == 2
    assert saved.read_bytes() == original


@pytest.mark.parametrize('raw', [page_xml(with_line=False), page_xml('')])
def test_empty_segmentation_or_recognition_cannot_be_frozen(tmp_path, raw):
    make_fragment(tmp_path)
    run = tmp_path / 'run.json'
    run.write_bytes(readings.encoded(sample_run(raw)))
    with pytest.raises(ValueError, match='zero lines or entirely empty'):
        readings.freeze_htr(tmp_path, argparse.Namespace(fragment='F-test', name='htr-01', run=run,
                           purpose='tool-validation', image_source=['https://example.org/image.jpg']))
    assert not (tmp_path / 'fragments' / 'F-test' / 'readings').exists()


def test_expansions_and_search_forms_cannot_overwrite_raw(tmp_path):
    run = tmp_path / 'run.json'
    run.write_bytes(readings.encoded(sample_run()))
    original = run.read_bytes()
    edits = tmp_path / 'expansions.json'
    edits.write_text(json.dumps({'image-001.jpg:L001': {
        'text': 'quod   test?', 'uncertain': True, 'basis': 'Proposed from the image; not resolved'}}))
    out = tmp_path / 'layers.json'
    htr.derive_layers(run, edits, out)
    line = json.loads(out.read_text())['lines'][0]
    assert line['raw'] == 'q\u0303  test'
    assert line['proposed_expansion']['uncertain'] is True
    assert line['search_text'] == 'quod test?' and line['search_basis'] == 'proposed_expansion'
    assert run.read_bytes() == original
    with pytest.raises(FileExistsError):
        htr.derive_layers(run, edits, out)
    edits.write_text('{"unknown-line": {}}')
    with pytest.raises(ValueError, match='Unknown expansion line IDs'):
        htr.derive_layers(run, edits, tmp_path / 'bad.json')


def test_no_expansion_is_invented(tmp_path):
    run = tmp_path / 'run.json'
    run.write_bytes(readings.encoded(sample_run()))
    edits = tmp_path / 'expansions.json'
    edits.write_text('{}')
    out = tmp_path / 'layers.json'
    htr.derive_layers(run, edits, out)
    line = json.loads(out.read_text())['lines'][0]
    assert line['proposed_expansion'] is None and line['search_basis'] == 'raw'
    assert line['search_text'] == 'q\u0303 test'


def test_wrong_weights_are_rejected(tmp_path):
    model = tmp_path / 'model.mlmodel'
    model.write_bytes(b'wrong weights')
    with pytest.raises(ValueError, match='checksum mismatch'):
        htr.verified(model, 'a' * 64)


def test_review_escapes_recognition_and_shows_line_polygons(tmp_path):
    run = sample_run(page_xml('<script>alert(1)</script>'))
    out = tmp_path / 'review.html'
    htr.render_review(run, out)
    page = out.read_text()
    assert '<script>' not in page and '&lt;script&gt;' in page
    assert '<polygon points="0,0 10,0 10,10 0,10">' in page
    assert 'images/image-001.jpg' in page
