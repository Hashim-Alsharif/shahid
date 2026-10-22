"""Small, single-instance judging gate. Stores counters, never log contents."""

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

from shahid.settings import ROOT, ConfigurationError

COOKIE = "__Host-shahid"
SESSION_SECONDS = 8 * 3600


def hash_access_code(code: str, salt: str | None = None) -> str:
    if not 16 <= len(code) <= 200:
        raise ConfigurationError("Choose an access code between 16 and 200 characters.")
    salt = salt or secrets.token_hex(16)
    digest = hashlib.scrypt(code.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
    return f"scrypt${salt}${digest}"


def valid_hash(value: str) -> bool:
    return bool(re.fullmatch(r"scrypt\$[0-9a-f]{32}\$[0-9a-f]{128}", value))


def verify_access_code(code: str, encoded: str) -> bool:
    if not 16 <= len(code) <= 200 or not valid_hash(encoded):
        return False
    return hmac.compare_digest(hash_access_code(code, encoded.split("$")[1]), encoded)


@dataclass(frozen=True)
class HostingSettings:
    mode: str = "local"
    origin: str = ""
    code_hash: str = field(default="", repr=False)
    db_path: Path | None = None
    ai_enabled: bool = False
    daily_limit: int = 20
    total_limit: int = 120
    session_limit: int = 5
    cooldown_seconds: int = 20

    @property
    def hosted(self):
        return self.mode == "hosted"

    def validate(self):
        if self.mode not in ("local", "hosted"):
            raise ConfigurationError("SHAHID_MODE must be local or hosted.")
        if not self.hosted:
            return
        parts = urlsplit(self.origin)
        if (parts.scheme != "https" or not parts.hostname or parts.username or parts.password
                or parts.port not in (None, 443) or parts.path or parts.query or parts.fragment):
            raise ConfigurationError("Hosted mode requires an exact HTTPS SHAHID_PUBLIC_ORIGIN.")
        if not valid_hash(self.code_hash):
            raise ConfigurationError("Hosted mode requires a scrypt access-code hash.")
        if not self.db_path or not self.db_path.is_absolute() or not self.db_path.parent.is_dir():
            raise ConfigurationError("Hosted mode requires an existing persistent directory and absolute database path.")
        for value, ceiling in ((self.daily_limit, 100), (self.total_limit, 1000), (self.session_limit, 20)):
            if type(value) is not int or not 1 <= value <= ceiling:
                raise ConfigurationError("Invalid hosted inference quota.")
        if not 1 <= self.cooldown_seconds <= 3600:
            raise ConfigurationError("Invalid inference cooldown.")


def load_hosting_settings() -> HostingSettings:
    load_dotenv(ROOT / ".env", override=False, interpolate=False)
    try:
        config = HostingSettings(
            mode=os.getenv("SHAHID_MODE", "hosted" if os.getenv("RENDER") == "true" else "local"),
            origin=os.getenv("SHAHID_PUBLIC_ORIGIN", os.getenv("RENDER_EXTERNAL_URL", "")).rstrip("/"),
            code_hash=os.getenv("SHAHID_ACCESS_CODE_HASH", ""),
            db_path=Path(os.environ["SHAHID_DB_PATH"]) if os.getenv("SHAHID_DB_PATH") else None,
            ai_enabled=os.getenv("SHAHID_AI_ENABLED", "false").lower() == "true",
            daily_limit=int(os.getenv("SHAHID_DAILY_LIMIT", "20")),
            total_limit=int(os.getenv("SHAHID_TOTAL_LIMIT", "120")),
            session_limit=int(os.getenv("SHAHID_SESSION_LIMIT", "5")),
            cooldown_seconds=int(os.getenv("SHAHID_COOLDOWN_SECONDS", "20")),
        )
        config.validate()
        return config
    except (ValueError, OSError):
        raise ConfigurationError("Invalid hosting configuration; check hosting environment variables.") from None


class GateError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class DemoStore:
    def __init__(self, config: HostingSettings, clock=time.time):
        config.validate()
        self.config, self.clock = config, clock
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, expires REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS logins (at REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS attempts (
                    id TEXT PRIMARY KEY, session TEXT NOT NULL, at REAL NOT NULL, tokens INTEGER);
                CREATE TABLE IF NOT EXISTS control (id INTEGER PRIMARY KEY CHECK(id=1), paused INTEGER NOT NULL,
                    lease TEXT, lease_until REAL NOT NULL DEFAULT 0);
                INSERT OR IGNORE INTO control(id, paused) VALUES (1, 0);
            """)

    @contextmanager
    def connect(self):
        # BEGIN IMMEDIATE serializes quota decisions across independent connections.
        with sqlite3.connect(self.config.db_path, timeout=5, isolation_level=None) as db:
            db.execute("PRAGMA busy_timeout=5000")
            db.execute("BEGIN IMMEDIATE")
            try:
                yield db
                db.commit()
            except BaseException:
                db.rollback()
                raise

    def identity(self, token: str) -> str:
        # Changing the configured access-code hash invalidates previous cookies.
        return hashlib.sha256((self.config.code_hash + token).encode()).hexdigest()

    def login(self, code: str) -> str:
        now = self.clock()
        # Reserve before the expensive hash. This is a global gate, not a trusted IP limit.
        with self.connect() as db:
            db.execute("DELETE FROM logins WHERE at <= ?", (now - 900,))
            if db.execute("SELECT COUNT(*) FROM logins").fetchone()[0] >= 30:
                raise GateError("login_limited")
            db.execute("INSERT INTO logins(at) VALUES (?)", (now,))
        if not verify_access_code(code, self.config.code_hash):
            raise GateError("login_failed")
        token = secrets.token_urlsafe(32)
        with self.connect() as db:
            db.execute("DELETE FROM sessions WHERE expires <= ?", (now,))
            db.execute("INSERT INTO sessions VALUES (?, ?)", (self.identity(token), now + SESSION_SECONDS))
        return token

    def session(self, token: str | None) -> str | None:
        if not token or len(token) > 100:
            return None
        identity = self.identity(token)
        with self.connect() as db:
            saved = db.execute("SELECT expires FROM sessions WHERE id=?", (identity,)).fetchone()
        return identity if saved and saved[0] > self.clock() else None

    def logout(self, token: str):
        with self.connect() as db:
            db.execute("DELETE FROM sessions WHERE id=?", (self.identity(token),))

    def _usage(self, db, session: str):
        now = self.clock()
        midnight = int(now // 86400) * 86400  # Explicit UTC reset, not host timezone.
        total, today, own = db.execute(
            "SELECT COUNT(*), COALESCE(SUM(at>=?),0), COALESCE(SUM(at>=? AND session=?),0) FROM attempts",
            (midnight, midnight, session),
        ).fetchone()
        paused, lease, until = db.execute("SELECT paused, lease, lease_until FROM control WHERE id=1").fetchone()
        return {"enabled": self.config.ai_enabled and not paused,
                "daily_remaining": max(0, self.config.daily_limit - today),
                "total_remaining": max(0, self.config.total_limit - total),
                "session_remaining": max(0, self.config.session_limit - own),
                "reset_timezone": "UTC", "busy": bool(lease and until > now)}

    def usage(self, session: str):
        with self.connect() as db:
            return self._usage(db, session)

    def reserve(self, session: str) -> str:
        now = self.clock()
        with self.connect() as db:
            saved = db.execute("SELECT expires FROM sessions WHERE id=?", (session,)).fetchone()
            if not saved or saved[0] <= now:
                raise GateError("auth_required")
            usage = self._usage(db, session)
            if not usage["enabled"]:
                raise GateError("ai_disabled")
            if not min(usage["daily_remaining"], usage["total_remaining"], usage["session_remaining"]):
                raise GateError("quota_exhausted")
            if usage["busy"]:
                raise GateError("ai_busy")
            latest = db.execute("SELECT MAX(at) FROM attempts").fetchone()[0]
            if latest is not None and now - latest < self.config.cooldown_seconds:
                raise GateError("ai_cooldown")
            attempt = secrets.token_hex(16)
            db.execute("INSERT INTO attempts(id,session,at) VALUES (?,?,?)", (attempt, session, now))
            db.execute("UPDATE control SET lease=?, lease_until=? WHERE id=1", (attempt, now + 180))
            return attempt

    def finish(self, attempt: str, usage: dict | None = None):
        tokens = (usage or {}).get("total_tokens")
        tokens = tokens if type(tokens) is int and 0 <= tokens <= 2**63 - 1 else None
        with self.connect() as db:
            db.execute("UPDATE attempts SET tokens=? WHERE id=?", (tokens, attempt))
            db.execute("UPDATE control SET lease=NULL, lease_until=0 WHERE id=1 AND lease=?", (attempt,))

    def pause(self, paused: bool):
        with self.connect() as db:
            db.execute("UPDATE control SET paused=? WHERE id=1", (int(paused),))
