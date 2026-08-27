/**
 * useMarketData — polls the backend snapshot every N seconds.
 *
 * Kept intentionally provider-agnostic so it can be swapped for a
 * WebSocket subscription in Phase 2 without touching UI components.
 */
import { useEffect, useRef, useState } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export function useMarketData(intervalMs = 2000) {
  const [snapshot, setSnapshot] = useState([]);
  const [summary, setSummary] = useState(null);
  const [source, setSource] = useState(null);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const timerRef = useRef(null);

  useEffect(() => {
    // Defined inside the effect so React's exhaustive-deps rule is honest
    // and the interval never captures a stale closure.
    const fetchAll = async () => {
      try {
        const [snap, src] = await Promise.all([
          axios.get(`${API}/snapshot`),
          axios.get(`${API}/source`),
        ]);
        const rows = snap.data;
        setSnapshot(rows);
        setSource(src.data);
        // Derive the summary client-side from the same snapshot, so the KPI
        // cards and the table are guaranteed to reflect the SAME tick.
        setSummary({
          nse_universe: rows.length,
          price_qualified: rows.filter((r) => r.price_qualified).length,
          liquidity_qualified: rows.filter((r) => r.liquidity_qualified).length,
          fully_qualified: rows.filter((r) => r.qualified).length,
          active_signals: rows.filter((r) => r.signal != null).length,
          lifetime_signals: rows.filter((r) => r.last_signal != null).length,
          signals_status: "SMMA(20)/SMMA(120) crossover live",
        });
        setLastUpdated(new Date());
        setError(null);
      } catch (e) {
        setError(e?.message || "Failed to load market data");
      }
    };

    fetchAll();
    timerRef.current = setInterval(fetchAll, intervalMs);
    return () => clearInterval(timerRef.current);
  }, [intervalMs]);

  return { snapshot, summary, source, error, lastUpdated };
}
