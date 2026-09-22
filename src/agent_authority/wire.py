"""Signed wire representation for authority decisions."""
from __future__ import annotations
from .crypto import Signer
from .models import AuthorizationDecision

class SignedDecision:
    def __init__(self, signer: Signer): self.signer=signer
    def issue(self, decision: AuthorizationDecision) -> dict:
        payload=decision.model_dump(mode="json")
        return {"payload":payload,"signature":self.signer.sign(payload)}
    def verify(self, envelope: dict) -> bool:
        return self.signer.verify(envelope["payload"], envelope["signature"])
