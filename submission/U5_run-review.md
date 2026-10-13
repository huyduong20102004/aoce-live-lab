# U5 — Review synthetic CI run packets

Mode: DRY-RUN / SIMULATED, không có actual CI run URL. Sources: CI-RUN-A/B/C và CI-51–58 trong CI-PACKET-05; revision fixture lab-a5, không revision bài nộp. [Workflow design](U5_ci-design.md) không đã chạy. Initial draft: [draft-1](review/00_analysis-first-draft.md).

| Packet | Có thể kết luận từ nguồn | Không đủ evidence / corrected report | Next proof / proposed owner |
| --- | --- | --- | --- |
| CI-RUN-A | Selected=3, executed=3, first-pass=2, failed=1; cleanup unresolved=1; artifacts linked=3; lab-a5 | SIMULATED runner first-pass=2/3, fail=1/3; operational unresolved cleanup. Ba artifact links không tự chứng minh nội dung/linkage đầy đủ. Không suite pass | Exact flow/attempt assertion results, current refs, owned cleanup record+reconcile, revision/config/build; QA triage + QA data |
| CI-RUN-B | Selected=0, executed=0, wrapper exit=0; install-log-only artifact, says 100% | SIMULATED NO-TESTS/false green. Pass rate N/A (executed=0), không 100%. Không có runtime assertions/cleanup proof | Remove pass-with-no-tests, verify selector+expected flow discovery, execute authorized runner; QA CI |
| CI-RUN-C | Manual dispatch; startup failure, selected=3 executed=0; no assertion report/no write evidence | SIMULATED BLOCKED-ENVIRONMENT, 0/3 execution completeness; pass N/A. “No write evidence” không tự chứng minh record absence nếu ledger thiếu | Browser permissions/deps/runner diagnostics, no-write ledger, exact revision manual rerun khi environment repaired; lab operator |

Không claim schedule fire từ manual C, không dùng lab-a5 để chứng minh draft workflow hiện tại pass. A cần preserve failure và cleanup status riêng; B cần exit nonzero khi no-tests; C không là application assertion failure/flaky.

Evidence checklist pending cho live: actual run URL/event/SHA, command/config/prompt/build; selected/executed per-flow; reporter/assertion artifacts; durable ownership/cleanup; budget/usage metadata và missing fields; scheduled trigger actual run riêng sau manual gate. Default branch/main còn assumption.

Review log: REJECT RUN-B exit0⇒100% (source count=0); ACCEPT RUN-A cần unresolved issue (source cleanup=1); REJECT RUN-C manual⇒schedule ready (source manual/browser failure); ACCEPT artifact linkage/content check riêng (linked=3 chưa full contents). Quyết định là AI đề xuất, chưa người QA phê duyệt.

Validation actual chỉ local document arithmetic/links; các packets không chạy lại được vì không runtime được cấp. Owner và next action là đề xuất, không assignment.

## Actual GitHub Actions extension — 2026-10-13

[Hosted CI evidence](hosted-ci/README.md): PR #1 checks SUCCESS ở run38337908837; manual Linux/Chromium smoke SUCCESS ở run38338108312/maince8d017, selected3/executed3/pass3, owned cleanup resolved và evidence COMPLETE. Các run URLs/metadata/artifacts có thật, không dùng CI-RUN-A/B/C packets như hosted results. Daily01:17 được gated bằng matching manual SHA; actual schedule event còn cần quan sát khi slot tới hạn.

## Bổ sung live-local ngày 2026-10-09

Đã dựng môi trường mới theo [PORTALLITE-LOCAL-01](../docs/LOCAL-LAB-CONTRACT.md), không phải chạy CI-RUN-A/B/C. Repo source riêng `aoce-live-lab`; code revision cuối `68ae69680f53e68e541813c0f044c5d22067389a`.

| Actual local run | Trigger / selected / executed | Kết quả / cleanup | Evidence |
| --- | --- | --- | --- |
| mv0nfj0v-fcf1b44e | manual-local /3/3 | RUN-PASSED; F01/F02/F03; unresolved0 | [Manifest](live/runs/mv0nfj0v-fcf1b44e/manifest.json) |
| mv0nfnvq-faeb5798 | manual-local full suite /11/11 | RUN-PASSED; 3 business+8 control cases; 33 exact owned IDs absent; unresolved0 | [Manifest](live/runs/mv0nfnvq-faeb5798/manifest.json), [cleanup](live/runs/mv0nfnvq-faeb5798/cleanup.json) |
| mv0nhq5q-5bc239db | windows-schedule /3/3 | RUN-PASSED; actual Task Scheduler launch, task exit0; cleanup resolved | [Manifest](live/runs/mv0nhq5q-5bc239db/manifest.json), [schedule evidence](live/schedule-evidence.md) |

Đã thực thi script guards missing password→nonzero, zero-tests→NO-TESTS exit8 và từ chối giả danh GitHub scheduled trigger: [actual guard checks](live/runtime-guard-checks.json). Lần kích hoạt từ Windows Task Scheduler và cấu hình daily được ghi riêng ở [live index](live/README.md); Windows schedule không phải GitHub Actions run. GitHub remote/PR checks trên hosted runner và actual provider benchmark chưa được chạy. Raw auth/trace không commit/export vào bài nộp. Các run thất bại lúc hoàn thiện runner giữ nguyên, không đổi verdict thành pass.
