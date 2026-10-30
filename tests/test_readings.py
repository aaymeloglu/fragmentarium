"""First readings must survive candidate-assisted revision unchanged."""
import argparse
import sys
import json
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import readings


@pytest.fixture
def work(tmp_path):
    fragment = tmp_path / 'fragments' / 'F-test'
    fragment.mkdir(parents=True)
    (tmp_path / 'data').mkdir()
    (tmp_path / 'data/fragments.json').write_text(json.dumps([{'id': 'F-test'}]))
    image = tmp_path / 'proposed-author-and-work.jpg'
    image.write_bytes(b'test image bytes')
    packet = readings.packet(tmp_path / 'packet', [image])
    response = tmp_path / 'response.txt'
    response.write_bytes('image-001.jpg L1: q\u0303 [?]\r\nL2: [illegible]\r\n'.encode('utf-8'))
    args = argparse.Namespace(fragment='F-test', name='first-01', packet=packet,
                             text=response, reader='test reader', session='isolated-test-session',
                             attest_isolated=True, image_source=['https://example.org/iiif/crop.jpg'])
    return tmp_path, args


def assisted(args, **overrides):
    values = dict(fragment=args.fragment, name='assisted-01', first=args.name,
                  text=args.text, reader='test reviewer', source=['Test edition, p. 1'],
                  reason='Test revision after consulting the edition')
    values.update(overrides)
    return argparse.Namespace(**values)


def test_packet_excludes_candidate_filenames_and_preserves_pixels(work):
    root, args = work
    assert sorted(p.name for p in args.packet.iterdir()) == ['PROMPT.md', 'image-001.jpg', 'packet.json']
    assert (args.packet / 'image-001.jpg').read_bytes() == (root / 'proposed-author-and-work.jpg').read_bytes()
    assert 'proposed-author' not in (args.packet / 'packet.json').read_text()
    with pytest.raises(FileExistsError):
        readings.packet(args.packet, [root / 'proposed-author-and-work.jpg'])


def test_first_response_is_exact_and_revision_does_not_replace_it(work):
    root, args = work
    first = readings.freeze(root, args)
    saved = first.read_bytes()
    assert json.loads(saved)['text'].encode('utf-8') == args.text.read_bytes()
    args.text.write_text('image-001.jpg L1: quod [source-assisted expansion]\n')
    revised = readings.revise(root, assisted(args))
    assert first.read_bytes() == saved
    r = json.loads(revised.read_bytes())
    assert r['kind'] == 'source-assisted'
    assert r['first_sha256'] == readings.sha(saved)
    assert r['sources'] == ['Test edition, p. 1']
    assert readings.check(root) == 2
    with pytest.raises(FileExistsError):
        readings.freeze(root, args)
    with pytest.raises(FileExistsError):
        readings.revise(root, assisted(args))


def test_exposure_attestation_is_required(work):
    root, args = work
    args.attest_isolated = False
    with pytest.raises(ValueError, match='attest-isolated'):
        readings.freeze(root, args)
    assert not (root / 'fragments' / 'F-test' / 'readings').exists()


@pytest.mark.parametrize('filename', ['image-001.jpg', 'PROMPT.md'])
def test_changed_packet_is_rejected_before_freezing(work, filename):
    root, args = work
    (args.packet / filename).write_bytes(b'changed')
    with pytest.raises(ValueError, match='changed'):
        readings.freeze(root, args)


def test_image_citations_must_cover_packet(work):
    root, args = work
    args.image_source = []
    with pytest.raises(ValueError, match='one --image-source'):
        readings.freeze(root, args)


def test_revision_requires_sources_and_a_first_reading(work):
    root, args = work
    with pytest.raises(FileNotFoundError):
        readings.revise(root, assisted(args))
    readings.freeze(root, args)
    with pytest.raises(ValueError, match='Source citations'):
        readings.revise(root, assisted(args, source=[]))
    readings.revise(root, assisted(args))
    with pytest.raises(ValueError, match='first image-only'):
        readings.revise(root, assisted(args, name='assisted-02', first='assisted-01'))


