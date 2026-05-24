# AXI Platform - Dev local
# Uso: .\dev.ps1

Write-Host ""
Write-Host "  AXI Platform - Iniciando ambiente de desenvolvimento..." -ForegroundColor Cyan
Write-Host ""

# Backend
$backendJob = Start-Job -Name "axi-backend" -ScriptBlock {
    Set-Location "$using:PWD\backend"
    $env:DATABASE_URL = 'sqlite:///../tests/backend/test_axi.db'
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
}

# Aguarda startup do backend
Write-Host "  [1/2] Aguardando backend iniciar..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    try {
        $resp = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health -TimeoutSec 2 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { $ready = $true; break }
    } catch { }
}

if ($ready) {
    Write-Host "  [1/2] Backend OK -> http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host "         Docs      -> http://127.0.0.1:8000/docs" -ForegroundColor DarkGray
} else {
    Write-Host "  [1/2] Backend demorou - verificar logs com: Receive-Job -Name axi-backend" -ForegroundColor Red
}

# Frontend
Write-Host "  [2/2] Iniciando frontend..." -ForegroundColor Yellow
Set-Location "$PWD\frontend"
$env:VITE_API_URL = "http://127.0.0.1:8000/api"
npm run dev -- --host 127.0.0.1 --port 5173
