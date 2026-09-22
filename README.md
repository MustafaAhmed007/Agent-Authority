# Agent Authority

**Let your agents act. Control what they can do. Prove what they did.**

Agent Authority is a vendor-neutral runtime authority layer for AI agents. It sits between an agent and the capabilities that agent is allowed to exercise, binding:

**identity → task → capability → policy → trust → risk → approval → execution → verification → evidence → learning**

The system is designed around **least privilege, fail-closed execution, task-bounded delegation, independent verification, tamper-evident evidence, and advisory-only learning**.

---

## Why Agent Authority exists

Modern AI agents can reason, call tools, modify files, access APIs, execute code, delegate work, and operate for long periods. The difficult problem is no longer only *what the model can generate*; it is **what the agent is actually authorized to do**.

Agent Authority turns that problem into an explicit runtime control plane:

- **Who** is acting?
- **On whose behalf?**
- **For which task?**
- **Which capability was delegated?**
- **Which resource is being accessed?**
- **What policy applies?**
- **How risky is the requested action?**
- **Does a human need to approve it?**
- **Was the action actually executed?**
- **Did the claimed result match independent evidence?**
- **Can the complete decision and execution history be replayed and audited?**

The answer to every question is represented as structured runtime state rather than being left to the agent's own judgment.

---

## Core promise

```text
Agents can act.

But authority is explicit.
Execution is gated.
High-risk actions can require humans.
Evidence is independently verifiable.
Audit history is tamper-evident.
Learning cannot silently increase privileges.
```

---

# Complete end-to-end system workflow

```text
┌─────────────────────────────────────────────────────────────┐
│                         HUMAN / OWNER                       │
│  Defines task, trust boundary, policy and delegation scope │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENT IDENTITY LAYER                     │
│ owner • agent • runtime • model • version • session        │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  TASK-SCOPED AUTHORITY                      │
│ expiry • revocation • action budget • cost budget           │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              CAPABILITY + RESOURCE MATCHING                 │
│ operation patterns • resource patterns • constraints        │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  POLICY + TRUST EVALUATION                   │
│ allow • deny • required conditions • tool trust             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       RISK ENGINE                            │
│ action • environment • context • resource sensitivity       │
└─────────────────────────────┬───────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                 DENY            APPROVAL_REQUIRED
                    │                   │
                    │             ┌─────▼─────┐
                    │             │ HUMAN GATE│
                    │             └─────┬─────┘
                    │                   │
                    └──────────┬────────┘
                               ▼
                    ┌──────────────────────┐
                    │    EXECUTION GATE    │
                    │ fail-closed boundary │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
              MCP            TOOL           SANDBOX
                │              │              │
                └──────────────┼──────────────┘
                               ▼
                         ACTUAL EXECUTION
                               │
                               ▼
                    ┌──────────────────────┐
                    │ INDEPENDENT VERIFY   │
                    │ claim vs observation │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ SIGNED / HASHED      │
                    │ PROOF + AUDIT EVENT  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ DURABLE STORAGE      │
                    │ SQLite / repository  │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┼──────────────┐
                 ▼             ▼              ▼
              REPLAY      AUTHORITY GRAPH   ANOMALY
                                                │
                                                ▼
                                      ADVISORY LEARNING
                                                │
                                                ▼
                                      HUMAN / POLICY REVIEW
```

### Step-by-step execution

