"""HTTP-free authority service primitives for embedding behind any transport."""
from __future__ import annotations
from dataclasses import dataclass
from .authority import Authority
from .models import AuthorizationRequest, AuthorizationDecision

@dataclass
class AuthorityService:
    authority: Authority

    def authorize(self, token_id: str, request: AuthorizationRequest) -> AuthorizationDecision:
        return self.authority.authorize(token_id, request)

    def revoke(self, token_id: str) -> bool:
        return self.authority.revoke(token_id)

    def explain(self, decision: AuthorizationDecision) -> str:
        return self.authority.explain(decision)
