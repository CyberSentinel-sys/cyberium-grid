"use client";

import { useEffect, useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { api } from "@/lib/api";
import type { Alert } from "@/lib/types";
import { SeverityBadge } from "./SeverityBadge";

export function AlertsFeed({ limit = 20 }: { limit?: number }) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.alerts.list()
      .then((data) => setAlerts(data.slice(0, limit)))
      .catch(() => setAlerts([]))
      .finally(() => setLoading(false));
  }, [limit]);

  const handleAcknowledge = async (id: string) => {
    try {
      await api.alerts.acknowledge(id);
      setAlerts((prev) =>
        prev.map((a) => (a.alert_id === id ? { ...a, acknowledged: true } : a))
      );
    } catch {
      // UI will reflect stale state; real app would toast here
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-16 bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-slate-500 text-sm font-mono">
        No active alerts
      </div>
    );
  }

  return (
    <div className="space-y-2 overflow-y-auto max-h-[500px] pr-1">
      {alerts.map((alert) => (
        <div
          key={alert.alert_id}
          className={`rounded-lg border p-3 transition-opacity ${
            alert.acknowledged
              ? "border-slate-700 bg-slate-900/40 opacity-50"
              : "border-slate-700 bg-slate-800/60"
          }`}
        >
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2 flex-wrap">
              <SeverityBadge severity={alert.severity} />
              {alert.mitre_technique && (
                <span className="text-xs font-mono text-purple-400">
                  {alert.mitre_technique}
                </span>
              )}
              {alert.rule_id && (
                <span className="text-xs font-mono text-slate-500">{alert.rule_id}</span>
              )}
            </div>
            <span className="text-xs text-slate-500 whitespace-nowrap shrink-0">
              {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-300 line-clamp-2">{alert.description}</p>
          {!alert.acknowledged && (
            <button
              onClick={() => handleAcknowledge(alert.alert_id)}
              className="mt-2 text-xs text-ot-green hover:text-green-300 font-mono transition-colors"
            >
              Acknowledge →
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
