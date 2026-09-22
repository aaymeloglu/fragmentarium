"""Retrieval regressions: tolerant search must not erase provenance or invent order."""
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import latin_search as latin
import ia_cluster


def documents(*texts):
    return [{'id': str(i), 'source': f'test source {i}', 'text': t} for i, t in enumerate(texts)]


def test_normalization_and_original_offsets():
    raw = 'Préface\r\n\fMATERIÆ, jvſta intel-\r\n lectivam. māter'
    view = latin.normalize(raw)
    assert view.text == 'préface materie iusta intellectiuam māter'
    index = latin.TextIndex(raw)
    start, end, edits, mode = next(index.find('materie iusta intellectiuam', 0))
    hit = index.hit(start, end, edits, mode, 'a1', 0, 'materie iusta intellectiuam')
    assert hit['text'] == 'MATERIÆ, jvſta intel-\r\n lectivam'
    assert raw[hit['start']:hit['end']] == hit['text']
    assert hit['line'] == 2 and hit['form_feed_page'] == 2
    assert latin.normalize('a\u0304').text == latin.normalize('ā').text
    assert latin.normalize('materiae').text == latin.normalize('materie').text
    assert latin.normalize('materiæ').text == latin.normalize('materie').text
    assert latin.normalize('fama').text != latin.normalize('sama').text
    assert latin.normalize('fama', True).text == latin.normalize('sama', True).text


def test_partial_words_and_expansion_alternatives_are_explicit():
    query = {'anchors': [{'id': 'line1', 'variants': [
        {'text': 'mater* prima', 'basis': 'uncertain ending'},
        {'text': 'substantia prima', 'basis': 'alternative proposed expansion'}]}]}
    result = latin.search(documents('materia prima; substantia prima; immateria prima'), query)
    hits = result['documents'][0]['hits']
    assert [h['variant'] for h in hits] == [0, 1]
    assert hits[0]['mode'] == 'partial-word'
    assert result['query'] == query
    assert 'materia' not in query['anchors'][0]['variants'][0]['text']


def test_fuzzy_retrieves_ocr_error_with_visible_distance():
    query = latin.literal_query(['ad recipiendum animam intellectivam'])
    result = latin.search(documents('ad recipendum animam intellectivam'), query, max_edits=1)
    hit = result['documents'][0]['hits'][0]
    assert hit['edits'] == 1 and hit['mode'] == 'edit-distance'
    assert not latin.search(documents('ad recipendum animam intellectivam'), query)['documents'][0]['hits']


def unbounded_distance(a, b):
    row = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        nxt = [i]
        for j, cb in enumerate(b, 1):
            nxt.append(min(row[j] + 1, nxt[j - 1] + 1, row[j - 1] + (ca != cb)))
        row = nxt
    return row[-1]


def test_bounded_distance_against_full_reference():
    words = [''.join(chars) for n in range(4) for chars in itertools.product('ab', repeat=n)]
    for a in words:
        for b in words:
            for limit in range(3):
                expected = unbounded_distance(a, b)
                assert min(latin.distance(a, b, limit), limit + 1) == min(expected, limit + 1)


def test_ngram_seeds_do_not_miss_bounded_matches():
    # Compare candidate pruning to exhaustive whole-word substring search, including word splits/joins.
    rng = random.Random(31)
    query = 'materia prima anima'
    for _ in range(60):
        variant = query
        for _ in range(rng.randrange(1, 4)):
            pos = rng.randrange(len(variant))
            operation = rng.randrange(3)
            variant = (variant[:pos] + rng.choice(' abcr') + variant[pos:] if operation == 0 else
                       variant[:pos] + variant[pos + 1:] if operation == 1 else
                       variant[:pos] + rng.choice(' abr') + variant[pos + 1:])
        index = latin.TextIndex('ante ' + variant + ' post')
        for limit in (1, 2, 3):
            actual = {(s, e, d) for s, e, d, _ in index.find(query, limit)}
            expected = {(s, e, unbounded_distance(query, index.text[s:e]))
                        for s in index.starts for e in index.ends if e > s
                        if unbounded_distance(query, index.text[s:e]) <= limit}
            assert actual == expected


def test_wrong_order_and_scattered_anchors_do_not_get_full_coverage():
    query = latin.literal_query(['prima materia', 'anima intellectiva', 'forma asini'])
    result = latin.search(documents('prima materia; anima intellectiva; forma asini',
                                    'forma asini; anima intellectiva; prima materia',
                                    'prima materia ' + 'x ' * 100 + 'anima intellectiva forma asini'),
                          query, window=65)
    by_id = {d['id']: d for d in result['documents']}
    assert by_id['0']['passages'][0]['matched'] == 3
    assert by_id['1']['passages'][0]['matched'] == 1
    assert by_id['2']['passages'][0]['matched'] == 2
    assert all(p['end'] - p['start'] <= 65 for d in result['documents'] for p in d['passages'])


