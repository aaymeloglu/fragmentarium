# Working in this repository

For manuscript research, read [METHOD.md](METHOD.md) and
[CONVENTIONS.md](CONVENTIONS.md) once. METHOD gives the workflow and stopping
conditions; CONVENTIONS owns the evidence and reporting rules. For code or
maintenance tasks, read only the references relevant to the change.

The essential obligations are to inspect images for transcription claims,
preserve original readings, distinguish source assistance, and support each
claim with the evidence actually checked. Research tactics are adaptable.
Tool availability is not a reason to mislabel evidence or repeat failed work.

## Working commands

One Python 3.13 environment and lockfile. Local checks need no API key:

```sh
uv sync --frozen
uv run pytest -q
uv run python tools/readings.py check --base origin/main
uv run python docs/_build_site.py
```

Run the relevant checks before submitting changes; include the generated site
when reports or data change. HTR dependencies are optional (`--group htr`).

## References, when needed

| Task | Reference |
|---|---|
| Acquire images or preserve an independent reading | [FIRST_READINGS.md](FIRST_READINGS.md) |
| Run or troubleshoot Kraken/CATMuS | [HTR.md](HTR.md) |
| Configure search access or match noisy Latin text | [RETRIEVAL.md](RETRIEVAL.md) |
| Understand earlier findings and limits | [REVIEW.md](REVIEW.md), the relevant fragment report, or `audits/` |

These references are not a reading checklist. Keep reports and candidate-bearing
repository context away from an isolated first reader.

## Repository hygiene

Do not commit images, credentials, private conversation text, or absolute local
paths. Use public source links. Public reports state current findings; history
belongs in Git or audits. Contacting a library requires an explicit request;
a research task by itself does not authorize sending messages.
