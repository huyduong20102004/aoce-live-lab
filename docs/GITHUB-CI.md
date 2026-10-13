# GitHub Actions — self-contained isolated lab

The repository is https://github.com/huyduong20102004/aoce-live-lab. The local app is started inside the GitHub-hosted runner on loopback; it does not connect to the Windows lab or to production.

PR lane: locked install, actual TypeScript check, 15 controller/fixture regressions, exactly three nonempty smoke discoveries; no live login or external account secret. Logs, revision, run URL and discovery are exported under evidence-export/pr. A green PR check is static/fixture evidence, not a live browser pass.

Manual lane on default branch: ephemeral random HR Admin/Viewer accounts generated in ignored .env, Chromium installation, static checks, owned-run preflight, three browser flows, exact owned reconciliation and evidence checks. Raw trace/reporter/auth/state stay in ignored .lab. Only redacted manifests, role/source/assertion metadata, cleanup and screenshots after login are uploaded from evidence-export/live. No credentials or API provider calls are published.

Schedule target: `17 18 * * *` UTC = 01:17 Vietnam UTC+7 the following calendar day. It runs only when repository variables AOCE_SCHEDULE_ENABLED=true and AOCE_MANUAL_VALIDATED_REVISION match the current default-branch SHA. Enable only after actual manual validation of that SHA. A manual event cannot be labeled a scheduled event; actual schedule requires an Actions run with event=schedule.

Source changes require a new manual validation SHA. GitHub may delay/miss schedules; do not report exact-minute availability. Job timeout20min, runner retries0, workers1, common live concurrency group, cancel-in-progress=false. This lab state is local to an ephemeral runner, so a force-cancel destroys that runner's data; external persistent environments would still require an out-of-job reconciler. The separate Windows scheduler remains a local lab mechanism and is not proof of GitHub scheduled execution.

Reference: [GitHub schedule/manual events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), [Playwright CI](https://playwright.dev/docs/ci-intro). Hosted run evidence and submission index are added under submission/ after review; no future schedule slot is marked passed without a real run.
