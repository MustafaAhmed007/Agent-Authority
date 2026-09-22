# Agent Authority

**Let your agents act. Control what they can do. Prove what they did.**

Agent Authority is a vendor-neutral runtime authority layer for AI agents. It binds **identity → task → capability → policy → trust → risk → approval → execution → verification → evidence** and fails closed when authority is missing.

## What is implemented

- Ed25519 identity/signing primitives plus persistent key storage
- Task-scoped, expiring, revocable authority tokens
- Capability/resource matching and deterministic policy-as-code
- Context-aware risk scoring and human approval gates
- Action and cost budgets
- Execution gate and MCP JSON-RPC stdio interception
- Durable SQLite token/event persistence
- Tamper-evident hash-chained audit ledger and replay
- Independent verification contract
- Agent-to-agent delegation
- Tool trust registry, anomaly signals and advisory learning feedback
- Authority graph
- Docker isolation adapter with network-off, read-only, dropped-capability defaults
- Framework adapters for LangGraph, CrewAI, OpenHands, Claude Code, Codex and OpenCode
- Local authenticated operational control plane
- Production Docker/Compose deployment
- CLI, regression suite and GitHub Actions CI

## Quick start

```bash
pip install -e ".[dev]"
authority init
pytest -q
authority doctor
```

## Run the control plane

```bash
export AUTHORITY_ADMIN_SECRET="replace-with-a-long-random-secret"
authority control --host 127.0.0.1 --port 8765
```

Health is available at `/health`. Operational endpoints require `Authorization: Bearer <secret>`.

## Docker deployment

```bash
export AUTHORITY_ADMIN_SECRET="replace-with-a-long-random-secret"
docker compose up --build -d
```

SQLite state is stored in the persistent `authority-data` volume. The container runs as a non-root user with a read-only root filesystem and a constrained `/tmp` filesystem.

## Runtime architecture

```text
Owner / Human
      ↓
Agent Identity + Session
      ↓
Task-scoped Authority Token
      ↓
Capability + Policy + Trust + Risk
      ↓
ALLOW / DENY / APPROVAL_REQUIRED
      ↓
Execution Gate / MCP Interceptor
      ↓
Sandbox / Tool / API
      ↓
Independent Verification
      ↓
Signed Proof + Audit Ledger
      ↓
Durable Storage
      ↓
Replay + Authority Graph + Anomaly Signals
      ↓
Advisory Learning Feedback
```

## Security model

- Least privilege and task-bounded delegation.
- No silent privilege escalation.
- Unauthorized actions fail closed.
- High-risk actions can require explicit human approval.
- Learning is advisory only and cannot grant privileges.
- Authority decisions can be signed and verified independently.
- Audit events form a tamper-evident hash chain.
- Docker execution uses a concrete isolation adapter; `Sandbox` remains the framework boundary for other isolation technologies.
- The control plane is authenticated when `AUTHORITY_ADMIN_SECRET` is configured and should be placed behind TLS/reverse-proxy controls for network exposure.

## Verification

GitHub Actions runs dependency installation, Ruff correctness checks and the full pytest suite on every push to `main`. The current production-runtime build has a green CI run for the authority kernel, durable storage, signing, graph and MCP integration tests.

## Version

`0.3.1`

## License

Apache-2.0.
