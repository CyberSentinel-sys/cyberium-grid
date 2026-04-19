"""Critic node — Reflexion loop that evaluates detection quality and triggers re-analysis."""
from __future__ import annotations

import json
from typing import Any

import anthropic
import structlog
from langchain_core.runnables import RunnableConfig

from orhashield.agents.state import OTState

log = structlog.get_logger(__name__)

CRITIC_SYSTEM_PROMPT = """You are a senior OT security analyst reviewing an automated detection session.
Evaluate whether the hypothesis and response plan are appropriate given the evidence.

Output ONLY a JSON object (no markdown):
{
  "needs_revision": <true|false>,
  "feedback": "<specific feedback if needs_revision is true, empty string otherwise>",
  "reason": "<brief explanation of your evaluation>"
}

Only set needs_revision=true if there is a clear gap in reasoning. Do not revise for minor issues."""


async def critic_node(state: OTState, config: RunnableConfig) -> dict[str, Any]:
    """Evaluate hypothesis and action quality; return feedback for Reflexion loop if needed."""
    if not state.hypotheses:
        return {"critic_feedback": None}

    client = anthropic.AsyncAnthropic()

    evaluation_prompt = _build_evaluation(state)

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",  # Cheaper model for critique.
            max_tokens=256,
            system=CRITIC_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": evaluation_prompt}],
        )
        raw = response.content[0].text  # type: ignore[union-attr]
        parsed = json.loads(raw)
    except Exception as exc:
        log.error("critic_failed", error=str(exc))
        return {"critic_feedback": None}

    needs_revision = bool(parsed.get("needs_revision", False))
    feedback = str(parsed.get("feedback", ""))
    reason = str(parsed.get("reason", ""))

    log.info("critic_evaluated", needs_revision=needs_revision, reason=reason)

    if needs_revision and state.iteration_count < state.max_iterations:
        return {"critic_feedback": feedback}

    return {"critic_feedback": None}  # Signal to supervisor: session is complete.


def _build_evaluation(state: OTState) -> str:
    lines = ["Detection session summary:"]
    for alert in state.alerts[:3]:  # Limit to 3 most recent alerts for context window.
        lines.append(f"  Alert: {alert.severity.value} — {alert.description}")

    for h in state.hypotheses[:2]:
        lines.append(f"  Hypothesis (conf={h.confidence:.2f}): {h.description}")
        lines.append(f"    Technique: {h.attack_technique}")
        lines.append(f"    Cross-check agreed: {h.cross_check_agreed}")

    for a in state.actions_queue[:2]:
        lines.append(f"  Proposed action: {a.action_class.value} — {a.description}")

    for a in state.approved_actions[:2]:
        lines.append(f"  Approved: {a.action_class.value}")

    for a in state.denied_actions[:2]:
        lines.append(f"  Denied: {a.action_class.value}")

    return "\n".join(lines)
