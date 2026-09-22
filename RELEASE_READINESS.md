# Agent Authority — Release Readiness

## Release

**v0.3.1 — COMPLETE RUNTIME BUILD**

## Implemented

- Cryptographic Ed25519 identity/signing primitives
- Persistent signing key store
- Task-scoped, expiring, revocable authority tokens
- Capability-based operation/resource matching
- Deterministic policy-as-code evaluation
- ALLOW / DENY / APPROVAL_REQUIRED decisions
- Context-aware risk engine
- Human approval callback boundary
- Action and cost budgets
- Controlled execution gate
- MCP JSON-RPC stdio interception and child-process forwarding
- Durable SQLite token/event persistence
- Tamper-evident hash-chained audit ledger
- Independent verification contract
- Replay/time-travel inspection
- Agent-to-agent task-scoped delegation
- Tool trust registry
- Data classification
- Anomaly detection signals
- Advisory learning feedback loop that cannot self-grant privileges
- Authority graph
- Docker isolation adapter with constrained defaults
- Runtime adapters for LangGraph, CrewAI, OpenHands, Claude Code, Codex and OpenCode
- Authenticated local control plane
- CLI operational controls
- Dockerfile and persistent Docker Compose deployment
- Security, contribution and architecture documentation
- Regression/integration test suite
- GitHub Actions CI

## Verification

The latest GitHub Actions run for `main` completed successfully with both:

- `ruff check .` — PASS
- `pytest -q` — PASS

The production-runtime test suite covers durable SQLite restart/revocation, signed decision integrity, authority graph behavior, MCP denial enforcement, sandbox configuration and persistent signing keys.

## Completion definition

The repository is considered complete for the planned open-source runtime scope when the authority kernel, real tool interception boundary, concrete local sandbox adapter, durable state, signing, verification, graph, trust/anomaly/learning feedback, framework adapter boundary, operational control plane, deployment artifacts and CI verification are all present and green.

External infrastructure remains deployment-specific: production TLS termination, container runtime hardening, secret management, and organization-specific framework credentials must be configured by the operator rather than embedded in the repository.
