$ErrorActionPreference = "SilentlyContinue"
Get-Process "joss-ai-cleanup-core" | Stop-Process -Force
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "JossAICleanup"
Remove-Item -Recurse -Force (Join-Path $env:LOCALAPPDATA "Joss AI Cleanup")
Write-Host "Joss AI Cleanup Core 已卸载。Windows 凭据管理器中的 API Key 需按需手动删除。"
