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
- Current 320x180 Pixel Perfect prototype reference rendered at 1280x720
- Locked production target: 640x360, PPU 64, and a 10 x 5.625 world-unit camera
- URP 2D renderer and global 2D light
- Data-only room exits for the Limbus bridge and Caligo
- Two active generated parallax layers in the combat lab, with near foreground reserved per room
- Curated pixel VFX and impact audio for fists, greatsword, hammer, and Lentium swaps
- IndustrialRuins brick collision fill and exposed platform-top tiles in the combat lab
- Proposal Caligo plaza composition with separate far/mid layers, modular platform dressing,
  and three non-colliding ambient residents
- Caligo experiment keeps the mid structure and rear NPC activity plane fixed in room space;
  the rejected continuous rear walkway is removed and only the far background uses parallax
- Role animation for the plaza mechanic and water attendant, plus a short stop-and-turn patrol
  for the clean-water carrier
- Tique's approved sprite presentation reduced to 70% of its previous screen size while gameplay
  movement and combat metrics remain unchanged

## Controls

- Move: `A` / `D`, arrow keys, gamepad stick, or D-pad
- Variable jump / double jump: `Z` or gamepad South
- Attack: `X` or gamepad West
- Dash: `C` or gamepad East
- Interact: `W`, Up, or gamepad North
- Weapons: `1` fist, `2` greatsword, `3` hammer
- With two Lentium segments, swap from fist using `2` or `3` to launch a red charge attack
- Hitbox overlay: `H`
- Reload current scene: `R` or gamepad Start
- Reset all test progress and return to the opening: `F1` or the HUD button
- Open the isolated grapple lab: `F2`; attach/release rope with `E`
- Open the isolated combat lab: `F3`; training targets restore indefinitely

Open `Assets/Clockwork/Scenes/CaligoMaintenanceShaft.unity` and press Play.
Run `Play CLOCKWORK Combat Lab.cmd` to open the isolated combat lab directly.
Run `Play CLOCKWORK Caligo Plaza.cmd` to open the proposal environment and ambient NPC test directly.
The project targets Standalone/Win64 at 1280x720 landscape. The Device Simulator may draw a
device frame, but the game orientation remains landscape; use the Game tab for desktop play.
Editor play and the Windows player reapply the 1280x720 window profile at startup.

## Placeholder boundary

`tile-placeholder-32.png`, the repair workbench block, and gate blocks are temporary technical visuals.
Replace them with production PPU 64 industrial RuleTile art and UI without changing collision or progression scripts.
Curated third-party prototype VFX and sound assets live under `Assets/Clockwork/ThirdParty/Curated` with their licenses.

Production measurements are defined in `docs/art/production-visual-metrics-v1.md`. Current
32 PPU imports and per-object transform scales remain experiment data until the Caligo benchmark
room is migrated and verified; do not copy those values into new production rooms.

The web prototype remains the visual reference. Only Tique assets listed in
`Assets/Clockwork/approved-assets.json` are used by the Unity player prefab.

The current movement speed (`2.5` units/second) preserves prototype camera-scale parity.
Re-tune it during the production-metrics benchmark without changing the approved feel blindly.

## Build verification

The editor menu `Clockwork > Build Approved Prototype` regenerates the prefab and scene.
Command-line builds use `ClockworkEditor.ApprovedPrototypeBuilder.BuildWindowsFromCommandLine`.
The runtime argument `-clockworkSmokeTest` validates the player, approved sprite, Input System,
Tilemap Collider, session, repair progression, and isolated labs without reading or writing a user save file.
