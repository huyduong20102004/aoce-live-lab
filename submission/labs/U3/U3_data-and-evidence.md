# U3 — Isolation, data ledger và evidence manifest

Mode: DRY-RUN / SIMULATED. Sources: FLOW-PACKET-03, OBS-31–34, LAB-AOCE-05, POLICY-PACKET-AOCE. Design version aoce-data-1. Không endpoint/DB permission được cấp; helper dưới đây là contract. Initial analysis/review: [draft](../../review/00_analysis-first-draft.md), [U3 design](U3_multi-flow-design.md).

## Namespace và concurrency

Logical ID: `E2E-AOCE-<run>-<attempt>-<flow>`, ví dụ r03/a1/F02 → E2E-AOCE-r03-a1-F02. run ID globally allocated trong lab, attempt tăng theo attempt; worker ID và reservation lease nằm trong ledger, không thay pattern. Một parameter/worker case cần run sub-ID riêng (ví dụ r03w2), chưa reuse cùng run/attempt/flow. Trainer xác nhận character/length và collision rules trước live; không âm thầm truncate/hash gây trùng.

Start với workers=1 và shared-environment lock. Nếu tăng concurrency: external environment lease + atomic exact-ID reservation hoặc cơ chế uniqueness trainer cấp; chạy F01/F02 với IDs/contexts khác nhau, F03 auth riêng. CI concurrency group chỉ giúp cùng repo, không bảo đảm lock nhiều repo. Không có atomic reservation được cấp → block parallel writes, giữ serial.

## Seed/cleanup ledger mẫu

Các refs chỉ synthetic pointers, không kết quả đã chạy. `planned` không phải success. Ledger durable lưu trước mutation, cập nhật write intent→dispatch→unknown/created→assertion→cleanup, kể cả worker crash.

| Run / attempt / flow | ID / seed | Owner/worker | Initial / write state | Cleanup design | Evidence hiện có / thiếu |
| --- | --- | --- | --- | --- | --- |
| r03/a1/F01 | E2E-AOCE-r03-a1-F01; mới ở QA | r03/a1/F01, w1 | reserved; write planned | cleanup exact ID khi ownership và created ref verified | Design only; reporter/lookup/ref còn thiếu |
| r03/a1/F02 | E2E-AOCE-r03-a1-F02; seed riêng QA | r03/a1/F02, w1 | OBS-31 seed owned synthetic; edit planned | delete seed owned theo reviewed cleanup contract; giữ before/after ledger | OBS-31/32 DOM fixtures, không live runner |
| r03/a1/F03 | E2E-AOCE-r03-a1-F03; absent probe | r03/a1/F03, viewer-context | OBS-33 not-found synthetic; no write permitted | N/A nếu absent; unexpected record→triage, không delete nếu chưa chứng minh owner | Disabled/lookup fixture; live role/reporter missing |

Ledger fields: run/attempt/flow/parameter/worker, employee ID, owner assertion, reservation token, lease expiry, seed source/ref/initial department, write intent and outcome, record ref, mutation history, assertion refs, cleanup status/ref, unresolved reason, proposed triage owner. Khi actual timestamps chưa có, dùng null; không bịa thời gian.

## Collision example

Workers w1 và w2 cùng yêu cầu E2E-AOCE-r03-a1-F02. w1 thắng atomic reservation; w2 thấy token đã thuộc w1 → BLOCKED collision trước seed/write, không lookup rồi cleanup ID của w1. Nếu phát hiện ID tồn tại nhưng ledger không chứng minh owner, cả setup lẫn cleanup dừng UNKNOWN; owner đề xuất QA data đối chiếu ledger. Retry w2 chỉ sau cấp run sub-ID mới và verified absent; lưu denied reservation và new-ID rationale. Không lấy uniqueness toast làm collision-proof.

## Per-flow run manifest mẫu

```json
{
  "schema_version": "aoce-run-1",
  "mode": "DRY-RUN",
  "label": "SIMULATED",
  "run_id": "r03",
  "attempt_id": "a1",
  "flow_id": "F02-change-department",
  "parameter_id": "QA-to-Engineering",
  "actor": "HR Admin",
  "code_revision": null,
  "prompt_version": "aoce-prompt-v3",
  "context_version": "aoce-context-v3",
  "environment_alias": "isolated-lab",
  "app_build": null,
  "employee_id": "E2E-AOCE-r03-a1-F02",
  "owner": "r03/a1/F02",
  "source_refs": ["LAB-AOCE-03", "LAB-AOCE-05", "OBS-31", "OBS-32"],
  "seed_ref": "OBS-31 synthetic seed",
  "runner_outcome": "NOT_EXECUTED",
  "assertion_refs": [],
  "artifact_refs": [],
  "cleanup_status": "PLANNED",
  "unknowns": ["live revision/build/reporter/cleanup helper"]
}
```

F01 template thay flow/sources=AC-EMP-01/02, seedRef=null, assert exact ID+QA. F03 thay actor=Viewer, source=LAB-AOCE-04, seed=absent, expected no write và cleanup=N/A; không reuse context/ref của F02. Mỗi selected case có entry kể cả BLOCKED/SKIPPED/NO-TESTS; attempts liên kết vào logical case, không tăng selected counts.

## Cleanup/termination và review

Known created owned → verify unchanged oracle → cleanup exact record ref; record absent authoritative → cleanup N/A/not needed theo state; outcome unknown → freeze mutation và bounded read reconcile; ownership mismatch → block delete; cleanup fail/unknown → unresolved ledger + owner, không runner retry tới khi safe. Tổng 20 phút, read recovery ≤1, runner retry ≤1 và chưa enabled mặc định.

Review proposals: REJECT “reset cả namespace bằng prefix” vì ownership phải exact ledger (LAB-AOCE-05); ACCEPT w2 collision stop trước write; REJECT F01 prerequisite seed cho F02 (FLOW-PACKET-03); ACCEPT NOT_EXECUTED/null manifest cho design. Local validation chỉ kiểm thiết kế/source links; chưa chứng minh reservation/cleanup live. Next evidence owner đề xuất trainer lab + QA data: approve namespace, helper inputs/permissions, lease behavior và canceled-run reconciliation.
