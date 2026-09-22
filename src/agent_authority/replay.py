"""Replay and time-travel helpers over the audit stream."""
from __future__ import annotations
from .ledger import AuditLedger

class ReplayEngine:
    def __init__(self, ledger: AuditLedger): self.ledger = ledger
    def run(self, task_id: str | None = None) -> list[dict]:
        events = self.ledger.events if task_id is None else [e for e in self.ledger.events if e.task_id == task_id]
        return [e.model_dump(mode="json") for e in events]
    def inspect(self, event_id: str) -> dict:
        for event in self.ledger.events:
            if event.event_id == event_id: return event.model_dump(mode="json")
        raise KeyError(event_id)
