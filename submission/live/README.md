# AOCE — bài nộp bổ sung LIVE-LOCAL

## M? nhanh

| Folder / file | N?i dung |
| --- | --- |
| [recovery](recovery/README.md) | B?o c?o m?i nh?t, scheduled run GitHub th?t, cancel/watchdog v?24/24 evidence checks |
| [ai](ai/README.md) | Actual Codex CLI benchmark U1/U2 v? model responses |
| [ci](ci/README.md) | Hosted PR/manual CI, API snapshots v? artifacts |
| [runs](runs) | Manifest, assertions, screenshots v? cleanup theo run ID |
| [local-checks](local-checks/README.md) | Log compiler/controller v? review local ban ??u |
| [windows-history](windows-history/README.md) | L?ch s? task Windows ?? t?t, XML v? invocation |
| [actual-metrics.md](actual-metrics.md) | Metrics ?? export, t?ch theo revision/cohort |
| [validation.md](validation.md) | Snapshot validator local ban ??u |

[Quay l?i b?i n?p](../ASSIGNMENTS.md). C?c b?o c?o c? theo ng?y/revision ? b?n d??i l? l?ch s?; tr?ng th?i hi?n t?i xem `recovery/README.md`. C?c file metrics/guard/validation ? root live l? ???ng d?n ??u ra c?a scripts.

**Cập nhật kiểm chứng 13/10/2026:** đã có scheduled event GitHub thật, cancellation/watchdog 7/7 và chẩn đoán Windows; GitHub là lịch chính, task local đã tắt. [Báo cáo mới nhất](recovery/README.md). Các trạng thái pending và SHA cũ bên dưới là snapshot lịch sử.

**Hosted update2026-10-13:** [GitHub PR/manual CI đã thực thi và repo đã publish](ci/README.md). Final mainSHA3878132 có fresh hosted/browser validation. Các trạng thái "GitHub chưa chạy" ở snapshot2026-10-09 chỉ là lịch sử; scheduled daily event mới vẫn cần proof riêng.

**AI update2026-10-09:** U1/U2 đã có actual Codex CLI benchmark/fixture outputs. Xem [AI cohort riêng](ai/README.md). Các dòng "provider benchmark/model outputs chưa có" bên dưới là giới hạn tại thời điểm hoàn tất webapp trước experiment; được cập nhật bằng cohort CLI, còn monetary billing/backend model snapshot và hosted CI chưa có.

Ngày 2026-10-09 (UTC+7). Webapp **http://127.0.0.1:4173**, source [aoce-live-lab](../../README.md). Môi trường này do Codex xây theo yêu cầu người dùng; backend/browser/tests thực sự chạy tại máy, dữ liệu nhân viên là dữ liệu lab. Không phải production PortalLite hoặc trainer-certified app. Dry-run packets ngày2026-10-07 giữ nguyên, không nhập vào cohort live.

Source revision cuối: `68ae69680f53e68e541813c0f044c5d22067389a`. Branch `feat/aoce-local-live`; repo Git riêng ở aoce-live-lab; không push/remote PR. Requirements AC-EMP-01/02, LAB-AOCE-03/04/05; endpoints/auth/fault/index semantics bổ sung theo [local contract](../../docs/LOCAL-LAB-CONTRACT.md), không tự biến unknown product contract thành confirmed requirement.

## Mở webapp và chạy lại

Account usernames `admin-lab` (HR Admin) và `viewer-lab` (Viewer). Password ngẫu nhiên riêng nằm ở file .env ignored trong aoce-live-lab; xem tại IDE trên máy, không gửi vào chat/commit. Server đang chạy hidden và chỉ bind loopback. Nếu đã dừng, từ terminal trong aoce-live-lab chạy `npm start` rồi mở URL trên.

```powershell
cd .\aoce-live-lab
npm run typecheck
npm run context:regression
npm run lab:smoke
npm test
npm run lab:metrics
```

Scripts require source committed/clean, namespace unique và preflight. `lab:init` có thể dựng lại cấu hình account/seed nếu chưa có, không reset data. Chạy test tự start server nếu chưa sẵn; server được start ngoài test giữ lại. Không cần public hosting hoặc tài khoản cloud để chạy local.

## Actual checks và evidence

