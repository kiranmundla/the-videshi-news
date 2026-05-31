import { useState, useEffect, useMemo } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  VisaBulletinRow,
  getVisaBulletin,
  getVisaBulletinHistory,
  formatPriorityDate,
  computeMovement,
  EB_CATEGORIES,
  FAMILY_CATEGORIES,
} from "@/lib/immigration";

/* ------------------------------------------------------------------ */
/* Simple SVG line chart                                              */
/* ------------------------------------------------------------------ */
function PriorityDateChart({ history }: { history: VisaBulletinRow[] }) {
  const sorted = [...history]
    .filter((r) => r.priority_date && r.status === "dated")
    .sort((a, b) => {
      if (a.bulletin_year !== b.bulletin_year) return a.bulletin_year - b.bulletin_year;
      return a.bulletin_month - b.bulletin_month;
    });

  if (sorted.length < 2) {
    return <div className="text-sm text-foreground/40 py-8 text-center">Not enough data to display chart</div>;
  }

  const W = 600, H = 200, PAD_X = 60, PAD_Y = 30;
  const MONTH_NAMES = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  const timestamps = sorted.map((r) => new Date(r.priority_date! + "T00:00:00").getTime());
  const minT = Math.min(...timestamps);
  const maxT = Math.max(...timestamps);
  const rangeT = maxT - minT || 1;

  const points = sorted.map((r, i) => {
    const x = PAD_X + ((i) / (sorted.length - 1)) * (W - PAD_X * 2);
    const y = PAD_Y + (1 - (timestamps[i] - minT) / rangeT) * (H - PAD_Y * 2);
    return { x, y, r };
  });

  // Y-axis labels (min and max dates)
  const minDate = new Date(minT);
  const maxDate = new Date(maxT);
  const fmtDate = (d: Date) => `${MONTH_NAMES[d.getMonth() + 1]} ${d.getFullYear()}`;

  return (
    <div className="w-full overflow-x-auto">
      <svg viewBox={`0 0 ${W} ${H + 20}`} className="w-full min-w-[400px]" preserveAspectRatio="xMidYMid meet">
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((f) => {
          const y = PAD_Y + (1 - f) * (H - PAD_Y * 2);
          return <line key={f} x1={PAD_X} x2={W - PAD_X} y1={y} y2={y} stroke="currentColor" strokeOpacity={0.07} />;
        })}

        {/* Line */}
        <polyline
          fill="none"
          stroke="#22c55e"
          strokeWidth={2.5}
          strokeLinejoin="round"
          points={points.map((p) => `${p.x},${p.y}`).join(" ")}
        />

        {/* Area fill */}
        <polygon
          fill="url(#greenGrad)"
          opacity={0.15}
          points={`${points[0].x},${H - PAD_Y} ${points.map((p) => `${p.x},${p.y}`).join(" ")} ${points[points.length - 1].x},${H - PAD_Y}`}
        />

        {/* Dots */}
        {points.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r={4} fill="#22c55e" stroke="#1a1a2e" strokeWidth={2} />
        ))}

        {/* X-axis labels */}
        {points.map((p, i) => (
          <text key={i} x={p.x} y={H + 2} textAnchor="middle" className="fill-foreground/40" fontSize={10}>
            {MONTH_NAMES[p.r.bulletin_month]} {String(p.r.bulletin_year).slice(2)}
          </text>
        ))}

        {/* Y-axis labels */}
        <text x={PAD_X - 5} y={PAD_Y + 4} textAnchor="end" className="fill-foreground/50" fontSize={10}>{fmtDate(maxDate)}</text>
        <text x={PAD_X - 5} y={H - PAD_Y + 4} textAnchor="end" className="fill-foreground/50" fontSize={10}>{fmtDate(minDate)}</text>

        <defs>
          <linearGradient id="greenGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#22c55e" />
            <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Comparison Table (India vs China vs Worldwide)                     */
