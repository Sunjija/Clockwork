# CLOCKWORK Handoff

Updated: 2026-07-20 (Asia/Seoul)

## 2026-07-20 scripted bridge collapse (canon opening defeat)

- `BridgeCollapseDirector` stages the intended opening: before repair the rat swarm cannot
  be beaten — killed rats are replaced every 1.6s from the bridge edges (3 alive cap), and
  Tique collapses either at 0 HP (via `TiqueHealth.DeathOverride`) or on reaching the west
  end trigger (accumulated damage per canon A-1), whichever comes first.
- Collapse staging: input lock -> 0.5s beat -> 1.8s slow fade ("eyes closing") -> dry log
  lines ("…구동계 정지. 신호 미약." / "…외부 개입 감지. 운반 중.") -> wake at Morbi's
  workshop bench repaired, full HP, save written to caligo/caligo-workshop.
- After repair the bridge reverts to the static staged pack (slow solo rat + pair, no
  respawn) so the once-unbeatable swarm becomes beatable — growth made tangible.
- Rats now spawn from a `RatEnemy.prefab` built by the pipeline; `RatEnemy.Initialize`
  allows runtime direction/speed setup.
- Smoke test gained `CLOCKWORK_COLLAPSE_PROBE` (repaired flag, workshop wake position,
  full HP). Full six-probe route passes.

## 2026-07-20 Caligo village: Morbi and part identification

- New `CaligoVillage` scene (roomId `caligo`) west of the shaft: Morbi workshop bench
  (repair/save, `caligo/caligo-workshop`), hut silhouettes, warm light (canon §4 tone),
  west plaza gate left data-only. The shaft's flag-locked west gate is now functional.
- `MorbiNpc`: state-based dry dialogue (canon §8 tone) — greeting/errand when empty-handed,
  the B-3 identification beat when carrying the Limbus part (sets `LIMBUS_MYSTERY_PART_IDENTIFIED`,
  HUD shows "Part: MOD attached"), then the purification-plant quest hook with the
  lock-before-key hint. W begins/advances lines; leaving the trigger closes dialogue.
- Loadout ruling recorded in docs (v5.5 F-1..F-4, adopted): 3 weapon slots + per-weapon MOD,
  fist always available but fist upgrades occupy a slot, bench-only loadout swap.
  No code needed yet — pool equals slots until a fourth weapon exists.
- Smoke test gained a village leg (dialogue-driven identification flag). Full route passes:
  Limbus -> bridge -> shaft -> village.
- Still deferred: 3-choice part selection, actual MOD gameplay effect, plaza room.
  (The collapse/rescue staging landed the same day — see the section above.)

## 2026-07-20 Limbus room: canon opening start

- New `Limbus` scene (RGN-006, roomId `limbus`): the game now boots at the canon awakening
  point under the disposal-chute terminus (v5.5 A-1/C-2), east side of a combat-free scrap
  plain whose mound heights rise westward as a single-jump tutorial (rulebook §9).
- `MysteryPartPickup` (v5.5 B-3 first treasure): W-interact on the westmost mound sets
  `LIMBUS_MYSTERY_PART`; HUD shows "Part: unidentified". Morbi's identification/MOD attach
  waits for the Caligo village scene. 3-choice selection is also deferred — single part for now.
- Bridge rewired for the canon east-to-west crossing: east gate ↔ Limbus, new east spawn,
  rats restaged so the slow solo rat meets the player entering from Limbus, pair mid-bridge.
- Fresh saves start at `limbus/start-awakening`; on boot `GameSession` continues into the
  saved room (fade transition) when it differs from the boot scene. Smoke runs skip this.
- Smoke test now walks the whole opening route: Limbus checks + part pickup + damage probes
  → bridge (rats, HP persistence) → shaft (bench repair flag). All probes pass.

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

## Next work (priority order — pick up from the top)

1. **Collapse-beat tuning (awaiting designer playtest).** Candidate knobs: 0.5s beat + 1.8s fade
   timing, blackout log wording (`BridgeCollapseDirector.OnGUI`), pre-repair rat pressure
   (respawn 1.6s / pack of 3). Do not restructure — the flow itself is approved canon.
2. **Plaza room** (`caligo-plaza`, canon CP) west of the workshop, then the **one-way drop
   shaft** toward the crossing cavern — extends the critical path toward the purification
   plant. Follow the existing scene pattern in `ApprovedPrototypeBuilder` (room id in
   `GameSession.RoomScenes`, gates + spawn points, smoke-test leg).
3. **Healing system** — direction confirmed in `docs/99_master_context.md` §10: kills charge
   a resource, hold-to-consume heals (Hollow Knight style), ACT1 = low efficiency
   (waste-lentium). Needs resource gauge, hold input in `TiqueInputReader`, HUD display.
   Open numbers (charge per kill, heal cost/time) are designer calls — propose, don't decide.
4. **Combo matrix, fist axis (8 entries)** — slice combat target, table in
   `docs/99_master_context.md` §9. Build on `TiqueCombat`'s 3-slot structure. Note the
   loadout ruling F-1..F-4 (3 slots, per-weapon MOD, fist upgrades occupy a slot).
5. **32 PPU tile art pass** for Caligo/Limbus industrial palette; after tiles lock,
   re-tune movement from prototype-scale units (see Risks).
6. **Rat art**: replace the generated placeholder with approved frames; add death
   feedback/SFX. Rats spawn from `Prefabs/RatEnemy.prefab` (pipeline-built).
7. **Aseprite/2D Animation workflow** for the approved action frames (combo expansion prep).
8. Later: loadout swap UI at benches once a fourth weapon exists (until then pool == slots).

> Working agreement: whenever a session ends, update this handoff (done section + this list)
> so the next agent — Claude Code or Codex — can continue without conversation context.
> Canon lives in `docs/00_canon_rules_v5.4.md` + `docs/rulebook-v5.5-patch.md`;
> `docs/99_master_context.md` is the portable snapshot and must be kept in sync.
