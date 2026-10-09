$ErrorActionPreference = 'Stop'
$aoceLabRoot = Split-Path -Parent $PSScriptRoot
$env:AOCE_SCHEDULER_TASK = 'AOCE-PortalLite-Live-Smoke'
Set-Location -LiteralPath $aoceLabRoot
$aoceNode = (Get-Command node).Source
$aoceProof = Get-Content -LiteralPath (Join-Path $aoceLabRoot '.lab/manual-validation.json') -Raw | ConvertFrom-Json
$aoceRevision = & git rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $aoceProof.code_revision -ne $aoceRevision) { throw 'Scheduled execution blocked: manual proof does not match source revision.' }
$aoceEvent = [ordered]@{ task_name = $env:AOCE_SCHEDULER_TASK; invoked_at = [DateTimeOffset]::Now.ToString('o'); code_revision = $aoceRevision }
$aoceEvent | ConvertTo-Json -Compress | Add-Content -LiteralPath (Join-Path $aoceLabRoot '.lab/scheduler-invocations.jsonl') -Encoding UTF8
& $aoceNode 'scripts/live-run.mjs' '--suite=smoke' '--trigger=windows-schedule'
exit $LASTEXITCODE
