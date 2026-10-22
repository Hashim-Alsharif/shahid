import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import httpx
import pytest

import app.main as server
from shahid.hosting import COOKIE, SESSION_SECONDS, DemoStore, GateError, HostingSettings, hash_access_code
from shahid.nebius import NebiusError
from shahid.settings import ConfigurationError, ROOT, Settings

CODE = "synthetic-testing-access-code"
HASH = hash_access_code(CODE)
ORIGIN = "https://judge.example"


@pytest.fixture
def config(tmp_path):
    return HostingSettings(mode="hosted", origin=ORIGIN, code_hash=HASH,
        db_path=tmp_path / "demo.sqlite3", ai_enabled=True)


def make_client(app):
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=ORIGIN, headers={"Origin": ORIGIN})


def test_configuration_fails_closed(config):
    for change in ({"origin": "http://judge.example"}, {"code_hash": ""}, {"db_path": None},
                   {"daily_limit": 0}, {"total_limit": 1001}, {"mode": "typo"}):
        with pytest.raises(ConfigurationError):
            replace(config, **change).validate()


def test_auth_origin_cookie_expiry_and_revocation(config):
    application = server.create_app(config)
    async def run():
        async with make_client(application) as client:
            assert (await client.get("/health")).status_code == 200
            assert (await client.get("/")).headers["location"] == "/login"
            assert (await client.get("/api/examples/normal")).status_code == 401
            assert (await client.post("/api/auth/login", json={"code": CODE}, headers={"Origin": "https://evil.example"})).status_code == 403
            client.headers.pop("Origin")
            assert (await client.post("/api/auth/login", json={"code": CODE})).status_code == 403
            client.headers["Origin"] = ORIGIN
            wrong = await client.post("/api/auth/login", json={"code": "wrong-code"})
            assert wrong.status_code == 401 and "wrong-code" not in wrong.text
            logged = await client.post("/api/auth/login", json={"code": CODE})
            cookie = logged.headers["set-cookie"]
            assert all(x in cookie for x in ("Secure", "HttpOnly", "SameSite=strict", "Path=/"))
            assert "Domain=" not in cookie
            token = client.cookies.get(COOKIE)
            assert (await client.get("/")).status_code == 200
            assert (await client.get("/openapi.json")).status_code == 404
            assert (await client.get("/", headers={"Host": "evil.example"})).status_code == 400
            assert (await client.post("/api/auth/logout", json={})).status_code == 200
            client.cookies.set(COOKIE, token)
            assert (await client.get("/api/demo")).status_code == 401
    asyncio.run(run())
    store = application.state.store
    token = store.login(CODE)
    store.clock = lambda: __import__("time").time() + SESSION_SECONDS + 1
    assert store.session(token) is None
    rotated = DemoStore(replace(config, code_hash=hash_access_code(CODE + "new")))
    assert rotated.session(token) is None


def test_login_throttle_is_durable(config):
    store = DemoStore(config)
    for _ in range(30):
        with pytest.raises(GateError, match="login_failed"):
            store.login("wrong")
    with pytest.raises(GateError, match="login_limited"):
        DemoStore(config).login(CODE)


def test_quota_persists_counts_failures_and_pause_does_not_reset(config):
    now = [100000.0]
    store = DemoStore(replace(config, session_limit=2), clock=lambda: now[0])
    session = store.session(store.login(CODE))
    first = store.reserve(session)
    with pytest.raises(GateError, match="ai_busy"):
        DemoStore(store.config, clock=lambda: now[0]).reserve(session)
    store.finish(first, {"total_tokens": 2**100})  # Invalid/unknown usage still consumes the attempt.
    with pytest.raises(GateError, match="ai_cooldown"):
        store.reserve(session)
    now[0] += 21
    second = store.reserve(session)
    store.finish(second, {"total_tokens": 123})
    restarted = DemoStore(store.config, clock=lambda: now[0])
    assert restarted.usage(session)["session_remaining"] == 0
    with pytest.raises(GateError, match="quota_exhausted"):
        restarted.reserve(session)
    restarted.pause(True)
    new_session = restarted.session(restarted.login(CODE))
    with pytest.raises(GateError, match="ai_disabled"):
        restarted.reserve(new_session)
    restarted.pause(False)
    assert restarted.usage(new_session)["total_remaining"] == 118


