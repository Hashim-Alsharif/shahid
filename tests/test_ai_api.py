import pytest

import app.main as server
from shahid.interpretation import InterpretationError
from shahid.nebius import NebiusError
from shahid.settings import Settings, ConfigurationError
from tests.test_app import request


@pytest.fixture
def payload(monkeypatch):
    monkeypatch.setattr(server, "load_settings", lambda: Settings("secret-example", model="nvidia/test-nemotron-model"))
    return {"text": request("GET", "/api/examples/login_attempts").json()["text"], "language": "en"}


def test_preview_does_not_call_provider_or_expose_key(payload, monkeypatch):
    monkeypatch.setattr(server.TokenFactoryClient, "interpret", lambda *_: pytest.fail("Preview must not call inference"))
    preview = request("POST", "/api/ai/preview", json=payload)
    assert preview.status_code == 200 and preview.json()["ai_executed"] is False
    assert "secret-example" not in preview.text
    assert preview.headers["cache-control"] == "no-store"


def test_interpret_requires_consent_and_valid_unchanged_preview(payload, monkeypatch):
    called = []
    monkeypatch.setattr(server.TokenFactoryClient, "interpret", lambda _, data, language: called.append(language) or {"ai_executed": True})
    ticket = request("POST", "/api/ai/preview", json=payload).json()["preview_token"]
    body = dict(payload, preview_token=ticket, consent=False)
    assert request("POST", "/api/ai/interpret", json=body).status_code == 400
    body["consent"] = True
    assert request("POST", "/api/ai/interpret", json=body).status_code == 200
    assert called == ["en"]
    assert request("POST", "/api/ai/interpret", json=body).status_code == 409
    assert called == ["en"]


@pytest.mark.parametrize("field,value", [("language", "ar"), ("text", "invalid")])
def test_changed_payload_cannot_reuse_preview(payload, monkeypatch, field, value):
    ticket = request("POST", "/api/ai/preview", json=payload).json()["preview_token"]
    monkeypatch.setattr(server.TokenFactoryClient, "interpret", lambda *_: pytest.fail("Changed preview must not call provider"))
    changed = dict(payload, preview_token=ticket, consent=True)
    changed[field] = value
    assert request("POST", "/api/ai/interpret", json=changed).status_code in (409, 422)


def test_provider_error_is_localizable_without_raw_detail(payload, monkeypatch):
    def failure(*_): raise NebiusError("secret-example raw provider body", "provider_402")
    monkeypatch.setattr(server.TokenFactoryClient, "interpret", failure)
    ticket = request("POST", "/api/ai/preview", json=payload).json()["preview_token"]
    response = request("POST", "/api/ai/interpret", json=dict(payload, preview_token=ticket, consent=True))
    assert response.status_code == 502
    assert response.json()["detail"]["code"] == "provider_402"
    assert "secret-example" not in response.text


def test_config_error_and_language_rejected_before_provider(payload, monkeypatch):
    assert request("POST", "/api/ai/preview", json=dict(payload, language="fr")).status_code == 422
    def missing(): raise ConfigurationError("secret-example")
    monkeypatch.setattr(server, "load_settings", missing)
    response = request("POST", "/api/ai/preview", json=payload)
    assert response.status_code == 503 and "secret-example" not in response.text


def test_cross_origin_and_foreign_host_rejected(payload):
    assert request("POST", "/api/ai/preview", json=payload, headers={"Origin": "https://evil.example"}).status_code == 403
    assert request("GET", "/", headers={"Host": "evil.example"}).status_code == 400


def test_concurrent_inference_is_rejected(payload):
    ticket = request("POST", "/api/ai/preview", json=payload).json()["preview_token"]
    server.inference_lock.acquire()
    try:
        result = request("POST", "/api/ai/interpret", json=dict(payload, preview_token=ticket, consent=True))
        assert result.status_code == 429
    finally:
        server.inference_lock.release()


def test_invalid_generated_references_return_error_not_success(payload, monkeypatch):
    def failure(*_):
        raise InterpretationError("invalid_ai_references", {"usage": {"total_tokens": 50}})
    monkeypatch.setattr(server.TokenFactoryClient, "interpret", failure)
    ticket = request("POST", "/api/ai/preview", json=payload).json()["preview_token"]
    response = request("POST", "/api/ai/interpret", json=dict(payload, preview_token=ticket, consent=True))
    assert response.status_code == 502
    assert response.json()["detail"] == {"code": "invalid_ai_references", "usage": {"total_tokens": 50}}
    assert "interpretation" not in response.json()
