import { clsx } from "clsx";

type Color = "green" | "amber" | "red" | "gray";

const DOT: Record<Color, string> = {
  green: "bg-ot-green",
  amber: "bg-ot-amber",
  red: "bg-ot-red",
  gray: "bg-slate-500",
};

export function StatusDot({ color, pulse = false }: { color: Color; pulse?: boolean }) {
  return (
    <span className="relative flex h-2.5 w-2.5">
      {pulse && (
        <span
          className={clsx(
            "animate-ping-slow absolute inline-flex h-full w-full rounded-full opacity-75",
            DOT[color]
          )}
        />
      )}
      <span className={clsx("relative inline-flex rounded-full h-2.5 w-2.5", DOT[color])} />
    </span>
  );
}
