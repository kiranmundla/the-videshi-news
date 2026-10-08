import { useEffect, useMemo, useState } from "react";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import HubStrip from "@/components/homepage/HubStrip";
import SiteFooter from "@/components/SiteFooter";
import type { EventItem } from "@/lib/events";

/* ── Festival calendar (dates verified 2026-10-06) ── */
const FESTIVALS = [
  {
    name: "Sharad Navratri",
    range: "Oct 11–19, 2026",
    start: "2026-10-11",
    end: "2026-10-19",
    note: "Ghatasthapana Oct 11 · nine nights of the Goddess",
  },
  {
    name: "Dussehra · Vijayadashami",
    range: "Oct 20, 2026",
    start: "2026-10-20",
    end: "2026-10-20",
    note: "Victory of good over evil",
  },
  {
    name: "Diwali",
    range: "Nov 6–10, 2026",
    start: "2026-11-06",
    end: "2026-11-10",
    note: "Dhanteras Nov 6 · Lakshmi Puja Sun Nov 8 · Bhai Dooj Nov 10",
  },
];

/* ── Navratri 9-day guide ──
   Colors verified against 5 independent 2026 lists (jdsvaranasi.in, astroyogi.com,
   jyotishgram.com, jabalpurtoday.com, thedailyjagran.com). One source (vedictemple.in)
   uses a different weekday-based scheme — the sequence below is the widely published one.
   Color traditions vary by region and family; shown as a guide. */
const NAVRATRI_DAYS = [
  { day: 1, date: "2026-10-11", form: "Shailaputri", color: "Orange", hex: "#EA580C" },
  { day: 2, date: "2026-10-12", form: "Brahmacharini", color: "White", hex: "#F8FAFC" },
  { day: 3, date: "2026-10-13", form: "Chandraghanta", color: "Red", hex: "#DC2626" },
  { day: 4, date: "2026-10-14", form: "Kushmanda", color: "Royal Blue", hex: "#1D4ED8" },
  { day: 5, date: "2026-10-15", form: "Skandamata", color: "Yellow", hex: "#EAB308" },
  { day: 6, date: "2026-10-16", form: "Katyayani", color: "Green", hex: "#16A34A" },
  { day: 7, date: "2026-10-17", form: "Kalaratri", color: "Grey", hex: "#6B7280" },
  { day: 8, date: "2026-10-18", form: "Mahagauri", color: "Purple", hex: "#8B5CF6" },
  { day: 9, date: "2026-10-19", form: "Siddhidatri", color: "Peacock Green", hex: "#0F766E" },
];

const EVENT_KEYWORDS = ["diwali", "navratri", "garba", "dandiya", "deepavali"];

// US states + DC — the hub serves the US diaspora; filters out stray non-US
// rows (e.g. Canadian provinces) that occasionally land in the events feed.
const US_STATES = new Set([
  "AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN","IA",
  "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM",
  "NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA",
  "WV","WI","WY",
]);

type Tab = "calendar" | "navratri" | "events";

