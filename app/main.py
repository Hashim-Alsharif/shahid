import hashlib
import sqlite3
import threading
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from shahid.hosting import COOKIE, SESSION_SECONDS, DemoStore, GateError, HostingSettings, load_hosting_settings
from shahid.interpretation import Language, InterpretationError, PreviewTickets, prepare_evidence, preview_digest
from shahid.logs import analyze_logs
from shahid.nebius import NebiusError, TokenFactoryClient
from shahid.settings import ROOT, ConfigurationError, load_settings

tickets = PreviewTickets()
inference_lock = threading.Lock()


class BodyLimit:
    """Bound JSON/form input before parsing, including chunked requests."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] not in ('POST', 'PUT', 'PATCH'):
            return await self.app(scope, receive, send)
        body = bytearray()
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            body.extend(message.get('body', b''))
            if len(body) > 650_000:
                return await JSONResponse({'detail': {'code': 'invalid_input'}}, status_code=413)(scope, receive, send)
            if not message.get('more_body', False):
                break
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {'type': 'http.request', 'body': bytes(body), 'more_body': False}
            return await receive()

        return await self.app(scope, replay, send)


async def browser_guard(request: Request, call_next):
    config = request.app.state.hosting
    origin = request.headers.get('origin')
    expected = config.origin if config.hosted else f"{request.url.scheme}://{request.headers.get('host', '')}"
    if request.method not in ('GET', 'HEAD', 'OPTIONS') and ((config.hosted and origin != expected) or (origin and origin != expected)):
        response = JSONResponse({'detail': {'code': 'origin_rejected'}}, status_code=403)
    else:
        try:
            request.state.session_id = request.app.state.store.session(request.cookies.get(COOKIE)) if config.hosted else None
            public = request.url.path in ('/health', '/login', '/api/auth/login') or request.url.path.startswith('/static/')
            if config.hosted and not public and not request.state.session_id:
                response = (JSONResponse({'detail': {'code': 'auth_required'}}, status_code=401)
                            if request.url.path.startswith('/api/') else RedirectResponse('/login', status_code=303))
            else:
                response = await call_next(request)
        except sqlite3.Error:
            response = JSONResponse({'detail': {'code': 'demo_unavailable'}}, status_code=503)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    if config.hosted:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    if request.url.path not in ('/docs', '/redoc', '/docs/oauth2-redirect'):
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    return response


class LogInput(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)


class PreviewInput(LogInput):
    language: Language = 'ar'


class InterpretInput(PreviewInput):
    preview_token: str = Field(min_length=20, max_length=100)
    consent: bool


class LoginInput(BaseModel):
    code: str = Field(min_length=1, max_length=200)


def home():
    return FileResponse(ROOT / 'app' / 'static' / 'index.html')


def login_page():
    return FileResponse(ROOT / 'app' / 'static' / 'login.html')


def login(payload: LoginInput, request: Request):
    if not request.app.state.hosting.hosted:
        raise HTTPException(404)
    try:
        token = request.app.state.store.login(payload.code)
    except GateError as error:
        raise HTTPException(429 if error.code == 'login_limited' else 401, {'code': error.code}) from None
    response = JSONResponse({'ok': True})
    response.set_cookie(COOKIE, token, max_age=SESSION_SECONDS, secure=True, httponly=True, samesite='strict', path='/')
    return response


def logout(request: Request):
    if request.app.state.hosting.hosted:
        request.app.state.store.logout(request.cookies.get(COOKIE, ''))
    response = JSONResponse({'ok': True})
    response.delete_cookie(COOKIE, secure=True, httponly=True, samesite='strict', path='/')
    return response


def demo_status(request: Request):
    if not request.app.state.hosting.hosted:
        return {'mode': 'local'}
    return {'mode': 'hosted', **request.app.state.store.usage(request.state.session_id)}


def health():
    return {'status': 'ok', 'ai_executed': False}


def example(name: str):
    if name not in ('normal', 'login_attempts', 'sensitive_paths', 'legitimate_burst'):
        raise HTTPException(404, 'Unknown synthetic example')
    return {'name': name, 'synthetic': True, 'text': (ROOT / 'samples' / f'{name}.log').read_text(encoding='utf-8')}


def analyze(payload: LogInput):
    if len(payload.text.encode('utf-8')) > 100_000:
        raise HTTPException(413, 'Log text exceeds the 100 KB limit.')
    result = analyze_logs(payload.text)
    if not result['summary']['valid_requests']:
        raise HTTPException(422, 'No supported Nginx combined-log lines found.')
    return result


def prepare(payload: PreviewInput, request: Request):
    try:
        evidence = prepare_evidence(analyze(payload))
        settings = load_settings()
        settings.validate(require_model=True)
        digest = preview_digest(evidence, payload.language, settings.model, settings.base_url)
        if request.app.state.hosting.hosted:
            digest = hashlib.sha256((request.state.session_id + digest).encode()).hexdigest()
        return evidence, settings, digest
    except InterpretationError as error:
        raise HTTPException(413, {'code': error.code}) from None
    except ConfigurationError:
        raise HTTPException(503, {'code': 'ai_not_configured'}) from None


def ai_preview(payload: PreviewInput, request: Request):
    evidence, settings, digest = prepare(payload, request)
    return {'provider': 'Nebius Token Factory', 'model': settings.model,
            'language': payload.language, 'data': evidence,
            'preview_token': tickets.issue(digest), 'expires_in_seconds': 600,
            'max_output_tokens': 4096, 'ai_executed': False}


def ai_interpret(payload: InterpretInput, request: Request):
    if not payload.consent:
        raise HTTPException(400, {'code': 'consent_required'})
    evidence, settings, digest = prepare(payload, request)
    if not inference_lock.acquire(blocking=False):
        raise HTTPException(429, {'code': 'ai_busy'})
    attempt, usage = None, None
    try:
        tickets.consume(payload.preview_token, digest)
        if request.app.state.hosting.hosted:
            attempt = request.app.state.store.reserve(request.state.session_id)
        result = TokenFactoryClient(settings).interpret(evidence, payload.language)
        usage = result.get('usage')
        return result
    except GateError as error:
        status = 503 if error.code == 'ai_disabled' else 401 if error.code == 'auth_required' else 429
        raise HTTPException(status, {'code': error.code}) from None
    except InterpretationError as error:
        usage = error.metadata.get('usage')
        status = 409 if error.code == 'preview_expired' else 502
        raise HTTPException(status, {'code': error.code, **error.metadata}) from None
    except NebiusError as error:
        raise HTTPException(502, {'code': error.code}) from None
    finally:
        try:
            if attempt:
                request.app.state.store.finish(attempt, usage)
        finally:
            inference_lock.release()


def create_app(hosting: HostingSettings | None = None):
    hosting = hosting or load_hosting_settings()
    hosting.validate()
    application = FastAPI(title='Shahid | شاهد', version='0.3.0',
        description='Evidence-linked log observations with optional Nemotron interpretation.',
        docs_url=None if hosting.hosted else '/docs', redoc_url=None if hosting.hosted else '/redoc',
        openapi_url=None if hosting.hosted else '/openapi.json')
    application.state.hosting = hosting
    application.state.store = DemoStore(hosting) if hosting.hosted else None
    hosts = [urlsplit(hosting.origin).hostname] if hosting.hosted else ['127.0.0.1', 'localhost', 'test', 'testserver']
    application.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts)
    application.middleware('http')(browser_guard)
    application.add_middleware(BodyLimit)
    application.mount('/static', StaticFiles(directory=ROOT / 'app' / 'static'), name='static')
    for path, endpoint, methods in (
        ('/', home, ['GET']), ('/login', login_page, ['GET']),
        ('/api/auth/login', login, ['POST']), ('/api/auth/logout', logout, ['POST']),
        ('/api/demo', demo_status, ['GET']), ('/health', health, ['GET']),
        ('/api/examples/{name}', example, ['GET']), ('/api/analyze', analyze, ['POST']),
        ('/api/ai/preview', ai_preview, ['POST']), ('/api/ai/interpret', ai_interpret, ['POST']),
    ):
        application.add_api_route(path, endpoint, methods=methods)

    @application.exception_handler(RequestValidationError)
    async def validation_error(request, error):
        return JSONResponse({'detail': {'code': 'invalid_input'}}, status_code=422)

    return application


app = create_app()