def test_checksum_and_revision_reference_detect_edits(work):
    root, args = work
    first = readings.freeze(root, args)
    readings.revise(root, assisted(args))
    r = json.loads(first.read_text())
    r['text'] = 'silently replaced'
    first.write_bytes(readings.encoded(r))
    with pytest.raises(ValueError, match='first reading changed|text checksum mismatch'):
        readings.check(root)
    r['text_sha256'] = readings.sha(r['text'].encode())
    first.write_bytes(readings.encoded(r))
    with pytest.raises(ValueError, match='first reading changed'):
        readings.check(root)


@pytest.mark.parametrize('change', ['edit_and_rehash', 'delete', 'rename'])
def test_committed_readings_are_preserved_against_base(work, change):
    root, args = work
    first = readings.freeze(root, args)
    def git(*argv):
        subprocess.run(['git', *argv], cwd=root, check=True, capture_output=True)
    git('init')
    git('add', 'fragments')
    git('-c', 'user.name=Test', '-c', 'user.email=test@example.org',
        '-c', 'commit.gpgsign=false', 'commit', '-m', 'First reading')
    assert readings.check(root, 'HEAD') == 1
    if change == 'delete':
        first.unlink()
    elif change == 'rename':
        r = json.loads(first.read_text())
        r['id'] = 'renamed'
        first.with_name('renamed.json').write_bytes(readings.encoded(r))
        first.unlink()
    else:
        r = json.loads(first.read_text())
        r['text'] = 'replacement'
        r['text_sha256'] = readings.sha(r['text'].encode())
        first.write_bytes(readings.encoded(r))
    with pytest.raises(ValueError, match='modified or deleted'):
        readings.check(root, 'HEAD')


def test_invalid_base_fails_closed(work):
    root, args = work
    readings.freeze(root, args)
    with pytest.raises(subprocess.CalledProcessError):
        readings.check(root, 'not-a-commit')


def test_repository_readings_validate():
    # Legacy reports need not invent an image-only history.
    readings.check(ROOT)


def test_ledger_registration_required_even_with_a_report(work):
    root, args = work
    (root / 'data/fragments.json').write_text('[]')
    (root / 'fragments/F-test/README.md').write_text('# unregistered')
    with pytest.raises(ValueError, match='Unknown fragment'):
        readings.freeze(root, args)


def test_first_reading_creates_folder_without_report(work):
    root, args = work
    (root / 'fragments/F-test').rmdir()
    first = readings.freeze(root, args)
    assert first.exists()
    assert not (first.parent.parent / 'README.md').exists()
    assert readings.check(root) == 1
    (root / 'data/fragments.json').write_text('[]')
    with pytest.raises(ValueError, match='Unknown fragment'):
        readings.check(root)


def test_freeze_batch_freezes_present_responses_once(work):
    root, args = work
    responses = root / 'responses'
    responses.mkdir()
    (responses / 'packet.txt').write_bytes(args.text.read_bytes())
    mapping = root / 'mapping.json'
    mapping.write_text(json.dumps({'F-test': {'packet': str(args.packet), 'files': [],
                                              'sources': ['https://example.org/iiif/crop.jpg']}}))
    batch = argparse.Namespace(name='batch-image-only', mapping=mapping, responses=responses,
                               reader='test reader', session='batch reader-a', attest_isolated=True)
    saved = readings.freeze_batch(root, batch)
    record = json.loads(saved[0].read_text())
    assert record['text'].encode('utf-8') == args.text.read_bytes() and record['session'] == 'batch reader-a (packet)'
    assert readings.freeze_batch(root, batch) == [], 'a frozen reading is never written twice'


