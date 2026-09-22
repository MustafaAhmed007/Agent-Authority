from agent_authority import Authority, Capability, AuthorizationRequest, MCPGateway, ToolCall, ToolTrust, ToolTrustRegistry, LearningEngine, Feedback, AnomalyDetector

def test_mcp_gateway_executes_only_allowed_tool():
    authority=Authority()
    identity=authority.issue_identity("owner","model","runtime","1")
    token=authority.issue_token(identity,"task",[Capability(name="read",operations=["read"],resources=["repo/*"])])
    gateway=MCPGateway(authority)
    decision,request=gateway.authorize(token.token_id,"req",identity,"task",ToolCall("read","repo/x"))
    assert decision.decision.value=="ALLOW"
    assert gateway.execute(token.token_id,request,lambda:{"ok":True})=={"ok":True}

def test_trust_registry_requires_verified_tool():
    registry=ToolTrustRegistry()
    registry.register(ToolTrust(tool="search",publisher="example",verified=True,allowed_environments={"production"}))
    assert registry.is_allowed("search","production")
    assert not registry.is_allowed("search","development")

def test_learning_never_changes_privilege():
    engine=LearningEngine(); engine.observe(Feedback("deploy","failure",9,False))
    assert engine.suggestions(); assert engine.summary()["samples"]==1

def test_anomaly_detector_flags_integrity_violation():
    authority=Authority(); identity=authority.issue_identity("o","m","r","1"); token=authority.issue_token(identity,"t",[Capability(name="x",operations=["x"],resources=["r"])])
    request=AuthorizationRequest(request_id="q",identity=identity,task_id="t",action="x",resource="r")
    decision=authority.authorize(token.token_id,request)
    event=authority.record_execution(token.token_id,request,decision,"success")
    event.authorization="DENY"
    assert AnomalyDetector().inspect([event])
