# CLOCKWORK Handoff

Updated: 2026-07-20 (Asia/Seoul)

## 2026-07-20 playtest feedback pass: transition dressing, rat staging

- Room loads now fade to black (0.18s) and back in (0.25s) through a persistent `ScreenFader`,
  Hollow Knight style; death respawn reuses the same fade. Room-per-scene structure stays —
  transition polish was the missing piece, not a world merge.
- Entry spawns moved next to their gates (±6.0) so arrivals read as walking through the door
  while held movement carries momentum into the room.
- Bridge rats restaged to the rulebook §9 four-beat rule (from the current west entry):
  one slow solo rat (0.7 speed) teaches the swing, then a pair (0.95) escalates. Rat HP 2 → 3
  (fist 3 / greatsword 2 / hammer 1 hits). Restage east-to-west when the Limbus room exists.
- Smoke test updated for the new spawn position and three rats; all probes pass through the
  fade-based transition.

## 2026-07-20 opening slice: bridge room, rats, health

- Added `TiqueHealth` (5 HP, 1s i-frames, knockback + hit stun via `TiqueMotor.Stun`,
  death respawns at the last saved room/spawn). HP persists across room loads through
  `GameSession.RuntimeHealth`; the repair bench refills it on save.
- Added `EnemyHealth` and `RatEnemy` (patrol with wall/ledge turnaround, 1 contact damage).
  Rats have 2 HP; attacks now deal damage (fist 1 / greatsword 2 / hammer 3, once per swing)
  via `AttackDefinition.Damage` and an overlap check during the active window.
- `RoomGate` now loads destination scenes on player touch when the destination room exists
  (`GameSession.LoadRoom` + `SpawnPoint`/`TiqueSpawnPlacer`). Unknown rooms stay data-only.
- New `LimbusCaligoBridge` scene (RGN-011): flat crossing with two patrolling rats, placeholder
  light, gates west to the maintenance shaft (functional) and east to Limbus (data-only).
- Map orientation fix (maps are canon): in the shaft the bridge gate now sits east and the
  flag-locked Caligo village gate west; previous builds had them swapped.
- Smoke test now also validates damage + i-frames, the gate transition into the bridge,
  spawn placement, rat presence, and HP persistence across the load
  (`CLOCKWORK_HEALTH_PROBE`, `CLOCKWORK_BRIDGE_PROBE`).
- Still missing by design: bridge sewage-waterfall art (v5.5 B-1), the scripted collapse
  beat after the bridge tutorial, rat sprite is a generated placeholder, no SFX.

## 2026-07-20 review fixes

- Fixed `RepairSavePoint` trigger: non-player colliders entering the trigger no longer clear the
  nearby player reference, so interaction survives future enemies/projectiles overlapping the bench.
- Added a 0.1s jump buffer to `TiqueMotor` (pairs with the existing coyote time). A jump pressed
  just before landing now fires on touchdown; double jump still requires a fresh press so a
  buffered input cannot silently consume the air jump after a dash.
- Deduplicated takeoff/landing/double-jump animation durations into `TiqueMotor` constants.
- `GameSession.Load` now backs up a save with a mismatched `schemaVersion` to
  `clockwork-save-01.json.v{N}.bak` before starting fresh, instead of silently overwriting it later.
- Moved the scene-reload gamepad binding from Start to Select to avoid accidental resets
  during pad playtests (keyboard `R` unchanged).

## Git state

- Branch: `main`
- Tracking: `origin/main`
- Base commit: `99cfda9` (`Add Unity prototype and refine ACT1 movement`)
- Existing untracked experimental sprite directories under
  `prototypes/lento-vertical-slice/assets/tique/generated/` were not modified or staged.

## Completed

- Installed Unity packages: Input System 1.19.0, Cinemachine 3.1.7, URP 17.5.0,
  Tilemap Extras 8.0.3, Pixel Perfect 6.0.0, 2D Animation 15.1.0, and Aseprite Importer 5.0.3.
- Replaced direct legacy keyboard polling with `TiqueInputReader` actions for keyboard and gamepad.
- Added versioned JSON session data for flags, abilities, room ID, and spawn ID.
- Added `TIQUE_REPAIRED` progression and connected it to damaged/repaired movement speed.
- Added a Caligo repair/save workbench. Interact with `W`, Up, or gamepad North.
- Rebuilt Caligo collision as RuleTile + Tilemap Collider + Composite Collider.
- Added Cinemachine 3 follow/confiner, 320x180 Pixel Perfect reference, URP 2D renderer,
  and a global 2D light.
- Added data-only room gates toward the Limbus bridge and Caligo.
- Kept the approved Tique animation and attack assets unchanged.

## Missing by design

- Final industrial 32 PPU RuleTile art
- Final repair bench and gate visuals
- Production UI, controller glyphs, SFX, BGM integration, enemies, and boss systems
- Adjacent Unity room scenes for the Limbus bridge and Caligo
- Full save-slot UI and save migration beyond schema version 1

## Test results

- Pass: Unity package resolution and script compilation.
- Pass: approved prefab and Caligo scene regeneration (`CLOCKWORK_APPROVED_BUILD_OK`).
- Pass: Windows x64 player build (`CLOCKWORK_WINDOWS_BUILD_OK`).
- Pass: isolated player runtime smoke (`CLOCKWORK_RUNTIME_SMOKE_OK`, exit code 0).
- Pass: runtime log contains no warning, exception, or error entries.
- Pass: runtime physics probe holds Tique at `y=-1.99` with `grounded=True` after 1.5 seconds.
- Pass: 1280x720 window capture shows the approved Tique sprite, background, HUD, floor, and platforms.
- Note: Unity logs a non-fatal package-cache assembly validation warning for a missing
  `Unity.Collections.LowLevel.ILSupport.dll`; compilation and Windows build still complete.

## Risks and cautions

- The current `2.5` unit movement speed preserves prototype camera-scale parity. Re-tune it after
  final 32 PPU room metrics are locked.
- `RoomGate` stores validated destination data but does not load missing adjacent scenes yet.
- Placeholder tile, workbench, and gate visuals are technical markers, not approved game art.
- Generated `Builds`, `Library`, `Logs`, `Temp`, and `UserSettings` remain excluded from Git.
- Do not stage the unrelated experimental sprite directories listed in Git status.

## Next work

1. Replace the placeholder RuleTile sprite with a coherent 32 PPU Caligo/Limbus industrial palette.
2. Build the Caligo village and Limbus rooms as scenes (bridge is done; their gates are data-only).
3. Replace the generated rat placeholder with approved sprite frames and add death feedback/SFX.
4. Move approved action frames into Aseprite source files or a 2D Animation workflow for combo expansion.
5. Re-tune movement from prototype-scale units after final tile and camera metrics are locked.
6. Decide the scripted collapse beat (bridge tutorial → Morbi rescue) staging once the village scene exists.
