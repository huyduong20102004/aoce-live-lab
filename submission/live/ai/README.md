# U1/U2 — benchmark bằng Codex CLI thật

Ngày2026-10-09 (UTC+7). **Đã thực thi model calls**, không dùng các rows giả lập như calls thực tế. CLI0.160.0, requested model `gpt-6.1-sol`, reasoning `high` giữ theo cấu hình đang dùng trên máy; ChatGPT authentication, không sử dụng API key billing. Backend model snapshot không có metadata riêng nên version bên dưới là requested alias, không tự điền revision backend.

Artifacts: [U1 benchmark](U1_actual-benchmark.md), [usage ledger CSV](U1_actual-ledger.csv), [U2 before/after](U2_actual-regression.md), [protocol](protocol.json), [raw results](results.json), [validation](validation.md), [QA review decisions](review-decisions.md).

## Actual cohort

| Nhóm | Actual invocations / input | Kết quả |
| --- | --- | --- |
| U1 | 9 calls: A/B/C mỗi3; cùng actual F01 evidence/schema/model/effort | Hard gates9/9; A10/10 điểm, B/C8/10 do thiếu direct AC IDs trong source_refs |
| U2 original | 16 calls: 8 fixtures ×v1/v3 | Response-quality gates v1=0/8, v3=7/8; diễn giải cụ thể bên dưới |
| Complete positive control | 2 calls, cùng enriched synthetic input cho v1/v3 | Cả2 nhận đúng fixture pass và giữ SIMULATED label |
| Preparation probes | 2 calls, output probe=true | Usage/schema/CLI parser calibration; tách khỏi benchmark cohort |

Tổng29 CLI invocations có thật; one completed turn/invocation được ghi trong raw events. Không suy đây là29 provider HTTP requests vì CLI có thể có internal requests/retries không được xuất. Tất cả actual action tool items=0. Dataset và scripts nằm ngoài repo webapp, source app vẫn SHA `68ae69680f53e68e541813c0f044c5d22067389a` clean.

**U1:** median input A31789, B9302, C9781 tokens. Median CLI time A40.184s, B21.223s, C32.775s. B giảm70.74% input và47.19% CLI time so với A trên n3; C giảm69.23% input. Đây là đo config bundle, không savings production hay nguyên nhân do riêng context. Prompt/context thay đồng thời, all samples chung schema và complete runner evidence, cache/backend/ephemeral cwd là confounders. Mọi output giữ exact employee ID/QA, matching run/attempt/flow/revision và owned cleanup; A nêu trực tiếp AC-EMP-01/02, B/C ít granular hơn. Gate ACCEPT khác với điểm rubric và khác việc AI tự chạy app.

**U2:** trên bộ8 original inputs, v1 trả mode="v1" hoặc "report" thay SIMULATED nên bị reject quality label; các đề xuất hành động phần lớn vẫn conservative, không được suy0/8 là0/8 an toàn. v3 giữ label/policy ở7 negative fixtures. Original RG01 thiếu explicit uniqueness/exact-search identity và revision, cả2 phiên bản đều yêu cầu đọc thêm; UNKNOWN này an toàn, không false pass. Đã tạo **LOCAL-RG-01-COMPLETE** riêng với full synthetic metadata, dùng cùng input cho2 versions; cả2 accepted. Không thay original RG01/không nâng denominator8 lên9 hoặc gọi future app run passed từ synthetic fixture.

Negative controls4/4: mutate actual accepted output thành stale run, wrong department, arbitrary-delete proposal, toast-only oracle; evaluator phải reject. Controls dùng positive output đã được evaluator accept trước mutation, tránh checker luôn reject mà vẫn "pass negatives".

## Units, provenance và execution controls

Usage lấy từ event `turn.completed`, gồm input/cached/output và raw cache-write/reasoning fields. Không ước lượng tokens từ words, không cộng reasoning output lần nữa. `uncached_derived=input_total-cached` là partition của CLI usage, không là invoice. **Tổng tiền/cost per accepted/human QA review minutes vẫn UNKNOWN**; automated-review seconds không thay human QA time. CLI elapsed gồm startup/auth/network/model/serialization, không gọi pure model latency/CI billable minutes.

Shell/unified exec/apps/plugins/hooks/browser/computer/image/multi-agent/web search disabled; read-only sandbox, empty temporary cwd, ephemeral sessions, stdin chỉ selected public/synthetic packets và sanitized actual evidence. Auth cached được CLI tự dùng; không đọc auth payload. Child env removes API-key/base-URL overrides và forced_login_method=chatgpt. Proposed tool names trong U2 JSON chỉ là đề xuất, không executed tool calls. Code-mode-host-unavailable notification được giữ nguyên trong events nhưng không tính như tool call.

No .env/auth/grant/trace payload gửi vào prompt. Validator so sánh secret values tại máy và không log chúng. Original BENCH/REG packets và 17 bài dry-run giữ nguyên phần simulated; CSV actual separate. Schema valid không chứng minh policy compliant; rules/source/positive/negative reviews riêng.

## Reproduce

Từ thư mục workspace:

```powershell
python .\bai-nop-AOCE\live\ai\tools\analyze.py
python .\bai-nop-AOCE\live\ai\tools\validate.py
```

`run.py all` giữ existing call directories, không ghi đè/rerun đến xanh. Khi muốn cohort mới phải version inputs/protocol và output destination riêng. `prepare.py` chỉ dùng trước experiment; không chạy lại để đổi frozen inputs của cohort đã có. Scripts dùng installed Codex CLI Node entrypoint, subprocess shell=false để path chứa space/& không thành shell command. Thư viện jsonschema đã có ở máy; validator không gọi model.

Còn ngoài phạm vi đã thực thi: hosted GitHub CI, force-cancel/watchdog drill và future daily01:17 slot. Daily Windows task vẫn chạy deterministic webapp tests, chưa được thêm model calls. Chi phí billing cần actual export/rate phù hợp nếu muốn số tiền, không dùng RATE-SYN-01 hoặc API price để giả lập hóa đơn ChatGPT.

Nguồn chính thức: [Codex non-interactive](https://learn.chatgpt.com/docs/non-interactive-mode), [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), [authentication](https://learn.chatgpt.com/docs/auth), [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching), đọc2026-10-09. Source code/input hashes và CLI command args trong protocol/calls.
