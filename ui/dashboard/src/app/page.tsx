"use client";

import { useEffect, useState } from "react";
import { Cpu, Bell, ShieldAlert, Clock, Activity } from "lucide-react";
import { StatCard } from "@/components/StatCard";
import { AlertsFeed } from "@/components/AlertsFeed";
import { ApprovalQueue } from "@/components/ApprovalQueue";
import { ComplianceDashboard } from "@/components/ComplianceDashboard";
import { AssetGraph } from "@/components/AssetGraph";
import { api } from "@/lib/api";
import type { DashboardStats } from "@/lib/types";

export default function OverviewPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    api.stats().then(setStats).catch(() => null);
    const interval = setInterval(() => {
      api.stats().then(setStats).catch(() => null);
    }, 30_000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-ot-green tracking-wide">
            Security Operations Center
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            AI-native OT/ICS protection · Purdue Model aware · Human-in-the-loop
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono px-3 py-1.5 rounded-full border border-red-800 bg-red-900/20 text-red-400">
          <span className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse" />
          AUTONOMOUS MODE: DISABLED
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Assets"
          value={stats?.total_assets ?? "—"}
          icon={Cpu}
          accent="blue"
        />
        <StatCard
          label="Active Alerts"
          value={stats?.active_alerts ?? "—"}
          icon={Bell}
          accent="amber"
          pulse={(stats?.active_alerts ?? 0) > 0}
        />
        <StatCard
          label="Critical Alerts"
          value={stats?.critical_alerts ?? "—"}
          icon={ShieldAlert}
          accent="red"
          pulse={(stats?.critical_alerts ?? 0) > 0}
        />
        <StatCard
          label="Pending Approvals"
          value={stats?.pending_actions ?? "—"}
          icon={Clock}
          accent="amber"
          pulse={(stats?.pending_actions ?? 0) > 0}
        />
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Asset topology */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/40 p-4">
          <h2 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <Activity className="w-4 h-4 text-ot-blue" />
            OT Asset Topology (Purdue Model)
          </h2>
          <AssetGraph />
        </div>

        {/* Compliance */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
          <h2 className="text-sm font-semibold text-slate-300 mb-3">
            Compliance Coverage
          </h2>
          <ComplianceDashboard />
        </div>
      </div>

      {/* Alerts + Approval Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
          <h2 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <Bell className="w-4 h-4 text-ot-amber" />
            Live Alerts Feed
          </h2>
          <AlertsFeed limit={10} />
        </div>

        <div className="rounded-xl border border-amber-900/40 bg-slate-900/40 p-4">
          <h2 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <Clock className="w-4 h-4 text-ot-amber" />
            Pending Human Approvals
          </h2>
          <ApprovalQueue />
        </div>
      </div>
    </div>
  );
}
