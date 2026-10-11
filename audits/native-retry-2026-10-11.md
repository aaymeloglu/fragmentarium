# Native-resolution retry, 11 October 2026

The initial twenty-fragment batch mistakenly capped six fragments' images at
5,000 pixels wide. Fixing the acquisition helper did not correct the evidence
already used. All six affected fragments were therefore reread from new
library-native packets. This is a retry of the same six records, not six new
attempts.

## Inputs and preservation

The downloaded JPEG dimensions were checked against each library's IIIF image
metadata. Both original sampled canvases were reacquired for each fragment:

| Fragment | Image 1 pixels | Image 2 pixels |
|---|---|---|
| F-su3k | 7621 × 11444 | 7706 × 11459 |
| F-ldh6 | 5203 × 7070 | 5176 × 7019 |
| F-516x | 7857 × 6396 | 7896 × 6411 |
| F-qnuy | 7558 × 10680 | 7665 × 10874 |
| F-lwy7 | 7890 × 6365 | 7839 × 6347 |
| F-mfvu | 8688 × 5792 | 8526 × 5404 |

Three fresh image-only sessions each received two neutral packets. They had no
catalogue, prior reading or candidate-text exposure during this phase. Each
response was frozen and committed before renewed source comparison for that
fragment. The six complete responses, exact image URLs, hashes, crop coordinates
and coverage limitations are in each fragment's
`readings/batch-2026-10-11-native-retry-image-only.json`. The original smaller-image
responses remain unchanged. Whole-image overviews were used for layout;
transcription used crops from the actual native images. This remains model
research, without human palaeographic verification.

## Findings

**F-su3k:** The retry recovered additional quotation material from the clearer
second face. Its right-column list matches Augustine's *Enchiridion* 71–72;
the left column also has a Gregory *Moralia* 22.11 parallel. The coordinator
inspected three native crops against these leads. These strengthen the source
connections, but do not identify the containing florilegium.

- [Augustine, Enchiridion](https://www.augustinus.it/latino/enchiridion/enchiridion_libro.htm),
  chapters 71–72: electronic primary text, list and surrounding passage checked.
- [Gregory source parallel](https://manipulus-project.wlu.ca/MFfontes/InuidiaG.pdf):
  the scholarly Manipulus source transcription supplies the *Moralia* locus.
- [Jonas, De institutione laicali 3.10](https://www.monumenta.ch/latein/text.php?tabelle=Ionas_Aurelianensis&level=4&rumpfid=Ionas_Aurelianensis,%20De%20Institutione%20Laicali,%203,%20%20%2010):
  complete electronic chapter inspected. It reuses the Augustine list, but did
  not supply the surrounding Chrysostom/Gregory sequence.
- [Pharetra 2.25, De charitate](https://pharetra-project.wlu.ca/2.25/index.html)
  and [2.49, De eleemosyna accepta](https://pharetra-project.wlu.ca/2.49/index.html):
  all seven displayed edition images inspected. No sustained matching quotation
  sequence established. This does not exclude other chapters or recensions.

Phrase searches likewise did not establish a containing work. An attempted
Janus search returned empty output without a validated positive control and is
not treated as a successful corpus search or exclusion. Retain partial/medium.

**F-ldh6:** Both initial layouts and eight native upper/middle column crops were
inspected, including a new block after a visible gap. Tentative formal/material
vocabulary and generic transitions did not supply diagnostic consecutive prose.
Zero new source searches or edition checks; no candidate excluded. The four
additional views surveyed in the initial investigation were only 2,000-pixel
overviews and were not repeated in this retry. Retain unidentified/none.

**F-516x:** Both layouts and ten native crop regions were inspected, extending
across upper, middle and lower writing on both faces. Only isolated uncertain
words emerged. No diagnostic passage justified a new source query; zero new
source searches, and no work excluded. Retain unidentified/none.

**F-qnuy:** Both layouts, seventeen native crop regions and six grayscale/contrast
variants were inspected. Tentative *bonum honestum* remained generic, with
unresolved surrounding prose. No diagnostic query justified; zero new source
searches, and no work excluded. The coordinator additionally inspected one
lower-left native crop without recovering a usable passage. Retain
unidentified/none.

**F-lwy7:** Both layouts and twelve native crops were inspected. Renewed searches
used the tentative woman/demon/altar passage and adjoining contrition/confession
prose, including combinations of `contritio`, `femina`, `demoniacum`, `altare`,
`sine clavibus`, `magdalena` and `petrus`. Six distinct queries and targeted HTML
contexts in [Caesarius, Dialogus II](https://www.tha.de/~harsch/Chronologia/Lspost13/Caesarius/cae_dm02.html)
(5, 12, 19–22) and [III](https://www.tha.de/~harsch/Chronologia/Lspost13/Caesarius/cae_dm03.html)
(5–9) yielded thematic parallels, without the surrounding manuscript sequence.
These were selected electronic text checks, not a full collation or exclusion
of Caesarius. Retain partial/medium for the already catalogued Exultet quotation;
the containing penitential work remains unknown.

**F-mfvu:** Both layouts and ten native crops were inspected after a lossless
180-degree rotation. Six distinct queries tested the uncertain group
`multi? viri? timorati? lombar̄?` and variants such as *lombardi* and *lombardorum*.
A [Walter Map edition](https://upload.wikimedia.org/wikipedia/commons/b/ba/Gualteri_Mapes_De_nugis_curialium_distinctiones_quinque_%28IA_b28748487%29.pdf)
search-result OCR excerpt (printed p. 8) shares three words, but reinspection of
the native manuscript crop did not establish the surrounding passage. This was
not an edition-image collation or a work exclusion. Dense abbreviations remain
unresolved; retain unidentified/none. The catalogue's Ioannes de Lignano
identification belongs to the host book, not this wrapper. Two other manifest
canvases remain unchecked.

No substantive corrected transcription was adopted in these source comparisons;
the six raw retry readings are retained as given. The final batch result remains
**2 identified/high, 8 partial and 10 unidentified**. No new public page or
confidence upgrade resulted from the retry.

## Interpretation limits

Resolution, reader session and selected crops changed together, so any extra
text cannot be attributed solely to resolution. Failure to identify a fragment
on this retry does not establish that it is intrinsically unreadable or that
resolution never matters. The original cap was an avoidable execution error,
not a requirement of the revised research method.

The earlier selected batches identified 8 of 22 records; this batch initially
identified 2 of 20. Catalogue script labels include Cursiva for 6 of the earlier
22 and 12 of these 20 (including mixed labels). Ten new records lacked an
established identification chiefly because a dependable diagnostic reading was
unavailable, compared with two earlier unidentified/none entries. This points
to selection and reading as plausible bottlenecks, but neither catalogue labels
nor these different nonrandom samples provide a controlled comparison. The
publication filter did not remove the earlier eight high-confidence results.
No causal claim about the workflow's yield, chance, or HTR performance follows.

Validation: 79 tests passed. All 81 preserved readings passed checks against
merged main and the pre-retry PR head; original responses and the earlier 22
ledger entries are unchanged. The generated site still contains 10 identified
works from 42 attempted records.
