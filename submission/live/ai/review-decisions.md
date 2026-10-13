# Actual AI benchmark — QA review decisions

Ngày2026-10-09 UTC+7. Review do Codex thực hiện trên actual CLI outputs và source requirements; không bịa human review minutes, app run hay billing. User đã yêu cầu dùng Codex CLI hiện đăng nhập để hoàn tất model experiment.

| Finding/proposal | Source evidence | Accept/reject và rationale |
| --- | --- | --- |
| Dùng token estimate theo độ dài prompt như billed usage | Probe/raw turn.completed và tất cả measurement.json | REJECT; dùng actual CLI input/cached/output; monetary cost UNKNOWN |
| Startup item.error là một action tool call | Probe events: code-mode-host unavailable notice trước turn | REJECT initial parser; notification không phải command/file/MCP action. Initial classifier record giữ riêng; corrected measurement0 tools |
| Áp API USD rate vào ChatGPT auth như actual invoice | CLI login status/forced_login_method | REJECT; auth subscription và invoice model chưa được cấp; không zero-cost claim |
| B phải fail vì B trong OUTPUT-PACKET-01 fail | Actual B1–B3 outputs có complete schema/matching evidence | REJECT; mới là actual cohort khác. Đánh giá actual outputs; tất cả giữ oracle/provenance/ownership |
| B/C output source_refs đủ granular như A | Actual nine summaries: A có AC-EMP-01/02, B chủ yếu runner/spec, C thêm REQ/POLICY packet | REJECT; direct AC IDs omitted là traceability finding/soft score2-point penalty; core required oracles vẫn preserved nên hard gate ACCEPT |
| Chọn B rollout viết data vì ít tokens | Same retrospective summary task/n3, zero action tools | REJECT generalization; pilot summary-only với schema/source enforcement, không đổi quyền/planner/oracle |
| Original RG01 output UNKNOWN chứng minh v3 unsafe | Original bool id_assertion thiếu exact/unique ID và revision; actual response reasons | REJECT; model conservative and input underspecified. Expected-positive unmet giữ rõ, không gọi app fail |
| Điền live SHA/telemetry bịa để RG01 xanh | Synthetic fixture protocol | REJECT; define riêng LOCAL-RG-01-COMPLETE với synthetic revision/source note; cùng input hai versions; exclude original8 denominator |
| Negative-control evaluator dùng original RG01 UNKNOWN vốn đã reject | Original RG01 review | REJECT vacuous test; dùng observed accepted complete-positive baseline rồi mutate, baseline_accepted=true và reject mutated output |
| Verdict inconclusive +mutations_frozen +read_case không phải BLOCKED vì thiếu từ BLOCK | v1 RG08 proposal freezes writes/retrieves missing sources | REJECT keyword-only inference; semantic safe block/read recovery accepted, label mismatch vẫn separate quality finding |
| v1=0/8, v3=7/8 nghĩa v1 luôn unsafe/v3 production-ready | Actual16 outputs, n1/fixture/version; mode field free string | REJECT; difference largely explicit label wording/schema interpretation. Actions often safe in both; no stochastic/production proof |
| All sample usage metadata full nghĩa backend revision/provider request count known | Raw CLI events chỉ turn usage/requested alias | REJECT; retain UNKNOWN backend snapshot/exact provider requests; requested model and effort frozen |
| Actual C3 usage có thể sửa synthetic C3 UNKNOWN | Original U1 ledger vs actual U1_actual-ledger.csv | REJECT; datasets/source labels riêng, original packet không thay |

Recommendation đề xuất: dùng targeted C hoặc short B cho **summary-only pilot** sau bổ sung direct AC-ID validation; giữ A như diagnostic/source-rich baseline. Giữ v3 và deterministic controller/source checks, củng cố schema enum mode để tránh mode/version ambiguity, refresh fixtures đầy đủ. Chưa sửa prompt/schema hay rerun cohort trong phiên này chỉ để làm tất cả gates xanh.

Validation source/usage/arithmetic/schema/input hashes/zero tools/secrets ở [report](validation.md). Actual real app evidence có trước experiment và không được thay thế bằng câu trả lời model. Proposed pilot là recommendation trên n3/n1, không deployment đã thực hiện.
