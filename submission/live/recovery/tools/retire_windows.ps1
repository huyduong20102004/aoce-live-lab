$ErrorActionPreference = 'Stop'
$aoceEvidenceRoot = Split-Path -Parent $PSScriptRoot
$aoceState = Get-Content -LiteralPath (Join-Path $aoceEvidenceRoot 'scheduler-final-state.json') -Raw | ConvertFrom-Json
$aoceRun = Get-Content -LiteralPath (Join-Path $aoceEvidenceRoot 'scheduled-run.json') -Raw | ConvertFrom-Json
if ($aoceRun.event -ne 'schedule' -or $aoceRun.conclusion -ne 'success' -or $aoceState.daily_workflow_state -ne 'active' -or $aoceState.daily_variable -ne 'true') {
    throw 'Successful real GitHub schedule and active daily workflow required before retiring Windows.'
}
$aoceTaskName = 'AOCE-PortalLite-Live-Smoke'
$aoceTask = Get-ScheduledTask -TaskName $aoceTaskName
if ($aoceTask.Description -ne 'AOCE isolated PortalLite smoke owned by this local lab') {
    throw 'Task ownership mismatch; refusing change.'
}
if ($aoceTask.State -eq 'Running') { throw 'Own task currently running; leave it intact until it finishes.' }
Disable-ScheduledTask -InputObject $aoceTask | Out-Null
$aoceFinal = Get-ScheduledTask -TaskName $aoceTaskName
if ($aoceFinal.State -ne 'Disabled') { throw 'Own Windows task did not become Disabled.' }
[ordered]@{
    captured_at = (Get-Date).ToString('o')
    task = $aoceTaskName
    state = $aoceFinal.State.ToString()
    description = $aoceFinal.Description
    action = 'Disabled only this lab task; definition retained for reversible re-enable'
    primary_scheduler = 'GitHub Actions'
    verified_scheduled_run = $aoceRun.html_url
    daily_target_vietnam = '01:17 UTC+7'
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $aoceEvidenceRoot 'windows-retired.json') -Encoding UTF8
Write-Output 'Own lab Windows task disabled; GitHub Actions is primary.'
