import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import HubStrip from "@/components/homepage/HubStrip";
import SiteFooter from "@/components/SiteFooter";
import type { EventItem } from "@/lib/events";
import EventCard from "@/components/EventCard";
import {
  useHubLocation,
  haversineMiles,
  loadClusters,
  getCachedClusters,
  type Cluster,
  type ClusterMember,
  type HubLocation,
} from "@/hooks/useHubLocation";
import { lookupZip } from "@/lib/geo";
import { useUserLocation, type UserLocation } from "@/hooks/useUserLocation";
import { DEADLINES, type Deadline } from "@/data/deadlines";
import { fetchKidsDeadlines } from "@/lib/kidsPrograms";

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

interface LocalNewsItem {
  kind: "article" | "rss";
  slug?: string;
  url?: string;
  domain?: string | null;
  source?: string;
  title: string;
  excerpt: string;
  published_at: string;
  hero_image_url: string;
  category: string;
}

interface FxData {
  rate: number;
  date: string;
  day_change: number;
  day_change_pct: number;
}

interface RemitProvider {
  provider: string;
  rate: number;
  fee_usd: number;
  recipient_gets_inr: number;
  promo?: boolean;
  promo_note?: string | null;
}

interface RemitData {
  as_of: string;
  providers: RemitProvider[];
  note?: string;
}

/** Resolve which cluster's news to show: exact label match, else the
    nearest cluster within 100 mi — distance measured to the closest of
    the cluster center and its member cities, so a reader in Frisco
    lands in the Frisco / Plano bucket, not Irving's. */
function resolveMetroNews(
  location: HubLocation | null,
  localNews: Record<string, LocalNewsItem[]>,
  clusters: Cluster[],
): { label: string; items: LocalNewsItem[] } | null {
  if (!location || Object.keys(localNews).length === 0) return null;
  if (localNews[location.label]?.length) {
    return { label: location.label, items: localNews[location.label] };
  }
  let best: { label: string; dist: number } | null = null;
  for (const cl of clusters) {
    if (!localNews[cl.label]?.length) continue;
    let d = haversineMiles(location.lat, location.lon, cl.center.lat, cl.center.lon);
    for (const mb of cl.members) {
      const dm = haversineMiles(location.lat, location.lon, mb.lat, mb.lon);
      if (dm < d) d = dm;
    }
    if (!best || d < best.dist) best = { label: cl.label, dist: d };
  }
  if (best && best.dist <= 100) {
    return { label: best.label, items: localNews[best.label] };
  }
  return null;
}

/** Human place for auto-detected coords (browser or IP): the nearest
 * cluster's label when within 100 mi — distance measured to the closest
 * of the cluster center and its member cities, the same rule the local
 * news resolution uses — else the IP city/region, else "Near You".
 * Also returns the city/state to store alongside the label, in the
 * same shape the manual picker stores. */
async function resolveAutoPlace(
  lat: number,
  lon: number,
  ip: UserLocation | null,
): Promise<{ label: string; city: string; state: string }> {
  const clusters = await loadClusters().catch(() => getCachedClusters());
  let best: { cluster: Cluster; dist: number } | null = null;
  for (const cl of clusters) {
    let d = haversineMiles(lat, lon, cl.center.lat, cl.center.lon);
    for (const mb of cl.members) {
      const dm = haversineMiles(lat, lon, mb.lat, mb.lon);
      if (dm < d) d = dm;
    }
    if (!best || d < best.dist) best = { cluster: cl, dist: d };
  }
  if (best && best.dist <= 100) {
    return { label: best.cluster.label, city: best.cluster.anchor, state: best.cluster.state };
  }
  if (ip?.city) {
    return {
      label: ip.region ? `${ip.city}, ${ip.region}` : ip.city,
      city: ip.city,
      state: ip.region ?? "",
    };
  }
  return { label: "Near You", city: "", state: "" };
}

