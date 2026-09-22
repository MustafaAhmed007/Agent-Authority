"""Minimal framework-neutral adapter protocol.
Concrete integrations should translate their framework callback into this interface.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol
from .mcp import MCPGateway, ToolCall

class AgentFrameworkAdapter(Protocol):
    def before_tool(self, tool: str, resource: str, arguments: dict[str, Any]) -> None: ...
    def after_tool(self, tool: str, result: Any) -> None: ...

@dataclass
class AuthorityAdapter:
    gateway: MCPGateway
    token_id: str
    identity: Any
    task_id: str

    def invoke(self, request_id: str, tool: str, resource: str, arguments: dict[str, Any], executor):
        call=ToolCall(tool=tool, resource=resource, arguments=arguments)
        decision, request=self.gateway.authorize(self.token_id, request_id, self.identity, self.task_id, call)
        return decision, request, (lambda: self.gateway.execute(self.token_id, request, executor))
