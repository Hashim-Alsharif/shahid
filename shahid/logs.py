"""Parse a limited Nginx combined-log format and produce local evidence.

Rules describe observations; they do not establish that a compromise occurred.
"""

import ipaddress
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import unquote

PATTERN = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<target>[^"\s]+) HTTP/[\d.]+" '
    r'(?P<status>[1-5]\d{2}) (?:\d+|-) "[^"\r\n]*" "[^"\r\n]*"$'
)


@dataclass(frozen=True)
class Entry:
    line: int
    source: str
    timestamp: datetime
    method: str
    path: str
    status: int

    @property
    def evidence_id(self) -> str:
        return f"L{self.line:04d}"


def parse_logs(text: str) -> tuple[list[Entry], list[int]]:
    entries, invalid = [], []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        match = PATTERN.fullmatch(line.strip())
        try:
            if not match:
                raise ValueError("Unsupported format")
            ipaddress.ip_address(match["ip"])
            timestamp = datetime.strptime(match["time"], "%d/%b/%Y:%H:%M:%S %z")
            if not match["target"].startswith("/"):
                raise ValueError("Only origin-form request targets are supported")
            # Query strings and fragments are excluded from evidence. Full raw
            # logs, referrers and user agents are not returned to the UI.
            path = match["target"].split("?", 1)[0].split("#", 1)[0]
            entries.append(Entry(number, match["ip"], timestamp, match["method"], path, int(match["status"])))
        except ValueError:
            invalid.append(number)
    return entries, invalid


def peak_window(entries: list[Entry]) -> list[Entry]:
    ordered = sorted(entries, key=lambda entry: entry.timestamp)
    start, best = 0, []
    for end, entry in enumerate(ordered):
        while (entry.timestamp - ordered[start].timestamp).total_seconds() > 60:
            start += 1
        if end - start + 1 > len(best):
            best = ordered[start:end + 1]
    return best


def analyze_logs(text: str) -> dict:
    entries, invalid = parse_logs(text)
    aliases = {source: f"source-{n}" for n, source in enumerate(dict.fromkeys(e.source for e in entries), 1)}
    grouped = defaultdict(list)
    for entry in entries:
        grouped[entry.source].append(entry)
    findings = []

    def add(kind: str, title: str, source: str, evidence: list[Entry], interpretation: str):
        findings.append({"id": f"F{len(findings) + 1}", "kind": kind, "title": title,
                         "source_id": aliases[source], "supporting_requests": len(evidence),
                         "evidence_ids": [e.evidence_id for e in evidence[:20]],
                         "interpretation": interpretation})

    for source, source_entries in grouped.items():
        login = peak_window([e for e in source_entries if e.path.rstrip("/").lower() in ("/login", "/api/login", "/signin")
                             and e.status in (401, 403)])
        if len(login) >= 5:
            add("repeated_login_rejection", "طلبات دخول مرفوضة متكررة خلال دقيقة", source, login,
                "قد تستحق مراجعة سجل المصادقة. استجابات 401 و403 وحدها لا تثبت تخمين كلمات المرور أو نجاح اختراق.")
        sensitive = [e for e in source_entries if any(unquote(e.path).lower().startswith(path)
                     for path in ("/.env", "/.git/", "/wp-admin", "/phpmyadmin"))]
        if len(sensitive) >= 2:
            add("sensitive_paths", "طلبات لمسارات حساسة", source, sensitive,
                "تحقق من غرض الطلبات وإعداد الخادم؛ طلب المسار لا يثبت أن الملف موجود أو أن بيانات تسربت.")
        burst = peak_window(source_entries)
        if len(burst) >= 12:
            add("request_burst", "كثافة طلبات خلال دقيقة", source, burst,
                "ملاحظة عن المعدل فقط؛ قد تمثل استخدامًا مشروعًا أو مصدرًا مشتركًا، ولا تكفي لإثبات هجوم.")

    return {
        "mode": "local_rules_only", "ai_executed": False,
        "summary": {"valid_requests": len(entries), "invalid_lines": len(invalid),
                    "unique_sources": len(aliases), "status_counts": dict(Counter(str(e.status) for e in entries))},
        "findings": findings,
        "evidence": [{"id": e.evidence_id, "line": e.line, "source_id": aliases[e.source],
                      "time": e.timestamp.isoformat(), "method": e.method, "path": e.path, "status": e.status}
                     for e in entries],
        "invalid_line_numbers": invalid,
        "scope": "Prototype thresholds on Nginx combined access logs. No compromise is confirmed. "
                 "IPs are replaced with local aliases and URL query strings are removed; paths may still contain sensitive values.",
    }
