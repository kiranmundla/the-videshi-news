import { useState, useEffect, useMemo } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { H1BDataRow, getH1BData } from "@/lib/immigration";

/* ------------------------------------------------------------------ */
/* Stat Card                                                          */
/* ------------------------------------------------------------------ */
function StatCard({ label, value, color, sub }: { label: string; value: string; color?: string; sub?: string }) {
  return (
    <div className="p-5 bg-card border border-border rounded-xl text-center">
      <p className={`text-3xl font-bold ${color || "text-foreground"}`}>{value}</p>
      <p className="text-xs text-foreground/50 mt-1">{label}</p>
      {sub && <p className="text-[10px] text-foreground/30 mt-0.5">{sub}</p>}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* H1B Hub Page                                                       */
/* ------------------------------------------------------------------ */
export default function H1BHubPage() {
  const [data, setData] = useState<H1BDataRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getH1BData().then((d) => {
      setData(d);
      setLoading(false);
    });
  }, []);

  const fiscalYears = useMemo(() => [...new Set(data.map((d) => d.fiscal_year))].sort().reverse(), [data]);
  const latestFY = fiscalYears[0];

  const get = (fy: number, metric: string) => data.find((d) => d.fiscal_year === fy && d.metric === metric)?.value || "—";

  return (
    <>
      <Helmet>
        <title>H-1B Visa Hub — Lottery Stats, Cap Season, Indian Workers | The Videshi</title>
        <meta name="description" content="H-1B visa hub for Indian professionals. FY2027 lottery results, selection rates, registration stats, wage-weighted changes, and guides." />
        <meta property="og:title" content="H-1B Visa Hub | The Videshi" />
        <meta property="og:url" content="https://www.thevideshi.com/immigration/h1b" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8">
        {/* Hero */}
        <section className="relative mb-8 -mx-4 px-4 py-10 md:py-14 rounded-2xl overflow-hidden bg-[#1a1a2e] border border-[#2a2a4a]/40">
          <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl" />
          <div className="relative z-10 max-w-3xl">
            <Link to="/immigration" className="text-xs text-amber-300/70 hover:text-amber-300 mb-3 inline-block">← Immigration Hub</Link>
            <h1 className="font-serif text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight text-white">
              H-1B Visa Hub
            </h1>
            <p className="text-white/60 mt-3 text-base md:text-lg">
              Lottery results, cap season updates, and everything Indian professionals need to know about the H-1B visa.
            </p>
          </div>
        </section>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : (
          <>
            {/* Latest FY stats */}
            {latestFY && (
              <section className="mb-10">
                <h2 className="font-serif text-xl font-bold mb-4 flex items-center gap-2">
                  <span>🎰</span> FY{latestFY} Lottery Results
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <StatCard label="Total Registrations" value={get(latestFY, "total_registrations")} />
                  <StatCard label="Selection Rate" value={get(latestFY, "selection_rate")} color="text-purple-500" />
                  <StatCard label="Indian Nationals" value={get(latestFY, "india_pct")} color="text-amber-500" />
                  <StatCard label="US Master's+" value={get(latestFY, "masters_pct")} color="text-blue-500" />
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                  <StatCard label="Regular Cap" value={get(latestFY, "cap_regular")} sub="65,000 visas" />
                  <StatCard label="Master's Cap" value={get(latestFY, "cap_masters")} sub="20,000 additional" />
                  <StatCard label="Selected" value={get(latestFY, "selected")} color="text-green-500" />
                  <StatCard label="Avg Registrations/Person" value={get(latestFY, "avg_registrations_per_beneficiary") !== "—" ? get(latestFY, "avg_registrations_per_beneficiary") : "~1.01"} />
                </div>
              </section>
            )}

            {/* Historical comparison */}
            {fiscalYears.length > 1 && (
              <section className="mb-10">
                <h2 className="font-serif text-xl font-bold mb-4 flex items-center gap-2">
                  <span>📊</span> Year-over-Year Comparison
                </h2>
                <div className="bg-card border border-border rounded-xl overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border bg-foreground/[0.02]">
                        <th className="text-left py-3 px-4 text-foreground/50 font-medium">Metric</th>
                        {fiscalYears.slice(0, 3).map((fy) => (
                          <th key={fy} className="text-right py-3 px-4 text-foreground/50 font-medium">FY{fy}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { metric: "total_registrations", label: "Total Registrations" },
                        { metric: "selected", label: "Selected" },
                        { metric: "selection_rate", label: "Selection Rate" },
                        { metric: "india_pct", label: "Indian Nationals %" },
                        { metric: "masters_pct", label: "US Master's+ %" },
                      ].map((row) => (
                        <tr key={row.metric} className="border-b border-border/50 hover:bg-foreground/[0.02]">
                          <td className="py-2.5 px-4 font-medium">{row.label}</td>
                          {fiscalYears.slice(0, 3).map((fy) => (
                            <td key={fy} className="py-2.5 px-4 text-right font-mono">{get(fy, row.metric)}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

            {/* Wage-weighted selection explained */}
            <section className="mb-10">
              <div className="bg-card border border-border rounded-xl p-6">
                <h3 className="font-serif text-lg font-bold mb-4">🆕 What Changed: Wage-Weighted Selection</h3>
                <div className="space-y-3 text-sm text-foreground/70 leading-relaxed">
                  <p>
                    Starting with <strong>FY2027</strong>, USCIS shifted to a <strong>wage-weighted selection process</strong>.
                    Instead of a pure random lottery, registrations are now prioritized based on the offered wage level relative
                    to the prevailing wage for the occupation and area of employment.
                  </p>
                  <p>
                    <strong>What this means for Indians:</strong> Higher-paying positions (typically Level 3-4 wages) have significantly
                    better odds. Only <strong>17.7%</strong> of FY2027 selections were at the lowest wage level, compared to ~25% historically.
                    71.5% of selected beneficiaries hold a US master's degree or higher (up from 57%).
                  </p>
                  <p>
                    <strong>Impact:</strong> This effectively favors experienced professionals with advanced degrees and higher salaries,
                    while making it harder for entry-level positions and outsourcing firms that file at lower wage levels.
                  </p>
                </div>
              </div>
            </section>

            {/* Key dates */}
            <section className="mb-10">
              <div className="bg-card border border-border rounded-xl p-6">
                <h3 className="font-serif text-lg font-bold mb-4">📅 Key H-1B Dates</h3>
                <div className="space-y-2">
                  {[
                    { date: "Early March", event: "Registration period opens", desc: "Employers register beneficiaries online" },
                    { date: "Mid-March", event: "Registration closes", desc: "~2 week window" },
                    { date: "Late March", event: "Lottery results announced", desc: "Selected beneficiaries notified" },
                    { date: "April 1", event: "Filing period begins", desc: "90-day window to file I-129 petitions" },
                    { date: "October 1", event: "New FY starts", desc: "Approved H-1B workers can begin employment" },
                  ].map((item) => (
                    <div key={item.event} className="flex items-start gap-3 py-2">
                      <span className="font-mono text-xs text-primary bg-primary/10 px-2 py-1 rounded shrink-0 mt-0.5 w-28 text-center">{item.date}</span>
                      <div>
                        <p className="text-sm font-semibold">{item.event}</p>
                        <p className="text-xs text-foreground/50">{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* Related guides */}
            <section className="mb-10">
              <h2 className="font-serif text-lg font-bold mb-4 flex items-center gap-2">
                <span>📚</span> Related Guides
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  { slug: "h1b-visa-complete-guide", title: "H-1B Visa: The Complete Guide", emoji: "💼" },
                  { slug: "f1-to-h1b-transition", title: "F-1 to H-1B: Student to Worker", emoji: "🎓" },
                  { slug: "h4-ead-work-authorization", title: "H-4 EAD: Work Authorization for Spouses", emoji: "👩‍💼" },
                  { slug: "green-card-employment-based", title: "Green Card: After Your H-1B", emoji: "🟢" },
                ].map((g) => (
                  <Link key={g.slug} to={`/immigration/guides/${g.slug}`} className="flex items-center gap-3 p-4 bg-card border border-border rounded-xl hover:border-primary/40 transition-all group">
                    <span className="text-2xl">{g.emoji}</span>
                    <span className="text-sm font-semibold group-hover:text-primary transition-colors">{g.title}</span>
                  </Link>
                ))}
              </div>
            </section>
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
