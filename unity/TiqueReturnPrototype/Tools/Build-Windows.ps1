param([string]$Editor = 'C:\Program Files\Unity\Hub\Editor\6000.5.3f1\Editor\Unity.exe', [switch]$Legacy)
$ErrorActionPreference = 'Stop'
$project = Split-Path $PSScriptRoot -Parent
if (!(Test-Path -LiteralPath $Editor)) { throw 'Unity 6000.5.3f1 not found. Pass -Editor with your Unity.exe path.' }
New-Item -ItemType Directory -Path (Join-Path $project 'QA') -Force | Out-Null
$log = Join-Path $project $(if ($Legacy) {'QA/build.log'} else {'QA/build-v10.log'})
$destination = Join-Path $project $(if ($Legacy) {'Builds/Windows/TiqueReturn.exe'} else {'Builds/WindowsV10/TiqueReturn.exe'})
$method = if ($Legacy) {'ReturnBuild.Build'} else {'ReworkBuild.Build'}
$arguments = @('-batchmode','-quit','-projectPath',('"'+$project+'"'),'-executeMethod',$method,'-logFile',('"'+$log+'"'),'--return-output',('"'+$destination+'"'))
$build = Start-Process -FilePath $Editor -ArgumentList $arguments -WindowStyle Hidden -Wait -PassThru
if ($build.ExitCode -ne 0) {
    if ((Test-Path -LiteralPath $log) -and (Select-String -LiteralPath $log -Pattern 'No valid Unity Editor license' -Quiet)) {
        throw 'Unity could not start: no valid editor license. Source is preserved; activate through Unity Hub before building.'
    }
    throw "Unity build failed ($($build.ExitCode)). See $log"
}
if (!(Test-Path -LiteralPath $destination)) { throw "No executable was produced. See $log" }
Write-Host "Built: $destination"
Write-Host 'Play: open Play.cmd in the project folder.'
