mod action;
mod evaluator;

use anyhow::Result;
use async_nats::Client;
use evaluator::PolicyEvaluator;
use tracing::Instrument;

#[tokio::main]
async fn main() -> Result<()> {
    // Structured JSON logging for log aggregation.
    tracing_subscriber::fmt()
        .json()
        .with_env_filter(
            tracing_subscriber::EnvFilter::from_default_env()
                .add_directive("orhashield_safety_gate=info".parse()?),
        )
        .init();

    let nats_url = std::env::var("NATS_URL").unwrap_or_else(|_| "nats://localhost:4222".to_string());
    let policy_path =
        std::env::var("POLICY_PATH").unwrap_or_else(|_| "policy/orhashield.rego".to_string());

    tracing::info!(
        nats_url = %nats_url,
        policy_path = %policy_path,
        "OrHaShield Safety Gate starting"
    );

    let mut evaluator = PolicyEvaluator::new(&policy_path)?;
    let client = async_nats::connect(&nats_url).await?;

    tracing::info!("Connected to NATS — subscribing to ot.actions.proposed");

    let mut sub = client.subscribe("ot.actions.proposed").await?;

    while let Some(msg) = sub.next().await {
        let span = tracing::info_span!("evaluate_action");
        let client_ref = client.clone();

        match process_message(&mut evaluator, &client_ref, msg).await {
            Ok(()) => {}
            Err(e) => {
                tracing::error!(error = %e, "Action evaluation failed");
            }
        }
    }

    tracing::info!("Safety gate shutting down");
    Ok(())
}

async fn process_message(
    evaluator: &mut PolicyEvaluator,
    client: &Client,
    msg: async_nats::Message,
) -> Result<()> {
    let req: action::ActionRequest = match serde_json::from_slice(&msg.payload) {
        Ok(r) => r,
        Err(e) => {
            tracing::warn!(error = %e, "Failed to deserialize ActionRequest — sending deny");
            // Publish a deny for malformed input (fail-closed).
            let decision = action::ActionDecision {
                action_id: uuid::Uuid::new_v7(uuid::Timestamp::now(uuid::NoContext)),
                decision: action::Decision::Deny,
                reason: format!("Malformed ActionRequest payload: {e}"),
                evaluated_at: chrono::Utc::now(),
                policy_version: "unknown".to_string(),
            };
            publish_decision(client, &decision).await?;
            return Ok(());
        }
    };

    let decision = match evaluator.evaluate_action(&req) {
        Ok(d) => d,
        Err(e) => {
            tracing::error!(
                action_id = %req.action_id,
                error = %e,
                "Policy evaluation error — failing closed with DENY"
            );
            action::ActionDecision {
                action_id: req.action_id,
                decision: action::Decision::Deny,
                reason: format!("Safety gate internal error (fail-closed): {e}"),
                evaluated_at: chrono::Utc::now(),
                policy_version: "error".to_string(),
            }
        }
    };

    tracing::info!(
        action_id = %req.action_id,
        action_class = ?req.action_class,
        purdue_level = req.purdue_level,
        decision = ?decision.decision,
        "Safety gate decision"
    );

    publish_decision(client, &decision).await
}

async fn publish_decision(client: &Client, decision: &action::ActionDecision) -> Result<()> {
    let subject = decision.nats_subject();
    let payload = serde_json::to_vec(decision)?;
    client.publish(subject, payload.into()).await?;
    Ok(())
}
