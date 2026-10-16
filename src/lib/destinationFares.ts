/* ------------------------------------------------------------------ */
/* Destination-page fare module — class resolution (Phase 2,          */
/* 2026-10-15; spec: research/travel-page-relook-2026-10-15.md §5).   */
/*                                                                    */
/* Every destination page gets the SAME fare module; what varies is   */
/* which class the destination belongs to, and the class is decided   */
/* by static maps + the deals files — never by borrowing another      */
/* destination's fares:                                               */
/*                                                                    */
/*  A — India guides whose OWN arrival metro is tracked. Today only   */
/*      karnataka (BLR): Delhi's fare is never shown as Rajasthan's.   */
/*      Data: daily snapshot merged over the weekly metros grid.      */
/*  B — destinations in the weekly international matrix. Data:        */
/*      flight-deals-intl.json only. A mapped destination whose       */
/*      routes haven't landed yet resolves to zero fares and the      */
/*      module degrades to the fallback — still no invented numbers.  */
/*  fallback — everything else (incl. goa/kerala until their own      */
/*      GOI/COK grid decision): planner facts + a labelled Google     */
/*      Flights search link. No fare numbers, ever.                   */
/*                                                                    */
/* Fetch discipline: the class comes from the slug alone, so the      */
/* module fetches ONLY its class's file(s) — and never                */
/* travel-destinations.json.                                          */
/* ------------------------------------------------------------------ */

import {
  ORIGIN_CITY_LABELS,
  dealRouteSource,
  detectHubOrigin,
  fmtDateLong,
  futureEntries,
  readFaresOriginPref,
  type CalendarEntry,
  type FlightDealsData,
  type IntlDealsData,
  type MetrosDealsData,
  type RouteData,
} from "@/lib/flightDeals";

/** Class A: destination slug → its OWN India arrival metro. Only
 *  metros the fare pipeline actually tracks (DEL/BOM/BLR/HYD/CCU)
 *  can ever appear here; a state whose gateway isn't tracked (Goa
 *  GOI, Kerala COK, Tamil Nadu MAA…) stays fallback by construction. */
export const INDIA_DESTINATION_METRO: Record<string, string> = {
  karnataka: "BLR",
};

/** Class B: destination slug → its airport in the weekly intl matrix. */
export const INTL_DESTINATION_AIRPORT: Record<
  string,
  { code: string; city: string }
> = {
  australia: { code: "SYD", city: "Sydney" },
  bali: { code: "DPS", city: "Denpasar (Bali)" },
  cabo: { code: "SJD", city: "Los Cabos" },
  egypt: { code: "CAI", city: "Cairo" },
  fiji: { code: "NAN", city: "Nadi" },
  france: { code: "CDG", city: "Paris" },
  greece: { code: "ATH", city: "Athens" },
  hawaii: { code: "HNL", city: "Honolulu" },
};

export type DestinationFareClass = "A" | "B" | "fallback";

/** The class is a property of the SLUG (static maps), so the module
 *  knows which deals file(s) to fetch before any data arrives. */
export function destinationFareClass(slug: string): DestinationFareClass {
  if (INDIA_DESTINATION_METRO[slug]) return "A";
  if (INTL_DESTINATION_AIRPORT[slug]) return "B";
  return "fallback";
}

/** One origin's fares to a destination: the route, its upcoming
 *  cells, the cheapest of them, and the route's own honest stamp —
 *  "Checked {date}" (daily) or "Checked weekly · {date}" (weekly
 *  grid / intl matrix), built from the winning cell's fetched_as_of,
 *  never a file-level date dressed up as the route's. */
export type DestinationOriginFare = {
  origin: string;
  routeKey: string;
  route: RouteData;
  entries: CalendarEntry[];
  cheapest: CalendarEntry;
  source: "daily" | "weekly";
  checkedLabel: string;
};

function toOriginFare(
  routeKey: string,
  route: RouteData,
  source: "daily" | "weekly",
  fileAsOf: string | undefined,
): DestinationOriginFare | null {
  const entries = futureEntries(route);
  if (!entries.length) return null;
  const cheapest = entries.reduce((a, b) =>
    b.price_min < a.price_min ||
    (b.price_min === a.price_min && b.dep_date < a.dep_date)
      ? b
      : a,
  );
  const checked = cheapest.fetched_as_of ?? fileAsOf;
  return {
    origin: route.origin,
    routeKey,
    route,
    entries,
    cheapest,
    source,
    checkedLabel: checked
      ? source === "daily"
        ? `Checked ${fmtDateLong(checked)}`
        : `Checked weekly · ${fmtDateLong(checked)}`
      : "",
  };
}

/** Class A fares: every tracked origin's route to the destination's
 *  OWN metro, daily merged over the weekly grid (daily wins per
 *  route, same merge rule as the /travel hub). Returns [] for a
 *  slug with no own-metro mapping — the caller renders fallback. */
