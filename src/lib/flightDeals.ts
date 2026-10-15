/* ------------------------------------------------------------------ */
/* Flight deals — shared types, metro→airport detection, helpers.     */
/* Data: public/data/flight-deals.json (real Duffel fare snapshots)   */
/* + flight-deals-intl.json (weekly matrix). Used by FlightDeals       */
/* (Cheapest Fares hub) and the Your Hub "Plan a trip" block — one     */
/* mapping, one source of truth.                                       */
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
  /** Band model (2026-10-15): the winning trip's actual duration. */
  duration_days?: number;
  /** Band id ("in-3wk" | "intl-1wk") the cell was sampled under. */
  band?: string;
  /** Legacy pre-band field; absent in new snapshots. */
  weeks?: number;
  /** Honest per-cell freshness (oldest fetch among the cell's samples). */
  fetched_as_of?: string;
  cheapest_month?: boolean;
  change_vs_prev?: {
    prev_price_min: number;
    prev_as_of: string | null;
    delta: number; // positive = price dropped
    delta_pct: number;
  };
};

export type FareBand = {
  id: string;
  label: string;
  center_days: number;
  min_days: number;
  max_days: number;
};

export type CheapestOverall = {
  year: number;
  month: number;
  band?: string;
  duration_days?: number;
  weeks?: number;
  price_min: number;
  date_range: string;
} | null;

export type RouteData = {
  origin: string;
  destination: string;
  origin_metro: string;
  dest_metro: string;
  /** Band id this route's calendar was sampled under. */
  band?: string;
  /** Legacy pre-band field; absent in new snapshots. */
  weeks?: number;
  calendar: CalendarEntry[];
  calendars_by_weeks?: Record<string, CalendarEntry[]>;
  cheapest_overall?: CheapestOverall;
  /** Intl matrix: travel-destinations.json slug for this route. */
  destination_slug?: string;
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
  market?: string;
  band?: FareBand;
  months_ahead?: number;
  /** Legacy pre-band field; absent in new snapshots. */
  weeks?: number;
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

/* Metro → airport mapping (auto-detect from Your Hub location).
   Substring-matched against the Hub record's label/city (longest keys
   win by insertion order below is NOT relied on — detectHubRoute also
   falls back to nearest-airport by coordinates). The Tri-Valley /
   East Bay keys were the 2026-10-15 audit gap: the site's own home
   reader (Dublin, CA) matched nothing and silently got SFO-DEL by
   default instead of by detection. */
export const METRO_AIRPORTS: Record<string, string> = {
  "bay area": "SFO",
  "san francisco": "SFO",
  "san jose": "SFO",
  "dublin": "SFO",
  "tri-valley": "SFO",
  "pleasanton": "SFO",
  "livermore": "SFO",
  "san ramon": "SFO",
  "fremont": "SFO",
  "hayward": "SFO",
  "oakland": "SFO",
  "east bay": "SFO",
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

/** Coordinates of the tracked origin airports — the lat/lon fallback
 *  for Hub records whose label/city matches no metro key (e.g. a bare
 *  town name). Nearest airport among the routes actually in the data
 *  wins; no distance cap — it only breaks the tie the label couldn't. */
export const AIRPORT_COORDS: Record<string, [number, number]> = {
  SFO: [37.6213, -122.379],
  LAX: [33.9416, -118.4085],
  SEA: [47.4502, -122.3088],
  JFK: [40.6413, -73.7781],
  EWR: [40.6895, -74.1745],
  ORD: [41.9742, -87.9073],
  DFW: [32.8998, -97.0403],
  IAH: [29.9902, -95.3368],
  IAD: [38.9531, -77.4565],
  ATL: [33.6407, -84.4277],
  BOS: [42.3656, -71.0096],
};

function haversineMiles(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number,
): number {
  const R = 3958.8;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

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
      // Fallback: nearest tracked origin airport to the Hub record's
      // coordinates (records carry lat/lon). Only origins present in
      // the data are candidates — detection can never invent a route.
      const lat = Number(parsed.lat);
      const lon = Number(parsed.lon);
      if (Number.isFinite(lat) && Number.isFinite(lon)) {
        const origins = [
          ...new Set(available.map((r) => r.split("-")[0])),
        ].filter((a) => AIRPORT_COORDS[a]);
        let best: { airport: string; miles: number } | null = null;
        for (const airport of origins) {
          const [alat, alon] = AIRPORT_COORDS[airport];
          const miles = haversineMiles(lat, lon, alat, alon);
          if (!best || miles < best.miles) best = { airport, miles };
        }
        if (best) {
          const match = available.find((r) =>
            r.startsWith(best!.airport + "-"),
          );
          if (match) return match;
        }
      }
    }
  } catch {
    /* no stored location */
  }
  return null;
}

