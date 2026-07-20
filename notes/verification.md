# CLOCKWORK Verification

Unity: `6000.5.3f1`
Project: `unity/ClockworkPrototype`

## Build

Execute editor method:

`ClockworkEditor.ApprovedPrototypeBuilder.BuildWindowsFromCommandLine`

Expected markers:

- `CLOCKWORK_APPROVED_BUILD_OK`
- `CLOCKWORK_WINDOWS_BUILD_OK`

## Runtime Smoke

Run:

`Builds/Windows/ClockworkPrototype.exe -batchmode -clockworkSmokeTest -logFile <log>`

Expected final marker:

`CLOCKWORK_RUNTIME_SMOKE_OK`

Target ownership:

- Limbus, health, bridge, shutdown: `OpeningSmokeProbe.cs`
- Maintenance shaft, village, plaza, drop shaft: `CaligoRouteSmokeProbe.cs`

## Fresh Playtest

Run:

`Builds/Windows/ClockworkPrototype.exe -clockworkFreshOpening -logFile <log>`

This ignores disk saves for the isolated opening test. Directly launch the executable for
the user; local Markdown links do not reliably start Windows applications in Codex.
