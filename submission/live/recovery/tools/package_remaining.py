"""Prepare curated proof for an evidence branch without changing tested runtime main."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
PUB = WORKSPACE / 'aoce-live-lab/submission/remaining-checks'
SHA = 'c27f9b8eff44a4875f2922831890dc8d8abf1851'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

result = read(ROOT / 'validation-results.json')
assert result['status'] == 'VERIFIED' and result['failed'] == 0 and not result['pending']
run = read(ROOT / 'scheduled-run.json')
state = read(ROOT / 'scheduler-final-state.json')
assert run['event'] == 'schedule' and run['head_sha'] == SHA
failed = WORKSPACE / 'aoce-live-lab/.lab/runs/cancel-mv63ymwj-83bc5d/cancellation-drill.json'
shutil.copy2(failed, ROOT / 'cancellation-initial-attempt.json')

report = f'''# Hoàn tất ba kiểm chứng còn thiếu — 13/10/2026

Revision thực thi: `{SHA}` trên `main`. Bằng chứng bổ sung được publish ở branch `evidence/recovery-schedule-20261013`; commit chứa báo cáo không được gọi là revision đã chạy tests. Main giữ nguyên SHA đã manual/scheduled validation để gate lịch không bị mất hiệu lực.

| Mục | Kết quả thực tế | Bằng chứng |
| --- | --- | --- |
| GitHub scheduled event | **SUCCESS**, API `event=schedule`; smoke F01–F03 3/3, cleanup resolved, evidence COMPLETE | [Run {run['id']}]({run['html_url']}), [manifest](hosted-scheduled/manifest.json), [REST snapshot](scheduled-run.json) |
| Force-cancel + watchdog | **RECOVERY-VERIFIED**, 7/7 controls; worker bị SIGKILL sau đúng một owned write; watchdog riêng phục hồi sau khi lease thực tế hết hạn | [Drill](../runs/cancel-mv63z50h-ec1f9a/cancellation-drill.json), [watchdog](../runs/cancel-mv63z50h-ec1f9a/watchdog.json), [cleanup](../runs/cancel-mv63z50h-ec1f9a/cleanup.json) |
| Windows schedule | Nguyên nhân máy ngủ qua mốc chạy được xác minh; đã tắt task lab local và dùng GitHub làm lịch chính | [System events/config](windows-diagnosis.json), [đối chiếu từng slot](windows-slot-analysis.json), [trạng thái đã tắt](windows-retired.json) |

## Lịch GitHub

Scheduled run này được GitHub timer tạo từ cron kiểm chứng `*/5 * * * *`, gọi cùng smoke workflow và cùng revision với [manual run 38340873990](https://github.com/huyduong20102004/aoce-live-lab/actions/runs/38340873990). Không dùng workflow_dispatch hoặc biến event giả làm bằng chứng lịch. Ba screenshots xuất bản được kiểm hash theo manifest.

Sau khi lấy bằng chứng, workflow kiểm chứng tạm đã `disabled_manually`, biến `AOCE_VERIFY_SCHEDULE_ENABLED=false`. Daily workflow vẫn active, `AOCE_SCHEDULE_ENABLED=true`, manual-validated SHA khớp main. [Trạng thái GitHub cuối](scheduler-final-state.json).

Lịch chính giữ `17 18 * * *` UTC = **01:17 giờ Việt Nam**. Slot daily 14/10/2026 01:17 là lần chạy tương lai, chưa được đánh dấu đã chạy. Bằng chứng ở đây xác nhận scheduled event thực tế và đường thực thi của workflow; chưa chứng minh độ ổn định nhiều ngày. GitHub có thể trì hoãn hoặc bỏ lịch khi tải cao theo [tài liệu schedule](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

## Force-cancel và phạm vi phục hồi

Worker PID3340 đã commit một employee owned, bị supervisor PID6596 force-kill. Record vẫn tồn tại và cleanup trong worker không chạy. Watchdog PID12372 từ chối xóa khi lease còn hoạt động. Sau deadline do server cấp, watchdog PID16436 chạy độc lập, xóa đúng ID được cấp, giải phóng lease và xác minh record không còn. EMP-1001 không thuộc run được giữ nguyên; số writes=1; chạy watchdog lại bỏ qua run đã released.

Đây là hủy process local thật trong môi trường app lưu state, với cleanup ở process ngoài worker bị hủy. Chưa chứng minh phục hồi sau khi toàn bộ GitHub VM/app ephemeral bị hủy. Victim manifest vẫn **CANCELLED**, business assertion **NOT_EXECUTED**; phục hồi thành công không đổi verdict business thành pass.

[Lần thử đầu](cancellation-initial-attempt.json) FAILED/UNKNOWN vì server chưa chạy (`fetch failed`), trước mọi write; giữ riêng để không che lịch sử. Sau khi khởi động server lab, lần thử có write/cancel/recovery nêu trên thành công. Full browser suite cùng revision có 11/11 cases passed, cleanup33 owned IDs resolved: [manifest](../runs/mv642583-879ae7b4/manifest.json).

## Windows

System Power-Troubleshooter ghi máy ngủ từ 11/10 23:26 đến 13/10 08:07 giờ Việt Nam, bao phủ cả slot 12/10 và 13/10 lúc01:17. Các interval khác cũng bao phủ slot10/10 và11/10. Task có `WakeToRun=false`, `StartWhenAvailable=true`, `LogonType=Interactive`. Invocation10/10 21:36,11/10 08:43 và13/10 08:11 xuất hiện khoảng ba phút sau máy thức.

Bằng chứng này xác định máy không thức ở các slot và phù hợp với cơ chế chạy bù; không khẳng định mỗi invocation là ánh xạ duy nhất của từng slot. TaskScheduler Operational log vốn disabled, nên dispatch detail lịch sử và evidence ngày12/10 không thể phục dựng thành một run đã xảy ra. [Microsoft StartWhenAvailable](https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings-startwhenavailable) mô tả chạy sau thời điểm dự kiến; [Interactive logon](https://learn.microsoft.com/en-us/windows/win32/taskschd/principal-logontype) cần user đã đăng nhập.

Đã tắt duy nhất task `AOCE-PortalLite-Live-Smoke` sau khi kiểm tra description xác nhận ownership và GitHub scheduled run đã thành công. Definition task được giữ để có thể bật lại; các task và cấu hình Windows khác không thay đổi. GitHub là scheduler chính nên việc máy local ngủ không chặn daily hosted run.

## Kiểm chứng bộ bằng chứng

[Validator](tools/validate_remaining.py) xác minh API/manifest/SHA/runID, ba assertions thật, hashes screenshots, cleanup, ranh giới lease, process riêng, verdict CANCELLED và trạng thái hai scheduler. [Kết quả](validation-results.json): **{result['passed']}/{result['passed']} passed**, failed0, pending0. Đây là checks nhất quán bằng chứng, tách khỏi 7 controls của cancellation drill và 11 browser tests.

Chạy từ workspace: `python bai-nop-AOCE/live/recovery/tools/validate_remaining.py`. Trong bản publish: `python submission/remaining-checks/recovery/tools/validate_remaining.py`.

Không publish .env, auth state, recovery grant/token, raw trace hay raw CLI streams. Chi phí monetary vẫn UNKNOWN khi không có hóa đơn/rate thật; packets UNKNOWN trong đề giữ nguyên.
'''
(ROOT / 'README.md').write_text(report, encoding='utf-8')
PUB.mkdir(parents=True, exist_ok=True)
recovery = PUB / 'recovery'
recovery.mkdir(exist_ok=True)
for name in ['README.md', 'windows-diagnosis.json', 'windows-slot-analysis.json', 'windows-retired.json',
             'scheduler-final-state.json', 'validation-results.json', 'cancellation-initial-attempt.json',
             'local-state-verification.json']:
    shutil.copy2(ROOT / name, recovery / name)
for name in ['manual-run.json', 'scheduled-run.json']:
    api = read(ROOT / name)
    safe = {k: api[k] for k in ['id', 'run_attempt', 'event', 'status', 'conclusion', 'head_sha',
                                'html_url', 'created_at', 'updated_at', 'run_started_at']}
    safe['source'] = f"https://api.github.com/repos/huyduong20102004/aoce-live-lab/actions/runs/{api['id']}"
    (recovery / name).write_text(json.dumps(safe, indent=2) + '\n', encoding='utf-8')
for folder in ['hosted-manual', 'hosted-scheduled']:
    shutil.copytree(ROOT / folder, recovery / folder, dirs_exist_ok=True)
(recovery / 'tools').mkdir(exist_ok=True)
shutil.copy2(ROOT / 'tools/validate_remaining.py', recovery / 'tools/validate_remaining.py')
for run_id in ['cancel-mv63z50h-ec1f9a', 'mv642583-879ae7b4']:
    source = ROOT.parent / 'runs' / run_id
    target = PUB / 'runs' / run_id
    target.mkdir(parents=True, exist_ok=True)
    for file in source.iterdir():
        if file.suffix in {'.json', '.png'}:
            shutil.copy2(file, target / file.name)
(PUB / 'README.md').write_text('# Bằng chứng bổ sung còn thiếu\n\n'
    '[Báo cáo và bằng chứng cho cả ba mục](recovery/README.md). '
    f'Revision thực thi `{SHA}`; branch này chỉ bổ sung evidence.\n', encoding='utf-8')

for file, link in [(WORKSPACE / 'bai-nop-AOCE/README.md', 'live/recovery/README.md'),
                   (ROOT.parent / 'README.md', 'recovery/README.md'),
                   (ROOT.parent / 'ci/README.md', '../recovery/README.md')]:
    text = file.read_text(encoding='utf-8')
    marker = '**Cập nhật kiểm chứng 13/10/2026:**'
    if marker not in text:
        first, remainder = text.split('\n', 1)
        text = first + '\n\n' + marker + ' đã có scheduled event GitHub thật, cancellation/watchdog 7/7 và chẩn đoán Windows; GitHub là lịch chính, task local đã tắt. '
        text += f'[Báo cáo mới nhất]({link}). Các trạng thái pending và SHA cũ bên dưới là snapshot lịch sử.\n' + remainder
        file.write_text(text, encoding='utf-8')
print(json.dumps({'prepared': str(PUB), 'tested_revision': SHA, 'scheduled_run': run['html_url']}))
