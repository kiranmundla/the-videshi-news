import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import HubStrip from "@/components/homepage/HubStrip";
import SiteFooter from "@/components/SiteFooter";
import type { EventItem } from "@/lib/events";
import EventCard from "@/components/EventCard";
import { useHubLocation, haversineMiles, METRO_PICKER, type HubLocation } from "@/hooks/useHubLocation";
import { DEADLINES } from "@/data/deadlines";

/* ── Festival spotlight data (dates verified 2026-10-06) ── */
const FESTIVALS = [
  {
    name: "Sharad Navratri",
    range: "Oct 11–19, 2026",
    start: "2026-10-11",
    end: "2026-10-19",
    note: "Nine nights of the Goddess — garba & dandiya every night",
  },
  {
    name: "Dussehra · Vijayadashami",
    range: "Oct 20, 2026",
    start: "2026-10-20",
    end: "2026-10-20",
    note: "Victory of good over evil — Ravan Dahan melas",
  },
  {
    name: "Diwali",
    range: "Nov 6–10, 2026",
    start: "2026-11-06",
    end: "2026-11-10",
    note: "Dhanteras Nov 6 · Lakshmi Puja Sun Nov 8 · Bhai Dooj Nov 10",
  },
];

const US_STATES = new Set([
  "AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN","IA",
  "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM",
  "NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA",
  "WV","WI","WY",
]);

const CATEGORY_LABELS: Record<string, string> = {
  Music: "Music",
  Dance: "Dance",
  Comedy: "Comedy",
  Food: "Food",
  Festival: "Festival",
  Cultural: "Cultural",
  Community: "Community",
  Entertainment: "Entertainment",
  Sports: "Sports",
};

