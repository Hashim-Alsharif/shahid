"""Offline scenarios by default; --live sends ONE synthetic case to Nemotron."""

import argparse
import json
from datetime import datetime, timezone

from shahid.evaluation import cases, evaluate_case
from shahid.interpretation import InterpretationError
from shahid.nebius import NebiusError, TokenFactoryClient
from shahid.settings import ConfigurationError, ROOT, load_settings


def main() -> int:
    catalog = cases()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=["all", *[c["name"] for c in catalog]], default="all")
    parser.add_argument("--live", action="store_true", help="Consume credits for exactly one synthetic case, no retries")
    parser.add_argument("--language", choices=["ar", "en"], default="en")
    args = parser.parse_args()
    if args.live and args.case == "all":
        parser.error("--live requires one explicit --case; batch paid requests are not implicit")
    selected = [c for c in catalog if args.case in ("all", c["name"])]
    record = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "synthetic_only": True,
              "live_requested": args.live, "cases": [], "semantic_accuracy_measured": False}
    evidence = None
    for case in selected:
        result, evidence = evaluate_case(case)
        record["cases"].append(result)
        print(f"{'PASS' if result['passed'] else 'FAIL'} | {case['name']} | local rule/evidence checks")
    code = 0 if all(c["passed"] for c in record["cases"]) else 1
    if args.live and not code:
        try:
            settings = load_settings()
            settings.validate(require_model=True)
            record["prepared_evidence"] = evidence
            record["live"] = TokenFactoryClient(settings).interpret(evidence, args.language)
            record["human_quality_review"] = "required; not scored automatically"
            print("Live response/reference checks: PASS. Human review of prose is still required.")
            print("Model:", record["live"]["model"])
            print("Tokens:", record["live"]["usage"].get("total_tokens", "unknown"))
        except (ConfigurationError, InterpretationError, NebiusError) as error:
            record["live_error"] = {"code": getattr(error, "code", "configuration_error"),
                                    "metadata": getattr(error, "metadata", {})}
            print("Live evaluation failed:", record["live_error"]["code"])
            code = 2
    directory = ROOT / "reports/evaluation"
    directory.mkdir(parents=True, exist_ok=True)
    name = f"{args.case}-{args.language}.json" if args.live else "local.json"
    path = directory / name
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Report:", path)
    print("These are synthetic rule-contract checks, not an intrusion-detection accuracy score.")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
