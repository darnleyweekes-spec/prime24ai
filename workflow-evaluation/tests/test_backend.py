import threading
import httpx
import pytest
from lead_eval.server import make_server
from lead_eval.prime24 import assessment_to_inquiry


@pytest.fixture
def api(db):
    server=make_server(db,port=0)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    with httpx.Client(base_url=f'http://127.0.0.1:{server.server_port}',timeout=5,trust_env=False) as client:
        yield client
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def test_http_backend_intake_duplicate_approval_and_retrieval(api,cases):
    assert api.get('/health').json()['sends_messages'] is False
    response=api.post('/api/leads',json={'inquiry':cases[0]['inquiry']})
    assert response.status_code==201
    result=response.json()
    assert result['mode']=='fixture' and result['status']=='pending_approval'
    id=result['id']
    assert api.get(f'/api/leads/{id}').json()['extraction']['service']=='plumbing'
    assert api.post('/api/leads',json={'inquiry':cases[0]['inquiry']}).json()['status']=='duplicate'
    assert api.post(f'/api/leads/{id}/approve',json={'staff':'Reviewer','confirmed':False}).status_code>=400
    approved=api.post(f'/api/leads/{id}/approve',json={'staff':'Reviewer','confirmed':True})
    assert approved.status_code==200 and approved.json()['status']=='approved'
    assert api.post(f'/api/leads/{id}/approve',json={'staff':'Other','confirmed':True}).status_code==409
    assert api.get(f'/api/leads/{id}').json()['approved_by']=='Reviewer'


def test_http_backend_rejects_bad_requests_and_cross_origin(api):
    assert api.post('/api/leads',content='{broken',headers={'Content-Type':'application/json'}).status_code==400
    assert api.post('/api/leads',json={'inquiry':'short'}).json()['status']=='invalid'
    assert api.post('/api/leads',json={'inquiry':'fictional inquiry'},headers={'Origin':'https://untrusted.example'}).status_code==403
    assert api.get('/health',headers={'Host':'untrusted.example'}).status_code==403
    assert api.post('/api/leads',json={'inquiry':'fictional inquiry','extra':'ignored?'}).status_code==400
    assert api.post('/api/leads',json={'inquiry':'fictional inquiry','assessment':{}}).status_code==400
    assert api.get('/api/leads/'+'0'*32).status_code==404


def test_http_backend_live_without_credentials_is_explicit(api,monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    response=api.post('/api/leads',json={'inquiry':'fictional inquiry','mode':'live'})
    assert response.status_code==503 and response.json()['error']=='live_not_configured'


def test_prime24_adapter_preserves_existing_intake_fields():
    text=assessment_to_inquiry({'name':'Alex Example','email':'alex@example.com','company':'Fictional Ltd',
                                'workflow':'Plumbing help today at 101 Fiction Lane','service':'Free workflow review'})
    assert 'Customer inquiry: Plumbing help today' in text
    assert 'Prime24AI offer selected: Free workflow review' in text
    with pytest.raises(ValueError): assessment_to_inquiry({'password':'not allowed'})


def test_http_approval_does_not_coerce_numeric_confirmation(api,cases):
    id=api.post('/api/leads',json={'inquiry':cases[0]['inquiry']}).json()['id']
    assert api.post(f'/api/leads/{id}/approve',json={'staff':'Reviewer','confirmed':1}).status_code==400
    assert api.get(f'/api/leads/{id}').json()['status']=='pending_approval'
