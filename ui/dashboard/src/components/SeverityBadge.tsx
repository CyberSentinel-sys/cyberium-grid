import { clsx } from "clsx";
import type { Severity } from "@/lib/types";

const COLORS: Record<Severity, string> = {
  info: "bg-slate-700 text-slate-300",
  low: "bg-blue-900/60 text-blue-300",
  medium: "bg-yellow-900/60 text-yellow-300",
  high: "bg-orange-900/60 text-orange-300",
  critical: "bg-red-900/60 text-red-400 animate-pulse-slow",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-semibold uppercase tracking-wide",
        COLORS[severity]
      )}
    >
      {severity}
    </span>
  );
}
