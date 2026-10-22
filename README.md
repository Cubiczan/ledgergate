# LedgerGate — a Supervised post-code release gate for finance software (GitLab Duo Agent Platform)

> Transcend Hackathon Showcase workspace for @sam1054 (DevPost: sam439). See the [onboarding issue](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/34995099/showcase/-/work_items/1).


Finance code (cash forecasts, payments, FX) fails in quiet ways: a `float` in a money path, a hard-coded FX rate, a leaked API key. LedgerGate puts a GitLab Duo agent flow plus a deterministic gate between "code merged" and "money moves".

**Autonomy level: Supervised.** Agents run tests, SAST, secret detection, the LedgerGate gate, explain findings on the MR and deploy to staging on their own; a human approves production for anything touching money logic.

## How it works
1. MR opened → GitLab CI: `unit` (pytest + JUnit), `SAST`, `Secret-Detection`.
2. `ledgergate` job diffs the MR and runs `ledgergate/gate.py` → `BLOCK` / `NEEDS_APPROVAL` / `PROMOTE_STAGING` / `AUTO_PROMOTE`, plus `ledgergate-report.md`.
3. Duo custom flow `.gitlab/duo/flows/ledgergate.yml` (trigger: mention / assign reviewer / pipeline event) reads the MR, pipeline and report, posts one plain-English MR note with fixes, and opens a remediation issue on BLOCK. It cannot override the gate, merge or deploy.
4. Main branch → `deploy_staging` automatically; `deploy_production` is manual (human outcome approval).

## Rules
| Rule | Severity | Catches |
|---|---|---|
| FIN-001 | high | `float()` in money paths |
| FIN-002 | medium | any change to sensitive money paths → finance-owner approval |
| SEC-001 | critical | hard-coded keys/passwords |
| QA-001 | high | failing tests |
| SAST * | from report | GitLab SAST findings |

## Run locally
```bash
pip install pytest && pytest -q
python3 -m ledgergate.gate samples/risky.diff   # BLOCK, exit 1
python3 -m ledgergate.gate samples/clean.diff   # PROMOTE_STAGING
```
## Set up on GitLab
Import the repo into your provisioned Transcend project, enable Duo Agent Platform, create a flow from AI → Flows → New flow with `.gitlab/duo/flows/ledgergate.yml`, enable triggers (Mention, Assign reviewer, Pipeline events). The samples' keys are fake test strings.

MIT licensed.
