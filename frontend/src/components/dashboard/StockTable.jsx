import { useEffect, useRef, useState } from "react";
import { DASH } from "../../constants/testIds";

const fmtPrice = (v) => (v == null ? "—" : `₹${Number(v).toFixed(2)}`);
const fmtQty = (v) => (v == null ? "—" : Number(v).toLocaleString("en-IN"));

/** cell that flashes green/red when its number changes */
function TickCell({ value, format = fmtPrice, className = "" }) {
  const [flash, setFlash] = useState("");
  const prev = useRef(value);
  useEffect(() => {
    if (prev.current != null && value != null && value !== prev.current) {
      setFlash(value > prev.current ? "tick-up" : "tick-down");
      const t = setTimeout(() => setFlash(""), 500);
      prev.current = value;
      return () => clearTimeout(t);
    }
    prev.current = value;
  }, [value]);
  return (
    <td className={`px-3 py-2 text-right font-mono-data ${flash} ${className}`}>
      {format(value)}
    </td>
  );
}

function ScreenBadge({ symbol, priceOk, liqOk, qualified }) {
  const cls = qualified
    ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300"
    : "border-zinc-700 bg-zinc-800/40 text-zinc-500";
  return (
    <span
      data-testid={DASH.screenBadge(symbol)}
      className={`inline-flex items-center px-2 py-0.5 rounded-sm border text-[10px] tracking-wider font-medium ${cls}`}
    >
      <ScreenBadgeText priceOk={priceOk} liqOk={liqOk} qualified={qualified} />
    </span>
  );
}

const Muted = () => <span className="text-zinc-600">—</span>;
const Pending = () => <span className="text-zinc-600 italic">Pending</span>;

// --- Small, single-purpose cell components (extracted to keep row logic flat) ---

function ScreenBadgeText({ priceOk, liqOk, qualified }) {
  if (qualified) return "PASS";
  if (!priceOk && !liqOk) return "FAIL";
  if (!priceOk) return "PRICE";
  return "LIQUIDITY";
}

function SignalPill({ signal, lastSignal }) {
  if (signal === "BUY")
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-sm border border-emerald-500/60 bg-emerald-500/20 text-emerald-300 text-[10px] font-semibold tracking-wider">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        BUY
      </span>
    );
  if (signal === "SELL")
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-sm border border-red-500/60 bg-red-500/20 text-red-300 text-[10px] font-semibold tracking-wider">
        <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
        SELL
      </span>
    );
  if (lastSignal === "BUY")
    return <span className="text-emerald-500/60 text-[10px] tracking-wider">BUY</span>;
  if (lastSignal === "SELL")
    return <span className="text-red-500/60 text-[10px] tracking-wider">SELL</span>;
  return <Muted />;
}

function AiProbabilityCell({ probability, hasSignal }) {
  if (probability != null) {
    const cls = probability >= 0.6 ? "text-emerald-300" : "text-amber-300";
    return <span className={cls}>{(probability * 100).toFixed(0)}%</span>;
  }
  if (hasSignal) {
    return <span className="text-zinc-600 text-[10px] italic">Insufficient</span>;
  }
  return <Muted />;
}

function DecisionCell({ decision, hasSignal }) {
  if (decision === "ACCEPT")
    return (
      <span className="inline-flex px-2 py-0.5 rounded-sm border border-emerald-500/60 bg-emerald-500/15 text-emerald-300 text-[10px] font-semibold tracking-wider">
        ACCEPT
      </span>
    );
  if (decision === "AVOID")
    return (
      <span className="inline-flex px-2 py-0.5 rounded-sm border border-red-500/60 bg-red-500/15 text-red-300 text-[10px] font-semibold tracking-wider">
        AVOID
      </span>
    );
  if (hasSignal)
    return <span className="text-zinc-600 text-[10px] italic">Pending ML</span>;
  return <Muted />;
}

