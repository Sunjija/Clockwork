@echo off
if not exist "%~dp0Builds\WindowsV3\TiqueReturn.exe" (
  echo No Unity player build exists yet.
  echo Activate Unity through Hub, then run Tools\Build-Windows.ps1.
  pause
  exit /b 1
)
start "Tique Return Circuit" "%~dp0Builds\WindowsV3\TiqueReturn.exe"