/* ------------------------------------------------------------------ */
function ComparisonTable({ category, allData }: { category: string; allData: VisaBulletinRow[] }) {
  const countries = ["india", "china", "worldwide"];
  const labels: Record<string, string> = { india: "🇮🇳 India", china: "🇨🇳 China", worldwide: "🌍 Worldwide" };

  const months = [...new Set(allData.filter((r) => r.category === category).map((r) => `${r.bulletin_year}-${r.bulletin_month}`))]
    .sort()
    .reverse();
  const latest = months[0];
  if (!latest) return null;
  const [ly, lm] = latest.split("-").map(Number);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            <th className="text-left py-2 px-3 text-foreground/50 font-medium">Country</th>
            <th className="text-right py-2 px-3 text-foreground/50 font-medium">Final Action Date</th>
            <th className="text-right py-2 px-3 text-foreground/50 font-medium">Dates for Filing</th>
          </tr>
        </thead>
        <tbody>
          {countries.map((country) => {
            const fa = allData.find((r) => r.category === category && r.country === country && r.chart_type === "final_action" && r.bulletin_year === ly && r.bulletin_month === lm);
            const df = allData.find((r) => r.category === category && r.country === country && r.chart_type === "dates_for_filing" && r.bulletin_year === ly && r.bulletin_month === lm);
            return (
              <tr key={country} className="border-b border-border/50 hover:bg-foreground/[0.02]">
                <td className="py-2.5 px-3 font-medium">{labels[country]}</td>
                <td className="py-2.5 px-3 text-right font-mono">{fa ? formatPriorityDate(fa.priority_date, fa.status) : "—"}</td>
                <td className="py-2.5 px-3 text-right font-mono">{df ? formatPriorityDate(df.priority_date, df.status) : "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Category Explanation                                               */
/* ------------------------------------------------------------------ */
const EXPLANATIONS: Record<string, string> = {
  "EB-1": "EB-1 is for priority workers with extraordinary ability, outstanding professors/researchers, and multinational managers. It's the fastest employment-based green card category — but India's massive demand has caused unprecedented backlogs even here.",
  "EB-2": "EB-2 is the most common category for Indian H-1B holders with a master's degree or equivalent. Requires PERM labor certification (unless filing NIW). India faces the longest backlog — currently 10+ years. Many Indians consider downgrading to EB-3 when it moves faster.",
  "EB-3": "EB-3 covers skilled workers and professionals with a bachelor's degree. Historically slower than EB-2, but in some periods the gap narrows — making EB-2→EB-3 downgrade a viable strategy. Currently only about 3 months behind EB-2 India.",
  "EB-5-Unreserved": "EB-5 is the investor visa requiring $800K (TEA) or $1.05M investment. Set-aside categories (Rural, High Unemployment, Infrastructure) remain 'Current' for India — making it an attractive backdoor for those stuck in EB-2/EB-3 backlogs.",
  "F1": "F1 is for unmarried sons and daughters of US citizens. Wait times for India are significant, typically 8-10 years from petition filing.",
  "F2A": "F2A covers spouses and minor children of permanent residents (green card holders). This category occasionally becomes 'Current' for India, allowing immediate filing.",
  "F2B": "F2B is for unmarried sons and daughters (21+) of permanent residents. Wait times exceed 8 years for India.",
  "F3": "F3 covers married sons and daughters of US citizens. Among the longest waits — 10+ years for India.",
  "F4": "F4 is for brothers and sisters of adult US citizens. The longest family-based wait — typically 12-15+ years for India.",
};

/* ------------------------------------------------------------------ */
/* GreenCardTrackerPage                                               */
/* ------------------------------------------------------------------ */
export default function GreenCardTrackerPage() {
  const [tab, setTab] = useState<"employment" | "family">("employment");
  const [selectedCat, setSelectedCat] = useState("EB-2");
  const [bulletinIndia, setBulletinIndia] = useState<VisaBulletinRow[]>([]);
  const [allCountries, setAllCountries] = useState<VisaBulletinRow[]>([]);
  const [history, setHistory] = useState<VisaBulletinRow[]>([]);
  const [loading, setLoading] = useState(true);

  const categories = tab === "employment" ? EB_CATEGORIES : FAMILY_CATEGORIES;

  // Load India final action + dates_for_filing data
  useEffect(() => {
    setLoading(true);
    Promise.all([
      getVisaBulletin("india", "final_action", tab),
      getVisaBulletin("india", "dates_for_filing", tab),
      getVisaBulletin("china", "final_action", tab),
      getVisaBulletin("china", "dates_for_filing", tab),
      getVisaBulletin("worldwide", "final_action", tab),
      getVisaBulletin("worldwide", "dates_for_filing", tab),
    ]).then(([ifa, idf, cfa, cdf, wfa, wdf]) => {
      setBulletinIndia([...ifa, ...idf]);
      setAllCountries([...ifa, ...idf, ...cfa, ...cdf, ...wfa, ...wdf]);
      setLoading(false);
    });
  }, [tab]);

  // Load chart history when selected category changes
  useEffect(() => {
    getVisaBulletinHistory(selectedCat, "india", "final_action", 12).then(setHistory);
  }, [selectedCat]);

  // Set default category when tab changes
  useEffect(() => {
    setSelectedCat(tab === "employment" ? "EB-2" : "F2A");
  }, [tab]);

  // Get current and previous month data for India
  const { current, previous, bulletinLabel } = useMemo(() => {
    const months = [...new Set(bulletinIndia.filter((r) => r.chart_type === "final_action").map((r) => `${r.bulletin_year}-${r.bulletin_month}`))]
      .sort()
      .reverse();
    const MONTH_NAMES = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const latest = months[0];
    const prev = months[1];
    let ly = 0, lm = 0;
    if (latest) {
      [ly, lm] = latest.split("-").map(Number);
    }
    return {
      current: latest ? bulletinIndia.filter((r) => r.bulletin_year === ly && r.bulletin_month === lm) : [],
      previous: prev
        ? (() => { const [py, pm] = prev.split("-").map(Number); return bulletinIndia.filter((r) => r.bulletin_year === py && r.bulletin_month === pm); })()
        : [],
      bulletinLabel: latest ? `${MONTH_NAMES[lm]} ${ly}` : "",
    };
  }, [bulletinIndia]);

  return (
    <>
      <Helmet>
        <title>Green Card Priority Dates — India Visa Bulletin Tracker | The Videshi</title>
        <meta name="description" content="Track EB-1, EB-2, EB-3, EB-5 green card priority dates for India. Historical movement charts, India vs China comparison, and monthly analysis." />
        <meta property="og:title" content="Green Card Tracker — The Videshi" />
        <meta property="og:url" content="https://www.thevideshi.com/immigration/green-card" />
              <link rel="canonical" href="https://www.thevideshi.com/immigration/green-card" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8">
        {/* Hero */}
        <section className="relative mb-8 -mx-4 px-4 py-10 md:py-14 rounded-2xl overflow-hidden bg-[#1a1a2e] border border-[#2a2a4a]/40">
          <div className="absolute top-0 right-0 w-64 h-64 bg-green-500/10 rounded-full blur-3xl" />
          <div className="relative z-10 max-w-3xl">
            <Link to="/immigration" className="text-xs text-amber-300/70 hover:text-amber-300 mb-3 inline-block">← Immigration Hub</Link>
            <h1 className="font-serif text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight text-white">
              Green Card Priority Dates
            </h1>
            <p className="text-white/60 mt-3 text-base md:text-lg">
              {bulletinLabel ? `Visa Bulletin for ${bulletinLabel}` : "Loading..."} · India Employment & Family-Based
            </p>
          </div>
        </section>

        {/* Tab toggle */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setTab("employment")}
            className={`px-5 py-2.5 text-sm font-medium rounded-full border transition-all ${
              tab === "employment"
                ? "bg-primary text-primary-foreground border-primary"
                : "border-border text-foreground/70 hover:text-primary hover:border-primary/50"
            }`}
          >
            💼 Employment-Based
          </button>
          <button
            onClick={() => setTab("family")}
            className={`px-5 py-2.5 text-sm font-medium rounded-full border transition-all ${
              tab === "family"
                ? "bg-primary text-primary-foreground border-primary"
                : "border-border text-foreground/70 hover:text-primary hover:border-primary/50"
            }`}
          >
            👨‍👩‍👧‍👦 Family-Based
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : (
          <>
            {/* Category pills */}
            <div className="flex gap-2 overflow-x-auto scrollbar-none mb-6 -mx-1 px-1">
              {categories.map((cat) => (
                <button
                  key={cat.key}
                  onClick={() => setSelectedCat(cat.key)}
                  className={`shrink-0 px-4 py-2 text-sm font-medium rounded-full border transition-all ${
                    selectedCat === cat.key
                      ? "bg-green-500 text-white border-green-500"
                      : "border-border text-foreground/70 hover:text-green-500 hover:border-green-500/50"
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Current data card */}
            {(() => {
              const curFA = current.find((r) => r.category === selectedCat && r.chart_type === "final_action");
              const curDF = current.find((r) => r.category === selectedCat && r.chart_type === "dates_for_filing");
              const prevFA = previous.find((r) => r.category === selectedCat && r.chart_type === "final_action");
              const movement = curFA && prevFA ? computeMovement(curFA.priority_date, prevFA.priority_date, curFA.status, prevFA.status) : null;
              const catInfo = categories.find((c) => c.key === selectedCat);

              return (
                <div className="bg-card border border-border rounded-xl overflow-hidden mb-8">
                  <div className="p-6">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
                      <div>
                        <h2 className="font-serif text-2xl font-bold">{selectedCat} India</h2>
                        <p className="text-sm text-foreground/50 mt-1">{catInfo?.desc}</p>
                      </div>
                      {movement && (
                        <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${
                          movement.days > 0 ? "bg-green-500/10" : movement.days < 0 ? "bg-red-500/10" : "bg-foreground/5"
                        }`}>
                          <span className={`text-lg font-bold ${movement.color}`}>{movement.arrow}</span>
                          <span className={`text-sm font-semibold ${movement.color}`}>{movement.label}</span>
                          <span className="text-xs text-foreground/40">from last month</span>
                        </div>
                      )}
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="p-5 bg-foreground/[0.02] border border-border/50 rounded-xl">
                        <p className="text-xs text-foreground/50 uppercase tracking-wider mb-2">Final Action Date</p>
                        <p className="text-3xl font-mono font-bold">{curFA ? formatPriorityDate(curFA.priority_date, curFA.status) : "—"}</p>
                        <p className="text-xs text-foreground/40 mt-1">Your priority date must be before this date</p>
                      </div>
                      <div className="p-5 bg-foreground/[0.02] border border-border/50 rounded-xl">
                        <p className="text-xs text-foreground/50 uppercase tracking-wider mb-2">Dates for Filing</p>
                        <p className="text-3xl font-mono font-bold">{curDF ? formatPriorityDate(curDF.priority_date, curDF.status) : "—"}</p>
                        <p className="text-xs text-foreground/40 mt-1">When USCIS allows this chart for AOS filing</p>
                      </div>
                    </div>
                  </div>

                  {/* Chart */}
                  <div className="border-t border-border p-6">
                    <h3 className="text-sm font-semibold mb-3 text-foreground/70">Priority Date Movement — Last {history.length} Months</h3>
                    <PriorityDateChart history={history} />
                  </div>
                </div>
              );
            })()}

            {/* Country comparison */}
            <div className="bg-card border border-border rounded-xl p-6 mb-8">
              <h3 className="font-serif text-lg font-bold mb-4">{selectedCat}: India vs China vs Worldwide</h3>
              <ComparisonTable category={selectedCat} allData={allCountries} />
            </div>

            {/* Explanation */}
            {EXPLANATIONS[selectedCat] && (
              <div className="bg-card border border-border rounded-xl p-6 mb-8">
                <h3 className="font-serif text-lg font-bold mb-3">💡 What does {selectedCat} mean?</h3>
                <p className="text-sm text-foreground/70 leading-relaxed">{EXPLANATIONS[selectedCat]}</p>
              </div>
            )}
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
