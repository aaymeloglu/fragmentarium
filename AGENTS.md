# Repository instructions

This work was done by LLM agents. It needs a specific set of capabilities, and most of the time
lost in the first pass went to tooling that was missing or blocked rather than to the fragments
themselves. Set the tooling up before opening a fragment.

`METHOD.md` is the research procedure and `CONVENTIONS.md` is the evidence standard. Read both.
This file covers what has to be available for either to work. Read
`FIRST_READINGS.md` before opening a fragment. The first reader must run in a fresh session
with only the neutral image packet and prompt, without this repository or inherited conversation.
The coordinator freezes and commits the complete response before revealing candidates.
A reader that has already seen a proposed answer cannot attest to an image-only reading.

## Capabilities to have before you start

**1. Reading images.** Every fragment starts with a transcription made by looking at IIIF crops of
the leaf. A model that cannot view a local JPEG cannot do this work at all, and no amount of
catalogue metadata substitutes. Everything else on this list is negotiable; this one is not.

**2. A shell, Python 3.12, and uv.** `uv sync --frozen`, `uv run pytest -q`, `uv run python
docs/_build_site.py`. Everything in `tools/` is standard library, so there is nothing to install
for the research itself.

**3. Plain outbound HTTP.** Nearly every source here answers a GET: the Fragmentarium IIIF
manifests and image servers, archive.org full-text search and `_djvu.txt`, Corpus Corporum,
Corpus Thomisticum, Gloss-e. An agent with `curl` and `urllib` can run the whole method.

**4. A Google Books API key.** This is the one credential worth setting up in advance. Google
Books covers the early printed editions where most medieval texts that reached print live, and it
produced several of the identifications here. Enable the Books API in the Google Cloud console,
create an API key, and export it:

    export GOOGLE_BOOKS_API_KEY=...
    python3 tools/gbsearch.py '"phrase one" "phrase two"'

The free tier is about a thousand queries a day. Without a key the endpoint returns a
quota-exceeded error on the first call, so there is no keyless fallback. A burst of queries earns
a 429 that can last the rest of the afternoon; `tools/searchd.py` spaces calls 2.5 seconds apart
for that reason.

**5. A browser, for the few things HTTP will not do.** Form-driven search pages (Corpus
Thomisticum), library page-image viewers (Gallica, `dl.ub.uni-freiburg.de/diglit/`), and anything
that refuses a scripted request. We used the Aside CLI; Playwright or a Chrome extension driver
does the same job. Nothing on the critical path needs it, so treat it as the escape hatch when a
source will not answer curl.

One hard rule: never point a browser at books.google.com page or image URLs. A burst of those
captcha-walls the whole network for hours and costs you the API too. Search through the API,
then read the passage in an archive.org mirror of the same scan, often `bub_gb_<volume id>`.

**6. Parallel subagents, if the harness has them.** The 2026-09-20 batches ran one agent per
fragment, ten at a time, roughly 20 minutes of wall clock, with a per-agent budget of about 40
tool calls. The lead then spot-checked every claimed identification against a fresh crop of the
image. Fragments are independent, so serial work gives the same results more slowly.

**7. A second model for review.** Claude did the research here and Codex reviewed all 22 reports
before anything was published; that review downgraded one identification and rewrote several
summaries. Overclaiming is the characteristic failure of this task: a real textual parallel gets
written up as a settled attribution, and a search that found nothing gets written up as proof that
a text was never printed. A self-review by the model that wrote the report does not catch this.
See `REVIEW.md`.

## What you do not need

No database, no Fragmentarium account, no OCR or image-processing libraries (the model reads the
crops directly), no email access until you are ready to report a result. Brepols Library of Latin
Texts and In Principio would help and are paywalled; the method works without them, and the
fragment READMEs record them as unchecked rather than ruled out.

## Handling the key when you fan out

Run `tools/searchd.py` once in the lead session with the key in its environment, and have the
workers query `127.0.0.1:8790` (`/gb`, `/ia`, `/cc`, `/health`). One process holds the credential,
paces Google Books for everyone, and caches results.

This pattern exists because of a failure worth anticipating. In the first batch the agent
harness's own credential classifier blocked worker sessions from reading a key out of any local
file, and then from running the wrapper script at all. Three fragments (F-1exy, F-ahiy, F-3yl2)
went through their research pass with no Google Books access; their READMEs record the gap, and
only one of them got a later pass from the lead. A localhost service sidesteps the problem: the
workers never touch a credential.

Keys and absolute local paths must not land in tracked files. `tests/test_data.py` checks for
them.

## Network quirks that cost a run

| Symptom | What is happening |
|---|---|
| Google Books 429 for hours | Query burst. Pace at 2.5 s, or use `searchd.py`, which does it for you. |
| books.google.com captcha on everything | Page or image scraping. API only, then read the passage on archive.org. |
| archive.org 401 on a volume | In-copyright item. Not available; record it as unchecked. |
| Ghent images 404 | The `adore.ugent.be` URLs in the manifest are dead. The working base is the ExLibris `service` `@id` inside the canvas; `tools/iiif.py` resolves it. |
| Gallica crops show the wrong region | Its IIIF region endpoint mis-registers. Download `full/full` and crop locally. |
| IIIF crop 404 at high zoom | Upscaling past about 2x is refused. `--scale` is capped at 2. |

## Quick start

    export GOOGLE_BOOKS_API_KEY=...
    uv sync --frozen
    python3 tools/searchd.py &                          # localhost search service
    python3 tools/iiif.py F-xxxx info                   # canvases and the working image base
    python3 tools/iiif.py F-xxxx tiles /tmp/f --canvas 0 --cols 2 --rows 4
    # Follow FIRST_READINGS.md: isolated reader, freeze response, commit, then search
    curl -s '127.0.0.1:8790/gb?q=%22phrase%20one%22%20%22phrase%20two%22'
    python3 tools/ia_cluster.py IDENTIFIER "phrase one" "phrase two" --show

Pick the next fragment from `docs/burndown.html`. Write the result to
`fragments/<F-id>/README.md`, add the row to `data/fragments.json`, rebuild the site, and run the
tests. Record the attempt whatever the outcome, so the negatives stay visible.

    uv run python docs/_build_site.py && uv run pytest -q

## House rules

Do not commit images. Fragmentarium and the holding libraries serve them over IIIF; the site
hotlinks thumbnails and the folder links to the record.

Do not email anyone from a research run. Reporting to the library is a separate, deliberate step
described in `CONVENTIONS.md`.

Every public page states current beliefs and stands on its own. Do not narrate revisions
("previously read", "now corrected"); replace the obsolete claim wherever it appears, including
tables, summaries and generated pages. Research history belongs in Git and in files that are
explicitly audits, such as `REVIEW.md`.

Say what was checked and what was not. A fragment README distinguishes what a search excluded,
what returned nothing, and what could not be reached at all. Failure to find a text does not
establish that it was never printed.
