# Writing up an identified fragment

For each fragment named to you, write three files in `<reports>/`. Do not touch
the repository checkout.

## 1. `<F-id>.README.md`, the public report

Follow the "Writeup" and "Report and record format" sections of
`CONVENTIONS.md`, and take two existing reports in `fragments/` as models of
length and tone.

- Title: `# <F-id>: <Author>, *<Work>*, <locus>`.
- An opening paragraph stating the finding plainly.
- A paragraph on the catalogue record (link
  `https://fragmentarium.ms/overview/<F-id>`; institution, shelfmark, size,
  catalogue date and title): whether its description fits and what it already
  said.
- Three bullets:
  - **Identification:** status and confidence; the diagnostic basis; the
    alternatives considered and why they are not the containing work; any
    difference of wording or version stated here, not further down.
  - **Transcription:** link the image-only first reading and the
    source-assisted reading
    (`https://github.com/aaymeloglu/fragmentarium/blob/main/fragments/<F-id>/readings/<batch>-image-only.json`
    and `...-source-assisted.json`); which lines were reread and by whom, which
    rest on the first reading; "Accuracy has not been measured."
  - **Verification:** who compared what with what kind of evidence. You are "a
    research reader". Leave one line `COORDINATOR CHECK: <the best single
    passage, its canvas and native box, and the address of the source page
    image>` for the coordinator to replace with what they checked. State the
    gaps in coverage. End with "No human review."
- `## Textual evidence`: where the manuscript passages are (public image
  address from `acquisition.json`, canvas label, native-pixel box); a two-column
  table of manuscript reading against source text for the passages collated; a
  paragraph on the differences; the edition or manuscript used, with public
  page links and the basis of its attribution.
- A closing section for leaf order, other items in the images, and what is not
  claimed (date, origin, version, novelty).

The report is a standalone account of present findings. No history of the
research, no mention of agents or passes. No local file paths. Absolute dates.
Plain hyphens or commas, not long dashes. Explain a technical term in a few
words on first use. Say "verbatim" or "line by line" only of passages that were
checked that way. Every claim must be one your research file supports.

## 2. `<F-id>.assisted.txt`, the source-assisted reading

Plain text: a first line saying it is source-assisted and which lines you
reread on the image, then the manuscript lines relied on, with canvas and
native box, uncertainty marked.

## 3. One entry for `results.json`

Give the coordinator this object for the fragment, which `tools/record.py`
applies:

```json
{"status": "identified", "confidence": "high",
 "identification": "<Author, Work, locus, short>",
 "kind": "<theology | law | science | arts | liturgy>",
 "note": "<three to five sentences: evidence, who checked what, differences, limits>",
 "verify": "<one public address of the edition or manuscript compared>",
 "report": "<F-id>.README.md", "assisted": "<F-id>.assisted.txt",
 "sources": ["<citation with page or locus for each source used>"],
 "reason": "<one sentence: why the reading was revised with the source>"}
```

`kind` sorts the record on the site: theology (Bible, commentary, sermons,
saints' lives, devotion), law, science (medicine, natural science, computus),
arts (philosophy, grammar, classical and vernacular literature) or liturgy.
An archival document gives `"document": true` instead.

Write it to `<reports>/<F-id>.result.json`. Reply with the file names only.
