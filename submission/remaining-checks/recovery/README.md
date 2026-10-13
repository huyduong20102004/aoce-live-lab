# Remaining runtime checks ? actual evidence 13/10/2026

Tested main revision: c27f9b8eff44a4875f2922831890dc8d8abf1851. This branch publishes evidence without changing the manually validated runtime main.

- Force-cancel: actual SIGKILL after exactly one owned write; independent watchdog recovery verified7/7. Victim remains CANCELLED, assertions NOT_EXECUTED. [Drill](../runs/cancel-mv63z50h-ec1f9a/cancellation-drill.json), [cleanup](../runs/cancel-mv63z50h-ec1f9a/cleanup.json). This proves local worker cancellation with persistent app state, not destruction of a whole GitHub VM.
- Windows diagnosis: System sleep intervals cover01:17 slots10?13October. WakeToRun=false, StartWhenAvailable=true, Interactive logon. [Actual config/events](windows-diagnosis.json), [slot analysis](windows-slot-analysis.json). Historical TaskScheduler Operational log was disabled; no12October run is invented. Own local task retirement is pending successful hosted schedule proof; GitHub is the chosen primary scheduler.
- GitHub: fresh [manual hosted run](https://github.com/huyduong20102004/aoce-live-lab/actions/runs/38340873990) on testedSHA passed3/3, cleanup resolved. Actual event=schedule is still PENDING, observed through the real temporary5-minute timer. Daily01:17 schedule remains enabled. Manual execution is not schedule evidence.

[Exported-evidence validator](tools/validate_remaining.py):15checks passed, zero failed; three closing gates still pending. [Result](validation-results.json). Full browser suite on sameSHA passed11/11 with cleanup33 resolved: [manifest](../runs/mv642583-879ae7b4/manifest.json). [Initial failed pre-write cancellation attempt](cancellation-initial-attempt.json) is retained separately.
