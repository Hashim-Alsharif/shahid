import asyncio

import httpx

from app.main import app


def request(method, url, **kwargs):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.request(method, url, **kwargs)
    return asyncio.run(run())


def test_home_and_status_are_honest_about_local_only_mode():
    assert request("GET", "/").status_code == 200
    assert request("GET", "/health").json()["ai_executed"] is False


def test_synthetic_example_is_analyzed_with_evidence():
    sample = request("GET", "/api/examples/login_attempts").json()
    report = request("POST", "/api/analyze", json={"text": sample["text"]})
    assert report.status_code == 200
    assert report.json()["summary"]["valid_requests"] == 8
    assert report.json()["findings"][0]["evidence_ids"]
    assert report.json()["ai_executed"] is False


def test_unknown_example_and_bad_log_are_rejected():
    assert request("GET", "/api/examples/unknown").status_code == 404
    assert request("POST", "/api/analyze", json={"text": "bad log"}).status_code == 422


def test_oversize_and_empty_inputs_rejected():
    assert request("POST", "/api/analyze", json={"text": ""}).status_code == 422
    assert request("POST", "/api/analyze", json={"text": "x" * 100001}).status_code == 422
    assert request("POST", "/api/analyze", json={"text": "ش" * 60000}).status_code == 413
