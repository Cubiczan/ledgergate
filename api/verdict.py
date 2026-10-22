import json, os, sys
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ledgergate.gate import evaluate

class handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        self._send(200, {"service": "LedgerGate", "status": "ok", "usage": "POST {diff, autonomy} to /api/verdict"})
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        if n > 200_000: return self._send(413, {"error": "diff too large"})
        try: body = json.loads(self.rfile.read(n) or b"{}")
        except Exception: return self._send(400, {"error": "invalid JSON"})
        v = evaluate(str(body.get("diff", "")), autonomy=body.get("autonomy", "supervised"))
        self._send(200, asdict(v))
