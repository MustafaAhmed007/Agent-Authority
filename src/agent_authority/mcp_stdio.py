"""JSON-RPC stdio MCP proxy enforcing authority before tool execution.

The proxy is transport-level: it reads one JSON-RPC object per line from stdin,
blocks unauthorized tools, and delegates authorized calls to a configured child
process. This keeps the policy decision outside the model/runtime.
"""
from __future__ import annotations
import json
import subprocess
from dataclasses import dataclass
from typing import Any
from .mcp import MCPGateway, ToolCall

@dataclass
class MCPStdioProxy:
    gateway: MCPGateway
    token_id: str
    identity: Any
    task_id: str

    def authorize_message(self, message: dict[str, Any]):
        params = message.get("params") or {}
        tool = params.get("name") or params.get("tool")
        arguments = params.get("arguments") or {}
        call = ToolCall(tool=str(tool), resource=str(params.get("resource", tool)), arguments=arguments)
        return self.gateway.authorize(self.token_id, str(message.get("id", "unknown")), self.identity, self.task_id, call)

    def filter(self, message: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        if message.get("method") not in {"tools/call", "tool/call"}:
            return True, message
        decision, _ = self.authorize_message(message)
        if decision.decision.value != "ALLOW":
            return False, {"jsonrpc":"2.0","id":message.get("id"),"error":{"code":-32001,"message":"Agent Authority denied tool call","data":decision.model_dump(mode="json")}}
        return True, message

    def proxy_lines(self, lines: list[str]) -> list[str]:
        output=[]
        for line in lines:
            message=json.loads(line)
            allowed,response=self.filter(message)
            output.append(json.dumps(response, separators=(",",":")))
            if not allowed:
                continue
        return output
