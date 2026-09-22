"""Authority kernel: identity, capability, policy, risk, approval, budgets, verification, audit."""
from __future__ import annotations
from typing import Callable, Any
from .crypto import Signer, random_id, sha256
from .ledger import AuditLedger
from .models import *
from .policy import PolicyEngine
from .risk import RiskEngine

class Authority:
    def __init__(self, policies: list[Policy] | None = None, approval_callback: Callable[[AuthorizationRequest, AuthorizationDecision], bool] | None = None):
        self.signer = Signer()
        self.policy = PolicyEngine(policies or [])
        self.risk = RiskEngine()
        self.ledger = AuditLedger()
        self.approval_callback = approval_callback
        self.tokens: dict[str, AuthorityToken] = {}
        self.verifications: dict[str, VerificationResult] = {}
        self._budgets: dict[str, float] = {}

    def issue_identity(self, owner_id: str, model: str, runtime: str, version: str, workload: str="default") -> AgentIdentity:
        return AgentIdentity(agent_id=random_id("agent"), owner_id=owner_id, model=model, runtime=runtime,
                             version=version, session_id=random_id("session"), workload=workload)

    def issue_token(self, identity: AgentIdentity, task_id: str, capabilities: list[Capability],
                    ttl_seconds: int=1200, max_actions: int=100, max_cost: float=0.0) -> AuthorityToken:
        token = AuthorityToken(token_id=random_id("aat"), subject=identity, capabilities=capabilities,
                              task_id=task_id, expires_at=utcnow()+timedelta(seconds=ttl_seconds),
                              max_actions=max_actions, max_cost=max_cost)
        self.tokens[token.token_id] = token
        return token

    def _capability_matches(self, token: AuthorityToken, request: AuthorizationRequest) -> Capability | None:
        for cap in token.capabilities:
            action_ok = not cap.operations or request.action in cap.operations or any(__import__("fnmatch").fnmatch.fnmatch(request.action, x) for x in cap.operations)
            resource_ok = not cap.resources or request.resource in cap.resources or any(__import__("fnmatch").fnmatch.fnmatch(request.resource, x) for x in cap.resources)
            if action_ok and resource_ok:
                return cap
        return None

    def authorize(self, token_id: str, request: AuthorizationRequest) -> AuthorizationDecision:
        token = self.tokens.get(token_id)
        reasons: list[str] = []
        if token is None:
            return AuthorizationDecision(request_id=request.request_id, decision=Decision.DENY, reasons=["authority token not found"])
        if not token.active:
            return AuthorizationDecision(request_id=request.request_id, decision=Decision.DENY, reasons=["authority token inactive, expired, revoked, or budget exhausted"])
        if request.identity.agent_id != token.subject.agent_id or request.task_id != token.task_id:
            return AuthorizationDecision(request_id=request.request_id, decision=Decision.DENY, reasons=["identity/task does not match delegated authority"])
        cap = self._capability_matches(token, request)
        if cap is None:
            return AuthorizationDecision(request_id=request.request_id, decision=Decision.DENY, reasons=["capability not granted for requested action/resource"])
        matched, allows, denies = self.policy.evaluate(request)
        risk = self.risk.assess(request)
        reasons.extend([f"capability={cap.name}", *risk.explanation])
        if denies:
            return AuthorizationDecision(request_id=request.request_id, decision=Decision.DENY, policy=denies[0], risk_score=risk.score, reasons=reasons+[f"policy denied: {denies[0]}"])
        approval = risk.score >= 8 or request.context.get("requires_approval", False)
        if request.environment == "production" and request.action in {"deploy", "production.deploy"}:
            approval = True
        policy_name = allows[0] if allows else (matched[0].name if matched else None)
        if approval and self.approval_callback is None:
            return AuthorizationDecision(request_id=request.request_id, decision=Decision.APPROVAL_REQUIRED, policy=policy_name, risk_score=risk.score, reasons=reasons+["human approval required"], required_approval=True)
        if approval:
            approved = bool(self.approval_callback(request, AuthorizationDecision(request_id=request.request_id, decision=Decision.APPROVAL_REQUIRED, policy=policy_name, risk_score=risk.score, reasons=reasons, required_approval=True)))
            if not approved:
                return AuthorizationDecision(request_id=request.request_id, decision=Decision.DENY, policy=policy_name, risk_score=risk.score, reasons=reasons+["human approval denied"])
        return AuthorizationDecision(request_id=request.request_id, decision=Decision.ALLOW, policy=policy_name, risk_score=risk.score, reasons=reasons+["authorization granted"])

    def record_execution(self, token_id: str, request: AuthorizationRequest, decision: AuthorizationDecision, result: str, metadata: dict[str, Any] | None=None) -> ExecutionEvent:
        token = self.tokens[token_id]
        token.action_count += 1
        token.spent_cost += request.estimated_cost
        event = ExecutionEvent(event_id=random_id("evt"), event_type="tool.call", request_id=request.request_id,
                               task_id=request.task_id, agent_id=request.identity.agent_id, action=request.action,
                               resource=request.resource, authorization=decision.decision.value, policy=decision.policy,
                               payload_hash=sha256(request.model_dump()), result=result, metadata=metadata or {})
        return self.ledger.append(event)

    def verify_claim(self, claimed_success: bool, actual_success: bool, verifier: str, summary: str, evidence: dict[str, Any] | None=None) -> VerificationResult:
        result = VerificationResult(verified=claimed_success == actual_success and actual_success, verifier=verifier,
                                    summary=summary, evidence=evidence or {})
        self.verifications[random_id("proof")] = result
        return result

    def explain(self, decision: AuthorizationDecision) -> str:
        return "\n".join([decision.decision.value, f"Policy: {decision.policy or 'none'}", f"Risk: {decision.risk_score}", *[f"- {r}" for r in decision.reasons]])

    def revoke(self, token_id: str) -> None:
        if token_id in self.tokens:
            self.tokens[token_id].revoked = True
