# Research workflow

The required evidence standards are in [CONVENTIONS.md](CONVENTIONS.md).
Choose tools, search order, and effort to answer the current question. The
workflow below is a default, not a requirement to exhaust every available tool.

## 1. Set the scope and obtain a reading

Identify the question and the passages needed to answer it. For identification,
start with legible, potentially distinctive spans; a full-leaf transcription is
not a prerequisite. Expand coverage when the evidence calls for it or the task
requests it. Record which areas were read and which remain unchecked.

For new identifications and re-adjudications, start with a fresh image-only
reader using [FIRST_READINGS.md](FIRST_READINGS.md). Preserve and commit its
response before candidate discovery. If session isolation is unavailable, record
that limitation and proceed with explicitly assisted work; do not manufacture
an independence attestation or keep restarting without a workable isolation
mechanism. If images cannot be inspected, pursue access or textual leads, but
leave image-dependent claims unresolved.

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

## 3. Verify the proposed claim

Compare the selected manuscript passages with the candidate edition, inspecting
images for claims about exact readings. Explain significant differences and
consider shared sources or compilations where relevant. Another reader or model
can challenge the conclusion when useful; record what it actually checked.
Apply the status definitions in CONVENTIONS rather than treating a retrieval
score, fluent reconstruction, or agreement between models as verification.

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
Publish the comparison and limitations in the fragment report; update the index
and site when the result changes. A partial result is an acceptable outcome.

Stop retrying a blocked source or unproductive tool when another attempt has no
specific reason to succeed. Record unavailable sources and inconclusive searches;
continue with other evidence where useful. Reopen a line of inquiry for new
material or a materially different approach, not to satisfy a tool checklist.

If no fragment is specified, `docs/burndown.html` offers candidate priorities.
Prior research and validation history are in [REVIEW.md](REVIEW.md) and `audits/`;
they are not evidence that a new reading has already been verified.
