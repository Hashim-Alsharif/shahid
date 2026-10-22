import json

import httpx
import pytest

from shahid.nebius import NebiusError, TokenFactoryClient
from shahid.settings import ConfigurationError, Settings

MODEL = "nvidia/test-nemotron-model"


def test_key_not_in_settings_repr():
    assert "secret-example" not in repr(Settings("secret-example"))


@pytest.mark.parametrize("url", [
    "http://api.tokenfactory.nebius.com/v1/", "https://example.com/v1/",
    "https://api.tokenfactory.nebius.com.evil.test/v1/",
    "https://api.tokenfactory.nebius.com/v1/?x=1", "https://api.tokenfactory.nebius.com:bad/v1/",
])
def test_credentials_cannot_be_sent_to_unapproved_endpoint(url):
    with pytest.raises(ConfigurationError):
        Settings("secret-example", base_url=url).validate()


def test_missing_key_has_actionable_message():
    with pytest.raises(ConfigurationError, match="NEBIUS_API_KEY"):
        Settings("").validate()


def test_model_list_filters_other_providers_and_preserves_exact_case():
    def handler(request):
        assert request.url.path == "/v1/models"
        assert request.headers["authorization"] == "Bearer secret-example"
        return httpx.Response(200, json={"data": [{"id": MODEL}, {"id": "other/provider"}, {"id": "nvidia/Nemotron-Exact-Case"}]})
    result = TokenFactoryClient(Settings("secret-example"), transport=httpx.MockTransport(handler)).list_nemotron_models()
    assert result == ["nvidia/Nemotron-Exact-Case", MODEL]


def test_smoke_chat_is_single_bounded_request_without_real_logs():
    requests = []
    def handler(request):
        requests.append(request)
        body = json.loads(request.content)
        assert request.url.path == "/v1/chat/completions"
        assert body["model"] == MODEL
        assert body["max_tokens"] == 1024
        assert "secret-example" not in request.content.decode()
        assert len(body["messages"]) == 2
        return httpx.Response(200, json={"model": MODEL, "choices": [{"message": {"content": "Shahid connection OK."}, "finish_reason": "stop"}], "usage": {"total_tokens": 20}})
    result = TokenFactoryClient(Settings("secret-example", model=MODEL), transport=httpx.MockTransport(handler)).smoke_chat()
    assert result["answer"] == "Shahid connection OK."
    assert len(requests) == 1


@pytest.mark.parametrize("status", [401, 402, 403, 404, 429, 500, 307])
def test_error_body_not_leaked_and_no_automatic_retry(status):
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(status, json={"detail": "secret-example private provider response"}, headers={"location": "https://example.com"})
    client = TokenFactoryClient(Settings("secret-example"), transport=httpx.MockTransport(handler))
    with pytest.raises(NebiusError) as error:
        client.list_nemotron_models()
    assert "secret-example" not in str(error.value)
    assert len(requests) == 1


def test_empty_final_content_is_not_reported_as_success():
    response = {"model": MODEL, "choices": [{"message": {"content": "", "reasoning_content": "not a final answer"}, "finish_reason": "length"}]}
    client = TokenFactoryClient(Settings("secret-example", model=MODEL), transport=httpx.MockTransport(lambda _: httpx.Response(200, json=response)))
    with pytest.raises(NebiusError, match="No final answer"):
        client.smoke_chat()


def test_non_nvidia_model_is_rejected_before_request():
    with pytest.raises(ConfigurationError):
        TokenFactoryClient(Settings("secret-example", model="other/model")).smoke_chat()
