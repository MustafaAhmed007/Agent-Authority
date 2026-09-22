"""Framework-neutral adapters with concrete helpers for common agent runtimes."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
from .gateway import ExecutionGate
from .models import AuthorizationRequest

@dataclass
class AgentRuntimeAdapter:
    name: str
    gate: ExecutionGate
    token_id: str
    identity: Any
    task_id: str

    def call(self, action: str, resource: str, fn: Callable[[], Any], **context: Any) -> Any:
        request=AuthorizationRequest(request_id=f"{self.name}:{action}", identity=self.identity, task_id=self.task_id, action=action, resource=resource, context=context)
        return self.gate.run(self.token_id, request, fn)

class LangGraphAdapter(AgentRuntimeAdapter):
    name="langgraph"
class CrewAIAdapter(AgentRuntimeAdapter):
    name="crewai"
class OpenHandsAdapter(AgentRuntimeAdapter):
    name="openhands"
class ClaudeCodeAdapter(AgentRuntimeAdapter):
    name="claude-code"
class CodexAdapter(AgentRuntimeAdapter):
    name="codex"
class OpenCodeAdapter(AgentRuntimeAdapter):
    name="opencode"
