"""Cached corpus bytes and physical page citations remain auditable."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import corpus
import latin_search as latin


def test_import_and_search_keep_exact_bytes_and_page_provenance(tmp_path):
    raw = 'préface\r\nMATERIÆ prima\r\nanima intellectiva'.encode()
    text = raw.decode()
    source = tmp_path / 'download.txt'
    source.write_bytes(raw)
    manifest = tmp_path / 'library/corpus.json'
    start = text.index('MATERIÆ')
    pages = [{'start': start, 'end': len(text), 'locus': 'fol. 12r', 'url': 'https://example.org/12r'}]
    edition = {'title': 'Test edition', 'attribution_source': 'https://example.org/title'}
    row = corpus.add_document(manifest, 'example', source, 'https://example.org/text', edition, pages)
    assert (manifest.parent / row['path']).read_bytes() == raw
    saved = manifest.read_bytes()
    # The corpus survives removal of the original download.
    source.unlink()
    docs = corpus.load_documents(manifest)
    assert docs[0]['text'] == text
    result = latin.search(docs, latin.literal_query(['materiae prima']))['documents'][0]
    assert result['edition'] == edition
    assert result['hits'][0]['source_pages'][0]['locus'] == 'fol. 12r'
    assert result['hits'][0]['source_pages'][0]['matched_start'] == start
    assert manifest.read_bytes() == saved
    (manifest.parent / row['path']).write_text('silently changed')
    with pytest.raises(ValueError, match='changed'):
        corpus.load_documents(manifest)


def test_duplicate_ids_and_content_addressed_reuse(tmp_path):
    text = tmp_path / 'text.txt'; text.write_text('materia prima')
    manifest = tmp_path / 'corpus.json'
    row = corpus.add_document(manifest, 'one', text, 'https://example.org/text')
    saved = manifest.read_bytes()
    with pytest.raises(ValueError, match='already registered'):
        corpus.add_document(manifest, 'one', text, 'https://example.org/text')
    assert manifest.read_bytes() == saved
    second = corpus.add_document(manifest, 'two', text, 'https://example.org/other')
    assert second['path'] == row['path']
    assert len(list((tmp_path / 'texts').glob('*.txt'))) == 1
    # Existing corrupt cache files must not be trusted or overwritten.
    (tmp_path / row['path']).write_text('corrupt')
    saved = manifest.read_bytes()
    with pytest.raises(ValueError, match='checksum'):
        corpus.add_document(manifest, 'three', text, 'https://example.org/text')
    assert manifest.read_bytes() == saved


def test_unmapped_spans_and_gapped_segments(tmp_path):
    text = 'prima materia longa anima intellectiva finis'
    docs = [{'id':'one', 'source':'test source', 'text':text, 'pages':[
        {'start':0,'end':5,'locus':'p.1 excerpt','url':'https://example.org/1'},
        {'start':20,'end':25,'locus':'p.2 excerpt','url':'https://example.org/2'}]}]
    q = {'anchors':[{'id':'a','variants':[{'parts':['prima','anima'],
        'gaps':[{'min':1,'max':20}], 'basis':'test reading'}]}]}
    hit = latin.search(docs,q)['documents'][0]['hits'][0]
    assert [p['locus'] for p in hit['source_pages']] == ['p.1 excerpt','p.2 excerpt']
    assert len(hit['segments'][0]['source_pages']) == 1
    assert hit['segments'][1]['source_pages'][0]['matched_start'] == text.index('anima')
    unmapped = latin.search(docs,latin.literal_query(['finis']))['documents'][0]['hits'][0]
    assert unmapped['source_pages'] == []


@pytest.mark.parametrize('ranges', [
    [{'start':0,'end':20,'locus':'x','url':'https://example.org'}],
    [{'start':True,'end':4,'locus':'x','url':'https://example.org'}],
    [{'start':2,'end':1,'locus':'x','url':'https://example.org'}],
    [{'start':0,'end':4,'locus':'x','url':'file:///private'}],
    [{'start':0,'end':4,'locus':'x','url':'https://example.org'},
     {'start':3,'end':5,'locus':'y','url':'https://example.org'}],
])
def test_bad_ranges_rejected_before_cache_write(tmp_path, ranges):
    text=tmp_path/'text.txt';text.write_text('abcdef')
    with pytest.raises(ValueError):
        corpus.add_document(tmp_path/'corpus.json','one',text,'https://example.org',pages=ranges)
    assert not (tmp_path/'texts').exists()
    assert not (tmp_path/'corpus.json').exists()


def test_html_challenge_not_registered_as_edition_text(tmp_path):
    text=tmp_path/'text.txt';text.write_text('<!DOCTYPE html><html>please sign in</html>')
    with pytest.raises(ValueError,match='HTML'):
        corpus.add_document(tmp_path/'corpus.json','one',text,'https://example.org')


def test_concurrent_import_lock_leaves_existing_files_alone(tmp_path):
    text=tmp_path/'text.txt';text.write_text('materia prima')
    manifest=tmp_path/'corpus.json';manifest.write_text('{"documents":[]}')
    lock=tmp_path/'corpus.json.lock';lock.touch()
    with pytest.raises(FileExistsError):
        corpus.add_document(manifest,'one',text,'https://example.org')
    assert lock.exists()
    assert manifest.read_text()=='{"documents":[]}'


def test_cli_search_checks_registered_checksum(tmp_path):
    text=tmp_path/'text.txt';text.write_text('materia prima')
    manifest=tmp_path/'corpus.json'
    subprocess.run([sys.executable,corpus.__file__,'--corpus',str(manifest),'--id','one',
                    '--text',str(text),'--source','https://example.org'],check=True,capture_output=True)
    q=tmp_path/'query.json';q.write_text(json.dumps(latin.literal_query(['materia prima'])))
    cmd=[sys.executable,latin.__file__,'--corpus',str(manifest),'--query',str(q)]
    result=json.loads(subprocess.check_output(cmd))
    assert result['documents'][0]['hits']
    row=json.loads(manifest.read_text())['documents'][0]
    (tmp_path/row['path']).write_text('altered text')
    failed=subprocess.run(cmd,capture_output=True,text=True)
    assert failed.returncode==1 and 'Cached text changed' in failed.stderr
