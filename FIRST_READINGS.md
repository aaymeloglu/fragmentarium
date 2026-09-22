# Preserve the reading before looking for the answer

A matching edition can make uncertain manuscript text look more readable than it
is. Every new identification or re-adjudication starts with an image-only reading
saved before the reader sees any proposed author, earlier report, search result,
or edition. Later source-assisted readings are separate records.

The existing 22 reports predate this procedure. Their transcriptions are not
retrospectively labelled blind. This procedure preserves evidence of the reading
process; it does not certify the transcription or make a model forget its training.

## 1. Prepare an isolated reader packet

The coordinator obtains crops with `tools/iiif.py` and records each image's URL or
canvas/region coordinates. Then:

```sh
python3 tools/readings.py packet /tmp/reading-packet /tmp/crops/column-a.jpg /tmp/crops/column-b.jpg
```

The new directory contains neutral names (`image-001.jpg`, `image-002.jpg`), a
`PROMPT.md`, and image/prompt checksums in `packet.json`. Original filenames, the
fragment ID, catalogue descriptions, and source citations are excluded. Images
are copied without changing their pixels. Keep this packet outside the repository;
images are never committed. Keep the source-to-neutral-name mapping with the
coordinator (the input order is preserved).

Start a **fresh reader session with no inherited conversation**, using the packet
as its working directory. Give it only `PROMPT.md` and the packet images. The
coordinator's existing conversation and repository contain proposed answers and
must not be passed to this reader. Allow image viewing and writing its response;
do not give the reader search access, the source map, or repository access. Check
the session's inputs and activity before attesting that it was isolated. If the
harness cannot provide this separation, do not label the result image-only.

The reader labels physical lines by neutral image name, keeps uncertainty visible,
and returns plain text. Save the **complete, unedited response** as UTF-8, for
example `/tmp/first-reading.txt`. Do not clean up its spelling, line breaks, or
abbreviations. If it reports prior exposure, discard the attempt as a blind run
and start a genuinely fresh session. A new turn in the same conversation is not a
fresh session.

## 2. Freeze before revealing candidates

The coordinator, not the isolated reader, saves the response:

```sh
python3 tools/readings.py freeze F-eo5z first-01 \
  --packet /tmp/reading-packet --text /tmp/first-reading.txt \
  --reader 'model and version' --session 'fresh-session-reference' \
  --image-source 'IIIF URL or canvas and region for image-001' \
  --image-source 'IIIF URL or canvas and region for image-002' \
  --attest-isolated
```

This creates `fragments/F-eo5z/readings/first-01.json`: exact response text and its
SHA-256, the actual prompt, image checksums and citations, reader/session identity,
and the capture time in UTC. Packet checksums are verified before saving. The
command refuses to overwrite an existing record. Use public source citations and
an opaque session reference, never credentials, private conversation content, or
absolute local paths.

Commit the record **before** searching or revealing a candidate to the reader:

```sh
python3 tools/readings.py check
git add fragments/F-eo5z/readings/first-01.json
git commit -m 'Preserve image-only reading for F-eo5z'
```

The explicit isolation attestation is an operator statement, not an automated
proof. Checksums detect changes; they cannot prove what a model previously saw.
The tool does not launch or sandbox model sessions and cannot block searches in
other tools. Session separation and the freeze-before-search sequence are the
coordinator's responsibilities.

## 3. Save source-assisted readings separately

After searching and comparing editions, preserve each revised reading as another
record with its own name. Cite every edition, search result, or earlier report
used, and explain why the reading changed:

```sh
python3 tools/readings.py revise F-eo5z assisted-01 \
  --first first-01 --text /tmp/revised-reading.txt \
  --reader 'model and version' \
  --source 'Edition or report citation and page/line locus' \
  --reason 'Expanded the uncertain abbreviation after comparing the edition'
```

The revision is labelled `source-assisted` and links to the first record by name
and file checksum. It never replaces that record. Additional revisions still
reference the first reading; cite any intermediate revision used as a source.
Corrections to a saved record, including metadata mistakes, belong in a new record
or an audit note; do not edit or delete the saved record. A later independent blind
reader can have its own `first-02` record and fresh-session attestation.

In the fragment README, link the records with explicit labels:

- **Image-only first reading (unverified):** link to the preserved record.
- **Source-assisted reading:** link to the revised record and describe its scope.

Use full GitHub file URLs so the current site renderer makes the links clickable.
The main report can present the current reading; it must label source assistance
and link back to the preserved first reading. The records are an audit trail, not
a revision narrative in the report prose.

## Checks

`python3 tools/readings.py check --base origin/main` validates every saved record,
its text checksum, source-assisted references, and byte-for-byte preservation of
records already in the base commit. CI runs this comparison against the PR base
(or previous main commit for a push), so changing the text and recomputing its hash
does not evade preservation. It also rejects deletion and renaming of old records.

The first PR introducing a record still needs review of the isolation attestation
and freeze-before-search sequence. Existing reports without records remain valid
legacy inputs to CI; re-adjudication requires a new isolated reading. The
[HTR workflow](HTR.md) adds a separately preserved Kraken/CATMuS reading of the same images. Save both readings before comparing them. Search ranking, identification
thresholds, and confidence scoring are separate steps.
