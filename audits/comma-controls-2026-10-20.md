# CoMMA manuscript-text search: blind controls, 20 October 2026

`tools/comma.py` was run against the full CoMMA corpus (revision
`dfaacb6e`, seven parts, 32,763 digitisations) with queries built from the
**image-only first readings** of identified fragments. These readings were
frozen before any search, so they contain no wording taken from the
identified source. The queries are in
[`comma-controls-2026-10-20/queries.json`](comma-controls-2026-10-20/queries.json).

Of the 53 identified records, 37 readings held enough secure words to query.
F-szlk was excluded because its passages were not labelled as image-only,
which leaves 36 controls. One pass with default settings took 14 minutes on an
18-core laptop. Every hit with a margin of 2 or more was then collated against
the CoMMA text and the manuscript's catalogue entry. The top five hits per
control, with classifications, are in
[`comma-controls-2026-10-20/result.json`](comma-controls-2026-10-20/result.json).

| Margin of top hit | Controls | What the hits were |
|---|---|---|
| 3 or more | 13 | All real textual agreement. The identified work was the top hit for 6: F-t273, F-7nce, F-kr2n, F-03xq, F-4usd, F-cfry. It was at rank 3 for 2 more: F-v7a4, whose top hit is Ezekiel 34 in a Bible, and F-vpe8, whose top hit is Haymo's homily, the source. A source the work quotes for 3: F-q5ti (Gregory, *Dialogues*), F-su3k (Augustine, *Enchiridion*), F-v0qx (*Legenda aurea*). The Bible verse only for 1: F-1szi. For F-bcte, the reading covered the sideways Priscian leaf (filed as F-fwl6), not the Bede leaf, and all five hits are Priscian XIV. That is the text actually read. |
| 2 to 3 | 3 | F-rl44: the work, Serapion, at rank 2 under Avicenna's shared prose. F-xukl: chance on Dutch prayer words. F-yybk: a stock list of virtues, not the work. |
| below 2 | 20 | Not collated. Four had five or fewer searchable words. The rest had 11 to 346. |

So the identified work came back in the top five for 9 of 36 controls. A
source or the quoted Bible text came back for 4 more. Every one of the 13
margins of 3 or more was real textual agreement, and none was chance.

The margin separates real agreement from chance. It does not tell the work
from its sources, its base text or its Bible verses, so each hit has to be
collated before anything is claimed. Misses mostly reflect coverage: CoMMA is
weighted to French libraries, and many controls are German, Austrian or Italian
fragments of works with few French copies. Short readings miss even when the
text is present: Psalm 1 with seven searchable words finds Psalters at a
margin under 2, because the shuffled baseline hits them too.

138 tests pass. The tests cover HTR normalisation, each match kind and its
weight, stop-word and frequency limits, ordered chains, an end-to-end search
that finds an abbreviated witness above the shuffled baseline and above a
scrambled decoy, the install states, a resumed download against a local
HTTP server that honours byte ranges, rejection of a wrong sha256, and the
refusal to download without `--yes`.

No ledger entry, report or reading was changed. Searches of the partly
identified fragments are research results and belong in their own pull
request. See [usage and limits](../tools/COMMA.md).
