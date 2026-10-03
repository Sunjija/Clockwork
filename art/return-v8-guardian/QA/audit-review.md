# Guardian V8 independent static audit — 2026-10-02

Result: **1,311 checks passed / 0 failed** in `audit-all-report.json`. Scope is saved image-generation originals, native derivation, editable/runtime exports and preservation of existing assets. **No game, Unity editor, or Unity build was launched.** Human final appearance approval, animated transition judgment and gameplay/fun validation remain pending.

## Source and derivation

- Six successful built-in image-generation outputs are preserved: five pose corrections and one unused jaw05 extraction variant. Actual complete prompts, references, saved images and author-host generated originals match recorded provenance. A failed dispatch is not counted as a produced image.
- Five rev1 corrections are selected. The jaw05 halo-like RGB outside the object has transparent alpha; premultiplied alpha-128 derivation excludes it without painting a new silhouette. Both revisions remain preserved.
- Independently reconstructed source BOX/unsharp sampling, fixed V7 palette conversion, permitted cleanup, per-pixel palette-index footprints and native registration exactly replay all five final native PNGs. No independent head/leg/body-part scaling is used.
- Native canvas192×176 and original32-colour V7 palette are preserved. All alpha is0/255. Every pose's planted-foot median remains row163. Jaw03/04 contain a lowest individual contact pixel at164; this does not change the preserved median-foot registration.
- Landing width is149px instead of the previous183px; its integer-centred bounding-box midpoint96.5 is within the accepted half-pixel raster registration of x96.

## Runtime and editable exports

- Exactly13 runtime PNGs changed: idle00–07, wave-strike00–02, slam-land00 and02. The remaining58 PNG files are byte-identical to V7, including held/open-core and core-flash frames, deliberate rolling and airborne rotation.
- All15 clips /71 exposures keep the original duration arrays. `clips.json` is byte-identical to V7.
- PNG copies, generated-native edits, V7 edits, frame00-relative edits, Piskel embedded sheets, individual sprite-sheet frames and APNG pixels/times replay exactly.
- Idle has one fixed body/alpha silhouette across eight exposures. Only existing back-vent pixels advance at most one step in the existing red ramp; mouth, steel body, feet and registration are unchanged across the loop.
- Every importer is Point filtered, no mipmaps, uncompressed,64 PPU. Export colours remain within the original32-colour palette.
- TiqueV10's whole tracked package is unchanged from HEAD, with139 PNGs. All77 ReadabilityV2 runtime PNG byte hashes match the pre-guardian independent audit. The77 preserved V1 draft frame-pixel hashes also match their previous recorded audit.

## Visual inspection and remaining risks

Viewed `native-v7-v8-comparison-2x.png` and `clip-correction-before-after.png`. The recognizable navy mechanical body, silver jaw plates, circular hinges and red mouth/vents remain. The triangular jaw/neck wedge and compressed facial block are reduced, and landing is more compact instead of stretched sideways.

The correction contacts are static comparisons, not runtime screenshots. They do not establish that the new impact poses join the58 reused frames smoothly at gameplay speed, nor that the more compact landing still communicates enough weight. Those are the next visual/gameplay judgments, not failed technical checks. Do not describe parent acceptance for packaging as human final-art approval.

## Reproduction and portability

Run `tools/art/check_guardian_v8.py --phase all` with Pillow and NumPy available. Only `QA/audit-*` evidence is written. Source/native/runtime images remain read-only.

Author-host checks compare the generated originals under the recorded `.codex/generated_images` cache paths with saved workspace originals. Those cache-path checks are author-machine-specific. The saved generated originals and `audit-raw-generation-baseline.json` / `audit-generated-baseline.json` SHA evidence are portable. Missing another machine's cache is not proof of asset corruption; this validator nevertheless retains the strict current-host checks instead of silently weakening evidence.
