# Agent rules for this repo
- Money is Decimal, never float. Rounding is ROUND_HALF_EVEN.
- The deterministic gate (ledgergate/gate.py) is the source of truth; agents explain, never override.
- Agents may comment and open issues; only humans approve production for finance paths.
