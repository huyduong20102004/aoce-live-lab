# Actual Windows scheduling evidence

Ngày2026-10-09 UTC+7. Task: **AOCE-PortalLite-Live-Smoke**. Source cuối `68ae69680f53e68e541813c0f044c5d22067389a`. Task registration và observed service status có thật, không manual run giả danh schedule.

## Final revision verification run

| Field | Actual value / source |
| --- | --- |
| Run ID | mv0nhq5q-5bc239db |
| Trigger | windows-schedule; task marker AOCE-PortalLite-Live-Smoke |
| Source SHA | 68ae69680f53e68e541813c0f044c5d22067389a |
| Node manifest started_at | 2026-10-09T07:35:20.824Z (UTC; xem manifest để lấy timestamp đầy đủ) |
| Selected / executed | 3 /3, F01/F02/F03 |
| Outcome / cleanup | RUN-PASSED / resolved, unresolved0 |
| Windows task result | LastTaskResult0; LastRunTime2026-10-09T14:35:35+07:00 |
| Script invocation event | 2026-10-09T14:35:20.6665525+07:00 |

[Manifest](runs/mv0nhq5q-5bc239db/manifest.json), [cleanup](runs/mv0nhq5q-5bc239db/cleanup.json), [Task Scheduler verification status](windows-schedule-verification-final.json), [observed invocation events](scheduler-invocations.jsonl), [one-time trigger XML](windows-schedule-verified-once.xml).

**Timing uncertainty:** Windows LastRunTime ở status snapshot và script/Node timestamp không cùng thứ tự thời gian. Chưa chứng minh nguyên nhân (clock/source/catch-up behavior đều chỉ hypotheses), nên không tính queue/dispatch delay hoặc claim đúng phút từ các timestamps này. Sự kiện task invocation, manifest trigger và service exit0 xác nhận OS-local launch đã chạy; chưa chứng minh timing SLA.

Các lần verification trước ở b4f9af0/d250e70/39902a6 được giữ trong run ledger và event log, tách code revision; không ghép một run revision cũ làm proof revision cuối.

## Daily schedule hiện cấu hình

Target01:17 mỗi ngày, **SE Asia Standard Time UTC+7**. XML daily đã export ở [task definition](windows-schedule.xml); [current service status](windows-schedule-status.json). Lần kế tiếp service báo **2026-10-10 01:17:17 UTC+7**, không hứa chính xác từng giây. Slot ngày2026-10-10 chưa diễn ra, kết quả là **PENDING**, không RUN-PASSED.

Task chạy PowerShell hidden, working directory là lab source, dưới user hiện tại với Interactive logon/Limited run level; max20 phút, IgnoreNew để không chồng task instances, StartWhenAvailable. Máy phải bật và user signed-in; thiếu điều kiện có thể missing/delay. Source thay đổi thì scheduled-entry từ chối nếu manual-validation SHA không khớp; chạy manual smoke mới trước resume schedule.

Task do Codex tạo theo yêu cầu thực thi live lab. Để dừng lịch này, Disable-ScheduledTask đúng tên AOCE-PortalLite-Live-Smoke; không thay task khác. Watchdog owned reconciliation còn có thể cần operator nếu forced termination/runner outage; luôn report unknown/unresolved, không arbitrary delete.

Đây là **Windows Task Scheduler local**, không GitHub Actions. Repo chưa remote, không có actual GitHub run URL và không claim hosted CI schedule fire. Expected daily completeness chỉ bắt đầu khi slot due; không lấy one-time verification4 runs làm4 nightly slots.
