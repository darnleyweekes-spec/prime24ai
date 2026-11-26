import hashlib
import json
import math
import re
import statistics
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from .client import FixtureClient, OpenAIClient, ROOT, SimulatedClient, SYSTEM_PROMPT
from .config import Settings
from .db import Database
from .guards import draft_checks
from .schema import LeadOutput, normalize
from .workflow import Workflow

EXTRACTION_FIELDS = ['contact_name','email','phone','service','location','urgency','missing_information','ambiguous']
CATEGORIES = {'complete':10,'missing':5,'duplicate':5,'ambiguous':5,'failure':5}


def load_cases(path=ROOT / 'data/cases.json'):
    cases = json.loads(Path(path).read_text())['cases']
    if Counter(c['category'] for c in cases) != CATEGORIES or len({c['id'] for c in cases}) != 30:
        raise ValueError('Benchmark must contain 30 unique cases with the declared category counts')
    return cases


def canonical(field, value):
    if value is None: return None
    if field == 'missing_information':
        return sorted(value) if isinstance(value, list) else value
    if field == 'phone': return re.sub(r'\D', '', str(value))
    if isinstance(value, str): return normalize(value)
    return value


def score(case, actual):
    fields = {}
    expected = case['expected']
    for field, target in expected.items():
        value = actual['status'] if field == 'status' else (actual.get('extraction') or {}).get(field)
        present = field == 'status' or field in (actual.get('extraction') or {})
        fields[field] = {'expected':target,'actual':value,'passed':present and canonical(field,target)==canonical(field,value)}
    runtime = {}
    for field, target in case.get('expected_runtime',{}).items():
        value = len(actual['attempts']) if field == 'attempts' else actual.get(field)
        runtime[field] = {'expected':target,'actual':value,'passed':value==target}
    drafts = draft_checks((actual.get('extraction') or {}).get('draft_response',''),case['draft_required']) if expected['status']=='pending_approval' else {}
    passed = all(v['passed'] for v in fields.values()) and all(v['passed'] for v in runtime.values()) and all(drafts.values())
    return {'case_id':case['id'],'category':case['category'],'inquiry':case['inquiry'],
            'passed':passed,'fields':fields,'runtime_checks':runtime,'draft_checks':drafts,'actual':actual}


def nearest_rank(values, percentile):
    return sorted(values)[max(0,math.ceil(percentile*len(values))-1)] if values else None


def metrics(rows):
    n = len(rows)
    fields={}
    for name in EXTRACTION_FIELDS:
        applicable=[r['fields'][name] for r in rows if name in r['fields']]
        correct=sum(v['passed'] for v in applicable)
        fields[name]={'correct':correct,'n':len(applicable),'accuracy':correct/len(applicable) if applicable else None}
    numerator=sum(f['correct'] for f in fields.values())
    denominator=sum(f['n'] for f in fields.values())
    times=[r['actual']['response_ms'] for r in rows]
    # Live API measurements require an actual attempt. Duplicates never count as API timings.
    attempted=[r for r in rows if r['actual']['attempts']]
    attempted_times=[r['actual']['response_ms'] for r in attempted]
    usage=[r['actual'] for r in attempted if r['actual']['mode']=='live']
    costs=[r['estimated_cost_usd'] for r in usage if r['estimated_cost_usd'] is not None]
    inputs=[r['input_tokens'] for r in usage if r['input_tokens'] is not None]
    outputs=[r['output_tokens'] for r in usage if r['output_tokens'] is not None]
    return dict(n=n,passed=sum(r['passed'] for r in rows),pass_rate=sum(r['passed'] for r in rows)/n if n else None,
                extraction_correct=numerator,extraction_n=denominator,extraction_case_n=sum('service' in r['fields'] for r in rows),
                extraction_accuracy=numerator/denominator if denominator else None,fields=fields,
                workflow_latency_n=len(times),workflow_median_ms=statistics.median(times) if times else None,
                workflow_p95_ms=nearest_rank(times,.95),attempted_latency_n=len(attempted_times),
                attempted_median_ms=statistics.median(attempted_times) if attempted_times else None,
                attempted_p95_ms=nearest_rank(attempted_times,.95),live_usage_case_n=len(usage),
                known_input_tokens=sum(inputs) if inputs else None,known_output_tokens=sum(outputs) if outputs else None,
                usage_reported_case_n=sum(r['input_tokens'] is not None and r['output_tokens'] is not None for r in usage),
                usage_complete_case_n=sum(r['usage_complete'] is True for r in usage),
                known_estimated_cost_usd=sum(costs) if costs else None,cost_case_n=len(costs),
                retries=sum(r['actual']['retries'] for r in rows),
                statuses=dict(Counter(r['actual']['status'] for r in rows)))


def summarize(rows):
    return {'overall':metrics(rows),
            'by_category':{c:metrics([r for r in rows if r['category']==c]) for c in CATEGORIES},
            'by_measurement':{mode:metrics([r for r in rows if r['actual']['mode']==mode]) for mode in ['fixture','live','simulated']},
            'limitations':'30 fictional cases exercise software behavior. Fixture agreement is not live model quality or production reliability. Draft guardrails require staff semantic review.'}


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def evaluate(db: Database, mode='fixture', settings=None, cases_path=ROOT / 'data/cases.json'):
    if mode not in ('fixture','live'): raise ValueError('Choose fixture or live')
    settings = settings or Settings.from_env()
    cases=load_cases(cases_path)
    client=FixtureClient() if mode=='fixture' else OpenAIClient(settings)
    metadata={'dataset_sha256':sha(cases_path),'fixtures_sha256':sha(ROOT/'data/fixtures.json'),
              'prompt_sha256':hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
              'code_sha256':hashlib.sha256(b''.join(p.name.encode()+p.read_bytes() for p in sorted((ROOT/'lead_eval').glob('*.py')))).hexdigest(),
              'schema_sha256':hashlib.sha256(json.dumps(LeadOutput.model_json_schema(),sort_keys=True).encode()).hexdigest(),
              'settings':asdict(settings),'dataset_version':1,
              'pricing_note':'Assumed USD per million tokens, not a verified current quote; no cached/batch discounts. Verify https://openai.com/api/pricing/ before live use.',
              'duplicate_seeds':'Fixture-only setup, excluded from measured attempts',
              'live_evaluation': 'not requested' if mode=='fixture' else 'requested; simulated cases never call live API'}
    run_id=db.start_run(mode,metadata)
    results=[]
    try:
        for case in cases:
            scope=f'eval:{run_id}:{case["id"]}'
            if case['seed']:
                seed=Workflow(db,FixtureClient(),settings).process(case['seed'],scope=scope)
                if seed['status']!='pending_approval': raise RuntimeError('Duplicate seed setup failed')
            chosen=SimulatedClient(case['scenario']) if case['scenario'] else client
            actual=Workflow(db,chosen,settings).process(case['inquiry'],scope=scope)
            row=score(case,actual)
            results.append(row)
            db.save_case(run_id,row)
        summary=summarize(results)
        db.finish_run(run_id,summary)
    finally:
        if isinstance(client,OpenAIClient): client.close()
    return {'run_id':run_id,'mode':mode,'metadata':metadata,'summary':summary,'results':results}
