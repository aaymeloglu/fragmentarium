#!/usr/bin/env python3
"""Rank ordered Latin passages in downloaded UTF-8 texts. Standard library only."""
import argparse
from bisect import bisect_left, bisect_right
from collections import defaultdict
from dataclasses import dataclass
import hashlib
import heapq
import json
import math
from pathlib import Path
import re
import unicodedata


@dataclass
class Normalized:
    text: str
    spans: list


def unicode_units(raw):
    start = 0
    while start < len(raw):
        end = start + 1
        while end < len(raw) and unicodedata.category(raw[end]).startswith('M'):
            end += 1
        yield start, end, unicodedata.normalize('NFC', raw[start:end])
        start = end


def normalize(raw, ocr_long_s=False):
    """Lossy search view, with every character mapped back to its original span."""
    skipped = {i for m in re.finditer(r'(?<=\w)[-\u00ad][ \t]*\r?\n[ \t]*(?=\w)', raw)
               for i in range(m.start(), m.end())}
    chars, spans = [], []
    for i, raw_end, ch in unicode_units(raw):
        if i in skipped:
            continue
        value = ch.lower().translate(str.maketrans({'ſ': 's', 'æ': 'ae', 'œ': 'oe', 'j': 'i', 'v': 'u'}))
        if ocr_long_s:
            value = value.replace('f', 's')
        for c in value:
            if not (c.isalnum() or unicodedata.category(c).startswith('M') or c == '*'):
                c = ' '
            if c == ' ' and (not chars or chars[-1] == ' '):
                if chars:
                    spans[-1] = (spans[-1][0], raw_end)
                continue
            # Fold ae/oe symmetrically, including ligatures, while retaining source offsets.
            if c == 'e' and chars and chars[-1] in 'ao':
                chars[-1] = 'e'
                spans[-1] = (spans[-1][0], raw_end)
            else:
                chars.append(c)
                spans.append((i, raw_end))
    if chars and chars[-1] == ' ':
        chars.pop()
        spans.pop()
    return Normalized(''.join(chars), spans)


def distance(a, b, limit):
    """Bounded Levenshtein distance (insertions, deletions, substitutions)."""
    if abs(len(a) - len(b)) > limit:
        return limit + 1
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [limit + 1] * (len(b) + 1)
        current[0] = i
        for j in range(max(1, i - limit), min(len(b), i + limit) + 1):
            current[j] = min(previous[j] + 1, current[j - 1] + 1,
                             previous[j - 1] + (ca != b[j - 1]))
        if min(current) > limit:
            return limit + 1
        previous = current
    return previous[-1]


class TextIndex:
    def __init__(self, raw, ocr_long_s=False):
        self.raw = raw
        self.normalized = normalize(raw, ocr_long_s)
        self.text = self.normalized.text
        self.starts = {m.start() for m in re.finditer(r'\S+', self.text)}
        self.ends = [m.end() for m in re.finditer(r'\S+', self.text)]
        self.grams = None
        self.newlines = [m.start() for m in re.finditer('\n', raw)]
        self.page_breaks = [m.start() for m in re.finditer('\f', raw)]

    def candidate_starts(self, query, edits):
        if self.grams is None:
            self.grams = defaultdict(list)
            for pos in range(len(self.text) - 2):
                self.grams[self.text[pos:pos + 3]].append(pos)
        # With <= k edits, at least one of k+1 disjoint blocks is unchanged.
        # One rare trigram per block is enough to seed that surviving block.
        candidates = set()
        for block in range(edits + 1):
            lo = len(query) * block // (edits + 1)
            hi = len(query) * (block + 1) // (edits + 1)
            offset = min(range(lo, hi - 2), key=lambda p: len(self.grams.get(query[p:p + 3], ())))
            for pos in self.grams.get(query[offset:offset + 3], ()):
                candidates.update(s for s in range(pos - offset - edits, pos - offset + edits + 1)
                                  if s in self.starts)
        return sorted(candidates)

    def find(self, query, edits):
        if '*' in query:
            # Explicit partial words, never an unbounded gap across words.
            expression = re.escape(query).replace(r'\*', r'[^\W_]*')
            for m in re.finditer(r'(?<!\S)(?=(' + expression + r')(?!\S))', self.text):
                yield m.start(), m.start() + len(m[1]), 0, 'partial-word'
        elif not edits:
            for m in re.finditer(r'(?<!\S)(?=(' + re.escape(query) + r')(?!\S))', self.text):
                yield m.start(), m.start() + len(query), 0, 'normalized-exact'
        else:
            for start in self.candidate_starts(query, edits):
                lo = bisect_left(self.ends, start + len(query) - edits)
                hi = bisect_right(self.ends, start + len(query) + edits)
                for end in self.ends[lo:hi]:
                    error = distance(query, self.text[start:end], edits)
                    if error <= edits:
                        yield start, end, error, 'normalized-exact' if not error else 'edit-distance'

    def hit(self, start, end, errors, mode, anchor, variant, query):
        raw_start = self.normalized.spans[start][0]
        raw_end = self.normalized.spans[end - 1][1]
        return {'anchor': anchor, 'variant': variant, 'normalized_query': query,
                'normalized_match': self.text[start:end], 'mode': mode, 'edits': errors,
                'start': raw_start, 'end': raw_end, 'text': self.raw[raw_start:raw_end],
                'line': bisect_left(self.newlines, raw_start) + 1,
                'form_feed_page': bisect_left(self.page_breaks, raw_start) + 1 if self.page_breaks else None}


