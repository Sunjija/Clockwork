# CLOCKWORK Working Notes

Use these files as the default entry point for implementation work:

1. `current-state.md` — compact implementation snapshot and ownership map.
2. `next-task.md` — one active target, constraints, and completion checks.
3. `verification.md` — build, smoke, and play commands.

Do not read `handoff.md` from top to bottom for ordinary changes. It is the chronological
archive. Search it only when a current note points to an older decision.

Do not read the full canon documents unless a task requires a story or rules decision.
Search the relevant heading in `docs/00_canon_rules_v5.4.md` and
`docs/rulebook-v5.5-patch.md`, then preserve canon/proposal/rejected status explicitly.

## Code Ownership

- Prototype build orchestration: `ApprovedPrototypeBuilder.cs`
- Plaza and drop shaft generation: `Editor/Builders/CaligoPlazaSceneBuilder.cs`
- Playable room index: `Runtime/Rooms/RoomSceneRegistry.cs`
- Smoke orchestration: `Runtime/Testing/PrototypeSmokeTestRunner.cs`
- Limbus/bridge probes: `Runtime/Testing/OpeningSmokeProbe.cs`
- Caligo/plaza/drop probes: `Runtime/Testing/CaligoRouteSmokeProbe.cs`

Generated `.unity` scenes are build outputs. Change their builder source instead of hand
editing scene YAML. Ignore unrelated generated Tique experiment directories.
