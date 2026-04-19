"use client";

import { useEffect, useState } from "react";
import { Cpu, Filter } from "lucide-react";
import { api } from "@/lib/api";
import type { Asset, PurdueLevel } from "@/lib/types";
import { SeverityBadge } from "@/components/SeverityBadge";
import { PurdueTag } from "@/components/PurdueTag";
import { AssetGraph } from "@/components/AssetGraph";

const PURDUE_LEVELS: Array<{ label: string; value: PurdueLevel | "" }> = [
  { label: "All Levels", value: "" },
  { label: "L0 Field", value: 0 },
  { label: "L1 Control", value: 1 },
  { label: "L2 Supervisory", value: 2 },
  { label: "L3 Site Ops", value: 3 },
  { label: "L3.5 DMZ", value: 4 },
  { label: "L5 Enterprise", value: 5 },
];

export default function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [filter, setFilter] = useState<PurdueLevel | "">("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.assets
      .list(filter === "" ? undefined : filter)
      .then(setAssets)
      .catch(() => setAssets([]))
      .finally(() => setLoading(false));
  }, [filter]);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-ot-green tracking-wide flex items-center gap-2">
          <Cpu className="w-5 h-5" />
          OT Asset Inventory
        </h1>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={String(filter)}
            onChange={(e) => {
              const v = e.target.value;
              setFilter(v === "" ? "" : (Number(v) as PurdueLevel));
            }}
            className="bg-slate-800 border border-slate-700 rounded px-3 py-1.5 text-xs font-mono text-slate-300 focus:outline-none focus:border-ot-blue"
          >
            {PURDUE_LEVELS.map(({ label, value }) => (
              <option key={label} value={String(value)}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Topology map */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
        <h2 className="text-sm font-semibold text-slate-400 mb-3">Network Topology</h2>
        <AssetGraph />
      </div>

      {/* Asset table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 overflow-hidden">
        <table className="w-full text-xs font-mono">
          <thead>
            <tr className="border-b border-slate-800 text-slate-500">
              <th className="px-4 py-3 text-left">IP Address</th>
              <th className="px-4 py-3 text-left">Hostname</th>
              <th className="px-4 py-3 text-left">Vendor / Model</th>
              <th className="px-4 py-3 text-left">Purdue Level</th>
              <th className="px-4 py-3 text-left">Protocols</th>
              <th className="px-4 py-3 text-left">Criticality</th>
              <th className="px-4 py-3 text-left">Site</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                  Loading assets…
                </td>
              </tr>
            ) : assets.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                  No assets discovered yet. Start the DPI sensor to begin passive fingerprinting.
                </td>
              </tr>
            ) : (
              assets.map((asset) => (
                <tr
                  key={asset.asset_id}
                  className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
                >
                  <td className="px-4 py-3 text-ot-green">{asset.ip_address}</td>
                  <td className="px-4 py-3 text-slate-300">{asset.hostname ?? "—"}</td>
                  <td className="px-4 py-3 text-slate-400">
                    {[asset.vendor, asset.model].filter(Boolean).join(" / ") || "—"}
                  </td>
                  <td className="px-4 py-3">
                    <PurdueTag level={asset.purdue_level} />
                  </td>
                  <td className="px-4 py-3 text-slate-400">
                    {asset.protocols.length ? asset.protocols.join(", ") : "—"}
                  </td>
                  <td className="px-4 py-3">
                    <SeverityBadge severity={asset.criticality} />
                  </td>
                  <td className="px-4 py-3 text-slate-500">{asset.site_id}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
