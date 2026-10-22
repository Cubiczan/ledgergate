"""Deterministic release-gate engine. Duo agents propose; this decides."""
import json, re, sys
from dataclasses import dataclass, field, asdict

MONEY_PATTERNS = [r"\bfloat\(", r"round\(", r"\* ?0\.\d+", r"amount", r"balance", r"fx_?rate"]
SENSITIVE_PATHS = ("ledgergate/forecast.py", "payments/", "ledger/", "fx/")

@dataclass
class Finding:
    rule: str; severity: str; detail: str

@dataclass
class Verdict:
    decision: str; risk: int; findings: list = field(default_factory=list); summary: str = ""

def scan_diff(diff: str):
    f, cur = [], None
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            cur = line[6:]
        elif line.startswith("+") and not line.startswith("+++") and cur:
            if cur.endswith(".py") and re.search(r"\bfloat\(", line) and any(cur.startswith(p) for p in SENSITIVE_PATHS):
                f.append(Finding("FIN-001 float-money", "high", f"{cur}: float used in money path: {line[1:].strip()}"))
            if re.search(r"(api[_-]?key|secret|password)\s*=\s*['\"][^'\"]{8,}", line, re.I):
                f.append(Finding("SEC-001 hardcoded-secret", "critical", f"{cur}: possible secret"))
    touched = {l[6:] for l in diff.splitlines() if l.startswith("+++ b/")}
    if any(t.startswith(SENSITIVE_PATHS) for t in touched):
        f.append(Finding("FIN-002 sensitive-path", "medium", "change touches money logic; finance owner approval required"))
    return f

def evaluate(diff: str, junit_failures: int = 0, sast: list | None = None, autonomy: str = "supervised") -> Verdict:
    findings = scan_diff(diff)
    if junit_failures:
        findings.append(Finding("QA-001 tests", "high", f"{junit_failures} failing test(s)"))
    for s in sast or []:
        findings.append(Finding("SAST " + s.get("id", "?"), s.get("severity", "medium").lower(), s.get("message", "")))
    w = {"critical": 60, "high": 30, "medium": 10, "low": 3}
    risk = min(100, sum(w.get(x.severity, 5) for x in findings))
    if any(x.severity == "critical" for x in findings) or risk >= 60:
        d = "BLOCK"
    elif risk >= 10 or autonomy == "assisted":
        d = "NEEDS_APPROVAL"
    else:
        d = "AUTO_PROMOTE" if autonomy == "hands-off" else "PROMOTE_STAGING"
    v = Verdict(d, risk, [asdict(x) for x in findings])
    v.summary = f"LedgerGate verdict: {d} (risk {risk}/100, {len(findings)} finding(s))"
    return v

def main(argv=None):
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("diff"); p.add_argument("--junit-failures", type=int, default=0)
    p.add_argument("--sast"); p.add_argument("--autonomy", default="supervised")
    a = p.parse_args(argv)
    sast = json.load(open(a.sast)).get("vulnerabilities", []) if a.sast else []
    v = evaluate(open(a.diff).read(), a.junit_failures, sast, a.autonomy)
    print(json.dumps(asdict(v), indent=2))
    with open("ledgergate-report.md", "w") as fh:
        fh.write(f"## {v.summary}\n\n| Rule | Severity | Detail |\n|---|---|---|\n")
        for x in v.findings:
            fh.write(f"| {x['rule']} | {x['severity']} | {x['detail']} |\n")
    return 1 if v.decision == "BLOCK" else 0

if __name__ == "__main__":
    sys.exit(main())
