/* ------------------------------------------------------------------ */
/* Flight deals — shared types, metro→airport detection, helpers.     */
/* Data: public/data/flight-deals.json (real Duffel fare snapshots).   */
/* Used by FlightDeals (price calendar), HolidayPlanner and the       */
/* Your Hub "Plan a trip" block — one mapping, one source of truth.   */
/* ------------------------------------------------------------------ */

export type CalendarEntry = {
  date_range: string;
  dep_date: string;
  ret_date: string;
  price_min: number;
  price_max: number;
  cheapest_airline: string;
  num_samples: number;
  year: number;
  month: number;
  weeks: number;
};

export type RouteData = {
  origin: string;
  destination: string;
  origin_metro: string;
  dest_metro: string;
  weeks: number;
  calendar: CalendarEntry[];
};

export type FestivalSeason = {
  id: string;
  name: string;
  emoji: string;
  start: [number, number, number];
  end: [number, number, number];
  book_by_months: number;
  note: string;
};

export type FlightDealsData = {
  generated_at: string;
  as_of: string;
  weeks: number;
  routes: Record<string, RouteData>;
  festival_seasons: FestivalSeason[];
  spec: {
    max_stops: number;
    trip_type: string;
    pricing: string;
    cabin: string;
    min_checked_bags: number;
    note: string;
  };
};

/* Metro → airport mapping (auto-detect from Your Hub location) */
export const METRO_AIRPORTS: Record<string, string> = {
  "bay area": "SFO",
  "san francisco": "SFO",
  "san jose": "SFO",
  "new york": "JFK",
  "nyc": "JFK",
  "new jersey": "EWR",
  "chicago": "ORD",
  "dallas": "DFW",
  "fort worth": "DFW",
  "seattle": "SEA",
  "los angeles": "LAX",
  "houston": "IAH",
  "boston": "BOS",
  "atlanta": "ATL",
  "washington": "IAD",
};

export const DEFAULT_ROUTES = ["SFO-DEL", "JFK-DEL", "ORD-DEL", "DFW-HYD", "SEA-DEL"];

/** Which route key matches the stored Hub location, from the routes
 *  actually present in the deals data. Returns null when the reader's
 *  metro has no route in the data — callers must degrade honestly
 *  (no fare shown) rather than substitute another city's fares. */
export function detectHubRoute(available: string[]): string | null {
  try {
    const hub = localStorage.getItem("videshi-user-location");
    if (hub) {
      const parsed = JSON.parse(hub);
      const label = `${parsed.label || ""} ${parsed.city || ""}`.toLowerCase();
      for (const [metro, airport] of Object.entries(METRO_AIRPORTS)) {
        if (label.includes(metro)) {
          const match = available.find((r) => r.startsWith(airport + "-"));
          if (match) return match;
        }
      }
    }
  } catch {
    /* no stored location */
  }
  return null;
}

export function todayStr(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

export function fmtDate(iso: string): string {
  const d = new Date(iso + "T12:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function fmtDateLong(iso: string): string {
  const d = new Date(iso + "T12:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export function fmtRange(start: string, end: string): string {
  const s = new Date(start + "T12:00:00");
  const e = new Date(end + "T12:00:00");
  const sameYear = s.getFullYear() === e.getFullYear();
  const sTxt = s.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  const eTxt = e.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    ...(sameYear ? {} : { year: "numeric" }),
  });
  return `${sTxt} – ${eTxt}`;
}

export function googleFlightsUrl(origin: string, dest: string, dep: string, ret: string): string {
  return (
    `https://www.google.com/travel/flights?q=` +
    encodeURIComponent(`Flights to ${dest} from ${origin} on ${dep} through ${ret}`) +
    `&curr=USD`
  );
}

let dealsCache: Promise<FlightDealsData | null> | null = null;
export function loadFlightDeals(): Promise<FlightDealsData | null> {
  if (!dealsCache) {
    dealsCache = fetch("/data/flight-deals.json")
      .then((r) => (r.ok ? r.json() : null))
      .catch(() => null);
  }
  return dealsCache;
}

/** Entries still bookable: departure today or later. Stale snapshot
 *  windows are dropped at render so old prices never pose as current. */
export function futureEntries(route: RouteData, from: string = todayStr()): CalendarEntry[] {
  return route.calendar.filter((e) => e.dep_date >= from);
}

/** Cheapest fare departing within the next `months` months. */
export function cheapestFare(
  route: RouteData,
  months = 6,
): { entry: CalendarEntry } | null {
  const now = new Date(todayStr() + "T12:00:00");
  const horizon = new Date(now);
  horizon.setMonth(horizon.getMonth() + months);
  const horizonStr = `${horizon.getFullYear()}-${String(horizon.getMonth() + 1).padStart(2, "0")}-${String(horizon.getDate()).padStart(2, "0")}`;
  const inWindow = futureEntries(route).filter((e) => e.dep_date <= horizonStr);
  if (!inWindow.length) return null;
  const entry = inWindow.reduce((a, b) => (b.price_min < a.price_min ? b : a));
  return { entry };
}

/** A calendar entry whose trip overlaps [start, end] (holiday window). */
export function fareForWindow(
  route: RouteData,
  start: string,
  end: string,
): CalendarEntry | null {
  const matches = futureEntries(route).filter((e) => e.dep_date <= end && e.ret_date >= start);
  if (!matches.length) return null;
  return matches.reduce((a, b) => (b.price_min < a.price_min ? b : a));
}
