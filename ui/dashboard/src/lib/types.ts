export type Severity = "info" | "low" | "medium" | "high" | "critical";
export type PurdueLevel = 0 | 1 | 2 | 3 | 4 | 5;
export type ActionClass =
  | "OBSERVE"
  | "ALERT"
  | "ISOLATE_NETWORK"
  | "MODIFY_SETPOINT"
  | "FIRMWARE_UPDATE";
export type Decision = "allow" | "deny" | "escalate";

export interface Asset {
  asset_id: string;
  ip_address: string;
  mac_address?: string;
  vendor?: string;
  model?: string;
  hostname?: string;
  purdue_level: PurdueLevel;
  criticality: Severity;
  protocols: string[];
  firmware_version?: string;
  site_id: string;
  created_at: string;
  updated_at: string;
}

export interface Alert {
  alert_id: string;
  asset_id?: string;
  severity: Severity;
  description: string;
  raw_event_id?: string;
  rule_id?: string;
  mitre_technique?: string;
  acknowledged: boolean;
  acknowledged_by?: string;
  acknowledged_at?: string;
  session_id?: string;
  created_at: string;
}

export interface AgentDecision {
  decision_id: number;
  session_id: string;
  action_id: string;
  action_class: ActionClass;
  asset_id?: string;
  purdue_level?: PurdueLevel;
  decision: Decision;
  reason: string;
  confidence?: number;
  severity?: Severity;
  model_used?: string;
  policy_version?: string;
  twin_verified: boolean;
  proposed_by?: string;
  decided_at: string;
}

export interface PendingAction {
  action_id: string;
  action_class: ActionClass;
  asset_id?: string;
  purdue_level?: PurdueLevel;
  reason: string;
  confidence?: number;
  severity?: Severity;
  proposed_at: string;
}

export interface ComplianceStatus {
  nerc_cip_015: number;
  iec_62443: number;
  nis2: number;
  phase: number;
  last_updated: string;
}

export interface RealtimeEvent {
  type: "alert" | "decision" | "action_proposed" | "action_resolved" | "heartbeat";
  payload: unknown;
  timestamp: string;
}

export interface DashboardStats {
  total_assets: number;
  active_alerts: number;
  critical_alerts: number;
  pending_actions: number;
  decisions_today: number;
  autonomous_mode: boolean;
}
