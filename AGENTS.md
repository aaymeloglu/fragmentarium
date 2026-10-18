# Working in this repository

This repository identifies medieval manuscript fragments that
[Fragmentarium](https://fragmentarium.ms/) catalogues as unidentified. A person
using it will usually ask for something like "identify F-xxxx", "find a few
promising fragments and work on them", or "run a batch". Do the setup below
first, then carry on with the request without waiting to be asked again.

## Setup, at the start of every session

Run this before the first tool command, even if the checkout looks ready. It
takes well under a second when nothing has changed.

1. **uv.** Check `uv --version`. If it is missing, tell the person in one line
   that you are installing [uv](https://docs.astral.sh/uv/) (Astral's Python
   project manager, installed per user, no admin rights) and install it:
   - macOS or Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`, or
     `brew install uv` if Homebrew is present;
   - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`.

   The installer puts `uv` in `~/.local/bin`; if the shell still cannot find
   it, call it by that path for the rest of the session.
2. **Environment.** `uv sync --frozen`. This downloads Python 3.13 if the
   machine lacks it and installs the locked dependencies (pytest, Pillow,
   numpy) into `.venv/`. Nothing is installed system-wide. Always run tools as
   `uv run python tools/<name>.py`, never with a system `python3`.
3. **Check.** `uv run python -c "import PIL, numpy"`. On failure, show the
   person the error rather than working around it.
4. **Search service**, only once research starts: run
   `uv run python tools/searchd.py` in the background from this checkout and
   confirm `curl -s 127.0.0.1:8790/health`. Internet Archive and Corpus
   Corporum search work without a key. Google Books search through the service
   needs `GOOGLE_BOOKS_API_KEY` in its environment; if it is not set, say once
   that Google Books phrase search is unavailable and how to add it (a free key
   from the Google Cloud console, exported before starting the session), then
   proceed with the other sources. Never ask the person to paste a key into
   the conversation.

The work needs network access to library IIIF servers and search sites, and a
model that can look at images. Do not install anything beyond the above
without asking.

## Doing the research

For manuscript research, read [METHOD.md](METHOD.md) and
[CONVENTIONS.md](CONVENTIONS.md) once. METHOD gives the workflow and stopping
conditions; CONVENTIONS owns the evidence and reporting rules. For code or
maintenance tasks, read only the references relevant to the change.

The essential obligations are to inspect images for transcription claims,
preserve original readings, distinguish source assistance, and support each
claim with the evidence actually checked. Research tactics are adaptable.
Tool availability is not a reason to mislabel evidence or repeat failed work.

Where to begin, by request:

- **One named fragment** (`F-xxxx` or a fragmentarium.ms link): check
  `data/fragments.json` for an earlier attempt, then follow METHOD from step 1.
- **"Find something to work on"**: `uv run python tools/survey.py --cache
  <dir> --sheets <dir>/sheets` lists records not yet attempted, with image
  sizes, and makes contact sheets. If the latest `data/unidentified-*.csv` is
  months old, offer to refresh it with `tools/sweep.py` first.
- **A batch**: [prompts/README.md](prompts/README.md).

An independent first reading needs a separate session or subagent that sees
only the images ([FIRST_READINGS.md](FIRST_READINGS.md)). If your agent cannot
start one, say so and label the reading as assisted.

## References, when needed

| Task | Reference |
|---|---|
| Run a batch of fragments end to end | [prompts/README.md](prompts/README.md) |
| Acquire images or preserve an independent reading | [FIRST_READINGS.md](FIRST_READINGS.md) |
| Where to search, and how to reach each source | [RETRIEVAL.md](RETRIEVAL.md) |
| Understand earlier findings and limits | the relevant fragment report, or `audits/` |

These references are not a reading checklist. Keep reports and candidate-bearing
repository context away from an isolated first reader.

## Checks before committing

Local checks need no API key:

```sh
uv run pytest -q
uv run python tools/readings.py check --base origin/main
uv run python docs/_build_site.py
```

Run the relevant checks before submitting changes; include the generated site
when reports or data change.

## Repository hygiene

Do not commit images, credentials, private conversation text, or absolute local
paths. Use public source links. Public reports state current findings; history
belongs in Git or audits. Commit, push or open a pull request only when the
person asks. Contacting a library or Fragmentarium requires an explicit
request; a research task by itself does not authorize sending messages.
