# AIQE — Agent Optimization & CI Execution

Bắt đầu ở [đề bài](../L3_AIQE_AOCE_exercises_vi.md), sau đó mở [mục lục bài nộp](../submission/ASSIGNMENTS.md). [Báo cáo live mới nhất](../submission/live/recovery/README.md) tập hợp scheduled run GitHub, force-cancel/watchdog và quyết định dùng GitHub làm lịch chính.

| Bạn cần xem | Mở ở đây |
| --- | --- |
| Đề bài gốc | [L3_AIQE_AOCE_exercises_vi.md](../L3_AIQE_AOCE_exercises_vi.md) |
| Nội dung khóa học | [L3_AIQE_AOCE_course_content_vi.md](../L3_AIQE_AOCE_course_content_vi.md) |
| Bài giải 7 lab / 17 file | [bai-nop-AOCE/labs](../submission/labs/README.md) |
| Kiểm tra bài giải, tính toán và nguồn | [bai-nop-AOCE/evidence](../submission/evidence/README.md) |
| Kết quả live và bằng chứng | [bai-nop-AOCE/live](../submission/live/README.md) |
| Source webapp và tests | [aoce-live-lab](../README.md) |

```text
AIQE Agent Optimization & CI Execution/
├── README.md                         ← mục lục workspace
├── L3_AIQE_AOCE_exercises_vi.md       ← đề bài gốc
├── L3_AIQE_AOCE_course_content_vi.md  ← tài liệu gốc
├── bai-nop-AOCE/                     ← bài nộp local
│   ├── README.md
│   ├── labs/                         ← U1–U7, mỗi lab một folder
│   ├── evidence/                     ← tính toán, nguồn, validation
│   ├── review/                       ← bản phân tích và review log
│   ├── tools/                        ← công cụ kiểm tra bài giải
│   └── live/                         ← AI, CI, recovery, runs
└── aoce-live-lab/                    ← repo Git của app/test project
```

`bai-nop-AOCE` là bản bài nộp làm việc tại máy. `aoce-live-lab/submission` là bản đã xuất bản trong repo Git; cấu trúc của bản này thuộc lịch sử commit riêng. Thư mục app giữ nguyên đường dẫn để server, scripts và gate kiểm tra SHA tiếp tục hoạt động.

Bài nộp trên GitHub: [bản chính](https://github.com/huyduong20102004/aoce-live-lab/tree/main/submission), [bằng chứng bổ sung](https://github.com/huyduong20102004/aoce-live-lab/tree/evidence/recovery-schedule-20261013/submission/remaining-checks).

Từ thư mục workspace, kiểm tra bài giải bằng `python bai-nop-AOCE/tools/validate.py`; kiểm tra bằng chứng mới nhất bằng `python bai-nop-AOCE/live/recovery/tools/validate_remaining.py`.
