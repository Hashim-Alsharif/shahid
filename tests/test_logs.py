from datetime import datetime, timedelta, timezone

from shahid.logs import analyze_logs
from shahid.settings import ROOT


def line(seconds=0, *, target="/", status=200, ip="192.0.2.1", method="GET"):
    stamp = (datetime(2026, 10, 22, 9, tzinfo=timezone.utc) + timedelta(seconds=seconds)).strftime("%d/%b/%Y:%H:%M:%S %z")
    return f'{ip} - - [{stamp}] "{method} {target} HTTP/1.1" {status} 100 "-" "SyntheticAgent/1.0"'


def test_synthetic_normal_has_no_findings():
    report = analyze_logs((ROOT / "samples/normal.log").read_text())
    assert report["summary"]["valid_requests"] == 6
    assert report["findings"] == []
    assert report["ai_executed"] is False


def test_login_evidence_is_counted_and_references_real_lines():
    report = analyze_logs((ROOT / "samples/login_attempts.log").read_text())
    finding = report["findings"][0]
    assert finding["kind"] == "repeated_login_rejection"
    assert finding["supporting_requests"] == 8
    assert set(finding["evidence_ids"]) <= {e["id"] for e in report["evidence"]}
    assert "لا تثبت" in finding["interpretation"]


def test_bad_lines_preserve_original_line_numbers():
    report = analyze_logs("not a log\n\n" + line(target="/login", status=401))
    assert report["invalid_line_numbers"] == [1]
    assert report["evidence"][0]["id"] == "L0003"


def test_evidence_omits_ip_query_referrer_and_user_agent():
    report = analyze_logs(line(target="/account?token=private-value", ip="198.51.100.77"))
    assert "198.51.100.77" not in str(report)
    assert "private-value" not in str(report)
    assert "SyntheticAgent" not in str(report)
    assert report["evidence"][0]["path"] == "/account"


def test_encoded_sensitive_path_is_detected():
    report = analyze_logs(line(target="/%2Eenv", status=404) + "\n" + line(3, target="/.git/config", status=404))
    assert report["findings"][0]["kind"] == "sensitive_paths"


def test_widely_spaced_login_failures_do_not_trigger_one_minute_rule():
    report = analyze_logs("\n".join(line(i * 120, target="/login", status=401) for i in range(8)))
    assert report["findings"] == []


def test_unsorted_entries_are_analyzed_in_time_order():
    report = analyze_logs("\n".join(line(i, target="/login", status=401) for i in (20, 5, 15, 0, 10)))
    assert report["findings"][0]["supporting_requests"] == 5


def test_legitimate_burst_is_described_as_rate_not_confirmed_attack():
    report = analyze_logs("\n".join(line(i, target="/products", status=200) for i in range(12)))
    assert [f["kind"] for f in report["findings"]] == ["request_burst"]
    assert "استخدامًا مشروعًا" in report["findings"][0]["interpretation"]
