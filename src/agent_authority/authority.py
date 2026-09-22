"""Authority kernel."""
from __future__ import annotations
import fnmatch
from datetime import timedelta
from typing import Any, Callable
from .crypto import Signer, random_id, sha256
from .ledger import AuditLedger
from .models import AgentIdentity, Capability, AuthorityToken, AuthorizationRequest, AuthorizationDecision, Decision, Policy, ExecutionEvent, VerificationResult, utcnow
from .policy import PolicyEngine
from .risk import RiskEngine

class Authority:
    def __init__(self, policies:list[Policy]|None=None, approval_callback:Callable[[AuthorizationRequest,AuthorizationDecision],bool]|None=None):
        self.signer=Signer()
        self.policy=PolicyEngine(policies or [])
        self.risk=RiskEngine()
        self.ledger=AuditLedger()
        self.approval_callback=approval_callback
        self.tokens:dict[str,AuthorityToken]={}
        self.verifications:dict[str,VerificationResult]={}

    def issue_identity(self,owner_id:str,model:str,runtime:str,version:str,workload:str="default")->AgentIdentity:
        return AgentIdentity(agent_id=random_id("agent"),owner_id=owner_id,model=model,runtime=runtime,version=version,session_id=random_id("session"),workload=workload)

    def issue_token(self,identity:AgentIdentity,task_id:str,capabilities:list[Capability],ttl_seconds:int=1200,max_actions:int=100,max_cost:float=0.0)->AuthorityToken:
        if ttl_seconds<=0 or max_actions<=0 or max_cost<0:
            raise ValueError("delegation bounds must be positive (except max_cost, which may be zero for unlimited)")
        token=AuthorityToken(token_id=random_id("aat"),subject=identity,capabilities=capabilities,task_id=task_id,expires_at=utcnow()+timedelta(seconds=ttl_seconds),max_actions=max_actions,max_cost=max_cost)
        self.tokens[token.token_id]=token
        return token

    def _capability_matches(self,t:AuthorityToken,r:AuthorizationRequest)->Capability|None:
        for c in t.capabilities:
            op_ok=not c.operations or any(fnmatch.fnmatch(r.action,str(p)) for p in c.operations)
            res_ok=not c.resources or any(fnmatch.fnmatch(r.resource,str(p)) for p in c.resources)
            if op_ok and res_ok:
                return c
        return None

    def authorize(self,token_id:str,r:AuthorizationRequest)->AuthorizationDecision:
        t=self.tokens.get(token_id)
        if not t:
            return AuthorizationDecision(request_id=r.request_id,decision=Decision.DENY,reasons=["authority token not found"])
        if not t.active:
            return AuthorizationDecision(request_id=r.request_id,decision=Decision.DENY,reasons=["authority token inactive, expired, revoked, or budget exhausted"])
        if r.identity.agent_id!=t.subject.agent_id or r.task_id!=t.task_id:
            return AuthorizationDecision(request_id=r.request_id,decision=Decision.DENY,reasons=["identity/task does not match delegated authority"])
        c=self._capability_matches(t,r)
        if not c:
            return AuthorizationDecision(request_id=r.request_id,decision=Decision.DENY,reasons=["capability not granted for requested action/resource"])
        matched,allows,denies=self.policy.evaluate(r)
        risk=self.risk.assess(r)
        reasons=[f"capability={c.name}",*risk.explanation]
        if denies:
            return AuthorizationDecision(request_id=r.request_id,decision=Decision.DENY,policy=denies[0],risk_score=risk.score,reasons=reasons+[f"policy denied: {denies[0]}"])
        if t.max_cost>0 and t.spent_cost+r.estimated_cost>t.max_cost:
            return AuthorizationDecision(request_id=r.request_id,decision=Decision.DENY,risk_score=risk.score,reasons=reasons+["cost budget exceeded"])
        approval=risk.score>=8 or bool(r.context.get("requires_approval")) or (r.environment=="production" and r.action in {"deploy","production.deploy"})
        policy_name=allows[0] if allows else (matched[0].name if matched else None)
        pending=AuthorizationDecision(request_id=r.request_id,decision=Decision.APPROVAL_REQUIRED,policy=policy_name,risk_score=risk.score,reasons=reasons+["human approval required"],required_approval=True)
        if approval:
            if self.approval_callback is None:
                return pending
            if not self.approval_callback(r,pending):
                return AuthorizationDecision(request_id=r.request_id,decision=Decision.DENY,policy=policy_name,risk_score=risk.score,reasons=reasons+["human approval denied"])
        return AuthorizationDecision(request_id=r.request_id,decision=Decision.ALLOW,policy=policy_name,risk_score=risk.score,reasons=reasons+["authorization granted"])

    def record_execution(self,token_id:str,r:AuthorizationRequest,d:AuthorizationDecision,result:str,metadata:dict[str,Any]|None=None)->ExecutionEvent:
        t=self.tokens[token_id]
        if d.decision==Decision.ALLOW:
            if not t.active or t.spent_cost+r.estimated_cost>t.max_cost>0:
                raise PermissionError("token budget exhausted before recording authorized execution")
            t.action_count+=1
            t.spent_cost+=r.estimated_cost
        e=ExecutionEvent(event_id=random_id("evt"),event_type="tool.call",request_id=r.request_id,task_id=r.task_id,agent_id=r.identity.agent_id,action=r.action,resource=r.resource,authorization=d.decision.value,policy=d.policy,payload_hash=sha256(r.model_dump()),result=result,metadata=metadata or {})
        return self.ledger.append(e)

    def verify_claim(self,claimed_success:bool,actual_success:bool,verifier:str,summary:str,evidence:dict[str,Any]|None=None)->VerificationResult:
        v=VerificationResult(verified=claimed_success==actual_success==True,verifier=verifier,summary=summary,evidence=evidence or {})
        self.verifications[random_id("proof")]=v
        return v

    def explain(self,d:AuthorizationDecision)->str:
        return "\n".join([d.decision.value,f"Policy: {d.policy or 'none'}",f"Risk: {d.risk_score}",*[f"- {x}" for x in d.reasons]])

    def revoke(self,token_id:str)->bool:
        t=self.tokens.get(token_id)
        if not t:return False
        t.revoked=True
        return True
