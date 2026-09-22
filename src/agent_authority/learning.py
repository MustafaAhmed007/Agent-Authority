"""Feedback loop for authority decisions; suggestions never self-grant authority."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter

@dataclass
class Feedback:
    action: str
    outcome: str
    risk_score: int
    verified: bool

@dataclass
class LearningEngine:
    history: list[Feedback] = field(default_factory=list)
    def observe(self, feedback: Feedback) -> None: self.history.append(feedback)
    def summary(self) -> dict:
        outcomes=Counter(x.outcome for x in self.history)
        verified=sum(x.verified for x in self.history)
        return {"samples":len(self.history),"outcomes":dict(outcomes),"verified_rate":(verified/len(self.history) if self.history else 0.0)}
    def suggestions(self) -> list[dict]:
        # Suggestions are advisory only. They cannot mutate policy or increase privilege.
        by_action={}
        for x in self.history: by_action.setdefault(x.action,[]).append(x)
        out=[]
        for action,items in by_action.items():
            failures=sum(x.outcome=="failure" for x in items)
            if failures: out.append({"action":action,"suggestion":"review policy/risk controls","failure_count":failures})
        return out
