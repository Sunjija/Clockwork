# CLOCKWORK Unity Foundation

Unity `6000.5.3f1` production foundation converted from the approved ACT1 web prototype snapshot.
The approved Tique animation boundary remains Git commit `c6c7862`.

## Installed Unity packages

- Input System `1.19.0`
- Cinemachine `3.1.7`
- Universal Render Pipeline `17.5.0`
- 2D Tilemap Extras `8.0.3`
- 2D Pixel Perfect `6.0.0`
- 2D Animation `15.1.0`
- Aseprite Importer `5.0.3`

## Implemented foundation

- Input System keyboard and gamepad action adapter
- Approved idle, walk, jump, double-jump, dash, fist, greatsword, and hammer sequences
- Variable jump, coyote time, double jump, dash, and three attack definitions
- JSON save session with versioned flags, abilities, room ID, and spawn ID
- Damaged/repaired movement state driven by `TIQUE_REPAIRED`
- Caligo repair workbench that repairs and saves with `W` / Up
- RuleTile room collision with Tilemap Collider and Composite Collider
- Cinemachine 3 follow camera with a 2D confiner
- 320x180 Pixel Perfect reference rendered at 1280x720
- URP 2D renderer and global 2D light
- Data-only room exits for the Limbus bridge and Caligo

## Controls

- Move: `A` / `D`, arrow keys, gamepad stick, or D-pad
- Variable jump / double jump: `Z` or gamepad South
- Attack: `X` or gamepad West
- Dash: `C` or gamepad East
- Interact: `W`, Up, or gamepad North
- Weapons: `1` fist, `2` greatsword, `3` hammer
- Hitbox overlay: `H`
- Reset scene: `R` or gamepad Start

Open `Assets/Clockwork/Scenes/CaligoMaintenanceShaft.unity` and press Play.

## Placeholder boundary

`tile-placeholder-32.png`, the repair workbench block, and gate blocks are temporary technical visuals.
Replace them with final 32 PPU industrial RuleTile art, UI, and audio without changing collision or progression scripts.
No external character, enemy, boss, UI, or sound asset has been added.

The web prototype remains the visual reference. Only Tique assets listed in
`Assets/Clockwork/approved-assets.json` are used by the Unity player prefab.

The current movement speed (`2.5` units/second) preserves prototype camera-scale parity.
Re-tune it when the final 32 PPU room metrics and tile dimensions are locked.

## Build verification

The editor menu `Clockwork > Build Approved Prototype` regenerates the prefab and scene.
Command-line builds use `ClockworkEditor.ApprovedPrototypeBuilder.BuildWindowsFromCommandLine`.
The runtime argument `-clockworkSmokeTest` validates the player, approved sprite, Input System,
Tilemap Collider, session, and repair progression without reading or writing a user save file.
