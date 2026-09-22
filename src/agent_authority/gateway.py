"""Controlled execution gate."""
from __future__ import annotations
from typing import Any, Callable
from .authority import Authority
from .models import AuthorizationRequest, Decision

class ExecutionGate:
    def __init__(self, authority: Authority):
        self.authority=authority

    def run(self, token_id:str, request:AuthorizationRequest, executor:Callable[[],Any])->Any:
        decision=self.authority.authorize(token_id,request)
        if decision.decision != Decision.ALLOW:
            self.authority.record_execution(token_id,request,decision,"blocked")
            raise PermissionError(self.authority.explain(decision))
        try:
            result=executor()
        except Exception as exc:
            self.authority.record_execution(token_id,request,decision,"failure",{"error":type(exc).__name__})
            raise
        self.authority.record_execution(token_id,request,decision,"success")
        return result
