# V10 Attack / Dash source and native review

PNG files are frozen. `png-freeze.json` records every Attack/Dash/ghost SHA256 and the author script SHA256. Runtime integration is owned by the parent task; this report does not certify runtime animation naturalness.

## Actual source workflow

- Built-in image generation produced 11 individual transparent full-character stills: 9 retained pose sources, 2 rejected attempts. Every generation attached only `../canonical-reference-16x.png`, the original 64px Idle sprite enlarged by nearest-neighbor. Generated images were never reused as identity references.
- Retained states: windup, strike, recoil, dashload, dashtravel, dashbrake, extension, withdraw, dashalternate. Windup attempt1 was rejected for elongated legs/physical-cap resizing. Strike attempt1 was rejected because the front arm punched instead of the rear arm. Rejected images remain in `rejected/`.
- Exact called prompts, provider output paths, preserved raw copies and their SHA256 fingerprints are in `generation-provenance.json` and `called-prompts/`. All 11 preserved files compare byte-identically to the actual generated files.
- No video, generated animation sheet, animation-sheet cutting, part resizing, rectangular canonical head/chest overwrite, or optical-flow interpolation was used.
- The actual sprite-gen extraction command was `sprite-gen extract --run-dir <absolute actions> --states windup,strike,recoil,dashload,dashtravel,dashbrake,extension,withdraw,dashalternate`. Engine revision `c639973b665a` used pixel-unfake grid recovery and the existing pinned original 13-color palette. `frames/frames-manifest.json` contains measured input grids, source copies and warnings.
- The extractor reported axis pitch crosschecks of 4.1% for windup, 4.5% for recoil, and 5.5% for dashalternate. These were reviewed as source-to-native contour quantization, not hidden by resizing body parts. Safe-area warnings concerned sprites that still fit inside the 64px margin zone. The nine accepted decoded sources did not require physical-cap resizing.

## Native corrections and causes

The previous V9 pipeline compressed head, torso and leg bands separately and then restored rectangular canonical identity regions. That broke the relationship between joints and the visible body. Long duplicate holds also hid intermediate movement. V10 derives each key's whole body from an independent complete still, then records individual native pixel edits. The original neutral is copied byte-for-byte at endpoints.

The first V10 cleanup mistakenly treated the original small zigzag mouth as unwanted source black dots. It also left old generated cap pixels beside newly standardized round hands, and some wrists connected only through a dark thin outline. Those faults were visible in actual frame contact sheets and the parent's interim Unity capture.

- Mouth: restore the original five INK points `(34,28),(36,28),(38,28),(35,29),(37,29)`, registered to each source pupil's position. Only those semantic points and actual old mouth points change. Lens rims and the complete head remain source-derived.
- Heart: trace only original cyan and warm glow color points, with the canonical cyan mask 8×7 / 41 pixels inside the 13×10 feature envelope. Bronze chest outlines, waist and arms are not replaced. Source stance/waist location determines placement. Warm glow highlights cannot grow outside an existing source alpha surface.
- Hands: all 40 new hands use `../round-hand.json`, a 5×5 / 21-pixel fingerless sphere with the shared original metal colors. Old cap nubs are erased as individual pixel annotations. Metallic wrist paths have at least two directly adjacent metal pixels on the hand boundary. Strike04/05 and Dash rear-arm paths were explicitly strengthened.
- Heart visibility: 23 of 24 final frames show the complete 41-pixel cyan mask. Attack06 shows 38 because the actual foreground hand/forearm covers three top heart pixels; the mask itself is unchanged. This is documented occlusion, not a flattened chest transformation.
- Dash alternate is a separately generated complete posture, with recorded native entry/exit sole and end-effector adjustments. The original Idle and Walk assets were not edited.

Every key correction is recorded in `native-keys/*-pixel-edits.json`; intermediate native frame edits are in `native-frame-edits/`. `review-before-semantic-fix/` preserves the prior complete PNGs, GIFs, native keys and author script.

## Verification evidence

`verify_freeze.py` reads the final actual PNG/GIF files and writes `native-checks.json`; it does not modify animation PNGs. Checks passed:

- Attack12 with original durations `[20,30,40,30,70,30,40,40,30,30,40,60]`, total460ms.
- Dash12 with original durations `[40,30,30,30,40,50,40,35,35,35,35,40]`, total440ms.
- All24 files are 64×64, contain only original13 opaque colors, and have alpha0/255. Every frame is one actual 4-neighbor alpha component.
- Every new hand matches the shared complete round glyph and has at least2 directly adjacent visible metal wrist pixels. No explicit finger/thumbnail nubs remain in the enlarged hand review.
- All4 clip endpoints equal the original Idle00 file bytes, SHA256 `608f094c30f30e16a7bedfbfad73fa0670601ce2cccae2512b92d233b1859c41`.
- All12 ghost alpha channels equal the corresponding Dash alpha channels byte-for-byte. Ghost changes only opaque RGB to original cyan; rendering opacity is handled by runtime integration.
- Each GIF decodes to12 exposures with pixels exactly equal to its corresponding PNG enlarged4× by nearest-neighbor. Attack GIF timing is exact; GIF's10ms resolution quantizes Dash's four35ms exposures to40/30/30/40 while preserving440ms total. Runtime duration arrays remain unchanged.
- Actual `sprite-gen inspect-motion` ran against each explicitly ordered `asset.json` with anchor32,56 and original per-frame seconds, without an FPS override. Both reports have11 changed transitions, zero adjacent exact duplicates and one nonadjacent exact duplicate from the intentionally identical neutral endpoints. Reports retain all durations.
- `inspect-motion` reports `needs-review`, with stride unverified because no manual planted-foot spans/isolated foot ROI were asserted. These measurements do not establish natural movement.

Author reviewed all24 actual PNGs in `all-actual-frames-5x.png`, all40 hand/wrist crops in `hands-final-8x.png`, original-side identity contacts, nine source/native keys, and both decoded GIF exposure galleries. The Jump worker independently re-reviewed updated Attack/Dash contact sheets: original zigzag mouth is visible throughout, heart is stable, GOLD wrist bridges reduce detached-cap impressions, and no clear finger/lower-nub remnants were found. This was a static review. Parent final Unity GPU/rendered-motion review remains the runtime gate.

Useful review artifacts: `../Attack/contact-3x.png`, `../Dash/contact-3x.png`, `native-keys-identity-5x.png`, `all-actual-frames-5x.png`, `hands-final-8x.png`, `attack-decoded-gif-4x.png`, `dash-decoded-gif-4x.png`, `attack-motion-report.json`, `dash-motion-report.json`.
