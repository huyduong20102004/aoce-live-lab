# U5 — CI lanes, scripts, scheduling và failure semantics

Mode: DRY-RUN / DESIGN-REVIEWED bởi AI; runtime pending. Sources: CI-PACKET-05, CI-51–58, Unit 5 scaffold/config trong course content, POLICY/LAB-AOCE-05; snapshot trong [manifest](../../evidence/source-manifest.json). Draft: [draft-1](../../review/00_analysis-first-draft.md). Prerequisites chưa được cấp; workflow/config ở thư mục bài nộp, không deploy.

## Lanes và prerequisite checklist

| Lane | Trigger / checks | Permissions / outcome |
| --- | --- | --- |
| PR | typecheck, synthetic context regression, nonempty test discovery | contents:read, không lab secrets/environment; static verified không là live pass |
| Manual live | Trusted reviewed default-branch revision, preflight, 3 smoke flows, reporter, cleanup/evidence check | isolated-lab approved credentials; explicit AOCE_MANUAL_ENABLED; assert và operational outcomes riêng |
| Scheduled live | Default branch, manual proof cùng SHA, AOCE_SCHEDULE_ENABLED | Same scoped lab/tool policy; chỉ actual schedule trigger run chứng minh đã fire |

Checklist trước live: repo/app được cấp phép; default branch verify (packet giả định main); Node 22 + lockfile/runtime compatible; Playwright chromium/tags/source-bound assertions; reviewed config; login fixture HR Admin/Viewer riêng; namespace length/charset approved; URL exact origin/path allowlist; role readiness/build; external environment lease và durable owned ledger/reconciler; scripts contracts implemented; secret store; restricted artifacts/access/7-day retention được chủ lab chấp thuận; manual live evidence complete và cleanup success; budget owner; schedule monitoring owner. Chưa item nào được giả định live đã hoàn tất.

Budget: total design 20 phút/run, baseline retries=0, workers=1, tool read recovery ≤1; controlled runner retry ≤1 chỉ sau safe setup/cleanup proven. Playwright globalTimeout 12 phút giới hạn phần test; wrapper còn phải lấy remaining deadline gồm install/setup và reserve reconcile/export. Timeout cấu hình là lab parameter, không search SLA.

## Workflow/config draft và scheduling

[Workflow draft](U5_workflow.yml), [Playwright config draft](U5_playwright-config.ts). Config giữ `forbidOnly`, workers=1, retries=0 và reporter JSON/HTML theo scaffold; thêm per-test/expect/global timeout là design parameters để dành thời gian cleanup, không sửa packet gốc.

Cron `17 18 * * *` mặc định UTC: 18:17 UTC ngày D = 01:17 Việt Nam UTC+7 ngày D+1, không DST. Theo [GitHub schedule docs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), workflow schedule cần default branch và có thể trễ; expected slot không chứng minh actual dispatch. Workflow draft có trigger schedule nhưng nằm ngoài `.github/workflows`; khi tích hợp, chưa bật schedule lane đến khi manual proof và environment được xác nhận. Repo variables AOCE_MANUAL_ENABLED/AOCE_SCHEDULE_ENABLED mặc định absent nên live job không dispatch. Schedule cần AOCE_MANUAL_VALIDATED_REVISION khớp SHA; revision mới làm lane bị chặn đến revalidation. Skip gate cần monitor báo rõ BLOCKED, không coi job skipped là live pass.

Concurrency group `aoce-isolated-lab-live` chung environment, `cancel-in-progress:false`; PR không chiếm lab lock. Theo [GitHub concurrency docs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency), group ở phạm vi repository và default pending có thể bị thay thế. Thiết kế chưa bật tùy chọn queue khác; monitor pending cancellation, không hứa mọi dispatch được thực thi. Cross-repo cần environment lease riêng. Force cancellation/runner outage vẫn có thể bỏ mọi always steps; durable ledger + out-of-job reconciler là prerequisite, không dựa YAML để đảm bảo delete.

