$ErrorActionPreference = "Stop"

if (Test-Path ".git") {
    Write-Error "A .git directory already exists. No repository was changed."
    exit 1
}

git init
git branch -M main
git add .
git commit -m "Initial standalone release: OpsReady Linux Lab 1.0.0"

Write-Host ""
Write-Host "Local repository created."
Write-Host "Create an empty remote repository named opsready-linux-lab, then run:"
Write-Host "git remote add origin <REMOTE_URL>"
Write-Host "git push -u origin main"