/* ── Helpers ── */
function todayStr(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function fmtDate(dateStr: string): string {
  const d = new Date(dateStr + "T12:00:00");
  return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
}

function decodeEntities(text: string): string {
  const el = document.createElement("textarea");
  el.innerHTML = text;
  return el.value;
}

function daysUntil(dateStr: string): number {
  const a = new Date(todayStr() + "T12:00:00").getTime();
  const b = new Date(dateStr + "T12:00:00").getTime();
  return Math.round((b - a) / 86400000);
}

/* ── Section header (Explore-hub visual language) ── */
function SectionHead({ title, sub }: { title: string; sub?: string }) {
  return (
    <div
      className="flex items-center justify-between mb-4 pb-2.5"
      style={{ borderBottom: "3px solid #D4A843" }}
    >
      <h2
        className="text-[13px] font-bold tracking-[2px] uppercase"
        style={{ color: "#0B1D3A" }}
      >
        {title}
      </h2>
      {sub && <span className="text-[11px] text-muted-foreground">{sub}</span>}
    </div>
  );
}

export default function FestivalsPage() {
  const [tab, setTab] = useState<Tab>("calendar");
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [stateSel, setStateSel] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data/events.json")
      .then((r) => (r.ok ? r.json() : []))
      .then((all: EventItem[]) => {
        const today = todayStr();
        const filtered = all
          .filter((e) => {
            if (!e.date || e.date < today) return false;
            if (!e.ticket_url) return false; // editorial rule: every listing needs a ticket link
            if (!US_STATES.has((e.state || "").toUpperCase())) return false; // US diaspora hub
            const hay = `${e.title} ${e.description || ""} ${e.long_description || ""}`.toLowerCase();
            return EVENT_KEYWORDS.some((k) => hay.includes(k));
          })
          .sort((a, b) => a.date.localeCompare(b.date));
        setEvents(filtered);
        setLoaded(true);
      })
      .catch(() => setLoaded(true));
  }, []);

  const byState = useMemo(() => {
    const m = new Map<string, EventItem[]>();
    for (const e of events) {
      const s = e.state || "Other";
      if (!m.has(s)) m.set(s, []);
      m.get(s)!.push(e);
    }
    return [...m.entries()].sort((a, b) => b[1].length - a[1].length);
  }, [events]);

  const activeState = stateSel ?? byState[0]?.[0] ?? null;
  const stateEvents = byState.find(([s]) => s === activeState)?.[1] ?? [];

  const today = todayStr();
  const nextFestival = FESTIVALS.find((f) => f.end >= today);

  const tabs: { key: Tab; label: string }[] = [
    { key: "calendar", label: "Calendar" },
    { key: "navratri", label: "Navratri Guide" },
    { key: "events", label: "Celebrate Near You" },
  ];

  return (
    <>
      <Helmet>
        <title>Festivals — The Videshi</title>
        <meta
          name="description"
          content="Festival dates, the 9-day Navratri color guide, and Diwali and Navratri celebrations near you across the US."
        />
        <link rel="canonical" href="https://www.thevideshi.com/festivals" />
      </Helmet>

      <Masthead />
      <HubStrip />

      <style>{`
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
      `}</style>

      <main className="container flex-1 pt-8 md:pt-10 pb-16">
        <div className="mb-6">
          <h1
            className="font-serif font-black tracking-tight text-foreground leading-none text-[1.75rem] md:text-[2.5rem]"
          >
            Festivals
          </h1>
          <p className="text-muted-foreground text-sm mt-2">
            Festival dates, the 9-day Navratri guide, and celebrations near you.
          </p>
        </div>

        {/* Tabs — Explore-hub pattern */}
        <div className="flex gap-2 mb-6 overflow-x-auto scrollbar-hide" role="tablist" aria-label="Festival sections">
          {tabs.map((t) => (
            <button
              key={t.key}
              role="tab"
              aria-selected={tab === t.key}
              onClick={() => setTab(t.key)}
              className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-colors border whitespace-nowrap ${
                tab === t.key
                  ? "bg-[#0B1D3A] text-white border-[#0B1D3A]"
                  : "bg-transparent text-muted-foreground border-border hover:border-[#0B1D3A]/40"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* ── Tab 1: Festival calendar ── */}
        {tab === "calendar" && (
          <section>
            <SectionHead title="Festival Calendar" sub="Fall 2026" />
            <div className="flex gap-3 overflow-x-auto scrollbar-hide pb-1 -mx-1 px-1">
              {FESTIVALS.map((f) => {
                const isPast = f.end < today;
                const isNow = f.start <= today && f.end >= today;
                const isNext = !isPast && !isNow && nextFestival?.name === f.name;
                const du = daysUntil(f.start);
                return (
                  <div
                    key={f.name}
                    className="min-w-[240px] max-w-[280px] flex-1 bg-card border border-border rounded-lg p-4 flex flex-col"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[11px] font-bold tracking-[1.5px] uppercase text-muted-foreground">
                        {f.range}
                      </span>
                      {isNow ? (
                        <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-green-600 text-white">
                          Happening now
                        </span>
                      ) : isNext ? (
                        <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#D4A843] text-[#0B1D3A]">
                          Next up
                        </span>
                      ) : isPast ? (
                        <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-muted text-muted-foreground">
                          Passed
                        </span>
                      ) : (
                        <span className="text-[11px] font-semibold text-muted-foreground">
                          {du === 1 ? "Tomorrow" : `In ${du} days`}
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-bold" style={{ color: "#0B1D3A" }}>
                      {f.name}
                    </h3>
                    <p className="text-[13px] text-muted-foreground mt-1">{f.note}</p>
                    {f.name === "Sharad Navratri" && !isPast && (
                      <button
                        onClick={() => setTab("navratri")}
                        className="mt-3 text-[13px] font-semibold text-left hover:underline"
                        style={{ color: "#A32D2F" }}
                      >
                        See the 9-day color guide →
                      </button>
                    )}
                    {f.name === "Diwali" && !isPast && (
                      <button
                        onClick={() => setTab("events")}
                        className="mt-3 text-[13px] font-semibold text-left hover:underline"
                        style={{ color: "#A32D2F" }}
                      >
                        Find celebrations near you →
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* ── Tab 2: Navratri 9-day guide ── */}
        {tab === "navratri" && (
          <section>
            <SectionHead title="Navratri 9-Day Guide" sub="Oct 11–19, 2026" />
            <p className="text-[13px] text-muted-foreground mb-4">
              Each night honors one form of Goddess Durga — wear the day's color to join in.
            </p>
            <div className="grid grid-cols-3 gap-2 md:gap-3">
              {NAVRATRI_DAYS.map((d) => {
                const isToday = d.date === today;
                return (
                  <div
                    key={d.day}
                    className={`bg-card border rounded-lg overflow-hidden ${
                      isToday ? "border-[#D4A843] ring-2 ring-[#D4A843]/50" : "border-border"
                    }`}
                  >
                    <div className="h-1.5" style={{ backgroundColor: d.hex }} />
                    <div className="p-2.5 md:p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-bold tracking-[1px] uppercase text-muted-foreground">
                          Day {d.day}
                        </span>
                        {isToday && (
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-[#D4A843] text-[#0B1D3A]">
                            Today
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-muted-foreground mb-0.5">
                        {fmtDate(d.date)}
                      </div>
                      <div className="text-[13px] md:text-sm font-bold leading-tight" style={{ color: "#0B1D3A" }}>
                        {d.form}
                      </div>
                      <div className="flex items-center gap-1.5 mt-1.5">
                        <span
                          className="inline-block w-3 h-3 rounded-full border border-black/20"
                          style={{ backgroundColor: d.hex }}
                        />
                        <span className="text-[11px] font-medium">{d.color}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            <p className="text-[11px] text-muted-foreground mt-3">
              Color traditions vary by region and family — treat this as a guide, not a rule.
            </p>
          </section>
        )}

        {/* ── Tab 3: Celebrate near you ── */}
        {tab === "events" && (
          <section>
            <SectionHead title="Celebrate Near You" sub="Diwali · Navratri · Garba" />
            {!loaded ? (
              <p className="text-sm text-muted-foreground">Loading celebrations…</p>
            ) : events.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No upcoming festival celebrations found. Check back soon.
              </p>
            ) : (
              <>
                <div className="flex gap-2 mb-4 overflow-x-auto scrollbar-hide" role="tablist" aria-label="States">
                  {byState.map(([s, list]) => (
                    <button
                      key={s}
                      role="tab"
                      aria-selected={activeState === s}
                      onClick={() => setStateSel(s)}
                      className={`px-3 py-1 rounded-full text-[13px] font-semibold transition-colors border whitespace-nowrap ${
                        activeState === s
                          ? "bg-[#0B1D3A] text-white border-[#0B1D3A]"
                          : "bg-transparent text-muted-foreground border-border hover:border-[#0B1D3A]/40"
                      }`}
                    >
                      {s} · {list.length}
                    </button>
                  ))}
                </div>

                <div className="flex flex-col gap-2.5">
                  {stateEvents.map((e) => {
                    const expanded = expandedId === e.id;
                    const title = decodeEntities(e.title);
                    return (
                      <article
                        key={e.id}
                        className="bg-card border border-border rounded-lg overflow-hidden"
                      >
                        <button
                          onClick={() => setExpandedId(expanded ? null : e.id)}
                          aria-expanded={expanded}
                          className="w-full flex items-center gap-3 p-3 text-left hover:bg-muted/40 transition-colors"
                        >
                          <div className="flex-shrink-0 w-12 text-center">
                            <div className="text-[10px] font-bold uppercase text-muted-foreground">
                              {fmtDate(e.date).split(", ")[0]}
                            </div>
                            <div className="text-sm font-bold" style={{ color: "#A32D2F" }}>
                              {fmtDate(e.date).split(", ")[1]}
                            </div>
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="text-[14px] font-semibold leading-snug line-clamp-2">
                              {title}
                            </h3>
                            <div className="text-[12px] text-muted-foreground mt-0.5 truncate">
                              {[e.venue_name, e.city].filter(Boolean).join(" · ")}
                              {e.price_range ? ` · ${e.price_range}` : ""}
                            </div>
                          </div>
                          <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            className={`w-4 h-4 flex-shrink-0 text-muted-foreground transition-transform ${expanded ? "rotate-180" : ""}`}
                          >
                            <path d="M6 9l6 6 6-6" />
                          </svg>
                        </button>
                        {expanded && (
                          <div className="px-3 pb-3 pt-1 border-t border-border/60">
                            {e.description && (
                              <p className="text-[13px] text-muted-foreground mt-2 leading-relaxed">
                                {decodeEntities(e.description)}
                              </p>
                            )}
                            <div className="flex items-center justify-between gap-3 mt-3">
                              <div className="text-[11px] text-muted-foreground">
                                {e.organizer ? `By ${decodeEntities(e.organizer)}` : ""}
                                {e.source ? ` · via ${e.source}` : ""}
                              </div>
                              {e.ticket_url && (
                                <a
                                  href={e.ticket_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex-shrink-0 px-4 py-1.5 rounded-full text-[13px] font-bold text-white transition-opacity hover:opacity-90"
                                  style={{ backgroundColor: "#A32D2F" }}
                                >
                                  Get tickets
                                </a>
                              )}
                            </div>
                          </div>
                        )}
                      </article>
                    );
                  })}
                </div>
                <p className="text-[11px] text-muted-foreground mt-4">
                  Every listing includes a ticket or registration link.{" "}
                  <a href="/events" className="underline hover:text-foreground">
                    Browse all events →
                  </a>
                </p>
              </>
            )}
          </section>
        )}
      </main>

      <SiteFooter />
    </>
  );
}