def test_record_updates_ledger_and_installs_only_clean_identifications(work):
    import record
    root, args = work
    args.name = 'b1-image-only'
    readings.freeze(root, args)
    ledger = root / 'data/fragments.json'
    ledger.write_text(json.dumps([{'id': 'F-test', 'record': 'https://fragmentarium.ms/overview/F-test',
                                   'status': 'unidentified', 'confidence': 'none', 'identified_on': None}]))
    out = root / 'out'
    out.mkdir()
    (out / 'r.md').write_text('# F-test: Author, Work\n')
    (out / 'a.txt').write_text('source-assisted reading\n')
    good = {'F-test': {'status': 'identified', 'confidence': 'high', 'identification': 'Author, Work',
                       'note': 'n', 'verify': 'https://example.org/ed', 'report': 'r.md', 'assisted': 'a.txt',
                       'sources': ['Edition, p. 1'], 'reason': 'resolved abbreviations'}}
    with pytest.raises(ValueError, match='cannot have confidence'):
        record.apply(root, {'F-test': dict(good['F-test'], confidence='medium')}, out, 'b1', 'r', '2026-01-02')
    with pytest.raises(ValueError, match='needs a report'):
        record.apply(root, {'F-test': {k: v for k, v in good['F-test'].items() if k != 'report'}}, out, 'b1', 'r', '2026-01-02')
    (out / 'bad.md').write_text('see /tmp/scratch/x.jpg\n')
    with pytest.raises(ValueError, match='local path'):
        record.apply(root, {'F-test': dict(good['F-test'], report='bad.md')}, out, 'b1', 'r', '2026-01-02')
    assert json.loads(ledger.read_text())[0]['status'] == 'unidentified', 'a refused result changes nothing'
    record.apply(root, good, out, 'b1', 'r', '2026-01-02')
    row = json.loads(ledger.read_text())[0]
    assert (row['status'], row['identified_on'], row['examined']) == ('identified', '2026-01-02', '2026-01-02')
    assert (root / 'fragments/F-test/README.md').read_text().startswith('# F-test')
    assisted_record = json.loads((root / 'fragments/F-test/readings/b1-source-assisted.json').read_text())
    assert assisted_record['first_reading'] == 'b1-image-only'
    record.apply(root, {'F-test': {'status': 'partial', 'confidence': 'low', 'identification': 'x', 'note': 'y'}},
                 out, 'b1', 'r', '2026-01-03')
    row = json.loads(ledger.read_text())[0]
    assert row['identified_on'] is None and row['verify'] == 'https://fragmentarium.ms/overview/F-test'


def test_record_marks_documents_moves_thumbnail_and_keeps_report_in_place(work):
    import record
    root, args = work
    ledger = root / 'data/fragments.json'
    ledger.write_text(json.dumps([{'id': 'F-test', 'record': 'https://fragmentarium.ms/overview/F-test',
                                   'manifest': 'https://fragmentarium.ms/metadata/iiif/F-test/manifest.json',
                                   'thumbnail': 'https://x.org/back/full/240,/0/default.jpg',
                                   'status': 'unidentified', 'confidence': 'none', 'identified_on': None}]))
    cache = root / 'cache'
    (cache / 'F-test').mkdir(parents=True)
    canvas = lambda n: {'images': [{'resource': {'@id': f'https://x.org/{n}.jpg', 'service': {'@id': f'https://x.org/{n}'}}}]}
    (cache / 'F-test/manifest.json').write_text(json.dumps({'sequences': [{'canvases': [canvas('back'), canvas('text')]}]}))
    report = root / 'fragments/F-test/README.md'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text('# F-test: a deed\n')
    result = {'status': 'identified', 'confidence': 'high', 'identification': 'a deed', 'note': 'n',
              'report': '../fragments/F-test/README.md', 'document': True, 'thumbnail_canvas': 1}
    record.apply(root, {'F-test': result}, root / 'data', 'b1', 'r', '2026-01-02', cache)
    row = json.loads(ledger.read_text())[0]
    assert row['document'] is True and row['thumbnail'] == 'https://x.org/text/full/240,/0/default.jpg'
    assert report.read_text() == '# F-test: a deed\n'
    record.apply(root, {'F-test': dict(result, document=False, thumbnail_canvas=None)}, root / 'data', 'b1', 'r',
                 '2026-01-03', cache)
    assert 'document' not in json.loads(ledger.read_text())[0]
