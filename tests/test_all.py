from ledgergate.forecast import forecast, runway_weeks, money
from ledgergate.gate import evaluate

def test_forecast_decimal():
    s = forecast(1000, [0.1]*13, [0.2]*13)
    assert s[-1] == money(998.70)

def test_runway():
    assert runway_weeks(forecast(100, [], [30]*13)) == 3

def test_clean_diff_promotes():
    assert evaluate("+++ b/README.md\n+docs").decision == "PROMOTE_STAGING"

def test_float_money_needs_review():
    d = "+++ b/ledgergate/forecast.py\n+    bal = float(bal) * 1.1\n"
    v = evaluate(d); assert v.decision in ("NEEDS_APPROVAL", "BLOCK") and v.risk >= 40

def test_secret_blocks():
    assert evaluate("+++ b/app.py\n+API_KEY = 'not-a-real-key-123456'\n").decision == "BLOCK"
