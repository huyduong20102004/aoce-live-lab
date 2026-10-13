# Bản phân tích đầu — trước bước AI tự review

Mode: DRY-RUN / SIMULATED. Version: draft-1, ngày 2026-10-07 (UTC+7).
Nguồn: handout và course content trong thư mục gốc; các packet giữ nguyên.

Đây là bản nháp do Codex tạo theo yêu cầu người dùng. **Không phải bằng chứng học viên đã phân tích manual trước AI.** Chưa có peer review hoặc người QA độc lập phê duyệt. Các quyết định QA trong bộ bài nộp là quyết định đề xuất của lời giải AI; học viên/trainer cần xác nhận riêng. Hai bước có thật trong phiên này: lưu draft trước; sau đó AI đối chiếu nguồn, tính toán và sửa artifact. Không có live model benchmark, app run hoặc CI run.

## U1 — BENCH/OUTPUT-PACKET-01, RATE-SYN-01

Fairness: cùng task/model/tools/evidence/schema; prompt và context đổi đồng thời nên không quy nguyên nhân cho riêng context. Sample n=3, không suy reliability. Scoring trước cost: A giữ oracle/provenance/ownership; B mất department, toast không đủ và cleanup vượt scope; C1/C2 phù hợp; C3 sai run evidence, usage missing. Công thức uncached=input_total-cached; không cộng cached hai lần. C3 chỉ biết CI=0.078, không gán model=0. Pilot đề xuất C có điều kiện sửa provenance; A giữ baseline.

## U2 — CONTEXT/REG-PACKET-02

Giữ CTX-01/02/03/04/08 với source/run, loại CTX-05/06 khỏi active context, quarantine CTX-07. Current observation không phải assertion. Candidate v2 mất ID/department, runner evidence, ownership, stop và budget. V3 phải có actor HR Admin và r02, tool allowlist và budget. RG-02/03/04/05/06/07/08 không được pass. Negative controls: wrong department và wrong run. Refresh khi build/role/run/source thay đổi; stop khi bị truncation.

## U3 — FLOW-PACKET-03

F01 create/search; F02 seed riêng QA→Engineering; F03 Viewer context riêng, disabled và lookup not found. UI permission không phải backend security. Reject F99/destructive/wrong env; clarification cho “Check employee”; block missing seed/role/budget. Namespace run/attempt/flow, reserve ID atomic, ledger có owner và ref. Collision không cleanup record worker khác.

## U4 — GIT-PACKET-04

Không có git repo thật ở workspace. Plan/diff là simulated. Stage prompt/selector/tests; sanitize và thêm revision trước stage docs. Ignore .env/auth; raw trace ở private artifact store. Không git add .; gitignore không xử lý file đã tracked. Merge oracle + evidence + UNKNOWN và 250 từ theo Unit 2, không 400. Reject toast/3 retries/remove ownership. VC-41 chỉ typecheck, VC-42 chỉ discovery, VC-43 environment blocked, VC-44 chưa có final-revision checks.

## U5 — CI-PACKET-05

PR static/context regression/discovery, không live secrets; trusted manual live trước schedule. Cron UTC 17 18 * * * = 01:17 Việt Nam hôm sau. Concurrency theo environment, không branch; runner retry=0 baseline. Missing secrets/no tests/cleanup unresolved đều fail rõ. always() không bảo đảm force-cancel cleanup: cần reconciler ngoài job với durable ledger. Workflow/config chỉ draft trong thư mục bài nộp. Script contracts phải bổ sung bootstrap manifest/discovery count/evidence check ngoài preflight/reconcile. RUN-A thất bại và cleanup unresolved; B no-tests false green; C environment blocked.

## U6 — INCIDENT/RET-PACKET-06

INC-61 test locator defect, scope Save trong dialog; overlay wait theo condition. INC-62 unknown write rồi lookup thấy created, không Save lần hai; verify search/cleanup còn thiếu. INC-63 iframe và virtualized search chưa có UI evidence, API existence không thay oracle. INC-64 runner infrastructure, không app flaky. X pass-after-retry, Y failed, Z first-pass; không root-cause fixed. Recovery bounded read một lần; retry runner tối đa một khi setup/cleanup chứng minh safe; tổng 20 phút.

## U7 — METRIC-PACKET-07

Selected 10, executed 8, attempts 11; first-pass 4, flaky-pass 2, failed 2, blocked 1, skipped 1. Full evidence executed=7; cleanup needs=6, success=4, failed=1, unknown=1. Evidence-complete passes=5, nhưng E08 cleanup/usage vẫn unknown. Cost subtotal=0.99, total unknown. Mapping 4/4 business IDs; policy 05 riêng. Schedule 3/4; delays dispatch=[3,0,2], queue=[2,8,1] phút. Không thêm missing slot vào selected. Risk gồm oracle drift, unknown write, shared data, missing evidence/schedule/cleanup/usage; owner và due date chỉ đề xuất.

## Cần kiểm chứng ở bước review

1. Tính lại tất cả monetary values bằng Decimal, gồm config C lower bounds.
2. Kiểm tra mẫu số U7: pass đủ evidence có bao gồm E08 dù cleanup unknown? Có theo định nghĩa assertion/evidence; report operational issue riêng.
3. Workflow có đủ bootstrap/evidence diagnostics khi preflight fail, và không upload auth/raw secrets?
4. Rõ actor provenance trong compact context: HR Admin lấy từ contract, không bịa từ CTX-03.
5. Kiểm tra U4 merged prompt có thống nhất 250 từ và scope rollback không xóa dữ liệu tùy tiện.

Unresolved: human manual-first/independent QA, runtime prerequisites, actual endpoints/SLA/backend security và production pricing chưa được cung cấp.
