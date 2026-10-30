# Evidence and reporting standards

These are the required standards for research claims. [METHOD.md](METHOD.md)
provides adaptable research tactics; the tool manuals describe commands.

## Evidence rules

- Base transcription claims on inspected manuscript images. Keep uncertainty,
  gaps, corrections, and physical line references visible. Distinguish raw
  recognition, proposed expansions, and search-normalized text.
- An independent image-only reading uses a fresh reader with no proposed answer,
  earlier transcription, edition, or other reader's output. Preserve the complete
  response and its input provenance, and commit it before candidate searching or
  comparison. [FIRST_READINGS.md](FIRST_READINGS.md) gives the procedure. If
  independence cannot be established, label the work assisted and state the
  limitation; do not claim a blind reading. Existing reports are not
  retrospectively certified as independent.
- Never edit or delete a preserved reading. Save substantive assisted revisions
  separately, citing the readings and sources used. Corrections to saved metadata
  also belong in a new record or audit note. Checksums protect preservation, not
  the truth of a reading or the reader's isolation.
- A search hit, retrieval score, common phrase, or agreement between readers
  establishes a lead, not an identification. Support identification with sustained
  distinctive wording and sequence, documenting differences. Shared biblical
  quotations and formulas are not diagnostic anchors on their own. Distinguish
  a matched source within the fragment from the work containing it: explain why
  the surrounding structure and prose favor that work over plausible reuse.
- Support the edition's author/work attribution with a bibliographic source,
  title page, colophon or scholarly discussion as appropriate. Cite that evidence
  separately from the matched passage; retain disputed or provisional attribution.
  Catalogue dating is evidence to examine, not an automatic veto of a text match.
- Say what was checked and what was not, including whether comparison used images,
  OCR, snippets, or secondary paraphrase. Do not describe LLM checks as human
  palaeographic verification. Distinguish a genuine exclusion from a no-hit search
  or an unavailable source; unsuccessful search does not establish unprinted status.
- Dating, provenance, leaf order, literary dependence, recension, and witness
  novelty need their own evidence. Identification does not certify transcription
  accuracy or those additional claims. Limit each conclusion to its support.

## Identification status and confidence

The research ledger's `status` and `confidence` describe support for the identification
claim only, including a provisional connection when status is partial. They do
not grade transcription accuracy, verification coverage, dating, or witness
novelty. A well-supported identification can coexist with a poor transcription.
Keep these labels tied to the stated identification rather than averaging the
strength of unrelated claims:

| Status | Meaning |
|---|---|
| **Identified** | Sustained agreement in distinctive wording and sequence identifies a text in a specific edition, with abbreviations and textual variants recorded. Give the author, work, locus, and a checkable link. Publication requires confidence `high`. |
| **Partial** | A source connection, genre, subject, or text layer has support, but the compiling work or attribution remains unresolved. Use `medium` for a substantial source parallel or text layer, `low` for chiefly genre, school, or author leads. |
| **Not identified** | Describe the fragment and searches, but no identification is established. Confidence `none`. |

Before recording `identified`, reread the report's own limits, gaps and
unexplained observations, and let them govern the claim. If the identified
text is on an object other than the one catalogued, the record is not
identified. If one piece or face is matched only in outline, or its placement
needs an anomaly the report leaves unexplained, withdraw the claim for that
piece; the record keeps its status only on what remains.

### Archival documents

For a deed, charter, letter or grant the identification is the document's
regest: issuer, addressee or beneficiary, legal action, place and date.
**Identified** needs the text read on the image, with the dating clause
converted. An element the image does not give (a year cut away, a feast name
under tape) is supplied from a named source and labelled as supplied, or
reported as lost. A single uncertain or lost element, such as one letter of a
surname, an illegible place or sum, or a burnt dating clause, is stated in the
regest and does not make the result partial when the rest of the text is read
securely. No reading may rest on the outside evidence used to confirm it. The
result is **partial** when the action or a party cannot be established, or
when much of the text is unread.

An independent record of the same act (an edition, a printed or online regest,
an inventory entry, another copy) is corroboration, reported separately with
its citation; it is not required, since a unique original can be understood
without one. A sheet carrying several documents is reported per document, and
counts say how many distinct acts they represent. A transcription attached to
the catalogue record is the same object, not an independent record.

