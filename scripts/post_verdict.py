"""Post the deterministic LedgerGate verdict to the merge request as a note (read by the Duo flow)."""
import json, os, sys, urllib.request
v = json.load(open("verdict.json"))
rows = "\n".join(f"| {f['rule']} | {f['severity']} | {f['detail']} |" for f in v["findings"]) or "| - | - | no findings |"
body = f"""<!-- ledgergate-verdict -->
## LedgerGate gate verdict (deterministic, from CI)

**Decision: {v['decision']}** | **Risk: {v['risk']}/100** | Pipeline: {os.environ.get('CI_PIPELINE_URL','')} | Job: {os.environ.get('CI_JOB_URL','')} | Commit: `{os.environ.get('CI_COMMIT_SHORT_SHA','')}`

| Rule | Severity | Detail |
|---|---|---|
{rows}

_This note is the confirmed gate verdict. Agents may explain it but never override it._"""
tok = os.environ.get("LEDGERGATE_BOT_TOKEN")
if not tok:
    print("LEDGERGATE_BOT_TOKEN not set; skipping MR note"); sys.exit(0)
url = f"{os.environ['CI_API_V4_URL']}/projects/{os.environ['CI_PROJECT_ID']}/merge_requests/{os.environ['CI_MERGE_REQUEST_IID']}/notes"
req = urllib.request.Request(url, json.dumps({"body": body}).encode(), {"PRIVATE-TOKEN": tok, "Content-Type": "application/json"})
print("posted verdict note", json.load(urllib.request.urlopen(req))["id"])
