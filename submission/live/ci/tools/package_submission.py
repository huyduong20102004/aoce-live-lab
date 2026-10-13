"""Bounded publication bundle: answers + curated evidence, never raw auth/trace/CLI stderr."""
from pathlib import Path
import json
import os
import re
import shutil
import hashlib
from datetime import datetime, timezone

WORK=Path(__file__).resolve().parents[4]
SOURCE=WORK/'bai-nop-AOCE'
LAB=WORK/'aoce-live-lab'
DEST=LAB/'submission'
files={}
if DEST.exists():
    raise RuntimeError('Publication bundle already exists; refusing any partial overwrite')
def add(file):
    if not file.is_file(): return
    relative=file.relative_to(SOURCE)
    target=DEST/relative
    if target.exists(): raise RuntimeError('Refuse to overwrite a previous publication bundle: '+str(relative))
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(file,target); files[file.resolve()]=target
for file in (SOURCE/'labs').rglob('*'):
    if file.suffix in ['.md','.csv','.ts','.yml']: add(file)
add(SOURCE/'README.md')
for sub in ['review','evidence','tools']:
    for file in (SOURCE/sub).rglob('*'):
        if '__pycache__' not in file.parts and file.suffix in ['.md','.json','.csv','.py','.txt'] and 'initial-attempt' not in file.name: add(file)
for file in (SOURCE/'live').iterdir():
    if file.is_file() and file.suffix in ['.md','.json','.jsonl']: add(file)
for sub in ['local-checks','windows-history']:
    for file in (SOURCE/'live'/sub).iterdir():
        if file.is_file() and file.suffix in ['.md','.json','.jsonl','.txt']: add(file)
for directory in (SOURCE/'live/runs').iterdir():
    for file in directory.iterdir():
        if file.suffix in ['.json','.png']: add(file)
for file in (SOURCE/'live/ai').iterdir():
    if file.is_file() and file.suffix in ['.md','.json','.csv']: add(file)
for file in (SOURCE/'live/ai/inputs').iterdir():
    if file.suffix in ['.json','.txt','.md']: add(file)
for directory in (SOURCE/'live/ai/calls').iterdir():
    for name in ['response.json','measurement.json','review.json']:
        add(directory/name)
for file in (SOURCE/'live/ai/tools').glob('*.py'): add(file)
for file in (SOURCE/'live/tools').glob('*.py'): add(file)
for name in ['L3_AIQE_AOCE_exercises_vi.md','L3_AIQE_AOCE_course_content_vi.md']:
    shutil.copyfile(WORK/name,LAB/name); files[(WORK/name).resolve()]=LAB/name
# Navigation links are relocated, but frozen model input bytes stay exactly as sent.
for original,target in files.items():
    if target.suffix!='.md' or (DEST/'live/ai/inputs') in target.parents or original.parent==WORK: continue
    text=target.read_text(encoding='utf-8-sig')
    def link(match):
        label,url=match.group(1),match.group(2)
        if url.startswith(('http://','https://','mailto:','#')): return match.group(0)
        path,separator,fragment=url.partition('#')
        old=(original.parent/path.strip('<>')).resolve()
        new=files.get(old)
        if new is None and (old==LAB or LAB in old.parents): new=old
        if new is None: return match.group(0)
        relative=os.path.relpath(new,target.parent).replace('\\','/')
        return '['+label+']('+relative+(separator+fragment if separator else '')+')'
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,text)
    target.write_text(text,encoding='utf-8')
# Measurements preserve requested model/input/schema hashes; private machine paths are not navigation.
for file in (DEST/'live/ai').rglob('*.json'):
    if (DEST/'live/ai/inputs') in file.parents: continue
    text=file.read_text(encoding='utf-8-sig')
    text=text.replace(str(WORK).replace('\\','\\\\'),'<original-local-workspace>')
    file.write_text(text,encoding='utf-8')
intro='''# Bài nộp Agent Optimization & CI Execution

Repo gồm source webapp/test project và **17 deliverables cho 7 lab**. Đây là bài làm có AI hỗ trợ; packets synthetic, browser runs LIVE-LOCAL và actual Codex model outputs được tách riêng, không có production-ready claim.

- [Mục lục U1–U7 và bài dry-run](ASSIGNMENTS.md)
- [Actual webapp/controller/recovery evidence](live/README.md)
- [Actual Codex CLI U1/U2 benchmark](live/ai/README.md)
- [GitHub Actions](https://github.com/huyduong20102004/aoce-live-lab/actions)
- [Source app/CI instructions](../README.md)
- [Handout source](../L3_AIQE_AOCE_exercises_vi.md)
- [Course content source](../L3_AIQE_AOCE_course_content_vi.md)

Published evidence includes sanitized manifest/discovery/cleanup/assertion screenshots, structured model responses/usage and review findings. Raw Playwright traces/auth/grants/CLI event streams and stderr remain local, not committed. Original local paths/timestamps in historical records are provenance, not URLs to this repo. Original local validation was run against private raw events; the public bundle is a curated export, not a fabricated rerun.

Scores are the documented analysis rubric, not external grading. Monetary cost remains UNKNOWN under ChatGPT authentication. Local historical scripts may require the original workspace layout/CLI install; source runtime and GitHub CI use the portable scripts at repo root. Sources PMLM/AAALE linked by the original course were not provided; their inherited ACs are used as supplied in the AOCE packet, not recreated.

GitHub hosted CI evidence is added after actual PR/manual runs; a future daily scheduled slot is not marked passed before execution.
'''
shutil.move(DEST/'README.md',DEST/'ASSIGNMENTS.md')
(DEST/'README.md').write_text(intro,encoding='utf-8')
# The old README link was mapped before renaming; fix only document navigation targets.
for file in DEST.rglob('*.md'):
    if (DEST/'live/ai/inputs') in file.parents: continue
    text=file.read_text(encoding='utf-8')
    # Parent links referencing submission README may remain the new index, which is intentional.
    file.write_text(text,encoding='utf-8')
records=[{'path':str(target.relative_to(LAB)).replace('\\','/'),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
    'source_sha256':hashlib.sha256(original.read_bytes()).hexdigest()} for original,target in files.items() if target.exists()]
(DEST/'publication-manifest.json').write_text(json.dumps({'generated_at':datetime.now(timezone.utc).isoformat(),
    'scope':'CURATED PUBLIC SUBMISSION EXPORT','files':records,'raw_auth_trace_cli_logs_published':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Curated submission prepared:',len(records),'files; 17 required outputs copied. Raw auth/trace/CLI logs excluded.')
