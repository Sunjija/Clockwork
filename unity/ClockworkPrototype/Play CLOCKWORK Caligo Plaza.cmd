@echo off
setlocal

set "GAME_EXE=%~dp0Builds\Windows\ClockworkPrototype.exe"

if not exist "%GAME_EXE%" (
    echo CLOCKWORK Windows build was not found:
    echo %GAME_EXE%
    pause
    exit /b 1
)

start "" "%GAME_EXE%" -clockworkCaligoPreview
