#!/usr/bin/env python3
"""Fetch a curated collection of public Internet Archive OCR into corpus.py's cache.

A collection lists IA identifiers, editions and intended coverage. This downloads
only public UTF-8 OCR, never borrowed books or page images. Re-running verifies
cached bytes and reuses successful downloads; failures remain explicit.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

import corpus

UA = {'User-Agent': 'fragmentarium-research/1.0 (public edition OCR)'}
MAX_BYTES = 120 * 1024 * 1024


def get(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as response:
                data = response.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise ValueError('Response exceeds 120 MiB; select a smaller source')
            return data
        except urllib.error.HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.download-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def truth(value):
    return value is True or str(value).lower() in {'true', '1'}


def select_ocr(metadata, filename=None):
    if not metadata or truth(metadata.get('is_dark')):
        raise ValueError('Item missing or unavailable')
    item = metadata.get('metadata', {})
    if truth(item.get('access-restricted-item')) or truth(item.get('access_restricted_item')):
        raise ValueError('Access-restricted item; not a public OCR source')
    files = [f for f in metadata.get('files', [])
             if f.get('name', '').endswith('_djvu.txt') and not truth(f.get('private'))]
    if filename:
        files = [f for f in files if f['name'] == filename]
    if len(files) != 1:
        raise ValueError(f'Expected one public OCR file, found {len(files)}; specify file in collection')
    return files[0]


def validate_collection(collection):
    rows = collection['documents']
    if not rows or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Collection needs nonempty documents with unique ids')
    for row in rows:
        for field in ('id', 'ia'):
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', row[field]):
                raise ValueError(f'Invalid {field}')
        if not row.get('edition') or not row.get('coverage'):
            raise ValueError('Every source needs an edition label and coverage note')
    return rows


def fetch_one(row, manifest, fetch=get):
    manifest = Path(manifest)
    existing = json.loads(manifest.read_text())['documents'] if manifest.exists() else []
    source = f"https://archive.org/details/{row['ia']}"
    prior = next((d for d in existing if d['id'] == row['id']), None)
    if prior:
        if prior['source'] != source or prior.get('edition', {}).get('title') != row['edition']:
            raise ValueError('Registered id has different source or edition; use a new id')
        raw = (manifest.parent / prior['path']).read_bytes()
        if corpus.digest(raw) != prior['sha256']:
            raise ValueError('Cached text changed; restore it or use a new corpus directory')
        if row.get('sha256') and prior['sha256'] != row['sha256']:
            raise ValueError('Cached text differs from pinned collection checksum')
        return {'id': row['id'], 'status': 'cached', 'bytes': len(raw), 'sha256': prior['sha256']}
    meta_url = f"https://archive.org/metadata/{row['ia']}"
    metadata = json.loads(fetch(meta_url))
    file = select_ocr(metadata, row.get('file'))
    url = f"https://archive.org/download/{row['ia']}/{urllib.parse.quote(file['name'], safe='/')}"
    raw = fetch(url)
    if file.get('size') and len(raw) != int(file['size']):
        raise ValueError('Download size disagrees with IA metadata')
    if file.get('sha1') and hashlib.sha1(raw).hexdigest() != file['sha1']:
        raise ValueError('Download checksum disagrees with IA metadata')
    if row.get('sha256') and corpus.digest(raw) != row['sha256']:
        raise ValueError('Download differs from pinned collection checksum')
    # Validate the response before storing it as a source. corpus.py also rejects HTML.
    text = raw.decode('utf-8')
    if not text.strip() or re.search(r'<(?:!doctype\s+html|html|head|body)\b', text[:4096], re.I):
        raise ValueError('Expected OCR text, received empty/HTML response')
    manifest.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=manifest.parent, suffix='.txt')
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
        receipt = {'id': row['id'], 'source': source, 'download': url,
                   'metadata_source': meta_url, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                   'ia_metadata': metadata.get('metadata', {}), 'ia_file': file,
                   'bytes': len(raw), 'sha256': corpus.digest(raw), 'coverage': row['coverage'],
                   'status': 'downloaded', 'page_mapping': 'none; verify loci on page images'}
        # Receipt first: a crash cannot leave registered text without its acquisition evidence.
        atomic_json(manifest.parent / 'receipts' / (row['id'] + '.json'), receipt)
        corpus.add_document(manifest, row['id'], name, source, {'title': row['edition']})
    finally:
        Path(name).unlink(missing_ok=True)
    return {k: receipt[k] for k in ('id', 'status', 'bytes', 'sha256')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('collection', type=Path, help='curated source collection JSON')
    parser.add_argument('--corpus', type=Path, help='local corpus.json to populate; omit to list sources')
    parser.add_argument('--id', action='append', help='fetch only these source ids (repeatable)')
    args = parser.parse_args()
    try:
        collection = json.loads(args.collection.read_text())
        rows = validate_collection(collection)
        if args.id:
            missing = set(args.id) - {r['id'] for r in rows}
            if missing:
                raise ValueError(f'Unknown source ids: {sorted(missing)}')
            rows = [r for r in rows if r['id'] in args.id]
        if not args.corpus:
            for row in rows:
                print(f"{row['id']}\t{row['edition']}\t{row['coverage']}")
            return
        results = []
        for row in rows:
            try:
                result = fetch_one(row, args.corpus)
            except (ValueError, KeyError, TypeError, OSError) as error:
                result = {'id': row['id'], 'status': 'unavailable', 'error': str(error)}
            results.append(result)
            print(json.dumps(result), flush=True)
            time.sleep(0.5)
        atomic_json(args.corpus.parent / 'fetch-results.json', {
            'collection_sha256': corpus.digest(args.collection.read_bytes()),
            'results': results, 'complete': all(r['status'] != 'unavailable' for r in results)})
        if any(r['status'] == 'unavailable' for r in results):
            parser.exit(1, 'Collection incomplete; see fetch-results.json. Unavailable is not a negative search.\n')
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
