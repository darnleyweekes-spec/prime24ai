"""Offline replay of saved fact fields. No provider calls or timing measurements."""
import json

from lead_eval.client import ROOT
from lead_eval.evaluation import load_cases, score
from lead_eval.intake import IntakeFacts, prepare


def test_recorded_facts_against_original_benchmark():
    report = json.loads((ROOT / 'reports/verified/live-facts-v2.json').read_text())
    cases = {case['id']: case for case in load_cases()}
    assert len(report['results']) == len(cases) == 30
    assert {row['case_id'] for row in report['results']} == cases.keys()
    original_passes = replay_passes = model_cases = 0
    for row in report['results']:
        case = cases[row['case_id']]
        actual = row['actual'].copy()
        assert row['inquiry'] == case['inquiry']
        original_passes += score(case, actual)['passed']
        if actual['mode'] == 'live' and actual['attempts']:
            model_cases += 1
            assert actual['retries'] == 0
            facts = {key: actual['extraction'][key] for key in IntakeFacts.model_fields}
            actual['extraction'] = prepare(json.dumps(facts), case['inquiry']).model_dump()
        replay_passes += score(case, actual)['passed']
    assert (original_passes, model_cases, replay_passes) == (28, 20, 30)
