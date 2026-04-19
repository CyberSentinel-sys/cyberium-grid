"use client";

import { useEffect, useState } from "react";
import { FileCheck, Download, CheckCircle, Circle } from "lucide-react";
import { api } from "@/lib/api";
import type { ComplianceStatus } from "@/lib/types";

const FRAMEWORKS = [
  {
    key: "nerc_cip_015" as const,
    name: "NERC CIP-015",
    description: "Internal Network Security Monitoring for high/medium BES Cyber Systems",
    color: "text-ot-blue border-ot-blue/30",
    controls: [
      { id: "CIP-015-1 R1", label: "Network monitoring plan documented", done: true },
      { id: "CIP-015-1 R2", label: "Traffic logging for high/medium BCS", done: true },
      { id: "CIP-015-1 R3", label: "Log retention ≥90 days", done: true },
      { id: "CIP-015-1 R4", label: "Anomaly alerting", done: true },
      { id: "CIP-015-1 R5", label: "Evidence of review", done: false },
    ],
  },
  {
    key: "iec_62443" as const,
    name: "IEC 62443-3-3",
    description: "System security requirements and security levels for industrial automation",
    color: "text-purple-400 border-purple-400/30",
    controls: [
      { id: "SR 1.1", label: "Human user identification & authentication", done: true },
      { id: "SR 2.8", label: "Auditable events", done: true },
      { id: "SR 3.1", label: "Communication integrity", done: true },
      { id: "SR 3.3", label: "Security functionality verification", done: true },
      { id: "SR 5.2", label: "Zone boundary protection", done: true },
      { id: "SR 6.1", label: "Audit log accessibility", done: true },
      { id: "SR 7.3", label: "Control system backup", done: false },
    ],
  },
  {
    key: "nis2" as const,
    name: "NIS2 Article 21",
    description: "EU Network and Information Security Directive 2 — OT/ICS obligations",
    color: "text-ot-green border-ot-green/30",
    controls: [
      { id: "Art. 21(2)(a)", label: "Risk analysis and information security policies", done: true },
      { id: "Art. 21(2)(b)", label: "Incident handling", done: true },
      { id: "Art. 21(2)(c)", label: "Business continuity and crisis management", done: false },
      { id: "Art. 21(2)(d)", label: "Supply chain security", done: false },
      { id: "Art. 21(2)(e)", label: "Security in network and information systems", done: true },
      { id: "Art. 21(2)(f)", label: "Policies for use of cryptography", done: true },
      { id: "Art. 21(2)(g)", label: "Human resources security", done: false },
    ],
  },
];

export default function CompliancePage() {
  const [status, setStatus] = useState<ComplianceStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.compliance
      .status()
      .then(setStatus)
      .catch(() => setStatus(null))
      .finally(() => setLoading(false));
  }, []);

  const handleExport = async (framework: string) => {
    try {
      const data = await api.compliance.export(framework);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `orhashield-compliance-${framework}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // toast error in real app
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-ot-green tracking-wide flex items-center gap-2">
          <FileCheck className="w-5 h-5" />
          Compliance Coverage
        </h1>
        {status && (
          <span className="text-xs font-mono text-slate-500">
            Phase {status.phase} · Last updated{" "}
            {new Date(status.last_updated).toLocaleDateString()}
          </span>
        )}
      </div>

      {/* Coverage summary */}
      {!loading && status && (
        <div className="grid grid-cols-3 gap-4">
          {FRAMEWORKS.map(({ key, name, color }) => (
            <div
              key={key}
              className={`rounded-xl border bg-slate-900/40 p-4 ${color}`}
            >
              <div className="text-2xl font-bold font-mono">{status[key]}%</div>
              <div className="text-xs mt-1 text-slate-400">{name}</div>
              <div className="mt-2 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${status[key]}%`,
                    background: "currentColor",
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Per-framework control lists */}
      <div className="space-y-4">
        {FRAMEWORKS.map(({ key, name, description, color, controls }) => (
          <div
            key={key}
            className={`rounded-xl border bg-slate-900/40 p-4 ${color}`}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h2 className="text-sm font-semibold">{name}</h2>
                <p className="text-xs text-slate-500 mt-0.5">{description}</p>
              </div>
              <button
                onClick={() => handleExport(key)}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded border border-current text-xs font-mono hover:bg-current/10 transition-colors"
              >
                <Download className="w-3 h-3" />
                Export
              </button>
            </div>

            <div className="space-y-1.5">
              {controls.map(({ id, label, done }) => (
                <div key={id} className="flex items-center gap-2 text-xs font-mono">
                  {done ? (
                    <CheckCircle className="w-3.5 h-3.5 text-ot-green shrink-0" />
                  ) : (
                    <Circle className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                  )}
                  <span className={done ? "text-slate-300" : "text-slate-600"}>
                    <span className="text-slate-500 mr-2">{id}</span>
                    {label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
