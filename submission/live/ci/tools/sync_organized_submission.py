"""Sync the organized local submission into the existing Git repo on a docs branch."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import shutil
import subprocess

WORK = Path(__file__).resolve().parents[4]
SOURCE = WORK / 'bai-nop-AOCE'
LAB = WORK / 'aoce-live-lab'
DEST = LAB / 'submission'
branch = subprocess.check_output(['git', '-C', str(LAB), 'branch', '--show-current'], text=True).strip()
if branch != 'chore/organize-submission':
    raise RuntimeError('Run this synchronization only on chore/organize-submission')
if not (SOURCE / 'labs/README.md').is_file():
    raise RuntimeError('Organized original workspace required; this is not a portable runtime script')

def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()

layout = json.loads((SOURCE / 'evidence/folder-layout.json').read_text(encoding='utf-8'))
relocated = {}
for item in layout['moved_files']:
    old = DEST / Path(item['from']).relative_to('bai-nop-AOCE')
    new = DEST / Path(item['to']).relative_to('bai-nop-AOCE')
    if not old.resolve().is_relative_to(LAB.resolve()) or not new.resolve().is_relative_to(LAB.resolve()):
        raise RuntimeError('Publication path outside intended repo')
    if old.exists() and new.exists():
        raise RuntimeError('Migration destination collision')
    relocated[old.resolve()] = new.resolve()
for old, new in relocated.items():
    if old.is_file():
        new.parent.mkdir(parents=True, exist_ok=True)
        old.rename(new)

files = {}
def add(file, target=None):
    if not file.is_file():
        return
    if '__pycache__' in file.parts:
        return
    target = target or DEST / file.relative_to(SOURCE)
    if not target.resolve().is_relative_to(LAB.resolve()):
        raise RuntimeError('Unsafe synchronization target')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(file, target)
    files[file.resolve()] = target.resolve()

for directory in ['labs', 'review', 'evidence', 'tools']:
    for file in (SOURCE / directory).rglob('*'):
        if file.suffix in {'.md', '.json', '.csv', '.py', '.txt', '.ts', '.yml'}:
            add(file)
add(SOURCE / 'README.md', DEST / 'ASSIGNMENTS.md')
add(WORK / 'README.md', LAB / 'docs/WORKSPACE-LAYOUT.md')
for file in (SOURCE / 'live').iterdir():
    if file.is_file() and file.suffix in {'.md', '.json', '.jsonl'}:
        add(file)
for directory in ['local-checks', 'windows-history']:
    for file in (SOURCE / 'live' / directory).iterdir():
        if file.suffix in {'.md', '.json', '.jsonl', '.txt', '.xml'}:
            add(file)
for directory in (SOURCE / 'live/runs').iterdir():
    for file in directory.iterdir():
        if file.suffix in {'.json', '.png'}:
            add(file)
for file in (SOURCE / 'live/ai').iterdir():
    if file.is_file() and file.suffix in {'.md', '.json', '.csv'}:
        add(file)
for file in (SOURCE / 'live/ai/inputs').iterdir():
    if file.suffix in {'.md', '.txt', '.json'}:
        add(file)
for directory in (SOURCE / 'live/ai/calls').iterdir():
    for name in ['response.json', 'measurement.json', 'review.json']:
        add(directory / name)
for directory in ['live/ai/tools', 'live/tools']:
    for file in (SOURCE / directory).glob('*.py'):
        add(file)
for directory in ['live/ci', 'live/recovery']:
    for file in (SOURCE / directory).rglob('*'):
        if '__pycache__' in file.parts:
            continue
        if file.suffix in {'.md', '.json', '.py', '.ps1', '.png'}:
            add(file)
for name in ['L3_AIQE_AOCE_exercises_vi.md', 'L3_AIQE_AOCE_course_content_vi.md']:
    add(WORK / name, LAB / name)

def local_target(original):
    original = original.resolve()
    if original in files:
        return files[original]
    if original == SOURCE or original.is_relative_to(SOURCE):
        return DEST / original.relative_to(SOURCE)
    if original == LAB or original.is_relative_to(LAB):
        return relocated.get(original, original)
    return None

for original, target in files.items():
    if target.suffix != '.md' or (DEST / 'live/ai/inputs') in target.parents:
        continue
    if original.parent == WORK and original.name.startswith('L3_'):
        continue  # Preserve original handout/course bytes.
    contents = target.read_text(encoding='utf-8-sig')
    def link(match):
        label, url = match.group(1), match.group(2)
        if url.startswith(('https://', 'http://', 'mailto:', '#')):
            return match.group(0)
        path, separator, fragment = url.partition('#')
        new = local_target(original.parent / path.strip('<>'))
        if new is None:
            return match.group(0)
        relative = os.path.relpath(new, target.parent).replace('\\', '/')
        return '[' + label + '](' + relative + (separator + fragment if separator else '') + ')'
    target.write_text(re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, contents), encoding='utf-8')

# Repair references from existing published snapshots to the relocated answers/logs.
copied_targets = set(files.values())
for file in DEST.rglob('*.md'):
    if file.resolve() in copied_targets or (DEST / 'live/ai/inputs') in file.parents:
        continue
    contents = file.read_text(encoding='utf-8-sig')
    def published_link(match):
        label, url = match.group(1), match.group(2)
        if url.startswith(('https://', 'http://', 'mailto:', '#')):
            return match.group(0)
        path, separator, fragment = url.partition('#')
        referenced = (file.parent / path.strip('<>')).resolve()
        new = relocated.get(referenced)
        if new is None:
            return match.group(0)
        relative = os.path.relpath(new, file.parent).replace('\\', '/')
        return '[' + label + '](' + relative + (separator + fragment if separator else '') + ')'
    changed = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', published_link, contents)
    if changed != contents:
        file.write_text(changed, encoding='utf-8')

# Frozen model inputs retain their bytes. Local-machine paths elsewhere are provenance.
for file in DEST.rglob('*.json'):
    if (DEST / 'live/ai/inputs') in file.parents:
        continue
    contents = file.read_bytes().decode('utf-8')
    changed = contents.replace(str(WORK).replace('\\', '\\\\'), '<original-local-workspace>')
    if changed != contents:
        file.write_bytes(changed.encode('utf-8'))

(DEST / 'README.md').write_text('''# Bài nộp Agent Optimization & CI Execution

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
''', encoding='utf-8')

repo_readme = LAB / 'README.md'
contents = repo_readme.read_text(encoding='utf-8')
marker = '## Bài nộp và bằng chứng'
if marker not in contents:
    contents += '\n' + marker + '\n\n- [Bài giải 7 lab theo folder](submission/labs/README.md).\n- [Bằng chứng live mới nhất](submission/live/recovery/README.md).\n- [Mục lục đầy đủ](submission/README.md).\n'
    repo_readme.write_text(contents, encoding='utf-8')

reverse = {target: original for original, target in files.items()}
# Preserve existing Git bytes when content agrees, and its newline style otherwise.
# This keeps historical evidence intact and avoids formatting-only diffs.
for name in subprocess.check_output(['git', '-C', str(LAB), 'ls-files'], text=True).splitlines():
    original_target = (LAB / name).resolve()
    target = relocated.get(original_target, original_target)
    if not target.is_file() or target.suffix not in {'.md', '.txt', '.py', '.json'} and name != '.gitignore':
        continue
    if (DEST / 'live/ai/inputs') in target.parents or target.name.startswith('L3_AIQE_AOCE_'):
        continue
    previous = subprocess.check_output(['git', '-C', str(LAB), 'show', 'HEAD:' + name])
    current = target.read_bytes()
    if target.suffix == '.json':
        try:
            if json.loads(previous.decode('utf-8-sig')) == json.loads(current.decode('utf-8-sig')):
                target.write_bytes(previous)
                continue
        except json.JSONDecodeError:
            pass
    old_text = previous.decode('utf-8-sig').replace('\r\n', '\n')
    new_text = current.decode('utf-8-sig').replace('\r\n', '\n')
    if old_text == new_text:
        target.write_bytes(previous)
    else:
        if b'\r\n' in previous:
            new_text = new_text.replace('\n', '\r\n')
        target.write_bytes(new_text.encode('utf-8'))

records = []
for file in sorted(DEST.rglob('*')):
    if not file.is_file() or file.name == 'publication-manifest.json':
        continue
    record = {'path': file.relative_to(LAB).as_posix(), 'sha256': sha(file)}
    original = reverse.get(file.resolve())
    if original:
        record['source_sha256'] = sha(original)
    records.append(record)
(DEST / 'publication-manifest.json').write_text(json.dumps({
    'generated_at': datetime.now(timezone.utc).isoformat(), 'scope': 'ORGANIZED CURATED PUBLIC SUBMISSION',
    'runtime_evidence_revision': layout['runtime_revision_unchanged'], 'files': records,
    'raw_auth_trace_cli_logs_published': False}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'branch': branch, 'local_files_synced': len(files), 'published_files': len(records),
                  'runtime_evidence_revision': layout['runtime_revision_unchanged']}))
