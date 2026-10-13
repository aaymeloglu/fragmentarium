"""Selection and vernacular-search helpers: parsing only, no network."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import catalogue
import mnlsearch
import survey

MANIFEST = {
    'label': 'Leipzig, UB, Fragm. lat. 1',
    'metadata': [
        {'label': 'Title', 'value': 'Liturgica (unidentified)'},
        {'label': 'Current Dimensions (in mm)', 'value': '39 x 193 mm'},
        {'label': 'Reconstruction Summary', 'value': '<p>Host volume: <i>Ms 953</i>.</p>'},
        {'label': 'Rights', 'value': 'CC'},
    ],
    'sequences': [{'canvases': [{'label': 'recto'}, {'label': 'verso'}]}],
}
OVERVIEW = '''<a href="https://fragmentarium.ms/description/F-test/313">Description</a>
<a href="/description/F-test/313">again</a> <a href="/description/F-other/9">other record</a>'''
DESCRIPTION = '''<html><head><title>x</title></head><body><nav>Home</nav>
<div>Overview</div><div>Description</div><h2>Content Description</h2>
<p>Excerpt aus Cantica Canticorum 2,14 &amp; 3,1-3</p><script>var a = 1;</script></body></html>'''


def fake_fetch(pages):
    def fetch(url):
        if url not in pages:
            raise OSError('404 ' + url)
        return pages[url].encode()
    return fetch


def test_description_links_are_this_records_and_not_repeated():
    assert catalogue.description_links('F-test', OVERVIEW) == ['https://fragmentarium.ms/description/F-test/313']


def test_record_gives_summary_fields_and_the_linked_description():
    text = catalogue.record('F-test', MANIFEST, fetch=fake_fetch({
        'https://fragmentarium.ms/overview/F-test': OVERVIEW,
        'https://fragmentarium.ms/description/F-test/313': DESCRIPTION,
    }))
    assert 'Title: Liturgica (unidentified)' in text
    assert 'Reconstruction Summary: Host volume: Ms 953' in text
    assert 'Rights' not in text
    assert 'Images (2): recto; verso' in text
    assert 'Linked description: https://fragmentarium.ms/description/F-test/313' in text
    assert 'Excerpt aus Cantica Canticorum 2,14 & 3,1-3' in text
    assert 'var a' not in text and 'Home' not in text


def test_record_says_when_there_is_no_description_or_the_page_failed():
    none = catalogue.record('F-test', MANIFEST, fetch=fake_fetch({'https://fragmentarium.ms/overview/F-test': '<p>no links</p>'}))
    assert 'Linked description: none' in none
    failed = catalogue.record('F-test', MANIFEST, fetch=fake_fetch({}))
    assert 'Linked description: not checked' in failed and 'none' not in failed


def test_phrase_becomes_a_sequence_of_whole_words():
    assert mnlsearch.cql('versamenden  sanghe') == '"(?i)versamenden" "(?i)sanghe"'
    assert mnlsearch.cql('"sachtmo.*"') == '"(?i)sachtmo.*"'
    with pytest.raises(ValueError):
        mnlsearch.cql('  ')


def test_hits_are_read_with_their_work_title():
    result = {'docInfos': {'d1': {'title': ['Getijdenboek van Geert Grote']}},
              'hits': [{'docPid': 'd1', 'left': {'word': ['in', 'eendrachtighen']},
                        'match': {'word': ['versamenden', 'sanghe']}, 'right': {'word': ['in', 'der']}}]}
    assert list(mnlsearch.rows(result)) == [('Getijdenboek van Geert Grote', 'in eendrachtighen', 'versamenden sanghe', 'in der')]


def test_catalogue_millimetres_long_side_first():
    assert survey.millimetres('39 x 193 mm') == (193.0, 39.0)
    assert survey.millimetres('ca. 45 x 100 mm') == (100.0, 45.0)
    assert survey.millimetres('171 mm x 50 mm, 55 mm x 35 mm') == (171.0, 55.0)
    assert survey.millimetres('') is None and survey.millimetres('1 leaf') is None


def test_density_is_an_upper_bound_from_the_largest_image():
    assert survey.density([(205, 768), (216, 768)], (273.0, 59.0)) == 2.8
    assert survey.density([(5760, 3840)], (193.0, 39.0)) == 29.8
    assert survey.density([(5760, 3840)], None) is None
    assert survey.density([], (193.0, 39.0)) is None


def test_flags():
    assert survey.flags([(205, 768)], True, None) == ['SMALL', 'DESC']
    assert survey.flags([(4384, 5777)], False, None) == []
    assert survey.flags([], False, 'HTTP Error 404') == ['ERR']
    assert survey.flags([(1500, 900)], False, None, small=2000) == ['SMALL']


def test_candidates_are_sweep_rows_without_a_ledger_row(tmp_path):
    sweep = tmp_path / 'sweep.csv'
    sweep.write_text('fragmentarium_id,title,dimensions_mm\nF-aaaa,One,1 x 2 mm\nF-bbbb,Two,3 x 4 mm\n', encoding='utf-8')
    ledger = tmp_path / 'ledger.json'
    ledger.write_text(json.dumps([{'id': 'F-aaaa'}]), encoding='utf-8')
    assert list(survey.candidates(sweep, ledger)) == ['F-bbbb']


def test_a_record_sharing_a_shelfmark_with_a_ledger_record_is_a_sibling():
    ledger = [
        {'id': 'F-join', 'institution': 'Orselina, Biblioteca', 'shelfmark': 'MdS 58 Ca 18/F2, MdS 58 Ca 19/F1-2', 'status': 'partial'},
        {'id': 'F-near', 'institution': 'Orselina, Biblioteca', 'shelfmark': 'MdS 58 Ca 19', 'status': 'unidentified'},
        {'id': 'F-else', 'institution': 'Leuven, KU Leuven', 'shelfmark': 'MdS 58 Ca 18/F2', 'status': 'identified'},
        {'id': 'F-bare', 'institution': None, 'shelfmark': None},
    ]
    assert survey.siblings('Orselina, Biblioteca, MdS 58 Ca 18/F2', ledger) == ['F-join (partial)']
    assert survey.siblings('Orselina, Biblioteca, MdS 58 Ca 20', ledger) == []
    assert survey.siblings('Orselina, Biblioteca, MdS 58 Ca 1, nr. 4', ledger + [{'id': 'F-alb', 'institution': 'Orselina, Biblioteca', 'shelfmark': 'MdS 58 Ca 1, nr. 9'}]) == []
    assert survey.siblings('', ledger) == []
    assert survey.flags([(4384, 5777)], False, None, sibling=True) == ['SIB']
