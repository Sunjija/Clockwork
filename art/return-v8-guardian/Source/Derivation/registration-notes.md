# Guardian V8 native registration

Five actual generated whole-pose edits were inspected before native derivation.
The parent inspected both native comparison images and accepted these native
candidates for export. Human final appearance approval and in-game motion
playtesting remain separate; no game/editor was launched for this conversion.

All sprites use the unchanged V7 32-color palette, binary alpha, and a 192×176
native canvas. Bounds below use an exclusive right/bottom edge.

| Native pose | Opaque bounds (left, top, right, bottom) | Width | Median planted-support row | Lowest opaque row |
|---|---|---:|---:|---:|
| idle | 28, 76, 164, 164 | 136 | 163 | 163 |
| jaw-impact-03 | 28, 89, 164, 165 | 136 | 163 | 164 |
| jaw-impact-04 | 28, 104, 164, 165 | 136 | 163 | 164 |
| jaw-impact-05 | 28, 100, 164, 164 | 136 | 163 | 163 |
| slam-land | 22, 102, 171, 164 | 149 | 163 | 163 |

The planted-support rule is the established V7 rule: take the median of each
occupied support column's lowest opaque pixel within the bottom 10 native rows.
It is not a rule that every opaque pixel must end on row 163. The one-pixel lower
extremity in the two initial jaw impact poses is accepted, not painted out or
region-rescaled. Full source alpha-128 support columns, native support columns,
median support row and lowest opaque row are recorded independently in
`native-derivation.json`.

Four even-width poses have an exclusive-bound midpoint at x=96. The 149-pixel
landing pose has an exclusive-bound midpoint at x=96.5 and an inclusive-pixel
midpoint at x=96; this is half-pixel integer-grid quantization, not motion drift.

Whole-pose source scaling is uniform before integer raster rounding. No head,
jaw, body shell, piston or limb receives an independent transform or a painted
replacement. The selected generated originals, unselected extraction revision,
V7 originals and their provenance are preserved.

Deterministic replay was checked: rerunning `derive_guardian_v8.py
--inspected-anchors` produced the same SHA-256 for all five native PNGs.
