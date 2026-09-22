"""Explainable runtime risk engine."""
from __future__ import annotations
from dataclasses import dataclass
from .models import AuthorizationRequest

BASE_RISK = {
    "read": 1, "search": 2, "branch.create": 3, "create_branch": 3,
    "write": 5, "modify": 5, "commit": 6, "github.commit.write": 6,
    "delete": 7, "push": 8, "github.push": 8, "merge": 9,
    "deploy": 10, "production.deploy": 10, "secrets.rotate": 10,
    "payment": 10, "financial.transaction": 10,
}

@dataclass(frozen=True)
class RiskAssessment:
    score: int
    factors: dict[str, int]
    explanation: list[str]

class RiskEngine:
    def assess(self, request: AuthorizationRequest) -> RiskAssessment:
        action_key = request.action.lower()
        base = BASE_RISK.get(action_key, 5)
        factors = {"action": base}
        score = base
        if request.environment.lower() == "production":
            score += 2; factors["production"] = 2
        if request.context.get("resource_sensitivity") in {"sensitive", "restricted", "secret"}:
            score += 2; factors["resource_sensitivity"] = 2
        if request.context.get("novelty"):
            score += 1; factors["novelty"] = 1
        if request.context.get("blast_radius") == "high":
            score += 2; factors["blast_radius"] = 2
        score = min(score, 10)
        explanation = [f"base action risk={base}"] + [f"{k} adds {v}" for k,v in factors.items() if k != "action"]
        return RiskAssessment(score, factors, explanation)
