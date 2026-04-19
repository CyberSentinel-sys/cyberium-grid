# OrHaShield — Purdue Model Action Matrix

This document is the authoritative reference for what the AI system is and is not permitted to do at each Purdue model level. The Rust safety gate's OPA policy enforces these rules deterministically.

## Purdue Level Definitions

| Level | Name | Typical Assets |
|---|---|---|
| 0 | Physical Process | Sensors, actuators, valves, pumps, motors |
| 1 | Basic Control | PLCs, RTUs, IEDs, safety systems, controllers |
| 2 | Area Supervisory | HMI workstations, SCADA servers, DCS stations |
| 3 | Site Operations | Historians, engineering workstations, application servers |
| 3.5 | Industrial DMZ | Firewalls, data diodes, jump servers, patch management |
| 4 | Enterprise | Business systems, IT endpoints, email, ERP |
| 5 | Enterprise Cloud | SaaS, cloud workloads |

## Action Class Definitions

| Action Class | Code | Description |
|---|---|---|
| OBSERVE | `observe` | Read-only data collection: PCAP capture, SNMP poll, asset fingerprinting |
| ALERT | `alert` | Generate a notification: SIEM event, email, PagerDuty, Teams message |
| ISOLATE_NETWORK | `isolate_network` | Block device connectivity: firewall rule, NAC quarantine, VLAN move |
| MODIFY_SETPOINT | `modify_setpoint` | Write to field device: PLC register write, valve position, pump speed |
| FIRMWARE_UPDATE | `firmware_update` | Push firmware or configuration to any device |

## Permission Matrix

| Level | OBSERVE | ALERT | ISOLATE_NETWORK | MODIFY_SETPOINT | FIRMWARE_UPDATE |
|---|---|---|---|---|---|
| **0** | ✅ Auto | ✅ Auto | ❌ Never | ❌ Never | ❌ Never |
| **1** | ✅ Auto | ✅ Auto | ❌ Never | ❌ Never | ❌ Never |
| **2** | ✅ Auto | ✅ Auto | ⚠️ Dual-human + twin | ❌ Never | ❌ Never |
| **3** | ✅ Auto | ✅ Auto | ⚠️ Human-gated + twin | ❌ Never | ❌ Never |
| **3.5** | ✅ Auto | ✅ Auto | ✅ Policy-gated (conf ≥0.7 + twin) | ❌ Never | ❌ Never |
| **4** | ✅ Auto | ✅ Auto | ✅ Policy-gated | ❌ Change control | ❌ Change control |
| **5** | ✅ Auto | ✅ Auto | ✅ Policy-gated | ❌ Change control | ❌ Change control |

**Legend:**
- ✅ Auto — Autonomous execution permitted (no human approval required)
- ⚠️ Human-gated — Human approval required via Approval Queue (5-min timeout → auto-deny)
- ⚠️ Dual-human — Two approvals required: standard operator + OT engineer role
- ✅ Policy-gated — OPA policy evaluation only (confidence threshold + twin verification)
- ❌ Never — Permanently prohibited for autonomous or policy-gated execution
- ❌ Change control — Requires formal change management process (out-of-band)

## Escalation Paths

When an action is escalated (not outright denied), the following applies:

1. Action is queued in the Approval Queue with escalation flag set.
2. Notification sent to on-call OT engineer (PagerDuty/Opsgenie integration).
3. If no response within **15 minutes**, action is automatically **denied** and logged.
4. Escalated actions require a mandatory note from the approver explaining the authorization basis.

## Overrides

Customer site administrators can configure per-asset-class relaxations via the control-plane API (stored in the `site_policies` table), subject to:

1. The relaxation must not violate the absolute prohibitions (MODIFY_SETPOINT, FIRMWARE_UPDATE are always off-limits for autonomous execution).
2. The relaxation must be documented with a justification.
3. Relaxations are audited monthly and flagged for review if not referenced in any approved action.

## OPA Policy Mapping

The following Rego rules in `policy/orhashield.rego` implement this matrix:

| Matrix Rule | Rego Rule |
|---|---|
| OBSERVE always allowed | `decision := "allow" { input.action_class == "observe" }` |
| ALERT always allowed | `decision := "allow" { input.action_class == "alert" }` |
| ISOLATE_NETWORK L3.5+ with twin+conf | `decision := "allow" { input.action_class == "isolate_network"; input.purdue_level >= 3; input.twin_verified; input.confidence >= 0.7 }` |
| ISOLATE_NETWORK L2 escalate | `decision := "escalate" { input.action_class == "isolate_network"; input.purdue_level == 2 }` |
| ISOLATE_NETWORK L0-1 never | default deny catches this |
| MODIFY_SETPOINT always deny | explicit deny rule |
| FIRMWARE_UPDATE always deny | explicit deny rule |
| CRITICAL severity escalate | explicit escalate rule |
