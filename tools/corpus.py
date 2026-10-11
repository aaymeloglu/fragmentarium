#!/usr/bin/env python3
"""Register downloaded UTF-8 texts in a reusable, checksummed local corpus.

No network requests. Page ranges are supplied evidence, never inferred foliation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit


def digest(data):
    return hashlib.sha256(data).hexdigest()


def public_url(value):
    if not isinstance(value, str):
        raise ValueError('Source citations must be public HTTP(S) URLs')
    url = urlsplit(value)
    if url.scheme not in {'http', 'https'} or not url.netloc or url.username or url.password:
        raise ValueError('Source citations must be public HTTP(S) URLs without credentials')
    return value


def validate_metadata(doc):
    """Optional edition metadata and non-overlapping source spans in original text."""
    if 'edition' in doc:
        edition = doc['edition']
        if not isinstance(edition, dict) or not isinstance(edition.get('title'), str) or not edition['title'].strip():
            raise ValueError('Edition metadata needs a title')
        if 'attribution_source' in edition:
            public_url(edition['attribution_source'])
    if 'pages' not in doc:
        return
    if not isinstance(doc['pages'], list):
        raise ValueError('pages must be a list of source ranges')
    previous_end = 0
    for page in doc['pages']:
        if (not isinstance(page, dict) or type(page.get('start')) is not int
                or type(page.get('end')) is not int
                or not previous_end <= page['start'] < page['end'] <= len(doc['text'])
                or not isinstance(page.get('locus'), str) or not page['locus'].strip()):
            raise ValueError('Page ranges need ordered non-overlapping original-text offsets and a locus')
        public_url(page.get('url'))
        previous_end = page['end']


def page_references(doc, hit):
    """Only mapped overlaps; absence means the physical page is not established."""
    return [dict(p, matched_start=max(hit['start'], p['start']), matched_end=min(hit['end'], p['end']))
            for p in doc.get('pages', []) if p['start'] < hit['end'] and hit['start'] < p['end']]


def load_documents(manifest_path):
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_bytes().decode('utf-8'))
    documents = []
    for item in manifest['documents']:
        raw = (manifest_path.parent / item['path']).read_bytes()
        if 'sha256' in item and digest(raw) != item['sha256']:
            raise ValueError(f"Cached text changed: {item['id']}")
        doc = {k: v for k, v in item.items() if k not in {'path', 'sha256'}}
        doc['text'] = raw.decode('utf-8')  # No newline conversion: ranges and hashes use exact bytes.
        validate_metadata(doc)
        documents.append(doc)
    return documents


def add_document(manifest_path, identifier, text_path, source, edition=None, pages=None):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', identifier):
        raise ValueError('Invalid document id')
    public_url(source)
    raw = Path(text_path).read_bytes()
    text = raw.decode('utf-8')
    if not text.strip() or re.search(r'<(?:!doctype\s+html|html|head|body)\b', text[:4096], re.I):
        raise ValueError('Expected UTF-8 plain text, not an empty file or an HTML response')
    row = {'id': identifier, 'path': f'texts/{digest(raw)}.txt', 'source': source, 'sha256': digest(raw)}
    if edition is not None:
        row['edition'] = edition
    if pages is not None:
        row['pages'] = pages
    validate_metadata(dict(row, text=text))
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    lock = manifest_path.with_name(manifest_path.name + '.lock')
    # Prevent concurrent registrations from silently dropping one another's entries.
    with lock.open('x'):
        try:
            manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'documents': []}
            if any(d['id'] == identifier for d in manifest['documents']):
                raise ValueError('Document id already registered; use a new id for a revised text')
            cached = manifest_path.parent / row['path']
            cached.parent.mkdir(exist_ok=True)
            if cached.exists():
                if cached.read_bytes() != raw:
                    raise ValueError('Cached text checksum mismatch')
            else:
                with cached.open('xb') as stream:
                    stream.write(raw)
            manifest['documents'].append(row)
            # Keep the prior manifest intact if writing or validation fails.
            fd, name = tempfile.mkstemp(dir=manifest_path.parent, prefix='.corpus-', suffix='.json')
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                    json.dump(manifest, stream, ensure_ascii=False, indent=2)
                    stream.write('\n')
                os.replace(name, manifest_path)
            finally:
                Path(name).unlink(missing_ok=True)
        finally:
            lock.unlink()
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, required=True)
    parser.add_argument('--id', required=True)
    parser.add_argument('--text', type=Path, required=True, help='already downloaded UTF-8 plain text')
    parser.add_argument('--source', required=True, help='public source citation')
    parser.add_argument('--edition', help='edition title and imprint, as checked')
    parser.add_argument('--attribution-source', help='title page, catalogue or scholarly attribution URL')
    parser.add_argument('--pages', type=Path, help='JSON list of checked original-text spans: start, end, locus, url')
    args = parser.parse_args()
    try:
        if args.attribution_source and not args.edition:
            raise ValueError('--attribution-source requires --edition')
        edition = {'title': args.edition} if args.edition else None
        if args.attribution_source:
            edition['attribution_source'] = args.attribution_source
        pages = json.loads(args.pages.read_text()) if args.pages else None
        print(json.dumps(add_document(args.corpus, args.id, args.text, args.source, edition, pages), ensure_ascii=False))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
