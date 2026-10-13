# Bộ bài nộp AOCE — 7 lab, bản dry-run

**Bổ sung 2026-10-09:** đã tạo webapp và test project local, chạy browser flows/recovery/controller thật. Xem [bài nộp live-local và bằng chứng](live/README.md). Nội dung và bảng trạng thái bên dưới là snapshot dry-run ngày 2026-10-07; không trộn packet synthetic với actual local runs.

**Bổ sung AI 2026-10-09:** đã chạy Codex CLI thật cho U1/U2: 9 benchmark samples, 16 before/after fixture responses và2 supplemental positive controls, lưu raw usage/output. Xem [AI benchmark/evidence](live/ai/README.md). Chi phí tiền vẫn UNKNOWN; không trộn với RATE-SYN-01 hoặc gọi model fixture output là app runtime pass.

Ngày: 2026-10-07 (UTC+7). Version: aoce-solution-1. Mode: **DRY-RUN / SIMULATED**. Bộ bài nộp giải đủ yêu cầu artifact/analysis của 7 units trên packets; không sửa hai tài liệu gốc, không tạo git repo/PR thật, không deploy CI hoặc gọi app.

Workspace đầu vào chỉ có handout/course content, chưa có PortalLite, lab test project, accounts, endpoints, live budget hay CI repo. Theo handout, dry-run được dùng cho design/analysis; các mục live extension/runtime giữ **PENDING**. DESIGN-REVIEWED ở đây nghĩa AI tự review nguồn/artifact, chưa human QA approved. Không có RUN-PASSED hoặc production-ready claim.

**Minh bạch về manual-first:** Người dùng yêu cầu AI làm bài nên [draft đầu](review/00_analysis-first-draft.md) cũng do AI soạn. Không có bằng chứng người dùng đã làm manual trước AI, không peer interaction bịa. Draft được lưu trước bước AI đối chiếu/tính lại và [review log](review/01_review-decisions.md) ghi các sửa đổi thực tế. Yêu cầu học viên manual-first và independent human review cần trainer xác nhận riêng; không được đánh dấu hoàn thành chỉ vì đủ files. Rubric/pass mark chưa trainer xác nhận, không tự cấp điểm/pass.

## Bài nộp theo unit

| Unit | Files đúng handout | Nội dung đã giải / runtime còn thiếu |
| --- | --- | --- |
| U1 | [Benchmark](U1_benchmark.md), [Cost ledger](U1_cost-ledger.csv) | 9 samples, gate scores, costs/missing usage/config medians/pilot; live benchmark pending |
| U2 | [Context/prompt](U2_context-and-prompt.md), [Regression matrix](U2_regression-matrix.md) | 8 fragments, compact≤250 từ, v3/diff/manifest, 8 fixtures +3 negatives; live model regression pending |
| U3 | [Multi-flow design](U3_multi-flow-design.md), [Data/evidence](U3_data-and-evidence.md) | 3 contracts, routing/stops, layers, isolated seed/ownership/collision/manifests; actual flow runs pending |
| U4 | [Change review](U4_change-review.md), [PR draft](U4_PR.md) | 7 inventory paths, merge250 từ/semantic diff, commit plan/review/rollback, VC matrix; actual branch/final-revision checks pending |
| U5 | [CI design](U5_ci-design.md), [Workflow YAML](U5_workflow.yml), [Playwright config](U5_playwright-config.ts), [Run review](U5_run-review.md) | 8 scenarios/3 packets, cron/lanes/contracts/cleanup/ops; manual/scheduled runtime pending |
| U6 | [Incident triage](U6_incident-triage.md), [Recovery/validation](U6_recovery-and-validation.md) | 4 incidents/3 retry outcomes, scoped locator/state recovery +4 negatives; live reproduction/fix pending |
| U7 | [Metrics/claims](U7_metrics-and-claims.md), [Risk register](U7_risk-register.md), [Sprint memo](U7_sprint-review.md) | 10 rows/4 slots, denominators/unknowns, claim audit/10 risks/action owners/dates; actual telemetry pending |

Tất cả owner/due dates là **đề xuất**, không đã giao việc. Source packets synthetic; giá/usage/observations/refs không telemetry thật. Source IDs/version không có exact timestamp dùng Not specified thay vì điền giả. [Source manifest](evidence/source-manifest.json) ghi snapshot SHA-256 hai files gốc và references technical official đã đọc.

## Số liệu đáng chú ý

A accept3/3, total0.325175 và cost/accepted0.108391667; B accept0/3 nên loại dù rẻ; C accept2/3, total UNKNOWN, cost/accepted lower bound0.1270375. U7 selected10/executed8, first-pass50%, eventual75%, flaky25%, evidence completeness87.5%, cleanup4/6; subtotal **0.89**, full cost UNKNOWN, schedule3/4. Các tỷ lệ này chỉ diễn giải fixture.

## Kiểm chứng tại máy

[Validation report](evidence/validation-report.md) ghi actual local arithmetic/source consistency/word budget/links/YAML checks và typecheck config draft. Chúng không thay runtime app/CI evidence. [JSON calculations](evidence/calculations.json), [U7 CSV](evidence/U7_execution-ledger.csv) và command outputs hỗ trợ review.

Chạy lại từ thư mục gốc:

```powershell
python .\bai-nop-AOCE\tools\calculate.py
python .\bai-nop-AOCE\tools\validate.py
```

Validator cần Python 3.12 và PyYAML (đã có ở môi trường hiện tại). `calculate.py` chỉ cần standard library. Chỉ ghi lại CSV/JSON/report trong bài nộp, không app/network access. Typecheck draft dùng tool dependencies tạm riêng; versions/output được lưu trong evidence, không thêm npm project vào workspace tài liệu.

Trước live: trainer cấp môi trường/project/accounts/helper permissions, approve namespace/budget/artifact policy; human review các gates; implement scripts/fixtures/tests từ contracts; actual final-revision PR checks và manual smoke phải có đầy đủ evidence trước schedule. Những việc này chưa thể thực hiện với input hiện có.
