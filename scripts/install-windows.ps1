$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Source = Join-Path $ScriptDir "joss-ai-cleanup-core.exe"
$InstallDir = Join-Path $env:LOCALAPPDATA "Joss AI Cleanup"
$Target = Join-Path $InstallDir "joss-ai-cleanup-core.exe"

if (-not (Test-Path $Source)) {
    throw "未找到 $Source"
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item -Force $Source $Target

$RunKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$LaunchCommand = "powershell.exe -NoProfile -WindowStyle Hidden -Command `"Start-Process -WindowStyle Hidden -FilePath '$Target' -ArgumentList 'serve --host 127.0.0.1 --port 18780'`""
New-ItemProperty -Path $RunKey -Name "JossAICleanup" -Value $LaunchCommand -PropertyType String -Force | Out-Null

Get-Process "joss-ai-cleanup-core" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Process -WindowStyle Hidden -FilePath $Target -ArgumentList "serve --host 127.0.0.1 --port 18780"

Write-Host "安装完成。核心地址：http://127.0.0.1:18780"
