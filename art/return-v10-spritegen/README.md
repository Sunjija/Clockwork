# Tique V10 native motion sources

Reference tool: [aldegad/sprite-gen](https://github.com/aldegad/sprite-gen), Apache-2.0, commit `bc64939c6e46a9679bb6569f40524d8a84c88160`, skill2.11.0. The reference checkout is outside the game repository. This folder stores actual single-pose sources and the authored native results, not the tool's virtual environment.

The approved original `canonical-native.png` is the only identity/style anchor. `canonical-reference-16x.png` is exactly NEAREST enlarged for image generation. Full animation sheets and videos were not generated.

Each `jump`, `actions`, `support` run stores its request, raw single-pose PNGs, decoded sprite-gen frames and a pinned original13-color palette. The documented rejected/capped extractions remain available. Native contour corrections have their own pixel-edit/provenance records; an authored import is never labelled unchanged canonical extraction.

To reproduce decoding, clone the pinned reference, install its CLI in an isolated environment, then run for the desired group:

```powershell
sprite-gen prepare --out-dir art/return-v10-spritegen/jump --character-id tique-v10-jump --base-image art/return-v10-spritegen/canonical-reference-16x.png --request art/return-v10-spritegen/jump/request-input.json --force
sprite-gen extract --run-dir art/return-v10-spritegen/jump
```

`prepare` rewrites tool prompt templates. Actual executed generation prompts belong to the separate generation-provenance/root-generation-record files. Do not regenerate from the strip templates: this project uses individual full-character stills.

```powershell
python tools/art/author_tique_jump_v10.py
python tools/art/author_tique_actions_v10.py
python tools/art/author_tique_support_v10.py
python tools/art/package_tique_v10.py
python unity/TiqueReturnPrototype/Tools/Review-TiqueV10.py
sprite-gen inspect-motion --source art/return-v10-spritegen/Jump/asset.json --out art/return-v10-spritegen/Jump/motion-report.json
```

`inspect-motion` reports evidence and explicitly warns when manual single-foot ground contact is unknown. It does not certify naturalness, automatically establish a foot contact, retime gameplay, or approve artwork. Runtime variable frame durations are in `clips.json` and `asset.json`; a default2fps unpacked atlas would be a different sequence.

Piskel sheets and APNG files are **exports of authored native frames** for editing and review. They are not generated animation sheets cut into game assets. Runtime PNGs preserve original exposures and the accepted original Walk/Idle bytes.
