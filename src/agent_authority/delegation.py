"""Task-scoped agent-to-agent delegation."""
from __future__ import annotations
from .authority import Authority
from .models import AgentIdentity, Capability, AuthorityToken

class DelegationManager:
    def __init__(self, authority: Authority): self.authority = authority
    def delegate(self, source: AgentIdentity, target: AgentIdentity, task_id: str, capabilities: list[Capability], ttl_seconds: int = 600, max_actions: int = 20, max_cost: float = 0.0) -> AuthorityToken:
        if not source.owner_id == target.owner_id:
            raise PermissionError("cross-owner delegation denied")
        return self.authority.issue_token(target, task_id, capabilities, ttl_seconds, max_actions, max_cost)
