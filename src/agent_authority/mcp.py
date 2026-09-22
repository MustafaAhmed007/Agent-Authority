"""MCP-style tool authorization bridge.

This module is transport-neutral: integrations adapt their MCP request/response
objects into ToolCall and invoke Gateway.authorize/execute before dispatch.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
from .authority import Authority
from .models import AuthorizationRequest, Decision

@dataclass(frozen=True)
class ToolCall:
    tool: str
    resource: str
    arguments: dict[str, Any] = field(default_factory=dict)
    environment: str = "development"
    estimated_cost: float = 0.0
    context: dict[str, Any] = field(default_factory=dict)

class MCPGateway:
    def __init__(self, authority: Authority):
        self.authority = authority

    def authorize(self, token_id: str, request_id: str, identity: Any, task_id: str, call: ToolCall):
        request = AuthorizationRequest(
            request_id=request_id, identity=identity, task_id=task_id,
            action=call.tool, resource=call.resource, environment=call.environment,
            context=call.context, estimated_cost=call.estimated_cost,
        )
        return self.authority.authorize(token_id, request), request

    def execute(self, token_id: str, request: AuthorizationRequest, executor: Callable[[], Any]) -> Any:
        decision = self.authority.authorize(token_id, request)
        if decision.decision != Decision.ALLOW:
            self.authority.record_execution(token_id, request, decision, "blocked")
            raise PermissionError(self.authority.explain(decision))
        try:
            result = executor()
        except Exception as exc:
            self.authority.record_execution(token_id, request, decision, "failure", {"error": type(exc).__name__})
            raise
        self.authority.record_execution(token_id, request, decision, "success")
        return result
