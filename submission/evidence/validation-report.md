# Actual local validation — bài nộp dry-run

Ngày 2026-10-07 (UTC+7). Các checks chạy thật trên file tại máy; packets app/CI/model vẫn SIMULATED. Không có RUN-PASSED app/CI.

`python bai-nop-AOCE/tools/calculate.py` tính lại CSV/JSON bằng Decimal; `python bai-nop-AOCE/tools/validate.py` đối chiếu bảng trong handout gốc, hashes, word budget, links và YAML.

Kết quả: 40/40 checks OK, 0 errors.

| Check | Actual result | Evidence / limitation |
| --- | --- | --- |
| 17 required deliverables | OK | U1_benchmark.md, U1_cost-ledger.csv, U2_context-and-prompt.md, U2_regression-matrix.md, U3_multi-flow-design.md, U3_data-and-evidence.md, U4_change-review.md, U4_PR.md, U5_ci-design.md, U5_workflow.yml, U5_playwright-config.ts, U5_run-review.md, U6_incident-triage.md, U6_recovery-and-validation.md, U7_metrics-and-claims.md, U7_risk-register.md, U7_sprint-review.md |
| Original source unchanged: L3_AIQE_AOCE_exercises_vi.md | OK | b6f6023b3a19ccdab9c7a344c9c4e4d1822331df74b19ae4e8ffba1aa9ed02f5 |
| Original source unchanged: L3_AIQE_AOCE_course_content_vi.md | OK | fe0e922ca4adc832b1cc2f15f55d33a23f53d98bb5fe8e6876b854cf89dac497 |
| U1 nine sample IDs | OK | A1–C3 present; no dropped rejected samples |
| U1 source-derived cost A1 | OK | Uncached partition/model/CI/total checked against original BENCH table |
| U1 source-derived cost A2 | OK | Uncached partition/model/CI/total checked against original BENCH table |
| U1 source-derived cost A3 | OK | Uncached partition/model/CI/total checked against original BENCH table |
| U1 source-derived cost B1 | OK | Uncached partition/model/CI/total checked against original BENCH table |
| U1 source-derived cost B2 | OK | Uncached partition/model/CI/total checked against original BENCH table |
| U1 source-derived cost B3 | OK | Uncached partition/model/CI/total checked against original BENCH table |
| U1 source-derived cost C1 | OK | Uncached partition/model/CI/total checked against original BENCH table |
| U1 source-derived cost C2 | OK | Uncached partition/model/CI/total checked against original BENCH table |
| U1 source-derived cost C3 | OK | Uncached partition/model/CI/total checked against original BENCH table |
| U1 rubric scores/ledger consistency | OK | A=10, B=1, C1/2=10, C3=5; hard gates separate |
| U1 all-sample config cost bounds | OK | C accepted=2; rejected C3 contributes known CI; total remains UNKNOWN |
| U1 config median A | OK | Latency/QA calculated independently from source rows |
| U1 config median B | OK | Latency/QA calculated independently from source rows |
| U1 config median C | OK | Latency/QA calculated independently from source rows |
| U2 compact word budget | OK | 182 whitespace-delimited words; limit250, not tokens |
| U2 eight fragment IDs | OK | Keep/drop/quarantine source manifest |
| U2 eight fixtures and >=2 negatives | OK | Walkthrough only; no model/runner executed |
| U3 three flow contracts/stop scenarios | OK | Structural coverage only; UI/backend boundary reviewed semantically |
| U5 YAML syntax + minimum permissions | OK | PyYAML parse; no GitHub execution/actionlint claim |
| U5 cron UTC conversion | OK | 18:17 UTC -> 01:17 next Vietnam day |
| U5 environment concurrency/no forced cancellation | OK | Shared environment group; not cross-repo lock |
| U5 live authorization gates | OK | Actual variables/repo/manual proof absent; no deployment |
| U5 no suppressed failures or no-tests pass | OK | Wrapper script implementations still prerequisite |
| U5 failure artifact export | OK | Safe export paths; force cancel still requires external reconciler |
| U5 actual draft config typecheck and hash | OK | tsc 7.0.2, Playwright types 1.63.0, Node types 22.20.5; config unchanged since compile; not live project runtime |
| U5 eight scenarios/three packets | OK | Source cards addressed, not actual CI evidence |
| U6 incidents/retry outcomes/negative controls | OK | 4 incidents, 3 retry outcomes, >=2 proposed negative controls |
| U7 all 10 source rows preserved | OK | Outcome/attempts/evidence/cleanup/calls/usage/cost/time checked against original table |
| U7 denominators/outcome partitions | OK | selected10/executed8/attempts11/pass4+2/fail2/full7/cleanup4of6/fullpasses5 |
| U7 source-derived subtotal and lower-bound cost | OK | All cohort costs included; E08 missing model usage !=zero |
| U7 test-duration stats | OK | n8, excludes not-executed; not E2E latency |
| U7 schedule source-derived metrics | OK | Completeness3/4; SL-04 missing, no zero fill |
| U7 >=6 complete risk rows | OK | 10 proposed risk rows with source/control/detection/owner/action/closure/residual |
| All local Markdown links resolve | OK | All referenced files present |
| Draft/manual-first provenance disclosed | OK | AI-authored draft; no fabricated human/peer review |
| No deployed workflow or app/auth payload created | OK | Submission-only drafts; original workspace documents preserved |

Typecheck config draft: xem [compiler output](typecheck-output.txt) và [tool versions](typecheck-versions.json). Đây là kiểm tra config độc lập với các package types tạm, không project lab typecheck/test execution.

Không kiểm được: actual lab runner/assertions, CI trigger/action execution, script implementations, permissions/helper behavior, live cleanup, provider usage/pricing, production readiness. Human manual-first và independent QA approval chưa có.

YAML parse/structural checks không thay GitHub workflow/actionlint/runtime validation. Row/ID coverage checks không chứng minh behavior controller. Proposed negative controls là walkthrough, chưa model/app executed.

[Machine-readable results](validation-results.json); [source snapshot](source-manifest.json); [review decisions](../review/01_review-decisions.md).
