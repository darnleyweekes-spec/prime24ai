import json
from collections import Counter
from lead_eval.db import Database
from lead_eval.evaluation import CATEGORIES, evaluate


def test_full_benchmark_persists_and_separates_populations(db):
    report=evaluate(db,'fixture')
    summary=report['summary']
    assert Counter(r['category'] for r in report['results'])==CATEGORIES
    assert summary['overall']['passed']==summary['overall']['n']==30
    assert summary['by_measurement']['fixture']['n']==25
    assert summary['by_measurement']['fixture']['extraction_n']==160
    assert summary['by_measurement']['simulated']['n']==5
    assert summary['by_measurement']['simulated']['retries']==3
    assert summary['by_measurement']['live']['n']==0
    assert summary['overall']['known_estimated_cost_usd'] is None
    reopened=Database(db.path)
    assert len(reopened.results(report['run_id']))==30
    run=reopened.runs()[0]
    assert run['finished_at'] is not None
    assert json.loads(run['summary_json'])==summary
    # A second run is isolated, repeatable and retained rather than overwriting history.
    second=evaluate(reopened,'fixture')
    assert second['summary']['overall']['passed']==30 and len(reopened.runs())==2
    assert len(reopened.results(report['run_id']))==30



def test_live_evaluation_without_key_makes_no_run(monkeypatch,db):
    import pytest
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    with pytest.raises(ValueError,match='requires OPENAI_API_KEY'):
        evaluate(db,'live')
    assert db.runs()==[]
