# =============================================================================
# AI-local 工作区一键停止脚本
# 用途：停止两个 SaaS 后端服务（按端口定位进程）
# 用法：双击本脚本，或 powershell -ExecutionPolicy Bypass -File stop-services.ps1
# =============================================================================
$ErrorActionPreference = 'Continue'

function Stop-PortService {
    param([int]$Port, [string]$Name)
    $conns = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    if (-not $conns) {
        Write-Host "[$Name] not running on :$Port" -ForegroundColor Yellow
        return
    }
    $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid_ in $pids) {
        Write-Host "[$Name] stopping pid $pid_ on :$Port" -ForegroundColor Cyan
        Stop-Process -Id $pid_ -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
    $check = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    if ($check) {
        Write-Host "[$Name] STILL RUNNING on :$Port" -ForegroundColor Red
    } else {
        Write-Host "[$Name] stopped" -ForegroundColor Green
    }
}

Write-Host '=== AI-local services shutdown ===' -ForegroundColor White
Stop-PortService -Port 8000 -Name 'AI-Local-Growth-SaaS'
Stop-PortService -Port 8001 -Name 'WeChat-POI-Groupbuy-SaaS'
Write-Host 'Done.'
