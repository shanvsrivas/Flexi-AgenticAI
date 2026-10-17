$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$studyPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $studyPython)) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0 -and -not (Test-Path -LiteralPath $studyPython)) { exit $LASTEXITCODE }
}
python -m pip --python $studyPython install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'Ready. Run .\run.ps1 to start StudyBuddy.'
