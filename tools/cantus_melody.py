#!/usr/bin/env python3
"""Search Cantus Index melodies and manuscript concordances by a surviving tune.

Supply 4-14 successive distinct Volpiano pitches (9, a-h, j-q), not note names.
Hyphens, clef/bar signs and staff breaks are accepted. Adjacent repeated pitches
collapse as in Cantus's web keyboard. Accidentals, gaps and uncertain notes are
rejected: choose a continuous secure segment and search alternatives separately.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request

BASE = 'https://cantusindex.org'
ENDPOINTS = ('searchmelody', 'searchmelody-con')


def pitches(value):
    value = re.sub(r'\s+', '', value).lower()
    if not re.fullmatch(r'[9a-hj-q13457-]+', value):
        raise ValueError('Use secure Volpiano pitches 9,a-h,j-q; gaps, accidentals and uncertainty are unsupported')
    notes = re.sub(r'[-13457]', '', value)
    notes = re.sub(r'(.)\1+', r'\1', notes)
    if not 4 <= len(notes) <= 14:
        raise ValueError('Supply 4-14 successive distinct pitches, as in the Cantus web keyboard')
    return '1-' + '-'.join(notes)


def search_url(endpoint, notes, start=False, transpose=False, text='', genre='', mode=''):
    return BASE + '/' + endpoint + '?' + urllib.parse.urlencode({
        't': pitches(notes), 'src': '', 'genre': genre, 'siglum': '',
        'text': text, 'feast': '', 'mode': mode,
        'start': int(start), 'transpose': int(transpose)})


def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', value))).strip()


def safe_link(value):
    url = urllib.parse.urljoin(BASE, html.unescape(value))
    if urllib.parse.urlsplit(url).scheme not in {'http', 'https'}:
        raise ValueError('Unexpected link scheme in Cantus result')
    return url


def parse_results(body, endpoint):
    heading = re.search(r'<h4>(.*?)</h4>', body, re.S | re.I)
    label = 'Melodies in the Cantus Index network' if endpoint.endswith('-con') else 'Cantus Index melodies'
    if not heading or not clean(heading[1]).startswith(label):
        raise ValueError('Unrecognised Cantus response; not a zero-result search')
    count = re.search(r'\(\s*([\d,]+)\s+melodies\s*\)', clean(heading[1]))
    if not count:
        raise ValueError('Cantus result count missing')
    total = int(count[1].replace(',', ''))
    rows = []
    for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>', body, re.S | re.I):
        cells = re.findall(r'<td\b[^>]*>(.*?)</td>', row, re.S | re.I)
        if len(cells) != 2:
            raise ValueError('Cantus result layout changed')
        tune = re.search(r'<div\b[^>]*class="volpiano[^\"]*"[^>]*>(.*?)</div>', cells[1], re.S)
        links = re.findall(r'<a\b[^>]*href="([^\"]+)"[^>]*>(.*?)</a>', row, re.S)
        if not tune or len(links) < 2:
            raise ValueError('Cantus result is missing melody or source links')
        fields = {key.lower(): clean(match[1]) if (match := re.search(
            key + r':\s*<b>(.*?)</b>', cells[0], re.S)) else '' for key in ('Genre', 'Mode', 'Folio', 'DB')}
        rows.append({**fields, 'label': clean(links[0][1]), 'source_url': safe_link(links[0][0]),
                     'result_url': safe_link(links[-1][0]), 'incipit': clean(links[-1][1]),
                     'volpiano': clean(tune[1])})
    if len(rows) > total or (total and not rows):
        raise ValueError('Cantus result count disagrees with parsed rows')
    return {'reported_count': total, 'returned_count': len(rows),
            'truncated': len(rows) < total, 'results': rows}


def fetch(url, cache, offline=False):
    cache.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()
    path = cache / (key + '.html')
    receipt_path = cache / (key + '.json')
    if path.exists() and receipt_path.exists():
        raw = path.read_bytes()
        receipt = json.loads(receipt_path.read_text())
        if receipt.get('url') != url or receipt.get('sha256') != hashlib.sha256(raw).hexdigest():
            raise ValueError('Melody cache changed; use a new cache directory')
        return raw.decode('utf-8-sig'), receipt
    if offline:
        raise ValueError('Query not cached; omit --offline to search online')
    with urllib.request.urlopen(urllib.request.Request(url, headers={
            'User-Agent': 'fragmentarium-research/1.0'}), timeout=120) as response:
        raw = response.read()
    body = raw.decode('utf-8-sig')
    # Do not cache a login/challenge/error page as a successful search.
    parse_results(body, urllib.parse.urlsplit(url).path.lstrip('/'))
    receipt = {'url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
               'sha256': hashlib.sha256(raw).hexdigest()}
    path.write_bytes(raw)
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    return body, receipt


def search(notes, cache, start=False, transpose=False, text='', genre='', mode='', offline=False):
    normalized = pitches(notes)
    result = {'status': 'candidate-retrieval-only', 'input': notes,
              'query': normalized, 'settings': {'start': start, 'transpose': transpose,
              'text': text, 'genre': genre, 'mode': mode}, 'indexes': {}, 'complete': True}
    for endpoint in ENDPOINTS:
        url = search_url(endpoint, normalized, start, transpose, text, genre, mode)
        try:
            body, receipt = fetch(url, cache, offline)
            result['indexes'][endpoint] = {**parse_results(body, endpoint), 'request': receipt}
        except (OSError, ValueError) as error:
            result['complete'] = False
            result['indexes'][endpoint] = {'status': 'unavailable', 'error': str(error), 'url': url}
        if not offline:
            time.sleep(0.5)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('notes', help='continuous Volpiano pitch segment, e.g. dcd fdc fghgfgh')
    parser.add_argument('--start', action='store_true', help='match an opening; default searches anywhere')
    parser.add_argument('--transpose', action='store_true', help='also request the server’s transposed matches')
    parser.add_argument('--text', default='', help='optional surviving chant words')
    parser.add_argument('--genre', default='')
    parser.add_argument('--mode', default='')
    parser.add_argument('--cache', type=Path, default=Path('scratch/cantus-melody'))
    parser.add_argument('--offline', action='store_true', help='replay previously cached queries')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--limit', type=int, default=20, help='display limit per index; JSON retains every returned row')
    args = parser.parse_args()
    try:
        if args.limit < 1:
            raise ValueError('--limit must be positive')
        result = search(args.notes, args.cache, args.start, args.transpose, args.text,
                        args.genre, args.mode, args.offline)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Query {result['query']} (candidate retrieval only)")
            for endpoint, index in result['indexes'].items():
                if index.get('status') == 'unavailable':
                    print(f"{endpoint}: unavailable: {index['error']}")
                    continue
                print(f"{endpoint}: {index['reported_count']} reported, {index['returned_count']} returned")
                if index['truncated']:
                    print('Server returned only part of the results; narrow the query.')
                for row in index['results'][:args.limit]:
                    print(f"* [{row['label']}]({row['result_url']}) {row['folio']} {row['genre']} {row['mode']}: {row['incipit']}")
                    print(f"  {row['volpiano']}")
                if len(index['results']) > args.limit:
                    print('Display limited; --json includes all returned rows.')
        if not result['complete']:
            parser.exit(1, 'One or more indexes unavailable; this is not a negative result.\n')
    except (OSError, ValueError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
