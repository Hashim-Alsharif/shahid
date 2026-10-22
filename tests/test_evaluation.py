import json
from zipfile import ZipFile

import pytest

from scripts.build_release import build_bundle
from shahid.evaluation import cases, evaluate_case


@pytest.mark.parametrize("case", cases(), ids=lambda c: c["name"])
def test_synthetic_rule_contract(case):
    result, _ = evaluate_case(case)
    assert result["passed"], result


def test_test_build_excludes_credentials_reports_and_verifies_manifest(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "reports").mkdir()
    (tmp_path / ".env").write_text("NEBIUS_API_KEY=private-test-credential\n")
    (tmp_path / ".env.example").write_text("NEBIUS_API_KEY=\n")
    (tmp_path / "README.md").write_text("Synthetic release instructions")
    (tmp_path / "app/main.py").write_text("print('synthetic')")
    (tmp_path / "reports/private.txt").write_text("do not export")
    target = tmp_path / "dist/build.zip"
    result = build_bundle(tmp_path, target)
    with ZipFile(target) as archive:
        names = archive.namelist()
        assert "shahid/.env.example" in names
        assert "shahid/.env" not in names
        assert not any("reports/" in name for name in names)
        assert b"private-test-credential" not in b"".join(archive.read(name) for name in names)
        manifest = json.loads(archive.read("shahid/source-manifest.json"))
        assert len(manifest["files"]) == result["file_count"]


def test_test_build_refuses_a_key_copied_into_source_without_printing_it(tmp_path):
    secret = "private-test-credential"
    (tmp_path / ".env").write_text("NEBIUS_API_KEY=" + secret)
    (tmp_path / "README.md").write_text("Example leaked value: " + secret)
    target = tmp_path / "dist/build.zip"
    with pytest.raises(ValueError) as error:
        build_bundle(tmp_path, target)
    assert secret not in str(error.value)
    assert not target.exists()


def test_test_build_requires_blank_example_key(tmp_path):
    (tmp_path / ".env.example").write_text("NEBIUS_API_KEY=accidental-example-secret\n")
    with pytest.raises(ValueError, match="empty API key"):
        build_bundle(tmp_path, tmp_path / "dist/build.zip")
