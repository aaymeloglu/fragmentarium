# Research workflow

The evidence standards are in [CONVENTIONS.md](CONVENTIONS.md). The steps below
are a default order of work. Choose tools and effort to answer the question in
hand; nothing here requires using every tool. The reasons behind the rules are
in the batch notes in `audits/`.

## 1. Know what you are looking at

- **Read the catalogue record first.** The manifest's folio reference,
  reconstruction summary, dimensions and canvas labels say which object in the
  images is the catalogued fragment and what the catalogue already identifies,
  sometimes under a sibling record for the same volume. A host page or
  neighbouring leaf can be far more legible than the fragment. Record what the
  catalogue already knew.
- **Look at every leaf and face** before characterising a fragment. The second
  leaf of a bifolium can hold the passage that names the work.
- **Survey a many-leaved record before reading it.** Look at every image reduced
  (`tools/contactsheet.py`), then read headings, openings and a few connected
  passages at native size. Set a limit, test candidates as soon as there are
  searchable phrases, and stop at the limit with a note of what was not read.
- **Treat the catalogue's genre as a lead.** "Legal treatise", "musical
  treatise" and "theological commentary" have each turned out to be something
  else; do not search only within the label.

## 2. Obtain a reading

Begin with layout: orientation, columns, running titles, rubrics, initials,
glosses, question openings. They show the text layers and where to read. Read
connecting prose and citation sequences as well as lemmata. A full transcription
is not needed; record which areas were read and which were not.

For a new identification, start with a fresh image-only reader
([FIRST_READINGS.md](FIRST_READINGS.md)) and commit its response before any
search. If isolation is not available, say so and proceed with work labelled as
assisted; do not claim an independent reading. If the images cannot be inspected
at all, pursue access or textual leads and leave image-dependent claims open.

A first reading full of gaps measures that reader, not the leaf. Before a
fragment is recorded as unreadable, the coordinator looks at it at reading size:
bands of ten to twenty lines, one column wide (`tools/localcrop.py --strips`).
If connected prose is visible, get a better reading, assisted and labelled so,
and search it.

## 3. Find candidate passages

Search distinctive connected prose in the source most likely to hold the text
([RETRIEVAL.md](RETRIEVAL.md) lists them). Shared quotations and formulas can
locate a candidate but settle nothing. Once a sustained passage is found, move
to verification; more queries returning the same passage add no evidence.

- **Early prints.** A search often returns a garbled snippet and no page.
  Adding the book's title phrase can surface a volume a bare phrase misses.
  Read the page in a digitised copy (`tools/gw.py`, `tools/mdzsearch.py`) and
  confirm the scan is the same work.
- **Unprinted works.** Many sermon collections and school texts have no edition.
  A repertory incipit (Schneyer for sermons) locates the work; then find a
  digitised manuscript through the repertory or a union catalogue and compare
  the body of the text. Manuscripts catalogued under one author and title can
  carry different texts, so one witness that does not match does not exclude
  the candidate.

## 4. Verify the claim

Compare manuscript passages with the candidate on images where exact readings
are claimed, and explain the differences.

- **Which layer matched?** A quoted lemma, an embedded source, or the containing
  work. For the containing work, compare the surrounding argument, question
  order, transitions and citations. A compilation or reworking built on your
  match is a different work whose source you have found.
- **Check the attribution** of the edition or manuscript compared, separately
  from the passage match: title page, colophon, catalogue or scholarship. Keep
  "printed as X" where that is all the source supports.
- **Seek a second passage** that could confirm or challenge the identification,
  preferably one not used in discovery. There is no fixed number; choose it for
  its power to separate plausible alternatives. A further match supports the
  identification, not the accuracy of the transcription.
- **A catalogue date or script label that conflicts with a strong match** is a
  reason to look again at both. Record the conflict; do not discard the match
  or invent a new date.
- **Claims that need their own evidence:** that located books were once part of
  this volume (shared owner, sale or size makes a candidate only); that a
  manuscript is independent of a print (differences of spelling, omissions and
  better readings do not show it); date, origin, version and novelty.

A retrieval score, a fluent reconstruction or agreement between models is not
verification. Apply the status definitions in CONVENTIONS.

## 5. Record the result and stop

The task is complete when the question has a supported answer, or a clear
unresolved result saying what is missing and what would resolve it.

- Record every attempt in `data/fragments.json` with status, confidence, the
  result, the evidence and the reason for stopping (`tools/record.py`).
- Write a public report only for an identification supported at high confidence.
  Set `identified_on` to the date it was established and keep it through later
  reviews. Rebuild the site when a published result changes. Never raise
  confidence to qualify for publication.
- If the containing work is not established, leave it unresolved with a ledger
  note and move on.
- Stop retrying a blocked source or an unproductive tool when another attempt
  has no specific reason to succeed, and record it as unavailable, not as a
  negative. Reopen a line for new material or a different approach.

If no fragment is specified, `docs/burndown.html` lists candidates. Earlier
findings are in the fragment reports and `audits/`; they are not evidence that
a new reading has been verified.