def test_daily_and_lifetime_limits_survive_new_sessions_and_utc_reset(config):
    now = [86400.0 * 2 + 10]
    store = DemoStore(replace(config, daily_limit=1, total_limit=2), clock=lambda: now[0])
    sid = store.session(store.login(CODE))
    store.finish(store.reserve(sid))
    fresh = store.session(store.login(CODE))
    with pytest.raises(GateError, match="quota_exhausted"):
        store.reserve(fresh)
    now[0] += 86400
    fresh = store.session(store.login(CODE))
    assert store.usage(fresh)["daily_remaining"] == 1
    store.finish(store.reserve(fresh))
    now[0] += 86400
    fresh = store.session(store.login(CODE))
    with pytest.raises(GateError, match="quota_exhausted"):
        store.reserve(fresh)


def test_atomic_reservation_across_independent_connections(config):
    store = DemoStore(config)
    sid = store.session(store.login(CODE))
    def attempt(_):
        try:
            return DemoStore(config).reserve(sid)
        except GateError as error:
            return error.code
    with ThreadPoolExecutor(max_workers=4) as pool:
        outcomes = list(pool.map(attempt, range(4)))
    assert outcomes.count("ai_busy") == 3
    assert store.usage(sid)["total_remaining"] == 119


def test_hosted_provider_failure_count_and_preview_session_binding(config, monkeypatch):
    application = server.create_app(replace(config, session_limit=1))
    monkeypatch.setattr(server, "load_settings", lambda: Settings("fake-key", model="nvidia/test-nemotron"))
    called = []
    def failure(*args):
        called.append(True)
        raise NebiusError("private provider detail", "provider_402")
    monkeypatch.setattr(server.TokenFactoryClient, "interpret", failure)
    payload = {"text": (ROOT / "samples/login_attempts.log").read_text(), "language": "en"}
    async def run():
        async with make_client(application) as a, make_client(application) as b:
            for client in (a, b):
                assert (await client.post("/api/auth/login", json={"code": CODE})).status_code == 200
            token = (await a.post("/api/ai/preview", json=payload)).json()["preview_token"]
            body = dict(payload, consent=True, preview_token=token)
            assert (await b.post("/api/ai/interpret", json=body)).status_code == 409
            assert not called
            body["preview_token"] = (await a.post("/api/ai/preview", json=payload)).json()["preview_token"]
            failed = await a.post("/api/ai/interpret", json=body)
            assert failed.status_code == 502 and "private provider detail" not in failed.text
            assert (await a.get("/api/demo")).json()["session_remaining"] == 0
            body["preview_token"] = (await a.post("/api/ai/preview", json=payload)).json()["preview_token"]
            assert (await a.post("/api/ai/interpret", json=body)).status_code == 429
            assert len(called) == 1
            assert (await a.post("/api/analyze", json=payload)).status_code == 200
    asyncio.run(run())
    assert payload["text"].encode() not in config.db_path.read_bytes()
    assert CODE.encode() not in config.db_path.read_bytes()


def test_disabled_and_failed_accounting_never_call_provider(config, monkeypatch):
    application = server.create_app(replace(config, ai_enabled=False))
    monkeypatch.setattr(server, "load_settings", lambda: Settings("fake", model="nvidia/test-nemotron"))
    monkeypatch.setattr(server.TokenFactoryClient, "interpret", lambda *_: pytest.fail("Must not call provider"))
    payload = {"text": (ROOT / "samples/normal.log").read_text(), "language": "ar"}
    async def run():
        async with make_client(application) as client:
            await client.post("/api/auth/login", json={"code": CODE})
            token = (await client.post("/api/ai/preview", json=payload)).json()["preview_token"]
            result = await client.post("/api/ai/interpret", json=dict(payload, consent=True, preview_token=token))
            assert result.status_code == 503 and result.json()["detail"]["code"] == "ai_disabled"
            assert (await client.get("/api/demo")).json()["total_remaining"] == 120
            def unavailable(*args):
                raise __import__("sqlite3").OperationalError("private path")
            monkeypatch.setattr(application.state.store, "reserve", unavailable)
            token = (await client.post("/api/ai/preview", json=payload)).json()["preview_token"]
            result = await client.post("/api/ai/interpret", json=dict(payload, consent=True, preview_token=token))
            assert result.status_code == 503 and "private path" not in result.text
    asyncio.run(run())


def test_chunked_body_bound_and_validation_do_not_echo_input(config):
    application = server.create_app(config)
    async def chunks():
        for _ in range(8):
            yield b"x" * 100000
    async def run():
        async with make_client(application) as client:
            result = await client.post("/api/auth/login", content=chunks())
            assert result.status_code == 413
            result = await client.post("/api/auth/login", json={"code": "sensitive" * 100})
            assert result.status_code == 422 and "sensitive" not in result.text
    asyncio.run(run())
