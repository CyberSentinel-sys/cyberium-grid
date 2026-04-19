"use client";

import { useEffect, useState } from "react";
import { Activity, Brain, CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { ApprovalQueue } from "@/components/ApprovalQueue";
import { SeverityBadge } from "@/components/SeverityBadge";
import { PurdueTag } from "@/components/PurdueTag";
import { useWebSocket } from "@/hooks/useWebSocket";
import type { RealtimeEvent } from "@/lib/types";

const DECISION_ICON = {
  allow: <CheckCircle className="w-4 h-4 text-ot-green" />,
  deny: <XCircle className="w-4 h-4 text-ot-red" />,
  escalate: <AlertTriangle className="w-4 h-4 text-ot-amber" />,
};

const DECISION_COLOR = {
  allow: "text-ot-green",
  deny: "text-ot-red",
  escalate: "text-ot-amber",
};

interface ActivityItem {
  id: string;
  type: string;
  payload: Record<string, unknown>;
  timestamp: string;
}

export default function AgentActivityPage() {
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const { lastEvent, status } = useWebSocket();

  useEffect(() => {
    if (!lastEvent || lastEvent.type === "heartbeat") return;
    setActivities((prev) => [
      {
        id: `${Date.now()}-${Math.random()}`,
        type: lastEvent.type,
        payload: lastEvent.payload as Record<string, unknown>,
        timestamp: lastEvent.timestamp,
      },
      ...prev.slice(0, 99), // keep last 100
    ]);
  }, [lastEvent]);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-ot-green tracking-wide flex items-center gap-2">
          <Activity className="w-5 h-5" />
          Agent Activity
        </h1>
        <div className="flex items-center gap-2 text-xs font-mono text-slate-500">
          <Brain className="w-4 h-4 text-ot-purple" />
          LangGraph Blue-Team AI ·{" "}
          <span className={status === "connected" ? "text-ot-green" : "text-ot-red"}>
            {status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Live event stream */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
          <h2 className="text-sm font-semibold text-slate-300 mb-3">
            Live Decision Stream
          </h2>

          {activities.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 gap-2 text-slate-500 text-sm font-mono">
              <Brain className="w-8 h-8 opacity-30" />
              Waiting for agent events…
              <span className="text-xs">
                {status === "connected" ? "WebSocket connected" : "Reconnecting…"}
              </span>
            </div>
          ) : (
            <div className="space-y-2 overflow-y-auto max-h-[500px]">
              {activities.map((item) => (
                <div
                  key={item.id}
                  className="rounded-lg border border-slate-700 bg-slate-800/50 p-3 text-xs font-mono"
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      {item.type === "decision" && item.payload.decision
                        ? DECISION_ICON[item.payload.decision as keyof typeof DECISION_ICON]
                        : <Activity className="w-4 h-4 text-ot-blue" />
                      }
                      <span className="text-slate-400 uppercase tracking-wide text-[10px]">
                        {item.type}
                      </span>
                      {item.type === "decision" && item.payload.decision && (
                        <span className={DECISION_COLOR[item.payload.decision as keyof typeof DECISION_COLOR]}>
                          {item.payload.decision as string}
                        </span>
                      )}
                    </div>
                    <span className="text-slate-600">
                      {formatDistanceToNow(new Date(item.timestamp), { addSuffix: true })}
                    </span>
                  </div>

                  {item.payload.action_class && (
                    <div className="text-slate-300">
                      Action:{" "}
                      <span className="text-ot-amber">
                        {item.payload.action_class as string}
                      </span>
                    </div>
                  )}
                  {item.payload.reason && (
                    <div className="text-slate-400 mt-1 line-clamp-2">
                      {item.payload.reason as string}
                    </div>
                  )}
                  {item.payload.confidence != null && (
                    <div className="text-slate-500 mt-1">
                      Confidence: {Math.round((item.payload.confidence as number) * 100)}%
                      {item.payload.model_used && ` · ${item.payload.model_used as string}`}
                    </div>
                  )}
                  {item.payload.purdue_level != null && (
                    <div className="mt-1">
                      <PurdueTag level={item.payload.purdue_level as 0} />
                    </div>
                  )}
                  {item.payload.severity && (
                    <div className="mt-1">
                      <SeverityBadge severity={item.payload.severity as "info"} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pending approvals */}
        <div className="rounded-xl border border-amber-900/40 bg-slate-900/40 p-4">
          <h2 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-ot-amber" />
            Human Approval Queue
          </h2>
          <ApprovalQueue />
        </div>
      </div>

      {/* Pipeline diagram */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
        <h2 className="text-sm font-semibold text-slate-300 mb-4">
          LangGraph Pipeline Topology
        </h2>
        <div className="font-mono text-xs text-slate-400 overflow-x-auto">
          <pre className="text-center leading-7">
{`NATS ot.events.>
       │
       ▼
  ┌─────────────┐
  │  Supervisor │◄────────────────────────────────────────┐
  └──────┬──────┘                                         │
         │ route                                          │
    ┌────▼────────────────────────────────────────┐      │
    │                                             │      │
    ▼              ▼              ▼               ▼      │
ThreatIntel  ProtocolExpert  TwinVerifier  ResponsePlanner│
    │              │              │               │      │
    └──────────────┴──────────────┴───────────────┘      │
                          │                              │
                     ┌────▼────┐    ┌────────┐           │
                     │HumanGate│    │ Critic │───────────┘
                     │(PAUSE)  │    └────────┘   feedback loop
                     └────┬────┘
                          │ resume via graph.update_state()
                     NATS ot.actions.approved/denied`}
          </pre>
        </div>
      </div>
    </div>
  );
}
