# Local lab contract — PORTALLITE-LOCAL-01

Ngày 2026-10-09 (UTC+7). Webapp lab do Codex dựng theo yêu cầu tạo môi trường live của người dùng. Không phải production PortalLite hay môi trường trainer đã cấp. Requirements kế thừa nguyên nghĩa từ REQ-PACKET-AOCE: AC-EMP-01/02, LAB-AOCE-03/04/05. Inputs nhân viên là dữ liệu thử; browser/server/runner outcomes thu tại máy là **LIVE-LOCAL**, không packets giả lập.

## Runtime được hiện thực

Node22, Playwright/Chromium, server HTTP chỉ bind 127.0.0.1:4173. Account admin-lab/HR Admin và viewer-lab/Viewer có password ngẫu nhiên riêng trong .env ignored. Cookie HttpOnly/SameSite=Strict; auth state chỉ memory. Server Node single process xử lý transactions đồng bộ, ghi state qua temporary file+atomic rename. Đây là lab nhỏ, không multi-process database hay security certification.

UI: Create employee dialog với Employee ID/Department/Save; Edit employee dialog đổi department; iframe title Employee directory, Search employee ID textbox và Search button; exact search. Danh sách render tối đa20 rows, count tổng hiển thị. Không tuyên bố search latency SLA; timeouts là lab budgets.

Mới định nghĩa cho local app: REST endpoints /api/login, /api/me, /api/employees (GET/POST), /api/employees/:id (PUT), /api/health. LOCAL-AUTH-01 kiểm backend403 Viewer create; coverage này là bổ sung riêng local app, không biến LAB-AOCE-04 của packet thành product/backend proof.

## Ownership/tool/helper contract

Controller chỉ catalog F01/F02/F03 và sáu tool cards synthetic; tests/controller-regression kiểm input/environment/actor/source/oracle/evidence/tool scope. CI runner là trusted Node script, không planner được quyền general shell.

Helper hiện thực /api/lab/runs, /api/lab/reservations, /api/lab/ledger, /api/lab/records/:id, /api/lab/release. Register yêu cầu authenticated HR Admin, fresh run ID/current40-charSHA và exclusive lease20 phút; trả capability token chỉ lưu private .lab/grants. Server lưu hash capability, exact reservation ledger trước write, deny F03 mutation/repeat write/unknown owner. Read+cleanup cho owned record được phép reconcile sau lease expiry; cleanup phải authenticated HR Admin + exact reservation/capability. Không wildcard/prefix delete.

Namespace: E2E-AOCE-<caseRun>-<attempt>-<flow>, caseRun=<suiteRun>-<c+8hex case hash>. Case hash mở rộng namespace run để nhiều logical cases cùng flow không đụng ID; suiteRun là lease owner. Max100 chars và [A-Za-z0-9-], validated server-side. Không truncate IDs. Fixture fresh auth/browser context mỗi case; F02 seed độc lập, không dựa F01. Server atomic reservation trong single process; external sources khác repo/process không được bảo đảm lock bởi GitHub concurrency.

## Faults có kiểm soát, khác incidents packet

LOCAL-INC-61 `?scenario=ambiguous-save`: page có2 Save và overlay900ms trên Create dialog; page-wide click strict violation trước write, dialog-scoped click giữ ID/QA oracle.

LOCAL-INC-62 `?scenario=unknown-write`: POST owned create commit durable rồi delay acknowledgement1800ms; UI abort250ms báo UNKNOWN. Đây là **known local transaction semantics**, authoritative helper lookup xác nhận created; controller blocks re-write; search exactID/QA+cleanup vẫn cần runner assertions. Không suy semantics này cho server ngoài lab.

LOCAL-INC-63 seed target sau22 extra owned rows; initial list first20 không render target; iframe exact search/render+department assertion giữ oracle. LOCAL-INC-64 deliberate missing browser executable gây launch exception trước app actions; không claim tái hiện nguyên bản permission exception của INC-64 packet.

NC-DEPARTMENT Sales không thỏa QA; NC-ID ID khác không thỏa target. Controls pass nghĩa checker phát hiện mismatch; không báo employee sai department là business pass. Model/provider live không tích hợp: deterministic runtime model_calls0, usage N/A; cost model0 nhưng điện/máy/CI không có rate nên tổng tiền UNKNOWN. U1 actual AI benchmark vẫn pending, không dùng token estimates như billed usage.

## Evidence

Manifest suite run/attempt/caseRun/flow/actor/SHA/build/source/oracle/outcome/duration/screenshot hashes/cleanup. Raw Playwright JSON/HTML/trace ở .lab ignored, có thể chứa auth headers nên không commit/publish/gửi AI. Export chỉ sanitized manifest, counts, assertions/oracles, cleanup, screenshot sau login; không cookies/password/capability. Keep suite failures; runner retry0; no no-tests/suppress errors. Smoke exactly3 flow cases; robustness controls là cohort riêng.

Git source repo riêng aoce-live-lab, không init Git ở thư mục tài liệu gốc. Actual commits/branch/run evidence bổ sung ngoài repo trong bai-nop-AOCE/live sau final SHA. Local scheduled execution chỉ báo khi Windows Task Scheduler thực sự launch, phải có task name/status/timestamps; manual smoke không schedule proof. GitHub remote/Actions run URLs không bịa.

Human manual-first requirement vẫn không thể phục hồi bằng AI; trainer acceptance/production reliability không được tự cấp.
