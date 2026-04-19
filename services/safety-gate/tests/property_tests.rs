/// Property-based tests for OrHaShield safety gate invariants.
///
/// These tests verify the three hardest safety invariants:
/// 1. MODIFY_SETPOINT is ALWAYS denied, regardless of any other field.
/// 2. OBSERVE is ALWAYS allowed, regardless of any other field.
/// 3. Level 0-1 assets NEVER receive an autonomous ALLOW for non-OBSERVE/ALERT actions.
#[cfg(test)]
mod property_tests {
    use orhashield_safety_gate::action::{ActionClass, ActionRequest, Decision, Severity};
    use orhashield_safety_gate::evaluator::PolicyEvaluator;
    use proptest::prelude::*;
    use uuid::Uuid;

    fn test_evaluator() -> PolicyEvaluator {
        PolicyEvaluator::new("policy/orhashield.rego")
            .expect("Failed to load policy — ensure tests run from services/safety-gate/")
    }

    fn make_request(
        action_class: ActionClass,
        purdue_level: u8,
        confidence: f32,
        twin_verified: bool,
        severity: Severity,
    ) -> ActionRequest {
        ActionRequest {
            action_id: Uuid::new_v4(),
            action_class,
            asset_id: "test-asset".to_string(),
            purdue_level,
            description: "test action".to_string(),
            parameters: serde_json::Value::Object(serde_json::Map::new()),
            confidence,
            severity,
            twin_verified,
            requires_human: true,
            proposed_by: "test".to_string(),
            hypothesis_id: "test".to_string(),
        }
    }

    proptest! {
        /// Safety invariant 1: MODIFY_SETPOINT is ALWAYS denied.
        #[test]
        fn modify_setpoint_always_denied(
            purdue_level in 0u8..=5u8,
            confidence in 0.0f32..=1.0f32,
            twin_verified in any::<bool>(),
        ) {
            let req = make_request(
                ActionClass::ModifySetpoint,
                purdue_level,
                confidence,
                twin_verified,
                Severity::Medium,
            );
            let mut evaluator = test_evaluator();
            let decision = evaluator.evaluate_action(&req).expect("evaluation failed");
            prop_assert_eq!(decision.decision, Decision::Deny,
                "MODIFY_SETPOINT must ALWAYS be denied; got {:?} for level={} conf={} twin={}",
                decision.decision, purdue_level, confidence, twin_verified
            );
        }

        /// Safety invariant 2: FIRMWARE_UPDATE is ALWAYS denied.
        #[test]
        fn firmware_update_always_denied(
            purdue_level in 0u8..=5u8,
            confidence in 0.0f32..=1.0f32,
            twin_verified in any::<bool>(),
        ) {
            let req = make_request(
                ActionClass::FirmwareUpdate,
                purdue_level,
                confidence,
                twin_verified,
                Severity::Medium,
            );
            let mut evaluator = test_evaluator();
            let decision = evaluator.evaluate_action(&req).expect("evaluation failed");
            prop_assert_eq!(decision.decision, Decision::Deny,
                "FIRMWARE_UPDATE must ALWAYS be denied"
            );
        }

        /// Safety invariant 3: OBSERVE is ALWAYS allowed.
        #[test]
        fn observe_always_allowed(
            purdue_level in 0u8..=5u8,
            confidence in 0.0f32..=1.0f32,
        ) {
            let req = make_request(
                ActionClass::Observe,
                purdue_level,
                confidence,
                false,
                Severity::Info,
            );
            let mut evaluator = test_evaluator();
            let decision = evaluator.evaluate_action(&req).expect("evaluation failed");
            prop_assert_eq!(decision.decision, Decision::Allow,
                "OBSERVE must ALWAYS be allowed; got {:?} for level={}", decision.decision, purdue_level
            );
        }

        /// Safety invariant 4: Level 0-1 assets never get ALLOW for non-OBSERVE/ALERT actions.
        #[test]
        fn level_0_1_never_autonomous_action(
            purdue_level in 0u8..=1u8,
            confidence in 0.0f32..=1.0f32,
        ) {
            for action_class in [
                ActionClass::IsolateNetwork,
                ActionClass::ModifySetpoint,
                ActionClass::FirmwareUpdate,
            ] {
                let req = make_request(
                    action_class.clone(),
                    purdue_level,
                    confidence,
                    true,
                    Severity::Low,
                );
                let mut evaluator = test_evaluator();
                let decision = evaluator.evaluate_action(&req).expect("evaluation failed");
                prop_assert_ne!(
                    decision.decision,
                    Decision::Allow,
                    "Level 0-1 action {:?} must never be ALLOW; level={} conf={}",
                    action_class, purdue_level, confidence
                );
            }
        }

        /// Safety invariant 5: Low confidence (<0.7) ISOLATE_NETWORK is never ALLOW.
        #[test]
        fn low_confidence_isolate_never_allowed(
            purdue_level in 0u8..=5u8,
            confidence in 0.0f32..0.7f32,
        ) {
            let req = make_request(
                ActionClass::IsolateNetwork,
                purdue_level,
                confidence,
                true,
                Severity::Medium,
            );
            let mut evaluator = test_evaluator();
            let decision = evaluator.evaluate_action(&req).expect("evaluation failed");
            prop_assert_ne!(
                decision.decision,
                Decision::Allow,
                "ISOLATE_NETWORK with confidence<0.7 must never be ALLOW; level={} conf={}",
                purdue_level, confidence
            );
        }
    }

    /// Unit test: fail-closed on missing policy file.
    #[test]
    fn evaluator_fails_on_missing_policy() {
        let result = PolicyEvaluator::new("/nonexistent/policy.rego");
        assert!(result.is_err(), "Expected error for missing policy file");
    }
}