export default function StockTable({ rows, onSelect, selected }) {
  return (
    <div
      data-testid={DASH.table}
      className="border border-zinc-800 bg-[#121212] rounded-sm overflow-hidden"
    >
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
        <div>
          <h2 className="font-heading text-sm font-bold tracking-wider uppercase">
            NSE Universe
          </h2>
          <p className="text-[11px] text-zinc-500 mt-0.5">
            Live-screened market snapshot · refresh every 2s
          </p>
        </div>
        <div className="text-[10px] uppercase tracking-widest text-zinc-500">
          {rows.length} symbols
        </div>
      </div>

      <div className="overflow-x-auto max-h-[70vh]">
        <table className="w-full text-xs">
          <thead className="sticky top-0 bg-[#0F0F0F] text-[10px] uppercase tracking-wider text-zinc-500 border-b border-zinc-800">
            <tr>
              <th className="text-left px-3 py-2 font-medium">Symbol</th>
              <th className="text-left px-3 py-2 font-medium">Screen</th>
              <th className="text-right px-3 py-2 font-medium">LTP</th>
              <th className="text-right px-3 py-2 font-medium border-l border-zinc-800">SMMA20</th>
              <th className="text-right px-3 py-2 font-medium">SMMA120</th>
              <th className="text-right px-3 py-2 font-medium">LTQ</th>
              <th className="text-right px-3 py-2 font-medium">ETQ 5m</th>
              <th className="text-right px-3 py-2 font-medium">ETQ 20m</th>
              <th className="text-right px-3 py-2 font-medium">ETQ 60m</th>
              <th className="text-right px-3 py-2 font-medium">Avg LTP 20m</th>
              <th className="text-right px-3 py-2 font-medium">Avg LTP 60m</th>
              <th className="text-right px-3 py-2 font-medium border-l border-zinc-800">Bid Price</th>
              <th className="text-right px-3 py-2 font-medium">Bid Qty</th>
              <th className="text-right px-3 py-2 font-medium">Ask Price</th>
              <th className="text-right px-3 py-2 font-medium">Ask Qty</th>
              <th className="text-right px-3 py-2 font-medium border-l border-zinc-800">Signal</th>
              <th className="text-right px-3 py-2 font-medium">AI Prob.</th>
              <th className="text-right px-3 py-2 font-medium">Decision</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((s) => {
              const t = s.tick;
              const isSel = selected === t.symbol;
              return (
                <tr
                  key={t.symbol}
                  data-testid={DASH.row(t.symbol)}
                  onClick={() => onSelect?.(t.symbol)}
                  className={`border-b border-zinc-900 cursor-pointer hover:bg-zinc-900/60 ${
                    isSel ? "bg-zinc-900/80" : ""
                  }`}
                >
                  <td className="px-3 py-2 text-left font-mono-data font-medium text-zinc-100">
                    {t.symbol}
                  </td>
                  <td className="px-3 py-2 text-left">
                    <ScreenBadge
                      symbol={t.symbol}
                      priceOk={s.price_qualified}
                      liqOk={s.liquidity_qualified}
                      qualified={s.qualified}
                    />
                  </td>
                  <TickCell value={t.ltp} className={s.price_qualified ? "text-zinc-100" : "text-zinc-500"} />
                  <td className="px-3 py-2 text-right border-l border-zinc-800 font-mono-data text-zinc-300">
                    {s.smma20 != null ? `₹${s.smma20.toFixed(2)}` : <Muted />}
                  </td>
                  <td className="px-3 py-2 text-right font-mono-data text-zinc-300">
                    {s.smma120 != null ? `₹${s.smma120.toFixed(2)}` : <Muted />}
                  </td>
                  <td className="px-3 py-2 text-right font-mono-data text-zinc-300">{fmtQty(t.ltq)}</td>
                  <td className="px-3 py-2 text-right font-mono-data text-zinc-300">
                    {s.etq_5m != null ? fmtQty(s.etq_5m) : <Muted />}
                  </td>
                  <td className="px-3 py-2 text-right font-mono-data text-zinc-300">
                    {s.etq_20m != null ? fmtQty(s.etq_20m) : <Muted />}
                  </td>
                  <td className="px-3 py-2 text-right font-mono-data text-zinc-300">
                    {s.etq_60m != null ? fmtQty(s.etq_60m) : <Muted />}
                  </td>
                  <td className="px-3 py-2 text-right font-mono-data text-zinc-300">
                    {s.avg_ltp_20m != null ? `₹${s.avg_ltp_20m.toFixed(2)}` : <Muted />}
                  </td>
                  <td className="px-3 py-2 text-right font-mono-data text-zinc-300">
                    {s.avg_ltp_60m != null ? `₹${s.avg_ltp_60m.toFixed(2)}` : <Muted />}
                  </td>
                  <TickCell value={t.bid_price} className="text-emerald-400/90 border-l border-zinc-800" />
                  <td className={`px-3 py-2 text-right font-mono-data ${s.liquidity_qualified ? "text-emerald-300" : "text-zinc-500"}`}>
                    {fmtQty(t.bid_quantity)}
                  </td>
                  <TickCell value={t.ask_price} className="text-red-400/90" />
                  <td className={`px-3 py-2 text-right font-mono-data ${s.liquidity_qualified ? "text-red-300" : "text-zinc-500"}`}>
                    {fmtQty(t.ask_quantity)}
                  </td>
                  <td className="px-3 py-2 text-right border-l border-zinc-800">
                    <SignalPill signal={s.signal} lastSignal={s.last_signal} />
                  </td>
                  <td className="px-3 py-2 text-right font-mono-data">
                    <AiProbabilityCell
                      probability={s.ai_probability}
                      hasSignal={!!s.last_signal}
                    />
                  </td>
                  <td className="px-3 py-2 text-right">
                    <DecisionCell decision={s.decision} hasSignal={!!s.last_signal} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
