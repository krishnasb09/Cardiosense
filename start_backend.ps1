$env:PYTHONPATH = $PSScriptRoot
Write-Host "Setting PYTHONPATH to project root: $PSScriptRoot"
& "$PSScriptRoot\.venv\Scripts\python.exe" "$PSScriptRoot\web\backend\app.py"
