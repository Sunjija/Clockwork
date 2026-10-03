# Puzzle readability V1 — readability prototype, image-first provenance pending

**Status, 2026-10-01: readability direction positively assessed; production process needs correction.** These new assets were authored through code/native pixel painting without an actual image-generation source, contrary to the user's image-first rule. They are a readability prototype / process-noncompliant draft, not final production art. Editable originals, Piskel/APNG exports, and deterministic authoring are not permission to skip image generation.

The user subsequently said the current objects are much easier to distinguish. Preserve the connected gray walls, handled brass square weights, cyan round orbs, and recessed square/circular sockets. The whole design and its readability improvement are not rejected. Image-first refinement must retain the current silhouettes/colors rather than redesigning from zero.

The required workflow is actual `image_gen` asset generation → inspect/show the generated anchor → derive native game assets from that anchor → animate with the established Tique/guardian pipeline. Keep complete prompts, reference inputs, generated originals, and source-to-export provenance. An unrelated moodboard generated after the fact does not validate this package. Unchanged approved art may be reused; only an explicit human exemption allows a new visual to bypass generation. See repo-root `AGENTS.md`.

Files and the existing working prototype integration are preserved, not deleted or disabled by this status correction. Technical export/model/build/capture tests remain valid evidence about the prototype; the user's positive readability feedback remains valid too. Neither completes the missing image-first provenance or final-art approval. Final assets need a genuine image-first refinement source while keeping the current visual distinction direction.

This is a puzzle-prop readability pass, not a character redraw or a level-design change. Existing `StateArt`, Tique V10, Warden V7, puzzle rules, cell positions, and object dimensions are preserved.

- Walls are continuous cool-gray structural panels with no centre hub.
- Weights are bright rectangular brass masses with a large open carrying handle.
- Orbs are cyan spheres with empty corners and a revolving meridian.
- Weight/orb sockets are dark square/circular cavities, respectively. Powered outer contacts remain visible beneath occupied objects. They contain no lock/latch: seated objects can still be pushed.
- Every drawn pixel belongs to a 19-colour fixed palette; alpha is strictly 0 or 255.

## Prototype authoring and runtime API

`tools/art/author_puzzle_readability.py` records the initial native/code-painted prototype approach. It exports editable native PNGs, a Piskel source for every clip, per-frame delta replay JSON, a sprite sheet, and variable-timing APNG for moving/connecting clips. It is retained for provenance and does not fulfill the image-first rule by itself. All moving prop and connecting socket durations are copied verbatim from `ReturnV2/StateArt/clips.json`.

Unity resources: `ReturnV2/ReadabilityArt/<clip>/NN.png` and `clips.json`. Texture metadata is deterministic by path, Point filtered, mipmap disabled, alpha enabled, and uncompressed on all platforms. The original assets are never overwritten.

Clip names retain `battery-idle/moving/docked`, `orb-idle/moving/docked`, `amber-slot-empty/wrong/connect/filled`, and `cyan-slot-empty/wrong/connect/filled`. Static tiles are `floor` and `wall-00` through `wall-15`.

For the wall suffix, use the sum of connected-neighbour bits: north/top 1, east/right 2, south/bottom 4, west/left 8. Grid Y increases downwards, matching `CorePuzzle`. Format suffix as two decimal digits. An isolated wall uses `wall-00`. Canvas dimensions: tiles/sockets 36×36, weight 30×32, orb 26×26. Place the weight at cell+(3,0) and orb at cell+(5,6), as before.

## Evidence and limitations

`QA/before-after.png` compares actual prior source PNGs with new ones. `QA/before-after-grayscale.png` removes colour. `QA/room-layouts-color-and-gray.png` and `room-N-native.png` use all three real puzzle layouts and the unchanged Tique V10 idle sprite. These are static asset compositions, **not runtime screenshots**.

`QA/occupied-socket-rims.png` verifies border visibility with seated objects. `QA/all-state-contact.png` shows every clip. `QA/validation.json` records dimensions, binary alpha, timing, APNG/Piskel/delta byte replay and connected-wall continuity checks. Gameplay and human first-sight recognition still require runtime/user testing; this package does not claim they are complete.
