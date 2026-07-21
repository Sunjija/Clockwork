# CLOCKWORK Selected Assets

Curated on 2026-07-21. The original extracted packs remain untouched.

This folder is a prototype shortlist, not a canon art decision. Listen to audio and review recolors in the isolated Unity labs before using anything in story rooms.

## 01_READY_TO_IMPORT

### Art/Environment/Industrial

- `IndustrialRuins_32x32.png`
- Best current environment candidate.
- Test first in Combat Lab, then use selected railings, platforms, lights, pipes, and warning props in Caligo.
- Keep toxic green limited to actual poison. Do not recolor the whole room green.

### Art/VFX/Movement

- `Dust_Run-Sheet.png`
- `Dust_Jump-Sheet.png`
- `Dust_Fall_Impact-Sheet.png`
- `Dust_Smoke-Sheet.png`
- Use for run, jump, landing, collapse debris, and function-shutdown dust.
- Recolor orange pixels toward muted brass before final approval.

### Art/VFX/Combat

- `Hit-Sheet.png`: fist hit and automatic third-hit feedback.
- `Blue_Sparks-Sheet.png`: Lentium and core feedback. Match the approved cyan core color.
- `Explosion-Sheet.png`: collapse and heavy-weapon debris source.
- `pixel_art_sword_slash_sprites.png`: greatsword and charged swap trail candidate.

### Audio

- `Combat/Fist`: medium and heavy punch variations.
- `Combat/HeavyWeapon`: heavy metal and plate impacts for hammer and charged finishers.
- `Combat/Greatsword`: knife draw and slice sources. Layer or pitch down for the greatsword.
- `Movement/Footsteps`: concrete and wood variations.
- `Grapple`: metal click, latch, and rope/structure creaks.
- `Lentium`: force-field, metal-energy, and low-frequency charge sources.
- `Environment/Collapse`: mining and crunchy collapse impacts.
- `UI`: click and switch audition set.

Audio files are filename-based shortlists. They still require listening, loudness matching, and in-game timing tests before approval.

## 02_HOLD_REWORK

### Art/Environment/Cave

- `MyCaveTileset_32x32.png`
- Geometry is useful for Crossing Cavern and B24, but the magenta/orange palette does not match CLOCKWORK.
- Do not import into story scenes until a muted rock, oxidized metal, and restrained toxic-green recolor exists.

### Art/Background/IndustrialParallax

- Four seamless industrial background layers.
- The current scene is dominated by green, which conflicts with CLOCKWORK's poison readability rule.
- Use only after shifting most green into cool gray and dark teal while reserving bright green for poison.

### Art/VFX/ParticleSources

- Dirt, smoke, spark, and trace source textures from Kenney.
- These are smooth high-resolution effects, not finished pixel-art assets.
- Downsample with nearest-neighbor, reduce the palette, and test at the logical pixel scale before use.

## Excluded From The Shortlist

- Pixelvania heroes, enemies, boss, projectiles, pickups, and full environment: they would replace CLOCKWORK's identity instead of supporting it.
- Pixelvania and Kenney UI packs: useful references, but their magenta or bright generic palettes do not match the current HUD.
- `ExtraordinaryPlanet-main`: duplicate Godot example project and implementation files.
- `Slash Effect Collection`: soft shaded, high-resolution style does not match the current pixel-art combat language.
- PSD, XCF, Unity package, Godot scripts, fonts, previews, and duplicate source files.

## Unity Import

Copy only the needed files from `01_READY_TO_IMPORT` into the Unity project under:

`Assets/Clockwork/ThirdParty/Curated/`

Recommended settings for the current 32 PPU prototype labs:

- Texture Type: Sprite (2D and UI)
- Sprite Mode: Multiple for sheets
- Pixels Per Unit: 32
- Filter Mode: Point (no filter)
- Compression: None
- Generate Mip Maps: Off
- Mesh Type: Full Rect

These settings preserve the source packs for comparison. Production rooms follow
`docs/art/production-visual-metrics-v1.md` and migrate selected art to PPU 64 rather than
copying the current lab transforms.

Recommended short SFX settings:

- Load Type: Decompress On Load
- Compression Format: PCM or ADPCM
- Preload Audio Data: On
- Force To Mono: On for positional gameplay sounds

Commit selected assets, Unity `.meta` files, this README, and `03_REFERENCE_LICENSES`. Do not commit the full downloaded packs or example projects.
