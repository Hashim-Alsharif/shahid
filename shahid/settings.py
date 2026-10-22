import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


class ConfigurationError(ValueError):
    """A safe error that never includes the credential's value."""


@dataclass(frozen=True)
class Settings:
    api_key: str = field(repr=False)
    base_url: str = "https://api.tokenfactory.nebius.com/v1/"
    model: str = ""

    def validate(self, *, require_model: bool = False) -> None:
        if not self.api_key or self.api_key.lower().startswith(("paste_", "your_", "replace_")):
            raise ConfigurationError("Add NEBIUS_API_KEY to .env locally. Do not send the key in chat.")
        try:
            parsed = urlsplit(self.base_url)
            port = parsed.port
        except ValueError:
            raise ConfigurationError("NEBIUS_BASE_URL is not a valid Token Factory URL.") from None
        host = parsed.hostname or ""
        official_host = host == "api.tokenfactory.nebius.com" or (
            host.startswith("api.tokenfactory.") and host.endswith(".nebius.com")
        )
        if (parsed.scheme != "https" or not official_host or parsed.username or parsed.password
                or port not in (None, 443) or parsed.query or parsed.fragment
                or parsed.path.rstrip("/") != "/v1"):
            raise ConfigurationError("NEBIUS_BASE_URL must be an official HTTPS Token Factory /v1/ URL.")
        if any(char.isspace() for char in self.api_key):
            raise ConfigurationError("The API key contains whitespace. Copy it again into .env.")
        if require_model and not is_nemotron(self.model):
            raise ConfigurationError(
                "Set NEBIUS_MODEL to an exact nvidia/ Nemotron ID from --models. No other provider is used."
            )


def is_nemotron(model: str) -> bool:
    return model.lower().startswith("nvidia/") and "nemotron" in model.lower()


def load_settings() -> Settings:
    load_dotenv(ROOT / ".env", override=False, interpolate=False)
    return Settings(
        api_key=os.getenv("NEBIUS_API_KEY", "").strip(),
        base_url=os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/").strip().rstrip("/") + "/",
        model=os.getenv("NEBIUS_MODEL", "").strip(),
    )
