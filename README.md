# Fragmentarium: identifying the unidentified

[Fragmentarium](https://fragmentarium.ms/) is the international database of medieval manuscript
fragments, the leaves and strips cut from old books and reused as binding waste. Hundreds of its
records describe the text as unidentified or unknown. This repository is a tool suite and method
for working through them with an AI coding agent: read the fragment from the library's images,
find the text in a printed edition or a digital corpus, and write the comparison out so anyone
can check it.

**Results:** the [published identifications](https://aaymeloglu.github.io/fragmentarium/), each
with a report linking the manuscript passage to the matching edition, and the
[research progress page](https://aaymeloglu.github.io/fragmentarium/burndown.html) covering every
fragment examined so far.

## What you need

- **git**, and a network connection that can reach library image servers and search sites.
- **An AI coding agent** that reads `AGENTS.md`, runs shell commands and can look at images,
  for example [Claude Code](https://claude.com/claude-code) or Codex CLI. One that can start
  subagents is best: the method calls for a first reading made by a session that sees only the
  images.
- **Optional:** a Google Books API key (free, from the Google Cloud console), which enables
  Google Books phrase search. Everything else works without it.

You do not need to install Python yourself. The agent sets the repository up on first use.

## Getting started

```sh
git clone https://github.com/aaymeloglu/fragmentarium.git
cd fragmentarium
export GOOGLE_BOOKS_API_KEY=...   # optional
claude                            # or your agent of choice
```

Then ask for what you want, for example:

- "Identify F-v7a4." (any Fragmentarium record id, or a fragmentarium.ms link)
- "Find three unidentified fragments that look readable and try to identify them."
- "Run a batch of five fragments."

Before doing anything else, the agent installs [uv](https://docs.astral.sh/uv/) if it is
missing, and uv fetches Python 3.13 and the locked dependencies (Pillow, numpy, pytest) into a
local `.venv/`. Nothing is installed system-wide apart from uv itself. Then the agent carries on
with your request. [AGENTS.md](AGENTS.md) holds those instructions.

To set up by hand instead:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh   # or: brew install uv
uv sync --frozen
uv run pytest -q
```

## What a research session does

1. Reads the catalogue record and any linked full description, and checks whether the fragment
   is legible at the size the library publishes.
2. Fetches images from the library's IIIF server, at reading size.
3. Has an isolated reader transcribe from the images alone, and freezes that reading before any
   searching, so later source-assisted corrections stay distinguishable from what was seen.
4. Searches distinctive phrases in Google Books, the Internet Archive, Corpus Corporum, the
   Munich digital library, chant and sermon repertories and others ([RETRIEVAL.md](RETRIEVAL.md)).
5. Compares the manuscript against the edition page and records the result, with its confidence,
   in the ledger. Identifications held with high confidence get a public report.

[METHOD.md](METHOD.md) is the workflow, [CONVENTIONS.md](CONVENTIONS.md) the evidence standards,
and [prompts/README.md](prompts/README.md) the sequence for a batch.

Research and comparisons are performed by LLMs. Each report states the scope and limits of the
evidence; an identification does not certify transcription accuracy or establish that a witness
is new. Check the matched passage against the images before relying on a result.

## Sharing what you find

Results land in your checkout: a ledger entry in `data/fragments.json`, a report in
`fragments/<F-id>/README.md`, and pages in `docs/` after `uv run python docs/_build_site.py`.
To contribute them here, open a pull request; CI checks the ledger, the preserved readings and
the site. To report an identification to the catalogue, write to fragmentarium@unifr.ch with the
holding library copied, using Fragmentarium's own field names, as described in
[CONVENTIONS.md](CONVENTIONS.md). The agent will not send messages or push on its own; ask it
when you want that.

## Layout

```
AGENTS.md                      instructions the agent reads first: setup, where to begin, rules
METHOD.md, CONVENTIONS.md      research workflow; evidence and reporting standards
FIRST_READINGS.md              isolated-reader procedure and command examples
RETRIEVAL.md                   where to search and how to reach each source
prompts/                       the reading prompt and the briefs for reader, research and report sessions
data/fragments.json            attempt ledger: catalogue data, result, confidence, identified_on, examined, links
data/unidentified-*.csv        the corpus list, from tools/sweep.py (the latest file is current)
fragments/<F-id>/              reports and preserved readings
audits/                        batch notes: what was tried, what worked, what to change
docs/                          the published site, generated by docs/_build_site.py
tests/                         data, readings and site consistency; CI fails if docs/ is stale

tools/sweep.py                 sweep Fragmentarium's search for records catalogued as unidentified
tools/survey.py                records not yet attempted: image sizes, linked descriptions, contact sheets
tools/catalogue.py             what the catalogue already says, including a linked full description
tools/probe.py                 measure text lines and cut a reading-size sample per image
tools/iiif.py                  fetch a fragment's images: info, overview, tiles, crop
tools/acquire_batch.py         fetch and cache the images for a batch
tools/register.py              add fragments to the ledger from their cached manifests
tools/tilepacket.py            neutral reading packets of overview plus reading-size tiles
tools/contactsheet.py          labelled thumbnails of every image in a record
tools/localcrop.py             crop and enhance cached images locally
tools/readings.py              image packets, frozen first readings, labelled assisted revisions
tools/searchd.py               local search service: Google Books, archive.org, Corpus Corporum (holds the key)
tools/gbwithin.py              search inside one Google Books volume, with printed page numbers
tools/ia_cluster.py            do anchor phrases sit in one passage of an archive.org volume's OCR?
tools/mdzsearch.py             full-text search of the Munich digital library's early prints
tools/latin_search.py          tolerant Latin matching against downloaded texts (see tools/MATCHING.md)
tools/schneyer.py              search Schneyer's sermon repertory
tools/cantus.py                chant texts, concordances and manuscript readings in Cantus
tools/mnlsearch.py             phrase search of the Corpus Middelnederlands
tools/hspsearch.py             search Handschriftenportal catalogue texts
tools/bnf.py                   pages of a BnF manuscript by shelfmark
tools/gw.py                    digitised copies of an incunable by GW number
tools/record.py                write results to the ledger; install a report and assisted reading
```

No images are stored here. Thumbnails on the site are served by the holding libraries' IIIF
servers; rights stay with the institutions named on each record.
