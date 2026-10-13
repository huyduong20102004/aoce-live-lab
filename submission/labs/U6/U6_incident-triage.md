# U6 — Incident triage và runner outcomes

Mode: DRY-RUN / SIMULATED. Sources: INCIDENT-PACKET-06 INC-61–64, RET-PACKET-06 X/Y/Z, REQ/POLICY-PACKET-AOCE; version theo [manifest](../../evidence/source-manifest.json). Initial draft: [draft-1](../../review/00_analysis-first-draft.md). Chưa tái hiện failure, không trace/live reporter; root cause ngoài facts dưới đây vẫn HYPOTHESIS.

## Timelines, facts, gaps và discriminating checks

| Incident / timeline nguồn | Facts có nguồn | Layer / hypotheses, không khẳng định cause ngoài nguồn | Evidence gaps và next check | Proposed owner |
| --- | --- | --- | --- | --- |
| INC-61 lab-a6: t0 dialog mở/2 Save; t100 locator match=2; t150 strict-mode violation trước click; overlay t0–900 | Page-wide Save ambiguous; chưa click/write; dialog Create employee có đúng 1 Save | Test locator scope defect được timeline chứng minh; overlay có thể ảnh hưởng actionability sau sửa, chưa chứng minh gây strict-mode | Inspect dialog scoped count=1, actionability/overlay lifecycle, trace sau click và ID/QA assertions; không chọn first | QA UI |
| INC-62: t0 request dispatched; t1500 timeout; t1800 server created ref62; t2100 search chưa row; t2400 proposed second Save; t2600 owned lookup ref62/QA | Write outcome initially UNKNOWN; fixture lookup sau đó chứng minh owned record tồn tại QA; search assertions/cleanup chưa có | Write-ack/client timeout; index lag có observation nhưng chưa SLA/cause. Không known app fail/pass từ timeout | Read matching runner/search đúng ID+QA dưới bounded wait; authoritative lookup/ownership refs; cleanup result; không resend Save | QA recovery + QA data |
| INC-63: main-page không row; iframe title Employee directory; list render 20 rows; lookup có owned target; search exact ID allowed | Target tồn tại qua synthetic lookup; frame/list/search contract có nguồn; chưa thấy row rendered | Test scope/frame/virtualization hypotheses; chưa xác định wrong selector vs search/render/index issue | Inspect frame unique và textbox; search exact ID rồi count row=1+Engineering; preserve negative controls | QA UI F02 |
| INC-64: browser startup permission exception trước body; reporter incomplete; no click/assert/write evidence | Runtime infrastructure blocked trước assertions | Environment/runner permissions issue; không app assertion failure/flaky. No-write evidence ≠ full reconciliation nếu ledger thiếu | Check browser launch stderr, runner user/permissions/deps/container; verify ledger no write; exact code/config rerun sau sửa env | Lab operator / QA CI |

INC-61 có evidence đủ cho locator ambiguity, không cho toàn bộ fix pass. INC-62 không còn được click Save lần nữa sau t2600, vì record đã created; lookup existence không thay search assertion. INC-63 API/helper state không chứng minh UI F02 contract. INC-64 wrapper retry 10 lần vượt budget và không thêm app assertion evidence.

## AI candidates audit

| Candidate | Source fact phản biện | Quyết định đề xuất |
| --- | --- | --- |
| INC-61 `.first()`, force:true, wait 5s | Hai Save page-wide, exact dialog có một; overlay có lifecycle | REJECT; first có thể chọn sai button, force bỏ actionability, sleep không oracle |
| INC-62 Save again cùng ID | t1800/t2600 created owned record | REJECT; duplicate-write risk LAB-AOCE-05; timeout không chứng minh failed write |
| INC-63 API exists⇒F02 passed | Chưa row rendered; LAB-AOCE-03 là search ID+new department | REJECT; giữ UI oracle, frame/search chỉ actions |
| INC-64 classify app flaky + retry 10 | Startup trước test body, reporter incomplete | REJECT; BLOCKED-ENVIRONMENT, repair infra trước limited retry |

## RET-PACKET-06 — logical run semantics

| Run | Outcomes observed trong fixture | Classification / attempts | Không kết luận |
| --- | --- | --- | --- |
| X | Attempt1 fail, attempt2 pass | SIMULATED flaky-pass / pass-after-retry; 2 attempts | Không root cause fixed; không first-pass; cần matching second-attempt assertion/cleanup evidence |
| Y | Fail cả 2 | SIMULATED failed; 2 attempts | Không lấy X pass để đổi Y pass |
| Z | Attempt1 pass | SIMULATED first-pass; 1 attempt | Không chứng minh cả cohort reliable |

Theo [Playwright retries](https://playwright.dev/docs/test-retries), pass sau retry được phân loại flaky, khác first-pass. Fixture n=3, executed 3, attempts5, first-pass1/3, eventual pass2/3, flaky1/3, retry overhead2; không root-cause hoặc production reliability inference. Chưa có assertion/artifact linkage của actual X/Y/Z.

## Review log / validation

| Finding/proposal | Source | Quyết định đề xuất |
| --- | --- | --- |
| Overlay là root cause strict-mode | INC-61 t100 match=2 | REJECT; ambiguity giải thích violation, overlay chỉ separate hypothesis |
| Search chưa có row nghĩa create failed | INC-62 t2100 + t2600 | REJECT; authoritative lookup có record, search/index issue chưa phân biệt |
| Browser permission fix xong sẽ app pass | INC-64 | REJECT; chỉ khôi phục ability to execute, assertions còn pending |
| Giữ per-run retry classification | RET-PACKET-06 | ACCEPT; không ghép evidence các runs |

Validation local đủ 4 incidents/3 runs/source links; proposed locator/recovery ở [recovery plan](U6_recovery-and-validation.md). Chưa environment live, chưa reproduced/fixed, human QA chưa approve.
