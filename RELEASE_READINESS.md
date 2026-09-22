# Agent Authority — Release Readiness

## Implemented

- Cryptographic agent identity model
- Task-scoped, expiring, revocable authority tokens
- Capability-based operation/resource matching
- Deterministic policy-as-code evaluation
- ALLOW / DENY / APPROVAL_REQUIRED decisions
- Context-aware risk engine
- Human approval callback gateway
- Action and cost budgets
- Controlled execution gate
- Tamper-evident hash-chained audit ledger
- Independent verification contract
- Replay/time-travel event inspection
- Agent-to-agent task-scoped delegation
- Data classification helpers
- Developer CLI
- Example policy
- Python package metadata and CI workflow
- Security and contribution guidance

## Verification boundary

GitHub Actions is configured to run `ruff check .` and `pytest -q`. The current GitHub connector exposes no workflow result/status for the latest commit, so CI execution is pending external GitHub Actions execution rather than being represented here as passed.

The implementation has been source-audited for import relationships and the core contracts covered by repository tests. A claim of CI clean should only be made after GitHub Actions reports a successful run.

## Next planned layers

MCP proxy/interception, production sandbox drivers, persistent/shared audit storage, signed wire-level authority tokens, framework adapters, tool trust registry, adaptive risk learning, anomaly detection, managed cloud control plane, and enterprise governance.

These layers remain separate from the v0.1 authority kernel so the security core stays deterministic and testable.