def test_missing_first_anchor_and_overlaps():
    query = latin.literal_query(['not present', 'anima intellectiva', 'intellectiva materia'])
    result = latin.search(documents('anima intellectiva materia'), query)
    passage = result['documents'][0]['passages'][0]
    assert passage['matched'] == 1  # overlapping text cannot support two anchors
    assert 'a1' in passage['unmatched']


def test_commonplace_only_cannot_rank_and_frequency_is_per_document():
    query = latin.literal_query(['leprosus generat leprosum', 'materia ipsius asini', 'denudatio ab omni alia forma'])
    query['anchors'][0].update(common=True, reason='shared maxim')
    result = latin.search(documents('leprosus generat leprosum ' * 5,
                                    'leprosus generat leprosum materia ipsius asini denudatio ab omni alia forma'), query)
    assert result['document_frequency'] == {'a1': 2, 'a2': 1, 'a3': 1}
    assert result['weights']['a1'] == 0
    assert result['documents'][0]['id'] == '1'
    assert result['documents'][0]['passages'][0]['matched'] == 2
    assert result['documents'][1]['hit_counts']['a1'] == 5
    assert result['documents'][1]['passages'] == []
    ordinary = latin.search(documents('materia prima anima longa', 'materia prima'),
                            latin.literal_query(['materia prima', 'anima longa']))
    assert ordinary['weights']['a2'] > ordinary['weights']['a1']


@pytest.mark.parametrize('phrase', ['*', 'ma*', 'a * prima'])
def test_unconstrained_wildcards_rejected(phrase):
    with pytest.raises(ValueError):
        latin.search(documents('materia prima'), latin.literal_query([phrase]))


def test_cli_preserves_bytes_and_refuses_overwriting(tmp_path):
    source = tmp_path / 'source.txt'
    raw = b'Intro\r\nmateria prima\r\n'
    source.write_bytes(raw)
    corpus = tmp_path / 'corpus.json'
    corpus.write_text(json.dumps({'documents': [{'id': 'one', 'path': 'source.txt', 'source': 'test citation'}]}))
    query = tmp_path / 'query.json'
    query.write_text(json.dumps(latin.literal_query(['materia prima'])))
    output = tmp_path / 'result.json'
    cmd = [sys.executable, latin.__file__, '--corpus', str(corpus), '--query', str(query), '--output', str(output)]
    subprocess.run(cmd, check=True, capture_output=True)
    saved = output.read_bytes()
    result = json.loads(saved)
    hit = result['documents'][0]['hits'][0]
    assert raw.decode()[hit['start']:hit['end']] == hit['text']
    assert result['documents'][0]['text_sha256'] == latin.hashlib.sha256(raw).hexdigest()
    assert source.read_bytes() == raw
    assert subprocess.run(cmd, capture_output=True).returncode == 1
    assert output.read_bytes() == saved


def test_ia_wrapper_uses_ordered_engine_and_local_cache(tmp_path, capsys):
    (tmp_path / 'sample.txt').write_text('anima intellectiva; materia prima. ' + 'x ' * 600)
    ia_cluster.main(['sample', 'materia prima', 'anima intellectiva', '--cache-dir', str(tmp_path), '--json'])
    result = json.loads(capsys.readouterr().out)
    assert result['documents'][0]['passages'][0]['matched'] == 1
    with pytest.raises(ValueError):
        ia_cluster.ocr_text('../escape', tmp_path)


def test_ordered_ranking_agrees_with_exhaustive_chains():
    rng = random.Random(19)
    anchors = latin.literal_query(['aaa', 'bbb', 'ccc', 'ddd'])['anchors']
    weights = {'a1': 1.1, 'a2': 1.7, 'a3': 1.0, 'a4': 1.5}
    for _ in range(30):
        hits = [{'anchor': rng.choice(list(weights)), 'start': i * 10,
                 'end': i * 10 + rng.randint(3, 13), 'edits': rng.randrange(2)} for i in range(7)]
        window = 35
        best = 0
        for n in range(1, len(hits) + 1):
            for chain in itertools.combinations(hits, n):
                if chain[-1]['end'] - chain[0]['start'] > window:
                    continue
                if any(a['end'] > b['start'] or a['anchor'] >= b['anchor'] for a, b in zip(chain, chain[1:])):
                    continue
                best = max(best, sum(weights[h['anchor']] / (1 + h['edits']) for h in chain))
        actual = latin.ordered_passages(hits, anchors, weights, window, 1)
        assert actual[0]['score'] == round(best, 6)
