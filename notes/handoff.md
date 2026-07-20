# CLOCKWORK Handoff

Updated: 2026-07-20 (Asia/Seoul)

> Compact entry point: read `notes/current-state.md`, `notes/next-task.md`, and
> `notes/verification.md` first. This file is the chronological archive.

## 2026-07-20 implementation structure refactor

- Split plaza/drop scene generation into `Editor/Builders/CaligoPlazaSceneBuilder.cs`.
- Moved playable room routing into `Runtime/Rooms/RoomSceneRegistry.cs`.
- Reduced `PrototypeBootstrap` to launch policy and split smoke coverage into opening and
  Caligo-route probe modules under `Runtime/Testing`.
- Added compact current/next/verification notes so ordinary changes do not require reading
  this full archive or the full canon documents.

## 2026-07-20 Caligo plaza and one-way drop shaft

- Added `CaligoPlaza` (`caligo-plaza`, map room 009) west of Morbi's workshop with a
  working workshop return gate, plaza checkpoint/save point, and a west gate into the
  drop shaft. Room/spawn routing is registered in `GameSession`.
- Added `CaligoDropShaft` (`caligo-drop-shaft`, map room 012) as a tall greybox traversal.
  Its first pass is deliberately one-way: there is no return gate to the plaza. The exit
  toward `crossing-cavern` (map room 013) is data-only until that scene is implemented.
  A later hook return remains a proposal and was not implemented.
- Reused `art/concepts/act1/03-caligo-v1.png` as
  `Art/Backgrounds/caligo-plaza-concept-v1.png` for a one-screen environment benchmark.
  This is a `[proposal]` concept candidate, not approved/canon production art. Collision
  remains an invisible greybox independent of the image.
- Added `QA/caligo-plaza-art-benchmark.png`. The environment-only capture hides the
  edit-time player renderer so prefab initialization cannot contaminate the comparison
  image; runtime player rendering is unchanged.
- Smoke coverage now has eight probes. `CLOCKWORK_PLAZA_PROBE` validates workshop entry,
  checkpoint activation, and the drop gate. `CLOCKWORK_DROP_SHAFT_PROBE` validates the
  fall/landing, absence of a plaza return gate, and the data-only cavern exit.
- Final Windows x64 build and the full route smoke test pass
  (`CLOCKWORK_APPROVED_BUILD_OK`, `CLOCKWORK_WINDOWS_BUILD_OK`,
  `CLOCKWORK_RUNTIME_SMOKE_OK`).

## 2026-07-20 bridge shutdown revised: finite fight, critically damaged Tique

- Fixed saved-game continuation ordering: a pending spawn is now consumed only by its
  destination scene, so the boot Limbus scene cannot steal a shaft/village spawn before
  the saved-room transition. `Play CLOCKWORK Fresh Opening.cmd` ignores disk saves for
  isolated opening playtests while preserving the normal continue save.
- The bridge does not collapse. Tique reaches it already near functional failure after
  Malphas's throw and the disposal fall. Fresh/unrepaired runs now start at 2/5 HP,
  retain the existing damaged movement penalty, and deal reduced weapon damage.
- `BridgeCollapseDirector` now stages a finite tutorial pack (slow solo rat + pair), with no
  respawning enemies. Tique shuts down at 0 HP, 0.9s after defeating the pack as residual
  power runs out, or on reaching the west end without fighting. Player skill is respected
  while Morbi's rescue remains deterministic.
- Collapse staging: input lock -> 0.5s beat -> 1.8s slow fade ("eyes closing") -> dry log
  lines ("…잔여 동력 임계치. 구동계 정지." / "…외부 개입 감지. 운반 중.") -> wake at Morbi's
  workshop bench repaired, full HP, save written to caligo/caligo-workshop.
- After repair the same static pack remains, while full HP, normal movement, and full weapon
  output make the before/after growth tangible.
- Rats now spawn from a `RatEnemy.prefab` built by the pipeline; `RatEnemy.Initialize`
  allows runtime direction/speed setup.
- Smoke test gained `CLOCKWORK_COLLAPSE_PROBE` (repaired flag, workshop wake position,
  full HP). Full six-probe route passes.

## 2026-07-20 Caligo village: Morbi and part identification

- New `CaligoVillage` scene (roomId `caligo`) west of the shaft: Morbi workshop bench
  (repair/save, `caligo/caligo-workshop`), hut silhouettes, warm light (canon §4 tone),
  and a west plaza gate. The shaft's flag-locked west gate is functional.
- `MorbiNpc`: state-based dry dialogue (canon §8 tone) — greeting/errand when empty-handed,
  the B-3 identification beat when carrying the Limbus part (sets `LIMBUS_MYSTERY_PART_IDENTIFIED`,
  HUD shows "Part: MOD attached"), then the purification-plant quest hook with the
  lock-before-key hint. W begins/advances lines; leaving the trigger closes dialogue.
- Loadout ruling recorded in docs (v5.5 F-1..F-4, adopted): 3 weapon slots + per-weapon MOD,
  fist always available but fist upgrades occupy a slot, bench-only loadout swap.
  No code needed yet — pool equals slots until a fourth weapon exists.