/** The user's detected origin airport (from the Hub record), without
 *  binding to a specific destination — for fare lists that span
 *  markets (India + international). Null when no location is stored. */
export function detectHubOrigin(airports: string[]): string | null {
  const route = detectHubRoute(airports.map((a) => `${a}-XXX`));
  return route ? route.split("-")[0] : null;
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
  return `${sTxt} → ${eTxt}`;
}

export function googleFlightsUrl(origin: string, dest: string, dep: string, ret: string): string {
  return (
    `https://www.google.com/travel/flights?q=` +
    encodeURIComponent(`Flights to ${dest} from ${origin} on ${dep} through ${ret}`) +
    `&curr=USD`
  );
}

/* ------------------------------------------------------------------ */
/* Airline direct-booking links (Kiran's decision, 2026-10-15): only  */
/* VERIFIED deep-link templates ship. A template is verified when its  */
/* parameter contract was confirmed against the carrier's own flight- */
/* search URL structure (docs + observed live search URLs) — never a  */
/* bare homepage dressed as a booking link. Carriers without a         */
/* verified template get the Google Flights compare link only.        */
/*                                                                     */
/* Delta — verified 2026-10-15 against delta.com's search parameter    */
/* contract (originCity/destinationCity IATA, MM/DD/YYYY dates,        */
/* tripType=ROUND_TRIP, paxCount, cabinFareClass=MAIN): see            */
/* research/travel-page-restructure-2026-10-15.md §D.                  */
/*                                                                     */
/* JetBlue — verified 2026-10-15 (link-check pass #1) by rendering the */
/* constructed URL and inspecting the landing: JFK→DEL               */
/* 2026-11-24→2026-12-16 (a live fare cell) landed on JetBlue's        */
/* "Select Flights" results carrying the route, the dates and          */
/* "1 Traveler"; JFK→LHR 2026-11-12→2026-11-19 corroborated. The       */
/* contract is adults/children/infants — do NOT "simplify" it to a    */
/* passengers=/fareType= variant: that variant parses the route but    */
/* searches with 0 travelers and lands on an empty results page.       */
/* Evidence: research/airline-link-check-2026-10-15.md.                */
/* ------------------------------------------------------------------ */

function mmddyyyy(iso: string): string {
  const [y, m, d] = iso.split("-");
  return `${m}/${d}/${y}`;
}

export const AIRLINE_LINK_TEMPLATES: Record<
  string,
  (origin: string, dest: string, dep: string, ret: string) => string
> = {
  delta: (origin, dest, dep, ret) =>
    "https://www.delta.com/flightsearch/search?action=findFlights" +
    "&tripType=ROUND_TRIP&priceSchedule=price" +
    `&originCity=${origin}&destinationCity=${dest}` +
    `&departureDate=${mmddyyyy(dep)}&returnDate=${mmddyyyy(ret)}` +
    "&paxCount=1&searchByCabin=true&cabinFareClass=MAIN&deltaOnlySearch=false",
  jetblue: (origin, dest, dep, ret) =>
    "https://www.jetblue.com/booking/flights" +
    `?from=${origin}&to=${dest}&depart=${dep}&return=${ret}` +
    "&isMultiCity=false&noOfRoute=1&adults=1&children=0&infants=0" +
    "&roundTripFaresFlag=false&sharedMarket=false&usePoints=false",
};

/** Direct booking URL on the airline's own site for this fare, or
 *  null when the airline has no verified template. Callers render the
 *  returned link as primary and Google Flights as the compare link;
 *  on null, Google Flights is the only link (honest — see header). */