Actions checkout@v6/setup-node@v6/upload-artifact@v4 theo [Playwright official CI example](https://playwright.dev/docs/ci-intro), đối chiếu 2026-10-07. Trước live cần pin reviewed commit SHA theo policy project và kiểm runner compatibility; không tạo SHA action giả trong dry-run. Secret refs dùng store; theo [GitHub secrets docs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets), thiếu secret có thể thành chuỗi rỗng và fork PR không nhận secrets, nên PR lane không login.

## Scenario outcomes (đủ 8)

| Scenario | Preflight / failure semantics | Cleanup và artifact / owner đề xuất |
| --- | --- | --- |
| CI-51 fork PR | PR static/synthetic/discovery only; no live credentials; label PR-VERIFIED nếu checks đủ | No writes, cleanup N/A; static evidence; QA CI review missing checks |
| CI-52 missing LAB_PASSWORD | Preflight nonzero BLOCKED, no skip login/all passed | No mutation, NOT_STARTED ledger; finalized manifest diagnostics upload; lab account owner cấp secret |
| CI-53 smoke selected=0 | discover nonzero NO-TESTS; remove pass-with-no-tests; executed=0 | No writes, cleanup N/A; selector/discovery report; QA tests sửa tags/config |
| CI-54 F01 assertion fail | Runner nonzero; assertion outcome FAILED | Reconcile owned records; export reporter/approved trace even fail via always; QA triage |
| CI-55 force cancel after write | CANCELLED/UNKNOWN write, no assertion proof; no guarantee in-job cleanup | External reconciler reads durable exact ledger/lease; unresolved until verified; QA data + lab operator |
| CI-56 branches share lab | Environment group serial, trusted default-branch restriction; external lease | Distinct run/attempt IDs; rejected lease logged; lab operator |
| CI-57 missing schedule, feature-only file | Verify actual default branch/workflow state/gates; feature-only cannot prove scheduled readiness; cause not assumed | Keep missing slot UNKNOWN; schedule monitor ticket; CI maintainer |
| CI-58 cleanup unresolved despite tests pass | Keep assertion pass AND cleanup unresolved; helper nonzero; no suppress error | Job operationally fail, durable ledger and artifacts retained; QA data owns reconcile |

## Script contracts — prerequisites, chưa implementation live

Các scripts bổ sung ngoài hai script packet đều được ghi là đề xuất cần hiện thực, không đã tồn tại. Scripts đọc credential trong runtime được cấp, không log/AI input. Controller/runner tools vẫn chỉ theo tool cards; shell trong CI là trusted reviewed implementation, không mở shell cho planner.

| Script | Inputs / validations | Outputs | Exit codes / unknown |
| --- | --- | --- | --- |
| lab:preflight (packet) | Required HR+Viewer secrets, URL/allowlist/environment exact, roles/build/readiness, remaining time, approved namespace, durable ledger và lease; no writes | Sanitized readiness/build/actor refs, lease proof; no credentials | 0 ready; 2 missing values; 3 disallowed URL/env; 4 readiness/role/lease block; 5 UNKNOWN helper state; nonzero stops runner |
| lab:reconcile (packet) | Exact run ledger/token/env, approved lookup/cleanup helper; unknown write first read; ownership required | Per-record reconciled/absent/cleanup success/failed/unknown; unresolved count | 0 verified resolved or no-write proven; 6 unresolved; 7 helper/ownership error; missing ledger without no-write proof=UNKNOWN nonzero |
| typecheck / context:regression (proposed) | Locked project, synthetic fixtures only in PR; invariants/negative controls | Static/fixture outputs under evidence-export/pr | 0 checks pass; 1 fail; no label live-pass |
| lab:discover (proposed) | Same config/project=chromium/grep=@smoke; list without login or module-level writes; expected F01/F02/F03 | Structured selected case IDs/flow map/count and command/revision | 0 nonempty expected set; 8 no tests; 9 expected flow missing/selector mismatch; errors nonzero |
| lab:execute (proposed) | Prior preflight/lease/discovery proven; remaining deadline; reserve cleanup/export time | Spawns reviewed `npx playwright test --project=chromium --grep=@smoke`, no pass-with-no-tests; reporter and attempts; all writes journaled before dispatch | Preserve runner nonzero; deadline fail code 10; never wrapper rerun/ignore failure; no reporter→UNKNOWN |
| lab-manifest-init.mjs (proposed, no npm deps) | GitHub run/attempt/SHA/trigger/env, UTC timestamp; no secrets read/print | Bootstrap manifest + deadline + durable ledger intent; schema aoce-ci-run-1 | 0 initialized; 11 missing/invalid identity/durable bootstrap; runner blocked |
| lab-manifest-finalize.mjs (proposed, no npm deps) | Bootstrap, step outcomes, structured reporter/ledger, current time | Final manifest, NOT_STARTED/BLOCKED/UNKNOWN when no execution; cleanup not fabricated | 0 finalized even failure outcomes; 12 corrupt/missing manifest; no pass conversion |
| lab-evidence-check.mjs (proposed, no npm deps) | Manifest+discovery+reporter+owned ledger; exact linkage/selected counts/artifact existence | Completeness results/missing refs; separate assertion/operational summary | 0 complete successful selected execution + resolved cleanup; 13 incomplete/no-tests/no-reporter; 14 unresolved cleanup; assertion failures remain nonzero upstream |
| lab-export-evidence.mjs (proposed, no npm deps) | Sanitized manifest/reporter/ledger and explicit approved trace policy | evidence-export/live with diagnostics on setup failure; no .env/auth/cookies/headers; restrictive access | 0 safe export; 15 unsafe payload or export error; block unsafe upload, private originals only if authorized |

No-write record absence không suy từ reporter thiếu. preflight không tạo seed; seeds chỉ sau durable ledger ready trong runner fixtures. Khi preflight không success, finalize ghi NOT_STARTED/no-write intent có nguồn; reconcile không gọi helper thiếu quyền/credentials. Nếu lease/bootstrap state không chứng minh no-write, external owner triage UNKNOWN.

## Manifest schema và evidence completeness

```text
schema_version=aoce-ci-run-1; mode=LIVE|DRY-RUN; label
run_id, github_run_attempt, logical_case_id, runner_attempt_id, flow_id, actor
code_revision, prompt_version, context_version, model_config_ref, build, environment_alias
trigger, expected_slot(UTC và UTC+7 hoặc null cho manual), dispatch/start/finish timestamps
command, selector, selected_case_ids, selected_count, executed_count, per-case outcomes/attempts
assertion_refs, artifact_refs, artifact_access_policy, durable_ledger_ref, ownership_refs
write_state, cleanup_status/ref, unresolved_count, usage_status, cost_subtotal/unknowns
budget_deadline, retry_reason, triage_owner, gaps, checks
```

Checker so sánh đúng run/attempt/case/flow/SHA/config/build; selected=3 đúng expected flow set không phải tự fixed reporter counts; mỗi executed case assertion/ref đúng ID/department hoặc Viewer disabled/not-found; blocked/skipped cũng explicit; artifacts tồn tại/access authorized; cleanup tất cả needed cases; usages missing giữ null/status và subtotal; trigger schedule chỉ từ event source. Upload thành công không bằng complete evidence; fail checker không xóa assertion pass đã có.

Ops design: schedule monitor riêng tính slot→observed dispatch, default-branch/gate status, delay/queue; owner CI maintainer khi missing >15 phút (alert threshold đề xuất, không product SLA). Watchdog reconciliation sau expired lease (TTL đề xuất ≥20 phút + margin trainer approve), chạy read-first dưới approved permission và record exact owner; owner QA data giải unresolved, không silent delete. Artifact missing→QA CI lấy reporter/runner diagnostics với access hợp lệ; không screenshot toast thay reporter. Owner/date chỉ đề xuất, không đã assign.

## Review log / validation

| Finding/proposal | Source | Quyết định đề xuất |
| --- | --- | --- |
| always cleanup đủ xử lý force cancel | CI-55 | REJECT; cần external reconciler/durable ledger |
| Group theo branch an toàn | CI-56 | REJECT; common environment group + external lease |
| Script discover/count và linkage checker còn thiếu ở scaffold | CI-53 / RUN-B | ACCEPT thêm contract rõ, không invent đã tồn tại |
| Upload mọi test-results bao gồm auth | GitHub/Playwright artifact sensitivity | REJECT; explicit export boundary + private store review |
| Retries=1 luôn cho smoke | LAB-AOCE-05 / INC-62 | REJECT; baseline 0, safe conditional exception mới được review |

Local validation: parse YAML, policy conditions, TS syntax bằng compiler nếu available; không project typecheck/runtime/CI deployment. [Validation report](../../evidence/validation-report.md), [run packet reviews](U5_run-review.md). Human review, live prerequisites và scheduled runtime objectives pending.
