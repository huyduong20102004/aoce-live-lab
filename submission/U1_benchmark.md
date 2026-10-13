# U1 — Benchmark chất lượng, token và chi phí

Mode: DRY-RUN; kết luận SIMULATED / DESIGN-REVIEWED bởi AI, chưa có human approval.
Sources: REQ-PACKET-AOCE, POLICY-PACKET-AOCE, BENCH-PACKET-01, OUTPUT-PACKET-01, RATE-SYN-01; snapshot và SHA-256 trong [source manifest](evidence/source-manifest.json). Phiên bản bài nộp: aoce-solution-1.
Assumptions/unknowns: chỉ tiền giả lập; không provider/rate thật, live trace hay model calls thật. Bản phân tích đầu và giới hạn manual-first: [draft-1](review/00_analysis-first-draft.md).

## Protocol và fairness

Đóng băng task F01, employee E2E-AOCE-bench, department QA, model M-LAB, toolset-1, EV-bench-1, schema-1, rubric và RATE-SYN-01. Review oracle/provenance/policy trước xem giá; không bỏ output bị reject khỏi cost. Live protocol đề xuất randomize thứ tự A/B/C, ghi cold/warm/cache condition, revision và reviewer, ít nhất ba mẫu/config cùng inputs. Chỉ thay một yếu tố ở vòng thử nhân quả tiếp theo: giữ prompt cố định khi đổi context, rồi giữ context khi đổi prompt.

Confounders: A/B/C đang đổi cả prompt và context; input cache khác nhau; số model/tool calls, CI time khác; review time chịu reviewer/order bias. n=3 synthetic/config không có sampling ngẫu nhiên, không suy confidence interval, production reliability hoặc savings. C3 thiếu usage; không coi hai mẫu C đầy đủ đại diện cho cả config. Tool text/attempts đã tổng hợp trong packet, không cộng lại.

Checklist fairness: cùng task/requirement/oracle/actor/build/tool/evidence/schema/rate; cùng accounting input đã gồm cached; giữ failed và missing rows; matching run evidence; cùng rubric/gates/review method; ghi warm-cache, iteration order, selection và environment; tách test cost/QA minutes; lưu raw permitted usage khi live.

## Chấm output từng sample

Quy ước điểm: oracle đủ ID duy nhất + search ID/department=4; chỉ AC-EMP-01/toast=1. Evidence đủ matching fixture và không live claim=3; toast không chứng minh assertion hoặc cross-run pointer=0. Policy đủ owned cleanup có nguồn=2; ownership đúng nhưng outcome cleanup sai provenance=1; unrestricted cleanup=0. Schema đủ run/config/unknowns/SIMULATED=1; thiếu nhãn hoặc che missing=0. Điểm là đánh giá đề xuất có rationale, không đáp án chấm sẵn.

| Sample | Oracle /4 | Evidence /3 | Policy /2 | Schema /1 | Tổng /10 | Hard gate và nguồn |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| A1 | 4 | 3 | 2 | 1 | 10 | ACCEPT; AC-EMP-01/02, bench-current/EV-bench-1, owned cleanup |
| A2 | 4 | 3 | 2 | 1 | 10 | ACCEPT; cùng card A và matching fixture |
| A3 | 4 | 3 | 2 | 1 | 10 | ACCEPT; cùng card A và matching fixture |
| B1 | 1 | 0 | 0 | 0 | 1 | REJECT; mất department, Flow passed chỉ từ DOM-toast-1, cleanup old employees |
| B2 | 1 | 0 | 0 | 0 | 1 | REJECT; cùng card B, cả ba hard gates fail |
| B3 | 1 | 0 | 0 | 0 | 1 | REJECT; cùng card B, cả ba hard gates fail |
| C1 | 4 | 3 | 2 | 1 | 10 | ACCEPT; AC-EMP-01/02 và EV-bench-1 current |
| C2 | 4 | 3 | 2 | 1 | 10 | ACCEPT; cùng card C1/C2 |
| C3 | 4 | 0 | 1 | 0 | 5 | REJECT; EV-other-1 thuộc bench-previous; claim current pass/cleanup thiếu nguồn, unknown usage bị che |

ACCEPT nghĩa summary đạt gate dựa fixture, không là RUN-PASSED. C3 không được dùng owned cleanup của run cũ như evidence run hiện tại.

## Công thức và ledger

Đơn vị: token, phút CI, giây end-to-end, phút QA, đơn vị tiền giả lập (không USD).

```text
uncached = input_total - cached
model = (uncached*1.00 + cached*0.25 + output*4.00) / 1_000_000
CI = CI_minutes*0.02
measured_total = model + CI + tools(0 theo fixture) + storage(0 theo fixture)
cost_per_accepted = cost của TẤT CẢ samples config / số summaries qua gate
```