| Check | Actual result tại revision cuối | Artifact |
| --- | --- | --- |
| TypeScript project | exit0 | [compiler log](local-checks/typecheck.txt) |
| Controller/context regression | 15/15, RG01–08 +negative/source/tool/redaction controls | [test output](local-checks/controller-regression.txt) |
| Manual three-flow smoke | selected3/executed3/pass3; retry0; cleanup resolved | [run mv0nfj0v](runs/mv0nfj0v-fcf1b44e/manifest.json) |
| Full browser suite | selected11/executed11/pass11; 3 business+8 controls; retry0 | [run mv0nfnvq](runs/mv0nfnvq-faeb5798/manifest.json) |
| Data reconciliation full suite | 33 exact reserved owned IDs verified absent; unresolved0, unowned demo giữ nguyên | [cleanup ledger](runs/mv0nfnvq-faeb5798/cleanup.json) |
| Runtime failure guards | Missing password nonzero; no-tests exit8; forged GitHub event nonzero | [guard checks](runtime-guard-checks.json) |
| Windows scheduler verification | Actual OS launch, selected3/executed3/pass3; cleanup resolved; task result0 | [scheduled run](runs/mv0nhq5q-5bc239db/manifest.json), [schedule proof](windows-history/schedule-evidence.md) |
| Independent artifact/secret/linkage check | xem actual report; không dùng screenshot thay assertions | [validation](validation.md) |

Screenshots sau login, source/oracle/actor/SHA/case IDs và cleanup refs được export từng run. Raw Playwright JSON/HTML/trace giữ private ở aoce-live-lab/.lab/runs/<run>; có thể chứa auth headers nên không commit/publish/gửi AI. Custom reporter xuất verdict từ runner thật; screenshot chỉ hỗ trợ quan sát. Actual costs monetary UNKNOWN (runner modelcalls0/usageN/A, chưa có compute/CI rate); không dùng RATE-SYN-01 thành provider invoice. [Actual metrics](actual-metrics.md) tách mỗi code revision, tách controls khỏi business cases và pre-body blocks khỏi executed.

## Recovery và controls đã thực thi

LOC-61: page-wide Save match2 strict-mode reject trước write; dialog-scoped combobox/Save và actionability wait giữ exactID/QA. LOC-62: owned create đã commit rồi UI abort250ms, lookup record tồn tại, controller freeze mutation, writes=1, search oracle và cleanup vẫn kiểm. LOC-63: target sau22 owned rows, first20 iframe không render, exact search tìm được rồi đổi Engineering. LOC-64: deliberate missing browser executable bị phân loại environment blocked; không claim tái hiện nguyên permission exception của packet INC-64. Wrong department/ID controls passed nghĩa oracle **phát hiện sai**, không employee sai được chấp nhận.

Additional LOCAL-AUTH-01: direct Viewer create trả403 HR Admin role required và no record. Chỉ là backend test của app local mới; LAB-AOCE-04 packet vẫn UI fixture boundary. Collision duplicate reservation409, duplicate create409 writes1, delete unowned demo403; server và helper exact ledger/token/role enforcement.

## Scheduling

Windows task `AOCE-PortalLite-Live-Smoke`, kiểm chứng bằng one-time OS trigger sau successful manual cùng SHA rồi cấu hình daily **01:17 UTC+7**. Task action chạy scheduled-entry.ps1 hidden dưới user hiện tại, Interactive logon, IgnoreNew, timeout20 phút. Máy phải bật và user signed-in; không đảm bảo job khi máy ngủ/tắt. Source đổi thì task block đến khi có manual smoke proof SHA mới.

Actual task dispatch/start/result, run ID và expected slot nằm ở [schedule evidence](windows-history/schedule-evidence.md); manifest trigger=windows-schedule không được gọi GitHub CI. Daily slot đầu sau khi bật chỉ được coi executed khi có actual run; one-time validation không chứng minh ngày tương lai. GitHub workflow source sẵn nhưng chưa remote/hosted Actions run URL.

Watchdog script hỗ trợ đọc ledger và cleanup exact expired-owned records ngoài runner; chưa fault-injection force-cancel process thật trong revision cuối. Forced kill/mất nguồn vẫn có thể bỏ in-job cleanup; không claim always bảo đảm mọi crash. Rerun mới bị block nếu server còn unresolved owned data. Owner local operator (người dùng) thực hiện/giám sát quyền và môi trường này; chưa gán trainer/team đã nhận việc.

## Lịch sử failures và giới hạn completion

Giữ nguyên các run cũ: readiness check sai Fetch property; tracing double-start fixture; Department locator exact-label không match và screenshot body chưa được export. Đã sửa ở commits có thật, không đổi những runs đó thành pass và không reuse old SHA cho revision cuối. [Review/validation bổ sung](local-checks/LIVE_completion-and-review.md) ghi facts/fixes/gaps và provenance.

U1 actual provider-backed calls/usage≥3 samples/config và U2 before/after **model** outputs đã bổ sung qua Codex CLI/ChatGPT; [actual AI evidence](ai/README.md), khác với Node regression. API monetary invoice chưa có và không áp giá API vào subscription như số tiền thực trả. U5 GitHub hosted PR/manual/schedule chưa chạy vì repo hiện local. Không tự cấp production-ready từ những cohorts nhỏ. Webapp local, source repo, controller, flows, recovery/model checks, scheduling proof và evidence hiện đã có để tiếp tục lab.
