"""Local control plane for operational inspection, authorization and revocation."""
from __future__ import annotations
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from .authority import Authority
from .models import AuthorizationRequest

class ControlPlane:
    def __init__(self,authority:Authority,admin_secret:str|None=None): self.authority=authority; self.admin_secret=admin_secret or os.getenv("AUTHORITY_ADMIN_SECRET")
    def handler(self):
        authority=self.authority; secret=self.admin_secret
        class Handler(BaseHTTPRequestHandler):
            def _authorized(self): return secret is None or self.headers.get("Authorization")==f"Bearer {secret}"
            def _json(self,code,payload):
                body=json.dumps(payload,default=str).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
            def _body(self):
                length=int(self.headers.get("Content-Length","0")); return json.loads(self.rfile.read(length) or b"{}")
            def do_GET(self):
                path=urlparse(self.path).path
                if path=="/health": return self._json(200,{"ok":True})
                if not self._authorized(): return self._json(401,{"error":"unauthorized"})
                if path=="/v1/tokens": return self._json(200,[t.model_dump(mode="json") for t in authority.tokens.values()])
                if path=="/v1/events": return self._json(200,authority.ledger.snapshot())
                if path=="/v1/audit/verify":
                    ok,msg=authority.ledger.verify(); return self._json(200,{"valid":ok,"message":msg})
                return self._json(404,{"error":"not found"})
            def do_POST(self):
                if not self._authorized(): return self._json(401,{"error":"unauthorized"})
                path=urlparse(self.path).path
                if path.startswith("/v1/tokens/") and path.endswith("/revoke"): return self._json(200,{"revoked":authority.revoke(path.split("/")[3])})
                if path=="/v1/authorize":
                    body=self._body(); request=AuthorizationRequest.model_validate(body["request"]); decision=authority.authorize(body["token_id"],request); return self._json(200,decision.model_dump(mode="json"))
                return self._json(404,{"error":"not found"})
            def log_message(self,*_): pass
        return Handler
    def serve(self,host="127.0.0.1",port=8765): ThreadingHTTPServer((host,port),self.handler()).serve_forever()