1. **Identity** — the runtime identifies the agent, owner, model/runtime and session.
2. **Task binding** — authority is issued for a specific task rather than as an unrestricted global permission.
3. **Capability matching** — the requested operation and resource are compared with the delegated capability.
4. **Policy evaluation** — deterministic policy rules can allow, deny, or introduce additional requirements.
5. **Trust evaluation** — the requested tool/capability can be evaluated against the Tool Trust Registry.
6. **Risk scoring** — context and action characteristics produce a risk signal.
7. **Approval** — high-risk or explicitly sensitive operations can pause for human authorization.
8. **Execution gate** — only an `ALLOW` decision reaches the actual executor.
9. **MCP interception** — MCP JSON-RPC calls can be inspected and gated before reaching downstream tools.
10. **Sandboxing** — Docker isolation can provide a concrete restricted execution boundary.
11. **Evidence capture** — the request, decision, execution result and metadata become auditable evidence.
12. **Independent verification** — the claimed outcome can be compared against independently observed evidence.
13. **Audit** — events are linked into a tamper-evident hash chain and persisted.
14. **Replay** — previous decisions/executions can be inspected after the fact.
15. **Graph analysis** — authority relationships can be reconstructed across agents, tasks and delegations.
16. **Anomaly detection** — suspicious behavioral patterns produce signals.
17. **Learning feedback** — observed outcomes can generate recommendations, but the learning layer cannot silently grant authority.

---

# Repository structure

```text
Agent-Authority/
│
├── .github/
│   └── workflows/
│       └── ci.yml                  # automated lint + test gate
│
├── docs/
│   ├── architecture.md             # system architecture
│   └── authority-kernel.md         # kernel design/specification
│
├── examples/
│   └── policy.yaml                 # example policy-as-code
│
├── src/agent_authority/
│   ├── __init__.py                 # public package API
│   ├── models.py                   # authority domain models
│   ├── authority.py                # central authorization kernel
│   ├── policy.py                   # deterministic policy engine
│   ├── risk.py                     # contextual risk scoring
│   ├── crypto.py                   # hashing/signing primitives
│   ├── key_store.py                # persistent signing-key storage
│   ├── ledger.py                   # tamper-evident audit ledger
│   ├── storage.py                  # durable persistence layer
│   ├── gateway.py                   # execution enforcement boundary
│   ├── mcp.py                      # MCP authorization layer
│   ├── mcp_stdio.py                # MCP stdio interception/forwarding
│   ├── docker_sandbox.py            # Docker isolation adapter
│   ├── delegation.py               # agent-to-agent delegation
│   ├── verification.py              # independent verification
│   ├── replay.py                    # event replay/inspection
│   ├── authority_graph.py           # authority relationship graph
│   ├── trust.py                     # Tool Trust Registry
│   ├── anomaly.py                   # anomaly signals
│   ├── learning.py                  # advisory learning feedback
│   ├── adapters.py                  # framework adapter boundary
│   ├── frameworks.py                # framework integrations
│   ├── control_plane.py             # authenticated operational API
│   ├── authority_server.py          # embeddable service boundary
│   ├── data.py                      # data classification
│   └── cli.py                       # command-line interface
│
├── tests/                           # regression/integration tests
├── Dockerfile                       # production container
├── docker-compose.yml               # persistent deployment
├── pyproject.toml                   # package/build/dependency config
├── SECURITY.md                      # security reporting guidance
├── CONTRIBUTING.md                  # contribution rules
├── RELEASE_READINESS.md             # release verification boundary
├── LICENSE
└── README.md
```

> The exact implementation tree may grow as adapters and deployment integrations are added. The README intentionally maps each major architectural responsibility to a recognizable module so the repository remains navigable.

---

# Runtime layers

| Layer | Responsibility |
|---|---|
| Identity | Establishes the acting agent and owner relationship |
| Authority | Issues and validates bounded authority |
| Capability | Defines permitted operations/resources |
| Policy | Applies deterministic organizational rules |
| Trust | Tracks trust posture for tools/capabilities |
| Risk | Calculates contextual risk signals |
| Approval | Introduces a human gate when required |
| Execution | Enforces the final allow/deny boundary |
| MCP | Intercepts tool protocol traffic |
| Sandbox | Restricts execution environment |
| Verification | Tests claims against independent observations |
| Evidence | Produces signed/hash-linked proof |
| Storage | Persists authority and execution state |
| Replay | Reconstructs historical activity |
| Graph | Models delegation/authority relationships |
| Anomaly | Detects suspicious behavior patterns |
| Learning | Generates advisory improvement signals |
| Control Plane | Provides authenticated operational management |
| Adapters | Connects external agent frameworks |

