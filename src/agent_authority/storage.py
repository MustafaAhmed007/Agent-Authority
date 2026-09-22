"""Persistence contracts. The kernel remains storage-independent."""
from __future__ import annotations
from typing import Protocol
from .models import AuthorityToken, ExecutionEvent

class AuthorityStore(Protocol):
    def save_token(self, token: AuthorityToken) -> None: ...
    def get_token(self, token_id: str) -> AuthorityToken | None: ...
    def append_event(self, event: ExecutionEvent) -> None: ...
    def list_events(self, task_id: str | None = None) -> list[ExecutionEvent]: ...

class MemoryStore:
    def __init__(self): self.tokens={}; self.events=[]
    def save_token(self, token): self.tokens[token.token_id]=token
    def get_token(self, token_id): return self.tokens.get(token_id)
    def append_event(self, event): self.events.append(event)
    def list_events(self, task_id=None): return [e for e in self.events if task_id is None or e.task_id==task_id]
