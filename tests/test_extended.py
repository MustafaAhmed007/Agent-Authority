from agent_authority import *
def test_explicit_approval_callback():
    a=Authority(approval_callback=lambda req,pending: True)
    i=a.issue_identity("u","m","r","1","ops")
    t=a.issue_token(i,"t",[Capability(name="deploy",operations=["deploy"],resources=["app/*"])])
    req=AuthorizationRequest(request_id="r",identity=i,task_id="t",action="deploy",resource="app/x")
    assert a.authorize(t.token_id,req).decision is Decision.ALLOW
def test_revoke():
    a=Authority(); i=a.issue_identity("u","m","r","1"); t=a.issue_token(i,"t",[Capability(name="r",operations=["read"],resources=["x"])])
    assert a.revoke(t.token_id) is True
    d=a.authorize(t.token_id,AuthorizationRequest(request_id="r",identity=i,task_id="t",action="read",resource="x"))
    assert d.decision is Decision.DENY
def test_data_levels():
    assert permits(DataClass.RESTRICTED,DataClass.CONFIDENTIAL)
    assert not permits(DataClass.INTERNAL,DataClass.SENSITIVE)
def test_replay():
    a=Authority(); i=a.issue_identity("u","m","r","1"); t=a.issue_token(i,"t",[Capability(name="r",operations=["read"],resources=["x"])])
    req=AuthorizationRequest(request_id="r",identity=i,task_id="t",action="read",resource="x"); d=a.authorize(t.token_id,req); a.record_execution(t.token_id,req,d,"success")
    assert len(ReplayEngine(a.ledger).run("t"))==1