---

# Authority decision lifecycle

Every controlled action follows the same conceptual lifecycle:

```text
REQUEST
  ↓
IDENTIFY
  ↓
BIND TO TASK
  ↓
MATCH CAPABILITY
  ↓
EVALUATE POLICY
  ↓
CHECK TRUST
  ↓
ASSESS RISK
  ↓
┌───────────────────────────────┐
│ DENY                          │ → stop + audit
│ APPROVAL_REQUIRED             │ → human decision
│ ALLOW                         │ → execution gate
└───────────────────────────────┘
  ↓
EXECUTE
  ↓
VERIFY
  ↓
RECORD EVIDENCE
  ↓
PERSIST
  ↓
REPLAY / GRAPH / ANOMALY
  ↓
LEARNING FEEDBACK
```

The critical invariant is:

> **The agent never gets to decide its own authority.**

The agent requests an action; the authority system decides whether that action is permitted.

---

# Security model

Agent Authority uses defense-in-depth rather than relying on a single permission check.

### 1. Least privilege

Tokens contain explicit task, capability, expiry, action-budget and cost-budget boundaries.

### 2. Fail closed

Missing, expired, revoked or insufficient authority produces a denial instead of falling through to execution.

### 3. No silent escalation

Delegation is task-scoped and bounded. The learning layer is advisory and cannot mutate authority by itself.

### 4. Human control

Sensitive/high-risk actions can require explicit human approval.

### 5. Independent verification

An agent's claim is not automatically treated as evidence. Verification can compare the claim with independently observed state.

### 6. Tamper evidence

Execution events are hash-linked so historical mutation becomes detectable.

### 7. Isolation

The Docker sandbox adapter provides a concrete execution boundary with restrictive defaults. Other sandbox technologies can implement the same abstraction.

### 8. Control-plane authentication

The operational control plane supports bearer-secret authentication and should be deployed behind TLS/reverse-proxy controls when exposed beyond localhost.

---

# MCP execution model

Agent Authority is designed to sit between an agent runtime and MCP-enabled tools:

```text
Agent Runtime
     │
     │ JSON-RPC / MCP
     ▼
┌─────────────────────┐
│ Agent Authority MCP │
│      Interceptor    │
└─────────┬───────────┘
          │
          ├── identity
          ├── task
          ├── capability
          ├── policy
          ├── trust
          ├── risk
          ├── approval
          └── budget
          │
          ▼
   ALLOW / DENY
          │
          ▼
Downstream MCP Server
          │
          ▼
        Tool
```

This makes authority enforcement a **runtime boundary**, rather than a prompt instruction that an agent may accidentally or deliberately ignore.

---

# Quick start

```bash
pip install -e ".[dev]"

# Initialize local authority state
authority init

# Run the complete test suite
pytest -q

# Inspect local installation/configuration
authority doctor
```

---

# Control plane

```bash
export AUTHORITY_ADMIN_SECRET="replace-with-a-long-random-secret"
authority control --host 127.0.0.1 --port 8765
```

Health is available at `/health`.
Operational endpoints require:

```text
Authorization: Bearer <secret>
```

For production exposure, place the service behind TLS, restrict network access, rotate secrets, and use an external secret manager where appropriate.

---

# Docker deployment

```bash
export AUTHORITY_ADMIN_SECRET="replace-with-a-long-random-secret"
docker compose up --build -d
```

The Compose deployment persists SQLite state through the `authority-data` volume. The container is configured with restrictive runtime defaults including a non-root process, read-only root filesystem and constrained temporary storage.

---

# Verification and quality gates

