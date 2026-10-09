$ErrorActionPreference = 'Stop'
$aoceLabRoot = Split-Path -Parent $PSScriptRoot
$env:AOCE_SCHEDULER_TASK = 'AOCE-PortalLite-Live-Smoke'
Set-Location -LiteralPath $aoceLabRoot
$aoceNode = (Get-Command node).Source
& $aoceNode 'scripts/live-run.mjs' '--suite=smoke' '--trigger=windows-schedule'
exit $LASTEXITCODE
