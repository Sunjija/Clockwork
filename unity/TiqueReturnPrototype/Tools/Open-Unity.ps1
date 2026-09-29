param([string]$Editor = 'C:\Program Files\Unity\Hub\Editor\6000.5.3f1\Editor\Unity.exe')
$ErrorActionPreference = 'Stop'
$project = Split-Path $PSScriptRoot -Parent
if (!(Test-Path -LiteralPath $Editor)) { throw 'Unity 6000.5.3f1 is required. Pass -Editor with your Unity.exe path.' }
Write-Host 'Open Assets/Scenes/TiqueReturn.unity and press Play. A valid editor license is required.'
& $Editor -projectPath $project
