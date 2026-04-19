# OrHaShield — OT Safety Policy

This document defines the non-negotiable safety envelope for all autonomous AI actions. Every engineer, every AI session, and every CI pipeline check must conform to this document.

## 1. Action Classes

| Class | Description | Examples | Default Gate |
|---|---|---|---|
| `OBSERVE` | Read-only data collection | PCAP capture, asset polling, log read | Autonomous OK |
| `ALERT` | Generate a notification only | Send alert to SIEM, page on-call | Autonomous OK |
| `ISOLATE_NETWORK` | Block a device at switch/firewall level | Firewall rule, NAC quarantine | Human-gated (L3.5+) or Escalate (L0-2) |
| `MODIFY_SETPOINT` | Write to a PLC register or process variable | Change pump speed, valve position | **NEVER autonomous** |
| `FIRMWARE_UPDATE` | Push firmware to any field device | PLC firmware, RTU config | **NEVER autonomous** |

## 2. Purdue Model Action Matrix

| Purdue Level | Zone | OBSERVE | ALERT | ISOLATE_NETWORK | Any Write |
|---|---|---|---|---|---|
| 0 — Physical process | Sensors, actuators | ✅ | ✅ | ❌ Escalate | ❌ Never |
| 1 — Basic control | PLCs, RTUs, IEDs | ✅ | ✅ | ❌ Escalate | ❌ Never |
| 2 — Area supervisory | HMI, SCADA servers | ✅ | ✅ | ⚠️ Human-gated | ❌ Never |
| 3 — Site operations | Historians, app servers | ✅ | ✅ | ⚠️ Human-gated | ❌ Never |
| 3.5 — DMZ | Firewalls, data diodes | ✅ | ✅ | ✅ Policy-gated | ❌ Never |
| 4-5 — Enterprise/Cloud | IT systems | ✅ | ✅ | ✅ Policy-gated | Standard IT rules |

## 3. Human-in-the-Loop Policy

- **Default**: all actions of class `ISOLATE_NETWORK` or above require explicit human approval via the dashboard Approval Queue.
- **Approval timeout**: 5 minutes. On expiry, the action is automatically **denied** and logged. The system does NOT retry without a new human-initiated trigger.
- **Approval format**: approver ID + timestamp + mandatory notes field. All recorded in WORM `human_approvals` table.
- **Escalation**: actions on Level 0-2 assets require a second approval from a user with `ot_engineer` role, regardless of confidence.

## 4. Digital Twin Pre-flight

Any action of class `ISOLATE_NETWORK` or above **must** be simulated in the OrHaShield digital twin sandbox before being queued for human approval. The `TwinVerifier` LangGraph node handles this. If twin simulation is unavailable, the action is automatically escalated (not denied) so a human can make an informed decision.

## 5. Two-Model Verification

For alerts with `severity=HIGH` or `severity=CRITICAL`:
1. **Proposing model** (`claude-sonnet-4-6`): generates hypothesis and action proposal.
2. **Verifying model** (`claude-haiku-4-5-20251001`): independently reviews the proposal without seeing the proposing model's reasoning.
3. If the verifying model disagrees: confidence is halved and the discrepancy is flagged in the hypothesis description. The action still goes to human gate but with a visible warning.

## 6. Global Kill Switch

Setting the environment variable `ORHASHIELD_AUTONOMOUS_MODE=disabled` on the `safety-gate` container immediately returns `DENY` for all actions except `OBSERVE` and `ALERT`, regardless of policy evaluation. This is the emergency stop for the entire autonomous response system.

## 7. WORM Audit Log

- Tables `agent_decisions`, `human_approvals`, and `audit_log` are **write-once, never-delete**.
- Postgres row-level security prevents DELETE and UPDATE from the application role.
- Minimum retention: 2 years for `agent_decisions`, 5 years for `audit_log`.
- Every agent decision record includes: `session_id`, `action_id`, `action_class`, `asset_id`, `decision`, `reason`, `confidence`, `model_used`, `policy_version`, `twin_verified`, `decided_at`.

## 8. Circuit Breaker (Ring Isolation)

The agent orchestrator tracks its decision rate. If more than **50 action proposals per minute** are generated for a single site, an automatic circuit breaker fires:
- All further proposals for that site are suppressed for 10 minutes.
- An `ANOMALY — AGENT_LOOP` alert is raised at `CRITICAL` severity.
- The event is logged to the audit stream.

This prevents runaway agent loops from flooding the approval queue or the OT network.

## 9. Safety Gate Fail-Closed

If the Rust safety gate encounters any internal error during policy evaluation (missing policy file, Rego parse error, NATS connectivity loss), it defaults to **DENY** on the affected action and emits an internal error alert. The gate never defaults to ALLOW on error.

## 10. What the AI System Is Not Permitted To Do

- Autonomously write to any field device register (any Purdue Level 0-3 asset).
- Autonomously push firmware to any device.
- Autonomously modify OT network routing or firewall policy without human approval.
- Send OT telemetry to any third-party cloud service without explicit customer DPA and configuration.
- Delete, truncate, or update any row in WORM tables (`agent_decisions`, `human_approvals`, `audit_log`).
- Operate with `ORHASHIELD_AUTONOMOUS_MODE=disabled` overridden by any agent action.
- Skip the digital twin pre-flight for any write-class action.

## 11. Safety Case Reference

Autonomous action capabilities are designed in alignment with:
- IEC 61508: Functional Safety of Electrical/Electronic/Programmable Electronic Safety-related Systems
- ISA-84 / IEC 61511: Safety Instrumented Systems for the Process Industry
- NIST AI RMF: AI Risk Management Framework
- ISO/IEC 42001: Artificial Intelligence Management System

Any expansion of autonomous action scope (e.g., relaxing Level 2 to autonomous `ISOLATE_NETWORK`) requires:
1. A formal safety analysis update
2. Digital twin validation covering the new action scope
3. Customer written authorization
4. A new ADR documenting the change
5. CI enforcement of the new policy via Rego unit tests