/* ── Location setup ── */
function LocationSetup({
  onDone,
  clusters,
}: {
  onDone: (loc: HubLocation) => void;
  clusters: Cluster[];
}) {
  const [geoError, setGeoError] = useState<string | null>(null);
  const [geoLoading, setGeoLoading] = useState(false);
  const [zip, setZip] = useState("");
  const [zipError, setZipError] = useState<string | null>(null);
  const [zipLoading, setZipLoading] = useState(false);
  const [cityQuery, setCityQuery] = useState("");

  /** Picker results: clusters whose label or any member city matches
   * the search text. Each row remembers the member the user matched, so
   * picking "Hicksville" stores Hicksville's own coordinates. */
  const pickerMatches = useMemo(() => {
    const q = cityQuery.trim().toLowerCase();
    const rows: { cluster: Cluster; member: ClusterMember | null }[] = [];
    for (const cl of clusters) {
      if (!q) {
        rows.push({ cluster: cl, member: null });
        continue;
      }
      const member =
        cl.members.find((mb) => mb.name.toLowerCase().includes(q)) ?? null;
      if (member || cl.label.toLowerCase().includes(q)) {
        rows.push({ cluster: cl, member });
      }
    }
    return q ? rows.slice(0, 16) : rows;
  }, [clusters, cityQuery]);

  const pickCluster = (cl: Cluster, member: ClusterMember | null) => {
    onDone({
      city: member?.name ?? cl.anchor,
      state: member?.state ?? cl.state,
      lat: member?.lat ?? cl.center.lat,
      lon: member?.lon ?? cl.center.lon,
      label: cl.label,
    });
  };

  const useMyLocation = () => {
    if (!navigator.geolocation) {
      setGeoError("Geolocation isn't available in this browser — enter your zip below.");
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
        setGeoError("Location access was denied — enter your zip below instead.");
      },
      { enableHighAccuracy: false, timeout: 8000 },
    );
  };

  const submitZip = async () => {
    const clean = zip.trim();
    if (!/^\d{5}$/.test(clean)) {
      setZipError("Enter a 5-digit US zip code.");
      return;
    }
    setZipLoading(true);
    setZipError(null);
    try {
      // Local zip database first (src/lib/geo.ts → /data/zipcodes.json);
      // the location then resolves to the nearest cluster with news.
      const info = await lookupZip(clean).catch(() => null);
      if (info) {
        onDone({
          city: info.city,
          state: info.state,
          lat: info.lat,
          lon: info.lng,
          label: `${info.city}, ${info.state}`,
        });
        return;
      }
      const r = await fetch(`https://api.zippopotam.us/us/${clean}`);
      if (!r.ok) throw new Error("not found");
      const d = await r.json();
      const place = d.places?.[0];
      if (!place) throw new Error("not found");
      onDone({
        city: place["place name"],
        state: place["state abbreviation"],
        lat: parseFloat(place.latitude),
        lon: parseFloat(place.longitude),
        label: `${place["place name"]}, ${place["state abbreviation"]}`,
      });
    } catch {
      setZipError("Couldn't find that zip — check it and try again.");
    } finally {
      setZipLoading(false);
    }
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
        <span className="text-[11px] uppercase tracking-wider text-muted-foreground">or enter your zip</span>
        <div className="flex-1 border-t border-border" />
      </div>
      <div className="flex gap-2">
        <input
          value={zip}
          onChange={(e) => setZip(e.target.value.replace(/\D/g, "").slice(0, 5))}
          onKeyDown={(e) => {
            if (e.key === "Enter") submitZip();
          }}
          inputMode="numeric"
          placeholder="Zip code"
          aria-label="Zip code"
          className="flex-1 min-w-0 px-4 py-2.5 rounded-full border border-border text-sm bg-background focus:outline-none focus:ring-2 focus:ring-[#D4A843]"
        />
        <button
          onClick={submitZip}
          disabled={zipLoading}
          className="px-5 py-2.5 rounded-full text-sm font-bold text-white transition-opacity hover:opacity-90 disabled:opacity-60"
          style={{ backgroundColor: "#0B1D3A" }}
        >
          {zipLoading ? "Finding…" : "Set"}
        </button>
      </div>
      {zipError && (
        <p className="text-[12px] mt-2" style={{ color: "#A32D2F" }}>
          {zipError}
        </p>
      )}
      <div className="flex items-center gap-3 my-4">
        <div className="flex-1 border-t border-border" />
        <span className="text-[11px] uppercase tracking-wider text-muted-foreground">or search your city</span>
        <div className="flex-1 border-t border-border" />
      </div>
      <input
        value={cityQuery}
        onChange={(e) => setCityQuery(e.target.value)}
        placeholder="Start typing your city — e.g. Hicksville, Carmel, Frisco…"
        aria-label="Search your city"
        className="w-full px-4 py-2.5 rounded-full border border-border text-sm bg-background focus:outline-none focus:ring-2 focus:ring-[#D4A843] mb-3"
      />
      {cityQuery.trim() ? (
        <div className="flex flex-col gap-1.5">
          {pickerMatches.length === 0 && (
            <p className="text-[13px] text-muted-foreground px-1">
              No match yet — try the nearest big suburb, or use your zip above.
            </p>
          )}
          {pickerMatches.map(({ cluster: cl, member }) => (
            <button
              key={cl.id + (member?.name ?? "")}
              onClick={() => pickCluster(cl, member)}
              className="px-3 py-2 rounded-lg border border-border text-[13px] font-medium text-left hover:border-[#0B1D3A]/50 hover:bg-muted/40 transition-colors"
            >
              {member ? (
                <>
                  {member.name}, {member.state}
                  <span className="text-muted-foreground font-normal">
                    {" "}— {cl.label} area
                  </span>
                </>
              ) : (
                cl.label
              )}
            </button>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 max-h-64 overflow-y-auto pr-1">
          {pickerMatches.map(({ cluster: cl }) => (
            <button
              key={cl.id}
              onClick={() => pickCluster(cl, null)}
              className="px-3 py-2 rounded-lg border border-border text-[13px] font-medium text-left hover:border-[#0B1D3A]/50 hover:bg-muted/40 transition-colors"
            >
              {cl.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function YourHubPage() {
  const { location, setLocation, clearLocation, isSet } = useHubLocation();
  const { location: ipLocation } = useUserLocation();
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [catSel, setCatSel] = useState<string | null>(null);
  const [localNews, setLocalNews] = useState<Record<string, LocalNewsItem[]>>({});
  const [clusters, setClusters] = useState<Cluster[]>(() => getCachedClusters());

  useEffect(() => {
    loadClusters()
      .then(setClusters)
      .catch(() => {});
  }, []);
  const [kidsDeadlines, setKidsDeadlines] = useState<Deadline[]>([]);
  const [fx, setFx] = useState<FxData | null>(null);
  const [remit, setRemit] = useState<RemitData | null>(null);

  useEffect(() => {
    fetch("/data/local-news.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d && d.metros) setLocalNews(d.metros);
      })
      .catch(() => {});
    fetch("/data/usdinr.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d && typeof d.rate === "number") setFx(d);
      })
      .catch(() => {});
    fetch("/data/remittance-rates.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d && Array.isArray(d.providers) && d.providers.length) setRemit(d);
      })
      .catch(() => {});
    // Competition / program registration deadlines from Learn — same source as /kids
    fetchKidsDeadlines(50)
      .then((ds) => {
        setKidsDeadlines(
          ds.map((d) => ({
            id: `kids-${d.id}`,
            title: d.title,
            date: d.deadline_date,
            category: "education" as const,
            blurb: d.description || d.deadline_type || "Registration deadline",
            sourceName: "Learn",
            sourceUrl: "/kids",
          })),
        );
      })
      .catch(() => {});
  }, []);

  /* Auto-detect location on page land, mirroring the events page:
     browser geolocation prompt first; on denial / unavailable /
     timeout, fall back to the IP location from useUserLocation;
     only if that also yields nothing does the manual LocationSetup
     panel below remain. Runs only when no location is stored — a
     returning user is never re-prompted — and a location the user
     picks manually while the prompt is pending is never overwritten. */
  const locationRef = useRef(location);
  useEffect(() => {
    locationRef.current = location;
  }, [location]);
  const ipRef = useRef(ipLocation);
  useEffect(() => {
    ipRef.current = ipLocation;
  }, [ipLocation]);

  const applyAutoLocation = useCallback(
    (lat: number, lon: number, ip: UserLocation | null) => {
      if (locationRef.current) return;
      void resolveAutoPlace(lat, lon, ip).then((place) => {
        if (locationRef.current) return;
        setLocation({ city: place.city, state: place.state, lat, lon, label: place.label });
      });
    },
    [setLocation],
  );

  const geoPendingRef = useRef(false);
  useEffect(() => {
    if (isSet) return;
    if (!navigator.geolocation) {
      // No browser ask possible — the IP location is the only source.
      if (ipLocation) {
        applyAutoLocation(ipLocation.latitude, ipLocation.longitude, ipLocation);
      }
      return;
    }
    if (geoPendingRef.current) return;
    geoPendingRef.current = true;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        geoPendingRef.current = false;
        applyAutoLocation(pos.coords.latitude, pos.coords.longitude, ipRef.current);
      },
      () => {
        geoPendingRef.current = false;
        const ip = ipRef.current;
        if (ip) applyAutoLocation(ip.latitude, ip.longitude, ip);
        /* no IP location either — LocationSetup panel is the fallback */
      },
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 },
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSet, ipLocation]);

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

  /* Deadlines — static list + Learn competition deadlines, merged */
  const upcomingDeadlines = useMemo(
    () =>
      [...DEADLINES, ...kidsDeadlines]
        .filter((d) => d.date >= today)
        .sort((a, b) => a.date.localeCompare(b.date)),
    [today, kidsDeadlines],
  );

  /* Festival spotlight: current, else next */
  const spotlight =
    FESTIVALS.find((f) => f.start <= today && f.end >= today) ??
    FESTIVALS.find((f) => f.start > today);

  const metroNews = useMemo(
    () => resolveMetroNews(location, localNews, clusters),
    [location, localNews, clusters],
  );

  const weekendLabel = `${fmtDate(friStr).replace(", 2026", "")} – ${fmtDate(sunStr)}`;

  return (
    <>
      <Helmet>
        <title>Your Hub — The Videshi</title>
        <meta
          name="description"
          content="Your personalized diaspora dashboard: this weekend near you, deadlines that matter, the morning brief, money moves, and festival season — all ranked by your location."
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
              Your weekend, your deadlines, your money, your festivals — personalized for you.
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

        {!isSet && <LocationSetup onDone={setLocation} clusters={clusters} />}

        {/* ── This Weekend ── */}
        <section className="mb-10">
          <SectionHead
            title={location ? `This Weekend Near ${location.label}` : "This Weekend Near You"}
            sub={weekendLabel}
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

        {/* ── Money Moves ── */}
        {fx && remit && (
          <section className="mb-10">
            <SectionHead title="Money Moves" sub="USD → INR" />
            <div className="bg-card border border-border rounded-lg p-4 md:p-5">
              <div className="flex items-end justify-between mb-4">
                <div className="flex items-baseline gap-2.5">
                  <span className="text-[2rem] font-black leading-none" style={{ color: "#0B1D3A" }}>
                    ₹{fx.rate.toFixed(2)}
                  </span>
                  <span
                    className={`text-[12px] font-bold px-2 py-0.5 rounded-full ${
                      fx.day_change >= 0 ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                    }`}
                  >
                    {fx.day_change >= 0 ? "▲" : "▼"} {Math.abs(fx.day_change_pct).toFixed(2)}%
                  </span>
                </div>
                <span className="text-[11px] text-muted-foreground">
                  Mid-market · {fmtDate(fx.date)}
                </span>
              </div>
              <div className="divide-y divide-border border-y border-border">
                {(() => {
                  const best = Math.max(...remit.providers.map((p) => p.recipient_gets_inr));
                  return remit.providers.slice(0, 4).map((p) => {
                    const isBest = p.recipient_gets_inr === best;
                    return (
                      <div key={p.provider} className="flex items-center justify-between py-2.5 gap-2">
                        <div className="min-w-0">
                          <span className="text-[13px] font-semibold">{p.provider}</span>
                          {isBest && (
                            <span
                              className="ml-2 text-[10px] font-bold px-1.5 py-0.5 rounded-full text-white align-middle"
                              style={{ backgroundColor: "#0B1D3A" }}
                            >
                              BEST
                            </span>
                          )}
                          {p.promo && p.promo_note && (
                            <p className="text-[10px] text-muted-foreground truncate">{p.promo_note}</p>
                          )}
                        </div>
                        <div className="text-right flex-shrink-0">
                          <div className="text-[13px] font-bold">₹{p.recipient_gets_inr.toLocaleString("en-IN", { maximumFractionDigits: 0 })}</div>
                          <div className="text-[10px] text-muted-foreground">
                            ₹{p.rate.toFixed(2)}/$ · {p.fee_usd === 0 ? "no fee" : `$${p.fee_usd} fee`}
                          </div>
                        </div>
                      </div>
                    );
                  });
                })()}
              </div>
              <p className="text-[11px] text-muted-foreground mt-2.5">
                For $1,000 sent · {remit.as_of ? `rates as of ${fmtDate(remit.as_of)}` : ""} · promos may apply to new customers only
              </p>
              <Link
                to="/markets-finance"
                className="inline-block mt-2.5 text-[13px] font-semibold hover:underline"
                style={{ color: "#A32D2F" }}
              >
                More in Markets →
              </Link>
            </div>
          </section>
        )}

        {/* ── Local News ── */}
        {metroNews && (
          <section className="mb-10">
            <SectionHead
              title="Local News"
              sub={metroNews.label}
            />
            <div className="bg-card border border-border rounded-lg divide-y divide-border overflow-hidden">
              {metroNews.items.map((n) => {
                const isRss = n.kind === "rss";
                const row = (
                  <>
                    {!isRss && n.hero_image_url && (
                      <img
                        src={n.hero_image_url}
                        alt=""
                        loading="lazy"
                        className="w-20 h-20 object-cover rounded-md flex-shrink-0"
                      />
                    )}
                    <div className="min-w-0">
                      <h3 className="text-[14px] font-semibold leading-snug">
                        {n.title}
                      </h3>
                      <p className="text-[12px] text-muted-foreground mt-1">
                        {isRss ? (
                          <>{n.source} →</>
                        ) : (
                          <>
                            {n.published_at ? fmtDate(n.published_at.slice(0, 10)) : ""}
                            {n.category ? ` · ${n.category}` : ""}
                          </>
                        )}
                      </p>
                    </div>
                  </>
                );
                const cls =
                  "flex gap-3.5 p-3.5 no-underline hover:bg-muted/30 transition-colors";
                return isRss ? (
                  <a
                    key={n.url}
                    href={n.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={cls}
                  >
                    {row}
                  </a>
                ) : (
                  <Link key={n.slug} to={`/articles/${n.slug}`} className={cls}>
                    {row}
                  </Link>
                );
              })}
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
