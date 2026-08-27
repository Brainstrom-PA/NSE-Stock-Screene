import { Activity, Radio } from "lucide-react";
import { DASH } from "../../constants/testIds";

export default function Header({ source, lastUpdated }) {
  const label = source?.label || "DEMO / SIMULATED";
  const ready = source?.ready ?? true;

  return (
    <header
      data-testid={DASH.header}
      className="border-b border-zinc-800 bg-[#0A0A0A]"
    >
      <div className="max-w-[1600px] mx-auto px-6 py-4 flex items-center justify-between gap-6">
        <div>
          <h1 className="font-heading text-2xl font-bold tracking-tight">
            AI MARKET SCREENING
          </h1>
          <p className="text-xs uppercase tracking-[0.18em] text-zinc-500 mt-1">
            NSE Stock Screening &amp; Quantitative Analysis
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <div
            data-testid={DASH.sourceBadge}
            className="flex items-center gap-2 border border-amber-500/40 bg-amber-500/10 text-amber-300 px-3 py-1.5 rounded-sm"
          >
            <Radio className="h-3 w-3" />
            <span className="font-medium uppercase tracking-wider">
              DATA SOURCE:&nbsp;{label}
            </span>
          </div>
          <div
            data-testid={DASH.statusBadge}
            className="flex items-center gap-2 border border-emerald-500/40 bg-emerald-500/10 text-emerald-300 px-3 py-1.5 rounded-sm"
          >
            <span
              className={`inline-block h-1.5 w-1.5 rounded-full ${
                ready ? "bg-emerald-400 animate-pulse" : "bg-zinc-500"
              }`}
            />
            <span className="font-medium uppercase tracking-wider">
              SYSTEM STATUS:&nbsp;{ready ? "RUNNING" : "IDLE"}
            </span>
          </div>
          <div className="hidden md:flex items-center gap-2 text-zinc-500">
            <Activity className="h-3 w-3" />
            <span className="font-mono-data">
              {lastUpdated
                ? lastUpdated.toLocaleTimeString([], { hour12: false })
                : "—"}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