def validate_query(query, edits, ocr_long_s):
    anchors = query['anchors']
    if not anchors or not isinstance(anchors, list):
        raise ValueError('Provide a nonempty anchors list in reading order')
    ids = []
    for anchor in anchors:
        ids.append(anchor['id'])
        if not isinstance(anchor['id'], str) or not anchor['id']:
            raise ValueError('Every anchor needs a nonempty string id')
        if not isinstance(anchor.get('common', False), bool):
            raise ValueError('common must be boolean')
        if anchor.get('common') and not anchor.get('reason'):
            raise ValueError('Common anchors need a reason for exclusion from ranking')
        if not anchor['variants']:
            raise ValueError('Every anchor needs at least one explicit variant')
        for variant in anchor['variants']:
            if not variant.get('basis') or not isinstance(variant['text'], str):
                raise ValueError('Each variant needs text and its basis')
            text = normalize(variant['text'], ocr_long_s).text
            if len(text.replace('*', '').replace(' ', '')) < 3:
                raise ValueError('Anchor variants need at least three literal characters')
            if '*' in text:
                if any(len(word.replace('*', '')) < 3 for word in text.split() if '*' in word):
                    raise ValueError('Each partial word needs at least three literal characters')
            elif edits and len(text) < 3 * (edits + 1):
                raise ValueError('Fuzzy variants need at least 3 * (max_edits + 1) characters')
    if len(set(ids)) != len(ids):
        raise ValueError('Anchor ids must be unique')


def ordered_passages(hits, anchors, weights, window, limit):
    """Maximum-weight non-overlapping anchor chains, bounded by full raw span."""
    order = {a['id']: i for i, a in enumerate(anchors)}
    diagnostic = [a['id'] for a in anchors if not a.get('common')]
    active = sorted((h for h in hits if h['anchor'] in diagnostic),
                    key=lambda h: (h['start'], h['end'], order[h['anchor']]))
    candidates = []
    seen_starts = set()
    for first, initial in enumerate(active):
        if initial['start'] in seen_starts:
            continue
        seen_starts.add(initial['start'])
        states, pending = [], []
        best_by_anchor = {}
        for position in range(first, len(active)):
            h = active[position]
            if h['start'] >= initial['start'] + window:
                break
            if h['end'] - initial['start'] > window:
                continue
            gain = weights[h['anchor']] / (1 + h['edits'])
            chain, score = [h], gain
            while pending and pending[0][0] <= h['start']:
                _, state_id = heapq.heappop(pending)
                previous, previous_score = states[state_id]
                anchor_index = order[previous[-1]['anchor']]
                old = best_by_anchor.get(anchor_index)
                if old is None or (previous_score, len(previous)) > (old[1], len(old[0])):
                    best_by_anchor[anchor_index] = (previous, previous_score)
            for anchor_index, (previous, previous_score) in best_by_anchor.items():
                if anchor_index < order[h['anchor']]:
                    candidate_score = previous_score + gain
                    if (candidate_score, len(previous) + 1) > (score, len(chain)):
                        chain, score = previous + [h], candidate_score
            heapq.heappush(pending, (h['end'], len(states)))
            states.append((chain, score))
        if states:
            chain, score = max(states, key=lambda s: (s[1], len(s[0]), -(s[0][-1]['end'] - s[0][0]['start'])))
            candidates.append({'score': round(score, 6), 'matched': len(chain),
                               'diagnostic_total': len(diagnostic), 'start': chain[0]['start'],
                               'end': chain[-1]['end'], 'matches': chain,
                               'total_edits': sum(h['edits'] for h in chain),
                               'gap_characters': [b['start'] - a['end'] for a, b in zip(chain, chain[1:])],
                               'unmatched': [a for a in diagnostic if a not in {h['anchor'] for h in chain}]})
    selected = []
    for passage in sorted(candidates, key=lambda p: (-p['score'], -p['matched'], p['end'] - p['start'], p['start'])):
        if not any(passage['start'] < other['end'] and other['start'] < passage['end'] for other in selected):
            selected.append(passage)
            if len(selected) == limit:
                break
    return selected


