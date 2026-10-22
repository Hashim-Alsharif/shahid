"""Small bounded Token Factory requests. No automatic retries or raw error dumps."""

from typing import Any
from time import perf_counter

import httpx

from shahid.settings import Settings, is_nemotron


class NebiusError(RuntimeError):
    def __init__(self, message: str, code: str = "provider_error"):
        self.code = code
        super().__init__(message)


STATUS_HELP = {
    400: "Request rejected. Check the selected model and its supported request parameters.",
    401: "Authentication failed. Check the key and its Token Factory project.",
    402: "Credits or billing are not ready. Check the Token Factory balance.",
    403: "Access denied. Check project permissions, model entitlement, and account activation.",
    404: "Endpoint or model not found. Use the exact model ID from --models and the correct regional URL.",
    429: "Rate limit or quota reached. Check the account limits before trying again.",
}


class TokenFactoryClient:
    def __init__(self, settings: Settings, *, transport: httpx.BaseTransport | None = None):
        settings.validate()
        self.settings = settings
        self.transport = transport

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict[str, Any]:
        try:
            with httpx.Client(
                base_url=self.settings.base_url,
                headers={"Authorization": f"Bearer {self.settings.api_key}"},
                timeout=httpx.Timeout(90, connect=15),
                transport=self.transport, trust_env=False, follow_redirects=False,
            ) as client:
                response = client.request(method, path, json=payload)
        except httpx.TimeoutException:
            raise NebiusError("Request timed out. No retry was sent. Check usage before repeating the request.", "provider_timeout") from None
        except httpx.RequestError:
            raise NebiusError("Could not reach Token Factory. Check the internet connection and endpoint.") from None
        if not 200 <= response.status_code < 300:
            help_text = STATUS_HELP.get(response.status_code, "Provider returned an error. Check its service status.")
            raise NebiusError(f"HTTP {response.status_code}: {help_text}", f"provider_{response.status_code}")
        try:
            result = response.json()
        except ValueError:
            raise NebiusError("Token Factory did not return JSON. No response body is printed.") from None
        if not isinstance(result, dict):
            raise NebiusError("Unexpected response format from Token Factory.")
        return result

    def list_nemotron_models(self) -> list[str]:
        response = self._request("GET", "models")
        data = response.get("data")
        if not isinstance(data, list):
            raise NebiusError("The model list has an unexpected format.")
        return sorted({item["id"] for item in data if isinstance(item, dict)
                       and isinstance(item.get("id"), str) and is_nemotron(item["id"])})

    def smoke_chat(self) -> dict:
        self.settings.validate(require_model=True)
        response = self._request("POST", "chat/completions", {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": "You are testing a connection. Reply briefly, without explanation."},
                {"role": "user", "content": "Reply with this sentence only: Shahid connection OK."},
            ],
            "max_tokens": 1024,
            "stream": False,
        })
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise NebiusError("Token Factory returned no chat choice. Live inference is not verified.")
        choice = choices[0]
        message = choice.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise NebiusError(
                "No final answer was returned. The model may have exhausted its output/reasoning budget. "
                "Check model settings and usage; live inference is not verified."
            )
        model = response.get("model", self.settings.model)
        if not isinstance(model, str) or not is_nemotron(model):
            raise NebiusError("The response does not identify an NVIDIA Nemotron model. Review it before claiming success.")
        return {"requested_model": self.settings.model, "response_model": model,
                "answer": content.strip(), "finish_reason": choice.get("finish_reason"),
                "usage": response.get("usage", {})}

    def interpret(self, evidence: dict, language: str) -> dict:
        from shahid.interpretation import Interpretation, InterpretationError, request_messages, validate_interpretation

        self.settings.validate(require_model=True)
        if language not in ("ar", "en"):
            raise ValueError("Unsupported language")
        start = perf_counter()
        response = self._request("POST", "chat/completions", {
            "model": self.settings.model,
            "messages": request_messages(evidence, language),
            "response_format": {"type": "json_schema", "json_schema": {
                "name": "shahid_interpretation", "strict": True, "schema": Interpretation.model_json_schema(),
            }},
            "max_tokens": 4096, "stream": False, "store": False,
            "chat_template_kwargs": {"enable_thinking": False},
            "temperature": 0.2, "top_p": 0.95,
        })
        usage = response.get("usage")
        usage = {k: v for k, v in (usage.items() if isinstance(usage, dict) else [])
                 if k in ("prompt_tokens", "completion_tokens", "total_tokens") and type(v) is int and v >= 0}
        metadata = {"usage": usage, "latency_ms": round((perf_counter() - start) * 1000)}
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise InterpretationError("invalid_ai_response", metadata)
        choice = choices[0]
        message = choice.get("message")
        if choice.get("finish_reason") != "stop" or not isinstance(message, dict) or message.get("refusal"):
            metadata["output_limit_reached"] = choice.get("finish_reason") == "length"
            raise InterpretationError("incomplete_ai_response", metadata)
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise InterpretationError("incomplete_ai_response", metadata)
        model = response.get("model")
        if not isinstance(model, str) or not is_nemotron(model) or model != self.settings.model:
            raise InterpretationError("unexpected_ai_model", metadata)
        try:
            interpretation = validate_interpretation(content, evidence)
        except InterpretationError as error:
            error.metadata = metadata
            raise
        overview_source = "model"
        if not evidence["findings"]:
            # A zero-rule result cannot support a broad model-written safety claim.
            # Display an explicitly identified local scope statement instead.
            interpretation["overview"] = (
                "لم تتجاوز البيانات عتبات القواعد المحلية المحددة. هذا لا يثبت سلامة الموقع أو غياب نشاط ضار."
                if language == "ar" else
                "No configured local rule threshold was crossed. This does not establish site safety or the absence of malicious activity."
            )
            overview_source = "local_rule_scope"
        return {"ai_executed": True, "provider": "Nebius Token Factory", "model": model,
                "language": language, "interpretation": interpretation, "usage": usage,
                "latency_ms": metadata["latency_ms"],
                "reference_check": "passed", "prose_truth_verified": False,
                "overview_source": overview_source}
