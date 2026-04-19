# OrHaShield Safety Gate Policy
# Version: 0.1.0
# This policy is the authoritative source for allow/deny/escalate decisions.
# Changes require: (1) cargo test to verify property tests pass, (2) ADR update, (3) PR review.

package orhashield.authz

policy_version := "0.1.0"

# Fail-closed: default deny + reason.
default decision := "deny"
default reason := "No policy rule matched — default deny (fail-closed)"

# ── Always-allow rules ────────────────────────────────────────────────────────

# OBSERVE: read-only data collection — always permitted at any Purdue level.
decision := "allow" if {
    input.action_class == "observe"
}

reason := "OBSERVE actions are always permitted (read-only, no OT impact)" if {
    input.action_class == "observe"
}

# ALERT: notification only — always permitted at any Purdue level.
decision := "allow" if {
    input.action_class == "alert"
}

reason := "ALERT actions are always permitted (notification only, no OT impact)" if {
    input.action_class == "alert"
}

# ── Hard denials — safety invariants that MUST hold ──────────────────────────

# MODIFY_SETPOINT: NEVER autonomous — always deny regardless of any other field.
decision := "deny" if {
    input.action_class == "modify_setpoint"
}

reason := "MODIFY_SETPOINT requires dual human authorization and change control — contact OT engineer" if {
    input.action_class == "modify_setpoint"
}

# FIRMWARE_UPDATE: NEVER autonomous — always deny.
decision := "deny" if {
    input.action_class == "firmware_update"
}

reason := "FIRMWARE_UPDATE requires formal change control process — never autonomous" if {
    input.action_class == "firmware_update"
}

# ── ISOLATE_NETWORK rules (ordered by Purdue level) ───────────────────────────

# Level 0-1: never allow ISOLATE_NETWORK — escalate for human review.
decision := "escalate" if {
    input.action_class == "isolate_network"
    input.purdue_level <= 1
}

reason := "Network isolation on Level 0-1 (field device) requires OT engineer dual approval" if {
    input.action_class == "isolate_network"
    input.purdue_level <= 1
}

# Level 2: escalate — requires dual human approval.
decision := "escalate" if {
    input.action_class == "isolate_network"
    input.purdue_level == 2
}

reason := "Network isolation on Level 2 (area supervisory) requires elevated human approval" if {
    input.action_class == "isolate_network"
    input.purdue_level == 2
}

# Level 3: allow with twin verification + human gate + confidence threshold.
decision := "allow" if {
    input.action_class == "isolate_network"
    input.purdue_level == 3
    input.twin_verified == true
    input.confidence >= 0.7
    not input.severity == "critical"  # critical always escalates
}

reason := "Network isolation on Level 3 approved: twin verified, confidence sufficient" if {
    input.action_class == "isolate_network"
    input.purdue_level == 3
    input.twin_verified == true
    input.confidence >= 0.7
    not input.severity == "critical"
}

# Level 3.5 (DMZ) and above: policy-gated without twin requirement for network layer.
decision := "allow" if {
    input.action_class == "isolate_network"
    input.purdue_level >= 4  # Level 3.5 is represented as 4 internally
    input.confidence >= 0.7
    not input.severity == "critical"
}

reason := "Network isolation on DMZ/Enterprise approved: confidence threshold met" if {
    input.action_class == "isolate_network"
    input.purdue_level >= 4
    input.confidence >= 0.7
    not input.severity == "critical"
}

# ── Critical severity override ────────────────────────────────────────────────

# CRITICAL severity: always escalate (except OBSERVE and ALERT which are already allowed above).
decision := "escalate" if {
    input.severity == "critical"
    not input.action_class == "observe"
    not input.action_class == "alert"
    not input.action_class == "modify_setpoint"
    not input.action_class == "firmware_update"
}

reason := "CRITICAL severity always requires elevated human review regardless of action class" if {
    input.severity == "critical"
    not input.action_class == "observe"
    not input.action_class == "alert"
    not input.action_class == "modify_setpoint"
    not input.action_class == "firmware_update"
}

# ── Kill switch ───────────────────────────────────────────────────────────────

# ORHASHIELD_AUTONOMOUS_MODE=disabled: deny everything except OBSERVE and ALERT.
decision := "deny" if {
    input.autonomous_mode == "disabled"
    not input.action_class == "observe"
    not input.action_class == "alert"
}

reason := "Autonomous mode is disabled — all non-OBSERVE/ALERT actions denied" if {
    input.autonomous_mode == "disabled"
    not input.action_class == "observe"
    not input.action_class == "alert"
}
