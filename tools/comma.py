#!/usr/bin/env python3
"""Search the CoMMA corpus of machine-read medieval manuscripts for a fragment's text.

CoMMA (Clérice et al., LREC 2026; CC-BY 4.0) holds Kraken/CATMuS HTR text of
about 32,800 digitised manuscripts, mostly from French libraries, in Latin and
Old French. It is the only source here that searches manuscripts rather than
printed editions, so it can reach texts that were never printed. The corpus is
a 27 GB download kept outside the repository and installed only on request:

    comma.py status                 # installed, partly installed, declined, or not set up
    comma.py fetch --yes            # download (resumable, sha256-checked) and index
    comma.py fetch --parts 6 --yes  # one 2 GB part, for a trial
    comma.py decline                # remember that this machine does not want it
    comma.py search queries.json    # see tools/COMMA.md for the query format
    comma.py search --passage 'sed pone quod apparet auditorem' --passage '...'
    comma.py context 'SHELFMARK' OFFSET

The text is raw: abbreviations are not expanded and the error rate is about 10%.
A corpus word matches a query word exactly, at one edit (words of six letters
or more), or, when it carries an abbreviation sign, as a prefix of three or more
letters. Hits are scored by the best chain of matches that runs in query order
within a window, weighted by rarity, and compared with the same query's words
shuffled. A hit is a lead to collate, never an identification.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import heapq
import json
import math
from multiprocessing import Pool
import os
from pathlib import Path
import random
import re
import sys
import unicodedata
import urllib.request

DATASET = 'comma-project/comma-jsonl'
REVISION = 'dfaacb6e79900e09f14a9fcd1fb13a1d595c2e0a'
PARTS = {
    'parts_0000.jsonl': (3652497716, '6d1bf52f2f1e8f6b0810fe15eaf52e4e15847803b4973186fd2decb9c6d3a019'),
    'parts_0001.jsonl': (3293308741, 'db04b0bc0d5b2c459eae93c9e60e33618d17891b79bc3ce93ad9822ea4627c66'),
    'parts_0002.jsonl': (4696194251, '1c2f44e17d32237d628a69085a683278154a1a4b882f2fcdf916c7a764974dd4'),
    'parts_0003.jsonl': (4583788162, '025b0653002f65be43861e9805b4a130368ae458534f2f770934c060fd0c6e2e'),
    'parts_0004.jsonl': (4435360644, '8681d3a9d73b398bcdad013414a8c4ff5f97993b24fa0c8b4f5918dfa44857a2'),
    'parts_0005.jsonl': (4014749471, 'c5a57e3786566c7e9132fa451961c5ee3d20d6433c76f4276f4a82cf5ad10a0b'),
    'parts_0006.jsonl': (2145096365, '27835f2a2663e53cfd7902001a3178d68c9589e1179deae60831f93fc48d6358'),
}
DECLINED = 'DECLINED'
INDEX = 'index.json'

# MUFI signs that stand for letters; any other combining mark or private-use
# character is treated as an unexpanded abbreviation.
SPECIAL = {
    'ꝑ': 'per', 'ꝓ': 'pro', 'ꝗ': 'qui', 'ꝙ': 'quo', 'ꝯ': 'con', 'ꝰ': 'us', 'ꝫ': 'et',
    '⁊': 'et', 'ẜ': 'ser', 'ꝛ': 'r', 'ꝝ': 'rum', 'ꝭ': 'is', 'ꝟ': 'uer', 'ꝉ': 'l',
    'ꝕ': 'pre', 'ꝥ': 'th', 'ꝁ': 'k', 'ꝃ': 'k', 'ꝋ': 'o', 'ꝍ': 'o', 'ꝏ': 'oo',
}
PLAIN = {'ſ': 's', 'æ': 'ae', 'œ': 'oe', 'ꝸ': 'um', 'ȝ': 'z', 'ß': 'ss', 'v': 'u', 'j': 'i', 'ý': 'y'}
TOKEN = re.compile(r"[^\s.,;:!?/()\[\]'\"·¶|*+=<>0-9-]+")
# Frequent Latin words that cannot distinguish a text; rarer words carry the score.
STOP = set('''est sunt esse erit quod quia quam quae quid quis quo qua qui sed enim autem etiam ergo
sicut tamen ideo unde inde vel uel aut atque etc non nec neque cum per pro sub super inter ante post
apud sine ab ad de ex in et ut si hic haec hoc ille illa illud ipse ipsa ipsum iste ista istud eius
eorum earum eum eam eis ei nos uos nobis uobis nostra uestra suum sua suis sibi se dicit dicitur
item igitur nam namque nunc tunc ita sic tam quoque iam modo omnis omnia omnes deus dei deo'''.split())
MAX_RATE = 5e-5        # words commoner than this are not searched
SAMPLE_BYTES = 150_000_000


def data_dir(value=None):
    return Path(value or os.environ.get('FRAGMENTARIUM_COMMA_DIR')
                or Path.home() / '.cache' / 'fragmentarium' / 'comma').expanduser()


# ------------------------------------------------------------------ normalising
def norm_word(word):
    """A query word as read and expanded, reduced to the letters compared."""
    out = []
    for c in unicodedata.normalize('NFD', word.lower()):
        if unicodedata.category(c) != 'Mn':
            out.append(SPECIAL.get(c) or PLAIN.get(c) or c)
    return re.sub(r'[^a-z]', '', ''.join(out))


_CACHE = {}


def norm_token(raw):
    """A raw CoMMA token -> (letters, carried an abbreviation sign)."""
    hit = _CACHE.get(raw)
    if hit is not None:
        return hit
    if raw.isascii():
        hit = (re.sub(r'[^a-z]', '', raw.lower().replace('v', 'u').replace('j', 'i')), False)
    else:
        abbr, out = False, []
        for c in unicodedata.normalize('NFD', raw.lower()):
            if 0xE000 <= ord(c) <= 0xF8FF or unicodedata.category(c) == 'Mn':
                abbr = True
            elif c in SPECIAL:
                abbr = True
                out.append(SPECIAL[c])
            else:
                out.append(PLAIN.get(c, c))
        hit = (re.sub(r'[^a-z]', '', ''.join(out)), abbr)
    if len(_CACHE) > 3_000_000:
        _CACHE.clear()
    _CACHE[raw] = hit
    return hit


def deletes(word):
    return {word[:i] + word[i + 1:] for i in range(len(word))}


# ------------------------------------------------------------------ installation
def part_paths(root):
    return [root / name for name in PARTS if (root / name).exists()]


def status(root):
    index = root / INDEX
    info = json.loads(index.read_text()) if index.exists() else None
    present = [p.name for p in part_paths(root)]
    if info and info.get('revision') == REVISION and set(info.get('parts', [])) == set(present) and present:
        state = 'installed' if len(present) == len(PARTS) else 'partial'
    elif (root / DECLINED).exists() and not present:
        state = 'declined'
    elif present:
        state = 'incomplete'      # files without a finished index: rerun fetch
    else:
        state = 'absent'
    return {'state': state, 'dir': str(root), 'parts': sorted(info['parts']) if info else [],
            'documents': info.get('documents') if info else None,
            'bytes_needed': sum(size for size, _ in PARTS.values())}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1 << 22), b''):
            h.update(block)
    return h.hexdigest()


def download(url, target, size, digest, opener=urllib.request.urlopen, log=print):
    """Resume into target.part, then check size and sha256 before renaming."""
    if target.exists() and target.stat().st_size == size and sha256(target) == digest:
        return 'present'
    partial = target.with_name(target.name + '.part')
    have = partial.stat().st_size if partial.exists() else 0
    if have > size:
        partial.unlink()
        have = 0
    if have < size:
        request = urllib.request.Request(url, headers={'Range': f'bytes={have}-'} if have else {})
        with opener(request) as response:
            if have and getattr(response, 'status', 206) != 206:
                have = 0               # server ignored the range: start again
            with open(partial, 'ab' if have else 'wb') as out:
                done = have
                for block in iter(lambda: response.read(1 << 22), b''):
                    out.write(block)
                    done += len(block)
                    if done // (1 << 30) != (done - len(block)) // (1 << 30):
                        log(f'  {target.name}: {done / 1e9:.1f} of {size / 1e9:.1f} GB')
    if partial.stat().st_size != size or sha256(partial) != digest:
        partial.unlink()
        raise ValueError(f'{target.name}: size or sha256 does not match revision {REVISION[:12]}; removed, rerun fetch')
    partial.rename(target)
    return 'downloaded'


def iter_docs(path, start=0, end=None):
    """Yield (byte offset, record) for each JSON line beginning in [start, end)."""
    with open(path, 'rb') as stream:
        if start:
            stream.seek(start - 1)
            if stream.read(1) != b'\n':
                stream.readline()
        while end is None or stream.tell() < end:
            offset = stream.tell()
            line = stream.readline()
            if not line:
                break
            try:
                yield offset, json.loads(line)
            except ValueError:
                continue


SHELFMARK = re.compile(rb'"shelfmark":\s*"((?:[^"\\]|\\.)*)"')


def index_part(path):
    """Shelfmark offsets and a token-frequency sample for one part."""
    shelves, counts, tokens = [], Counter(), 0
    with open(path, 'rb') as stream:
        offset = 0
        for line in stream:
            m = SHELFMARK.search(line, 0, 4000) or SHELFMARK.search(line)
            if m:
                shelves.append((json.loads(b'"' + m.group(1) + b'"'), path.name, offset))
            offset += len(line)
    size = path.stat().st_size
    samples = 4 if size > SAMPLE_BYTES else 1   # evenly spaced samples per part
    for i in range(samples):
        start = i * size // samples
        stop = min(size, start + SAMPLE_BYTES // samples) if samples > 1 else size
        for _, doc in iter_docs(path, start, stop):
            for m in TOKEN.finditer(doc.get('text') or ''):
                letters, _ = norm_token(m.group())
                if letters:
                    counts[letters] += 1
                    tokens += 1
    return shelves, counts, tokens


def build_index(root, workers=None, log=print):
    parts = part_paths(root)
    shelves, counts, tokens = defaultdict(list), Counter(), 0
    with Pool(min(len(parts), workers or os.cpu_count())) as pool:
        for found, c, n in pool.imap_unordered(index_part, parts):
            for shelf, name, offset in found:
                shelves[shelf].append([name, offset])
            counts.update(c)
            tokens += n
    (root / 'shelfmarks.json').write_text(json.dumps(shelves, ensure_ascii=False))
    (root / 'frequencies.json').write_text(json.dumps(
        {'tokens': tokens, 'counts': {w: c for w, c in counts.items() if c >= 3}}))
    info = {'revision': REVISION, 'parts': sorted(p.name for p in parts),
            'documents': sum(len(v) for v in shelves.values())}
    (root / INDEX).write_text(json.dumps(info, indent=1))
    log(f'indexed {info["documents"]} digitisations in {len(parts)} parts')
    return info


def fetch(root, parts, log=print):
    root.mkdir(parents=True, exist_ok=True)
    (root / DECLINED).unlink(missing_ok=True)
    (root / INDEX).unlink(missing_ok=True)
    for name in parts:
        size, digest = PARTS[name]
        url = f'https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{name}'
        log(f'{name}: {size / 1e9:.1f} GB')
        log(f'  {download(url, root / name, size, digest, log=log)}')
    return build_index(root, log=log)


# ------------------------------------------------------------------ queries
def load_queries(path=None, passages=(), fragment='query'):
    """A list of {fragment, passages: [{text}]}; passages keep reading order."""
    if passages:
        raw = [{'fragment': fragment, 'passages': [{'text': p} for p in passages]}]
    else:
        raw = json.loads(Path(path).read_text())
        raw = raw if isinstance(raw, list) else [raw]
    queries = []
    for q in raw:
        if q.get('usable') is False:
            continue
        words = [w for p in q.get('passages', []) for w in map(norm_word, p['text'].split()) if w]
        if words:
            queries.append({'fragment': q.get('fragment', 'query'), 'words': words})
    return queries


def with_nulls(queries, seed=0):
    """Each query followed by its own words in a shuffled order."""
    rng = random.Random(seed)
    out = []
    for q in queries:
        shuffled = q['words'][:]
        rng.shuffle(shuffled)
        out += [q, {'fragment': q['fragment'] + '#null', 'words': shuffled}]
    return out


def build_lookup(queries, frequencies):
    total, counts = frequencies['tokens'], frequencies['counts']
    exact, near, prefix, weight = defaultdict(set), defaultdict(set), defaultdict(set), {}
    for qi, q in enumerate(queries):
        for k, w in enumerate(q['words']):
            if len(w) < 4 or w in STOP or counts.get(w, 0) / total > MAX_RATE:
                continue
            weight[w] = math.log((total + 1) / (counts.get(w, 0) + 1)) / math.log(total)
            exact[w].add((qi, k))
            if len(w) >= 6:
                for d in deletes(w):
                    near[d].add((qi, k))
            for n in range(3, len(w)):
                prefix[w[:n]].add((qi, k))
    # short prefixes that are common words in their own right only add noise
    prefix = {p: v for p, v in prefix.items() if counts.get(p, 0) / total < MAX_RATE and len(v) < 40}
    freeze = lambda d: {key: tuple(v) for key, v in d.items()}
    return {'exact': freeze(exact), 'near': freeze(near), 'prefix': freeze(prefix), 'weight': weight,
            'words': [q['words'] for q in queries]}


def match(letters, abbr, lookup):
    """Query positions a corpus token may stand for, and the match weight."""
    n = len(letters)
    if n < 3:
        return None, 0
    exact, near = lookup['exact'], lookup['near']
    if abbr:
        found = exact.get(letters) if n >= 4 else None
        if found:
            return found, 0.9
        return lookup['prefix'].get(letters), 0.6
    if n < 4:
        return None, 0
    found = exact.get(letters)
    if found:
        return found, 1.0
    if n >= 5:
        found = near.get(letters)              # the token lacks one letter
        if not found and n >= 6:
            for d in deletes(letters):          # one substituted or extra letter
                found = exact.get(d) or near.get(d)
                if found:
                    break
        if found:
            return found, 0.8
    return None, 0


def best_chain(segment, weights):
    """Highest-weight run of hits whose query positions increase."""
    dp = []
    for a, hit in enumerate(segment):
        value = hit[2] * weights[a]
        prev, best = -1, 0.0
        for c in range(a):
            if segment[c][1] < hit[1] and dp[c][0] > best:
                best, prev = dp[c][0], c
        dp.append((best + value, prev))
    a = max(range(len(dp)), key=lambda i: dp[i][0])
    score, chain = dp[a][0], []
    while a != -1:
        chain.append(segment[a])
        a = dp[a][1]
    return score, chain[::-1]


def scan(path, start, end, lookup, window=150, min_hits=4, keep=15):
    """Best windows per query in one byte range of one part."""
    weight, words = lookup['weight'], lookup['words']
    best, documents = defaultdict(list), 0
    for _, doc in iter_docs(path, start, end):
        documents += 1
        text = doc.get('text') or ''
        hits = defaultdict(list)
        for ti, m in enumerate(TOKEN.finditer(text)):
            letters, abbr = norm_token(m.group())
            found, wt = match(letters, abbr, lookup)
            if found:
                for qi, k in found:
                    hits[qi].append((ti, k, wt, m.start(), m.end()))
        for qi, found in hits.items():
            if len({h[1] for h in found}) < min_hits:
                continue
            j = 0
            for i in range(len(found)):
                while found[i][0] - found[j][0] > window:
                    j += 1
                segment = found[j:i + 1]
                if len({h[1] for h in segment}) < min_hits:
                    continue
                score, chain = best_chain(segment, [weight[words[qi][h[1]]] for h in segment])
                if len(chain) < min_hits:
                    continue
                heap = best[qi]
                if len(heap) >= keep and score <= heap[0][0]:
                    continue
                first, last = chain[0][3], chain[-1][4]
                key = (doc.get('shelfmark'), first // 2000)   # one hit per stretch of text
                record = {
                    'score': round(score, 2), 'chain': len(chain),
                    'matched': [[words[qi][h[1]], text[h[3]:h[4]], h[2]] for h in chain],
                    'shelfmark': doc.get('shelfmark'), 'biblissima_id': doc.get('biblissima_id'),
                    'manifest': doc.get('iiif_manifest'), 'notBefore': doc.get('notBefore'),
                    'pages': doc.get('pages'), 'offset': first,
                    'position': round(first / max(1, len(text)), 3),
                    'excerpt': text[max(0, first - 300):last + 300],
                }
                for n, (old, old_key, _) in enumerate(heap):
                    if old_key == key:
                        if score > old:
                            heap[n] = (score, key, record)
                            heapq.heapify(heap)
                        break
                else:
                    (heapq.heappush if len(heap) < keep else heapq.heapreplace)(heap, (score, key, record))
    return {qi: [r for _, _, r in heap] for qi, heap in best.items()}, documents


_STATE = {}


def _init(state):
    _STATE.update(state)


def _scan_task(task):
    path, start, end = task
    s = _STATE
    return scan(Path(path), start, end, s['lookup'], s['window'], s['min_hits'], s['keep'])


def search(root, queries, workers=None, window=150, min_hits=4, keep=15, chunks=8, log=print):
    info = status(root)
    if info['state'] not in ('installed', 'partial'):
        raise SystemExit(f'CoMMA is {info["state"]} in {root}; run tools/comma.py status')
    frequencies = json.loads((root / 'frequencies.json').read_text())
    queries = with_nulls(queries)
    lookup = build_lookup(queries, frequencies)
    tasks = []
    for path in part_paths(root):
        size = path.stat().st_size
        tasks += [(str(path), i * size // chunks, (i + 1) * size // chunks) for i in range(chunks)]
    state = {'lookup': lookup, 'window': window, 'min_hits': min_hits, 'keep': keep}
    merged, documents = defaultdict(list), 0
    if workers == 1:
        _init(state)
        results = map(_scan_task, tasks)
        pool = None
    else:
        pool = Pool(workers or os.cpu_count(), initializer=_init, initargs=(state,))
        results = pool.imap_unordered(_scan_task, tasks)
    try:
        for n, (found, docs) in enumerate(results, 1):
            documents += docs
            for qi, records in found.items():
                merged[qi].extend(records)
            if n % 8 == 0 or n == len(tasks):
                log(f'{n}/{len(tasks)} chunks, {documents} digitisations', file=sys.stderr)
    finally:
        if pool:
            pool.close()
            pool.join()
    out = []
    for qi in range(0, len(queries), 2):
        hits = sorted(merged.get(qi, []), key=lambda r: -r['score'])[:keep]
        null = sorted(merged.get(qi + 1, []), key=lambda r: -r['score'])
        null_top = null[0]['score'] if null else 0.0
        for h in hits:
            h['margin'] = round(h['score'] - null_top, 2)
        q = queries[qi]
        out.append({'fragment': q['fragment'], 'words': len(q['words']),
                    'searched_words': sum(1 for w in set(q['words']) if w in lookup['weight']),
                    'null_top_score': null_top, 'hits': hits})
    return {'revision': REVISION, 'parts': info['parts'], 'documents': documents,
            'settings': {'window': window, 'min_hits': min_hits}, 'queries': out}


def context(root, shelfmark, offset=None, find=None, before=1500, after=3000):
    shelves = json.loads((root / 'shelfmarks.json').read_text())
    if shelfmark not in shelves:
        raise SystemExit('shelfmark not in the installed parts')
    out = []
    for name, byte in shelves[shelfmark]:
        _, doc = next(iter_docs(root / name, byte))
        text = doc['text']
        item = {'manifest': doc.get('iiif_manifest'), 'pages': doc.get('pages'), 'chars': len(text),
                'scope': (doc.get('scopecontent') or '')[:800]}
        if find is not None:
            item['found'] = [m.start() for m in re.finditer(re.escape(find), text)]
        else:
            item['position'] = round(offset / max(1, len(text)), 3)
            item['text'] = text[max(0, offset - before):offset + after]
        out.append(item)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--dir', help='data directory (default $FRAGMENTARIUM_COMMA_DIR or ~/.cache/fragmentarium/comma)')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('status')
    f = sub.add_parser('fetch', help='download and index the corpus (27 GB for all parts)')
    f.add_argument('--parts', default='0-6', help='part numbers, e.g. 6 or 0,3 or 0-6')
    f.add_argument('--yes', action='store_true', help='confirm the download; the person must have agreed')
    sub.add_parser('decline', help='record that this machine does not want the corpus')
    s = sub.add_parser('search')
    s.add_argument('queries', nargs='?', help='query JSON (see tools/COMMA.md)')
    s.add_argument('--passage', action='append', default=[], help='one passage in reading order; repeatable')
    s.add_argument('--fragment', default='query')
    s.add_argument('--window', type=int, default=150, help='tokens spanned by one hit')
    s.add_argument('--min-hits', type=int, default=4)
    s.add_argument('--keep', type=int, default=15, help='hits kept per query')
    s.add_argument('--workers', type=int)
    s.add_argument('--limit', type=int, default=5, help='hits shown per query; JSON keeps all')
    s.add_argument('--json', action='store_true')
    c = sub.add_parser('context')
    c.add_argument('shelfmark')
    c.add_argument('offset', nargs='?', type=int)
    c.add_argument('--find', help='list offsets of this raw substring instead')
    c.add_argument('--before', type=int, default=1500)
    c.add_argument('--after', type=int, default=3000)
    args = parser.parse_args()
    root = data_dir(args.dir)

    if args.command == 'status':
        print(json.dumps(status(root), indent=1))
    elif args.command == 'decline':
        root.mkdir(parents=True, exist_ok=True)
        (root / DECLINED).write_text('CoMMA corpus declined; remove this file or run fetch to install.\n')
        print(f'recorded in {root / DECLINED}')
    elif args.command == 'fetch':
        numbers = set()
        for piece in args.parts.split(','):
            lo, _, hi = piece.partition('-')
            numbers.update(range(int(lo), int(hi or lo) + 1))
        names = [f'parts_{n:04d}.jsonl' for n in sorted(numbers)]
        unknown = [n for n in names if n not in PARTS]
        if unknown:
            parser.error(f'no such part: {", ".join(unknown)}')
        need = sum(PARTS[n][0] for n in names)
        if not args.yes:
            parser.error(f'this downloads {need / 1e9:.1f} GB into {root}; ask first, then pass --yes')
        fetch(root, names)
    elif args.command == 'search':
        if not args.queries and not args.passage:
            parser.error('give a query file or --passage')
        result = search(root, load_queries(args.queries, args.passage, args.fragment), args.workers,
                        args.window, args.min_hits, args.keep)
        if args.json:
            json.dump(result, sys.stdout, ensure_ascii=False, indent=1)
            return
        for q in result['queries']:
            print(f'{q["fragment"]}: {q["searched_words"]} searchable words, shuffled-order top {q["null_top_score"]}')
            for h in q['hits'][:args.limit]:
                print(f'  {h["margin"]:+6.2f}  score {h["score"]:5.2f}  chain {h["chain"]:2d}  {h["shelfmark"]}'
                      f'  offset {h["offset"]} (~{h["position"]:.0%} of {h["pages"]} pages)')
                print('          ' + ' '.join(m[1] for m in h['matched'][:14]))
    elif args.command == 'context':
        if args.offset is None and args.find is None:
            parser.error('give an offset or --find')
        for item in context(root, args.shelfmark, args.offset, args.find, args.before, args.after):
            text = item.pop('text', None)
            print(json.dumps(item, ensure_ascii=False))
            if text is not None:
                print(text)


if __name__ == '__main__':
    main()
