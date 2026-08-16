# =============================================================================
# AI-local auto-start installer
# Registers a Windows scheduled task that starts both SaaS services at logon.
# Usage: right-click > Run with PowerShell, or:
#       powershell -ExecutionPolicy Bypass -File install-autostart.ps1
# Note: run once as Administrator for reliable registration.
# =============================================================================
$ErrorActionPreference = 'Stop'

$ROOT = Split-Path -Parent $PSScriptRoot
$SCRIPT = Join-Path $ROOT 'scripts\start-services.ps1'
$TASK = 'AI-Local-Services'

if (-not (Test-Path $SCRIPT)) {
    Write-Host "[ERROR] start-services.ps1 not found: $SCRIPT" -ForegroundColor Red
    exit 1
}

$action = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$SCRIPT`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Register-ScheduledTask -TaskName $TASK -Action $action -Trigger $trigger -Settings $settings -Force
    Write-Host "[OK] Scheduled task '$TASK' registered." -ForegroundColor Green
    Write-Host '     Services will auto-start at logon.'
    Write-Host '     Starting now...'
    Start-ScheduledTask -TaskName $TASK
    Write-Host "[OK] Task started now." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Register failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host '       Please re-run this script as Administrator.' -ForegroundColor Yellow
    exit 1
}

Write-Host ''
Write-Host 'Done. URLs: http://127.0.0.1:8000 (AI-Local) | http://127.0.0.1:8001 (WeChat-POI)'
Write-Host 'Uninstall: powershell -Command "Unregister-ScheduledTask -TaskName AI-Local-Services -Confirm:$false"'