@echo off
setlocal

set "UNITY_EXE=C:\Program Files\Unity\Hub\Editor\6000.5.3f1\Editor\Unity.exe"

if not exist "%UNITY_EXE%" (
    echo Unity 6000.5.3f1 was not found:
    echo %UNITY_EXE%
    pause
    exit /b 1
)

start "" "%UNITY_EXE%" -projectPath "%~dp0"
