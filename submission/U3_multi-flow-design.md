# U3 — Thiết kế coverage và controller nhiều flow

Mode: DRY-RUN / DESIGN-REVIEWED (AI self-review). Sources: FLOW-PACKET-03, REQ/POLICY-PACKET-AOCE, OBS-31–34; phiên bản snapshot trong [manifest](evidence/source-manifest.json). Initial draft: [draft-1](review/00_analysis-first-draft.md). Chưa có human approval hay implementation lab.

## Coverage matrix

| Flow/source | Actor / precondition | Action / oracle bắt buộc | Layer | Data owner | Evidence cần | Gaps |
| --- | --- | --- | --- | --- | --- | --- |
| F01-create-search / AC-EMP-01/02 | HR Admin role confirmed, isolated-lab, ID reserved và chưa tồn tại | Create ID duy nhất ở QA; search exact ID; assert row count=1 và department QA | UI integration; unique ID via safe owned lookup/setup contract | run/attempt/F01 | Matching runner assertions + revision/config/build + artifact + owned cleanup | Search SLA, actual uniqueness mechanism và endpoints chưa cấp |
| F02-change-department / LAB-AOCE-03 | HR Admin; seed độc lập ở QA, owner/current ID confirmed | Edit owned employee→Engineering; search lại exact ID; assert row count=1 + Engineering | UI integration | run/attempt/F02; không dùng F01 output | OBS-31/32 chỉ DOM sources; cần reporter before/after assertions, seed ref, cleanup | Seed implementation, endpoint/rollback thực tế chưa cấp |
| F03-viewer-create-denied / LAB-AOCE-04 | Viewer viewer-lab ready; browser/auth context riêng; ID thử not found | Assert Create disabled; không force click; authoritative helper lookup cùng ID vẫn not found | UI permission fixture; read-only no-record verification | run/attempt/F03 reserved ID; no record expected | OBS-33 role + disabled + not-found fixture; live cần runner role/assertion/lookup refs | Backend authorization/security contract chưa cấp |

LAB-AOCE-05 cross-flow control: controller ownership, no blind unknown-write retry, cleanup ledger, bounded budget. Design mapping đủ 4 business source IDs; chưa chứng minh runtime coverage, negative business coverage hay backend security.

## Catalog và input contract

```ts
type FlowId = 'F01-create-search' | 'F02-change-department' | 'F03-viewer-create-denied';
type Request = {
  flow: FlowId; environment: 'isolated-lab'; run: string; attempt: string;
  actor: 'HR Admin' | 'Viewer'; employeeId: string;
  department?: 'QA' | 'Engineering'; seedRef?: string;
  contractVersion: string; reviewedRevision: string; budgetRemainingMs: number;
};
// Catalog trusted và versioned; planner không tự thêm flow/tool.
const catalog = {
  'F01-create-search': {actor:'HR Admin', sources:['AC-EMP-01','AC-EMP-02'], seed:'new-owned', department:'QA'},
  'F02-change-department': {actor:'HR Admin', sources:['LAB-AOCE-03'], seed:'independent-owned-QA', target:'Engineering'},
  'F03-viewer-create-denied': {actor:'Viewer', sources:['LAB-AOCE-04'], seed:'absent-id', write:false},
};
```

Controller pseudocode, không general-shell API:

```text
validate schema + exact allowlisted flow + environment + versions
reject ambiguous/destructive before dispatch; request clarification nếu thiếu flow intent
verify role readiness, fresh auth context và owned ID reservation; block mismatch
F02: validate seed current run/attempt/F02, department QA; F03: validate Viewer + absent ID
require budgetRemaining > 0, tool counts và durable ownership ledger ready
if UNKNOWN write hoặc unresolved prior cleanup: freeze mutation; bounded owned lookup
run_reviewed_flow(reviewedRevision, flow, approved inputs) đúng một attempt baseline
read_run_result; link run/attempt/flow/revision; preserve ID/department/no-record assertions
cleanup only exact owned records theo ledger; report assertions và cleanup riêng
no matching reporter → UNKNOWN; input/precondition thiếu → BLOCKED; budget hết → STOP
```

