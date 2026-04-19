import { clsx } from "clsx";
import type { PurdueLevel } from "@/lib/types";

const LABELS: Record<PurdueLevel, string> = {
  0: "L0 Field",
  1: "L1 Control",
  2: "L2 Supervisory",
  3: "L3 Site Ops",
  4: "L3.5 DMZ",
  5: "L5 Enterprise",
};

const COLORS: Record<PurdueLevel, string> = {
  0: "border-red-500 text-red-400",
  1: "border-orange-500 text-orange-400",
  2: "border-yellow-500 text-yellow-400",
  3: "border-green-500 text-green-400",
  4: "border-blue-500 text-blue-400",
  5: "border-slate-500 text-slate-400",
};

export function PurdueTag({ level }: { level: PurdueLevel }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center px-2 py-0.5 rounded border text-xs font-mono",
        COLORS[level]
      )}
    >
      {LABELS[level]}
    </span>
  );
}
