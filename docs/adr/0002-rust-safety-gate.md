# ADR 0002 — Rust + regorus for Safety Gate

**Status:** Accepted  
**Date:** 2026-04-19  
**Author:** CyberSentinel Systems Engineering

## Context

Every action proposed by the AI agent orchestrator must pass through a deterministic policy evaluation engine before it can be executed or queued for human approval. Requirements:

- Memory safety: the safety gate processes untrusted data from the agent (LLM outputs); memory-unsafe code here is a security vulnerability
- Deterministic: given the same input and policy, always produce the same decision — no probabilistic behavior
- Embedded Rego: must run without an external OPA binary for air-gap deployments
- Formally verifiable: the core `evaluate_action` function should be provable correct for the safety invariants (setpoint always denied, observe always allowed, etc.)
- High throughput: must evaluate actions faster than they arrive (target <1ms per evaluation)
- Fail-closed: any internal error produces DENY, never ALLOW

## Decision

Use **Rust** (edition 2021) with:

- `tokio` for async NATS message consumption
- `regorus` crate for embedded Rego policy evaluation (pure Rust, no CGo binding, no external OPA binary)
- `proptest` for property-based testing of safety invariants
- **Kani** model checker for formal verification of `evaluate_action` (run in CI on a separate job)
- `tracing` + `tracing-subscriber` (JSON format) for structured logging

## Policy File

`policy/orhashield.rego` is the single source of truth for allow/deny/escalate decisions. It is:

- Version-controlled in this repository
- Loaded at safety-gate startup from an environment-variable-specified path
- Never hot-reloaded in production without a CI-validated deployment

## Alternatives Rejected

| Alternative | Rejection Reason |
|---|---|
| Python + OPA REST API | Python memory safety concerns; network latency to OPA sidecar |
| Go + OPA REST API | Memory safety weaker than Rust; formal verification tooling less mature |
| Go + rego library | CGo binding; harder formal verification |
| Python + manual rules | No formal verification; harder to audit; Python type safety weaker |

## Consequences

- `regorus` crate must be kept up to date; audit for Rego compatibility with any policy changes.
- Kani verification runs on every CI push; if Kani is not available in CI, skip gracefully but log a warning.
- Policy changes require: (1) update `orhashield.rego`, (2) run `cargo test` to verify property tests pass, (3) open PR with ADR annotation, (4) update `policy_version` string in Rego.
- Any expansion of ALLOW rules must be accompanied by a new proptest case proving the invariant.

## Key Safety Invariants (formally verified)

1. `action_class == MODIFY_SETPOINT` → decision is always DENY, regardless of any other field
2. `action_class == FIRMWARE_UPDATE` → decision is always DENY
3. `action_class == OBSERVE` → decision is always ALLOW
4. `purdue_level ∈ {0,1}` AND `action_class ∉ {OBSERVE, ALERT}` → decision is never ALLOW
