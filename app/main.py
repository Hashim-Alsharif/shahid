import threading

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from shahid.interpretation import Language, InterpretationError, PreviewTickets, prepare_evidence, preview_digest
from shahid.logs import analyze_logs
from shahid.nebius import NebiusError, TokenFactoryClient
from shahid.settings import ROOT, ConfigurationError, load_settings

app = FastAPI(title="Shahid | شاهد", version="0.2.0", description="Local evidence with optional Nemotron interpretation. Localhost prototype.")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "test", "testserver"])
app.mount("/static", StaticFiles(directory=ROOT / "app" / "static"), name="static")
tickets = PreviewTickets()
inference_lock = threading.Lock()


@app.middleware("http")
async def local_browser_guard(request: Request, call_next):
    # The prototype has no public authentication; bind it to localhost only.
    origin = request.headers.get("origin")
    expected = f"{request.url.scheme}://{request.headers.get('host', '')}"
    if request.method == "POST" and origin and origin != expected:
        return JSONResponse({"detail": {"code": "origin_rejected"}}, status_code=403)
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path not in ("/docs", "/redoc", "/docs/oauth2-redirect"):
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    return response


class LogInput(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)


class PreviewInput(LogInput):
    language: Language = "ar"


class InterpretInput(PreviewInput):
    preview_token: str = Field(min_length=20, max_length=100)
    consent: bool


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(ROOT / "app" / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "stage": "optional_nemotron_interpretation", "ai_executed": False}


@app.get("/api/examples/{name}")
def example(name: str):
    if name not in ("normal", "login_attempts", "sensitive_paths", "legitimate_burst"):
        raise HTTPException(404, "Unknown synthetic example")
    return {"name": name, "synthetic": True, "text": (ROOT / "samples" / f"{name}.log").read_text(encoding="utf-8")}


@app.post("/api/analyze")
def analyze(payload: LogInput):
    if len(payload.text.encode("utf-8")) > 100_000:
        raise HTTPException(413, "Log text exceeds the 100 KB limit.")
    result = analyze_logs(payload.text)
    if not result["summary"]["valid_requests"]:
        raise HTTPException(422, "No supported Nginx combined-log lines found.")
    return result


def prepare(payload: PreviewInput):
    try:
        evidence = prepare_evidence(analyze(payload))
        settings = load_settings()
        settings.validate(require_model=True)
        digest = preview_digest(evidence, payload.language, settings.model, settings.base_url)
        return evidence, settings, digest
    except InterpretationError as error:
        raise HTTPException(413, {"code": error.code}) from None
    except ConfigurationError:
        raise HTTPException(503, {"code": "ai_not_configured"}) from None


@app.post("/api/ai/preview")
def ai_preview(payload: PreviewInput):
    evidence, settings, digest = prepare(payload)
    return {"provider": "Nebius Token Factory", "model": settings.model,
            "language": payload.language, "data": evidence,
            "preview_token": tickets.issue(digest), "expires_in_seconds": 600,
            "max_output_tokens": 4096, "ai_executed": False}


@app.post("/api/ai/interpret")
def ai_interpret(payload: InterpretInput):
    if not payload.consent:
        raise HTTPException(400, {"code": "consent_required"})
    evidence, settings, digest = prepare(payload)
    if not inference_lock.acquire(blocking=False):
        raise HTTPException(429, {"code": "ai_busy"})
    try:
        tickets.consume(payload.preview_token, digest)
        return TokenFactoryClient(settings).interpret(evidence, payload.language)
    except InterpretationError as error:
        status = 409 if error.code == "preview_expired" else 502
        raise HTTPException(status, {"code": error.code, **error.metadata}) from None
    except NebiusError as error:
        raise HTTPException(502, {"code": error.code}) from None
    finally:
        inference_lock.release()
