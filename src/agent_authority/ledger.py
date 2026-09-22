"""Tamper-evident append-only execution ledger."""
from __future__ import annotations
from .crypto import sha256
from .models import ExecutionEvent

class AuditLedger:
    def __init__(self):
        self.events: list[ExecutionEvent] = []
        self._head = "GENESIS"

    def append(self, event: ExecutionEvent) -> ExecutionEvent:
        event.previous_hash = self._head
        event.event_hash = sha256(event.model_dump(mode="json", exclude={"event_hash"}))
        self._head = event.event_hash
        self.events.append(event)
        return event

    def verify(self) -> tuple[bool, str]:
        previous = "GENESIS"
        for event in self.events:
            if event.previous_hash != previous:
                return False, f"broken previous hash at {event.event_id}"
            expected = sha256(event.model_dump(mode="json", exclude={"event_hash"}))
            if expected != event.event_hash:
                return False, f"tampered event at {event.event_id}"
            previous = event.event_hash
        return True, "audit chain valid"

    def snapshot(self) -> list[dict]:
        return [event.model_dump(mode="json") for event in self.events]