export function resolveIndiaFares(
  slug: string,
  daily: FlightDealsData | null,
  metros: MetrosDealsData | null,
): DestinationOriginFare[] {
  const metro = INDIA_DESTINATION_METRO[slug];
  if (!metro) return [];
  const out: DestinationOriginFare[] = [];
  const keys = new Set([
    ...Object.keys(metros?.routes ?? {}),
    ...Object.keys(daily?.routes ?? {}),
  ]);
  for (const key of [...keys].sort()) {
    if (!key.endsWith(`-${metro}`)) continue;
    const route = daily?.routes[key] ?? metros?.routes[key];
    if (!route) continue;
    const source = dealRouteSource(key, daily);
    const fare = toOriginFare(
      key,
      route,
      source,
      source === "daily" ? daily?.as_of : metros?.as_of,
    );
    if (fare) out.push(fare);
  }
  return out;
}

/** Class B fares: every origin's route to the destination's airport
 *  in the weekly intl matrix. Routes carry a destination_slug; when
 *  present it must match — an airport shared by two guides never
 *  leaks one destination's fares onto the other's page. */
export function resolveIntlFares(
  slug: string,
  intl: IntlDealsData | null,
): DestinationOriginFare[] {
  const airport = INTL_DESTINATION_AIRPORT[slug];
  if (!airport || !intl) return [];
  const out: DestinationOriginFare[] = [];
  for (const key of Object.keys(intl.routes).sort()) {
    const route = intl.routes[key];
    if (route.destination !== airport.code) continue;
    if (route.destination_slug && route.destination_slug !== slug) continue;
    const fare = toOriginFare(key, route, "weekly", intl.as_of);
    if (fare) out.push(fare);
  }
  return out;
}

/** The cheapest-fare origin among resolved fares. Ties break to the
 *  alphabetically first origin code so the default is deterministic. */
export function cheapestOrigin(
  fares: DestinationOriginFare[],
): string | null {
  let best: DestinationOriginFare | null = null;
  for (const f of [...fares].sort((a, b) =>
    a.origin.localeCompare(b.origin),
  )) {
    if (!best || f.cheapest.price_min < best.cheapest.price_min) best = f;
  }
  return best?.origin ?? null;
}

export type OriginResolution = {
  origin: string;
  reason: "stored" | "hub" | "cheapest";
};

/** Default origin for the module, in the decided order: the
 *  reader's stored fares preference (shared with the /travel hub —
 *  only when it has fares HERE), then their Hub-location origin
 *  (same detection the hub uses, run over THIS destination's
 *  origins), then the cheapest-fare origin. Null when there are no
 *  origins to choose from. */
export function resolveModuleOrigin(
  origins: string[],
  cheapest: string | null,
): OriginResolution | null {
  if (!origins.length) return null;
  const stored = readFaresOriginPref();
  if (stored && origins.includes(stored)) {
    return { origin: stored, reason: "stored" };
  }
  const hub = detectHubOrigin(origins);
  if (hub && origins.includes(hub)) {
    return { origin: hub, reason: "hub" };
  }
  return { origin: cheapest ?? origins[0], reason: "cheapest" };
}

/** Origins the fallback module's dropdown offers: the tracked
 *  origin set (the same labels the hub uses). No deals file is
 *  fetched to build this list. */
export const TRACKED_ORIGINS: string[] = Object.keys(ORIGIN_CITY_LABELS);

const MONTH_INDEX: Record<string, number> = {
  jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5,
  jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11,
};

function isoOf(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** A representative search window for the fallback module's Google
 *  Flights link: departing on the 10th of the cheapest month's next
 *  occurrence (the planner's cheapest_month is a range label like
 *  "Jun – Sep (monsoon)" — its first month anchors the window), for
 *  a ~3-week India trip or a ~1-week trip elsewhere, matching the
 *  fare bands. Unparseable labels degrade to ~2 months out. The
 *  window is SHOWN next to the link and the link is labelled a
 *  search link — it never poses as a fare. */
export function representativeWindow(
  cheapestMonthLabel: string | null | undefined,
  indiaTrip: boolean,
  today: string,
): { dep: string; ret: string } {
  const days = indiaTrip ? 20 : 7;
  const base = new Date(today + "T12:00:00");
  let dep: Date | null = null;
  const m = cheapestMonthLabel?.trim().toLowerCase().slice(0, 3);
  if (m && m in MONTH_INDEX) {
    const candidate = new Date(base.getFullYear(), MONTH_INDEX[m], 10);
    if (candidate.getTime() < base.getTime() + 7 * 86400000) {
      candidate.setFullYear(candidate.getFullYear() + 1);
    }
    dep = candidate;
  }
  if (!dep) {
    dep = new Date(base);
    dep.setDate(dep.getDate() + 60);
  }
  const ret = new Date(dep);
  ret.setDate(ret.getDate() + days);
  return { dep: isoOf(dep), ret: isoOf(ret) };
}
