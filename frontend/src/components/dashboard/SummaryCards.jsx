import { DASH } from "../../constants/testIds";

function Card({ testid, label, value, hint, accent }) {
  return (
    <div
      data-testid={testid}
      className="border border-zinc-800 bg-[#121212] p-5 rounded-sm hover:bg-[#161616] transition-colors"
    >
      <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-500">
        {label}
      </div>
      <div
        data-testid={`${testid}-value`}
        className={`font-heading text-3xl font-bold mt-2 font-mono-data ${
          accent || "text-zinc-50"
        }`}
      >
        {value}
      </div>
      {hint && (
        <div className="text-[11px] text-zinc-500 mt-1">{hint}</div>
      )}
    </div>
  );
}
export default function SummaryCards({ summary }) {
  const s = summary || {};
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card
        testid={DASH.card("universe")}
        label="NSE Universe"
        value={s.nse_universe ?? "—"}
        hint="symbols tracked"
      />
      <Card
        testid={DASH.card("price")}
        label="Price Qualified"
        value={s.price_qualified ?? "—"}
        hint="₹30 ≤ LTP ≤ ₹500"
        accent="text-sky-400"
      />
      <Card
        testid={DASH.card("liquidity")}
        label="Liquidity Qualified"
        value={s.liquidity_qualified ?? "—"}
        hint="Bid & Ask Qty > 10 lakh"
        accent="text-emerald-400"
      />
      <Card
        testid={DASH.card("signals")}
        label="Active Signals"
        value={s.active_signals ?? 0}
        hint={s.signals_status || "Pending (Phase 2)"}
        accent="text-zinc-500"
      />
    </div>
  );
}
