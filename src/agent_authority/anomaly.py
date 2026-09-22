"""Deterministic anomaly signals for authority telemetry."""
from __future__ import annotations
from collections import Counter
from .models import ExecutionEvent

class AnomalyDetector:
    def inspect(self, events: list[ExecutionEvent]) -> list[dict]:
        alerts=[]
        by_agent=Counter(e.agent_id for e in events if e.result=="success")
        for agent,count in by_agent.items():
            if count >= 100:
                alerts.append({"type":"high_volume","agent_id":agent,"count":count})
        for e in events:
            if e.authorization=="DENY" and e.result=="success":
                alerts.append({"type":"authorization_integrity","event_id":e.event_id,"severity":"critical"})
        return alerts