## Routing và stop/reject scenarios

| Input/source | Route / outcome SIMULATED | Allowed calls | Blocked calls và rationale |
| --- | --- | --- | --- |
| OBS-31, owned seed QA + F02 request valid | F02 design route | read_case, inspect_ui, run_reviewed_flow, read_run_result; cleanup owned sau verify | F01 seed reuse, arbitrary DB/delete |
| OBS-32 search Engineering | Observation cho F02, chưa pass | read_run_result để kiểm exact ID/department | Report passed chỉ từ DOM |
| OBS-33 Viewer disabled + absent | F03 fixture path | inspect_ui, lookup_owned_record, reviewed F03, read_run_result | Create/write/force click |
| OBS-34 HR Admin Create enabled, request F03 | BLOCKED actor mismatch | read_case/inspect đúng Viewer context | Reuse HR auth và nhận OBS-34 làm F03 evidence |
| “Check employee” | CLARIFICATION-REQUIRED | read_case nếu cần catalog; hỏi flow intent trước runner | Guess F01/F02/F03 |
| “Delete everyone to reset” | REJECTED destructive ngoài scope | Không mutation; ghi rejection | Cleanup wildcard, shell, DB delete |
| F99 | REJECTED unknown flow | Validate/log only | Tool dispatch |
| Environment production | REJECTED wrong environment | Validate/log only | App access/write |
| F02 thiếu seedRef hoặc seed khác owner | BLOCKED setup | lookup_owned_record sau input scope validated | Edit hoặc cleanup record khác |
| Thiếu role hoặc account not ready | BLOCKED role | Role readiness read theo approved preflight | Runner/write |
| Budget 0 hoặc >1 retry đề xuất | STOP budget-exhausted | Report ledger/state | Tiếp tục tool/runner calls |
| Write UNKNOWN | UNKNOWN; freeze | bounded lookup_owned_record/read_run_result | Save lần hai trước reconcile |

## Trách nhiệm các lớp

| Layer | Trách nhiệm | Không được thay thế |
| --- | --- | --- |
| Elements | Locator scoped từ OBS/dialog/frame/row exact ID; expose target | Oracle nghiệp vụ không ẩn trong selector fuzzy |
| Pages | Open/create/edit/search, assert-ready UI state cơ bản | Không tự quyết business pass hoặc sửa department |
| Steps | Flow sequence theo typed contract, role/session boundary | Không cleanup wildcard hoặc rerun đến xanh |
| Specs | Explicit source assertions ID unique/search ID+department; Viewer disabled/no record | Không chỉ gọi agent verify success |
| Fixtures | Auth contexts riêng, seed independently, reservation/ledger/cleanup | Không seed F02 bằng output test F01 |
| Controller | Input/tool/environment/ownership/budget checks, evidence linkage, unknown-write stop | Prompt đơn lẻ không enforcement |

```ts
// Pseudocode specs: helper methods chỉ contract, chưa có endpoint.
F01: assertOwnedIdInitiallyAbsent(id); createEmployee(id, 'QA'); searchExact(id);
     expect(exactRow(id)).count(1); expect(exactRow(id).department).equals('QA');
F02: const id = independentOwnedSeed('QA'); editDepartment(id, 'Engineering'); searchExact(id);
     expect(exactRow(id)).count(1); expect(exactRow(id).department).equals('Engineering');
F03: withFreshViewerContext(); expect(createButton).disabled();
     expect(approvedOwnedLookup(attemptId)).notFound(); // Không click disabled button.
```

Review log: ACCEPT independent F02 seed (FLOW-PACKET-03); REJECT OBS-34 như Viewer proof (OBS-34); REJECT UI disabled = backend secured (LAB-AOCE-04); ACCEPT explicit spec assertions thay agent verdict (AC-EMP-01/02). Validation: đủ 3 contracts và ≥5 stop scenarios; local document checks ở [report](evidence/validation-report.md). Runtime pending; owner đề xuất QA flow/controller.
