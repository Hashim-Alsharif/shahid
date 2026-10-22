"""Local/server-shell operator commands; no public administration endpoint."""

import argparse
import getpass
import json
import secrets
from pathlib import Path

from dotenv import load_dotenv

from shahid.hosting import DemoStore, hash_access_code, load_hosting_settings
from shahid.settings import ConfigurationError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("hash-code", "status", "pause", "resume"))
    parser.add_argument("--env-file", type=Path, help="Private operator environment file; values are never printed")
    args = parser.parse_args()
    if args.action == "hash-code":
        code = getpass.getpass("New private judging code (16+ characters; empty = generate): ")
        if not code:
            code = secrets.token_urlsafe(24)
            print("Private access code (save privately; never commit):", code)
        print("SHAHID_ACCESS_CODE_HASH=" + hash_access_code(code))
        return 0
    if args.env_file:
        if not args.env_file.is_absolute() or not args.env_file.is_file():
            raise ConfigurationError("An existing absolute private environment path is required.")
        load_dotenv(args.env_file, override=True, interpolate=False)
    config = load_hosting_settings()
    if not config.hosted:
        raise ConfigurationError("Operator counters require hosted mode and its persistent database.")
    store = DemoStore(config)
    if args.action in ("pause", "resume"):
        store.pause(args.action == "pause")
    print(json.dumps(store.usage("operator-status"), indent=2))
    print("Counts are attempts, not a guaranteed dollar spending cap. No logs are stored here.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ConfigurationError as error:
        print(str(error))
        raise SystemExit(1) from None
