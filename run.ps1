$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$studyPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $studyPython)) {
    Write-Host 'Run setup.ps1 first to install the project dependencies.'
    exit 1
}
& $studyPython -m streamlit run frontend/app.py --server.headless true
