"""Sample product code: a 13-week cash forecast (the app LedgerGate protects)."""
from decimal import Decimal, ROUND_HALF_EVEN

def money(x) -> Decimal:
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

def forecast(opening, inflows, outflows, weeks=13):
    bal, out = money(opening), []
    for w in range(weeks):
        bal = money(bal + money(inflows[w] if w < len(inflows) else 0) - money(outflows[w] if w < len(outflows) else 0))
        out.append(bal)
    return out

def runway_weeks(series, floor=0):
    for i, b in enumerate(series):
        if b < money(floor):
            return i
    return len(series)
