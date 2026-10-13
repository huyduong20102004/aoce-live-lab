"""Sequential CLI calls in an empty temp cwd with tools disabled. No shell quoting."""
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import subprocess
import tempfile
import time
import sys
import hashlib

AI=Path(__file__).resolve().parents[1]
INPUT=AI/'inputs'; OUTPUT=AI/'calls'; OUTPUT.mkdir(exist_ok=True)
NODE='C:/Program Files/nodejs/node.exe'
CLI='C:/Users/Admin/AppData/Roaming/npm/node_modules/@openai/codex/bin/codex.js'
PROTOCOL=json.loads((AI/'protocol.json').read_text(encoding='utf-8'))
DISABLED=['shell_tool','unified_exec','apps','plugins','hooks','browser_use','browser_use_external','computer_use','image_generation','multi_agent','goals','memories','skill_search','code_mode_host','remote_plugin','sleep_tool','view_image']
def events(text):
    result=[]
    for line in text.splitlines():
        try: result.append(json.loads(line))
        except json.JSONDecodeError: pass
    return result
def call(identifier,input_file,schema_file,timeout=180):
    destination=OUTPUT/identifier
    if destination.exists():
        print('Retain existing call '+identifier,flush=True)
        return json.loads((destination/'measurement.json').read_text(encoding='utf-8'))
    destination.mkdir()
    prompt=input_file.read_text(encoding='utf-8')
    # No child shell. CLI host writes JSON output; model sandbox is read-only and no tools exposed.
    with tempfile.TemporaryDirectory(prefix='aoce-ai-isolated-') as cwd:
        args=[NODE,CLI,'exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--json','--color','never',
              '-c','approval_policy="never"','-c','forced_login_method="chatgpt"','-c','web_search="disabled"','-c','features.code_mode.enabled=false',
              '--output-schema',str(schema_file.resolve()),'-o',str((destination/'response.json').resolve())]
        if PROTOCOL['requested_model']: args+=['--model',PROTOCOL['requested_model']]
        if PROTOCOL['reasoning_effort']: args+=['-c',f'model_reasoning_effort="{PROTOCOL["reasoning_effort"]}"']
        for feature in DISABLED: args+=['--disable',feature]
        args+=['-']
        started=datetime.now(timezone.utc).isoformat(); clock=time.perf_counter()
        try:
            child_env=os.environ.copy()
            for key in ['CODEX_API_KEY','OPENAI_API_KEY','OPENAI_BASE_URL']: child_env.pop(key,None)
            result=subprocess.run(args,input=prompt,cwd=cwd,env=child_env,encoding='utf-8',capture_output=True,timeout=timeout,shell=False)
            stdout,stderr,code=result.stdout,result.stderr,result.returncode
        except subprocess.TimeoutExpired as e:
            stdout=e.stdout or ''; stderr=e.stderr or ''
            if isinstance(stdout,bytes): stdout=stdout.decode('utf-8',errors='replace')
            if isinstance(stderr,bytes): stderr=stderr.decode('utf-8',errors='replace')
            code=124
        elapsed=time.perf_counter()-clock
    (destination/'events.jsonl').write_text(stdout,encoding='utf-8')
    (destination/'stderr.txt').write_text(stderr,encoding='utf-8')
    parsed=events(stdout)
    completions=[e for e in parsed if e.get('type') in ['turn.completed','thread.completed']]
    usage=[e['usage'] for e in completions if isinstance(e.get('usage'),dict)]
    actual_tools=[e for e in parsed if e.get('type')=='item.completed' and e.get('item',{}).get('type') not in ['agent_message','reasoning','error']]
    notifications=[e['item'].get('message') for e in parsed if e.get('item',{}).get('type')=='error']
    totals={key:sum(u[key] for u in usage) if usage and all(isinstance(u.get(key),int) for u in usage) else None
            for key in ['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens']}
    measurement={'id':identifier,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':elapsed,
      'exit_code':code,'cli_invocations':1,'completed_turns':len(completions),'provider_request_count':'UNKNOWN','actual_tool_items':len(actual_tools),
      'input_file':str(input_file.relative_to(AI)),'input_sha256':hashlib.sha256(input_file.read_bytes()).hexdigest(),
      'schema_sha256':hashlib.sha256(schema_file.read_bytes()).hexdigest(),'requested_model':PROTOCOL['requested_model'],
      'reasoning_effort':PROTOCOL['reasoning_effort'],'usage':totals,'raw_usage_events':usage,
      'usage_status':'COMPLETE' if all(totals[k] is not None for k in ['input_tokens','cached_input_tokens','output_tokens']) else 'MISSING',
      'monetary_cost':'UNKNOWN','actual_model_response':(destination/'response.json').exists(),'tool_policy':'tools_disabled_read_only_isolated_cwd','runtime_notifications':notifications,
      'command':['node','<installed-codex-cli>']+args[2:-1]+['<prompt via stdin>']}
    (destination/'measurement.json').write_text(json.dumps(measurement,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:measurement[k] for k in ['id','exit_code','elapsed_seconds','usage_status','usage','actual_tool_items']},ensure_ascii=False),flush=True)
    if actual_tools: raise RuntimeError('Unexpected actual tool call; halt instead of weakening policy')
    return measurement

if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'all'
    if mode=='probe':
        prompt=INPUT/'probe.txt'; prompt.write_text('Return only JSON with probe=true. No tools or filesystem actions.\n',encoding='utf-8')
        result=call('probe-v2',prompt,INPUT/'probe.schema.json')
        if result['exit_code'] or result['usage_status']!='COMPLETE': sys.exit(1)
    else:
        budget_start=time.perf_counter()
        for identifier in PROTOCOL['U1_order']:
            if time.perf_counter()-budget_start>1800: raise RuntimeError('Experiment wall budget exhausted')
            result=call('U1-'+identifier,INPUT/f'U1-{identifier[0]}.txt',INPUT/'summary.schema.json')
            if result['exit_code']: raise RuntimeError('CLI failure retained; investigate before dependent samples')
        for fixture in PROTOCOL['U2_cases']:
            for version in PROTOCOL['U2_versions']:
                if time.perf_counter()-budget_start>1800: raise RuntimeError('Experiment wall budget exhausted')
                result=call('U2-'+version+'-'+fixture,INPUT/f'U2-{version}-{fixture}.txt',INPUT/'decision.schema.json')
                if result['exit_code']: raise RuntimeError('CLI failure retained; investigate before dependent samples')
