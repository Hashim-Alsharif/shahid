"""Build a source test bundle from explicit paths, without .env or reports."""

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from dotenv import dotenv_values

from shahid.settings import ROOT

ROOT_FILES = {"README.md", "LICENSE", "requirements.txt", "requirements-lock.txt", ".env.example", ".gitignore", ".gitattributes"}
SOURCE_DIRS = ("app", "shahid", "scripts", "samples", "tests", "docs", ".github")
EXTENSIONS = {".py", ".js", ".css", ".html", ".md", ".json", ".log", ".yml", ".yaml", ".png", ".svg"}


def source_files(root: Path) -> list[Path]:
    candidates = [root / name for name in ROOT_FILES if (root / name).is_file()]
    for directory in SOURCE_DIRS:
        if not (root / directory).exists():
            continue
        for path in (root / directory).rglob("*"):
            rel = path.relative_to(root)
            if any(part in ("__pycache__", ".pytest_cache") or
                   (part.startswith(".") and part != ".github") for part in rel.parts):
                continue
            if path.is_file() and path.suffix.lower() in EXTENSIONS:
                candidates.append(path)
    resolved_root = root.resolve()
    for path in candidates:
        if path.is_symlink() or not path.resolve().is_relative_to(resolved_root):
            raise ValueError("Refusing a source path outside the project")
    return sorted(set(candidates), key=lambda p: p.relative_to(root).as_posix())


def build_bundle(root: Path, destination: Path) -> dict:
    files = source_files(root)
    secret = dotenv_values(root / ".env", interpolate=False).get("NEBIUS_API_KEY", "")
    secret_bytes = secret.encode("utf-8") if secret else None
    content = []
    for path in files:
        data = path.read_bytes()
        if secret_bytes and secret_bytes in data:
            # Deliberately do not print the key, matched contents or source line.
            raise ValueError("Configured API key detected in release source; bundle not written")
        if path.name == ".env.example" and dotenv_values(path, interpolate=False).get("NEBIUS_API_KEY"):
            raise ValueError(".env.example must contain an empty API key")
        content.append((path.relative_to(root).as_posix(), data))
    manifest = {"format": 1, "kind": "source-test-build", "files": [
        {"path": name, "sha256": hashlib.sha256(data).hexdigest()} for name, data in content
    ], "excluded": [".env", ".git", ".venv", "reports", "dist", "uploads", "__pycache__"]}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in content + [("source-manifest.json", json.dumps(manifest, indent=2).encode("utf-8"))]:
            entry = ZipInfo("shahid/" + name)
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, data)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix(".sha256").write_text(f"{digest}  {destination.name}\n", encoding="utf-8")
    return {"file_count": len(content), "sha256": digest, "configured_key_exact_match_absent": True}


def main() -> int:
    destination = ROOT / "dist/shahid-test-build.zip"
    try:
        result = build_bundle(ROOT, destination)
    except ValueError as error:
        print("Build failed:", error)
        return 1
    print("Test build:", destination)
    print("Source files:", result["file_count"])
    print("SHA256:", result["sha256"])
    print(".env/reports excluded; configured key exact-match scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
