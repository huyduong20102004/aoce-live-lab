# Sprint review memo — AOCE, đề xuất ngày 2026-10-07

Mode: DRY-RUN / SIMULATED. Sources: packets U1–U7, cohort lab-a7/v3/ui-12/isolated-lab và SL-01–04. Memo do AI soạn, chưa human review/assignment; dates UTC+7 và owners là đề xuất.

Phạm vi sprint là thiết kế agent giữ oracle/evidence/ownership khi nén context, mở coverage từ F01 sang F02/F03, kiểm soát Git/CI/recovery và đọc metrics đúng mẫu số. Bộ bài nộp có benchmark ledger, compact context≤250 từ và v3, 8 regression fixtures, 3 flow contracts/isolated data strategy, simulated change review/PR, workflow/config CI draft, 4 incident recoveries và risk register. Không có live app, test project, credential hoặc CI runtime nên các thay đổi chưa chứng minh execution outcomes.

Cohort metrics là 10 selected logical cases, 8 executed với 11 attempts. First-pass 4/8=50%, eventual pass6/8=75%, flaky2/8=25%, failures2/8=25%; E06 blocked account và E07 skipped budget nằm trong selected, không pass. Retry overhead3 extra attempts=37.5% của baseline8. Đây là fixture sample nhỏ; pass-after-retry không chứng minh fix/root cause hay production reliability.

Evidence full7/8 executed, E05 partial; full-evidence passes5 gồm E08 nhưng E08 cleanup/usage UNKNOWN. Cleanup success4/6 needed, E04 failed và E08 unknown cần giữ unresolved. Subtotal tiền giả lập0.89, full cost UNKNOWN do E08 usage missing; cost per evidence-complete pass có lower bound0.178, không exact total. Budget1.20 chưa chứng minh under-budget; forecast của E07 thiếu inputs nên không kết luận guard đúng/sai. Test duration n8 median82.5s, range40–170s, không end-to-end latency.

Schedule packet có observed dispatch3/4 slots, SL-04 missing cause unknown. Dispatch delay n3 median2 phút/range0–3, queue median2/range1–8. Không claim CI ran every night on time. Design mapping4/4 business IDs là mapping có oracle; policy LAB-AOCE-05 đánh giá riêng, Viewer UI coverage chưa backend authorization proof.

Benchmark U1 cho thấy B rẻ nhưng fail oracle/provenance/cleanup gates, không được chọn. C1/C2 summary tốt và review time thấp hơn A trên fixture, nhưng C3 stale evidence/missing usage khiến toàn config chỉ accept2/3; all-row cost/accepted lower bound0.1270375 đã vượt A0.108391667. Đề xuất giữ A làm baseline, sửa matching-evidence gate/context missing flags của C rồi lấy cohort mới; không báo production savings hay kết luận nguyên nhân do riêng context.

Quyết định hiện tại: hoàn thành bài nộp dry-run để review; **chưa production rollout, chưa bật live schedule**. Pilot manual hẹp chỉ đề xuất sau trainer cấp runtime và human QA xác nhận controls. Bộ YAML ở thư mục bài nộp, không được copy deploy trước prerequisites/manual gate. Rủi ro ưu tiên R01/R02/R03/R07 về false pass, stale evidence, unknown write và unresolved cleanup có score đề xuất9; score không probability.

| Action/decision | Evidence hiện có | Remaining gap / next proof | Proposed owner | Proposed due date / review condition |
| --- | --- | --- | --- | --- |
| Giữ oracle và reject stale evidence trước pilot | B fails, C3, RG-03/04/08 | Actual controller negatives reject + positive accepts; human review | QA context/controller | 2026-10-08; gate fail thì rollback v1 |
| Reconcile cleanup issues, block unsafe rerun | E04/E08, INC-62, CI-55/58 | Exact owned refs/authoritative states, helper permission và durable canceled-run reconciliation | QA data + lab operator | 2026-10-08; chỉ resume write khi resolved/proven safe |
| Triển khai static PR lane trong lab repo được cấp | VC-41/42 old revision, draft workflow | Actual final-SHA typecheck/regression/discovery, no secrets in PR | Repo/CI maintainer | 2026-10-09; không gọi PR static green là live pass |
| Chạy một manual smoke 3 flow sau prerequisites | Flow contracts/isolated auth/data design | Approved lab URL/accounts/lease; reporter/assertion/artifact/cleanup actual run URL/SHA | Trainer lab + QA runner | 2026-10-09; zero no-tests/unresolved cleanup, matching evidence |
| Xác minh SL-04 và schedule monitor; sau đó mới cân nhắc schedule | 3/4 observed slots | Cause investigation, default branch/gates, monitor missing-slot evidence; actual scheduled event khác manual | CI maintainer | 2026-10-10; manual validation cùng SHA, quyền schedule được cấp |
| Hoàn thiện cost/budget evidence | E08 missing, subtotal0.89, E07 forecast unknown | Usage export/rate version/forecast decision inputs; exact total | QA metrics/cost owner | 2026-10-10; missing vẫn phải report UNKNOWN |
| Xác nhận manual-first và independent QA | AI draft/self-review thật đã lưu | Học viên tự phân tích nguồn, trainer/peer xác nhận review decisions; không backdate | Học viên + trainer | 2026-10-10; completion pedagogy do trainer quyết định |

Tại review tiếp theo, chỉ mở rộng pilot/schedule khi human review và evidence của revision cuối chứng minh các gates; runtime negative-case/security cần contract riêng. Nếu không tái hiện incident thì ghi chưa tái hiện, không lấy run retry xanh để đóng risk. Các dates/owners ở đây là kế hoạch đề xuất, không thông báo đã giao việc.

Review log: ACCEPT subtotal correction0.89 (sum10 rows); REJECT AI draft production-ready/retries-fixed/on-time/cleanup-complete (E04/E05/E08/E09/SL-04); ACCEPT lower-bound cost cùng UNKNOWN; REJECT dùng UI disabled làm toàn bộ security coverage (LAB-AOCE-04). [Metrics evidence](U7_metrics-and-claims.md), [risk register](U7_risk-register.md), [local validation report](evidence/validation-report.md).
