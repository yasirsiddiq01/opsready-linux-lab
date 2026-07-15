$ErrorActionPreference = "Stop"

$obsolete = @(
    "opsready_lab/services/assessment_agent.py",
    "tests/test_assessment_agent.py",
    "docs/ASSESSMENT_AGENT_SETUP.md"
)

foreach ($path in $obsolete) {
    if (Test-Path $path) {
        Remove-Item $path -Force
        Write-Host "Removed $path"
    }
}

Write-Host "Legacy assessment-generator files removed."
