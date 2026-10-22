"""Check local config, list models, or make ONE small synthetic smoke request."""

import argparse
import json
from datetime import datetime, timezone

from shahid.nebius import NebiusError, TokenFactoryClient
from shahid.settings import ConfigurationError, ROOT, load_settings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-config", action="store_true", help="Validate .env without a network call")
    mode.add_argument("--models", action="store_true", help="List NVIDIA Nemotron IDs returned by your account")
    mode.add_argument("--chat", action="store_true", help="Send one short paid/credit-backed synthetic request")
    args = parser.parse_args()
    try:
        settings = load_settings()
        settings.validate(require_model=args.chat)
        if args.check_config:
            print("Local configuration: key present (hidden). No network request was made.")
            print("Model:", settings.model or "Not selected yet; use --models.")
            return 0
        client = TokenFactoryClient(settings)
        if args.models:
            models = client.list_nemotron_models()
            if not models:
                print("No NVIDIA Nemotron IDs were returned. Check account/project/model access; no substitute was selected.")
                return 1
            print("NVIDIA Nemotron model IDs returned by Token Factory:")
            for model in models:
                print(model)
            print("\nCopy one exact ID to NEBIUS_MODEL in .env. A listing alone does not prove inference access.")
            return 0
        result = client.smoke_chat()
        result.update({"provider": "Nebius Token Factory", "live_request": True,
                       "synthetic_prompt_only": True, "executed_at_utc": datetime.now(timezone.utc).isoformat()})
        directory = ROOT / "reports" / "nebius"
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / "smoke-last.json"
        destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("Live inference: PASS (a non-empty Nemotron answer was returned).")
        print("Model:", result["response_model"])
        print("Answer:", result["answer"])
        print("Usage:", json.dumps(result["usage"], ensure_ascii=False))
        print("Evidence:", destination)
        return 0
    except (ConfigurationError, NebiusError) as error:
        print("Check failed:", error)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
