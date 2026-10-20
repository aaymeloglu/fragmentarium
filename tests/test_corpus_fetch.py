import hashlib
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import corpus
import corpus_fetch as fetcher
import latin_search

ROW = {'id': 'test', 'ia': 'test-source', 'edition': 'A test edition', 'coverage': 'Homilies'}


def response(raw=b'prima materia longa anima intellectiva finis'):
    return {'metadata': {'title': 'A test edition', 'language': 'lat'}, 'files': [
        {'name': 'test_djvu.txt', 'size': str(len(raw)), 'sha1': hashlib.sha1(raw).hexdigest()}]}


def test_download_register_resume_and_search(tmp_path):
    raw = b'prima materia longa anima intellectiva finis'
    calls = []
    def get(url):
        calls.append(url)
        return json.dumps(response(raw)).encode() if '/metadata/' in url else raw
    manifest = tmp_path / 'corpus.json'
    result = fetcher.fetch_one(ROW, manifest, get)
    assert result['status'] == 'downloaded' and len(calls) == 2
    assert fetcher.fetch_one(ROW, manifest, get)['status'] == 'cached'
    assert len(calls) == 2
    receipt = json.loads((tmp_path / 'receipts/test.json').read_text())
    assert receipt['sha256'] == corpus.digest(raw)
    query = {'anchors': [{'id': 'a', 'variants': [{'parts': ['prima materia', 'anima intellectiva'],
             'gaps': [{'min': 1, 'max': 20}], 'basis': 'test damaged reading'}]}]}
    hits = latin_search.search(corpus.load_documents(manifest), query)['documents'][0]['hits']
    assert hits[0]['segments'][1]['text'] == 'anima intellectiva'
    saved = json.loads(manifest.read_text())['documents'][0]
    (tmp_path / saved['path']).write_text('changed')
    with pytest.raises(ValueError, match='Cached text changed'):
        fetcher.fetch_one(ROW, manifest, get)


@pytest.mark.parametrize('metadata', [
    {}, {'is_dark': True}, {'metadata': {'access-restricted-item': 'true'}},
    {'files': [{'name': 'x_djvu.txt', 'private': 'true'}]},
    {'files': [{'name': 'x_djvu.txt'}, {'name': 'y_djvu.txt'}]},
])
def test_missing_private_restricted_or_ambiguous_sources_are_not_imported(metadata):
    with pytest.raises(ValueError):
        fetcher.select_ocr(metadata)


def test_explicit_ocr_file_for_multivolume_items():
    meta = {'files': [{'name': 'x_djvu.txt'}, {'name': 'y_djvu.txt'}]}
    assert fetcher.select_ocr(meta, 'y_djvu.txt')['name'] == 'y_djvu.txt'


@pytest.mark.parametrize('bad', [b'<html>Please log in</html>', b'wrong size', b''])
def test_failed_download_never_enters_manifest(tmp_path, bad):
    def get(url):
        return json.dumps(response()).encode() if '/metadata/' in url else bad
    with pytest.raises(ValueError):
        fetcher.fetch_one(ROW, tmp_path / 'corpus.json', get)
    assert not (tmp_path / 'corpus.json').exists()


def test_pinned_source_change_rejected(tmp_path):
    raw = b'materia prima'
    def get(url):
        return json.dumps(response(raw)).encode() if '/metadata/' in url else raw
    with pytest.raises(ValueError, match='pinned'):
        fetcher.fetch_one(dict(ROW, sha256='0' * 64), tmp_path / 'corpus.json', get)


def test_changed_source_cannot_reuse_an_existing_id(tmp_path):
    raw = b'materia prima'
    def get(url):
        return json.dumps(response(raw)).encode() if '/metadata/' in url else raw
    manifest = tmp_path / 'corpus.json'
    fetcher.fetch_one(ROW, manifest, get)
    with pytest.raises(ValueError, match='different source'):
        fetcher.fetch_one(dict(ROW, ia='different'), manifest, get)
