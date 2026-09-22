"""Tool trust registry and risk feedback primitives."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ToolTrust:
    tool: str
    publisher: str
    verified: bool = False
    risk_floor: int = 0
    allowed_environments: set[str] = field(default_factory=lambda: {"development"})
    evidence: list[str] = field(default_factory=list)

class ToolTrustRegistry:
    def __init__(self): self._tools: dict[str, ToolTrust] = {}
    def register(self, trust: ToolTrust) -> None: self._tools[trust.tool] = trust
    def get(self, tool: str) -> ToolTrust | None: return self._tools.get(tool)
    def is_allowed(self, tool: str, environment: str) -> bool:
        item=self.get(tool)
        return bool(item and item.verified and environment in item.allowed_environments)
    def snapshot(self) -> list[dict[str, Any]]:
        return [{"tool":x.tool,"publisher":x.publisher,"verified":x.verified,"risk_floor":x.risk_floor,"allowed_environments":sorted(x.allowed_environments),"evidence":list(x.evidence)} for x in self._tools.values()]
