import { useState, useEffect, useMemo } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  ConsulateWaitRow,
  getConsulateWaitTimes,
  formatWaitMonths,
  waitColor,
  waitBg,
  INDIA_CONSULATES,
  CONSULATE_DISPLAY,
} from "@/lib/immigration";

/* ------------------------------------------------------------------ */
/* Third-country consulates for Indian H-1B holders                   */
/* ------------------------------------------------------------------ */
const THIRD_COUNTRY = ["dubai", "singapore", "toronto", "calgary", "london"] as const;
const THIRD_DISPLAY: Record<string, string> = {
  dubai: "🇦🇪 Dubai",
  singapore: "🇸🇬 Singapore",
  toronto: "🇨🇦 Toronto",
  calgary: "🇨🇦 Calgary",
  london: "🇬🇧 London",
};

const VISA_TYPE_LABELS: Record<string, string> = {
  B1B2: "Visitor (B1/B2)",
  F_M_J: "Student (F/M/J)",
  H_L_O_P_Q: "Work (H/L/O/P/Q)",
  C_D: "Crew (C/D)",
};

const VISA_TYPES = ["B1B2", "F_M_J", "H_L_O_P_Q", "C_D"];

/* ------------------------------------------------------------------ */
/* Consulate Card                                                     */
/* ------------------------------------------------------------------ */
function ConsulateDetailCard({
  consulate,
  label,
  rows,
}: {
  consulate: string;
  label: string;
  rows: Record<string, ConsulateWaitRow>;
}) {
  // Determine overall color from B1/B2
  const b1b2 = rows["B1B2"];
  const mainWait = b1b2?.next_available_months ?? b1b2?.avg_wait_months ?? null;
  const borderColor = mainWait === null
    ? "border-border"
    : mainWait < 2 ? "border-green-500/30" : mainWait < 5 ? "border-yellow-500/30" : mainWait < 8 ? "border-orange-500/30" : "border-red-500/30";

  return (
    <div className={`bg-card border-2 ${borderColor} rounded-xl overflow-hidden`}>
      <div className="flex items-center justify-between px-5 py-3 border-b border-border bg-foreground/[0.02]">
        <h3 className="font-serif font-bold text-base">{label}</h3>
        {mainWait !== null && (
          <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${waitBg(mainWait)} ${waitColor(mainWait)}`}>
            {mainWait < 2 ? "Fast" : mainWait < 5 ? "Moderate" : mainWait < 8 ? "Slow" : "Very Slow"}
          </span>
        )}
      </div>
      <div className="divide-y divide-border/50">
        {VISA_TYPES.map((vt) => {
          const row = rows[vt];
          const avg = row?.avg_wait_months;
          const next = row?.next_available_months;
          return (
            <div key={vt} className="flex items-center justify-between px-5 py-2.5">
              <span className="text-sm text-foreground/70">{VISA_TYPE_LABELS[vt]}</span>
              <div className="flex items-center gap-4 text-sm">
                {avg !== null && avg !== undefined && (
                  <div className="text-right">
                    <span className={`font-mono font-semibold ${waitColor(avg)}`}>{formatWaitMonths(avg)}</span>
                    <p className="text-[10px] text-foreground/30">avg</p>
                  </div>
                )}
                <div className="text-right">
                  <span className={`font-mono font-semibold ${waitColor(next ?? null)}`}>{formatWaitMonths(next ?? null)}</span>
                  <p className="text-[10px] text-foreground/30">next appt</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Page                                                               */
/* ------------------------------------------------------------------ */
export default function ConsulateWaitTimesPage() {
  const [allData, setAllData] = useState<ConsulateWaitRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getConsulateWaitTimes().then((data) => {
      setAllData(data);
      setLoading(false);
    });
  }, []);

  // Group by consulate → visa_type (latest only)
  const grouped = useMemo(() => {
    const map: Record<string, Record<string, ConsulateWaitRow>> = {};
    for (const row of allData) {
      if (!map[row.consulate]) map[row.consulate] = {};
      if (!map[row.consulate][row.visa_type]) {
        map[row.consulate][row.visa_type] = row;
      }
    }
    return map;
  }, [allData]);

  // Find fastest for H/L stamping
  const fastestHL = useMemo(() => {
    let best: { consulate: string; months: number } | null = null;
    for (const c of INDIA_CONSULATES) {
      const hl = grouped[c]?.["H_L_O_P_Q"];
      if (hl?.next_available_months != null) {
        if (!best || hl.next_available_months < best.months) {
          best = { consulate: c, months: hl.next_available_months };
        }
      }
    }
    return best;
  }, [grouped]);

  const sourceDate = allData[0]?.source_updated;

  return (
    <>
      <Helmet>
        <title>US Consulate Wait Times in India — Mumbai, Delhi, Chennai, Hyderabad, Kolkata | The Videshi</title>
        <meta name="description" content="Compare US visa appointment wait times across all 5 Indian consulates. B1/B2 visitor visa, H-1B/L-1 work visa, student visa, and more." />
        <meta property="og:title" content="US Consulate Wait Times — India | The Videshi" />
        <meta property="og:url" content="https://www.thevideshi.com/immigration/consulate-wait-times" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8">
        {/* Hero */}
        <section className="relative mb-8 -mx-4 px-4 py-10 md:py-14 rounded-2xl overflow-hidden bg-[#1a1a2e] border border-[#2a2a4a]/40">
          <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl" />
          <div className="relative z-10 max-w-3xl">
            <Link to="/immigration" className="text-xs text-amber-300/70 hover:text-amber-300 mb-3 inline-block">← Immigration Hub</Link>
            <h1 className="font-serif text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight text-white">
              US Consulate Wait Times
            </h1>
            <p className="text-white/60 mt-3 text-base md:text-lg">
              Compare visa appointment availability across all 5 US consulates in India
              {sourceDate && <span className="ml-2 text-white/40">· Updated {sourceDate}</span>}
            </p>
          </div>
        </section>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : (
          <>
            {/* Fastest for stamping banner */}
            {fastestHL && (
              <div className="mb-6 p-4 bg-green-500/10 border border-green-500/20 rounded-xl flex items-center gap-3">
                <span className="text-2xl">⚡</span>
                <div>
                  <p className="text-sm font-semibold">
                    Fastest for H/L/O work visa stamping: <span className="text-green-500">{CONSULATE_DISPLAY[fastestHL.consulate]}</span>
                  </p>
                  <p className="text-xs text-foreground/50">Next available appointment: {formatWaitMonths(fastestHL.months)}</p>
                </div>
              </div>
            )}

            {/* Indian Consulates */}
            <h2 className="font-serif text-xl font-bold mb-4 flex items-center gap-2">
              <span>🇮🇳</span> Indian Consulates
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5 mb-12">
              {INDIA_CONSULATES.map((c) => {
                if (!grouped[c]) return null;
                return (
                  <ConsulateDetailCard
                    key={c}
                    consulate={c}
                    label={CONSULATE_DISPLAY[c]}
                    rows={grouped[c]}
                  />
                );
              })}
            </div>

            {/* Third-country stamping */}
            <h2 className="font-serif text-xl font-bold mb-2 flex items-center gap-2">
              <span>🌏</span> Third-Country Stamping Options
            </h2>
            <p className="text-sm text-foreground/50 mb-4">
              Popular consulates for Indians doing visa stamping outside India — can be faster depending on the season.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5 mb-12">
              {THIRD_COUNTRY.map((c) => {
                if (!grouped[c]) return null;
                return (
                  <ConsulateDetailCard
                    key={c}
                    consulate={c}
                    label={THIRD_DISPLAY[c]}
                    rows={grouped[c]}
                  />
                );
              })}
              {THIRD_COUNTRY.every((c) => !grouped[c]) && (
                <div className="col-span-full text-center py-8 text-foreground/40">
                  <p>Third-country wait time data coming soon</p>
                </div>
              )}
            </div>

            {/* Tips */}
            <div className="bg-card border border-border rounded-xl p-6 mb-8">
              <h3 className="font-serif text-lg font-bold mb-4">💡 Consulate Appointment Tips</h3>
              <ul className="space-y-3 text-sm text-foreground/70">
                <li className="flex gap-2">
                  <span className="text-green-500 font-bold">✓</span>
                  <span>Check appointment slots <strong>daily</strong> — consulates release new slots regularly. Morning is best.</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-green-500 font-bold">✓</span>
                  <span>Consider <strong>lesser-known consulates</strong> — Kolkata and Chennai often have shorter wait times than Mumbai/Delhi.</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-green-500 font-bold">✓</span>
                  <span>For <strong>emergency appointments</strong>, you can request expedited scheduling through the embassy website if you have urgent travel needs.</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-green-500 font-bold">✓</span>
                  <span><strong>Dropbox/Interview Waiver</strong> is available for many H-1B/L-1 renewals — check eligibility to skip the interview entirely.</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-green-500 font-bold">✓</span>
                  <span><strong>Third-country stamping</strong> (e.g., Canada, Dubai) can be faster — but confirm the consulate accepts TCN appointments for your visa type.</span>
                </li>
              </ul>
            </div>
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
