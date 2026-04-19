# OrHaShield OPA Policy Bundle

This directory contains the authoritative Rego policies for the Safety Gate.

## Files

- `orhashield.rego` — Main authz policy (`package orhashield.authz`)

## Policy version

Current: **0.1.0**

## Usage

The Rust safety gate loads this policy via `regorus` (embedded OPA engine — no OPA binary needed, air-gap compatible).

The `services/safety-gate/policy/orhashield.rego` file is kept in sync with this copy. Any change to either must be reflected in both and accompanied by:

1. `cargo test` in `services/safety-gate/` to verify property test invariants pass
2. An ADR update if the change alters a fundamental safety invariant
3. PR review with OT engineer sign-off

## Invariants enforced by property tests (`tests/property_tests.rs`)

1. `OBSERVE` always → `allow` (any input)
2. `MODIFY_SETPOINT` always → `deny` (any input)
3. `FIRMWARE_UPDATE` always → `deny` (any input)
4. `ISOLATE_NETWORK` on Purdue Level 0–1 always → `escalate`
5. Kill switch (`autonomous_mode=disabled`) → `deny` for non-OBSERVE/ALERT
