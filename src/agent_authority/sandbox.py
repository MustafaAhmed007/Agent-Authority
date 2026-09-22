"""Sandbox abstraction for production execution adapters."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class SandboxLimits:
    timeout_seconds: float = 30.0
    memory_mb: int = 512
    network: bool = False
    filesystem: str = "isolated"

class Sandbox:
    def __init__(self, limits: SandboxLimits | None = None):
        self.limits = limits or SandboxLimits()

    def run(self, operation: Callable[[], Any]) -> Any:
        # This is an adapter boundary, not a fake security sandbox.
        # Integrations must replace it with OS/container isolation before untrusted execution.
        return operation()

    @property
    def production_ready(self) -> bool:
        return False
