"""Fixed synthetic scenarios. A rule-contract check is not detection accuracy."""

import json

from shahid.interpretation import prepare_evidence
from shahid.logs import analyze_logs
from shahid.settings import ROOT


def cases() -> list[dict]:
    return json.loads((ROOT / "samples/cases.json").read_text(encoding="utf-8"))


def evaluate_case(case: dict) -> tuple[dict, dict]:
    text = (ROOT / "samples" / f"{case['name']}.log").read_text(encoding="utf-8")
    report = analyze_logs(text)
    actual = {k: report["summary"][k] for k in ("valid_requests", "invalid_lines", "unique_sources")}
    actual["finding_kinds"] = [f["kind"] for f in report["findings"]]
    actual["evidence_ids"] = [e["id"] for e in report["evidence"]]
    known = set(actual["evidence_ids"])
    references_valid = all(set(f["evidence_ids"]) <= known for f in report["findings"])
    prepared = prepare_evidence(report)
    serialized = json.dumps(prepared)
    privacy_markers_absent = all(marker not in serialized for marker in (
        "192.0.2.", "198.51.100.", "203.0.113.", "SYNTHETIC_QUERY_SECRET",
        "SYNTHETIC_REFERRER", "SYNTHETIC_USER_AGENT",
    ))
    result = {"case": case["name"], "passed": actual == case["expected"] and references_valid and privacy_markers_absent,
              "expected": case["expected"], "actual": actual,
              "references_valid": references_valid, "privacy_markers_absent": privacy_markers_absent,
              "synthetic_context": case["context"]}
    return result, prepared
