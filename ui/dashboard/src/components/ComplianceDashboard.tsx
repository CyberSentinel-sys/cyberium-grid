"use client";

import { useEffect, useState } from "react";
import { RadialBarChart, RadialBar, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "@/lib/api";
import type { ComplianceStatus } from "@/lib/types";

const FRAMEWORKS = [
  { key: "nerc_cip_015" as const, label: "NERC CIP-015", color: "#0ea5e9" },
  { key: "iec_62443" as const, label: "IEC 62443-3-3", color: "#a855f7" },
  { key: "nis2" as const, label: "NIS2 Art.21", color: "#00ff88" },
];

function GaugeBar({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  const data = [{ value, fill: color }];
  return (
    <div className="flex flex-col items-center gap-1">
      <ResponsiveContainer width={100} height={100}>
        <RadialBarChart
          cx="50%"
          cy="50%"
          innerRadius={30}
          outerRadius={45}
          startAngle={90}
          endAngle={-270}
          data={data}
        >
          <RadialBar dataKey="value" background={{ fill: "#1e293b" }} cornerRadius={4} />
          <Tooltip
            content={() => null}
          />
        </RadialBarChart>
      </ResponsiveContainer>
      <span className="text-lg font-bold font-mono" style={{ color }}>
        {value}%
      </span>
      <span className="text-xs text-slate-400 text-center">{label}</span>
    </div>
  );
}

export function ComplianceDashboard() {
  const [status, setStatus] = useState<ComplianceStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.compliance
      .status()
      .then(setStatus)
      .catch(() => setStatus(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse flex gap-6 justify-center">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-28 w-24 bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  }

  if (!status) {
    return (
      <div className="text-center text-slate-500 text-sm font-mono py-8">
        Compliance data unavailable
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-center gap-8 flex-wrap">
        {FRAMEWORKS.map(({ key, label, color }) => (
          <GaugeBar key={key} label={label} value={status[key]} color={color} />
        ))}
      </div>
      <div className="flex items-center justify-between text-xs font-mono text-slate-500 border-t border-slate-800 pt-3">
        <span>Phase {status.phase} coverage</span>
        <a
          href="/compliance"
          className="text-ot-blue hover:text-sky-300 transition-colors"
        >
          Full report →
        </a>
      </div>
    </div>
  );
}
