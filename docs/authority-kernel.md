# Agent Authority v0.1 — Authority Kernel

The kernel binds human owner → agent identity → session → task → capability → action/resource. Authority tokens are task-scoped, time-bounded, action-bounded, cost-bounded, and revocable.

Authorization evaluates identity binding, capability coverage, policy allow/deny, context-aware risk and approval requirements. Decisions are ALLOW, DENY, or APPROVAL_REQUIRED. Every permitted execution can be recorded as an event containing the request hash and chained audit hash.

Verification is independent from the agent claim: the verifier records whether the claimed outcome matches independently established evidence. The audit ledger can be checked for tampering by recomputing the chain.
