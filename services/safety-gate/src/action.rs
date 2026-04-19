use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// OT action classes ordered by risk level.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ActionClass {
    /// Read-only observation — always allowed.
    Observe,
    /// Notification only — always allowed.
    Alert,
    /// Block device at firewall/NAC — policy-gated.
    IsolateNetwork,
    /// Write to field device register — NEVER autonomous.
    ModifySetpoint,
    /// Push firmware to device — NEVER autonomous.
    FirmwareUpdate,
}

/// Alert severity levels.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(rename_all = "snake_case")]
pub enum Severity {
    Info,
    Low,
    Medium,
    High,
    Critical,
}

/// An action proposed by the agent orchestrator for safety gate evaluation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActionRequest {
    pub action_id: Uuid,
    pub action_class: ActionClass,
    pub asset_id: String,
    /// Purdue model level: 0-5 (4 = Level 3.5 DMZ).
    pub purdue_level: u8,
    pub description: String,
    pub parameters: serde_json::Value,
    pub confidence: f32,
    pub severity: Severity,
    pub twin_verified: bool,
    pub requires_human: bool,
    pub proposed_by: String,
    pub hypothesis_id: String,
}

/// The safety gate decision for an action.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum Decision {
    /// Action is permitted — forward to response executor.
    Allow,
    /// Action is denied — log and discard.
    Deny,
    /// Requires elevated human review before proceeding.
    Escalate,
}

/// The full decision record emitted by the safety gate.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActionDecision {
    pub action_id: Uuid,
    pub decision: Decision,
    pub reason: String,
    pub evaluated_at: DateTime<Utc>,
    pub policy_version: String,
}

impl ActionDecision {
    /// Returns the NATS subject for publishing this decision.
    pub fn nats_subject(&self) -> &'static str {
        match self.decision {
            Decision::Allow => "ot.actions.approved",
            Decision::Deny => "ot.actions.denied",
            Decision::Escalate => "ot.actions.escalate",
        }
    }
}
