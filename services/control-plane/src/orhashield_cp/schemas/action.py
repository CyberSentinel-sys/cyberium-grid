from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ActionClassEnum(str, Enum):
    OBSERVE = "observe"
    ALERT = "alert"
    ISOLATE_NETWORK = "isolate_network"
    MODIFY_SETPOINT = "modify_setpoint"
    FIRMWARE_UPDATE = "firmware_update"


class HumanApprovalCreate(BaseModel):
    action_id: str
    approved: bool
    approver_id: str
    notes: str = ""


class ApprovalResponse(BaseModel):
    approval_id: str
    action_id: str
    approved: bool
    approver_id: str
    notes: str
    approved_at: datetime

    model_config = {"from_attributes": True}
