"""JSON-RPC stdio MCP proxy enforcing authority before tool execution."""
from __future__ import annotations
import json
import subprocess
from dataclasses import dataclass
from typing import Any
from .mcp import MCPGateway, ToolCall

@dataclass
class MCPStdioProxy:
    gateway:MCPGateway
    token_id:str
    identity:Any
    task_id:str

    def authorize_message(self,message:dict[str,Any]):
        params=message.get("params") or {}; tool=params.get("name") or params.get("tool")
        call=ToolCall(tool=str(tool),resource=str(params.get("resource",tool)),arguments=params.get("arguments") or {},environment=params.get("environment","development"),estimated_cost=float(params.get("estimated_cost",0)),context=params.get("context") or {})
        return self.gateway.authorize(self.token_id,str(message.get("id","unknown")),self.identity,self.task_id,call)

    def filter(self,message:dict[str,Any])->tuple[bool,dict[str,Any]]:
        if message.get("method") not in {"tools/call","tool/call"}: return True,message
        decision,_=self.authorize_message(message)
        if decision.decision.value!="ALLOW":
            return False,{"jsonrpc":"2.0","id":message.get("id"),"error":{"code":-32001,"message":"Agent Authority denied tool call","data":decision.model_dump(mode="json")}}
        return True,message

    def proxy_lines(self,lines:list[str])->list[str]:
        output=[]
        for line in lines:
            message=json.loads(line); _,response=self.filter(message); output.append(json.dumps(response,separators=(",",":")))
        return output

    def proxy_process(self,command:list[str])->int:
        """Forward JSON-RPC to a child MCP server, blocking unauthorized calls."""
        if not command or any("\x00" in x for x in command): raise ValueError("invalid child command")
        child=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
        assert child.stdin is not None and child.stdout is not None
        try:
            for line in child.stdout:
                try: message=json.loads(line)
                except json.JSONDecodeError: continue
                allowed,response=self.filter(message)
                if allowed:
                    child.stdin.write(json.dumps(response,separators=(",",":"))+"\n"); child.stdin.flush()
                else:
                    print(json.dumps(response,separators=(",",":")),flush=True)
        finally:
            child.stdin.close(); child.wait()
        return child.returncode or 0
