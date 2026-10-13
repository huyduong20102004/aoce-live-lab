# GitHub hosted CI — actual execution 2026-10-13

**Cập nhật kiểm chứng 13/10/2026:** đã có scheduled event GitHub thật, cancellation/watchdog 7/7 và chẩn đoán Windows; GitHub là lịch chính, task local đã tắt. [Báo cáo mới nhất](../recovery/README.md). Các trạng thái pending và SHA cũ bên dưới là snapshot lịch sử.

Repo Public: https://github.com/huyduong20102004/aoce-live-lab. [Published full submission](https://github.com/huyduong20102004/aoce-live-lab/tree/main/submission). Source and all17 deliverables/curated model/local evidence are on main. Credentials/auth/grants/raw traces/CLI streams remain outside Git.

| Actual execution | Event / revision | Actual result | Run URL |
| --- | --- | --- | --- |
| PR #1 | pull_request head20dd38b; tested merge ref534c048 | typecheck PASSED; controller15/15; discovery exactly3; live job skipped by policy | https://github.com/huyduong20102004/aoce-live-lab/actions/runs/38337908837 |
| Initial hosted smoke | workflow_dispatch maince8d017 | selected3/executed3/pass3; exact owned cleanup resolved; evidence COMPLETE | https://github.com/huyduong20102004/aoce-live-lab/actions/runs/38338108312 |
| Final hosted smoke | workflow_dispatch main3878132e26c9e883ccdf0d756118fff81b29ff06 | selected3/executed3/pass3; exact owned cleanup resolved; screenshots hashes verified; evidence COMPLETE | https://github.com/huyduong20102004/aoce-live-lab/actions/runs/38338801288 |

[PR #1](https://github.com/huyduong20102004/aoce-live-lab/pull/1) was merged after actual successful checks. Final main contains the reviewed evidence documentation; a fresh manual run of the final SHA was completed rather than reusing the previous SHA as proof. Root app repo is clean and synchronized with origin/main.

Permanent curated initial hosted artifacts are tracked under [submission/hosted-ci](https://github.com/huyduong20102004/aoce-live-lab/tree/main/submission/hosted-ci). Final artifacts are linked from the final Actions run and copied locally under [final-evidence](final-evidence/gh-38338801288-1/manifest.json); retention7days applies to hosted artifact downloads. The public repo includes source packets/sanitized historical assertions, not raw auth state or production data.

## Schedule now enabled, future proof pending

Repository variables verified: AOCE_SCHEDULE_ENABLED=true, AOCE_MANUAL_VALIDATED_REVISION=3878132e26c9e883ccdf0d756118fff81b29ff06. Cron `17 18 * * *` UTC targets01:17 Vietnam the next calendar day; next expected slot after this Oct13 setup is **2026-10-14 01:17 UTC+7**. This slot has not been marked passed. Need an actual Actions run with event=schedule; manual workflow_dispatch is not scheduled proof. GitHub may delay/miss a slot, so monitor actual timestamps/run state.

Source changes invalidate schedule execution until a fresh successful manual smoke SHA is recorded. Windows Task Scheduler also received a fresh local manual validation of this same final source SHA; it is a separate runner and not GitHub proof. Each GitHub live run starts its own ephemeral app/credentials/data on Linux loopback, never accesses the Windows webapp or external HR environment.

No API/model is invoked by CI. Monetary cost UNKNOWN; installed Node/Playwright and source fixed in lockfile, baseline retries0/workers1, job timeout20min, shared live concurrency, no pass-with-no-tests or suppressed cleanup failures. Missing setup/credentials/selectors/reporter/cleanup stay failed/unknown.

Actual artifacts/REST metadata: [PR jobs](pr-jobs.json), [initial live jobs](manual-jobs.json), [final live jobs](final-jobs.json), [final verification](final-verification.json), [schedule variables](variables-after.json), [publication scan](publication-audit.json). Git Credential Manager was used locally; credentials were neither printed nor stored in these records.

Remaining checks: actual GitHub daily event, force-cancel/watchdog drill, and diagnosis of delays/missing Windows daily slots. All synthetic packets remain unchanged; no future scheduled execution/production reliability/financial invoice is claimed from a green manual smoke.
