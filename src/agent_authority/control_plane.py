"""Minimal local control plane for operational inspection and revocation."""
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from .authority import Authority

class ControlPlane:
    def __init__(self, authority: Authority): self.authority=authority

    def handler(self):
        authority=self.authority
        class Handler(BaseHTTPRequestHandler):
            def _json(self, code, payload):
                body=json.dumps(payload, default=str).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
            def do_GET(self):
                path=urlparse(self.path).path
                if path=="/health": return self._json(200,{"ok":True})
                if path=="/v1/tokens": return self._json(200,[t.model_dump(mode="json") for t in authority.tokens.values()])
                if path=="/v1/events": return self._json(200,authority.ledger.snapshot())
                if path=="/v1/audit/verify":
                    ok,msg=authority.ledger.verify(); return self._json(200,{"valid":ok,"message":msg})
                return self._json(404,{"error":"not found"})
            def do_POST(self):
                path=urlparse(self.path).path
                if path.startswith("/v1/tokens/") and path.endswith("/revoke"):
                    token_id=path.split("/")[3]; return self._json(200,{"revoked":authority.revoke(token_id)})
                return self._json(404,{"error":"not found"})
            def log_message(self, *_): pass
        return Handler

    def serve(self, host="127.0.0.1", port=8765):
        server=ThreadingHTTPServer((host,port),self.handler())
        server.serve_forever()
