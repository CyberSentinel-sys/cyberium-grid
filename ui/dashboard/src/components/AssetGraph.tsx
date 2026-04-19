"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { api } from "@/lib/api";
import type { Asset, PurdueLevel } from "@/lib/types";

// Purdue level Y-positions (normalized 0-1)
const LEVEL_Y: Record<PurdueLevel, number> = {
  0: 0.9,
  1: 0.74,
  2: 0.58,
  3: 0.42,
  4: 0.26,
  5: 0.1,
};

const LEVEL_COLORS: Record<PurdueLevel, string> = {
  0: "#ff3b3b",
  1: "#ff8c00",
  2: "#ffb020",
  3: "#00ff88",
  4: "#0ea5e9",
  5: "#a855f7",
};

const CRITICALITY_RADIUS: Record<string, number> = {
  critical: 10,
  high: 8,
  medium: 6,
  low: 5,
  info: 4,
};

interface Node {
  id: string;
  x: number;
  y: number;
  color: string;
  r: number;
  asset: Asset;
}

export function AssetGraph() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [hovered, setHovered] = useState<Node | null>(null);
  const nodesRef = useRef<Node[]>([]);

  useEffect(() => {
    api.assets.list().then(setAssets).catch(() => setAssets([]));
  }, []);

  const buildNodes = useCallback((width: number, height: number): Node[] => {
    const byLevel: Record<number, Asset[]> = {};
    assets.forEach((a) => {
      byLevel[a.purdue_level] = byLevel[a.purdue_level] ?? [];
      byLevel[a.purdue_level].push(a);
    });

    return assets.map((a) => {
      const levelAssets = byLevel[a.purdue_level];
      const idx = levelAssets.indexOf(a);
      const total = levelAssets.length;
      const xFrac = total === 1 ? 0.5 : 0.1 + (0.8 * idx) / (total - 1);
      return {
        id: a.asset_id,
        x: xFrac * width,
        y: LEVEL_Y[a.purdue_level as PurdueLevel] * height,
        color: LEVEL_COLORS[a.purdue_level as PurdueLevel],
        r: CRITICALITY_RADIUS[a.criticality] ?? 6,
        asset: a,
      };
    });
  }, [assets]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const { width, height } = canvas;
    const nodes = buildNodes(width, height);
    nodesRef.current = nodes;

    ctx.clearRect(0, 0, width, height);

    // Draw Purdue zone labels
    const levels: Array<[PurdueLevel, string]> = [
      [0, "Level 0 — Field"], [1, "Level 1 — Control"],
      [2, "Level 2 — Supervisory"], [3, "Level 3 — Site Ops"],
      [4, "Level 3.5 — DMZ"], [5, "Level 5 — Enterprise"],
    ];
    levels.forEach(([lvl, label]) => {
      const y = LEVEL_Y[lvl] * height;
      ctx.strokeStyle = LEVEL_COLORS[lvl] + "22";
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = LEVEL_COLORS[lvl] + "88";
      ctx.font = "10px monospace";
      ctx.fillText(label, 6, y - 4);
    });

    // Draw nodes
    nodes.forEach((n) => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fillStyle = n.color + "cc";
      ctx.fill();
      ctx.strokeStyle = n.color;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      ctx.fillStyle = "#e2e8f0";
      ctx.font = "9px monospace";
      ctx.textAlign = "center";
      ctx.fillText(
        n.asset.hostname ?? n.asset.ip_address,
        n.x,
        n.y + n.r + 11
      );
      ctx.textAlign = "left";
    });
  }, [assets, buildNodes]);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const hit = nodesRef.current.find((n) => {
      const dx = n.x - mx;
      const dy = n.y - my;
      return Math.sqrt(dx * dx + dy * dy) <= n.r + 4;
    });
    setHovered(hit ?? null);
  }, []);

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        width={700}
        height={400}
        className="w-full rounded-lg bg-slate-900/80 border border-slate-700 cursor-crosshair"
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setHovered(null)}
      />
      {hovered && (
        <div className="absolute top-2 right-2 bg-slate-800 border border-slate-600 rounded-lg p-3 text-xs font-mono space-y-1 min-w-48 z-10">
          <div className="text-ot-green font-semibold">
            {hovered.asset.hostname ?? hovered.asset.ip_address}
          </div>
          <div className="text-slate-400">IP: {hovered.asset.ip_address}</div>
          {hovered.asset.vendor && (
            <div className="text-slate-400">Vendor: {hovered.asset.vendor}</div>
          )}
          <div className="text-slate-400">
            Protocols: {hovered.asset.protocols.join(", ") || "unknown"}
          </div>
          <div className="text-slate-400">
            Criticality:{" "}
            <span className="text-ot-amber">{hovered.asset.criticality}</span>
          </div>
        </div>
      )}
      {assets.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center text-slate-500 text-sm font-mono">
          No assets discovered yet
        </div>
      )}
    </div>
  );
}