/* ── Helpers ── */
function todayStr(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function toStr(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function fmtDate(dateStr: string): string {
  const d = new Date(dateStr + "T12:00:00");
  return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
}

function fmtLong(dateStr: string): string {
  const d = new Date(dateStr + "T12:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function daysUntil(dateStr: string): number {
  const a = new Date(todayStr() + "T12:00:00").getTime();
  const b = new Date(dateStr + "T12:00:00").getTime();
  return Math.round((b - a) / 86400000);
}

/** Friday–Sunday of the *upcoming* weekend (rest of it if already in it). */
function weekendRange(): [string, string] {
  const now = new Date();
  const day = now.getDay(); // 0=Sun … 5=Fri, 6=Sat
  const fri = new Date(now);
  if (day >= 1 && day <= 4) {
    // Mon–Thu: jump forward to the upcoming Friday
    fri.setDate(now.getDate() + (5 - day));
  } else {
    // Fri/Sat/Sun: Friday of the weekend we're in
    const daysSinceFri = (day + 7 - 5) % 7;
    fri.setDate(now.getDate() - daysSinceFri);
  }
  const sun = new Date(fri);
  sun.setDate(fri.getDate() + 2);
  return [toStr(fri), toStr(sun)];
}

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

function distanceFor(e: EventItem, loc: HubLocation | null): number | null {
  if (!loc || e.latitude == null || e.longitude == null) return null;
  return haversineMiles(loc.lat, loc.lon, e.latitude, e.longitude);
}

/* ── Location setup ── */
function LocationSetup({
  onDone,
}: {
  onDone: (loc: HubLocation) => void;
}) {
  const [geoError, setGeoError] = useState<string | null>(null);
  const [geoLoading, setGeoLoading] = useState(false);

  const useMyLocation = () => {
    if (!navigator.geolocation) {
      setGeoError("Geolocation isn't available in this browser — pick your metro below.");
      return;
    }
    setGeoLoading(true);
    setGeoError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setGeoLoading(false);
        onDone({
          city: "Current location",
          state: "",
          lat: pos.coords.latitude,
          lon: pos.coords.longitude,
          label: "Current location",
        });
      },
      () => {
        setGeoLoading(false);
        setGeoError("Location access was denied — pick your metro below instead.");
      },
      { enableHighAccuracy: false, timeout: 8000 },
    );
  };

  return (
    <div className="bg-card border border-border rounded-lg p-4 md:p-5 mb-6">
      <h2 className="text-base font-bold" style={{ color: "#0B1D3A" }}>
        Where are you?
      </h2>
      <p className="text-[13px] text-muted-foreground mt-1 mb-4">
        Set your location once — Your Hub then ranks the weekend, festivals and
        everything else by what's near you. Stored only in this browser.
      </p>
      <button
        onClick={useMyLocation}
        disabled={geoLoading}
        className="w-full sm:w-auto px-5 py-2.5 rounded-full text-sm font-bold text-white transition-opacity hover:opacity-90 disabled:opacity-60"
        style={{ backgroundColor: "#0B1D3A" }}
      >
        {geoLoading ? "Locating…" : "Use my location"}
      </button>
      {geoError && (
        <p className="text-[12px] mt-2" style={{ color: "#A32D2F" }}>
          {geoError}
        </p>
      )}
      <div className="flex items-center gap-3 my-4">
        <div className="flex-1 border-t border-border" />
        <span className="text-[11px] uppercase tracking-wider text-muted-foreground">or pick your metro</span>
        <div className="flex-1 border-t border-border" />
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
        {METRO_PICKER.map((m) => (
          <button
            key={`${m.city},${m.state}`}
            onClick={() =>
              onDone({
                city: m.city,
                state: m.state,
                lat: m.lat,
                lon: m.lon,
                label: `${m.city}, ${m.state}`,
              })
            }
            className="px-3 py-2 rounded-lg border border-border text-[13px] font-medium text-left hover:border-[#0B1D3A]/50 hover:bg-muted/40 transition-colors"
          >
            {m.city}, {m.state}
          </button>
        ))}
      </div>
    </div>
  );
}

export default function YourHubPage() {
  const { location, setLocation, clearLocation, isSet } = useHubLocation();
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [catSel, setCatSel] = useState<string | null>(null);
  const [geoTried, setGeoTried] = useState(false);

  /* Auto-request geolocation on page land (like the events page).
     If the user declines, the manual setup panel below is the fallback. */
  useEffect(() => {
    if (isSet || geoTried || !navigator.geolocation) return;
    setGeoTried(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocation({
          city: "",
          state: "",
          lat: pos.coords.latitude,
          lon: pos.coords.longitude,
          label: "Near You",
        });
      },
      () => {
        /* denied — LocationSetup panel handles it */
      },
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 },
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSet, geoTried]);

  useEffect(() => {
    fetch("/data/events.json")
      .then((r) => (r.ok ? r.json() : []))
      .then((all: EventItem[]) => {
        const today = todayStr();
        const filtered = all.filter((e) => {
          if (!e.date || e.date < today) return false;
          if (!e.ticket_url) return false;
          if (!US_STATES.has((e.state || "").toUpperCase())) return false;
          return true;
        });
        setEvents(filtered);
        setLoaded(true);
      })
      .catch(() => setLoaded(true));
  }, []);

  const today = todayStr();
  const [friStr, sunStr] = weekendRange();

  /* This weekend's events */
  const weekendEvents = useMemo(() => {
    let list = events.filter((e) => e.date >= friStr && e.date <= sunStr && e.date >= today);
    if (catSel) list = list.filter((e) => e.category === catSel);
    if (location) {
      list = [...list].sort((a, b) => {
        const da = distanceFor(a, location) ?? Infinity;
        const db = distanceFor(b, location) ?? Infinity;
        return da - db || a.date.localeCompare(b.date);
      });
    } else {
      list = [...list].sort((a, b) => a.date.localeCompare(b.date));
    }
    return list;
  }, [events, friStr, sunStr, today, catSel, location]);

  const weekendCats = useMemo(() => {
    const counts = new Map<string, number>();
    for (const e of events.filter((e) => e.date >= friStr && e.date <= sunStr && e.date >= today)) {
      const c = e.category || "Other";
      if (CATEGORY_LABELS[c]) counts.set(c, (counts.get(c) ?? 0) + 1);
    }
    return [...counts.entries()].sort((a, b) => b[1] - a[1]);
  }, [events, friStr, sunStr, today]);

  /* Deadlines */
  const upcomingDeadlines = useMemo(
    () => DEADLINES.filter((d) => d.date >= today).sort((a, b) => a.date.localeCompare(b.date)),
    [today],
  );

  /* Festival spotlight: current, else next */
  const spotlight =
    FESTIVALS.find((f) => f.start <= today && f.end >= today) ??
    FESTIVALS.find((f) => f.start > today);

  const weekendLabel = `${fmtDate(friStr).replace(", 2026", "")} – ${fmtDate(sunStr)}`;

  return (
    <>
      <Helmet>
        <title>Your Hub — The Videshi</title>
        <meta
          name="description"
          content="Your personalized diaspora dashboard: this weekend near you, deadlines that matter, and festival season — all ranked by your location."
        />
        <link rel="canonical" href="https://www.thevideshi.com/your-hub" />
      </Helmet>

      <Masthead />
      <HubStrip />

      <style>{`
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
      `}</style>

      <main className="container flex-1 pt-8 md:pt-10 pb-16">
        <div className="mb-6 flex items-start justify-between gap-3">
          <div>
            <h1 className="font-serif font-black tracking-tight text-foreground leading-none text-[1.75rem] md:text-[2.5rem]">
              Your Hub
            </h1>
            <p className="text-muted-foreground text-sm mt-2">
              Your weekend, your deadlines, your festivals — personalized for you.
            </p>
          </div>
          {isSet && location && (
            <button
              onClick={clearLocation}
              className="flex-shrink-0 mt-1 px-3 py-1.5 rounded-full border border-border text-[12px] font-semibold text-muted-foreground hover:border-[#0B1D3A]/40 whitespace-nowrap"
              title="Change your location"
            >
              {location.label} · change
            </button>
          )}
        </div>

        {!isSet && <LocationSetup onDone={setLocation} />}

        {/* ── This Weekend ── */}
        <section className="mb-10">
          <SectionHead
            title="This Weekend Near You"
            sub={location ? `${location.label} · ${weekendLabel}` : weekendLabel}
          />
          {!isSet && (
            <p className="text-[12px] text-muted-foreground mb-3">
              Set your location above to rank these by distance.
            </p>
          )}
          {!loaded ? (
            <p className="text-sm text-muted-foreground">Loading the weekend…</p>
          ) : weekendEvents.length === 0 ? (
            <div className="bg-card border border-border rounded-lg p-5 text-center">
              <p className="text-sm text-muted-foreground">
                Nothing with tickets found for this weekend{location ? ` near ${location.label}` : ""} yet.
              </p>
              <Link
                to="/events"
                className="inline-block mt-2 text-[13px] font-semibold hover:underline"
                style={{ color: "#A32D2F" }}
              >
                Browse all events →
              </Link>
            </div>
          ) : (
            <>
              {weekendCats.length > 1 && (
                <div className="flex gap-2 mb-4 overflow-x-auto scrollbar-hide" aria-label="Filter by category">
                  <button
                    onClick={() => setCatSel(null)}
                    className={`px-3 py-1 rounded-full text-[13px] font-semibold border whitespace-nowrap ${
                      catSel === null
                        ? "bg-[#0B1D3A] text-white border-[#0B1D3A]"
                        : "text-muted-foreground border-border"
                    }`}
                  >
                    All
                  </button>
                  {weekendCats.map(([c, n]) => (
                    <button
                      key={c}
                      onClick={() => setCatSel(catSel === c ? null : c)}
                      className={`px-3 py-1 rounded-full text-[13px] font-semibold border whitespace-nowrap ${
                        catSel === c
                          ? "bg-[#0B1D3A] text-white border-[#0B1D3A]"
                          : "text-muted-foreground border-border"
                      }`}
                    >
                      {CATEGORY_LABELS[c]} · {n}
                    </button>
                  ))}
                </div>
              )}
              <div
                className="flex gap-3 overflow-x-auto pb-2 -mx-4 px-4 md:mx-0 md:px-0"
                style={{ scrollbarWidth: "none", WebkitOverflowScrolling: "touch" }}
              >
                {weekendEvents.slice(0, 8).map((e) => (
                  <div key={e.id} className="flex-shrink-0 w-[300px]">
                    <EventCard
                      event={e}
                      distance={distanceFor(e, location) ?? undefined}
                    />
                  </div>
                ))}
              </div>
              {weekendEvents.length > 8 && (
                <Link
                  to="/events"
                  className="inline-block mt-3 text-[13px] font-semibold hover:underline"
                  style={{ color: "#A32D2F" }}
                >
                  See all {weekendEvents.length} weekend events →
                </Link>
              )}
            </>
          )}
        </section>

        {/* ── Deadlines ── */}
        <section className="mb-10">
          <SectionHead title="Deadlines That Matter" sub={`${upcomingDeadlines.length} upcoming`} />
          {upcomingDeadlines.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No upcoming deadlines on the radar. Check back soon.
            </p>
          ) : (
            <div
              className="flex gap-3 overflow-x-auto pb-2 -mx-4 px-4 md:mx-0 md:px-0"
              style={{ scrollbarWidth: "none", WebkitOverflowScrolling: "touch" }}
            >
              {upcomingDeadlines.map((d) => {
                const du = daysUntil(d.date);
                const urgent = du <= 7;
                const badge = du === 0 ? "TODAY" : du === 1 ? "TOMORROW" : `in ${du} days`;
                return (
                  <div
                    key={d.id}
                    className="flex-shrink-0 w-[240px] bg-card border border-border rounded-lg p-3.5 flex flex-col"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div
                        className="text-[11px] font-bold uppercase tracking-wide"
                        style={{ color: urgent ? "#A32D2F" : "#64748b" }}
                      >
                        {fmtDate(d.date)}
                      </div>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full whitespace-nowrap ${
                          urgent ? "text-white" : "bg-muted text-muted-foreground"
                        }`}
                        style={urgent ? { backgroundColor: "#A32D2F" } : undefined}
                      >
                        {badge}
                      </span>
                    </div>
                    <h3 className="text-[14px] font-semibold leading-snug mb-1.5">{d.title}</h3>
                    <p className="text-[12px] text-muted-foreground leading-relaxed flex-1">
                      {d.blurb}
                    </p>
                    <a
                      href={d.sourceUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[12px] underline hover:text-foreground mt-2 self-start"
                    >
                      {d.sourceName} →
                    </a>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        {/* ── Festival Spotlight ── */}
        {spotlight && (
          <section className="mb-10">
            <SectionHead title="Festival Spotlight" />
            <div className="bg-card border border-border rounded-lg p-4 md:p-5 mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold tracking-[1.5px] uppercase text-muted-foreground">
                  {spotlight.range}
                </span>
                {(() => {
                  const isNow = spotlight.start <= today && spotlight.end >= today;
                  const du = daysUntil(spotlight.start);
                  return isNow ? (
                    <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-green-600 text-white">
                      Happening now
                    </span>
                  ) : (
                    <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#D4A843] text-[#0B1D3A]">
                      {du === 1 ? "Tomorrow" : `In ${du} days`}
                    </span>
                  );
                })()}
              </div>
              <h3 className="text-xl font-bold" style={{ color: "#0B1D3A" }}>
                {spotlight.name}
              </h3>
              <p className="text-[13px] text-muted-foreground mt-1">{spotlight.note}</p>
              <Link
                to="/festivals"
                className="inline-block mt-3 text-[13px] font-semibold hover:underline"
                style={{ color: "#A32D2F" }}
              >
                Open the Festivals hub →
              </Link>
            </div>
          </section>
        )}

        <p className="text-[11px] text-muted-foreground">
          Deadlines are for general information only — confirm details with official
          sources or a professional before acting.{" "}
          <Link to="/events" className="underline hover:text-foreground">
            Browse all events →
          </Link>
        </p>
      </main>

      <SiteFooter />
    </>
  );
}