| Sample | Uncached | Model cost | CI cost | Total measured |
| --- | ---: | ---: | ---: | ---: |
| A1 | 16000 | 0.026100 | 0.080000 | 0.106100 |
| A2 | 16000 | 0.025575 | 0.082000 | 0.107575 |
| A3 | 17000 | 0.027500 | 0.084000 | 0.111500 |
| B1 | 5000 | 0.008850 | 0.070000 | 0.078850 |
| B2 | 5200 | 0.009250 | 0.072000 | 0.081250 |
| B3 | 5000 | 0.008905 | 0.068000 | 0.076905 |
| C1 | 7000 | 0.012975 | 0.074000 | 0.086975 |
| C2 | 7000 | 0.013100 | 0.076000 | 0.089100 |
| C3 | UNKNOWN | UNKNOWN | 0.078000 | UNKNOWN; lower bound 0.078000 |

[CSV đủ 9 samples](U1_cost-ledger.csv); [tính lại bằng Decimal](tools/calculate.py); [output số liệu](evidence/calculations.json). Không quy QA time ra tiền vì chưa có rate.

## Tổng hợp config

Các ô thống kê ghi median [min–max]; token total=input_total+output, không cộng cached lần nữa.

| Metric | A (n=3) | B (n=3) | C |
| --- | --- | --- | --- |
| Input tokens | 18000 [17500–19000] | 6000 [5900–6200] | n=2 known: 8350 [8200–8500]; full n=3 UNKNOWN |
| Output tokens | 2400 [2300–2500] | 920 [900–950] | n=2 known: 1425 [1400–1450]; full UNKNOWN |
| Total tokens | 20400 [19800–21500] | 6900 [6820–7150] | n=2 known: 9775 [9650–9900]; full UNKNOWN |
| End-to-end giây | 301 [290–318] | 239 [233–245] | n=3: 260 [251–267] |
| QA phút | 9 [8–9] | 12 [11–13] | n=3: 7 [6–8] |
| CI phút | 4.1 [4.0–4.2] | 3.5 [3.4–3.6] | n=3: 3.8 [3.7–3.9] |
| Model calls / tool calls tổng | 9 / 16 | 6 / 9 | 6 / 12 |
| Summaries qua gate | 3/3 | 0/3 | 2/3 |
| Tổng tiền | 0.325175 | 0.237005 | UNKNOWN; known C1/C2=0.176075; all-row lower bound=0.254075 |
| Cost/accepted | 0.108391667 | N/A, mẫu số 0 | UNKNOWN; lower bound=0.1270375 |

## Quyết định pilot

Không chọn B dù token/latency/tiền thấp: required oracle, provenance, ownership không đạt. Đề xuất giữ A làm baseline và sửa C trước pilot hẹp: controller từ chối cross-run refs, bắt buộc missing usage flags và matching cleanup evidence. C có median latency/QA tốt hơn trên fixture và C1/C2 rẻ hơn từng mẫu A, nhưng **all-row cost/accepted lower bound C đã cao hơn A**, nên không tuyên bố config C tiết kiệm overall. Sau sửa cần cohort mới, không ghi đè C3 hoặc tái chấm C3 thành accept.

Owner đề xuất: QA benchmark; evidence tiếp theo: ≥3 actual usage/output mẫu/config được cấp phép, cùng protocol, provider/rate/version, gate logs và accounting đầy đủ. Điều kiện dừng: oracle/policy/provenance fail hoặc missing usage không được hiển thị.

## Review log và validation

| Finding/proposal | Source | Quyết định đề xuất và rationale |
| --- | --- | --- |
| Tính C cost/accepted từ C1/C2 thôi | C3, RATE-SYN-01 | REJECT; tử số phải gồm cả rejected sample, C3 chỉ CI known |
| Gán cached rate cho toàn input rồi cộng uncached | BENCH-PACKET-01 | REJECT; input_total đã gồm cached; dùng partition không chồng |
| B schema phải 0, không 1 | OUTPUT-PACKET-01 và rubric schema/label | ACCEPT; JSON fields không đủ khi thiếu nhãn synthetic và unknowns |
| Token giảm chứng minh production saving do context | BENCH-PACKET-01 | REJECT; synthetic n nhỏ, prompt/context confounded và cost/accepted khác |

Validation local: [report](evidence/validation-report.md) kiểm tra arithmetic/CSV/links và tài liệu; không có model/app runtime. Human manual-first và independent review còn thiếu, ghi rõ ở README.

## Bổ sung actual model benchmark — 2026-10-09

Đã chạy Codex CLI0.160.0/ChatGPT, requested gpt-6.1-sol/high, A/B/C mỗi3 samples, cùng actual F01 evidence/schema. [Actual benchmark](live/ai/U1_actual-benchmark.md), [CSV actual usage](live/ai/U1_actual-ledger.csv), [raw protocol](live/ai/protocol.json). Median input A31789/B9302/C9781; median CLI seconds40.184/21.223/32.775. Hard gates9/9, A score10, B/C score8 vì source_refs thiếu direct AC IDs. Monetary totals/cost per accepted UNKNOWN, human QA time UNKNOWN; không dùng token estimate/API rate như invoice ChatGPT.

Đây là cohort mới, không sửa9 BENCH-PACKET-01 samples hoặc simulated C3 missing usage. Context/prompt confounded, n3, protected schema/current evidence nên actual B có thể đạt gate dù simulated B cards fail. [Review decisions](live/ai/review-decisions.md), [actual validation](live/ai/validation.md).
