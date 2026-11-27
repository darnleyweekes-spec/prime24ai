import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from lead_eval.client import APIError, FixtureClient, ModelReply, SimulatedClient
from lead_eval.config import Settings
from lead_eval.db import Database
from lead_eval.workflow import Workflow, fingerprint


def test_duplicate_variants_skip_model_and_scopes_are_isolated(cases,db):
    class Counting(FixtureClient):
        calls=0
        def complete(self,text):
            self.calls+=1
            return super().complete(text)
    client=Counting()
    workflow=Workflow(db,client)
    first=workflow.process(cases[0]['inquiry'],scope='one')
    second=workflow.process(cases[0]['inquiry'].upper().replace(' ','  '),scope='one')
    assert second['status']=='duplicate' and second['duplicate_of']==first['id']
    assert second['attempts']==[] and client.calls==1
    assert workflow.process(cases[0]['inquiry'],scope='two')['status']=='pending_approval'
    assert client.calls==2


def test_concurrent_duplicate_claim_allows_one_call(cases,db):
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:Workflow(db,FixtureClient()).process(cases[0]['inquiry']),range(2)))
    assert sorted(r['status'] for r in results)==['duplicate','pending_approval']
    assert sum(len(r['attempts']) for r in results)==1


def test_approval_requires_explicit_review_and_persists(cases,workflow,db):
    result=workflow.process(cases[0]['inquiry'])
    assert result['status']=='pending_approval'
    for staff,confirmed in [('',True),('Reviewer',False),('  ',True)]:
        with pytest.raises(ValueError): db.approve(result['id'],staff,confirmed=confirmed)
    db.approve(result['id'],'Reviewer A',confirmed=True)
    reopened=Database(db.path)
    record=reopened.get_inquiry(result['id'])
    assert record['status']=='approved' and record['approved_by']=='Reviewer A'
    assert json.loads(record['result_json'])['status']=='approved'
    with reopened.connect() as conn:
        assert conn.execute('SELECT COUNT(*) FROM approval_events').fetchone()[0]==1
    with pytest.raises(ValueError): reopened.approve(result['id'],'Reviewer B',confirmed=True)
    assert workflow.process(cases[0]['inquiry'])['status']=='duplicate'


@pytest.mark.parametrize('inquiry',[None,123,'','short','x'*4001,'bad\x00input text','           ','..........'])
def test_invalid_input_makes_no_calls(inquiry,db):
    class NoCalls:
        mode='fixture'
        def complete(self,_): raise AssertionError('Must not call model')
    result=Workflow(db,NoCalls()).process(inquiry)
    assert result['status']=='invalid' and not result['attempts']
    with pytest.raises(ValueError): db.approve(result['id'],'Staff',confirmed=True)


@pytest.mark.parametrize('scenario,status,attempts,retries,code',[
    ('timeout_then_success','pending_approval',2,1,None),
    ('timeout_exhausted','error',3,2,'api_timeout'),
    ('malformed_json','error',1,0,'malformed_output'),
    ('schema_mismatch','error',1,0,'malformed_output'),
    ('permanent_api_error','error',1,0,'api_http_401')])
def test_failure_and_retry_contract(scenario,status,attempts,retries,code,cases,db):
    waits=[]
    client=SimulatedClient(scenario)
    result=Workflow(db,client,sleep=waits.append).process(cases[0]['inquiry'])
    assert (result['status'],len(result['attempts']),result['retries'],result['error_code'])==(status,attempts,retries,code)
    assert client.calls==attempts
    assert waits==[.1,.2][:retries]
    assert result['mode']=='simulated' and result['estimated_cost_usd'] is None
    if status=='error':
        with pytest.raises(ValueError): db.approve(result['id'],'Reviewer',confirmed=True)


def test_failed_attempt_does_not_block_resubmission(cases,db):
    first=Workflow(db,SimulatedClient('malformed_json')).process(cases[0]['inquiry'])
    second=Workflow(db,FixtureClient()).process(cases[0]['inquiry'])
    assert first['status']=='error' and second['status']=='pending_approval'


@pytest.mark.parametrize('change',[
    {'email':'invented@example.com'}, {'contact_name':'Made Up'}, {'missing_information':['location']},
    {'ambiguous':'yes'}, {'service':'roofing'}, {'extra':'forbidden'},
    {'draft_response':'Staff will review. You are booked for $100.'}])
def test_schema_grounding_and_draft_guards_reject(change,cases,db):
    output=json.loads(FixtureClient().complete(cases[0]['inquiry']).text)
    output.update(change)
    class Changed:
        mode='fixture'
        def complete(self,_): return ModelReply(json.dumps(output))
    result=Workflow(db,Changed()).process(cases[0]['inquiry'])
    assert result['status']=='error' and len(result['attempts'])==1
    assert result['extraction'] is None


def test_pricing_counts_malformed_reply_tokens(cases,db):
    class BadLive:
        mode='live'
        def complete(self,_): return ModelReply('{broken',100,50,'test-model')
    result=Workflow(db,BadLive()).process(cases[0]['inquiry'])
    assert result['status']=='error'
    assert result['input_tokens']==100 and result['output_tokens']==50
    assert result['estimated_cost_usd']==pytest.approx(.00012)
    assert result['usage_complete'] is True


def test_timeout_usage_is_unknown_even_after_recovery(cases,db):
    class Recovery:
        mode='live'
        calls=0
        def complete(self,text):
            self.calls+=1
            if self.calls==1: raise APIError('api_timeout',True)
            return ModelReply(FixtureClient().complete(text).text,100,50,'mock-live')
    result=Workflow(db,Recovery(),sleep=lambda _:None).process(cases[0]['inquiry'])
    assert result['status']=='pending_approval' and result['usage_complete'] is False
    assert result['input_tokens']==100


def test_settings_bound_retries_and_timeout():
    for kw in [{'max_retries':3},{'timeout_seconds':0},{'backoff_seconds':3},{'input_usd_per_million':float('nan')}]:
        with pytest.raises(ValueError): Settings(**kw)


def test_unknown_live_usage_is_not_fabricated(cases,db):
    class UnknownUsage:
        mode='live'
        def complete(self,text): return ModelReply(FixtureClient().complete(text).text)
    result=Workflow(db,UnknownUsage()).process(cases[0]['inquiry'])
    assert result['status']=='pending_approval'
    assert result['input_tokens'] is None and result['output_tokens'] is None
    assert result['estimated_cost_usd'] is None and result['usage_complete'] is False

def test_validation_rule_is_persisted_without_model_input(cases, db):
    payload = json.loads(FixtureClient().complete(cases[0]['inquiry']).text)
    payload['email'] = 'private-invalid-value'

    class InvalidEmail:
        mode = 'fixture'

        def complete(self, inquiry):
            return ModelReply(json.dumps(payload))

    result = Workflow(db, InvalidEmail()).process(cases[0]['inquiry'])
    saved = db.get_inquiry(result['id'])['result_json']
    assert json.loads(saved)['error_details'][0]['type'] == 'email_format'
    assert 'private-invalid-value' not in saved
