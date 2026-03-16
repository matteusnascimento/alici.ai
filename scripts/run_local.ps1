Set-Location "$PSScriptRoot/../apps/api"
Start-Process powershell -ArgumentList '-NoExit','-Command','uvicorn app.main:app --reload --port 8000'
Set-Location "$PSScriptRoot/../apps/web"
npm run dev
