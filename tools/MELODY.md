# Searching a surviving chant melody

`cantus_melody.py` queries both parts of the [Cantus melody search](https://cantusindex.org/melody):
the melody catalogue and the network's manuscript concordances. It uses the same
requests as the web keyboard, with no account or API key. Text-only searches and
chant-sequence comparisons remain in `cantus.py`.

```sh
# A known catalogue opening, for testing the tool:
uv run python tools/cantus_melody.py dcdfdfdcfghgfg --start

# A fragment normally begins inside a melody, so anywhere is the default.
uv run python tools/cantus_melody.py edfghgfgfedcdh

# Search all diatonic pitch placements; add surviving words only if secure.
uv run python tools/cantus_melody.py edegegedghjhgh --transpose --start
uv run python tools/cantus_melody.py edfghgfgfedcdh --text 'Homo quidam'

# Save all returned candidates; replay without network access.
uv run python tools/cantus_melody.py edfghgfgfedcdh --json > results.json
uv run python tools/cantus_melody.py edfghgfgfedcdh --offline --json
```

## Reading the input

Use **Volpiano pitch positions, not A-G note names**: `9 a b c d e f g h j k l m n o p q`.
These rise by staff steps; `h` is followed by `j`, not `i`. Establish the clef and
staff position from the image. With an uncertain clef, relative staff steps plus
`--transpose` can generate candidates, but this does not establish absolute pitch.
Undiastematic neumes whose pitch cannot be read cannot supply this query.

The tool accepts 4-14 successive distinct pitches, matching the web keyboard's
range. It collapses adjacent repeated pitches and ignores accepted formatting
(hyphens, clef/bar signs 1/3/4/5 and staff breaks 7). Uppercase pitches are folded
to lowercase. Rhythm, syllable grouping, repeated-note counts and liquescence
therefore do not distinguish candidates. `--transpose` generates every diatonic
shift that fits the keyboard's `9` through `q` range and searches each placement
exactly in both indexes, including the original pitch. It does this even when
one placement returns candidates. It does not use Cantus's server transposition
flag, which [missed known candidates in a reproducible case](../audits/melody-retries-2026-10-20.md).
This preserves staff-step intervals, not chromatic intervals or rhythm.

Accidentals, missing music (`6`), question marks and unknown symbols are rejected.
Choose a continuous secure segment; do not join notes across a torn or hidden
span. Run uncertain pitch alternatives separately and retain their basis. Four
notes can return a large number of matches: use a longer surviving run or a
secure text/genre/mode filter when available.

## Results and evidence

Without `--transpose`, each index reports its server total and returned count.
With `--transpose`, records are deduplicated by result URL within each index;
the output retains every pitch placement that retrieved each candidate.
Server totals from different placements overlap, so no combined total is
claimed. The display reports unique candidates returned and how many placements
were available, and identifies failed or truncated placements. The default
display shows 20 candidates per index, while `--json` retains every candidate.
Catalogue links identify melody records; concordance
links lead to manuscript chant records with siglum, folio, incipit and encoded
melody. Do not infer a Cantus text ID from a melody ID's spelling.

Transposed JSON uses `strategy: exact-pitch-placements`. Each index's `queries`
contains the pitch `query`, diatonic `shift` from the input, server counts,
truncation and request receipt (or an unavailable error). `results[].retrieved_by`
links candidates to those queries; this records retrieval, not verified musical
agreement. The aggregate `reported_count` is null; `returned_count` counts unique
returned records. `complete` means all requests succeeded, not that unreturned
rows or unindexed chants have been searched. `truncated` remains true if any
successful placement was truncated.

Responses and retrieval receipts are cached in `scratch/cantus-melody` (override
with `--cache`). Receipts include request, timestamp and SHA-256; `--offline`
checks cached bytes. Transposition can require up to 32 requests across the two
indexes; network requests are paced, and cached requests add no delay. Existing
exact-query caches are reused. An old server-transposed response alone cannot
satisfy offline replay: each exact placement must be cached. Use a new cache
directory for a fresh survey. A blocked, changed-layout or failed response is
**unavailable**, not zero matches. If any placement fails, successful candidates
remain visible, `complete` is false, and the command exits nonzero. Truncation
alone is reported without treating the request as a failure.

A match is a candidate: inspect the manuscript image and compare more of its tune,
text and liturgical context. Different chants share melodic formulas, and a
known chant does not by itself identify the book's use or origin. Coverage is
limited to encoded melodies; no hit does not exclude a chant.

[Live controls and limitations](../audits/melody-tooling-2026-10-20.md) document
recovery of a known catalogue melody and manuscript concordances. No unidentified
fragment was identified by these controls. The
[exact-transposition regression](../audits/cantus-transposition-fix-2026-10-20.md)
records the failing case and its recovery by the current tool.
