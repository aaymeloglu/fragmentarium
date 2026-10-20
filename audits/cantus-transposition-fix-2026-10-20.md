# Exact transposition search, 20 October 2026

`cantus_melody.py --transpose` now searches every diatonic pitch placement that
fits the supported keyboard, using exact requests in both Cantus indexes.
It retains the original placement and runs every placement regardless of
whether earlier searches return results. The algorithm uses the supplied notes;
no fragment IDs, known melodies or special-case variants are built into it.

## Reproduced failure and recovery

The [twelve-fragment retry](melody-retries-2026-10-20.md) exposed a false negative
for `jhjlkjhghjhf` with Cantus's server transposition flag. A fresh live comparison
on 20 October reproduced it: the server returned **zero catalogue and zero
network records**. The fixed tool made 24 exact requests (12 pitch placements
in each index), returning **one catalogue and seven unique network records**.
All requests succeeded and none was truncated.

The returned records include both controls known to be missed:

| Exact placement | Shift in staff steps | Recovered record |
|---|---:|---|
| `hghkjhgfghge` | -1 | [Kyrie, Porrentruy 18, p.357](https://cantusdatabase.org/chant/644939) |
| `lklnmlkjklkh` | +2 | [Paratur, Utrecht 406, 137v](https://cantusdatabase.org/chant/495687) |

[Live receipts](cantus-transposition-fix-2026-10-20.json) preserve counts,
request timestamps/hashes, every searched placement, and candidate provenance.
Offline CLI replay recovered the same candidates from those exact-query caches;
its display limit limited presentation only. No fragment identification changes.
These are retrieved candidates, not automatic musical or textual verification.

## Behavior and validation

- Candidate records are deduplicated by result URL within each index, retaining
  every placement that retrieved them. Per-query server counts and receipts
  remain available. Overlapping server totals are not added into a misleading
  unique total: the aggregate `reported_count` is null.
- Failure of one placement preserves results from the others, marks the search
  incomplete, and exits nonzero. Truncation is retained per query and flagged
  on the aggregate. Successful truncated requests are distinct from failures.
- All placements retain the requested opening/text/genre/mode filters. Exact
  searches without `--transpose` still make one request per index.
- Cached exact requests are reused; uncached requests remain paced. Offline
  replay requires all exact-placement responses and reports missing or damaged
  caches as unavailable. It does not silently accept an old server-transposed
  cache as coverage of the exact searches.

Regression tests use captured result tables for the recovered records, with
[source receipts](../tests/fixtures/cantus-exact-provenance.json). Additional
checks cover keyboard bounds and interval preservation, nonempty-result
continuation, deduplication/provenance, filters, partial failure, truncation,
offline cache reuse/missing entries, and all-unavailable CLI behavior. All 128
tests pass; 334 preserved readings check against main; the site rebuild is
unchanged.

This addresses the demonstrated server-transposition failure. It cannot remove
Cantus's result limits, guarantee index completeness, resolve damaged notation,
or establish a fragment's identity. The underlying cause of Cantus's transposed
retrieval discrepancy has not been diagnosed.
