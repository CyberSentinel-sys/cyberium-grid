import { clsx } from "clsx";
import type { LucideIcon } from "lucide-react";

interface Props {
  label: string;
  value: number | string;
  icon: LucideIcon;
  accent?: "green" | "amber" | "red" | "blue";
  pulse?: boolean;
}

const ACCENT: Record<string, string> = {
  green: "text-ot-green border-ot-green/20",
  amber: "text-ot-amber border-ot-amber/20",
  red: "text-ot-red border-ot-red/20",
  blue: "text-ot-blue border-ot-blue/20",
};

export function StatCard({ label, value, icon: Icon, accent = "blue", pulse = false }: Props) {
  return (
    <div className={clsx("rounded-xl border bg-slate-900/60 p-4 flex flex-col gap-3", ACCENT[accent])}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono text-slate-400 uppercase tracking-wide">{label}</span>
        <Icon className={clsx("w-4 h-4", ACCENT[accent].split(" ")[0])} />
      </div>
      <div className={clsx("text-3xl font-bold font-mono", ACCENT[accent].split(" ")[0], pulse && "animate-pulse-slow")}>
        {value}
      </div>
    </div>
  );
}
