# Twelve retries for the homiletic corpus

Ranked after submitting the corpus tooling PR on 20 October 2026. These are
unresolved containing works, including ledger entries marked `partial`; none is
a new identification. Full catalogue descriptions were refreshed on 20 October.
The substantive readings and prior exclusions come from the
[research ledger](../data/fragments.json), not new transcriptions.

Use the [twelve-edition collection](../data/corpora/homiletic.json) and
[ordered-gap matcher](../tools/MATCHING.md). Begin with preserved readings and
encode only surviving spans, in order. The improvement is searching several
separated scraps against whole editions, including OCR variants, rather than
repeating the old exact phrases. No full retry was performed to create this list.

| Rank | Fragment | Unresolved material | First search enabled by the collection |
|---|---|---|---|
| 1 | [F-8dod](https://fragmentarium.ms/overview/F-8dod) | Office lesson strips; only line beginnings/ends survive. | Search ordered spans across PL 39, 94, 95, 117, 165 and *Legenda aurea*. The earlier attempt searched the Bible and CC proximity; homiliary and legendary corpora were explicitly untested. |
| 2 | [F-1jo7](https://fragmentarium.ms/overview/F-1jo7) | Homily on John 16:5-8; half-lines, no phrase longer than three words. | Build a gapped query from the consolation / `tertia pars` / reproof sequence. Compare Sunday homiliaries PL 94, 95, 117 and 165; seek the argument around the biblical words. |
| 3 | [F-cbfe](https://fragmentarium.ms/overview/F-cbfe) | Three strips on the naming of John the Baptist; another strip's source is already known. | Search the unplaced Luke 1:57-65 exposition in homiletic volumes. Treat the Ps.-Augustine App. 115 match as a control, not a new result; require agreement on the other strips. |
| 4 | [F-hz5c](https://fragmentarium.ms/overview/F-hz5c) | Passiontide homily on John 12:20-32, with Jeremiah 46:12. | Combine the argument around both passages in one ordered query against PL 39, 94, 95, 117 and 165. Voragine and Durand were already compared without agreement. |
| 5 | [F-2gqg](https://fragmentarium.ms/overview/F-2gqg) | Sunday-gospel homiliary crossing Matthew 8 to Matthew 13. | Search damaged connecting prose and the transition between consecutive Sundays across PL 94, 95, 117, 131 and 165. The Bede/Remigius borrowings alone are already known. |
| 6 | [F-plko](https://fragmentarium.ms/overview/F-plko) | Moral/literal exposition of Hebrews 11:33-34, possibly a martyrs' sermon. | Search the ordered explanatory clauses against sermon/homiliary volumes, allowing gaps. Biblical lemmata and isolated Job/Isaiah quotations must not carry the identification. |
| 7 | [F-kaqh](https://fragmentarium.ms/overview/F-kaqh) | Four leaves of weekday Lenten sermons, apparently for religious. | Use separate anchors from the ship/religio passage and another day's sermon against the homiliary volumes, then compare the order of days. Petrus Hieremia can supply later parallels, not an automatic attribution of these earlier leaves. |
| 8 | [F-2nxm](https://fragmentarium.ms/overview/F-2nxm) | Mary Magdalene and Jacob/James exposition, probably de sanctis. | Search surrounding prose for each subject across the sermon volumes; use their relative order to test collections. The relevant *Legenda aurea* and Voragine saints' sermons were already rejected. |
| 9 | [F-vl52](https://fragmentarium.ms/overview/F-vl52) | Preaching-aid article with repeated `Elemosina debet` paragraphs. | Compare ordered paragraph openings and damaged continuations across both Bromyard volumes with long-s/OCR tolerance. Bromyard's Elemosina art. 7 is only a thematic parallel already checked; a match must extend beyond it. |
| 10 | [F-36nn](https://fragmentarium.ms/overview/F-36nn) | Moral compilation: fasting, vanity, penance/vine and physician/confessor. | Search distinctive connecting prose across Bromyard I-II, testing more than one chapter. Geminiano and Rainerius parallels are already known and their editions are not added by this collection. |
| 11 | [F-k81e](https://fragmentarium.ms/overview/F-k81e) | Excerpt/exemplum compilation; several constituent sources are known. | Search unplaced transitions and rewritten exempla across PL 39/40/76 and Bromyard, using known quotations as controls. Re-finding the Dialogus or Gregory does not identify the compilation. |
| 12 | [F-63r4](https://fragmentarium.ms/overview/F-63r4) | Avarice treatise with Jerome, Seneca and Ambrose authorities. | Test the ordered chain plus explanatory prose across Bromyard with OCR tolerance. Earlier isolated Bromyard parallels did not match the context, so this is a lower-priority test of the fuller sequence. |

Rows 1-6 have the clearest connection between the prior failure and the new
search capability. Rows 9-12 are more speculative: the containing compilations
may not occur in any of these editions. A source parallel remains partial.

Published editions later than a fragment can preserve earlier works, but a later
author's similar passage cannot identify an earlier manuscript without resolving
the attribution/date conflict. Preserve the catalogue dates and alternative
explanations. Do not treat negative OCR searches as exclusions.

Image-limited records and cases waiting for a specific unscanned manuscript
(such as F-j0wm) are not priorities for this corpus. The acquisition and retrieval
control is documented in the [tooling audit](corpus-tooling-2026-10-20.md).
