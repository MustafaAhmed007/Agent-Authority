from agent_authority import *
def _auth():
    a=Authority([Policy(name="allow-write",when={"agent.role":"coder"},allow={"operations":["read","write"]},priority=10)])
    i=a.issue_identity("u","m","r","1","coder")
    t=a.issue_token(i,"task",[Capability(name="coding",operations=["read","write"],resources=["repo/*"])],max_actions=1,max_cost=1.0)
    return a,i,t

def test_explicit_approval_callback():
    a=Authority(approval_callback=lambda req,pending: True)
    i=a.issue_identity("u","m","r","1","ops")
    t=a.issue_token(i,"t",[Capability(name="deploy",operations=["deploy"],resources=["app/*"])])
    req=AuthorizationRequest(request_id="r",identity=i,task_id="t",action="deploy",resource="app/x")
    assert a.authorize(t.token_id,req).decision is Decision.ALLOW

def test_revoke():
    a,i,t=_auth(); assert a.revoke(t.token_id)
    d=a.authorize(t.token_id,AuthorizationRequest(request_id="r",identity=i,task_id="task",action="read",resource="repo/x"))
    assert d.decision is Decision.DENY

def test_budget():
    a,i,t=_auth()
    req=AuthorizationRequest(request_id="r",identity=i,task_id="task",action="write",resource="repo/x",estimated_cost=.6)
    d=a.authorize(t.token_id,req); assert d.decision is Decision.ALLOW
    a.record_execution(t.token_id,req,d,"success")
    req2=req.model_copy(update={"request_id":"r2","estimated_cost":.5})
    assert a.authorize(t.token_id,req2).decision is Decision.DENY

def test_gate_blocks():
    a,i,t=_auth()
    req=AuthorizationRequest(request_id="r",identity=i,task_id="task",action="delete",resource="repo/x")
    try: ExecutionGate(a).run(t.token_id,req,lambda:"bad")
    except PermissionError: pass
    else: raise AssertionError("gate must block")

def test_replay_and_verify():
    a,i,t=_auth(); req=AuthorizationRequest(request_id="r",identity=i,task_id="task",action="read",resource="repo/x"); d=a.authorize(t.token_id,req); a.record_execution(t.token_id,req,d,"success")
    assert len(ReplayEngine(a.ledger).run("task"))==1
    assert Verifier().verify(True,True,lambda x,y:x==y).verified

def test_data_levels():
    from agent_authority.data import DataClass, permits
    assert permits(DataClass.RESTRICTED,DataClass.CONFIDENTIAL)
    assert not permits(DataClass.INTERNAL,DataClass.SENSITIVE)
