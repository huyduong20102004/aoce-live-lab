param([switch]$VerifySoon)
$ErrorActionPreference = 'Stop'
$aoceLabRoot = Split-Path -Parent $PSScriptRoot
$aoceEvidence = Join-Path (Split-Path -Parent $aoceLabRoot) 'bai-nop-AOCE/live'
$aoceTaskName = 'AOCE-PortalLite-Live-Smoke'
$aoceProofPath = Join-Path $aoceLabRoot '.lab/manual-validation.json'
if (-not (Test-Path -LiteralPath $aoceProofPath)) { throw 'Successful manual smoke proof required before scheduling.' }
$aoceProof = Get-Content -LiteralPath $aoceProofPath -Raw | ConvertFrom-Json
$aoceRevision = & git -C $aoceLabRoot rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $aoceProof.code_revision -ne $aoceRevision) { throw 'Manual smoke proof must match current source revision.' }
if ((Get-TimeZone).BaseUtcOffset.TotalHours -ne 7) { throw 'This definition requires UTC+7 Windows timezone for 01:17 Vietnam.' }
$aoceEntry = Join-Path $PSScriptRoot 'scheduled-entry.ps1'
$aoceAction = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $aoceEntry + '"') -WorkingDirectory $aoceLabRoot
$aoceTrigger = if ($VerifySoon) { New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) } else { New-ScheduledTaskTrigger -Daily -At '01:17' }
$aoceIdentity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$aocePrincipal = New-ScheduledTaskPrincipal -UserId $aoceIdentity -LogonType Interactive -RunLevel Limited
$aoceSettings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 20) -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$aoceExisting = Get-ScheduledTask -TaskName $aoceTaskName -ErrorAction SilentlyContinue
if ($aoceExisting -and $aoceExisting.Description -ne 'AOCE isolated PortalLite smoke owned by this local lab') { throw 'Task name belongs to another definition; refusing replacement.' }
Register-ScheduledTask -TaskName $aoceTaskName -Action $aoceAction -Trigger $aoceTrigger -Principal $aocePrincipal -Settings $aoceSettings -Description 'AOCE isolated PortalLite smoke owned by this local lab' -Force | Out-Null
New-Item -ItemType Directory -Path $aoceEvidence -Force | Out-Null
Export-ScheduledTask -TaskName $aoceTaskName | Set-Content -LiteralPath (Join-Path $aoceEvidence 'windows-schedule.xml') -Encoding UTF8
Get-ScheduledTaskInfo -TaskName $aoceTaskName | Select-Object LastRunTime,LastTaskResult,NextRunTime,NumberOfMissedRuns | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $aoceEvidence 'windows-schedule-status.json') -Encoding UTF8
Write-Output "Registered $aoceTaskName. Mode=$($VerifySoon.IsPresent); daily target when normal: 01:17 UTC+7. Interactive logon required."
