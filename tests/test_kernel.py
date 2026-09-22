from agent_authority import Authority, Capability, AuthorizationRequest, Policy, Decision

def setup():
    policies = [
        Policy(name="coder-write", when={"agent.role":"coder"}, allow={"operations":["read","write","commit","github.pr.create"]}, priority=10),
        Policy(name="no-production", when={"environment":"production"}, deny={"operations":["deploy","production.deploy"]}, priority=100),
    ]
    a = Authority(policies)
    ident = a.issue_identity("user-1","test-model","test-runtime","1","coder")
    token = a.issue_token(ident,"task-1",[Capability(name="coding", operations=["read","write","commit","github.pr.create"], resources=["repo/*"])])
    return a, ident, token

def test_allow():
    a,i,t = setup()
    req = AuthorizationRequest(request_id="r1", identity=i, task_id="task-1", action="write", resource="repo/x")
    d = a.authorize(t.token_id, req)
    assert d.decision == Decision.ALLOW

def test_deny_capability():
    a,i,t = setup()
    req = AuthorizationRequest(request_id="r2", identity=i, task_id="task-1", action="delete", resource="repo/x")
    d = a.authorize(t.token_id, req)
    assert d.decision == Decision.DENY

def test_production_requires_control():
    a,i,t = setup()
    t.capabilities[0].operations.append("deploy")
    req = AuthorizationRequest(request_id="r3", identity=i, task_id="task-1", action="deploy", resource="repo/x", environment="production")
    d = a.authorize(t.token_id, req)
    assert d.decision in {Decision.DENY, Decision.APPROVAL_REQUIRED}

def test_ledger():
    a,i,t = setup()
    req = AuthorizationRequest(request_id="r4", identity=i, task_id="task-1", action="write", resource="repo/x")
    d = a.authorize(t.token_id, req)
    a.record_execution(t.token_id, req, d, "success")
    ok,_ = a.ledger.verify()
    assert ok
