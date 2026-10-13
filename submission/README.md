# Bài nộp Agent Optimization & CI Execution

Bài giải gồm **17 file cho 7 lab**, đã gom theo từng thư mục. Source webapp và tests nằm ở root repo.

| Nội dung | Mở ở đây |
| --- | --- |
| Bài giải U1–U7 | [labs](labs/README.md) |
| Mục lục và lịch sử bài nộp | [ASSIGNMENTS.md](ASSIGNMENTS.md) |
| Bằng chứng live mới nhất | [live/recovery](live/recovery/README.md) |
| Benchmark Codex CLI U1/U2 | [live/ai](live/ai/README.md) |
| GitHub PR/manual CI | [live/ci](live/ci/README.md) |
| Runs, assertions và cleanup | [live](live/README.md) |
| Kiểm tra bài giải và nguồn | [evidence](evidence/README.md) |
| Layout workspace local | [WORKSPACE-LAYOUT.md](../docs/WORKSPACE-LAYOUT.md) |
| Source app và hướng dẫn chạy | [README repo](../README.md) |

Giữ riêng packets synthetic, model responses và actual browser/CI evidence. Các source revision trong manifests là revision đã chạy, không phải SHA của commit sắp xếp tài liệu. Phần schedule/cancel/Windows đã được kiểm chứng trên runtime revision c27f9b8eff44a4875f2922831890dc8d8abf1851.

Bản export gồm sanitized manifests, assertions/screenshots/cleanup, structured model responses và usage. Credentials, auth state, grants, raw traces, CLI events/stderr và Python cache nằm ngoài Git. Những scripts kiểm tra/chuẩn bị trong submission lưu workflow của workspace gốc; scripts chạy app/CI portable nằm ở root repo. Không chạy lại benchmark từ dữ liệu public thiếu raw events rồi gọi đó là phép thử mới.
