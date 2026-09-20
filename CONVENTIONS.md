# Conventions

What the labels on the index mean, and what a fragment folder has to contain before a result is
claimed. Adopted 20 September 2026 from the working rules of
[aaymeloglu/unsolved-ciphers](https://github.com/aaymeloglu/unsolved-ciphers).

## 1. Status

| Status | Meaning |
|---|---|
| **Identified** | Several consecutive lines of the fragment match a specific edition verbatim, allowing abbreviation expansion and ordinary copyist variants. Author, work, and the place in the edition are given with a link. Confidence is always `high`; nothing is called identified on a single phrase, a shared quotation, or a match of structure alone. |
| **Partial** | The sources the fragment quotes, its genre, or one of its layers is pinned to an edition, but the compiling work itself is not. The folder says exactly what is established and what is not. Confidence `medium` when a layer matches a printed text verbatim (the verses in F-jaob, the Aquinas core of F-3yl2); `low` when only genre and quoted sources are fixed. |
| **Not identified** | Genre and content are described, the searches are logged, and nothing matched. Confidence `none`. |

Biblical quotations never count as anchors; everyone quotes the Bible. The connecting prose does.

## 2. What a fragment folder contains

- `README.md`: the catalogue record as found (title, date, script, dimensions); the transcription of every side read, by line, with abbreviations expanded in parentheses; the identification with a line-by-line comparison table against the edition and a link that lets a reader check it in a minute; every corpus and edition actually searched, listed under "ruled out"; open items; and, where the catalogue's date or genre no longer fits the text, a query flagged as such rather than a verdict.
- No images. Fragmentarium and the holding libraries serve the images through IIIF; the site hotlinks thumbnails from those servers and the folder links to the record. Nothing is redistributed.
- Dates are absolute ("20 September 2026").

## 3. The index row

`data/fragments.json` holds one object per fragment: catalogue data as the record gives it, our
identification in one sentence, a one-sentence note on the evidence, the status and confidence
above, the verification link, and the IIIF thumbnail URL. `docs/_build_site.py` renders it; CI
fails if `docs/` is stale or a folder and the data file disagree.

## 4. Reporting to the library

Results are sent to fragmentarium@unifr.ch with the holding library copied, in Fragmentarium's own
field names (Title, Subtitle, Persons, Date of origin, Script Type, Reconstruction Summary,
Bibliography), so a cataloguer can paste rather than re-derive. Whether a result has been sent is
recorded in the fragment's README.
