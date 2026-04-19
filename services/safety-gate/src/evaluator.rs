use anyhow::Result;
use regorus::Engine;

use crate::action::{ActionDecision, ActionRequest, Decision};

/// PolicyEvaluator wraps a regorus Rego engine and evaluates ActionRequests
/// against the OrHaShield OPA policy bundle.
///
/// # Safety invariants (property-tested in tests/property_tests.rs)
/// 1. MODIFY_SETPOINT → always DENY, regardless of any other field.
/// 2. FIRMWARE_UPDATE → always DENY, regardless of any other field.
/// 3. OBSERVE → always ALLOW, regardless of any other field.
/// 4. Purdue level 0-1 + any non-OBSERVE/ALERT action → never ALLOW.
pub struct PolicyEvaluator {
    policy_path: String,
    policy_version: String,
    autonomous_mode: String,
}

impl PolicyEvaluator {
    /// Create a new PolicyEvaluator loading the policy from the given path.
    pub fn new(policy_path: &str) -> Result<Self> {
        let policy_version = Self::read_policy_version(policy_path)?;
        let autonomous_mode =
            std::env::var("ORHASHIELD_AUTONOMOUS_MODE").unwrap_or_else(|_| "enabled".to_string());

        tracing::info!(
            policy_path = policy_path,
            policy_version = %policy_version,
            autonomous_mode = %autonomous_mode,
            "Policy evaluator initialized"
        );

        Ok(Self {
            policy_path: policy_path.to_string(),
            policy_version,
            autonomous_mode,
        })
    }

    /// Evaluate an ActionRequest against the Rego policy.
    ///
    /// Fails closed: any internal error returns a DENY decision.
    pub fn evaluate_action(&mut self, req: &ActionRequest) -> Result<ActionDecision> {
        // Build regorus engine fresh per evaluation to avoid state leakage.
        let mut engine = Engine::new();
        engine.add_policy_from_file(self.policy_path.clone())?;

        // Build input JSON including the kill switch state.
        let mut input_value = serde_json::to_value(req)?;
        if let Some(obj) = input_value.as_object_mut() {
            obj.insert(
                "autonomous_mode".to_string(),
                serde_json::Value::String(self.autonomous_mode.clone()),
            );
        }

        engine.set_input(regorus::Value::from_json_str(&input_value.to_string())?);

        // Query decision and reason.
        let decision_val = engine
            .eval_rule("data.orhashield.authz.decision")
            .map_err(|e| anyhow::anyhow!("Rego eval error: {e}"))?;

        let reason_val = engine
            .eval_rule("data.orhashield.authz.reason")
            .unwrap_or_else(|_| regorus::Value::from_json_str("\"Policy evaluation error\"").unwrap());

        let decision = match decision_val.as_str() {
            Some("allow") => Decision::Allow,
            Some("escalate") => Decision::Escalate,
            _ => Decision::Deny, // fail-closed: unknown result = deny
        };

        let reason = reason_val
            .as_str()
            .unwrap_or("No reason provided")
            .to_string();

        tracing::debug!(
            action_id = %req.action_id,
            action_class = ?req.action_class,
            purdue_level = req.purdue_level,
            confidence = req.confidence,
            decision = ?decision,
            reason = %reason,
        );

        Ok(ActionDecision {
            action_id: req.action_id,
            decision,
            reason,
            evaluated_at: chrono::Utc::now(),
            policy_version: self.policy_version.clone(),
        })
    }

    fn read_policy_version(policy_path: &str) -> Result<String> {
        // Extract version from the first `policy_version := "x.y.z"` line.
        let content = std::fs::read_to_string(policy_path)
            .map_err(|e| anyhow::anyhow!("Cannot read policy file {policy_path}: {e}"))?;

        for line in content.lines() {
            if line.trim().starts_with("policy_version :=") {
                if let Some(ver) = line.split('"').nth(1) {
                    return Ok(ver.to_string());
                }
            }
        }
        Ok("unknown".to_string())
    }
}
