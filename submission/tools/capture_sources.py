"""Capture immutable input file hashes. Refuse to overwrite an existing snapshot."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'evidence/source-manifest.json'
SOURCES = ['L3_AIQE_AOCE_exercises_vi.md', 'L3_AIQE_AOCE_course_content_vi.md']
REFS = {
    'SRC-GH-EVENTS': 'https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows',
    'SRC-GH-CONCURRENCY': 'https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency',
    'SRC-GH-SECRETS': 'https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets',
    'SRC-PW-CI': 'https://playwright.dev/docs/ci-intro',
    'SRC-PW-RETRY': 'https://playwright.dev/docs/test-retries',
    'SRC-PW-WAIT': 'https://playwright.dev/docs/actionability',
    'SRC-PW-ASSERT': 'https://playwright.dev/docs/test-assertions',
    'SRC-PW-FRAME': 'https://playwright.dev/docs/frames',
    'SRC-ACTION-CHECKOUT': 'https://github.com/actions/checkout',
    'SRC-ACTION-SETUP-NODE': 'https://github.com/actions/setup-node',
    'SRC-ACTION-UPLOAD-ARTIFACT': 'https://github.com/actions/upload-artifact',
}

if __name__ == '__main__':
    if TARGET.exists():
        raise SystemExit('Snapshot already exists; not overwriting provenance.')
    result = {
        'schema_version': 'aoce-source-snapshot-1',
        'captured_date': '2026-10-07', 'timezone': 'UTC+7',
        'capture_type': 'local_file_hashes_and_official_docs_read_by_AI',
        'data_label': 'SYNTHETIC / SIMULATED',
        'file_version_note': 'Source documents do not declare a file version; SHA-256 identifies the snapshot.',
        'files': [],
        'packets': {
            'common': ['REQ-PACKET-AOCE', 'POLICY-PACKET-AOCE'],
            'U1': ['BENCH-PACKET-01', 'OUTPUT-PACKET-01', 'RATE-SYN-01'],
            'U2': ['CONTEXT-PACKET-02', 'REG-PACKET-02'],
            'U3': ['FLOW-PACKET-03'], 'U4': ['GIT-PACKET-04'],
            'U5': ['CI-PACKET-05', 'course-content Unit 5 scaffold'],
            'U6': ['INCIDENT-PACKET-06', 'RET-PACKET-06'],
            'U7': ['METRIC-PACKET-07', 'schedule monitoring packet'],
        },
        'declared_fragment_versions': {'CTX-01':'contract v1','CTX-02':'policy v1','current_UI':'r02/ui-12','previous_UI':'r01/ui-11'},
        'undeclared_packet_versions_and_exact_fragment_timestamps': 'Not specified; use containing file snapshot, not invented values.',
        'official_reference_checked_date': '2026-10-07',
        'official_references': REFS,
        'unavailable_local_references': ['L3_AIQE_PMLM_course_content_vi.md', 'L3_AIQE_AAALE_course_content_vi.md'],
        'unavailable_reference_note': 'Inherited AC-EMP-01/02 are used as supplied in AOCE REQ packet; missing prerequisite course files not invented.',
    }
    for name in SOURCES:
        raw = (ROOT.parent/name).read_bytes()
        result['files'].append({'path':'../../'+name,'name':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    TARGET.parent.mkdir(exist_ok=True)
    TARGET.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Captured input snapshot:', ', '.join(SOURCES))
