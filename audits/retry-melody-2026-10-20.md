# Twelve candidates for melody-first retries

Ranked after submitting the melody tooling PR on 20 October 2026. These records
remain unresolved in the current screening set. Many were screened out as chant
or insufficient text, rather than subjected to a full identification attempt.
Their full catalogue descriptions and image lists were refreshed on 20 October.
No melody was transcribed or identification made to create this shortlist.

Use the [melody tool](../tools/MELODY.md) on a continuous surviving passage:
4-14 pitches after collapsing adjacent repeats, preferably toward the longer
end. Search anywhere in the melody; use `--start` only for a demonstrable chant
opening. Never concatenate notes across a damaged interval. An uncertain clef
can motivate separate transposed searches, but does not establish absolute pitch.

**This is a priority list for inspecting and encoding music, not twelve confirmed
encodable passages.** F-82z1 has the clearest newly inspected musical prospect.
Most of the others still need native-resolution crops and a pitch-readability
check. Stop a candidate if no continuous run meets the input requirements.

| Rank | Fragment | Why melody adds something | First image/encoding task |
|---|---|---|---|
| 1 | [F-82z1](https://fragmentarium.ms/overview/F-82z1) | Unidentified Marian antiphon/responsory; paper conceals most of the words, while exposed bands retain square notation. | Both overview images were inspected on 20 October. Start with the lower exposed staff on the first image, `fol. [1]r`, which shows a longer musical run; crop at native resolution and establish its pitches. The reverse is much more abraded. |
| 2 | [F-30ta](https://fragmentarium.ms/overview/F-30ta) | A Franciscan antiphoner reconstruction has 12 fragments, of which 11 are placed. Its known neighbours offer a useful liturgical constraint. | First map the one unplaced piece among the 25 images against the reconstruction. Encode that piece, not one of the already identified eleven. This mapping and image inspection remain to be done. |
| 3 | [F-31tn](https://fragmentarium.ms/overview/F-31tn) | Square notation survives on a partial leaf whose text may have been washed off: music could bypass the main textual obstacle. | Inspect front and back cover faces among the seven images, avoiding the host title/explicit and the separately catalogued printed pastedowns. Prior screening saw ghost staves; confirm that actual pitches, not merely staff lines, survive. |
| 4 | [F-gs4f](https://fragmentarium.ms/overview/F-gs4f) | Unplaced rhymed office material has short textual anchors such as `deificum` and `cristicole`, plus pitched neumes. | Check corners as well as the spine; the catalogue describes a music-only line on a corner. The freshly inspected spine overview contains very short runs, so it is not yet a usable query. Use secure words to narrow a longer corner run if one survives. |
| 5 | [F-mt26](https://fragmentarium.ms/overview/F-mt26) | Two removed pasteboards preserve Hufnagel notation but little connected chant text. | Inspect the front and rear boards separately for one uninterrupted musical passage. Layered paper and mirrored later writing caused trouble before; neither supplies missing chant pitches. |
| 6 | [F-50ro](https://fragmentarium.ms/overview/F-50ro) | A comparatively broad vertical strip preserves seven chant lines, with only endings transcribed. The catalogue suggests an antiphon beginning with E. | Locate the strip in the sole image before cropping: prior probes hit decorative host paper. The catalogue reports no visible clef; if relative staff steps are clear, test transposition and retain that uncertainty. Do not assume the E marks the queried musical opening. |
| 7 | [F-5qb0](https://fragmentarium.ms/overview/F-5qb0) | Square notation accompanies short words such as `facie` and `nostr`; these can filter melody candidates more effectively than they identify text alone. | Find the 70 mm spine strip and corners in the sole image, rather than the host label. Check whether any single surviving staff has enough notes after collapsing repeated pitches. |
| 8 | [F-lbfy](https://fragmentarium.ms/overview/F-lbfy) | Antiphoner spine and corner material has almost no usable words, making pitched music the remaining searchable evidence. | Inspect both images and locate the actual fragments; the earlier sample hit marbled host paper. Prefer a corner if the spine preserves only short endings. A related binding is a follow-up lead, not an assumed continuation. |
| 9 | [F-htjx](https://fragmentarium.ms/overview/F-htjx) | Two notated sewing guards preserve only isolated letters; a musical run could succeed where text cannot. | Use the three images explicitly labelled for guards A/B, including `A_unten` and `B_oben`. Earlier probes sampled the host title page. Keep each uninterrupted guard passage separate. |
| 10 | [F-euvy](https://fragmentarium.ms/overview/F-euvy) | Neumes on red staves accompany only `mar`, `runt a` and `ti s`. Melody is a plausible additional discriminator. | Compare outside and inside images of the 82 x 70 mm strip/tabs. The legible Martinus Muller label belongs to the host. Its small size makes this a conditional prospect: require a real continuous pitch run. |
| 11 | [F-p8zx](https://fragmentarium.ms/overview/F-p8zx) | Faint chant syllables already transcribed by the catalogue have not identified the piece; some staff notation survives. | Crop the narrow spine strip in the sole image. This is a low-priority readability test: scattered notes on different rows cannot be combined into a query. |
| 12 | [F-857d](https://fragmentarium.ms/overview/F-857d) | An antiphoner strip has at least nine staves but only one-to-three-letter text endings. | Locate the strip in the sole image; prior probes hit the marbled host. Check continuous notes on a single four-line staff. The catalogue's related B 555 Bd. 126 may supply context later, but is not evidence for filling gaps. |

F-30ta is especially promising for contextual verification once its unplaced
piece is located; F-31tn is especially dependent on image quality. Rows 6-12
are less certain acquisition/readability checks, not predictions of a match.
Longer sequences and agreement on a second passage matter: unrelated chants
can share short melodic formulas. A chant match also does not establish the
manuscript's liturgical use or origin.

## Deliberate exclusions

- **F-w8rs:** the newly inspected crop has only a few notes on each surviving
  staff. More text is visible than usable uninterrupted melody in that crop.
- **F-3thm, F-hf4a, F-zpqa:** current catalogue/manifest requests returned 404;
  restore access before placing them in an actionable image queue.
- **F-ledt:** its unidentified C verso is described as music-only, but the
  current four image labels name A recto and portions of D. Obtain or locate
  the C-verso image first; re-identifying the already described A/B/D chants
  would not address the missing piece.
- Unpitched notation, isolated puncta, decorated initials and already identified
  chants are not candidates simply because they occur in a music manuscript.

The [tooling audit](melody-tooling-2026-10-20.md) records successful known-melody,
transposition and interior-passage controls. Those controls validate retrieval,
not the chances of identifying these fragments. Cantus coverage is incomplete;
a zero-result search is not an exclusion.
