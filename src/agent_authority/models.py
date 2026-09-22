"""Core Agent Authority contracts."""
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class Decision(str, Enum):
    ALLOW="ALLOW"; DENY="DENY"; APPROVAL_REQUIRED="APPROVAL_REQUIRED"; SANITIZE="SANITIZE"; RATE_LIMIT="RATE_LIMIT"

class AgentIdentity(BaseModel):
    model_config=ConfigDict(extra="forbid")
    agent_id:str
    owner_id:str
    model:str
    runtime:str
    version:str
    session_id:str
    workload:str="default"
    issued_at:datetime=Field(default_factory=utcnow)

class Capability(BaseModel):
    model_config=ConfigDict(extra="forbid")
    name:str
    operations:list[str]=Field(default_factory=list)
    resources:list[str]=Field(default_factory=list)
    constraints:dict[str,Any]=Field(default_factory=dict)

class AuthorityToken(BaseModel):
    model_config=ConfigDict(extra="forbid")
    token_id:str
    subject:AgentIdentity
    capabilities:list[Capability]
    task_id:str
    expires_at:datetime
    max_actions:int=100
    max_cost:float=0.0
    spent_cost:float=0.0
    action_count:int=0
    revoked:bool=False
    @property
    def active(self)->bool:
        return (not self.revoked and utcnow()<self.expires_at
                and self.action_count<self.max_actions
                and (self.max_cost<=0 or self.spent_cost+1e-12<self.max_cost))

class AuthorizationRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    request_id:str
    identity:AgentIdentity
    task_id:str
    action:str
    resource:str
    environment:str="development"
    context:dict[str,Any]=Field(default_factory=dict)
    estimated_cost:float=0.0
    risk_override:int|None=None
    requested_at:datetime=Field(default_factory=utcnow)

class AuthorizationDecision(BaseModel):
    model_config=ConfigDict(extra="forbid")
    request_id:str
    decision:Decision
    policy:str|None=None
    risk_score:int=0
    reasons:list[str]=Field(default_factory=list)
    required_approval:bool=False
    expires_at:datetime|None=None

class Policy(BaseModel):
    model_config=ConfigDict(extra="forbid")
    name:str
    when:dict[str,Any]=Field(default_factory=dict)
    allow:dict[str,Any]=Field(default_factory=dict)
    deny:dict[str,Any]=Field(default_factory=dict)
    require:dict[str,Any]=Field(default_factory=dict)
    priority:int=0

class ExecutionEvent(BaseModel):
    model_config=ConfigDict(extra="forbid")
    event_id:str
    event_type:str
    request_id:str
    task_id:str
    agent_id:str
    action:str
    resource:str
    authorization:str
    policy:str|None=None
    timestamp:datetime=Field(default_factory=utcnow)
    payload_hash:str=""
    previous_hash:str=""
    event_hash:str=""
    result:str|None=None
    metadata:dict[str,Any]=Field(default_factory=dict)

class VerificationResult(BaseModel):
    model_config=ConfigDict(extra="forbid")
    verified:bool
    verifier:str
    summary:str
    evidence:dict[str,Any]=Field(default_factory=dict)
    timestamp:datetime=Field(default_factory=utcnow)
