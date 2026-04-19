"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import { Shield, Cpu, Bell, Activity, FileCheck } from "lucide-react";
import { StatusDot } from "./StatusDot";
import { useWebSocket } from "@/hooks/useWebSocket";

const NAV = [
  { href: "/", label: "Overview", icon: Cpu },
  { href: "/assets", label: "Assets", icon: Shield },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/agent-activity", label: "Agent Activity", icon: Activity },
  { href: "/compliance", label: "Compliance", icon: FileCheck },
];

export function Navbar() {
  const pathname = usePathname();
  const { status } = useWebSocket();

  const dotColor =
    status === "connected" ? "green" : status === "connecting" ? "amber" : "red";

  return (
    <nav className="flex items-center justify-between px-6 py-3 border-b border-slate-800 bg-slate-950">
      <div className="flex items-center gap-3">
        <Shield className="w-6 h-6 text-ot-green" />
        <span className="font-mono font-bold text-ot-green tracking-wider text-sm">
          OrHaShield
        </span>
        <span className="text-slate-600 text-xs font-mono">SCADA Security Platform</span>
      </div>

      <div className="flex items-center gap-1">
        {NAV.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={clsx(
              "flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono transition-colors",
              pathname === href
                ? "bg-slate-800 text-ot-green"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            )}
          >
            <Icon className="w-3.5 h-3.5" />
            {label}
          </Link>
        ))}
      </div>

      <div className="flex items-center gap-2 text-xs font-mono text-slate-500">
        <StatusDot color={dotColor} pulse={status === "connected"} />
        <span>{status}</span>
      </div>
    </nav>
  );
}
