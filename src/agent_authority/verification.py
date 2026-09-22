"""Independent outcome verification contracts."""
from __future__ import annotations
from typing import Any, Callable
from .models import VerificationResult

class Verifier:
    def verify(self, claimed: Any, observed: Any, check: Callable[[Any, Any], bool], verifier_name: str = "custom") -> VerificationResult:
        ok = bool(check(claimed, observed))
        return VerificationResult(verified=ok, verifier=verifier_name, summary="independent verification passed" if ok else "independent verification failed", evidence={"claimed": claimed, "observed": observed})
