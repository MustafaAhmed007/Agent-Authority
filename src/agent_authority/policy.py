"""Deterministic policy-as-code evaluator."""
from __future__ import annotations
import fnmatch
from typing import Any, Dict, Iterable
from .models import AuthorizationRequest, Policy

def _matches(actual: Any, expected: Any) -> bool:
    if expected is None:
        return True
    if isinstance(expected, list):
        return any(_matches(actual, item) for item in expected)
    if isinstance(expected, str) and isinstance(actual, str):
        return fnmatch.fnmatch(actual, expected)
    return actual == expected

class PolicyEngine:
    def __init__(self, policies: Iterable[Policy] = ()):
        self.policies = sorted(list(policies), key=lambda p: p.priority, reverse=True)

    def add(self, policy: Policy) -> None:
        self.policies.append(policy)
        self.policies.sort(key=lambda p: p.priority, reverse=True)

    @staticmethod
    def _value(request: AuthorizationRequest, key: str) -> Any:
        roots = {
            "agent.id": request.identity.agent_id,
            "agent.role": request.identity.workload,
            "user": request.identity.owner_id,
            "action": request.action,
            "resource": request.resource,
            "environment": request.environment,
            "task": request.task_id,
            "cost": request.estimated_cost,
        }
        return roots.get(key, request.context.get(key))

    def matching(self, request: AuthorizationRequest) -> list[Policy]:
        result = []
        for policy in self.policies:
            if all(_matches(self._value(request, k), v) for k, v in policy.when.items()):
                result.append(policy)
        return result

    def evaluate(self, request: AuthorizationRequest) -> tuple[list[Policy], list[str], list[str]]:
        matched = self.matching(request)
        allow, deny = [], []
        for p in matched:
            ops = p.allow.get("operations", p.allow.get("actions", []))
            deny_ops = p.deny.get("operations", p.deny.get("actions", []))
            if not ops or request.action in ops or any(fnmatch.fnmatch(request.action, str(x)) for x in ops):
                allow.append(p.name)
            if request.action in deny_ops or any(fnmatch.fnmatch(request.action, str(x)) for x in deny_ops):
                deny.append(p.name)
        return matched, allow, deny
