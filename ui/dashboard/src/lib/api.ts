import type {
  Alert,
  Asset,
  PendingAction,
  AgentDecision,
  ComplianceStatus,
  DashboardStats,
  PurdueLevel,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`${BASE}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  }
  const res = await fetch(url.toString(), {
    headers: { "Content-Type": "application/json" },
    next: { revalidate: 0 },
  });
  if (!res.ok) throw new Error(`GET ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

export const api = {
  assets: {
    list: (purdueLevel?: PurdueLevel) =>
      get<Asset[]>("/assets", purdueLevel != null ? { purdue_level: String(purdueLevel) } : undefined),
    get: (id: string) => get<Asset>(`/assets/${id}`),
  },

  alerts: {
    list: () => get<Alert[]>("/alerts"),
    acknowledge: (id: string) => post<Alert>(`/alerts/${id}/acknowledge`, {}),
  },

  actions: {
    pending: () => get<PendingAction[]>("/actions/pending"),
    approve: (actionId: string, approverId: string, notes = "") =>
      post("/actions/approve", { action_id: actionId, approved: true, approver_id: approverId, notes }),
    deny: (actionId: string, approverId: string, notes = "") =>
      post("/actions/approve", { action_id: actionId, approved: false, approver_id: approverId, notes }),
  },

  compliance: {
    status: () => get<ComplianceStatus>("/compliance/status"),
    export: (framework: string) => get<unknown>(`/compliance/export/${framework}`),
  },

  health: () => get<{ status: string }>("/healthz"),

  // Client-side aggregated stats (assembled from multiple endpoints)
  stats: async (): Promise<DashboardStats> => {
    const [assets, alerts, actions] = await Promise.allSettled([
      api.assets.list(),
      api.alerts.list(),
      api.actions.pending(),
    ]);

    const assetList = assets.status === "fulfilled" ? assets.value : [];
    const alertList = alerts.status === "fulfilled" ? alerts.value : [];
    const actionList = actions.status === "fulfilled" ? actions.value : [];

    return {
      total_assets: assetList.length,
      active_alerts: alertList.filter((a) => !a.acknowledged).length,
      critical_alerts: alertList.filter((a) => a.severity === "critical" && !a.acknowledged).length,
      pending_actions: actionList.length,
      decisions_today: 0,
      autonomous_mode: false,
    };
  },
};
