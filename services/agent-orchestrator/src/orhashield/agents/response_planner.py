"""Response planner node — converts hypotheses into concrete OT-safe ActionRequests."""
from __future__ import annotations

import json
import uuid
from typing import Any

import anthropic
import structlog
from langchain_core.runnables import RunnableConfig

from orhashield.agents.state import (
    ActionClass,
    ActionRequest,
    Hypothesis,
    OTState,
    PurdueLevel,
    Severity,
)

log = structlog.get_logger(__name__)

RESPONSE_SYSTEM_PROMPT = """You are an OT incident response planner for the OrHaShield platform.
Given a security hypothesis and asset context, propose ONE specific, safe response action.

Strict rules:
- NEVER propose MODIFY_SETPOINT or FIRMWARE_UPDATE — these are permanently prohibited for automation
- For Level 0-1 assets: only propose OBSERVE or ALERT
- For Level 2 assets: you may propose ISOLATE_NETWORK but it requires human approval
- For Level 3.5+: you may propose ISOLATE_NETWORK if confidence >= 0.7

Output ONLY a JSON object (no markdown):
{
  "action_class": "<observe|alert|isolate_network>",
  "description": "<clear description of the action and expected outcome>",
  "parameters": {"<key>": "<value>"},
  "confidence": <float 0.0-1.0>,
  "severity": "<info|low|medium|high|critical>",
  "requires_human": <true|false>
}"""


async def response_planner_node(state: OTState, config: RunnableConfig) -> dict[str, Any]:
    """Plan a response action for the highest-confidence hypothesis."""
    if not state.hypotheses:
        return {}

    hypothesis = max(state.hypotheses, key=lambda h: h.confidence)
    if hypothesis.confidence < 0.3:
        log.info("hypothesis_confidence_too_low", confidence=hypothesis.confidence)
        return {}

    asset = next((a for a in state.assets if a.asset_id == _get_alert_asset_id(state)), None)
    client = anthropic.AsyncAnthropic()

    prompt = _build_prompt(hypothesis, asset)

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system=RESPONSE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text  # type: ignore[union-attr]
        parsed = json.loads(raw)
    except Exception as exc:
        log.error("response_planning_failed", error=str(exc))
        return {}

    action_class_str = parsed.get("action_class", "observe")
    try:
        action_class = ActionClass(action_class_str)
    except ValueError:
        action_class = ActionClass.OBSERVE

    # Safety enforcement: never plan MODIFY_SETPOINT or FIRMWARE_UPDATE.
    if action_class in (ActionClass.MODIFY_SETPOINT, ActionClass.FIRMWARE_UPDATE):
        log.warning("llm_proposed_forbidden_action", action_class=action_class_str)
        action_class = ActionClass.ALERT  # Demote to ALERT.

    purdue = asset.purdue_level if asset else PurdueLevel.LEVEL_3
    severity = Severity(parsed.get("severity", "medium"))

    requires_human = _requires_human(action_class, purdue)

    action = ActionRequest(
        action_id=str(uuid.uuid4()),
        action_class=action_class,
        asset_id=asset.asset_id if asset else "unknown",
        purdue_level=purdue,
        description=parsed.get("description", ""),
        parameters=parsed.get("parameters", {}),
        proposed_by="response_planner",
        hypothesis_id=hypothesis.hypothesis_id,
        confidence=float(parsed.get("confidence", hypothesis.confidence)),
        severity=severity,
        requires_human=requires_human,
        twin_verified=False,
    )

    log.info(
        "action_planned",
        action_id=action.action_id,
        action_class=action_class.value,
        requires_human=requires_human,
        confidence=action.confidence,
    )

    return {"actions_queue": state.actions_queue + [action]}


def _requires_human(action_class: ActionClass, purdue: PurdueLevel) -> bool:
    if action_class in (ActionClass.OBSERVE, ActionClass.ALERT):
        return False
    if action_class == ActionClass.ISOLATE_NETWORK and purdue.value >= PurdueLevel.LEVEL_3_5.value:
        return False  # Policy-gated only; safety gate will evaluate.
    return True  # Everything else requires explicit human approval.


def _build_prompt(hypothesis: Hypothesis, asset: Any) -> str:
    lines = [
        f"Hypothesis: {hypothesis.description}",
        f"Confidence: {hypothesis.confidence:.2f}",
        f"Attack technique: {hypothesis.attack_technique} ({hypothesis.attack_technique_name})",
        f"Evidence: {', '.join(hypothesis.supporting_evidence)}",
    ]
    if asset:
        lines += [
            f"Asset IP: {asset.ip_address}",
            f"Vendor: {asset.vendor or 'unknown'}",
            f"Purdue level: {asset.purdue_level.name}",
            f"Criticality: {asset.criticality.value}",
        ]
    return "\n".join(lines)


def _get_alert_asset_id(state: OTState) -> str:
    alert = next((a for a in state.alerts if a.alert_id == state.current_alert_id), None)
    if alert:
        return alert.asset_id
    return state.alerts[0].asset_id if state.alerts else "unknown"
