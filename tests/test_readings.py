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
    (fragment / 'README.md').write_text('# F-test\n')
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