## Publication

Publish only entries with `status: identified` and `confidence: high`. The site
shows the identification and `identified_on` date; confidence stays in the ledger.
Partial source connections and unsuccessful attempts need only a short ledger
note recording evidence and the stopping reason. Existing research reports and
preserved readings remain available in Git. Do not turn a partial result into
an identification to obtain a public page.

The site and its count show this project's findings only. When the scholarship
has already identified the text of this very fragment (an edition of the leaf, a
repertory entry naming its shelfmark) and the catalogue record lacks it, record
the result as identified, add `known_from` with the citation, and keep the
report in `fragments/`. Such a row gets no public page and is not counted. An
unknown author or a single surviving copy does not make an identification
partial.

`identified_on` is an ISO date (`YYYY-MM-DD`) for the original establishment of
the stated identification, or null for an unresolved attempt. Later reviews
update `examined`, not `identified_on`. If the identification changes to a different
work, record the new identification's date; retain the earlier finding in history.

## Writeup: distinguish the claim, the reading, and the checks

Write current fragment pages as standalone accounts of the present findings and
evidence. Keep review dates, changes to past claims, and run history in audits or
preserved records, rather than narrating them in the report.

Open a new or revised report with a concise evidence summary. Three short bullets
or a paragraph are enough; no additional scores or fixed table are required:

- **Identification:** state the proposed work or source connection, its status
  and identification confidence, the diagnostic basis, and material alternatives.
- **Transcription:** describe the reading's basis (image-only or assisted),
  the passages covered, and known errors or unresolved readings. State who reviewed
  which lines against the manuscript image; if accuracy has not been assessed,
  say so. Identification confidence does not transfer to the transcription.
- **Verification:** specify which manuscript and edition passages were compared,
  by whom, and using what evidence: images, OCR, snippets, or a secondary account.
  State gaps in coverage. Expert support for an attribution is not approval of
  every transcribed word; model agreement is not human review.

For each main identification claim, give enough linked evidence to inspect it:
selected manuscript lines and their image/crop reference, the candidate text's
edition/locus and link, and significant agreements or differences. Distinguish
literal quotations from paraphrases or thematic parallels. Common formulas may
explain how a candidate was found, but the diagnostic comparison must carry the
identification. Avoid "verbatim" or "line-by-line verified" beyond the passages
actually checked. Link preserved raw readings and label unverified machine text.

Address dating, leaf order, dependence, recension, or novelty separately **when
making those claims**, with their own basis and limits. Otherwise omit them; this
is not a checklist requiring research into every dimension. Report the checks
performed rather than creating new searches or verification work to fill headings.
Missing evidence remains explicit and limits the conclusion. No character/word
accuracy rate should be invented without a suitable checked reference.

## Report and record format

`fragments/<F-id>/README.md` is required for published identifications. It contains
the catalogue details, scoped reading and comparison, sources, result, and
unresolved questions. Include the lines needed
to assess the claim, with proposed expansions in parentheses and uncertainty
marked. State the coverage; do not imply unread sides were transcribed. Provide
an edition/facsimile link and locus, and use a comparison table when it helps.
Dates are absolute, for example "22 September 2026".

Link preserved `readings/*.json` records by their actual kind: image-only or
source-assisted (two records of a September 2026 recognition trial are kind `htr`). Use the preservation commands when those records exist;
If isolation was unavailable and
there is no independent base record, keep the assisted text and its provenance
in the report or a separate labelled file outside `readings/`; the CLI cannot
create an assisted record without a base. The report states the missing
independent evidence. Do not fabricate a base to satisfy the schema.

`data/fragments.json` holds catalogue data, identification, note, status,
identification confidence, links, order, identification date, and examination date. `docs/_build_site.py` renders the
site; CI checks record preservation, data consistency, and generated pages.

When outreach is explicitly requested, use Fragmentarium's catalogue field names
(Title, Subtitle, Persons, Date of origin, Script Type, Reconstruction Summary,
Bibliography), address fragmentarium@unifr.ch with the holding library copied,
and record whether the report was sent.
