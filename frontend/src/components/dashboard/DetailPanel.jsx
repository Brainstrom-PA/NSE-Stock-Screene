import { DASH } from "../../constants/testIds";

function Row({ label, value, valueClass = "" }) {
  return (
    <div className="flex justify-between items-baseline py-1.5 border-b border-zinc-800/60">
      <span className="text-[11px] uppercase tracking-wider text-zinc-500">
        {label}
      </span>
      <span className={`font-mono-data text-sm ${valueClass}`}>{value}</span>
    </div>
  );
}

const stanceOf = (s) => {
  if (s.smma20 == null || s.smma120 == null) return "—";
  if (s.smma20 > s.smma120) return "BULLISH";
  if (s.smma20 < s.smma120) return "BEARISH";
  return "FLAT";
};

export default function DetailPanel({ stock }) {
  if (!stock) {
    return (
      <aside
        data-testid={DASH.detailPanel}
        className="border border-zinc-800 bg-[#121212] rounded-sm p-5 h-full"
      >
        <h3 className="font-heading text-sm uppercase tracking-wider font-bold">
          Instrument Detail
        </h3>
        <p className="text-xs text-zinc-500 mt-2">
          Select a row from the table to inspect market depth and quantitative
          context.
        </p>
      </aside>
    );
  }

  const t = stock.tick;
  const inr = (v) => `₹${Number(v).toFixed(2)}`;
  const qty = (v) => Number(v).toLocaleString("en-IN");

  return (
    <aside
      data-testid={DASH.detailPanel}
      className="border border-zinc-800 bg-[#121212] rounded-sm p-5 h-full flex flex-col gap-4"
    >
      <div>
        <div className="flex items-center justify-between">
          <h3 className="font-heading text-lg font-bold tracking-tight">
            {t.symbol}
          </h3>
          <span
            className={`text-[10px] uppercase px-2 py-0.5 rounded-sm border ${
              stock.qualified
                ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300"
                : "border-zinc-700 text-zinc-500"
            }`}
          >
            {stock.qualified ? "QUALIFIED" : "NOT QUALIFIED"}
          </span>
        </div>
        <div className="text-[11px] text-zinc-500 mt-0.5">
          {t.exchange} · Token {t.token} · Source {t.source}
        </div>
      </div>

      <section>
        <div className="text-[10px] uppercase tracking-widest text-zinc-500 mb-2">
          Screening Result
        </div>
        <Row
          label="Price 30 ≤ LTP ≤ 500"
          value={stock.price_qualified ? "PASS" : "FAIL"}
          valueClass={stock.price_qualified ? "text-emerald-400" : "text-red-400"}
        />
        <Row
          label="Bid Qty > 10L"
          value={t.bid_quantity > 1_000_000 ? "PASS" : "FAIL"}
          valueClass={t.bid_quantity > 1_000_000 ? "text-emerald-400" : "text-red-400"}
        />
        <Row
          label="Ask Qty > 10L"
          value={t.ask_quantity > 1_000_000 ? "PASS" : "FAIL"}
          valueClass={t.ask_quantity > 1_000_000 ? "text-emerald-400" : "text-red-400"}
        />
      </section>

      <section>
        <div className="text-[10px] uppercase tracking-widest text-zinc-500 mb-2">
          Top of Book (Market Depth)
        </div>
        <Row label="Last Traded" value={inr(t.ltp)} valueClass="text-zinc-100" />
        <Row label="LTQ" value={qty(t.ltq)} valueClass="text-zinc-300" />
        <Row label="Day Volume" value={qty(t.day_volume)} valueClass="text-zinc-300" />
        <Row label="Bid Price" value={inr(t.bid_price)} valueClass="text-emerald-300" />
        <Row label="Bid Quantity" value={qty(t.bid_quantity)} valueClass="text-emerald-300" />
        <Row label="Ask Price" value={inr(t.ask_price)} valueClass="text-red-300" />
        <Row label="Ask Quantity" value={qty(t.ask_quantity)} valueClass="text-red-300" />
      </section>

      <section>
        <div className="text-[10px] uppercase tracking-widest text-zinc-500 mb-2">
          SMMA &amp; Signal
        </div>
        <Row
          label="SMMA20"
          value={stock.smma20 != null ? inr(stock.smma20) : "—"}
          valueClass="text-zinc-100"
        />
        <Row
          label="SMMA120"
          value={stock.smma120 != null ? inr(stock.smma120) : "—"}
          valueClass="text-zinc-100"
        />
        <Row
          label="Stance"
          value={stanceOf(stock)}
          valueClass={
            stanceOf(stock) === "BULLISH"
              ? "text-emerald-300"
              : stanceOf(stock) === "BEARISH"
              ? "text-red-300"
              : "text-zinc-500"
          }
        />
        <Row
          label="Latest Event"
          value={stock.signal || stock.last_signal || "—"}
          valueClass={
            stock.signal === "BUY"
              ? "text-emerald-300 font-semibold"
              : stock.signal === "SELL"
              ? "text-red-300 font-semibold"
              : stock.last_signal === "BUY"
              ? "text-emerald-500/70"
              : stock.last_signal === "SELL"
              ? "text-red-500/70"
              : "text-zinc-500"
          }
        />
        {stock.last_signal_at && (
          <Row
            label="Event Time"
            value={new Date(stock.last_signal_at).toLocaleTimeString([], {
              hour12: false,
            })}
            valueClass="text-zinc-400"
          />
        )}
      </section>

      <section>
        <div className="text-[10px] uppercase tracking-widest text-zinc-500 mb-2">
          Rolling Activity
        </div>
        <Row
          label="ETQ 5m"
          value={stock.etq_5m != null ? qty(stock.etq_5m) : "—"}
          valueClass="text-zinc-100"
        />
        <Row
          label="ETQ 20m"
          value={stock.etq_20m != null ? qty(stock.etq_20m) : "—"}
          valueClass="text-zinc-100"
        />
        <Row
          label="ETQ 60m"
          value={stock.etq_60m != null ? qty(stock.etq_60m) : "—"}
          valueClass="text-zinc-100"
        />
        <Row
          label="Avg LTP 20m"
          value={stock.avg_ltp_20m != null ? inr(stock.avg_ltp_20m) : "—"}
          valueClass="text-zinc-100"
        />
        <Row
          label="Avg LTP 60m"
          value={stock.avg_ltp_60m != null ? inr(stock.avg_ltp_60m) : "—"}
          valueClass="text-zinc-100"
        />
      </section>

      <section>
        <div className="text-[10px] uppercase tracking-widest text-zinc-500 mb-2">
          AI Model
        </div>
        <Row
          label="Probability"
          value={
            stock.ai_probability != null
              ? `${(stock.ai_probability * 100).toFixed(1)}%`
              : stock.last_signal
              ? "Insufficient training data"
              : "—"
          }
          valueClass={
            stock.ai_probability != null
              ? stock.ai_probability >= 0.6
                ? "text-emerald-300"
                : "text-amber-300"
              : "text-zinc-500 italic"
          }
        />
        <Row
          label="Decision"
          value={
            stock.decision === "ACCEPT"
              ? "ACCEPT"
              : stock.decision === "AVOID"
              ? "AVOID"
              : stock.last_signal
              ? "Pending ML training data"
              : "—"
          }
          valueClass={
            stock.decision === "ACCEPT"
              ? "text-emerald-300 font-semibold"
              : stock.decision === "AVOID"
              ? "text-red-300 font-semibold"
              : "text-zinc-500 italic"
          }
        />
        {stock.explanation && (
          <div className="mt-2 text-xs text-zinc-400 leading-relaxed">
            {stock.explanation}
          </div>
        )}
      </section>
    </aside>
  );
}
