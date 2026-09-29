param([string]$Editor = 'C:\Program Files\Unity\Hub\Editor\6000.5.3f1\Editor\Unity.exe')
$ErrorActionPreference = 'Stop'
$project = Split-Path $PSScriptRoot -Parent
$data = Join-Path (Split-Path $Editor -Parent) 'Data'
$dotnet = Join-Path $data 'DotNetSdk/dotnet.exe'
if (!(Test-Path -LiteralPath $dotnet)) { throw "Bundled .NET SDK not found: $dotnet" }
Push-Location $project
try {
    & $dotnet run --project Tools/ModelChecks/ModelChecks.csproj -- $project
    if ($LASTEXITCODE -ne 0) { throw 'Model tests failed.' }
    $output = Join-Path $project 'QA/StaticCompile'
    New-Item -ItemType Directory -Path $output -Force | Out-Null
    $compiler = Get-ChildItem -Path (Join-Path $data 'DotNetSdk/sdk/*/Roslyn/bincore/csc.dll') | Select-Object -First 1
    $references = @(
        Get-ChildItem (Join-Path $data 'UnityReferenceAssemblies/unity-4.8-api') -Filter '*.dll'
        Get-ChildItem (Join-Path $data 'UnityReferenceAssemblies/unity-4.8-api/Facades') -Filter '*.dll'
        Get-ChildItem (Join-Path $data 'Managed/UnityEngine') -Filter '*.dll'
    )
    $common = @('/nologo', '/target:library', '/nostdlib+', '/langversion:9', '/warn:4')
    $common += $references | ForEach-Object { '/reference:"' + $_.FullName + '"' }
    $runtime = Join-Path $output 'TiqueReturn.Runtime.dll'
    $runtimeArgs = $common + ('/out:"' + $runtime + '"')
    $runtimeArgs += Get-ChildItem Assets/Scripts -Filter '*.cs' | ForEach-Object { '"' + $_.FullName + '"' }
    $rsp = Join-Path $output 'runtime.rsp'
    $runtimeArgs | Set-Content -LiteralPath $rsp -Encoding utf8
    & $dotnet $compiler.FullName ('@' + $rsp)
    if ($LASTEXITCODE -ne 0) { throw 'Runtime C# compilation failed.' }
    $editorArgs = $common + '/define:UNITY_EDITOR,UNITY_EDITOR_WIN' + ('/reference:"' + $runtime + '"') + ('/out:"' + (Join-Path $output 'TiqueReturn.Editor.dll') + '"')
    $editorArgs += Get-ChildItem Assets/Editor -Filter '*.cs' | ForEach-Object { '"' + $_.FullName + '"' }
    $rsp = Join-Path $output 'editor.rsp'
    $editorArgs | Set-Content -LiteralPath $rsp -Encoding utf8
    & $dotnet $compiler.FullName ('@' + $rsp)
    if ($LASTEXITCODE -ne 0) { throw 'Editor C# compilation failed.' }
    [ordered]@{
        passed = $true
        unityVersion = '6000.5.3f1'
        scope = 'Roslyn compiles runtime and editor assemblies against installed Unity managed references. Does not run Unity, import assets or build a player.'
        unityRuntimeVerified = $false
    } | ConvertTo-Json | Set-Content -LiteralPath QA/source-compile.json -Encoding utf8
    Write-Host 'PASS runtime + editor source compilation. Unity runtime remains unverified.'
} finally { Pop-Location }
