# U7 — Metrics, schedule và AI claim audit

Mode: DRY-RUN / SIMULATED. Source: METRIC-PACKET-07, 10 EIDs/4 slots; code lab-a7, prompt/context v3, app ui-12, isolated-lab. Source snapshot/hashes: [manifest](../../evidence/source-manifest.json). Initial draft: [draft-1](../../review/00_analysis-first-draft.md); AI tự review đã sửa subtotal từ 0.99 thành **0.89**, không tạo telemetry mới. Không human manual-first/independent QA approval.

## Cohort và ledger

Selected = 10 logical case+parameter executions; EIDs không phải attempts. D71={E01–03}, D72={E04–06}, D73={E07–10}. Executed={E01,E02,E03,E04,E05,E08,E09,E10}; E06 blocked Viewer not ready và E07 budget-skipped trước assertion không executed. SL-04 missing không có case list, không thêm selected/failed cases giả.

| EID / dispatch | Flow/outcome | Attempts | Evidence | Cleanup needed / outcome | Model calls / usage | Subtotal tiền | Test giây |
| --- | --- | ---: | --- | --- | --- | ---: | --- |
| E01/D71 | F01 first-pass | 1 | full | yes/success | 0/not-applicable | 0.10 | 80 |
| E02/D71 | F02 flaky-pass | 2 | full | yes/success | 1/complete | 0.16 | 150 |
| E03/D71 | F03 first-pass | 1 | full | no/not-applicable | 0/not-applicable | 0.04 | 40 |
| E04/D72 | F01 failed | 2 | full | yes/failed | 1/complete | 0.18 | 170 |
| E05/D72 | F02 flaky-pass | 2 | partial | yes/success | 1/complete | 0.17 | 145 |
| E06/D72 | F03 blocked | 0 | none | no/not-applicable | 0/not-applicable | 0.02 | not-executed |
| E07/D73 | F01 skipped | 0 | none | no/not-applicable | 0/not-applicable | 0.00 | not-executed |
| E08/D73 | F02 first-pass | 1 | full | yes/unknown | 1/missing | 0.08 | 85 |
| E09/D73 | F03 failed | 1 | full | no/not-applicable | 0/not-applicable | 0.05 | 55 |
| E10/D73 | F01 first-pass | 1 | full | yes/success | 0/not-applicable | 0.09 | 75 |

[CSV ledger](../../evidence/U7_execution-ledger.csv), [Decimal/statistics output](../../evidence/calculations.json), [recompute script](../../tools/calculate.py). Tiền là synthetic unit, không USD/provider invoice. Missing model usage E08 không được điền 0; model calls=0 ở những row khác có fixture evidence nên model marginal cost có thể 0 trong lane deterministic, không total CI cost 0.

## Metric dictionary với numerator/denominator

| Metric | Value | Numerator | Denominator / included EIDs | Unknowns / interpretation |
| --- | --- | --- | --- | --- |
| Selected / executed | 10 / 8 | 8 executed | 10 E01–E10 | E06/E07 trước assertion; không discard selected |
| Execution completeness | 80% | 8 | selected10 | Không tính SL-04 vào selected |
| First-attempt pass rate | 50% | 4: E01,E03,E08,E10 | executed8 | Outcome fixture, không live pass |
| Eventual pass rate | 75% | 6: E01,E02,E03,E05,E08,E10 | executed8 | Bao gồm flaky; E04/E09 vẫn failed |
| Flaky proportion | 25% | 2: E02,E05 | executed8 | Root cause/fixed chưa chứng minh |
| Persistent failure rate | 25% | 2: E04,E09 | executed8 | Runner fixture failed; không tự suy app cause |
| Blocked / selected | 10% | 1: E06 | selected10 | Viewer not ready |
| Skipped / selected | 10% | 1: E07 | selected10 | Forecast inputs chưa kiểm chứng |
| Attempts | 11 | 1+2+1+2+2+0+0+1+1+1 | 8 executed logical cases | Attempts không thành 11 selected |
| Retry overhead | 3 extra attempts | 11−8; E02,E04,E05 mỗi1 | baseline8 attempts, tỷ lệ 3/8=37.5% | Không thể tách actual retry money/time từ aggregate rows |
| Cases retried | 37.5% | 3: E02,E04,E05 | executed8 | Phân biệt flaky2 vs retried3 |
| Evidence completeness | 87.5% | 7: E01,E02,E03,E04,E08,E09,E10 | executed8 | E05 partial thiếu assertion artifact; full không có nghĩa passed |
| Evidence-complete passes | 5 cases; 5/6=83.33% pass evidence completeness | E01,E02,E03,E08,E10 | all passes6 | E08 full rubric nhưng cleanup/usage unknown riêng |
| Cleanup completion | 4/6=66.67% | E01,E02,E05,E10 success | needs6: E01,E02,E04,E05,E08,E10 | E04 failed, E08 unknown giữ mẫu số; F03 denied no write không thêm cleanup |
| Cleanup failures / unknown | 1 failed +1 unknown | E04 / E08 | needs6 | Không “complete”; unresolved owned records |
| Business requirement mapping | 4/4=100% design | AC-EMP-01/02→F01; LAB-AOCE-03→F02; LAB-AOCE-04→F03 | business source IDs4 | Không runtime/negative/backend coverage; LAB-AOCE-05 control riêng |
| Measured subtotal | 0.89 | Sum E01–E10, gồm failed/blocked/skipped | cohort10 | Total UNKNOWN do E08 usage missing; lower bound 0.89 |
| Cost per evidence-complete pass | UNKNOWN; measured lower bound 0.178 | ALL cohort cost lower bound0.89 | 5 full-evidence passes | Không dùng chỉ pass-cost làm numerator; E08 cleanup unknown không bị che |
| Usage completeness khi có model call | 75% | 3: E02,E04,E05 complete | 4 call-bearing E02,E04,E05,E08 | E08 missing; 6 no-call rows là N/A, không missing |
| Budget status | UNKNOWN | Known0.89 < budget1.20 | cohort budget1.20 | Actual headroom tối đa0.31 nếu missing cost nonnegative; chưa chứng minh under budget |

