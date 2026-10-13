# Prompts for a batch

| File | Given to | Purpose |
|---|---|---|
| `first-reading.md` | every reader, inside its packet as `PROMPT.md` | how to read and what to return |
| `reader-brief.md` | an isolated reader session | which packets to read and where to write |
| `research-brief.md` | a research session | how to find and prove an identification |
| `report-brief.md` | the research session that made an identification | the public report and its files |

Words in angle brackets (`<checkout>`, `<cache>`, `<responses>`, `<evidence>`,
`<research>`, `<reports>`, `<batch>`) are working directories and the batch's
reading-name prefix; fill them in when handing a brief out. Keep the briefs,
the image cache and the tile mapping away from readers.

One batch, in order:

1. Choose records: `tools/survey.py` lists the records not yet attempted with
   their native image sizes and makes contact sheets. A record it flags SIB
   shares a shelfmark with a ledger record: look at that record first, since
   the two may be one leaf or one already examined. Read each record's
   catalogue description, including a linked full description
   (`tools/catalogue.py`), before choosing it and before choosing what to
   image (METHOD.md). Confirm which object in the image is the fragment.
   Start `tools/searchd.py` from this checkout; one left running from an
   earlier checkout runs that checkout's code.
2. `tools/acquire_batch.py`, then `tools/register.py`.
3. `tools/tilepacket.py`; one fresh session per few packets with
   `reader-brief.md`.
4. `tools/readings.py freeze-batch`, commit, and only then start research.
5. Research sessions with `research-brief.md`, one to three records each. Stop
   a session that has no candidate to test after about half an hour. Send a
   session back when it stopped with a named candidate untested, giving it
   the candidates to read on the page.
6. For each proposed identification, the coordinator reads one matched passage
   on the manuscript image and, where there is one, the source's page image.
7. `report-brief.md` for those that hold; `tools/record.py` for every record;
   rebuild the site; write the batch note in `audits/`.
