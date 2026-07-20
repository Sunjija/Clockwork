# CLOCKWORK Next Task

Status: ready

## Target

`crossing-cavern` greybox after the Caligo drop shaft.

## Read Only

- `notes/current-state.md`
- the map source for room `013 crossing-cavern`
- `Editor/Builders/CaligoPlazaSceneBuilder.cs`
- `Runtime/Testing/CaligoRouteSmokeProbe.cs`

## Change

- Add the cavern as a separate greybox scene and registry entry.
- Connect the drop-shaft landing to the cavern entrance.
- Add a route probe for the new transition and arrival point.

## Preserve

- Map-authored room order and geography.
- Existing combat, damaged-state, save, and room-transition behavior.
- Canon documents and approved Tique assets.
- Hook return remains proposal-only and unimplemented.

## Done When

- The full route reaches `crossing-cavern` from the drop shaft.
- Existing probes and the new cavern probe pass.
- Fresh Windows build launches directly.
