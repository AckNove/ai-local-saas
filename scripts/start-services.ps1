# =============================================================================
# AI-local workspace one-click start script
# Starts both SaaS backends as detached processes (survive window close)
#   - AI-Local-Growth-SaaS      -> http://127.0.0.1:8000
#   - WeChat-POI-Groupbuy-SaaS  -> http://127.0.0.1:8001
# Usage: double-click, or powershell -ExecutionPolicy Bypass -File start-services.ps1
# =============================================================================
$ErrorActionPreference = 'Stop'

$ROOT      = Split-Path -Parent $PSScriptRoot
$PYTHON    = 'C:/Users/25803/.workbuddy/binaries/python/envs/default/Scripts/python.exe'
$LOG_DIR   = Join-Path $ROOT 'logs'
New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null

if (-not (Test-Path $PYTHON)) {
    Write-Host "[ERROR] Python venv not found: $PYTHON" -ForegroundColor Red
    Read-Host 'Press Enter to exit'
    exit 1
}

function Start-Service {
    param(
        [string]$Name,
        [string]$WorkDir,
        [string]$Module,
        [int]$Port,
        [string]$LogFile
    )
    $existing = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "[$Name] already running on :$Port (pid $($existing.OwningProcess -join ','))" -ForegroundColor Yellow
        return
    }
    Write-Host "[$Name] starting uvicorn $Module on :$Port ..." -ForegroundColor Cyan
    $proc = Start-Process -FilePath $PYTHON `
        -ArgumentList @('-m', 'uvicorn', $Module, '--host', '0.0.0.0', '--port', "$Port") `
        -WorkingDirectory $WorkDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput $LogFile `
        -RedirectStandardError "$LogFile.err" `
        -PassThru
    Start-Sleep -Seconds 4
    $check = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    if ($check) {
        Write-Host "[$Name] UP on :$Port (pid $($check.OwningProcess -join ','))" -ForegroundColor Green
    } else {
        Write-Host "[$Name] FAILED to listen on :$Port - see $LogFile" -ForegroundColor Red
    }
}

Write-Host "=== AI-local services bootstrap ===" -ForegroundColor White
Write-Host "Python: $PYTHON"

Start-Service -Name 'AI-Local-Growth-SaaS' `
    -WorkDir (Join-Path $ROOT 'AI-Local-Growth-SaaS\backend') `
    -Module 'main:app' `
    -Port 8000 `
    -LogFile (Join-Path $LOG_DIR 'ai-local-8000.log')

Start-Service -Name 'WeChat-POI-Groupbuy-SaaS' `
    -WorkDir (Join-Path $ROOT 'WeChat-POI-Groupbuy-SaaS\backend') `
    -Module 'app.main:app' `
    -Port 8001 `
    -LogFile (Join-Path $LOG_DIR 'wechat-poi-8001.log')

Write-Host ''
Write-Host '=== Health check ===' -ForegroundColor White
Start-Sleep -Seconds 2
foreach ($url in @('http://127.0.0.1:8000/api/health', 'http://127.0.0.1:8001/api/health')) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        Write-Host "GET $url -> $($r.StatusCode) $($r.Content)" -ForegroundColor Green
    } catch {
        Write-Host "GET $url -> FAILED $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ''
Write-Host 'Done. 管理后台: http://127.0.0.1:8000  (AI-Local) | http://127.0.0.1:8001  (WeChat-POI)'
Write-Host '服务为独立进程，关闭本窗口不影响运行。停止服务请运行 stop-services.ps1'