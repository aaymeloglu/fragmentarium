# Cantus melody search: live controls, 20 October 2026

The tool queries the two endpoints used by the public
[Cantus melody keyboard](https://cantusindex.org/melody). Its
[client implementation](https://cantusindex.org/modules/my_melodysearch/js/searchmelody.js)
provides both the query parameters and the repeated-pitch simplification.
The response HTML and request/hash/timestamp receipts are cached locally.

The positive control is [melody 003133m1, Homo quidam erat dives](https://cantusindex.org/melody/003133m1).
All queries below were derived from that catalogue encoding, not read from an
unidentified fragment. Repeated adjacent pitches are collapsed, as in the website.

| Query | Settings | Melody catalogue | Manuscript network |
|---|---|---|---|
| `dcdfdfdcfghgfg` | opening, exact | 1 result, 003133m1 | 4 concordances |
| `edegegedghjhgh` | opening, transpositions | 1 result, 003133m1 | 4 concordances |
| `edfghgfgfedcdh` | anywhere, exact | 1 result, 003133m1 | 0 concordances |

The manuscript results include *Homo quidam* in CH-E 611, but also
*Sanctus Sebastianus dixit Nicostrato*, which shares the selected opening.
This is a practical false-positive warning: a melody segment retrieves candidates,
not a unique text or a manuscript's liturgical use. The interior query's differing
counts also demonstrate that the two indexes have different coverage/readings.

119 tests passed. Tests cover both real response shapes, formatting and repeated
pitches, rejection of gaps/accidentals/uncertainty, explicit zero results versus
unavailable responses, partial service failure, truncated responses and cached-byte
integrity. Offline replay gives the same candidate counts. The small fixtures
retain one public row each with the heading count adjusted to one; they test
parsing, not the live index size.

No fragment status or transcription was changed. Input still requires a secure
pitch sequence from the image. Music recognition and the interpretation of
unpitched neumes are not implemented. See [usage and limitations](../tools/MELODY.md).
