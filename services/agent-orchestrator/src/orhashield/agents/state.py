"""OrHaShield OT agent state model — the single source of truth for a detection session."""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Sequence

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class PurdueLevel(int, Enum):
    LEVEL_0 = 0  # Physical process: sensors, actuators
    LEVEL_1 = 1  # Basic control: PLCs, RTUs, IEDs
    LEVEL_2 = 2  # Area supervisory: HMI, SCADA servers
    LEVEL_3 = 3  # Site operations: historians, app servers
    LEVEL_3_5 = 4  # Industrial DMZ (internally represented as 4)
    LEVEL_4 = 5  # Enterprise: IT systems


class ActionClass(str, Enum):
    OBSERVE = "observe"
    ALERT = "alert"
    ISOLATE_NETWORK = "isolate_network"
    MODIFY_SETPOINT = "modify_setpoint"
    FIRMWARE_UPDATE = "firmware_update"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Asset(BaseModel):
    asset_id: str
    ip_address: str
    mac_address: str | None = None
    vendor: str | None = None
    model: str | None = None
    purdue_level: PurdueLevel = PurdueLevel.LEVEL_3
    protocols: list[str] = Field(default_factory=list)
    criticality: Severity = Severity.MEDIUM
    hostname: str | None = None


class Alert(BaseModel):
    alert_id: str
    asset_id: str
    severity: Severity
    description: str
    raw_event_id: str
    timestamp: str  # ISO 8601
    rule_id: str | None = None
    mitre_technique: str | None = None


class Hypothesis(BaseModel):
    hypothesis_id: str
    description: str
    confidence: float  # 0.0–1.0
    attack_technique: str  # MITRE ATT&CK for ICS (e.g. "T0855")
    attack_technique_name: str = ""
    supporting_evidence: list[str] = Field(default_factory=list)
    model_used: str = ""
    cross_check_agreed: bool | None = None
    cross_check_note: str | None = None


class ActionRequest(BaseModel):
    action_id: str
    action_class: ActionClass
    asset_id: str
    purdue_level: PurdueLevel
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    proposed_by: str = ""  # agent node name
    hypothesis_id: str = ""
    confidence: float = 0.0
    severity: Severity = Severity.MEDIUM
    twin_verified: bool = False
    requires_human: bool = True  # default True; gate can relax for OBSERVE/ALERT


class HumanApproval(BaseModel):
    action_id: str
    approved: bool
    approver_id: str
    timestamp: str
    notes: str = ""


class OTState(BaseModel):
    """Central LangGraph state for a single OT detection/response session."""

    # Session context (immutable after graph entry)
    session_id: str
    site_id: str

    # Message history (LangGraph reducer: append-only)
    messages: Annotated[Sequence[dict[str, Any]], add_messages] = Field(default_factory=list)

    # Accumulated intelligence (append-only during session)
    assets: list[Asset] = Field(default_factory=list)
    alerts: list[Alert] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    actions_queue: list[ActionRequest] = Field(default_factory=list)
    approved_actions: list[ActionRequest] = Field(default_factory=list)
    denied_actions: list[ActionRequest] = Field(default_factory=list)
    human_approvals: list[HumanApproval] = Field(default_factory=list)

    # Processing focus (set by supervisor)
    current_alert_id: str | None = None
    current_hypothesis_id: str | None = None

    # Reflexion / critic
    critic_feedback: str | None = None
    iteration_count: int = 0
    max_iterations: int = 3  # circuit breaker

    # Control
    halt: bool = False
    error: str | None = None

    class Config:
        arbitrary_types_allowed = True
