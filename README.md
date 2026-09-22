# Agent Authority

**Let your agents act. Control what they can do. Prove what they did.**

Open-source, local-first runtime authority layer for AI agents. The kernel combines cryptographic identity, task-scoped capabilities, deterministic policy decisions, context-aware risk, human approval gates, execution evidence, independent verification, and a tamper-evident audit ledger.

## Quick start

```bash
pip install -e ".[dev]"
authority init
authority doctor
pytest
```

## Architecture

```
Human
  ↓
Agent identity + task-scoped authority
  ↓
Policy + capability + risk
  ↓
ALLOW / DENY / APPROVAL_REQUIRED
  ↓
Execution gate
  ↓
Tool / API / MCP
  ↓
Verification
  ↓
Proof + tamper-evident audit
```

## Roadmap

Phase 1: authority kernel. Phase 2: MCP gateway, approval, budget and sandbox. Phase 3: verification/replay/authority graph. Phase 4: ecosystem adapters and SDKs. Phase 5: tool trust, learning and anomaly detection. Phase 6: hosted control plane.

## Design principles

Least privilege, task-bounded delegation, explainability, local-first operation, no silent privilege escalation, evidence over agent claims, protocol compatibility, deterministic security decisions.

## License

Apache-2.0.
