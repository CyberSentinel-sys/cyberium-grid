"""Hypothesis generator node — uses Claude claude-sonnet-4-6 to generate attack hypotheses.

Two-model verification is applied for HIGH and CRITICAL severity alerts:
  - Proposing model: claude-sonnet-4-6
  - Cross-checking model: claude-haiku-4-5-20251001
"""
from __future__ import annotations

import json
import uuid
from typing import Any

import anthropic
import structlog
from langchain_core.runnables import RunnableConfig

from orhashield.agents.state import Alert, Asset, Hypothesis, OTState, Severity

log = structlog.get_logger(__name__)

HYPOTHESIS_SYSTEM_PROMPT = """You are an expert OT/ICS cybersecurity analyst for the OrHaShield platform.
Your task is to generate a single, specific attack hypothesis based on the OT alert and asset context provided.

Output ONLY a JSON object with these exact fields (no markdown, no explanation):
{
  "description": "<concise description of the hypothesized attack>",
  "confidence": <float 0.0-1.0>,
  "attack_technique": "<MITRE ATT&CK for ICS technique ID e.g. T0855>",
  "attack_technique_name": "<human-readable technique name>",
  "supporting_evidence": ["<evidence point 1>", "<evidence point 2>"]
}

IMPORTANT safety rules:
- Never suggest actions that could harm physical processes
- Focus on detection and observation, not exploitation
- If confidence is below 0.5, say so clearly
- Base your hypothesis strictly on the provided evidence"""

CROSS_CHECK_SYSTEM_PROMPT = """You are a second cybersecurity analyst performing an independent review.
Evaluate whether you agree with the following attack hypothesis about an OT/ICS alert.

Output ONLY a JSON object (no markdown):
{
  "agrees": <true|false>,
  "confidence_adjustment": <float -0.3 to 0.3>,
  "reason": "<brief explanation>"
}"""


async def hypothesis_generator_node(state: OTState, config: RunnableConfig) -> dict[str, Any]:
    """Generate an attack hypothesis using Claude claude-sonnet-4-6 with two-model verification for HIGH/CRITICAL."""
    if not state.alerts:
        return {}

    alert = _get_current_alert(state)
    if alert is None:
        return {}

    asset = _get_asset(state, alert.asset_id)
    client = anthropic.AsyncAnthropic()

    context = _build_context(alert, asset)

    log.info("generating_hypothesis", alert_id=alert.alert_id, severity=alert.severity.value)

    # Primary hypothesis from claude-sonnet-4-6.
    try:
        primary_response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=HYPOTHESIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": context}],
        )
        raw = primary_response.content[0].text  # type: ignore[union-attr]
        parsed = json.loads(raw)
    except Exception as exc:
        log.error("hypothesis_generation_failed", error=str(exc))
        return {"error": f"Hypothesis generation failed: {exc}"}

    hypothesis = Hypothesis(
        hypothesis_id=str(uuid.uuid4()),
        description=parsed.get("description", ""),
        confidence=float(parsed.get("confidence", 0.5)),
        attack_technique=parsed.get("attack_technique", "T0000"),
        attack_technique_name=parsed.get("attack_technique_name", ""),
        supporting_evidence=parsed.get("supporting_evidence", []),
        model_used="claude-sonnet-4-6",
    )

    # Two-model verification for HIGH and CRITICAL alerts.
    if alert.severity in (Severity.HIGH, Severity.CRITICAL):
        hypothesis = await _cross_check(client, hypothesis, context, alert)

    log.info(
        "hypothesis_generated",
        hypothesis_id=hypothesis.hypothesis_id,
        confidence=hypothesis.confidence,
        technique=hypothesis.attack_technique,
        cross_check_agreed=hypothesis.cross_check_agreed,
    )

    return {"hypotheses": state.hypotheses + [hypothesis]}


async def _cross_check(
    client: anthropic.AsyncAnthropic,
    hypothesis: Hypothesis,
    original_context: str,
    alert: Alert,
) -> Hypothesis:
    """Cross-check the hypothesis using claude-haiku-4-5-20251001."""
    try:
        cross_prompt = (
            f"Original alert context:\n{original_context}\n\n"
            f"Proposed hypothesis:\n{hypothesis.description}\n"
            f"Confidence: {hypothesis.confidence}\n"
            f"Technique: {hypothesis.attack_technique}\n"
            f"Evidence: {hypothesis.supporting_evidence}"
        )
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            system=CROSS_CHECK_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": cross_prompt}],
        )
        raw = response.content[0].text  # type: ignore[union-attr]
        parsed = json.loads(raw)
        agrees = bool(parsed.get("agrees", True))
        adjustment = float(parsed.get("confidence_adjustment", 0.0))
        reason = str(parsed.get("reason", ""))

        new_confidence = max(0.0, min(1.0, hypothesis.confidence + adjustment))
        if not agrees:
            new_confidence *= 0.6  # Halve confidence on disagreement (safety margin).
            log.warning(
                "cross_check_disagreement",
                alert_severity=alert.severity.value,
                reason=reason,
                original_confidence=hypothesis.confidence,
                adjusted_confidence=new_confidence,
            )

        return hypothesis.model_copy(update={
            "confidence": new_confidence,
            "cross_check_agreed": agrees,
            "cross_check_note": reason,
        })
    except Exception as exc:
        log.error("cross_check_failed", error=str(exc))
        # On cross-check failure, reduce confidence conservatively.
        return hypothesis.model_copy(update={
            "confidence": hypothesis.confidence * 0.8,
            "cross_check_agreed": None,
            "cross_check_note": f"Cross-check failed: {exc}",
        })


def _build_context(alert: Alert, asset: Asset | None) -> str:
    lines = [
        f"Alert severity: {alert.severity.value}",
        f"Alert description: {alert.description}",
        f"Rule ID: {alert.rule_id or 'N/A'}",
        f"MITRE technique hint: {alert.mitre_technique or 'unknown'}",
        f"Timestamp: {alert.timestamp}",
    ]
    if asset:
        lines += [
            f"Asset IP: {asset.ip_address}",
            f"Vendor: {asset.vendor or 'unknown'}",
            f"Model: {asset.model or 'unknown'}",
            f"Protocols: {', '.join(asset.protocols) or 'unknown'}",
            f"Purdue level: {asset.purdue_level.name}",
            f"Criticality: {asset.criticality.value}",
        ]
    else:
        lines.append("Asset: unknown (no inventory entry)")
    return "\n".join(lines)


def _get_current_alert(state: OTState) -> Alert | None:
    if state.current_alert_id:
        for a in state.alerts:
            if a.alert_id == state.current_alert_id:
                return a
    return state.alerts[0] if state.alerts else None


def _get_asset(state: OTState, asset_id: str) -> Asset | None:
    for a in state.assets:
        if a.asset_id == asset_id:
            return a
    return None
