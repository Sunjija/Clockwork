# CLOCKWORK Production Visual Metrics v1

Status: `[production lock v1]`
Approved: 2026-07-22

This document locks the shared visual measurement system for future production art and
room assembly. It is an art-production rule, not story canon. Existing generated concepts,
prototype sprites, and scene compositions remain proposals until separately approved.

## Locked Metrics

- Aspect ratio: `16:9`
- Reference resolution: `640x360`
- Production sprite density: `64 pixels per unit` (`PPU 64`)
- Camera view: `10 x 5.625` world units
- World conversion: `1 unit = 64 design pixels`
- Small gameplay module: `0.25 unit = 16 design pixels`
- Tique visible silhouette height: `42-48 design pixels`

The visible silhouette excludes transparent canvas padding. Source canvases may be larger,
but animation frames must preserve a stable foot pivot and consistent visible scale.

## Output Scaling

The reference image must scale by whole numbers at the primary output resolutions:

| Output | Reference scale |
| --- | ---: |
| `1280x720` | `2x` |
| `1920x1080` | `3x` |
| `2560x1440` | `4x` |
| `3840x2160` | `6x` |

Production sprite import defaults are Point filtering, no mipmaps, and no lossy compression.
Pivots may be custom, but every frame in an animation must share the same grounded foot line.

## Background Sharpness Lock

- Environment art at every depth plane must retain crisp source edges at the reference
  resolution. Do not use blur, soft focus, or bilinear filtering as the default depth cue.
- Separate depth through value range, saturation, detail density, overlap, and parallax while
  preserving readable pixel boundaries in far, mid, gameplay, and foreground layers.
- Downscaled painterly sources must receive a reference-scale sharpening and pixel-cleanup pass
  before Unity import. The current deterministic baseline is the `crisp-v1` profile in
  `tools/art/crisp_environment.py`.
- Any later use of blur is a per-room proposal that requires a direct sharp-versus-blurred
  runtime comparison. The sharp version remains the production source until that comparison is
  approved.

**Exception — character sprites (Tique):** approved Tique frames are smooth-shaded painted
art (PixelLab-generated), not authored on a native low-resolution pixel grid. Displaying them
with Point filtering at the `42-48 px` locked height produces aliased, muddy results without a
dedicated re-authoring/quantization pass. Until that pass happens, Tique's import `filterMode`
is set to Bilinear instead of Point (all 54 approved frames under
`Assets/Clockwork/Art/Tique/Approved/`, changed 2026-07-22). This intentionally targets a
softer, painterly small-sprite look (closer to Hollow Knight than to flat-palette retro pixel
art) rather than genuine pixel art for the character. Point filtering remains the default for
tile/environment art unless a matching decision is made for that art separately.

## Character Size Guidance

Tique's `42-48 px` visible height is locked. Until character lineups are approved, these
ranges are composition guidance rather than additional locks:

- Standard Caligo resident: approximately `48-58 px`
- Common enemy: approximately `48-72 px`, according to gameplay role
- Bosses and exceptional silhouettes: established per encounter

Character hierarchy should come from authored source dimensions at `PPU 64`, not arbitrary
per-instance transform scaling.

## Depth And Parallax Policy

- Gameplay collision, doors, platforms, and structures that visually support characters are
  fixed in world space.
- Rear activity planes containing grounded NPCs are fixed in world space with their support
  architecture. A character must never slide against the structure it appears to stand on.
- Non-supporting middle-distance decoration may retain roughly `40-60%` of camera motion on
  screen. In the current `ParallaxLayer2D` convention this means a factor near `0.4-0.6`.
- Far scenery may retain roughly `15-30%` of camera motion on screen. In the current component
  convention this means a factor near `0.7-0.85`.
- A continuous decorative walkway must not be added solely to hide an incorrect ground line.

## Current Prototype Boundary

The current Unity slice was assembled around a `320x180` reference and mainly `PPU 32`, while
approved Tique sources use a different importer density. Per-object values such as Tique
`0.21`, NPC `0.32`, and Caligo background `0.625` are comparison-experiment values only.
They are not production metrics and must not be propagated to new rooms.

This lock does not immediately rewrite the existing importers or scene transforms. Doing so in
the experiment commit would make visual conclusions difficult to compare. Migration starts with
one Caligo benchmark room and proceeds only after the result is verified at multiple outputs.

## Migration Gate

A room is migrated to production metrics only when all of the following are true:

- Pixel Perfect reference is `640x360` and the camera shows `10 x 5.625` units.
- Production sprites import at `PPU 64` and use scale `1` unless an authored exception is recorded.
- Tique reads at `42-48 px` without changing collider or combat reach by accident.
- Ground, rear activity, mid, and far planes have explicit ownership and stable ground lines.
- Captures at `1280x720` and `1920x1080` show crisp integer scaling and no layer drift.
- Movement, jump, attack, gate, and smoke probes still pass after metric conversion.
