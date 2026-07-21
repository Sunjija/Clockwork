# CLOCKWORK Next Task

Status: ready

## Target

Migrate one Caligo benchmark room to Production Visual Metrics v1.

## Read Only

- `notes/current-state.md`
- `docs/art/production-visual-metrics-v1.md`
- `Editor/Builders/CaligoPlazaSceneBuilder.cs`
- `Runtime/Testing/CaligoRouteSmokeProbe.cs`

## Change

- Convert one duplicate/benchmark Caligo composition to `640x360`, `PPU 64`, and scale-1 art.
- Preserve the current playable scene as a before/after reference until the benchmark is approved.
- Capture 720p and 1080p output and compare character size, ground line, and depth motion.

## Preserve

- Current playable route and map-authored geography.
- Existing combat, damaged-state, save, and room-transition behavior.
- Canon documents and approved Tique assets.
- Current proposal scene remains available for direct comparison.

## Done When

- Tique is visibly `42-48` reference pixels tall with no accidental collider/combat change.
- Grounded NPCs and their support structures have no relative layer drift.
- 720p and 1080p captures are crisp, and existing runtime probes pass.
