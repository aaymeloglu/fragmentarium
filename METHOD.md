# Research workflow

The required evidence standards are in [CONVENTIONS.md](CONVENTIONS.md).
Choose tools, search order, and effort to answer the current question. The
workflow below is a default, not a requirement to exhaust every available tool.

## 1. Set the scope and obtain a reading

Identify the question and the passages needed to answer it. For identification,
begin with an image-only overview of orientation and layout. Running titles,
rubrics, initials, underlining, glosses and question openings can identify the
text layers and guide crop selection. Include connecting commentary and citation
sequences as well as prominent lemmata. A full-leaf transcription is not a
prerequisite. Expand coverage when the evidence calls for it or the task
requests it. Record which areas were read and which remain unchecked.

For new identifications and re-adjudications, start with a fresh image-only
reader using [FIRST_READINGS.md](FIRST_READINGS.md). Preserve and commit its
response before candidate discovery. If session isolation is unavailable, record
that limitation and proceed with explicitly assisted work; do not manufacture
an independence attestation or keep restarting without a workable isolation
mechanism. If images cannot be inspected, pursue access or textual leads, but
leave image-dependent claims unresolved.

A first reading full of gaps is a measurement of that reader, not of the leaf.
Before recording a fragment as unreadable, the coordinator looks at the image at
reading size: bands of ten to twenty lines, one column wide, enlarged until the
letters are large (`tools/localcrop.py --strips` cuts these from a cached native
image). If connected prose is visible there, obtain a better reading, assisted
if necessary and labelled so, and search it; do not let an isolated reader's
`[illegible]` decide that no search is justified. The recheck in
[audits/recheck-2026-10-11.md](audits/recheck-2026-10-11.md) found three
identifications among records stopped this way.

[HTR](HTR.md) is an optional second measurement. Try it when it could clarify
uncertain text or when the task calls for a comparison. Inspect segmentation
before relying on its output. If it fails, try a targeted correction when there
is a plausible layout or input problem; otherwise save the failure and continue.
Further model or segmentation tuning is separate work unless needed for the task.

## 2. Find candidate passages

Start with the resource most likely to contain the text: a genre-specific corpus,
a known edition, Google Books, Internet Archive, or Corpus Corporum. There is no
mandatory search order or requirement to use every service. Prefer distinctive
connecting prose; shared quotations can help locate candidates but cannot settle
attribution.

Use [RETRIEVAL.md](RETRIEVAL.md) for search setup, spelling/expansion alternatives,
noisy OCR, or comparisons across candidate texts. Simple direct searches need
not become a corpus-building exercise. Once a plausible sustained passage is
located, shift effort to verification. More query variants returning the same
passage add little evidence.

Catalogue genre labels are leads to test. In one batch a "legal treatise" was a
commentary on Priscian, a "treatise on logic" was a grammatical summa, and a
suspected Psalm 118 commentary was on Psalm 50; searching only within the
catalogued genre would have missed each.

For early printed books, Google Books often returns a garbled snippet and no
page. Adding the book's title phrase to the query can surface a volume that a
bare phrase search misses. Treat the snippet as a lead and read the page:
`tools/gw.py <GW number>` lists libraries holding a digitised copy, and the GW
number is given in ISTC and most incunable catalogues. Confirm the scan is the
same work, since unrelated books share short titles.

Many sermon collections and school texts have no edition. A repertory incipit
(Schneyer for sermons) can locate the work; then find a digitised manuscript of
it through the repertory's manuscript list or a union catalogue (Biblissima,
ARCA, DigiVatLib, e-codices, MDZ) and compare the bodies of the text on the page
images. An incipit and explicit matched against a repertory are a lead; the
collation carries the identification. Manuscripts catalogued under one author and
title can carry different texts, so a candidate tested in one witness of an
unprinted work is not excluded by that witness alone.

Read every leaf and face of a fragment before characterising it. A bifolium's
second leaf can hold the passage that names the work.

## 3. Verify the proposed claim

Compare the selected manuscript passages with the candidate edition, inspecting
images for claims about exact readings. Explain significant differences and
consider shared sources or compilations where relevant. First establish which
layer matched: a quoted lemma, an embedded source, or the containing commentary.
For the containing work, compare the surrounding argument, question order,
transitions and citation sequence. Use these to distinguish the closest plausible
reworking or compilation; an accessible edition is not automatically the best
candidate. No exhaustive survey of every possible author is required. Another reader or model
can challenge the conclusion when useful; record what it actually checked.
Apply the status definitions in CONVENTIONS rather than treating a retrieval
score, fluent reconstruction, or agreement between models as verification.

Check the edition's author/work attribution separately from the passage match.
Use its title page or colophon and a reliable bibliographic record or scholarly
attribution discussion where needed. Record the edition, locus and basis for the
attribution. If the source only supports "printed as X", keep that qualification;
a matching passage cannot settle disputed authorship.

A catalogue date or script label that conflicts with a strong textual match is
a reason to inspect the metadata and image again. Do not automatically discard
the match or invent a replacement date. Record the conflict separately, and seek
specialist assessment if dating is necessary to settle the identification.

When an identification rests on the passage used to discover the candidate,
look for another available passage that could confirm or challenge it. Prefer
material not used in discovery when practical. Choose the check for its ability
to distinguish plausible alternatives; record its scope and remaining limitations.
Use judgment about whether another check would add evidence; there is no fixed
number of passages or lines, or requirement to use another side of the fragment.

A passage already examined against the candidate is not held-out evidence.
An additional match supports identification, not automatic certification of the
transcription, authorship, or originality of the work.

## 4. Record the result and stop

The task is complete when the scoped question has a supported answer, or a clear
unresolved result explaining the missing evidence and what would resolve it.
Record every attempt in `data/fragments.json`, with confidence, the candidate or
result, evidence, and the reason for stopping in a brief note. If the containing
work is not established, leave it unresolved and move on; a source or genre match
does not require a public writeup. Revisit when new evidence or a different
approach justifies the effort.

Write a concise public report only for an identified work supported at high
confidence under CONVENTIONS. Link the diagnostic manuscript and edition passages,
explain material differences, and keep extended readings in the details. Set
`identified_on` to the date that identification was established; preserve it
through later reviews, tracked separately by `examined`. Rebuild the site when a
published result changes. Never raise confidence merely to qualify for publication.

Stop retrying a blocked source or unproductive tool when another attempt has no
specific reason to succeed. Record unavailable sources and inconclusive searches;
continue with other evidence where useful. Reopen a line of inquiry for new
material or a materially different approach, not to satisfy a tool checklist.

If no fragment is specified, `docs/burndown.html` offers candidate priorities.
Prior research and validation history are in [REVIEW.md](REVIEW.md) and `audits/`;
they are not evidence that a new reading has already been verified.
