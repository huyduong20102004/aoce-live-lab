"""One-time local layout migration. Preserve runtime repo and immutable evidence bytes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import subprocess

WORK = Path(__file__).resolve().parents[2]
SUB = WORK / 'bai-nop-AOCE'
LIVE = SUB / 'live'
MANIFEST = SUB / 'evidence/folder-layout.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inside(path):
    resolved = path.resolve()
    if not resolved.is_relative_to(WORK.resolve()):
        raise RuntimeError('Path outside intended workspace')
    return resolved

if MANIFEST.exists():
    print('Local layout migration already recorded; no files moved.')
    raise SystemExit(0)

sources = {p.name: digest(p) for p in WORK.glob('L3_AIQE_AOCE_*.md')}
revision = subprocess.check_output(['git', '-C', str(WORK / 'aoce-live-lab'), 'rev-parse', 'HEAD'], text=True).strip()
moves = {}
deliverables = [p for p in SUB.iterdir() if p.is_file() and re.match(r'^U[1-7]_', p.name)]
if len(deliverables) != 17:
    raise RuntimeError('Expected exactly17 deliverables before migration')
for file in deliverables:
    moves[file.resolve()] = SUB / 'labs' / file.name.split('_', 1)[0] / file.name
for file in LIVE.iterdir():
    if not file.is_file():
        continue
    if file.name.startswith('windows-schedule') or file.name in {'schedule-evidence.md', 'scheduler-invocations.jsonl'}:
        moves[file.resolve()] = LIVE / 'windows-history' / file.name
    elif file.name in {'typecheck.txt', 'controller-regression.txt', 'git-evidence.json', 'LIVE_completion-and-review.md'}:
        moves[file.resolve()] = LIVE / 'local-checks' / file.name

# Validate every absolute source/destination before changing any file.
for old, new in moves.items():
    inside(old)
    inside(new)
    if not old.is_file() or new.exists():
        raise RuntimeError('Missing source or destination collision: ' + str(new.relative_to(WORK)))

docs = []
for old in SUB.rglob('*.md'):
    if (LIVE / 'ai/inputs') in old.parents:
        continue  # Frozen model input bytes and archived sources are never navigation migrations.
    docs.append((old.resolve(), moves.get(old.resolve(), old), old.read_text(encoding='utf-8-sig')))
records = []
for old, new in moves.items():
    original_hash = digest(old)
    new.parent.mkdir(parents=True, exist_ok=True)
    old.rename(new)
    records.append({'from': old.relative_to(WORK).as_posix(), 'to': new.relative_to(WORK).as_posix(),
                    'sha256_before': original_hash})

link_changes = 0
for old, new, contents in docs:
    def link(match):
        global link_changes
        label, url = match.group(1), match.group(2)
        if url.startswith(('https://', 'http://', 'mailto:', '#')):
            return match.group(0)
        target, separator, fragment = url.partition('#')
        if not target:
            return match.group(0)
        referenced = (old.parent / target.strip('<>')).resolve()
        relocated = moves.get(referenced, referenced)
        relative = os.path.relpath(relocated, new.parent).replace('\\', '/')
        updated = relative + (separator + fragment if separator else '')
        if target.startswith('<'):
            updated = '<' + relative + '>' + (separator + fragment if separator else '')
        if updated == url:
            return match.group(0)
        link_changes += 1
        return '[' + label + '](' + updated + ')'
    rewritten = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, contents)
    if rewritten != contents:
        new.write_text(rewritten, encoding='utf-8')

# Tools read the same artifacts through their new local locations.
validator = SUB / 'tools/validate.py'
text = validator.read_text(encoding='utf-8')
text = text.replace('checks = []', "checks = []\n\ndef artifact(name):\n    return ROOT / 'labs' / name.split('_', 1)[0] / name\n")
text = text.replace('all((ROOT/p).is_file() for p in EXPECTED)', 'all(artifact(p).is_file() for p in EXPECTED)')
text = re.sub(r"ROOT/'(U[1-7]_[^']+)'", r"artifact('\1')", text)
validator.write_text(text, encoding='utf-8')
calculate = SUB / 'tools/calculate.py'
text = calculate.read_text(encoding='utf-8').replace("ROOT/'U1_cost-ledger.csv'", "ROOT/'labs/U1/U1_cost-ledger.csv'")
calculate.write_text(text, encoding='utf-8')
legacy = LIVE / 'tools/verify-evidence.py'
text = legacy.read_text(encoding='utf-8')
for name in ['typecheck.txt', 'controller-regression.txt']:
    text = text.replace("LIVE/'" + name + "'", "LIVE/'local-checks/" + name + "'")
text = text.replace("LIVE/'windows-schedule-status.json'", "LIVE/'windows-history/windows-schedule-status.json'")
legacy.write_text(text, encoding='utf-8')
package = LIVE / 'ci/tools/package_submission.py'
text = package.read_text(encoding='utf-8')
text = text.replace('files={}\n', "files={}\nif DEST.exists():\n    raise RuntimeError('Publication bundle already exists; refusing any partial overwrite')\n")
text = text.replace("for file in SOURCE.glob('U*'): add(file)",
                    "for file in (SOURCE/'labs').rglob('*'):\n    if file.suffix in ['.md','.csv','.ts','.yml']: add(file)")
text = text.replace("for directory in (SOURCE/'live/runs').iterdir():",
    "for sub in ['local-checks','windows-history']:\n    for file in (SOURCE/'live'/sub).iterdir():\n        if file.is_file() and file.suffix in ['.md','.json','.jsonl','.txt']: add(file)\nfor directory in (SOURCE/'live/runs').iterdir():")
package.write_text(text, encoding='utf-8')

for record in records:
    target = WORK / record['to']
    record['sha256_after'] = digest(target)
    if target.suffix != '.md' and record['sha256_before'] != record['sha256_after']:
        raise RuntimeError('Evidence/source bytes changed unexpectedly')
if sources != {p.name: digest(p) for p in WORK.glob('L3_AIQE_AOCE_*.md')}:
    raise RuntimeError('Original handout/content changed')
MANIFEST.write_text(json.dumps({'scope': 'LOCAL FOLDER ORGANIZATION; NO RUNTIME REPO MUTATION',
    'organized_at': datetime.now(timezone.utc).isoformat(), 'runtime_revision_unchanged': revision,
    'moved_files': records, 'markdown_links_updated': link_changes,
    'original_source_hashes': sources}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'moved_files': len(records), 'deliverables': len(deliverables),
                  'markdown_links_updated': link_changes, 'runtime_revision_unchanged': revision}))