Arithmetic cost: 0.10+0.16+0.04+0.18+0.17+0.02+0+0.08+0.05+0.09=0.89. D71=0.30, D72=0.37, D73 known=0.22 và total UNKNOWN. Eventual passed/selected=6/10=60% là metric khác, không thay 6/8 eventual rate. E07 forecast đúng/sai UNKNOWN: thiếu predicted spend/decision inputs và E08 usage, không suy từ cuối cohort0.89.

## Test durations: n=8, không end-to-end latency

Mẫu raw theo EID: E01=80, E02=150, E03=40, E04=170, E05=145, E08=85, E09=55, E10=75 giây. Sorted=[40,55,75,80,85,145,150,170]; median=(80+85)/2=82.5s, range40–170s, sum800s, mean100s. Mean/sum chỉ descriptive; không tách attempt duration từ row aggregated. Không queue/install/cleanup/model time, không end-to-end/p95 reliability.

| Flow | Included executed samples | Median / range giây |
| --- | --- | --- |
| F01 | E01=80,E04=170,E10=75 | 80 / 75–170 (n3) |
| F02 | E02=150,E05=145,E08=85 | 145 / 85–150 (n3) |
| F03 | E03=40,E09=55 | 47.5 / 40–55 (n2) |

## Schedule metrics riêng

Tất cả giờ dưới đây UTC+7. Expected 01:17 theo từng ngày packet; không yêu cầu actual minute precision. Delay tính phút cùng slot.

| Slot / date | Expected | Dispatch / start | Dispatch delay | Queue delay=start−dispatch | Expected→start | Status |
| --- | --- | --- | ---: | ---: | ---: | --- |
| SL-01 / 2026-10-01 | 01:17 | D71 01:20 / 01:22 | 3 | 2 | 5 | observed synthetic |
| SL-02 / 2026-10-02 | 01:17 | D72 01:17 / 01:25 | 0 | 8 | 8 | observed synthetic |
| SL-03 / 2026-10-03 | 01:17 | D73 01:19 / 01:20 | 2 | 1 | 3 | observed synthetic |
| SL-04 / 2026-10-04 | 01:17 | no observed dispatch/start | UNKNOWN | UNKNOWN | UNKNOWN | missing, cause unknown |

Scheduling completeness=observed dispatch3 / expected slots4=75%. Observed dispatch delays n3=[3,0,2], median2, range0–3 phút; queue n3=[2,8,1], median2, range1–8 phút; expected→start n3=[5,8,3], median5, range3–8. Không đưa SL-04 delay=0 hay timestamp giả; completeness chưa runtime business pass. Owner đề xuất CI maintainer xác minh default branch/gates/event/run service; không tự gán cause feature branch ở slot này (CI-57 chỉ scenario riêng).

## Audit từng AI draft claim

| Claim | Source refs | Supported / unsupported / unknown | Corrected wording |
| --- | --- | --- | --- |
| Agent production-ready | Cohort synthetic n10, all rows + U1/CI limitations | UNSUPPORTED | Chỉ design/fixture analysis; missing execution/evidence/cleanup/usage cần pilot evidence |
| All completed tests passed eventually | E04,E09 failed; executed8 | UNSUPPORTED | 6/8 eventual pass, 2/8 failed; E06/E07 excluded executed nhưng retained selected |
| Retries resolved flaky root cause | E02,E05 flaky-pass; E04 failed after2 | UNSUPPORTED cause; observed retry outcomes supported | 2 pass-after-retry; root cause/fix UNKNOWN, extra attempts3 |
| CI ran every night on time | SL-01/03 dispatch delayed, SL-04 missing; SL-02 queue8 | UNSUPPORTED | Observed dispatch3/4; dispatch delay0–3, queue1–8 phút; missing cause UNKNOWN |
| Cost below budget | E08 usage missing, subtotal0.89 budget1.20 | UNKNOWN actual total | Known subtotal0.89, full cost UNKNOWN; forecast E07 also UNKNOWN |
| Missing usage is zero | E08 calls1/usage missing | UNSUPPORTED | Missing model charge UNKNOWN, không zero |
| Cleanup complete | E04 failed, E08 unknown | UNSUPPORTED | Success4/6; two unresolved outcomes |
| All security coverage done vì Viewer cannot click Create | LAB-AOCE-04 UI contract; no backend contract | UNSUPPORTED | UI disabled/not-found design fixture coverage; backend security Not specified |

## Review decisions và evidence limits

| Finding/proposal | Source | Quyết định đề xuất |
| --- | --- | --- |
| Draft subtotal0.99 | Sum 10 row values | ACCEPT correction **0.89**; Decimal output reproduces |
| Exclude E08 khỏi full-evidence-pass denominator do cleanup unknown | Evidence full rubric + dictionary | REJECT cho metric này; denominator5, cleanup issue riêng; không gọi operationally clean |
| Thêm SL-04 như failed case | Schedule packet no selected list | REJECT; separate schedule denominator4 |
| 0.89<1.20 chứng minh budget guard E07 đúng | E07 note/E08 usage | REJECT; thiếu forecast inputs và total |

Actual local checks: arithmetic, row IDs, delays, links trong [validation report](../../evidence/validation-report.md); không live telemetry. Next evidence/owners/dates: [risk register](U7_risk-register.md), [sprint memo](U7_sprint-review.md). Human review còn pending.
