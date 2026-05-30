import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { ChevronRight, ExternalLink } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  VisaBulletinRow,
  ConsulateWaitRow,
  ProcessingTimeRow,
  H1BDataRow,
  getVisaBulletin,
  getConsulateWaitTimes,
  getProcessingTimes,
  getH1BData,
  getImmigrationNews,
  formatPriorityDate,
  formatWaitMonths,
  waitColor,
  waitBg,
  computeMovement,
  INDIA_CONSULATES,
  CONSULATE_DISPLAY,
  EB_CATEGORIES,
  GUIDE_PLACEHOLDERS,
  GUIDE_CATEGORIES,
  KEY_FORMS,
} from "@/lib/immigration";

const MONTH_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
function compactDate(dateStr: string | null, status: string): string {
  if (status === "current") return "Current";
  if (status === "unavailable") return "Unavail.";
  if (!dateStr) return "N/A";
  const d = new Date(dateStr + "T00:00:00");
  return `${MONTH_SHORT[d.getMonth()]} '${String(d.getFullYear()).slice(2)}`;
}

/* ------------------------------------------------------------------ */
/* Green Card Tracker Card                                            */
/* ------------------------------------------------------------------ */
function GreenCardCard({ data }: { data: VisaBulletinRow[] }) {
  // Get latest month
  const months = [...new Set(data.map((r) => `${r.bulletin_year}-${r.bulletin_month}`))].sort().reverse();
  const latest = months[0];
  const prev = months[1];
  if (!latest) return null;

  const [latestYear, latestMonth] = latest.split("-").map(Number);
  const MONTH_NAMES = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const bulletinLabel = `${MONTH_NAMES[latestMonth]} ${latestYear}`;

  const categories = ["EB-1", "EB-2", "EB-3"];

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-border bg-green-500/5">
        <div className="flex items-center gap-2">
          <span className="text-lg">🟢</span>
          <h3 className="font-serif font-bold text-[15px]">Green Card Priority Dates</h3>
        </div>
        <span className="text-[11px] text-foreground/50 whitespace-nowrap">Visa Bulletin: {bulletinLabel}</span>
      </div>
      <div className="divide-y divide-border">
        {categories.map((cat) => {
          const cur = data.find((r) => r.category === cat && r.bulletin_year === latestYear && r.bulletin_month === latestMonth);
          const prv = prev
            ? data.find((r) => {
                const [py, pm] = prev.split("-").map(Number);
                return r.category === cat && r.bulletin_year === py && r.bulletin_month === pm;
              })
            : null;
          if (!cur) return null;
          const movement = prv ? computeMovement(cur.priority_date, prv.priority_date, cur.status, prv.status) : null;
          return (
            <div key={cat} className="flex items-center justify-between px-4 py-2.5 hover:bg-foreground/[0.02] transition-colors">
              <div className="min-w-0">
                <span className="font-semibold text-sm">{cat} India</span>
                <p className="text-[11px] text-foreground/40 leading-tight">
                  {EB_CATEGORIES.find((e) => e.key === cat)?.desc?.split("(")[0]?.trim()}
                </p>
              </div>
              <div className="text-right flex items-center gap-2 flex-shrink-0">
                <span className="font-mono text-sm font-semibold whitespace-nowrap">{compactDate(cur.priority_date, cur.status)}</span>
                {movement && (
                  <span className={`text-xs font-semibold ${movement.color} flex items-center gap-0.5`}>
                    {movement.arrow} {movement.label}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
      <Link to="/immigration/green-card" className="flex items-center justify-center gap-1 px-4 py-2 text-sm text-primary font-medium border-t border-border hover:bg-primary/5 transition-colors">
        View full tracker with history <ChevronRight className="h-4 w-4" />
      </Link>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Consulate Wait Times Card                                          */
/* ------------------------------------------------------------------ */
function ConsulateCard({ data }: { data: ConsulateWaitRow[] }) {
  // Group by consulate, take latest entry per visa_type
  const grouped: Record<string, Record<string, ConsulateWaitRow>> = {};
  for (const row of data) {
    if (!INDIA_CONSULATES.includes(row.consulate as any)) continue;
    if (!grouped[row.consulate]) grouped[row.consulate] = {};
    if (!grouped[row.consulate][row.visa_type]) grouped[row.consulate][row.visa_type] = row;
  }

  const consulates = INDIA_CONSULATES.filter((c) => grouped[c]);
  // Sort by B1/B2 next_available ascending (fastest first)
  consulates.sort((a, b) => {
    const aWait = grouped[a]?.["B1B2"]?.next_available_months ?? 99;
    const bWait = grouped[b]?.["B1B2"]?.next_available_months ?? 99;
    return aWait - bWait;
  });

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-border bg-blue-500/5">
        <div className="flex items-center gap-2">
          <span className="text-lg">🏛️</span>
          <h3 className="font-serif font-bold text-[15px]">US Consulate Wait Times — India</h3>
        </div>
      </div>
      <div className="divide-y divide-border">
        {consulates.map((c) => {
          const b1b2 = grouped[c]?.["B1B2"];
          const hlop = grouped[c]?.["H_L_O_P_Q"];
          const b1Val = b1b2?.next_available_months ?? b1b2?.avg_wait_months ?? null;
          const hlVal = hlop?.next_available_months ?? null;
          return (
            <div key={c} className="flex items-center justify-between px-4 py-2 hover:bg-foreground/[0.02] transition-colors">
              <div className="flex items-center gap-2.5">
                <div className={`w-2 h-2 rounded-full ${b1Val === null ? "bg-gray-400" : b1Val < 2 ? "bg-green-500" : b1Val < 5 ? "bg-yellow-500" : b1Val < 8 ? "bg-orange-500" : "bg-red-500"}`} />
                <span className="font-semibold text-sm">{CONSULATE_DISPLAY[c] || c}</span>
              </div>
              <div className="flex items-center gap-5 text-sm">
                <div className="text-right">
                  <span className={`font-mono font-semibold ${waitColor(b1Val)}`}>{formatWaitMonths(b1Val)}</span>
                  <p className="text-[10px] text-foreground/40 leading-tight">B1/B2</p>
                </div>
                <div className="text-right">
                  <span className={`font-mono font-semibold ${waitColor(hlVal)}`}>{formatWaitMonths(hlVal)}</span>
                  <p className="text-[10px] text-foreground/40 leading-tight">H/L/O/P</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <Link to="/immigration/consulate-wait-times" className="flex items-center justify-center gap-1 px-4 py-2 text-sm text-primary font-medium border-t border-border hover:bg-primary/5 transition-colors">
        Compare all consulates <ChevronRight className="h-4 w-4" />
      </Link>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* H-1B Season Card                                                   */
/* ------------------------------------------------------------------ */
function H1BCard({ data }: { data: H1BDataRow[] }) {
  const fy = [...new Set(data.map((d) => d.fiscal_year))].sort().reverse();
  const latestFY = fy[0];
  if (!latestFY) return null;

  const get = (fy: number, metric: string) => data.find((d) => d.fiscal_year === fy && d.metric === metric)?.value || "—";

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-border bg-purple-500/5">
        <div className="flex items-center gap-2">
          <span className="text-lg">🎰</span>
          <h3 className="font-serif font-bold text-[15px]">H-1B Season — FY{latestFY}</h3>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-0 divide-x divide-border">
        <div className="px-4 py-3 text-center">
          <p className="text-xl font-bold text-foreground">{get(latestFY, "total_registrations")}</p>
          <p className="text-[11px] text-foreground/50 mt-0.5">Registrations</p>
        </div>
        <div className="px-4 py-3 text-center">
          <p className="text-xl font-bold text-purple-500">{get(latestFY, "selection_rate")}</p>
          <p className="text-[11px] text-foreground/50 mt-0.5">Selection Rate</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-0 divide-x divide-border border-t border-border">
        <div className="px-4 py-3 text-center">
          <p className="text-xl font-bold text-amber-500">{get(latestFY, "india_pct")}</p>
          <p className="text-[11px] text-foreground/50 mt-0.5">Indian Nationals</p>
        </div>
        <div className="px-4 py-3 text-center">
          <p className="text-xl font-bold text-foreground">{get(latestFY, "masters_pct")}</p>
          <p className="text-[11px] text-foreground/50 mt-0.5">US Master's+</p>
        </div>
      </div>
      <Link to="/immigration/h1b" className="flex items-center justify-center gap-1 px-4 py-2 text-sm text-primary font-medium border-t border-border hover:bg-primary/5 transition-colors">
        H-1B Hub <ChevronRight className="h-4 w-4" />
      </Link>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Processing Times Card                                              */
/* ------------------------------------------------------------------ */
function ProcessingCard({ data }: { data: ProcessingTimeRow[] }) {
  const keyForms = ["I-140", "I-485", "I-765", "N-400"];
  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-border bg-amber-500/5">
        <div className="flex items-center gap-2">
          <span className="text-lg">⏱️</span>
          <h3 className="font-serif font-bold text-[15px]">USCIS Processing Times</h3>
        </div>
      </div>
      <div className="divide-y divide-border">
        {keyForms.map((form) => {
          const rows = data.filter((r) => r.form_number === form);
          if (rows.length === 0) return null;
          const low = Math.min(...rows.filter((r) => r.estimated_range_low != null).map((r) => r.estimated_range_low!));
          const high = Math.max(...rows.filter((r) => r.estimated_range_high != null).map((r) => r.estimated_range_high!));
          const info = KEY_FORMS.find((f) => f.number === form);
          return (
            <div key={form} className="flex items-center justify-between px-4 py-2.5 hover:bg-foreground/[0.02] transition-colors">
              <div>
                <span className="font-semibold text-sm">{form}</span>
                <p className="text-[11px] text-foreground/40 leading-tight">{info?.desc}</p>
              </div>
              <span className="font-mono text-sm font-semibold text-foreground/80">
                {isFinite(low) && isFinite(high) ? `${low}–${high} mo` : "—"}
              </span>
            </div>
          );
        })}
      </div>
      <Link to="/immigration/processing-times" className="flex items-center justify-center gap-1 px-4 py-2 text-sm text-primary font-medium border-t border-border hover:bg-primary/5 transition-colors">
        All processing times <ChevronRight className="h-4 w-4" />
      </Link>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Immigration Page                                                   */
/* ------------------------------------------------------------------ */
export default function ImmigrationPage() {
  const [bulletin, setBulletin] = useState<VisaBulletinRow[]>([]);
  const [waits, setWaits] = useState<ConsulateWaitRow[]>([]);
  const [processing, setProcessing] = useState<ProcessingTimeRow[]>([]);
  const [h1b, setH1B] = useState<H1BDataRow[]>([]);
  const [news, setNews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getVisaBulletin("india", "final_action", "employment"),
      getConsulateWaitTimes([...INDIA_CONSULATES]),
      getProcessingTimes(),
      getH1BData(),
      getImmigrationNews(8),
    ]).then(([b, w, p, h, n]) => {
      setBulletin(b);
      setWaits(w);
      setProcessing(p);
      setH1B(h);
      setNews(n);
      setLoading(false);
    });
  }, []);

  return (
    <>
      <Helmet>
        <title>Immigration Hub — Visa Tracker, Green Card Dates, H-1B | The Videshi</title>
        <meta name="description" content="The go-to immigration dashboard for Indian Americans. Track green card priority dates, US consulate wait times, H-1B lottery stats, USCIS processing times, and get expert guides." />
        <meta property="og:title" content="Immigration Hub — The Videshi" />
        <meta property="og:description" content="Track green card priority dates, consulate wait times, H-1B lottery, and USCIS processing times. Your Indian American immigration dashboard." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://www.thevideshi.com/immigration" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8">
        {/* ── Hero ─────────────────────────────────────────── */}
        <section className="relative mb-10 -mx-4 px-4 py-12 md:py-16 rounded-2xl overflow-hidden bg-[#1a1a2e] border border-[#2a2a4a]/40">
          <div className="absolute inset-0 opacity-[0.06]" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")" }} />
          <div className="absolute top-0 right-0 w-64 h-64 bg-green-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-amber-500/8 rounded-full blur-3xl" />

          <div className="relative z-10 max-w-3xl">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs font-bold uppercase tracking-widest text-amber-300 bg-amber-500/15 px-3 py-1 rounded-full">
                🗽 Immigration Hub
              </span>
            </div>
            <h1 className="font-serif text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight leading-[1.1] text-white">
              Your Immigration<br />
              <span className="text-green-400">Dashboard.</span>
            </h1>
            <p className="text-white/70 mt-4 text-lg md:text-xl max-w-2xl leading-relaxed">
              Track green card priority dates, consulate wait times, H-1B lottery stats, and USCIS processing times — all in one place, for the Indian diaspora.
            </p>
          </div>
        </section>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : (
          <>
            {/* ── Immigration News (horizontal scroll) ─────────── */}
            {news.length > 0 && (
              <section className="mb-12">
                <div className="flex items-center justify-between mb-5">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">📰</span>
                    <h2 className="font-serif text-xl font-bold">Latest Immigration News</h2>
                  </div>
                  <Link to="/immigration" className="text-sm text-primary hover:text-primary/80 font-medium flex items-center gap-1">
                    More <ChevronRight className="h-4 w-4" />
                  </Link>
                </div>
                <div
                  className="flex gap-4 overflow-x-auto pb-4"
                  style={{
                    scrollSnapType: "x mandatory",
                    WebkitOverflowScrolling: "touch",
                    scrollbarWidth: "none",
                    msOverflowStyle: "none",
                  } as React.CSSProperties}
                >
                  <style>{`.imm-news-strip::-webkit-scrollbar { display: none; }`}</style>
                  {news.map((article: any) => (
                    <Link
                      key={article.id}
                      to={`/articles/${article.slug}`}
                      className="block group flex-shrink-0"
                      style={{ width: "280px", scrollSnapAlign: "start" }}
                    >
                      <article className="bg-card border border-border rounded-xl overflow-hidden hover:border-primary/40 transition-all duration-200 hover:shadow-lg h-full">
                        {article.image_url && (
                          <div className="h-36 overflow-hidden">
                            <img
                              src={article.image_url}
                              alt=""
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                              loading="lazy"
                            />
                          </div>
                        )}
                        <div className="p-4">
                          <div className="flex items-center gap-2 mb-1.5">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-primary">Immigration</span>
                            <span className="text-[10px] text-foreground/40">
                              {new Date(article.published_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                            </span>
                          </div>
                          <h3 className="font-semibold text-sm group-hover:text-primary transition-colors line-clamp-2">{article.title}</h3>
                          {article.excerpt && (
                            <p className="text-xs text-foreground/50 mt-1 line-clamp-2">{article.excerpt}</p>
                          )}
                        </div>
                      </article>
                    </Link>
                  ))}
                </div>
              </section>
            )}

            {/* ── Visa Appointment Tracker Banner ────────────── */}
            <Link
              to="/immigration/visas"
              className="block mb-8 rounded-xl overflow-hidden border border-green-500/20 bg-gradient-to-r from-[#1a1a2e] to-[#1a2e1a] hover:from-[#1e1e35] hover:to-[#1e351e] transition-all duration-300 shadow-lg shadow-green-500/5 hover:shadow-green-500/10 group"
            >
              <div className="flex items-center gap-4 px-5 py-5">
                <span className="text-3xl flex-shrink-0">🛂</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-green-400 bg-green-500/15 px-2 py-0.5 rounded-full">
                      New
                    </span>
                  </div>
                  <p className="font-serif text-lg md:text-xl font-bold text-white leading-tight">
                    US Visa Appointment Tracker
                  </p>
                  <p className="text-sm text-white/60 mt-1">
                    Community-powered slot intelligence for India's 5 consulates — see sightings, report open slots, help each other
                  </p>
                </div>
                <span className="text-white/40 text-2xl shrink-0 group-hover:text-green-400 group-hover:translate-x-1 transition-all">→</span>
              </div>
            </Link>

            {/* ── Data Trackers ────────────────────────────────── */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-12">
              <GreenCardCard data={bulletin} />
              <ConsulateCard data={waits} />
              <H1BCard data={h1b} />
              <ProcessingCard data={processing} />
            </div>

            {/* ── Quick Links: Guides ─────────────────────────── */}
            <section className="mb-12">
              <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-2">
                  <span className="text-xl">📚</span>
                  <h2 className="font-serif text-xl font-bold">Immigration Guides</h2>
                </div>
                <Link to="/immigration/guides" className="text-sm text-primary hover:text-primary/80 font-medium flex items-center gap-1">
                  View all guides <ChevronRight className="h-4 w-4" />
                </Link>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {GUIDE_PLACEHOLDERS.slice(0, 9).map((g) => {
                  const catInfo = GUIDE_CATEGORIES.find((c) => c.key === g.category);
                  return (
                    <Link key={g.slug} to={`/immigration/guides/${g.slug}`} className="block group">
                      <div className="flex items-start gap-3 p-4 bg-card border border-border rounded-xl hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5 h-full">
                        <span className="text-2xl flex-shrink-0 mt-0.5">{g.emoji}</span>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-sm group-hover:text-primary transition-colors line-clamp-2">{g.title}</h3>
                          <span className="inline-block mt-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-foreground/5 text-foreground/50">
                            {catInfo?.label}
                          </span>
                        </div>
                        <ChevronRight className="h-4 w-4 text-foreground/20 group-hover:text-primary transition-colors flex-shrink-0 mt-1" />
                      </div>
                    </Link>
                  );
                })}
              </div>
            </section>

            {/* ── Find a Lawyer CTA ──────────────────────────── */}
            <section className="mb-12">
              <div className="relative p-8 bg-[#1a1a2e] rounded-2xl border border-[#2a2a4a]/40 text-center overflow-hidden">
                <div className="absolute top-0 right-0 w-40 h-40 bg-amber-500/10 rounded-full blur-3xl" />
                <div className="relative z-10">
                  <span className="text-4xl mb-3 block">⚖️</span>
                  <h3 className="font-serif text-2xl font-bold text-white mb-2">Find an Immigration Lawyer</h3>
                  <p className="text-white/60 text-sm mb-5 max-w-lg mx-auto">
                    Browse our directory of immigration attorneys serving the Indian community across the US.
                  </p>
                  <Link
                    to="/directory?category=Attorneys+%26+Immigration"
                    className="inline-flex items-center gap-2 bg-amber-500 text-black font-semibold text-sm py-2.5 px-6 rounded-full hover:bg-amber-400 transition-colors"
                  >
                    Browse Attorneys <ExternalLink className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            </section>
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
