# Completion và review — local live extension

Ngày2026-10-09 UTC+7. AI-generated implementation/review theo yêu cầu user tự tạo lab. Không bịa human manual analysis/peer approval. Source cuối `68ae69680f53e68e541813c0f044c5d22067389a`; branch feat/aoce-local-live; original source packets giữ nguyên hashes.

| Unit | Dry-run artifact đã có | Actual live bổ sung | Remaining evidence / limitation |
| --- | --- | --- | --- |
| U1 | 9 samples/rubric/cost ledger | Có real browser latency/counts và monetary usage N/A cho deterministic runtime | Chưa provider/model benchmark A/B/C, billed tokens/rate ≥3 actual outputs/config; không nói production savings |
| U2 | Compact v3/manifest/8 fixtures/controls | 15 Node regression checks gồm stale run/revision, wrong dept/ID, source/actor truncation, tool allowlist và redaction | Không actual AI model output trước/sau; fixture source synthetic nhưng checker execution thật |
| U3 | 3 flow contracts/layers/isolation | Elements→Pages→Steps→Specs/fixtures/controller thực thi; independent F02 seed actual verified trước routing; Viewer separate context | Local app contract tự dựng, backend security chỉ case LOCAL-AUTH-01, không all-security proof |
| U4 | PR/conflict/staging plan | Git repo/branch/commits/SHA thật; final typecheck/regression/browser/evidence linkage; .env/.lab/node_modules ignored | Không remote PR/push/merge (handout không bắt buộc); trainer/peer chưa review |
| U5 | YAML/script/scenario design +packet reviews | Scripts implemented, manual smoke, failure guard exits, Windows scheduled launch và daily config | Hosted GitHub PR/manual/schedule chưa thực thi; actual future daily slots phải monitor |
| U6 | Incident/recovery plan | Strict Save/overlay, known delayed acknowledgement, beyond20 iframe, wrong oracle controls; missing-executable environment fault | Local faults không nguyên bản packet telemetry; no original INC-64 permission repro; force cancel drill chưa chạy |
| U7 | Synthetic10EIDs/4slots/risks | Actual manifests/cleanup/screenshots/metrics theo SHA/trigger; monetary total UNKNOWN; historical failures giữ | Không trộn synthetic; n nhỏ, no production readiness; human manual-first/trainer pass pending |

**AI extension2026-10-09:** các missing provider/model items của U1/U2 trong bảng snapshot trên đã bổ sung bằng [Codex CLI actual cohort](../ai/README.md): U1=9samples với usage thật; U2=16 originalresponses +2 complete-positive controls. Monetary cost UNKNOWN/không API invoice; app fixtures synthetic không được gọi live app pass. Hosted CI vẫn pending.

## Actual review decisions / fixes

| Finding / evidence | Source location | Decision và result |
| --- | --- | --- |
| Native Fetch Response.ok là boolean, initial code gọi như function khiến readiness false | scripts/live-run.mjs; startup runs mv0mm4yl/mv0mmqly/mv0mnbio | ACCEPT fix .ok property + consume health JSON/close connections; giữ startup failures, không app failure |
| Test runner đã tự manage tracing cho browser contexts; manual start gọi lần hai | tests/fixtures/lab.ts; mv0mnwwh fixture errors | ACCEPT remove manual tracing; raw failure traces remain private; zero app writes verified/reconciled separately |
| Helper fetch failed sau synchronous runner; stale keepalive là hypothesis từ code/timeline, chưa definitive RCA | scripts/runtime.mjs | ACCEPT Connection:close/helper body consume; runs tiếp theo reconcile thành công, không coi fix outcome là root-cause proof |
| Department exact label selector không match wrapper label text chứa option values | public/index.html, EmployeePage.ts; mv0mpki6 screenshot/error-context | ACCEPT explicit label-for và scoped combobox from observed DOM; keep ID/department assertions; final smoke passes |
| Explicit screenshot attachment body không có path ở onTestEnd | reporters/manifest.ts; earlier missing screenshot despite F03 pass | ACCEPT persist body +hash +unique exported filename, không gọi upload success evidence complete trước fix |
| Discovery no-tests CLI exit1 đã fail nhưng classifier chưa gán NO-TESTS exit8 | scripts/runtime.mjs; actual guard-check initial detectedfalse | ACCEPT inspect structured errors then explicit exit8; guard actual final detectedtrue |
| Error call logs có thể chứa session/capability, exporter raw regex có thể làm JSON invalid | server/lib.mjs, scripts/runtime.mjs | ACCEPT redact exact private grant/session/headers; sanitize strings recursively; synthetic header negative passes; actual exports secret-scanned without printing secrets |
| F02 route seedOwned=true trước seed tồn tại là sai precondition | tests/fixtures/lab.ts | ACCEPT BLOCKED trước seed; validate actual created record owner/ID/QA rồi permit route; rerun final3/11 pass |
| Reporter-started fixture errors chưa nghĩa business body executed | scripts/metrics.mjs; tracing setup failures | ACCEPT selected retains blocked cases, executed excludes missing oracle/source before body; group theo codeSHA |
| Không phải mọi F01 đã vào body đều tạo record cần cleanup | scripts/metrics.mjs; earlier Department locator failure trước Save | ACCEPT cleanup=N/A được loại needs denominator khi absence đã verified; failed/unknown cleanup vẫn giữ mẫu số; không dùng flow type đơn lẻ suy needs |
| Wrong dept/control case pass có thể bị nhầm business success | manifest kind +actual metrics | REJECT aggregate controls như business requirement passes; current full suite3business+8controls |
| One-time OS trigger proof có thể bị nhầm daily/GitHub proof | scheduled-entry.ps1/task info +manifest | REJECT; distinguish Windows actual one-time, future daily pending, no GitHub URL |

## Git review và rollback

Commits có thật nằm ở [source revision record](git-evidence.json). Root app commit6f19de8, reviewed run pipeline và fixes trên feat/aoce-local-live; final source clean. Ignored credentials/auth/grants/raw artifacts không staged. Validation ở [actual local report](../validation.md). PR description đề xuất: "Add isolated PortalLite lab with source-bound create/search, owned department edit and Viewer denial; run scoped recovery/negative controls with durable ownership and evidence checks. Final local smoke3/3, suite11/11 and controller15/15; no hosted CI/provider benchmark claim."

Rollback: disable task do lab tạo nếu cần dừng automated writes, stop đúng server PID của lab, revert scoped source commits đến revision đã kiểm chứng; code revert không undo writes. Reconcile exact ledger/capability IDs và verify absence, giữ unowned demo/manual data; unknown ownership/outcome stop, không prefix delete. Không hard reset user docs. Namespace/contracts/provider permissions mới cần review trước mở rộng.

Residual risks: machine offline/not logged in; timer dispatch delay; forced termination bỏ cleanup; lost local .env/state/grants; controller tests không chứng minh model sẽ tuân policy; artifacts raw nhạy cảm; actual cost rate unknown. Chỉ controls có local runtime evidence được đánh dấu validated locally, không close mọi risk của production/course packets.
