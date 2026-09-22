"""Queryable authority graph for agents, tasks, tokens, tools and events."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AuthorityGraph:
    nodes: dict[str, dict[str, Any]] = field(default_factory=dict)
    edges: list[tuple[str, str, str]] = field(default_factory=list)

    def node(self, node_id: str, kind: str, **attrs: Any) -> None:
        self.nodes[node_id] = {"kind": kind, **attrs}

    def edge(self, source: str, relation: str, target: str) -> None:
        self.edges.append((source, relation, target))

    def neighbors(self, node_id: str, relation: str | None = None) -> list[str]:
        return [t for s, r, t in self.edges if s == node_id and (relation is None or r == relation)]

    def explain(self, node_id: str) -> dict[str, Any]:
        return {"node": self.nodes.get(node_id), "outgoing": [{"relation":r,"target":t} for s,r,t in self.edges if s==node_id]}
