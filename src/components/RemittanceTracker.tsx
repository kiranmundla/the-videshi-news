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

interface RateProvider {
  provider: string;
  rate: number;
  fee_usd: number;
  recipient_gets_inr: number;
  delivery?: string;
  source_url?: string;
  as_of?: string;
  promo?: boolean;
  promo_note?: string;
}

interface ProviderRates {
  as_of: string;
  send_usd: number;
  providers: RateProvider[];
}
export default function RemittanceTracker() {
  const [data, setData] = useState<UsdInrData | null>(null);
  const [providers, setProviders] = useState<ProviderRates | null>(null);

  useEffect(() => {
    fetch("/data/usdinr.json")
      .then((r) => (r.ok ? r.json() : null))
      .then(setData)
      .catch(() => {});
    fetch("/data/remittance-rates.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => {
        if (j && Array.isArray(j.providers) && j.providers.length > 0) setProviders(j);
      })
      .catch(() => {});
  }, []);

  if (!data) return null;

  const up = data.day_change >= 0;
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
                <p className="text-white/50 text-sm mt-1">per US $1 · 30-day range ₹{data.low_30d.toFixed(2)} – ₹{data.high_30d.toFixed(2)}</p>
              </div>

              {/* Chart — desktop only; mobile stays lean */}
              <div className="hidden md:block bg-white/[0.03] rounded-xl p-3 border border-white/10">
                <p className="text-[11px] uppercase tracking-wider text-white/40 px-1 pb-2">Last 30 days</p>
                <Sparkline points={data.sparkline} />
              </div>
            </div>

            {/* Provider comparison — who puts more rupees in hand */}
            {providers && (
              <div className="mt-6">
                <div className="mb-3">
                  <h3 className="text-white font-bold text-[15px]">
                    Who gives you more for ${providers.send_usd.toLocaleString()}?
                  </h3>
                  <span className="text-[11px] text-white/40">
                    Updated {fmtDate(providers.as_of)} · bank deposit
                  </span>
                </div>
                {/* Desktop table */}
                <div className="hidden md:block overflow-x-auto rounded-xl border border-white/10">
                  <table className="w-full text-sm min-w-[520px]">
                    <thead>
                      <tr className="text-left text-[11px] uppercase tracking-wider text-white/40 border-b border-white/10">
                        <th className="px-4 py-2.5 font-semibold">Provider</th>
                        <th className="px-4 py-2.5 font-semibold text-right">Rate</th>
                        <th className="px-4 py-2.5 font-semibold text-right">Fee</th>
                        <th className="px-4 py-2.5 font-semibold text-right">They get</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[...providers.providers]
                        .sort((a, b) => b.recipient_gets_inr - a.recipient_gets_inr)
                        .map((p, i) => (
                          <tr
                            key={p.provider}
                            className={`border-b border-white/5 last:border-0 ${i === 0 ? "bg-[#D4A843]/10" : ""}`}
                          >
                            <td className="px-4 py-2.5 text-white font-semibold">
                              {p.provider}
                              {i === 0 && (
                                <span className="ml-2 text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-[#D4A843] text-[#0B1D3A]">
                                  Best
                                </span>
                              )}
                              {p.promo ? (
                                <span className="block text-[11px] text-white/40 font-normal">
                                  {p.promo_note || "Promotional rate"} · as of {p.as_of ? fmtDate(p.as_of) : "—"}
                                </span>
                              ) : (
                                <span className="block text-[11px] text-white/40 font-normal">
                                  {[p.delivery, p.as_of ? `as of ${fmtDate(p.as_of)}` : null].filter(Boolean).join(" · ")}
                                </span>
                              )}
                            </td>
                            <td className="px-4 py-2.5 text-right text-white/70 tabular-nums">₹{p.rate.toFixed(2)}</td>
                            <td className="px-4 py-2.5 text-right text-white/70 tabular-nums">${p.fee_usd.toFixed(2)}</td>
                            <td className="px-4 py-2.5 text-right text-[#D4A843] font-bold tabular-nums">
                              ₹{p.recipient_gets_inr.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
                {/* Mobile: stacked provider cards, no horizontal scroll */}
                <div className="md:hidden rounded-xl border border-white/10 divide-y divide-white/5 overflow-hidden">
                  {[...providers.providers]
                    .sort((a, b) => b.recipient_gets_inr - a.recipient_gets_inr)
                    .map((p, i) => (
                      <div key={p.provider} className={`px-4 py-3 ${i === 0 ? "bg-[#D4A843]/10" : ""}`}>
                        <div className="flex items-center justify-between gap-2">
                          <div className="min-w-0">
                            <span className="text-white font-semibold text-[15px]">{p.provider}</span>
                            {i === 0 && (
                              <span className="ml-2 text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-[#D4A843] text-[#0B1D3A] align-middle">
                                Best
                              </span>
                            )}
                            <p className="text-[11px] text-white/40 truncate">
                              {p.promo
                                ? `${p.promo_note || "Promotional rate"} · as of ${p.as_of ? fmtDate(p.as_of) : "—"}`
                                : [p.delivery, p.as_of ? `as of ${fmtDate(p.as_of)}` : null].filter(Boolean).join(" · ")}
                            </p>
                          </div>
                          <div className="text-right shrink-0">
                            <p className="text-[#D4A843] font-bold text-lg tabular-nums">
                              ₹{p.recipient_gets_inr.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                            </p>
                            <p className="text-[11px] text-white/40 tabular-nums">
                              ₹{p.rate.toFixed(2)} · ${p.fee_usd.toFixed(2)} fee
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
                <p className="text-white/30 text-[11px] mt-2">
                  Best available advertised rates for bank deposit — some are new-customer promos. Providers change rates through the day; check before sending.
                </p>
              </div>
            )}
          </div>
          <div className="h-1" style={{ background: "linear-gradient(90deg, #D4A843, #A32D2F)" }} />
        </div>
      </div>
    </section>
  );
}
