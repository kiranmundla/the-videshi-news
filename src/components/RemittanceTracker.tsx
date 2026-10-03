import { useState, useEffect } from "react";

interface SparkPoint { d: string; r: number; }
interface UsdInrData {
  pair: string;
  rate: number;
  date: string;
  updated_utc: string;
  source: string;
  day_change: number;
  day_change_pct: number;
  high_30d: number;
  low_30d: number;
  sparkline: SparkPoint[];
}

/* ------------------------------------------------------------------ */
/* SVG sparkline                                                        */
/* ------------------------------------------------------------------ */
function Sparkline({ points }: { points: SparkPoint[] }) {
  if (points.length < 2) return null;
  const W = 560, H = 120, PAD = 8;
  const rates = points.map((p) => p.r);
  const min = Math.min(...rates), max = Math.max(...rates);
  const span = max - min || 1;
  const step = (W - PAD * 2) / (points.length - 1);
  const path = points
    .map((p, i) => {
      const x = PAD + i * step;
      const y = PAD + (1 - (p.r - min) / span) * (H - PAD * 2);
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  const last = points[points.length - 1];
  const lx = PAD + (points.length - 1) * step;
  const ly = PAD + (1 - (last.r - min) / span) * (H - PAD * 2);
  const up = last.r >= points[0].r;
  const stroke = up ? "#0E7C3A" : "#A32D2F";

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-24 md:h-28" preserveAspectRatio="none">
      <defs>
        <linearGradient id="usdinr-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={stroke} stopOpacity="0.18" />
          <stop offset="100%" stopColor={stroke} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={`${path} L${lx.toFixed(1)},${H} L${PAD},${H} Z`} fill="url(#usdinr-fill)" />
      <path d={path} fill="none" stroke={stroke} strokeWidth="2.5" strokeLinecap="round" />
      <circle cx={lx} cy={ly} r="4" fill={stroke} stroke="#fff" strokeWidth="2" />
    </svg>
  );
}

/* ------------------------------------------------------------------ */
/* Remittance tracker — USD → INR                                      */
/* ------------------------------------------------------------------ */
export default function RemittanceTracker() {
  const [data, setData] = useState<UsdInrData | null>(null);
  const [amount, setAmount] = useState("1000");

  useEffect(() => {
    fetch("/data/usdinr.json")
      .then((r) => (r.ok ? r.json() : null))
      .then(setData)
      .catch(() => {});
  }, []);

  if (!data) return null;

  const up = data.day_change >= 0;
  const inr = (parseFloat(amount) || 0) * data.rate;
  const fmtDate = (iso: string) => {
    const [y, m, d] = iso.split("-").map(Number);
    return new Date(y, m - 1, d).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  };

  return (
    <section className="mb-10">
      <div className="container">
        <div
          className="rounded-2xl overflow-hidden border border-[#0B1D3A]/10"
          style={{ background: "linear-gradient(135deg, #0B1D3A 0%, #132E57 100%)" }}
        >
          <div className="p-5 md:p-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <p className="text-[11px] uppercase tracking-[0.2em] text-[#D4A843] font-semibold mb-1">
                  Remittance Tracker
                </p>
                <h2 className="text-xl md:text-2xl font-bold text-white">
                  Dollar to Rupee
                </h2>
              </div>
              <div className="text-right">
                <p className="text-[11px] text-white/50">Mid-market · {fmtDate(data.date)}</p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6 md:gap-10 items-center">
              {/* Rate + converter */}
              <div>
                <div className="flex items-baseline gap-3">
                  <span className="text-4xl md:text-5xl font-bold text-white tabular-nums">
                    ₹{data.rate.toFixed(2)}
                  </span>
                  <span
                    className={`text-sm font-semibold px-2 py-0.5 rounded-full ${
                      up ? "bg-green-500/15 text-green-300" : "bg-red-500/15 text-red-300"
                    }`}
                  >
                    {up ? "▲" : "▼"} {Math.abs(data.day_change).toFixed(2)} ({Math.abs(data.day_change_pct).toFixed(2)}%)
                  </span>
                </div>
                <p className="text-white/50 text-sm mt-1 mb-5">per US $1 · 30-day range ₹{data.low_30d.toFixed(2)} – ₹{data.high_30d.toFixed(2)}</p>

                <div className="flex items-center gap-3 bg-white/5 rounded-xl p-3 border border-white/10">
                  <div className="flex-1">
                    <label className="text-[11px] uppercase tracking-wider text-white/40 block mb-1">You send</label>
                    <div className="flex items-center gap-1">
                      <span className="text-white/60 font-semibold">$</span>
                      <input
                        value={amount}
                        onChange={(e) => setAmount(e.target.value.replace(/[^0-9.]/g, ""))}
                        inputMode="decimal"
                        className="bg-transparent text-white text-xl font-bold w-full outline-none tabular-nums"
                      />
                    </div>
                  </div>
                  <div className="text-white/30 text-xl">→</div>
                  <div className="flex-1 text-right">
                    <label className="text-[11px] uppercase tracking-wider text-white/40 block mb-1">They get ≈</label>
                    <p className="text-[#D4A843] text-xl font-bold tabular-nums">
                      ₹{inr.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                    </p>
                  </div>
                </div>
                <p className="text-white/30 text-[11px] mt-2">Indicative mid-market rate — transfer services add their own margin.</p>
              </div>

              {/* Chart */}
              <div className="bg-white/[0.03] rounded-xl p-3 border border-white/10">
                <p className="text-[11px] uppercase tracking-wider text-white/40 px-1 pb-2">Last 30 days</p>
                <Sparkline points={data.sparkline} />
              </div>
            </div>
          </div>
          <div className="h-1" style={{ background: "linear-gradient(90deg, #D4A843, #A32D2F)" }} />
        </div>
      </div>
    </section>
  );
}
