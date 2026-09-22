# Latin retrieval trial, 22 September 2026

Purpose: test pipeline change #3 on actual downloaded texts. This is a known-answer
tooling check. The queries come from the existing source-assisted F-eo5z report,
not a new blind reading, and neither recognition accuracy nor identification
confidence is measured. The manuscript report and site are unchanged.

## Inputs and settings

- [Query with provenance and line references](retrieval-2026-09-22-query.json).
  Four diagnostic anchors in manuscript order, plus the leprosy maxim explicitly
  marked common and excluded from diagnostic ranking. No automatic expansions.
- [Hocedez 1925 OCR](https://archive.org/download/richarddemiddlet0000edga/richarddemiddlet0000edga_djvu.txt),
  entire cached volume, 1,274,797 decoded characters. SHA-256:
  `6d7634a2ec6a2bb6b97ae28661729ff9077028b0975b3c8edc2c1780d0b8ab7f`.
- [Durandus, Sentences II d.20 q.5](https://reader.lombardpress.org/text/jsnvu6/jsnvu6-d1e3228),
  fetched 22 September 2026, text extracted from `div#jsnvu6-d1e3228` only,
  excluding navigation and scripts. HTMLParser character data concatenated in
  order, adding a newline at each closing `p` or `h2`; no spelling corrections.
  6,106 decoded characters, SHA-256:
  `212424631ebb87c001fd28023e720439a69f73c8db12a45ef6e6c5b8f8e93eba`.
  Downloaded HTML SHA-256:
  `4c6e235aaada8630ded5ff4e09089dd9fc0c8c70f82e607ca3e9e5fdd6033415`.
- Python 3.13; standard-library engine; window 1,800 original characters; one
  selected passage per document; f/s OCR conflation off. Compared zero-edit
  matching with a maximum of one edit per anchor.

## Observed effect

| Input | Zero-edit diagnostic coverage | One-edit diagnostic coverage | Common maxim hits |
|---|---:|---:|---:|
| Hocedez | 3/4 | 4/4, in order | 1 |
| Durandus question | No diagnostic passage | No diagnostic passage | 1 |

The recovered fourth anchor has `recipiendum` in the query and `recipendum` in the
OCR. The tool records edit distance 1, keeps both strings, and points to original
characters `[833611, 833666)`, beginning on OCR line 20746. This is a retrieval
mismatch, not a judgment about which reading is correct.

The full four-anchor chain covers `[832271, 833666)`, 1,395 original characters,
starting on line 20725. It corresponds to the already-known material on
[Hocedez p.392, scan n405](https://archive.org/details/richarddemiddlet0000edga/page/n405/mode/1up).
The tool did not infer that printed page number. Original snippets and character
spans were checked against the input bytes decoded as UTF-8.

[Saved one-edit result](retrieval-2026-09-22.json) includes query/settings, source
hashes, all hits, normalized forms, variant choices, offsets, frequencies, and
ordered passage coverage. For this two-document corpus the four diagnostic
anchors each occur in one document. The common maxim occurs in both but contributes
zero to the score. The Hocedez chain's retrieval score is 4.919128; Durandus has no
ranked diagnostic passage. These numbers are not confidence scores.

The old helper finds four of the five supplied phrases in Hocedez but cannot
recover the `recipiendum` mismatch, does not require their order, and counts the
maxim like any other anchor. Its score is not directly comparable to the new
**diagnostic** coverage. Regression tests separately verify that reversing three
nearby anchors cannot receive full ordered coverage, that non-overlapping source
spans are required, and that the search can recover later anchors when the first
is absent.

## Reproduction

Save the two source texts above as `hocedez.txt` and `durandus.txt`, and list them
in a local corpus manifest as described in [RETRIEVAL.md](../RETRIEVAL.md).
Run from the repository root, using new output filenames:

```sh
uv run python tools/latin_search.py --corpus scratch/retrieval/corpus.json \
  --query audits/retrieval-2026-09-22-query.json --window 1800 --limit 1 \
  --output scratch/retrieval/exact.json
uv run python tools/latin_search.py --corpus scratch/retrieval/corpus.json \
  --query audits/retrieval-2026-09-22-query.json --max-edits 1 --window 1800 --limit 1 \
  --output scratch/retrieval/fuzzy.json
```

The Internet Archive wrapper was also exercised on the actual cached volume with
`--query`, `--max-edits 1`, `--window 1800`, `--limit 1`, and `--show`; it found the
same chain. Its single-document score is 3.5 because the corpus frequency weights
are different. Scores should only be compared within one corpus/settings run.

All 46 repository tests pass, including comparison of the bounded edit-distance
implementation with an exhaustive reference, trigram candidate recall under
insertions/deletions/substitutions, ordered ranking against exhaustive chains,
source-offset fidelity, partial words, expansion alternatives, common-phrase
exclusion, and CLI behavior. Site rebuild and preserved-reading checks pass.

## Limits

Two deliberately selected texts with unequal coverage do not constitute a broad
retrieval benchmark or a test of universal distinctiveness. Durandus is a
commonplace control, not a comprehensive comparison against Hervaeus or other
competing works. The positive query already contains source assistance. This
trial does not show that raw CATMuS output alone finds the passage, certify any
transcription, or complete the planned comparative pilot. Held-out verification
and confidence reporting remain changes #4 and #5.