def search(documents, query, max_edits=0, window=6000, limit=3, ocr_long_s=False):
    if not 0 <= max_edits <= 3 or window < 1 or limit < 1:
        raise ValueError('max_edits must be 0..3; window and limit must be positive')
    validate_query(query, max_edits, ocr_long_s)
    if not documents or len({d['id'] for d in documents}) != len(documents):
        raise ValueError('Supply documents with unique ids')
    anchors = query['anchors']
    results = []
    frequencies = {a['id']: 0 for a in anchors}
    for doc in documents:
        index = TextIndex(doc['text'], ocr_long_s)
        hits = {}
        for anchor in anchors:
            found = False
            for vi, variant in enumerate(anchor['variants']):
                normalized = normalize(variant['text'], ocr_long_s).text
                for start, end, errors, mode in index.find(normalized, max_edits):
                    hit = index.hit(start, end, errors, mode, anchor['id'], vi, normalized)
                    key = (anchor['id'], hit['start'], hit['end'])
                    if key not in hits or errors < hits[key]['edits']:
                        hits[key] = hit
                    found = True
            frequencies[anchor['id']] += found
        results.append({'id': doc['id'], 'source': doc['source'],
                        'text_sha256': hashlib.sha256(doc['text'].encode('utf-8')).hexdigest(),
                        'hits': sorted(hits.values(), key=lambda h: (h['start'], h['anchor'], h['edits']))})
    weights = {a['id']: 0.0 if a.get('common') else 1 + math.log((1 + len(documents)) / (1 + frequencies[a['id']]))
               for a in anchors}
    for result in results:
        result['hit_counts'] = {a['id']: sum(h['anchor'] == a['id'] for h in result['hits']) for a in anchors}
        result['passages'] = ordered_passages(result['hits'], anchors, weights, window, limit)
    results.sort(key=lambda r: -(r['passages'][0]['score'] if r['passages'] else 0))
    return {'format': 'latin-retrieval-v1', 'status': 'candidate-retrieval-only', 'query': query,
            'settings': {'max_edits': max_edits, 'window_raw_characters': window, 'limit_per_document': limit,
                         'ocr_long_s': ocr_long_s, 'normalization': 'latin-mapped-v1'},
            'corpus_size': len(documents), 'document_frequency': frequencies, 'weights': weights,
            'documents': results}


def literal_query(phrases):
    return {'anchors': [{'id': f'a{i}', 'variants': [{'text': p, 'basis': 'caller-supplied search phrase'}]}
                        for i, p in enumerate(phrases, 1)]}


def read_utf8(path):
    # read_text's universal newline conversion would invalidate original offsets/hashes.
    return Path(path).read_bytes().decode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, required=True, help='JSON documents: id, path, public source citation')
    parser.add_argument('--query', type=Path, required=True, help='JSON anchors in reading order with explicit variants')
    parser.add_argument('--max-edits', type=int, default=0)
    parser.add_argument('--window', type=int, default=6000, help='maximum full passage span in original characters')
    parser.add_argument('--limit', type=int, default=3, help='non-overlapping passages per document')
    parser.add_argument('--ocr-long-s', action='store_true', help='also conflate OCR f with s (lossy, opt-in)')
    parser.add_argument('--output', type=Path, help='new output file; defaults to stdout')
    args = parser.parse_args()
    try:
        manifest = json.loads(read_utf8(args.corpus))
        documents = [{'id': d['id'], 'source': d['source'],
                      'text': read_utf8(args.corpus.parent / d['path'])} for d in manifest['documents']]
        query_text = read_utf8(args.query)
        result = search(documents, json.loads(query_text), args.max_edits, args.window, args.limit, args.ocr_long_s)
        result['query_sha256'] = hashlib.sha256(query_text.encode('utf-8')).hexdigest()
        output = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            with args.output.open('x', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output, end='')
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
