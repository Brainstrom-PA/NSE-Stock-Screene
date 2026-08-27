import { useMemo, useState } from "react";
import Header from "../components/dashboard/Header";
import SummaryCards from "../components/dashboard/SummaryCards";
import StockTable from "../components/dashboard/StockTable";
import DetailPanel from "../components/dashboard/DetailPanel";
import { useMarketData } from "../hooks/useMarketData";

export default function Dashboard() {
  const { snapshot, summary, source, error, lastUpdated } = useMarketData(2000);
  const [selected, setSelected] = useState(null);

  const selectedStock = useMemo(
    () => snapshot.find((s) => s.tick.symbol === selected) || null,
    [snapshot, selected]
  );

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-zinc-100">
      <Header source={source} lastUpdated={lastUpdated} />

      {error && (
        <div className="max-w-[1600px] mx-auto px-6 mt-4">
          <div className="border border-red-500/40 bg-red-500/10 text-red-300 text-xs px-4 py-2 rounded-sm">
            Backend unreachable: {error}
          </div>
        </div>
      )}

      <div className="max-w-[1600px] mx-auto px-6 py-6 space-y-6">
        <SummaryCards summary={summary} />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-9">
            <StockTable
              rows={snapshot}
              onSelect={setSelected}
              selected={selected}
            />
          </div>
          <div className="lg:col-span-3">
            <DetailPanel stock={selectedStock} />
          </div>
        </div>

        <footer className="text-[11px] text-zinc-600 text-center py-6 border-t border-zinc-900">
          <p className="uppercase tracking-widest">
            AI Market Screening · Phase 1 · Demo Data
          </p>
          <p className="mt-1 italic">
            Simulated market data — not connected to any live broker or exchange.
          </p>
        </footer>
      </div>
    </div>
  );
}
