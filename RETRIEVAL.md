# Candidate retrieval from imperfect Latin readings

Use `searchd.py` for Google Books, Internet Archive, and Corpus Corporum discovery
as before. Download the candidate texts and compare passages with the shared
standard-library engine in `tools/latin_search.py`. It adds no dependencies,
service, or environment. Use UTF-8 plain text, not HTML/XML markup.

Freeze the independent readings first, following `FIRST_READINGS.md` and `HTR.md`.
Select anchors in their manuscript reading order. Carry their line references and
reading/expansion provenance into the query. Do not replace an uncertain reading
with the candidate edition's wording. If an edition informs a query variant,
label that basis explicitly; it is source-assisted retrieval.

## One Internet Archive volume

The existing command uses the new engine:

```sh
uv run python tools/ia_cluster.py richarddemiddlet0000edga \
  'materia ipsius asini' 'denudatio ab omni alia forma' --show
```

Use `--max-edits 1` to allow one character insertion, deletion, or substitution per
anchor. `--window 1800` bounds the **entire passage** in original characters.
The best chain can start at any anchor, but matches must be in query order and
must not overlap. Missing anchors are reported. Results include original offsets,
line numbers, the matched variant, and edit counts. `--json` saves the full result
via shell redirection. `--cache-dir` chooses the OCR cache.

This changes the old score's meaning: nearby phrases in the wrong order no longer
receive full coverage. Long-s (`ſ`) still matches `s`; conflating OCR `f` with `s`
is now an explicit `--ocr-long-s` option because it also creates false matches.

## Competing texts and uncertain expansions

A query JSON lists anchors in reading order. Each variant is a **whole alternative
phrase**, supplied by the researcher; the tool does not invent expansions or
combine alternatives into a new reading. `line_ref` and other provenance fields
are retained unchanged. For example:

```json
{
  "source": "Preserved reading record and checksum, or explicit source-assisted basis",
  "anchors": [
    {
      "id": "maxim",
      "common": true,
      "reason": "Shared maxim; not diagnostic of a work",
      "variants": [{"text": "leprosus generat leprosum", "basis": "Proposed expansion of the reading"}]
    },
    {
      "id": "passage",
      "line_ref": "image-001.jpg:L020",
      "variants": [
        {"text": "mater* ipsius asini", "basis": "Uncertain word ending"},
        {"text": "materia ipsius asini", "basis": "Alternative proposed expansion; unverified"}
      ]
    }
  ]
}
```

`*` matches within a single word. Each partial word needs at least three literal
characters. Partial-word variants use only wildcard matching, even when fuzzy
search is enabled; they do not also receive edit tolerance. A match reports the
best variant (fewest edits, then first supplied) when alternatives hit the same
span. Punctuation separates words; it is not a wildcard for missing text.

A corpus JSON lists downloaded texts, with paths relative to the manifest:

```json
{
  "documents": [
    {"id": "candidate", "path": "candidate.txt", "source": "Public edition/OCR URL"},
    {"id": "competitor", "path": "competitor.txt", "source": "Public edition/OCR URL"}
  ]
}
```

```sh
uv run python tools/latin_search.py --corpus scratch/corpus.json \
  --query scratch/query.json --max-edits 1 --window 1800 \
  --output scratch/retrieval.json
```

Output files must be new. Inputs are never rewritten. The JSON includes the exact
query, its file hash, source citations, decoded-text hashes, every hit and its
original excerpt, normalized query/match, and ranked non-overlapping passages per
document. A source offset is a zero-based Unicode character index, with an
exclusive end, in that exact decoded UTF-8 text. Newlines are preserved. Lines
are one-based; `form_feed_page` is a one-based OCR section only when form feeds
exist, otherwise null. It is **not** a printed page or an Internet Archive scan
number. Use edition facsimiles to establish the physical locus.

## Matching and ranking

The separate search view uses Unicode NFC/lowercase, `ſ/s`, `u/v`, `i/j`, and
`ae/oe/æ/œ/e` folding. It joins hyphens at line breaks and collapses punctuation
and whitespace. Combining abbreviation marks are retained, not silently expanded.
Every normalized character maps to its original span, so lossy search rules never
destroy the source. `--ocr-long-s` also conflates `f/s` and records that choice.
These equivalences deliberately broaden retrieval; they are not editorial rules.

Fuzzy search uses character trigrams to locate candidate spans, followed by
bounded Levenshtein verification at word boundaries. `--max-edits` is 0 by default,
with a maximum of 3 per whole anchor. Fuzzy phrases need at least
`3 * (max_edits + 1)` normalized characters. Edit distance is measured **after**
normalization; zero edits is not a claim of verbatim agreement. This is intended
for selected anchors in a modest set of candidate volumes, not a universal index.

For N supplied documents, each diagnostic anchor has weight
`1 + log((N + 1) / (document_frequency + 1))`. Frequency counts documents containing
any accepted variant, using the selected matching rules. A chain sums
`weight / (1 + edits)` for its non-overlapping, ordered anchor matches. Reports show
coverage, missing anchors, total edits, and intervening character gaps. Explicit
`common: true` anchors have zero weight and do not contribute to diagnostic
coverage or form a ranked passage on their own. Their hits remain visible.

Supply one document per work when practical; duplicated editions and unequal
text coverage distort frequency. Rarity within the supplied corpus is not
universal rarity. A two-document trial cannot establish that a phrase is unique.
The score is a retrieval aid, never a confidence percentage or identification
threshold. Inspect intervening prose, omissions, quotations, shared sources,
compilations, and manuscript/edition images. No hit does not exclude a work.

The [F-eo5z tooling trial](audits/retrieval-2026-09-22.md) records the effect on an
actual known passage and a commonplace control. It is not the planned pilot or a
fresh adjudication. Held-out verification and confidence changes remain separate
pipeline steps.
