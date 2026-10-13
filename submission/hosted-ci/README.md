# GitHub Actions — actual hosted CI evidence

Ngày2026-10-13 UTC+7. Repo https://github.com/huyduong20102004/aoce-live-lab, default branch main. This is hosted GitHub Actions execution, separate from the Windows scheduler and local/Codex benchmark cohorts.

| Lane | Actual event / source | Outcome | Evidence |
| --- | --- | --- | --- |
| PR #1 | pull_request; head20dd38b, tested synthetic merge534c048 | SUCCESS; typecheck, controller15/15, discovery3; live job intentionally skipped | [PR](https://github.com/huyduong20102004/aoce-live-lab/pull/1), [run38337908837](https://github.com/huyduong20102004/aoce-live-lab/actions/runs/38337908837), [checks](pr/checks.json) |
| Manual smoke | workflow_dispatch; maince8d0172ee59b4708855adbe3f64e04448c70e4a | SUCCESS; selected3/executed3/pass3, cleanup resolved, evidence COMPLETE | [run38338108312](https://github.com/huyduong20102004/aoce-live-lab/actions/runs/38338108312), [manifest](manual-initial/gh-38338108312-1/manifest.json) |

PR checks are static/fixture/discovery evidence, not an application runtime pass. The manual job starts PortalLite inside the Linux runner, generates private ephemeral HR Admin/Viewer accounts, runs Chromium with unchanged ID/department/Viewer oracles, reconciles exact owned IDs, and exports only sanitized metadata/cleanup/screenshots. No actual model/provider calls are made in this CI job.

The checked PR revision is GitHub's merge ref, so it differs from the PR head SHA; both are recorded instead of reusing an unrelated old revision. The manual artifacts have exact current-run/source linkage. These tracked artifacts are a permanent curated copy; original Actions artifacts have7-day retention and may require GitHub login to download.

Daily target `17 18 * * *` UTC = 01:17 Vietnam next day. A later evidence-documentation commit will receive a fresh manual run before repository variables enable scheduled execution for that exact SHA. Latest workflow runs are visible at [Actions](https://github.com/huyduong20102004/aoce-live-lab/actions/workflows/lab.yml). No future daily slot is recorded as passed; scheduled execution requires an actual run whose event is schedule.

Raw credentials/auth/grants/traces/runner output are excluded from source/artifacts; the publisher scanned local Git history and known secrets before push. Monetary CI/provider cost remains UNKNOWN; actual job durations do not constitute a billable invoice. Force-cancel/watchdog drill remains a separate unverified scenario, not hidden by a green smoke.
