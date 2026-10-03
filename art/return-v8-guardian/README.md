# Guardian V8 — selective distortion correction

2026-10-02. Asset improvement candidate, not human-approved final art.
No Unity editor, game executable, player build or runtime capture was launched
for this revision. Existing binaries have not been updated.

## What changed

Keep the V7 mechanical guardian's navy/gray plates, red vents, four-legged
silhouette, side-view camera and pixel density. Correct three visible problems:

- Idle: the head, shell and joints no longer change shape between exposures.
  One generated neutral pose is held rigidly; only existing vent colors pulse.
- Jaw strike: replace the tall wedge, compressed muzzle and flattened recovery
  poses with generated corrections that keep a more coherent rigid jaw/hinge.
- Landing: reduce the extreme 183-pixel lateral sprawl to 149 pixels. The body
  stays crouched rather than stretching independently at each limb.

This is a selective repair, not a complete redesign or a claim that every V7
pose has been re-authored. Intended curled charge and head-down air rotation
remain unchanged, as do exposed-core poses and their attack alignment.

## Image-first production and source trail

1. Five actual image-generation edits depict the five corrected full poses.
   Each request uses the target V7 pose, V7 neutral pose and canonical boss
   reference. Exact prompts and references are in `Source/requests.json`.
2. Generated anchors were shown and inspected before native derivation. All
   five selected originals remain in `Source/Generated/rev1/`.
3. A sixth successful image-generation call attempted to remove an apparent
   gray halo from jaw recovery. RGBA inspection showed it was already alpha-0
   RGB, not visible glow. The unselected result is preserved in `rev2/`; the
   selected source remains rev1. One earlier dispatch failed before generation
   because an unsupported bookkeeping argument was supplied. Both the exact
   retry request and failed dispatch record remain available.
4. Native conversion uses the established V7 palette and whole-pose uniform
   scaling: alpha-128 crop, premultiplied area sampling, limited cleanup,
   palette normalization and fixed registration. No independent head/limb
   transform or arbitrary geometric replacement was used.
5. The native comparisons were inspected and accepted for packaging by the
   production agent. This is separate from human final appearance approval.
6. The established editable PNG/Piskel/APNG and pixel-delta export process
   produces the new `WardenV8` resources. V7 originals are preserved.

`Source/provenance.json` is the immutable generation record. Current production
and validation state is recorded separately in `production-status.json`.
`Source/Derivation/native-derivation.json` and per-pose pixel maps record crop,
source footprints, palette choices, cleanup, registration and SHA-256 hashes.
`export-manifest.json` maps every native/V7 source to its runtime PNG and edits.

## Exact change boundary

| Runtime frames | Source | Change |
|---|---|---|
| `idle/00..07` | new generated neutral pose | fixed geometry, small red vent pulse |
| `wave-strike/00..02` | three generated jaw corrections | rigid plate/joint repair |
| `slam-land/00` | generated landing correction | compact 149-pixel crouch |
| `slam-land/02` | generated neutral pose | consistent return to idle |
| remaining 58 PNGs | V7 runtime PNGs | byte-for-byte reuse |

15 clips, 71 frames, all clip names and durations unchanged. Runtime
`clips.json` is a byte-identical V7 copy. Canvas 192×176, existing 32-color
palette, binary alpha, PPU64, Point filtering, no mipmaps or compression.
Tique and puzzle/readability visual assets are outside this revision.

The planted-support median remains row 163. Jaw impact 03/04 have one lowest
opaque row at 164; this does not change the existing median-support contract.
See `Source/Derivation/registration-notes.md` for all bounds. The odd-width
landing has the expected half-pixel exclusive-bound midpoint quantization.

## Inspection and validation

- `QA/native-source-comparison-2x.png`: actual selected anchors versus native.
- `QA/native-v7-v8-comparison-2x.png`: old versus corrected native poses.
- `QA/clip-correction-before-after.png`: exported old/new frame comparison.
- `QA/clip-idle-preview.gif`: offline art preview, not an in-game recording.
- `QA/clip-wave-strike-v7-v8-full-contact.png` and
  `QA/clip-slam-land-v7-v8-full-contact.png`: all old/new sequence exposures,
  inspected as static contacts. V7/V8 GIFs and their duration/hash evidence are
  recorded in `QA/clip-sequence-preview.json`; none are runtime captures.
- `QA/clip-validation.json`: exact editable/runtime replay, palette, import
  settings, 13 corrected / 58 byte-identical frames and stable idle geometry.
- `QA/audit-native-report.json`: independent reconstruction of generated source
  through native conversion, rather than trusting the export's assertions.
- `QA/audit-all-report.json`: 1,311 independent static checks passed, zero
  failures; preserved V7, Tique and readability exports checked separately.
- `QA/model-regression/V8/animation-model-checks.json`: pure C# selector checks,
  105,600 state/time selections over the actual V8 clip manifest. Full model
  regression evidence is isolated under `QA/model-regression/` so previous
  production QA is not overwritten.

Game source prefers `ReturnV2/WardenV8/`, with V7 fallback. Combat physics,
damage/weak-point rules, transforms and animation selection timings are not
changed. No live rendering, runtime motion, user playtest or final appearance
approval is claimed for this revision.

## Reproduce without launching the game

Use the bundled Python runtime with Pillow/NumPy. These scripts process art and
validation data only; they do not launch Unity or the game.

```sh
python3 tools/art/derive_guardian_v8.py --inspected-anchors
python3 tools/art/export_guardian_v8.py
python3 tools/art/check_guardian_v8.py
```

The strict audit compares author-machine cache originals as well as the saved
repository copies. Cache paths are host-specific; on another computer use the
preserved generated files and SHA evidence, not an assumption that an absent
author cache means an asset is corrupt.

The optional second argument of `Tools/ModelChecks` selects an isolated report
directory. The dotnet harness compiles/tests pure C# models; it is not a Unity
player build. Never rerun the older V7 authoring script to produce V8: V7
originals are the preserved comparison/reuse sources.
