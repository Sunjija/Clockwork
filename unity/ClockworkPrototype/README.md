# CLOCKWORK Unity Prototype

Unity 6000.5.3f1 conversion of the approved ACT1 web prototype snapshot.

Approval boundary: Git commit `c6c7862`.

## Controls

- Move: `A` / `D` or arrow keys
- Variable jump / double jump: `Z`
- Attack: `X`
- Dash: `C`
- Weapons: `1` fist, `2` greatsword, `3` hammer
- Hitbox overlay: `H`
- Reset scene: `R`

Open `Assets/Clockwork/Scenes/CaligoMaintenanceShaft.unity` and press Play.

The web prototype remains the visual reference. Only assets listed in
`Assets/Clockwork/approved-assets.json` are imported into this project.

The Caligo scene uses the repaired movement speed (`2.5` units/second) and
ground response (`21`). `TiqueMotor.SetDamagedState(true)` applies the early
damaged-state multiplier (`0.86`). Double jump uses a core-centered resonance
pulse; the deprecated downward jet frame is not used by the runtime sequence.
