# Independent readability V2 audit — 2026-10-02

Status: source/native/export technical inspection only. **Human appearance approval and gameplay/fun validation remain pending.** No generated image, native source, animation, runtime asset, or game code was changed by this audit.

## Mechanical evidence

Run `tools/art/check_readability_v2.py --phase all` with Pillow installed. `audit-all-report.json` records individual checks and any failures; `audit-source-baseline.json` captured the six selected raw hashes before native/export validation.

- Selected generated files are byte-identical to their actual built-in image-generation originals, and map to preserved prompts. No v1 draft is retroactively relabelled as generated art.
- Native derivation records alpha-128 crop bounds, unchanged original SHA, final SHA, palette entries, and a complete per-target-pixel source footprint. All recorded native pixels replay exactly. Raw nonzero-alpha bounding boxes are intentionally not used: faint distant pixels would make assets too small after conversion.
- Dimensions remain wall/floor/socket36×36, weight30×32 and orb26×26. Final alpha is binary and the shared export palette contains no more than48 colours.
- 31 clip names and77 PNG exposures retain previous timings. Every native-source edit, pixel-delta edit, Piskel embedded frame, sprite-sheet frame and APNG exposure/timing replays exactly. Runtime PNG copies are byte-identical, Point filtered, no mipmaps,64 PPU, and uncompressed.
- All16 connected wall masks keep opaque full-cell footprints, retain the anchor-derived centre, and have reciprocal EW/NS edge continuity. The connected border conversion does not replace the wall centre with arbitrary art.

## Visual review

Inspected actual raw wall/weight/orb/floor anchors, both corrected socket anchors, `audit-native-review.png`, `clip-all-state-contact.png`, and `clip-occupied-rims.png`.

- Connected cool-gray wall panels remain structure with a broad seam and dull corner rivets, not bright movable props or a central mechanical hub.
- The brass weight retains its large open rectangular handle and rectangular three-stroke inset. The handle hole stays legible at the native scale.
- The cyan orb retains a round cutout silhouette, upper-left reflection and broad meridian. Native material is richer than v1 without reverting to a gold mechanical hub.
- Empty weight/orb sockets have dark square/circular negative-space centres. The revised square socket's thin amber rim is readable; the orb socket remains cyan/iron rather than gold. Objects placed above them leave outside contacts visible. There are no locks/latches implying immobility.
- Grayscale shapes still distinguish architectural cell, handled rectangle, sphere and recessed square/circular cavity. This is reviewer inspection, not a measured5-person recognition study.

One non-blocking playtest concern: empty versus powered socket differences are relatively subtle, especially amber. Check their connection animation and counters together in the actual640×360 game. This audit does not decide that a brighter rim or another visual source is necessary; retain the existing candidate until user feedback.

`audit-native-review.png` and the exporter contact/rim images are **static native compositions, not runtime screenshots**. Do not cite them as proof of integrated gameplay, user approval, or successful boss/puzzle playtesting.