- Smoke test gained a village leg (dialogue-driven identification flag). Full route passes:
  Limbus -> bridge -> shaft -> village.
- Still deferred: 3-choice part selection and the actual MOD gameplay effect.
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
- Base commit: `88580c3` (`Refine damaged Tique opening shutdown flow`)
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
- Added the working Limbus-to-Caligo-to-plaza room route and data-only gates for
  destinations whose Unity scenes do not exist yet.
- Kept the approved Tique animation and attack assets unchanged.

## Missing by design

- Final industrial 32 PPU RuleTile art
- Final repair bench and gate visuals
- Production UI, controller glyphs, SFX, BGM integration, enemies, and boss systems
- Crossing cavern and later ACT1 Unity room scenes
- Production modular plaza art; the current full-screen concept is a benchmark candidate
- Full save-slot UI and save migration beyond schema version 1

## Test results

- Pass: Unity package resolution and script compilation.
- Pass: approved prefab and Caligo scene regeneration (`CLOCKWORK_APPROVED_BUILD_OK`).
- Pass: Windows x64 player build (`CLOCKWORK_WINDOWS_BUILD_OK`).
- Pass: isolated player runtime smoke (`CLOCKWORK_RUNTIME_SMOKE_OK`, exit code 0).
- Pass: runtime log contains no warning, exception, or error entries.
- Pass: runtime physics probe holds Tique at `y=-1.99` with `grounded=True` after 1.5 seconds.
- Pass: plaza checkpoint and gate route (`CLOCKWORK_PLAZA_PROBE`).
- Pass: one-way shaft fall and landing at `y=-9.99` (`CLOCKWORK_DROP_SHAFT_PROBE`).
- Pass: 1280x720 window capture shows the approved Tique sprite, background, HUD, floor, and platforms.
- Pass: 1280x720 plaza environment benchmark has no collision/debug overlay or capture artifact.
- Note: Unity logs a non-fatal package-cache assembly validation warning for a missing
  `Unity.Collections.LowLevel.ILSupport.dll`; compilation and Windows build still complete.

## Risks and cautions

- The current `2.5` unit movement speed preserves prototype camera-scale parity. Re-tune it after
  final 32 PPU room metrics are locked.
- `RoomGate` loads registered scenes; unknown destinations such as `crossing-cavern`
  intentionally remain data-only.
- Placeholder tile, workbench, and gate visuals are technical markers, not approved game art.
- The plaza concept image is a proposal benchmark, not a modular gameplay background or
  a canon art approval. Keep collision authored independently.
- Generated `Builds`, `Library`, `Logs`, `Temp`, and `UserSettings` remain excluded from Git.
- Do not stage the unrelated experimental sprite directories listed in Git status.

## Next work (priority order — pick up from the top)

1. **Plaza/drop playtest and art decision.** Check route direction, checkpoint placement,
   drop pacing, and whether `caligo-plaza-concept-v1.png` is useful as the visual target.
   Approval here means target mood/composition only; production art should become a modular
   32 PPU environment kit after geometry is stable.
2. **Shutdown-beat tuning (awaiting designer playtest).** Candidate knobs: starting HP 2/5,
   damaged output 0.6x, post-combat shutdown delay 0.9s, 0.5s beat + 1.8s fade timing,
   and blackout log wording (`BridgeCollapseDirector.OnGUI`). The finite-pack/residual-power
   structure is the current designer direction; tune values without reintroducing infinite spawns.
3. **Crossing cavern greybox** (`crossing-cavern`, map room 013) after the shaft. Preserve
   the map route and keep any unconfirmed hook-return details proposal-only.
4. **Healing system** — direction confirmed in `docs/99_master_context.md` §10: kills charge
   a resource, hold-to-consume heals (Hollow Knight style), ACT1 = low efficiency
   (waste-lentium). Needs resource gauge, hold input in `TiqueInputReader`, HUD display.
   Open numbers (charge per kill, heal cost/time) are designer calls — propose, don't decide.
5. **Combo matrix, fist axis (8 entries)** — slice combat target, table in
   `docs/99_master_context.md` §9. Build on `TiqueCombat`'s 3-slot structure. Note the
   loadout ruling F-1..F-4 (3 slots, per-weapon MOD, fist upgrades occupy a slot).
6. **32 PPU tile art pass** for Caligo/Limbus industrial palette; after tiles lock,
   re-tune movement from prototype-scale units (see Risks).
7. **Rat art**: replace the generated placeholder with approved frames; add death
   feedback/SFX. Rats spawn from `Prefabs/RatEnemy.prefab` (pipeline-built).
8. **Aseprite/2D Animation workflow** for the approved action frames (combo expansion prep).
9. Later: loadout swap UI at benches once a fourth weapon exists (until then pool == slots).

> Working agreement: whenever a session ends, update this handoff (done section + this list)
> so the next agent — Claude Code or Codex — can continue without conversation context.
> Canon lives in `docs/00_canon_rules_v5.4.md` + `docs/rulebook-v5.5-patch.md`;
> `docs/99_master_context.md` is the portable snapshot and must be kept in sync.
