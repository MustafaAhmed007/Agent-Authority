import tempfile
from pathlib import Path
from agent_authority import *

def test_sqlite_restart_and_revoke():
    with tempfile.TemporaryDirectory() as d:
        store=SQLiteStore(Path(d)/"authority.db")
        a=Authority(store=store); identity=a.issue_identity("owner","model","runtime","1")
        token=a.issue_token(identity,"task",[Capability(name="read",operations=["read"],resources=["repo/*"])])
        assert Authority(store=store).authorize(token.token_id,AuthorizationRequest(request_id="1",identity=identity,task_id="task",action="read",resource="repo/x")).decision==Decision.ALLOW
        assert a.revoke(token.token_id)
        assert Authority(store=store).authorize(token.token_id,AuthorizationRequest(request_id="2",identity=identity,task_id="task",action="read",resource="repo/x")).decision==Decision.DENY
        store.close()

def test_signed_decision_and_graph():
    a=Authority(); i=a.issue_identity("o","m","r","1"); t=a.issue_token(i,"t",[Capability(name="r",operations=["read"],resources=["x"])])
    d=a.authorize(t.token_id,AuthorizationRequest(request_id="r",identity=i,task_id="t",action="read",resource="x"))
    signed=SignedDecision(a.signer); envelope=signed.issue(d); assert signed.verify(envelope)
    envelope["payload"]["request_id"]="tampered"; assert not signed.verify(envelope)
    graph=AuthorityGraph(); graph.node(i.agent_id,"agent"); graph.node(t.token_id,"token"); graph.edge(i.agent_id,"holds",t.token_id); assert graph.neighbors(i.agent_id)==[t.token_id]

def test_mcp_proxy_denies_unknown_tool():
    a=Authority(); i=a.issue_identity("o","m","r","1"); t=a.issue_token(i,"t",[Capability(name="read",operations=["read"],resources=["repo/*"])])
    proxy=MCPStdioProxy(MCPGateway(a),t.token_id,i,"t")
    ok,response=proxy.filter({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"delete","resource":"repo/x"}})
    assert not ok and response["error"]["code"]==-32001

def test_docker_command_isolated_shape():
    cfg=DockerSandboxConfig(network="none",read_only=True)
    assert cfg.network=="none" and cfg.read_only
