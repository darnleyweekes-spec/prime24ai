import pytest
from lead_eval.evaluation import EXTRACTION_FIELDS, metrics, nearest_rank, score


def test_correct_extraction_scores_and_tracks_denominator(cases,workflow):
    result=workflow.process(cases[0]['inquiry'])
    row=score(cases[0],result)
    assert row['passed']
    assert metrics([row])['extraction_n']==8


@pytest.mark.parametrize('field',EXTRACTION_FIELDS)
def test_every_wrong_field_fails_independently(field,cases,workflow):
    actual=workflow.process(cases[0]['inquiry'])
    wrong={'contact_name':'Wrong Person','email':'wrong@example.com','phone':'2025550199','service':'hvac',
           'location':'99 Wrong Lane','urgency':'routine','missing_information':['location'],'ambiguous':True}
    actual['extraction'][field]=wrong[field]
    row=score(cases[0],actual)
    assert not row['passed']
    assert not row['fields'][field]['passed']
    assert metrics([row])['extraction_correct']==7


def test_normalization_and_missing_set_order(cases,workflow):
    actual=workflow.process(cases[2]['inquiry'])
    actual['extraction']['phone']='(202) 555 0103'
    actual['extraction']['contact_name']='  CASEY   DEMO '
    assert score(cases[2],actual)['passed']
    missing=next(c for c in cases if c['id']=='M05')
    result=workflow.process(missing['inquiry'])
    result['extraction']['missing_information'].reverse()
    assert score(missing,result)['passed']


def test_no_extraction_does_not_receive_null_field_credit(cases,workflow):
    actual=workflow.process(cases[0]['inquiry'])
    actual['extraction']=None
    actual['status']='error'
    row=score(cases[0],actual)
    assert metrics([row])['extraction_correct']==0


def test_draft_checks_fail_with_correct_extraction(cases,workflow):
    actual=workflow.process(cases[0]['inquiry'])
    actual['extraction']['draft_response']='You are booked for $100. We will arrive today.'
    assert not score(cases[0],actual)['passed']


def test_wrong_failure_cause_or_retry_count_fails(cases,workflow):
    case=next(c for c in cases if c['id']=='F02')
    actual=workflow.process('unknown fictional inquiry for fixture')
    actual.update(error_code='api_http_401',retries=0)
    assert not score(case,actual)['passed']


def test_percentiles_and_empty_metrics():
    assert nearest_rank([1,2,3,4,100],.95)==100
    assert nearest_rank(list(range(1,21)),.95)==19
    assert metrics([])['pass_rate'] is None
    assert metrics([])['known_estimated_cost_usd'] is None
