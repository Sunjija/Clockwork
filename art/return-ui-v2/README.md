# Compact UI V2 — image-first candidate

Two actual built-in image-generation anchors were produced on 2026-10-02,
shown to the user, and inspected by the parent production agent before native
conversion. They depict the actual panel and button, not a generic moodboard.
Production inspection permits packaging; **human final appearance approval is
still pending**. Technical checks are not appearance approval or a playtest.

The generated frame identity stays intact: quiet navy centers, cool steel
chamfered borders, restrained cyan/brass hardware. The native panel is 96×23;
the button is 112×21. Whole-asset uniform conversion retains each generated
source aspect rather than forcing the initial suggested dimensions. No new
silhouette, decorative gear, corner, or replacement rectangle is code-painted.

## Source and runtime chain

- `Source/requests.json`: exact prompts and reference paths.
- `Source/provenance.json`: immutable generation originals and inspection record.
- `Source/Generated`: unchanged actual generated images, copied into the repo.
- `Source/Native`: image-derived panel/button and fixed 19-color material palette.
- `Source/Derivation`: alpha crop, premultiplied BOX samples, palette indices,
  native-to-generated source footprints and exact SHA256 records.
- `Clips`: editable PNG, Piskel, APNG-compatible PNG, and pixel-delta files.
- `export-manifest.json`: every runtime copy, source-edit chain, schema and hash.
- `QA/native-source-comparison.png`: actual anchors beside native candidates.
- `QA/native-button-palette-states.png`: identical silhouettes in four states.
- Runtime: `unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/UiV2`.

`panel`, `button`, `button-selected`, `button-pressed`, and `button-disabled`
each have one runtime PNG. Selection is cyan, press is brass, disabled is dim
steel, and normal retains the native source. These are explicit palette-only
state edits; source alpha and geometry remain identical. A separate four-frame
button-state preview is an editable diagnostic, **not** an in-game animation.
The five runtime PNGs are exact copies of the editable clip PNGs.

`skins.json` is `{ skins: [{ name, width, height, margins }] }` with margins in
left/top/right/bottom order. Panel margins `[10,6,10,6]` and button margins
`[8,5,8,5]` retain the actual source corner/rivet regions. Renderer code should
retain native corners and crop/tile native edge samples, not resize the entire
frame or paint an unrelated fill. Imports use Point filtering, no mipmaps,
no compression and 64 pixels per unit.
The connected renderer fixes corner dimensions, tiles/crops the native edge
strips, and stretches only the center with Point sampling.

## Unchanged licensed font reuse

The existing NeoDunggeunmo 1.601 source font is reused unchanged under SIL OFL
1.1. The source and license remain in `art/return-v5-feedback/Source/Font`;
the runtime package includes `FONT-LICENSE.txt`. The approved Feedback atlas,
index and every other Feedback asset are preserved and SHA-checked.

All 381 existing glyph tiles, including the already-approved arrow tiles, are
copied RGBA-byte-exact into the V2 atlas. Only missing current C# source
characters are added from the same unchanged licensed outlines at the existing
16px cell size. No font, arrow shape or generated lettering is redesigned.
The default body is 14 logical pixels, secondary labels 12, and large text 16.
The 12/14/20/24px display atlases rasterize the same unchanged licensed outlines
at their native display size, avoiding lost Korean strokes from shrinking the
16px atlas on the GPU. Existing approved control symbols remain reused shapes.
The approved 16px glyph atlas remains RGBA-byte-exact. Source corpus hashes,
added glyphs, native size atlas hashes, coverage and
unchanged tile evidence are in `Source/Font/provenance.json` and
`QA/font-coverage.json`. Refresh coverage after any new UI text is added.

## Reproduction and validation

Use `tools/art/derive_export_ui_v2.py`. Derivation requires explicit
`--derive --inspected-anchors`, and runtime export additionally requires
`--export --inspected-native`. Both gates mean production-agent inspection,
not a human approval claim. `--font-only` refreshes unchanged-font coverage;
run the full export afterward to refresh the manifest and corpus hashes.

The exporter checks Piskel replay, APNG/PNG replay, native-source delta replay,
binary alpha, fixed palette, runtime PNG hashes, button geometry invariance,
licensed font coverage and preservation of all existing Feedback files.
`QA/export-validation.json` records mechanical results. This art tool does not
launch the game, open Unity, build a player, capture runtime, or change gameplay.

GUI layout and adaptive guidance behavior belong to the separate C# integration
work; the static art package alone does not establish their runtime readability.

## Integrated layout review

`QA/layout-preview/overview.png` and its 16 individual scenarios consume the
actual C# `CompactUiLayout.Build` draw plans, exported by ModelChecks. They
compose current runtime skins/fonts/icons over earlier world-camera images;
they are explicitly **offline fixtures, not live Unity screenshots**. Background
poses and fixture models are not synchronized. `review-manifest.json` records
the inputs, source hashes and that limitation. Technical UI/guidance checks and
the full game-source compiler run do not launch a Unity player. Details and
primary reference links are in the compact UI work-order document.
