#!/bin/sh
# Smoke-check the live LedgerGate deployment: UI up, API healthy, gate verdicts correct.
set -eu
U="${LEDGERGATE_URL:?}"
curl -fsS -o /dev/null "$U/"
curl -fsS "$U/api/verdict" | grep -q '"status": "ok"'
curl -fsS -X POST "$U/api/verdict" -H 'Content-Type: application/json' \
  -d '{"diff":"+++ b/README.md\n+docs\n"}' | tee smoke.json | grep -q PROMOTE_STAGING
echo "LedgerGate live at $U: OK"