The CI pipeline is intentionally simple and strict:

```text
checkout
  ↓
Python setup
  ↓
pip install -e ".[dev]"
  ↓
ruff check .
  ↓
pytest -q
  ↓
GREEN / BLOCK RELEASE
```

A repository change is not considered verified merely because the code was written. It must survive the automated quality gate.

---

# Suggested production additions

The current system is intentionally structured so the following can be added without redesigning the authority kernel.

## A. External secret management

Move signing keys and control-plane secrets into Vault, cloud KMS/HSM, or an equivalent managed secret system.

## B. PostgreSQL audit backend

SQLite is useful for local/single-node operation. A PostgreSQL backend should be used when multiple authority instances need shared durable state.

## C. Redis rate limiting

Add distributed request/risk throttling for large agent fleets.

## D. OpenTelemetry observability

Emit traces and metrics for authorization latency, denials, approvals, tool calls, verification failures and anomaly signals.

## E. Policy simulation mode

Allow security teams to run proposed policies against historical events before enforcing them.

## F. Policy versioning

Every authorization decision should be associated with an immutable policy version so an old decision can be reconstructed exactly.

## G. Approval UX

Add a dedicated web/mobile approval surface showing:

- agent identity
- requested action
- target resource
- reason
- risk score
- policy matched
- tool trust status
- estimated cost
- expiration
- approve/deny controls

## H. Key rotation and revocation infrastructure

Add automated signing-key rotation, key IDs, revocation lists and emergency global kill-switch support.

## I. Enterprise SSO/RBAC

Connect the control plane to OIDC/SAML and map human roles to authority-management permissions.

## J. Security test suite

Expand into fuzzing, malicious MCP payload tests, policy-confusion tests, replay attacks, token substitution, privilege-escalation attempts and sandbox escape testing.

## K. Multi-node authority federation

Support multiple Authority instances with signed cross-node authority records while preserving local fail-closed behavior.

## L. Agent behavior baselines

Build historical per-agent baselines for tool frequency, resource access, cost, latency and failure patterns to strengthen anomaly detection.

These are **production-hardening and scale additions**, not prerequisites for understanding or operating the core authority model.

---

# Example business use cases

### Coding agents

Restrict an autonomous coding agent to a repository, allow read/write operations, block production deployment, and require human approval for release actions.

### DevOps agents

Allow diagnostics and staging changes while requiring explicit approval for production mutations.

### Research agents

Allow web/API access under budget limits while restricting secrets, destructive tools and sensitive datasets.

### Enterprise workflow agents

Delegate bounded tasks between agents while preserving owner/task lineage and a complete audit trail.

### Customer-support agents

Permit ticket reads and draft responses while requiring approval for refunds, account changes or other high-impact actions.

---

# Design principles

1. **Authority is explicit.**
2. **Permissions are bounded by task.**
3. **Execution is always gated.**
4. **High-impact actions can require humans.**
5. **Evidence is stronger than agent claims.**
6. **Security decisions should be explainable.**
7. **Learning must not become privilege escalation.**
8. **The kernel remains vendor-neutral.**
9. **Adapters belong at the boundary, not inside the security core.**
10. **Every important action should be reconstructable after the fact.**

---

# Project status

```text
Authority Kernel              ████████████████████  Complete
Execution Enforcement        ████████████████████  Complete
MCP Integration              ████████████████████  Complete
Persistence                  ████████████████████  Complete
Verification + Evidence      ████████████████████  Complete
Delegation + Authority Graph ████████████████████  Complete
Trust + Anomaly + Learning   ████████████████████  Complete
Sandbox Boundary             ████████████████████  Complete
Framework Adapters           ████████████████████  Complete
Control Plane                ████████████████████  Complete
Deployment                   ████████████████████  Complete
CI / Regression Suite        ████████████████████  Verified
```

**Current version:** `0.3.1`

---

# License

Apache-2.0.
