# CLOCKWORK Current State

Updated: 2026-07-20
Branch: `main`
Last pushed base: `88580c3`

## Playable Route

`Limbus -> LimbusCaligoBridge -> CaligoMaintenanceShaft -> CaligoVillage -> CaligoPlaza -> CaligoDropShaft`

- Fresh Tique starts critically damaged at 2/5 HP with reduced movement and weapon output.
- Bridge tutorial uses a finite three-rat pack. Residual power failure leads to Morbi's
  workshop; repair restores 5/5 HP and normal output.
- Plaza has a checkpoint and working gates to the workshop and drop shaft.
- Drop shaft first traversal is one-way. `crossing-cavern` is data-only.
- Hook return is proposal-only and not implemented.

## Art Status

- Approved Tique action assets remain locked.
- Plaza uses `caligo-plaza-concept-v1.png` as a proposal benchmark only.
- Plaza collision is invisible greybox data, independent of the concept image.
- Final modular 32 PPU environment art is not approved or implemented.

## Source Ownership

- Build pipeline and shared helpers: `Assets/Clockwork/Editor/ApprovedPrototypeBuilder.cs`
- Plaza/drop implementation: `Assets/Clockwork/Editor/Builders/CaligoPlazaSceneBuilder.cs`
- Room id to scene mapping: `Assets/Clockwork/Scripts/Runtime/Rooms/RoomSceneRegistry.cs`
- Opening probes: `Assets/Clockwork/Scripts/Runtime/Testing/OpeningSmokeProbe.cs`
- Caligo route probes: `Assets/Clockwork/Scripts/Runtime/Testing/CaligoRouteSmokeProbe.cs`

## Verification Baseline

- `CLOCKWORK_APPROVED_BUILD_OK`
- `CLOCKWORK_WINDOWS_BUILD_OK`
- Eight probes followed by `CLOCKWORK_RUNTIME_SMOKE_OK`
- Runtime smoke log contains no warning, exception, or error.

## Cautions

- Maps and canon rulebooks are authoritative; do not silently change geography or story.
- Opening remains intentionally east-to-west/right-to-left. Improve visual guidance before
  considering a map reversal.
- Do not stage or delete untracked generated Tique experiment folders.
- Keep music changes in separate commits.
