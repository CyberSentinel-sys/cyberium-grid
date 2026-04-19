"use client";

import { useEffect, useState } from "react";
import { Bell, RefreshCw } from "lucide-react";
import { formatDistanceToNow, format } from "date-fns";
import { api } from "@/lib/api";
import type { Alert, Severity } from "@/lib/types";
import { SeverityBadge } from "@/components/SeverityBadge";
import { useWebSocket } from "@/hooks/useWebSocket";

const SEVERITIES: Array<Severity | "all"> = ["all", "critical", "high", "medium", "low", "info"];

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<Severity | "all">("all");
  const [showAcked, setShowAcked] = useState(false);
  const { lastEvent } = useWebSocket();

  const load = () => {
    setLoading(true);
    api.alerts
      .list()
      .then(setAlerts)
      .catch(() => setAlerts([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  // Refresh when we receive a real-time alert event
  useEffect(() => {
    if (lastEvent?.type === "alert") load();
  }, [lastEvent]);

  const handleAcknowledge = async (id: string) => {
    await api.alerts.acknowledge(id);
    setAlerts((prev) =>
      prev.map((a) => (a.alert_id === id ? { ...a, acknowledged: true } : a))
    );
  };

  const visible = alerts
    .filter((a) => filter === "all" || a.severity === filter)
    .filter((a) => showAcked || !a.acknowledged);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <h1 className="text-xl font-bold text-ot-green tracking-wide flex items-center gap-2">
          <Bell className="w-5 h-5" />
          Alerts
          {!loading && (
            <span className="text-xs font-normal text-slate-500 ml-1">
              ({visible.length} shown)
            </span>
          )}
        </h1>

        <div className="flex items-center gap-3 flex-wrap">
          {/* Severity filter pills */}
          <div className="flex gap-1">
            {SEVERITIES.map((s) => (
              <button
                key={s}
                onClick={() => setFilter(s)}
                className={`px-2.5 py-1 rounded text-xs font-mono transition-colors ${
                  filter === s
                    ? "bg-slate-700 text-slate-100"
                    : "text-slate-500 hover:text-slate-300"
                }`}
              >
                {s}
              </button>
            ))}
          </div>

          <label className="flex items-center gap-1.5 text-xs font-mono text-slate-400 cursor-pointer">
            <input
              type="checkbox"
              checked={showAcked}
              onChange={(e) => setShowAcked(e.target.checked)}
              className="rounded"
            />
            Show acknowledged
          </label>

          <button
            onClick={load}
            className="flex items-center gap-1 px-2.5 py-1 rounded border border-slate-700 text-slate-400 text-xs hover:text-slate-200 transition-colors"
          >
            <RefreshCw className="w-3 h-3" />
            Refresh
          </button>
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/40 overflow-hidden">
        <table className="w-full text-xs font-mono">
          <thead>
            <tr className="border-b border-slate-800 text-slate-500">
              <th className="px-4 py-3 text-left">Severity</th>
              <th className="px-4 py-3 text-left">MITRE</th>
              <th className="px-4 py-3 text-left">Rule</th>
              <th className="px-4 py-3 text-left w-1/2">Description</th>
              <th className="px-4 py-3 text-left">Created</th>
              <th className="px-4 py-3 text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                  Loading…
                </td>
              </tr>
            ) : visible.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                  No alerts match the current filter
                </td>
              </tr>
            ) : (
              visible.map((alert) => (
                <tr
                  key={alert.alert_id}
                  className={`border-b border-slate-800/50 transition-colors ${
                    alert.acknowledged ? "opacity-50" : "hover:bg-slate-800/30"
                  }`}
                >
                  <td className="px-4 py-3">
                    <SeverityBadge severity={alert.severity} />
                  </td>
                  <td className="px-4 py-3 text-purple-400">
                    {alert.mitre_technique ?? "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-500">{alert.rule_id ?? "—"}</td>
                  <td className="px-4 py-3 text-slate-300 max-w-sm truncate">
                    {alert.description}
                  </td>
                  <td
                    className="px-4 py-3 text-slate-500"
                    title={format(new Date(alert.created_at), "PPpp")}
                  >
                    {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                  </td>
                  <td className="px-4 py-3">
                    {alert.acknowledged ? (
                      <span className="text-slate-600">Acknowledged</span>
                    ) : (
                      <button
                        onClick={() => handleAcknowledge(alert.alert_id)}
                        className="text-ot-green hover:text-green-300 transition-colors"
                      >
                        Acknowledge
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
