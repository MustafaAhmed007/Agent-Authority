# Agent Authority

**Let your agents act. Control what they can do. Prove what they did.**

Open-source, local-first runtime authority layer for AI agents. Agent Authority binds identity → task → capability → policy → risk → approval → execution → verification → evidence.

## Runtime surface

- Cryptographic Ed25519 signing primitives
- Task-scoped, expiring and revocable authority tokens
- Capability/resource matching and deterministic policy evaluation
- Risk scoring and human approval boundary
- Action/cost budgets
- Execution gate and transport-neutral MCP gateway
- Tamper-evident audit chain and replay
- Independent verification contract
- Delegation, trust registry, anomaly signals and advisory learning feedback
- Sandbox and framework-adapter boundaries

## Quick start

```bash
pip install -e ".[dev]"
authority init
authority doctor
pytest
```

## Architecture

```text
Human / Owner
      ↓
Agent Identity + Session
      ↓
Task-scoped Authority Token
      ↓
Capability + Policy + Trust + Risk
      ↓
ALLOW / DENY / APPROVAL_REQUIRED
      ↓
Execution Gate / MCP Gateway
      ↓
Sandbox / Tool / API
      ↓
Independent Verification
      ↓
Proof + Audit Ledger
      ↓
Replay + Anomaly + Learning Feedback
```

## Security boundary

Learning is advisory and cannot grant privileges. Sandbox.py is an explicit adapter boundary and is **not** a security sandbox by itself; production deployments must connect a real OS/container isolation implementation before executing untrusted workloads. CI is configured in `.github/workflows/ci.yml`; GitHub status must be green before a release is considered verified.

## Production roadmap

The repository now contains the authority runtime foundations. Production deployment work consists of replacing adapter boundaries with concrete hardened integrations: MCP transport interception, OS/container sandboxing, durable shared audit storage, signed wire-level authority tokens, framework-specific adapters, and an enterprise control plane.

## Design principles

Least privilege, task-bounded delegation, explainability, local-first operation, no silent privilege escalation, evidence over agent claims, protocol compatibility, deterministic security decisions, fail-closed execution, advisory-only learning.

## License

Apache-2.0.
