# Conventions

What the labels on the index mean, and what a fragment folder has to contain before a result is
claimed. Adopted 20 September 2026 from the working rules of
[aaymeloglu/unsolved-ciphers](https://github.com/aaymeloglu/unsolved-ciphers).

## 1. Status

| Status | Meaning |
|---|---|
| **Identified** | Sustained agreement in distinctive wording and sequence identifies a text in a specific edition, with abbreviations and textual variants recorded. Author, work, and the place in the edition are given with a link. Confidence is always `high`; nothing is called identified on a single phrase, a shared quotation, or a match of structure alone. |
| **Partial** | A source connection, genre, subject, or text layer has support, but the compiling work or attribution remains unresolved. The folder says exactly what is established and what is not. Confidence `medium` when a substantial source parallel or text layer is supported but the compiling work or attribution remains unresolved; `low` when the evidence chiefly establishes genre, subject, or possible source connections. |
| **Not identified** | Genre and content are described, the searches are logged, and nothing matched. Confidence `none`. |

Dating, provenance, literary dependence, recension, and witness novelty require separate evidence. A later compilation may preserve earlier material; an edition match alone does not date a manuscript. Negative searches do not establish unprinted status. Verification scope and uncollated material must be stated.

Biblical quotations never count as anchors; everyone quotes the Bible. The connecting prose does.

## 2. What a fragment folder contains

- `README.md`: the catalogue record as found (title, date, script, dimensions); the transcription of every side read, by line, with abbreviations expanded in parentheses; the identification with a line-by-line comparison table against the edition and a link that lets a reader check it in a minute; the resources searched, distinguishing actual exclusions, no-hit searches, and inaccessible or unchecked candidates; open items; and, where the catalogue's date or genre no longer fits the text, a query flagged as such rather than a verdict.
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
