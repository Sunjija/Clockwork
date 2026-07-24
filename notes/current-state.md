# CLOCKWORK Current State

Updated: 2026-07-22
Branch: `main`
Previous pushed base: `1564452`

## Playable Route

`Limbus -> LimbusCaligoBridge -> CaligoMaintenanceShaft -> CaligoVillage -> CaligoPlaza -> CaligoDropShaft`

- Fresh Tique starts critically damaged at 2/5 HP with reduced movement and weapon output.
- Limbus opens facing west; sealed-chute dressing, route lights, and directional camera lead
  reinforce the intentional right-to-left first move without tutorial text.
- Bridge tutorial uses a finite three-rat pack. Residual power failure leads to Morbi's
  workshop; repair restores 5/5 HP and normal output.
- Plaza has a checkpoint and working gates to the workshop and drop shaft.
- Drop shaft first traversal is one-way. `crossing-cavern` is data-only.
- Hook return is proposal-only and not implemented.
- The prototype HUD and `F1` reset the session and save file to `Limbus/start-awakening`.
- Combat now reads staged `ComboDefinition` data. Fist uses three distinct single-input steps:
  right straight, left straight, then a stronger finisher. The step count persists between
  attacks and every third basic input is enhanced without a timing requirement.
- The third fist step emits
  a gold gear pulse so the finisher and weapon-transition timing are visible without debug hitboxes.
  The HUD only fills executed strikes; alternating impact strokes distinguish the two hands with
  the current approved single-hand animation set.
- `WeaponDefinition` owns basic and transition combos. With at least 10 Lentium, swapping from
  fist to slot `2` or `3` immediately spends two segments and launches a red-wave greatsword or
  hammer charge attack; no attack-button chord is required. A swap during another strike waits
  for that strike to end. With insufficient energy the same input performs a plain free swap.
  The 10 cost is proposal tuning, and reverse utility transitions remain unimplemented.
- Successful hit/defeat events feed a segmented Lentium energy prototype. The current +5 hit,
  +5 defeat bonus, 100 capacity, and 10-cost swap combo are proposal tuning. Transition-combo
  consumption is connected; hold-to-heal consumption remains unimplemented.
- The Unity target is Standalone/Win64 at 1280x720. Mobile orientation is locked to landscape so
  Device Simulator cannot silently present the game as a portrait layout. Editor play and the
  Windows player reapply the 16:9 window profile at startup instead of restoring an old resolution.
- `F2` opens a non-canon Grapple Lab. Rope travel, soft reel-in, spring tension, pendulum momentum,
  release velocity, and `E` input are isolated from progression pending post-Lento integration.
- `F3` opens a non-canon Combat Lab with three stationary targets that restore after every defeat,
  allowing unlimited combo and transition testing without changing story-room encounters.

## Art Status

- Approved Tique action assets remain locked.
- Production visual metrics are locked in `docs/art/production-visual-metrics-v1.md`:
  `640x360`, `PPU 64`, a `10 x 5.625` world-unit camera, and a `42-48 px` visible Tique.
- All 54 approved Tique sprite imports (`Assets/Clockwork/Art/Tique/Approved/`) were switched
  from Point to Bilinear filtering (2026-07-22). The approved frames are smooth-shaded painted
  art, not native low-res pixel art, and downscaling them to the `42-48 px` lock with Point
  filtering produced aliased/muddy results. This is a deliberate style choice (soft small
  sprite, closer to Hollow Knight than flat-palette pixel art) documented in
  `production-visual-metrics-v1.md`. Tile/environment art is unaffected and still defaults to
  Point filtering.
- Approved Tique frames remain unchanged. Their current Unity presentation scale is 70% of the
  previous prototype value only for comparison against the existing 32 PPU environment.
- Plaza uses proposal `03-caligo` far/mid layers and modular platform dressing. The previous
  `caligo-plaza-concept-v1.png` remains a benchmark source but is no longer the generated
  plaza scene's only background.
- Current values such as background `0.625`, NPC `0.32`, and Tique `0.21` are proposal
  experiment values, not production scale locks. New production assets must use the shared
  PPU and authored dimensions rather than copying these transform scales.
- The continuous rear walkway experiment was rejected and removed. The mid structures and
  NPC activity plane are fixed in room space at `y=-1.75`; only the far layer uses parallax.
- Three proposal background residents occupy work-specific positions: mechanic, water-ration
  attendant, and clean-water carrier. Only the carrier patrols within a short rear activity route.
- Plaza collision is invisible greybox data, independent of the concept image.
- These modular 32 PPU environment and resident assets are implemented for evaluation but are
  not approved/canon production art. The first migration target is one Caligo benchmark room.

## Source Ownership

- Build pipeline and shared helpers: `Assets/Clockwork/Editor/ApprovedPrototypeBuilder.cs`
- Limbus opening: `Assets/Clockwork/Editor/Builders/LimbusOpeningSceneBuilder.cs`
- Directional camera lead: `Assets/Clockwork/Scripts/Runtime/Camera/DirectionalCameraTarget.cs`
- Plaza/drop implementation: `Assets/Clockwork/Editor/Builders/CaligoPlazaSceneBuilder.cs`
- Grapple/Combat labs: `Assets/Clockwork/Editor/Builders/GrappleLabSceneBuilder.cs` and
  `Assets/Clockwork/Editor/Builders/CombatLabSceneBuilder.cs`
- Room id to scene mapping: `Assets/Clockwork/Scripts/Runtime/Rooms/RoomSceneRegistry.cs`
- Opening probes: `Assets/Clockwork/Scripts/Runtime/Testing/OpeningSmokeProbe.cs`
- Caligo route probes: `Assets/Clockwork/Scripts/Runtime/Testing/CaligoRouteSmokeProbe.cs`

## Verification Baseline

- `CLOCKWORK_APPROVED_BUILD_OK`
- `CLOCKWORK_WINDOWS_BUILD_OK`
- All route, combat-lab, grapple-lab, and reset probes followed by `CLOCKWORK_RUNTIME_SMOKE_OK`
- Runtime smoke log contains no warning, exception, or error.

## Cautions

- Maps and canon rulebooks are authoritative; do not silently change geography or story.
- Opening remains intentionally east-to-west/right-to-left. Improve visual guidance before
  considering a map reversal.
- Do not stage or delete untracked generated Tique experiment folders.
- Keep music changes in separate commits.
