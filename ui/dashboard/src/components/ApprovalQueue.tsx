"use client";

import { useEffect, useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { api } from "@/lib/api";
import type { PendingAction } from "@/lib/types";
import { SeverityBadge } from "./SeverityBadge";
import { PurdueTag } from "./PurdueTag";

const ACTION_COLORS: Record<string, string> = {
  OBSERVE: "text-slate-400",
  ALERT: "text-yellow-400",
  ISOLATE_NETWORK: "text-orange-400",
  MODIFY_SETPOINT: "text-red-400",
  FIRMWARE_UPDATE: "text-red-500",
};

export function ApprovalQueue() {
  const [actions, setActions] = useState<PendingAction[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<string | null>(null);

  const load = () => {
    api.actions
      .pending()
      .then(setActions)
      .catch(() => setActions([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handle = async (actionId: string, approved: boolean) => {
    setProcessing(actionId);
    try {
      if (approved) {
        await api.actions.approve(actionId, "operator", "Approved via dashboard");
      } else {
        await api.actions.deny(actionId, "operator", "Denied via dashboard");
      }
      setActions((prev) => prev.filter((a) => a.action_id !== actionId));
    } catch {
      // toast error in real app
    } finally {
      setProcessing(null);
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-24 bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  }

  if (actions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-32 gap-2 text-slate-500 text-sm font-mono">
        <CheckCircle className="w-6 h-6 text-ot-green opacity-50" />
        No pending approvals
      </div>
    );
  }

  return (
    <div className="space-y-3 overflow-y-auto max-h-[500px] pr-1">
      {actions.map((action) => (
        <div
          key={action.action_id}
          className="rounded-lg border border-amber-800/50 bg-amber-900/10 p-4"
        >
          <div className="flex items-start justify-between gap-2 flex-wrap">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-ot-amber shrink-0" />
              <span
                className={`font-mono font-semibold text-sm ${ACTION_COLORS[action.action_class] ?? "text-white"}`}
              >
                {action.action_class}
              </span>
              {action.severity && <SeverityBadge severity={action.severity} />}
              {action.purdue_level != null && <PurdueTag level={action.purdue_level} />}
            </div>
            <span className="text-xs text-slate-500">
              {formatDistanceToNow(new Date(action.proposed_at), { addSuffix: true })}
            </span>
          </div>

          <p className="mt-2 text-sm text-slate-300">{action.reason}</p>

          {action.confidence != null && (
            <div className="mt-2 flex items-center gap-2">
              <span className="text-xs text-slate-500 font-mono">Confidence</span>
              <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-ot-blue rounded-full transition-all"
                  style={{ width: `${Math.round(action.confidence * 100)}%` }}
                />
              </div>
              <span className="text-xs text-slate-400 font-mono">
                {Math.round(action.confidence * 100)}%
              </span>
            </div>
          )}

          <div className="mt-3 flex gap-2">
            <button
              disabled={processing === action.action_id}
              onClick={() => handle(action.action_id, true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-green-900/40 border border-green-700 text-green-400 text-xs font-mono hover:bg-green-800/40 transition-colors disabled:opacity-50"
            >
              <CheckCircle className="w-3.5 h-3.5" />
              Approve
            </button>
            <button
              disabled={processing === action.action_id}
              onClick={() => handle(action.action_id, false)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-red-900/40 border border-red-700 text-red-400 text-xs font-mono hover:bg-red-800/40 transition-colors disabled:opacity-50"
            >
              <XCircle className="w-3.5 h-3.5" />
              Deny
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
