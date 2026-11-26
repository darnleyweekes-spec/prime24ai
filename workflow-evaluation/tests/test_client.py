import json
import httpx
import pytest
from lead_eval.client import APIError, OpenAIClient
from lead_eval.config import Settings


@pytest.mark.parametrize('status,transient',[(408,True),(429,True),(500,True),(503,True),(401,False),(400,False)])
def test_http_error_classification_is_sanitized(monkeypatch,status,transient):
    monkeypatch.setenv('OPENAI_API_KEY','fake-key-for-transport-test')
    def respond(request): return httpx.Response(status,json={'error':{'message':'sensitive upstream text'}})
    client=OpenAIClient(Settings(),transport=httpx.MockTransport(respond))
    try:
        with pytest.raises(APIError) as error: client.complete('fictional inquiry')
        assert error.value.code==f'api_http_{status}'
        assert error.value.transient is transient
        assert 'sensitive' not in str(error.value)
    finally: client.close()


def test_timeout_is_transient_and_request_has_strict_schema(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','fake-key-for-transport-test')
    def timeout(request):
        body=json.loads(request.content)
        assert body['response_format']['json_schema']['strict'] is True
        assert body['response_format']['json_schema']['schema']['additionalProperties'] is False
        assert request.extensions['timeout']['read']==1.25
        assert request.url==httpx.URL('https://api.openai.com/v1/chat/completions')
        raise httpx.ReadTimeout('private provider detail',request=request)
    client=OpenAIClient(Settings(timeout_seconds=1.25),transport=httpx.MockTransport(timeout))
    try:
        with pytest.raises(APIError,match='api_timeout') as error: client.complete('fictional inquiry')
        assert error.value.transient
    finally: client.close()


def test_provider_usage_and_model_are_preserved(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','fake-key-for-transport-test')
    response={'choices':[{'message':{'content':'{not JSON'}}], 'usage':{'prompt_tokens':123,'completion_tokens':45},'model':'provider-version'}
    client=OpenAIClient(Settings(),transport=httpx.MockTransport(lambda _:httpx.Response(200,json=response)))
    try:
        result=client.complete('fictional inquiry')
        assert (result.input_tokens,result.output_tokens,result.model)==(123,45,'provider-version')
    finally: client.close()


def test_missing_usage_is_not_zero(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','fake-key-for-transport-test')
    client=OpenAIClient(Settings(),transport=httpx.MockTransport(lambda _:httpx.Response(200,json={'choices':[{'message':{'content':'{}'}}]})))
    try:
        reply=client.complete('fictional inquiry')
        assert reply.input_tokens is None and reply.output_tokens is None
    finally: client.close()


def test_missing_key_blocks_live_client(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    with pytest.raises(ValueError,match='requires OPENAI_API_KEY'): OpenAIClient(Settings())


def test_malformed_api_envelope_is_permanent(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','fake-key-for-transport-test')
    client=OpenAIClient(Settings(),transport=httpx.MockTransport(lambda _:httpx.Response(200,json={'choices':[]})))
    try:
        with pytest.raises(APIError,match='api_envelope_malformed') as error: client.complete('fictional inquiry')
        assert error.value.transient is False
    finally: client.close()