export function airlineBookingUrl(
  airline: string | null | undefined,
  origin: string,
  dest: string,
  dep: string,
  ret: string,
): string | null {
  if (!airline) return null;
  const name = airline.toLowerCase();
  for (const [key, build] of Object.entries(AIRLINE_LINK_TEMPLATES)) {
    if (name.includes(key)) return build(origin, dest, dep, ret);
  }
  return null;
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

/** Weekly international matrix (public/data/flight-deals-intl.json). */
export type IntlDealsData = {
  generated_at: string;
  as_of: string;
  cadence?: string;
  indicative?: boolean;
  band?: FareBand;
  routes: Record<string, RouteData>;
  biggest_drops?: unknown[];
};

let intlCache: Promise<IntlDealsData | null> | null = null;
export function loadIntlFlightDeals(): Promise<IntlDealsData | null> {
  if (!intlCache) {
    intlCache = fetch("/data/flight-deals-intl.json")
      .then((r) => (r.ok ? r.json() : null))
      .catch(() => null);
  }
  return intlCache;
}

/** Cheapest upcoming fare to a destination airport in the intl matrix.
 *  Prefers the reader's own origin airport (from their Hub location)
 *  when that route exists; otherwise the cheapest origin overall.
 *  Returns null when the destination has no data — never borrowed. */
export function cheapestIntlFare(
  data: IntlDealsData,
  destAirport: string,
  preferredOrigin?: string | null,
): { route: RouteData; entry: CalendarEntry } | null {
  const candidates = Object.values(data.routes).filter(
    (r) => r.destination === destAirport,
  );
  const pools = preferredOrigin
    ? [candidates.filter((r) => r.origin === preferredOrigin), candidates]
    : [candidates];
  for (const pool of pools) {
    let best: { route: RouteData; entry: CalendarEntry } | null = null;
    for (const route of pool) {
      const c = cheapestFare(route, 3);
      if (c && (!best || c.entry.price_min < best.entry.price_min)) {
        best = { route, entry: c.entry };
      }
    }
    if (best) return best;
  }
  return null;
}

/* ------------------------------------------------------------------ */
/* India metros grid (flight-deals-metros.json) — the weekly grid     */
/* behind the India Metros Scroll (Kiran, 2026-10-15). The daily      */
/* core covers 12 routes; the grid's 38 pairs (incl. CCU from every   */
/* origin) refresh weekly through daily slices. Merged UNDER the      */
/* daily data: for any route present in both, the DAILY fare wins.    */
/* Grid fares carry their own check date and a "checked weekly"       */
/* label — never the daily snapshot's date.                           */
/* ------------------------------------------------------------------ */

export const INDIA_METROS: { code: string; name: string }[] = [
  { code: "DEL", name: "Delhi" },
  { code: "BOM", name: "Mumbai" },
  { code: "BLR", name: "Bengaluru" },
  { code: "HYD", name: "Hyderabad" },
  { code: "CCU", name: "Kolkata" },
];

/** Weekly metros grid data (public/data/flight-deals-metros.json). */
export type MetrosDealsData = {
  generated_at: string;
  as_of: string;
  cadence?: string;
  indicative?: boolean;
  band?: FareBand;
  routes: Record<string, RouteData>;
};

let metrosCache: Promise<MetrosDealsData | null> | null = null;
export function loadMetrosFlightDeals(): Promise<MetrosDealsData | null> {
  if (!metrosCache) {
    metrosCache = fetch("/data/flight-deals-metros.json")
      .then((r) => (r.ok ? r.json() : null))
      .catch(() => null);
  }
  return metrosCache;
}

/** Merge the grid under the daily snapshot: same route key in both →
 *  the daily route wins (fresher, fuller cadence). */
export function mergeDealRoutes(
  daily: FlightDealsData | null,
  metros: MetrosDealsData | null,
): Record<string, RouteData> {
  return { ...(metros?.routes ?? {}), ...(daily?.routes ?? {}) };
}

/** Where a merged route's data came from. */
export function dealRouteSource(
  routeKey: string,
  daily: FlightDealsData | null,
): "daily" | "weekly" {
  return daily?.routes[routeKey] ? "daily" : "weekly";
}

/** The reader's origin airport, resolved against the COMBINED route
 *  pool (daily ∪ grid) — the grid gives every tracked origin all five
 *  metros, so origin resolution must see both files. Null when no Hub
 *  location is stored. */
export function detectMetrosOrigin(
  daily: FlightDealsData | null,
  metros: MetrosDealsData | null,
): string | null {
  const keys = Object.keys(mergeDealRoutes(daily, metros));
  if (!keys.length) return null;
  const rk = detectHubRoute(keys);
  return rk ? rk.split("-")[0] : null;
}

export type MetroFare = {
  /** Destination airport code (DEL/BOM/BLR/HYD/CCU). */
  metro: string;
  metroName: string;
  routeKey: string;
  route: RouteData;
  entry: CalendarEntry;
  source: "daily" | "weekly";
  /** Honest per-fare freshness, in the page's two standard stamp
   *  formats (audit item 22, 2026-10-15): "Checked Oct 15, 2026"
   *  (daily) or "Checked weekly · Oct 15, 2026" (grid). Built from
   *  the winning cell's own fetched_as_of, never the file's date. */
  checkedLabel: string;
};

/** One fare per India metro for `origin`, in canonical metro order.
 *  Metros whose route has no upcoming fare are OMITTED — the rail
 *  shows real fares only, never a placeholder or a borrowed route. */
export function metroFaresForOrigin(
  daily: FlightDealsData | null,
  metros: MetrosDealsData | null,
  origin: string,
): MetroFare[] {
  const out: MetroFare[] = [];
  for (const { code, name } of INDIA_METROS) {
    const routeKey = `${origin}-${code}`;
    const dailyRoute = daily?.routes[routeKey];
    const route = dailyRoute ?? metros?.routes[routeKey];
    if (!route) continue;
    const c = cheapestFare(route, 3);
    if (!c) continue;
    const source = dailyRoute ? "daily" : "weekly";
    const checked = c.entry.fetched_as_of ??
      (source === "daily" ? daily?.as_of : metros?.as_of);
    out.push({
      metro: code,
      metroName: name,
      routeKey,
      route,
      entry: c.entry,
      source,
      checkedLabel: checked
        ? source === "daily"
          ? `Checked ${fmtDateLong(checked)}`
          : `Checked weekly · ${fmtDateLong(checked)}`
        : "",
    });
  }
  return out;
}

/** Entries still bookable: departure today or later. Stale snapshot
 *  windows are dropped at render so old prices never pose as current. */
export function futureEntries(route: RouteData, from: string = todayStr()): CalendarEntry[] {
  const cal =
    route.calendar && route.calendar.length
      ? route.calendar
      : (route.calendars_by_weeks?.[String(route.weeks ?? 3)] ?? []);
  return cal.filter((e) => e.dep_date >= from);
}

/** Human label for a fare cell's trip length under the band model:
 *  "21-day trip" from the actual duration; legacy weeks as fallback. */
export function tripLengthLabel(entry: CalendarEntry): string {
  if (entry.duration_days) return `${entry.duration_days}-day trip`;
  if (entry.weeks) return `${entry.weeks}-week trip`;
  return "round trip";
}

/** Festival advice for a price card (holistic audit item 16,
 * 2026-10-15 — fixes the template, not the instances): the
 * "Book N months ahead for best fares" clause is appended ONLY while
 * that advice is still actionable. Once the departure is inside the
 * book-by window (today is past departure − book_by_months), the
 * clause is expired advice and is suppressed; the season note alone
 * renders. Book-by messaging otherwise belongs to the urgency strip,
 * which computes the window state correctly. */
export function festivalAdvice(
  entry: CalendarEntry,
  season: FestivalSeason,
  today: Date = new Date(),
): string {
  const dep = new Date(entry.dep_date + "T12:00:00");
  const bookBy = new Date(dep);
  bookBy.setMonth(bookBy.getMonth() - season.book_by_months);
  // Compare calendar dates, not instants: on the book-by date itself
  // the departure is already inside the window.
  const bookByStart = new Date(
    bookBy.getFullYear(),
    bookBy.getMonth(),
    bookBy.getDate(),
  );
  const todayStart = new Date(
    today.getFullYear(),
    today.getMonth(),
    today.getDate(),
  );
  if (todayStart >= bookByStart) return season.note;
  return `${season.note} · Book ${season.book_by_months} months ahead for best fares`;
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
