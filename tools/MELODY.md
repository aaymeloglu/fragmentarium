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

# Also ask for transposed matches; add surviving words only if secure.
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
therefore do not distinguish candidates. Transposition uses Cantus's server
semantics; it is not a promise of chromatic or rhythm-aware matching.

Accidentals, missing music (`6`), question marks and unknown symbols are rejected.
Choose a continuous secure segment; do not join notes across a torn or hidden
span. Run uncertain pitch alternatives separately and retain their basis. Four
notes can return a large number of matches: use a longer surviving run or a
secure text/genre/mode filter when available.

## Results and evidence

Each index reports its own total and returned count; a truncated response is
labelled explicitly. The default display shows 20 rows per index, while `--json`
retains every returned row. Catalogue links identify melody records; concordance
links lead to manuscript chant records with siglum, folio, incipit and encoded
melody. Do not infer a Cantus text ID from a melody ID's spelling.

Responses and retrieval receipts are cached in `scratch/cantus-melody` (override
with `--cache`). Receipts include request, timestamp and SHA-256; `--offline`
checks cached bytes. Use a new cache directory for a fresh survey. A blocked,
changed-layout or failed response is **unavailable**, not zero matches. If one
index fails, successful results from the other remain visible and the command
exits nonzero.

A match is a candidate: inspect the manuscript image and compare more of its tune,
text and liturgical context. Different chants share melodic formulas, and a
known chant does not by itself identify the book's use or origin. Coverage is
limited to encoded melodies; no hit does not exclude a chant.

[Live controls and limitations](../audits/melody-tooling-2026-10-20.md) document
recovery of a known catalogue melody and manuscript concordances. No unidentified
fragment was identified by these controls.
