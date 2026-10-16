import { useState, useEffect, useMemo } from "react";
import {
  Plane,
  CalendarDays,
  ShieldCheck,
  Luggage,
  Info,
  ChevronRight,
  ChevronDown,
  Sparkles,
} from "lucide-react";
import {
  ORIGIN_CITY_LABELS,
  dealRouteSource,
  detectHubRoute,
  festivalAdvice,
  fmtDate,
  fmtDateLong,
  futureEntries,
  loadFlightDeals,
  loadMetrosFlightDeals,
  mergeDealRoutes,
  metroFaresForOrigin,
  readFaresOriginPref,
  seasonForEntry,
  tripLengthLabel,
  writeFaresOriginPref,
  type CalendarEntry,
  type FestivalSeason,
  type FlightDealsData,
  type RouteData,
  type MetrosDealsData,
} from "@/lib/flightDeals";
import MetroFareRail from "@/components/MetroFareRail";
import BookingLinks from "@/components/BookingLinks";

/* Helpers shared with the destination-page fare module (Phase 2):
 * seasonForEntry + ORIGIN_CITY_LABELS live in lib/flightDeals.ts and
 * BookingLinks in components/BookingLinks.tsx — one copy each, so the
 * hub and the destination pages can never drift apart. */

/* ------------------------------------------------------------------ */
/* Price card                                                         */
/* ------------------------------------------------------------------ */

function PriceCard({
  entry,
  origin,
  dest,
  season,
  isBest,
}: {
  entry: CalendarEntry;
  origin: string;
  dest: string;
  season: FestivalSeason | null;
  isBest: boolean;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={`relative bg-card border rounded-2xl p-5 transition-all duration-200 hover:shadow-xl hover:shadow-primary/5 ${
        season ? "border-amber-500/40" : isBest ? "border-emerald-500/40" : "border-border hover:border-primary/30"
      }`}
    >
      {season && (
        <div className="absolute -top-3 left-4 bg-amber-500 text-black text-[11px] font-bold px-3 py-1 rounded-full flex items-center gap-1">
          <span>{season.emoji}</span> {season.name}
        </div>
      )}
      {isBest && !season && (
        <div className="absolute -top-3 left-4 bg-emerald-600 text-white text-[11px] font-bold px-3 py-1 rounded-full flex items-center gap-1">
          <Sparkles className="h-3 w-3" /> Lowest fare
        </div>
      )}

      <div className="flex items-start justify-between gap-3 mt-1">
        <div className="min-w-0">
          <div className="flex items-center gap-1.5 text-sm font-semibold text-foreground">
            <CalendarDays className="h-4 w-4 text-foreground/40 flex-shrink-0" />
            <span className="truncate">
              {fmtDate(entry.dep_date)} → {fmtDate(entry.ret_date)}
            </span>
          </div>
          <div className="text-[11px] text-foreground/45 mt-0.5">
            {tripLengthLabel(entry)}
          </div>
        </div>
        <div className="text-right flex-shrink-0">
          <div className={`text-xl font-bold tracking-tight ${isBest ? "text-emerald-600 dark:text-emerald-400" : "text-foreground"}`}>
            <span className="text-[13px] font-semibold text-foreground/45 mr-1">from</span>
            ${entry.price_min.toLocaleString()}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1.5 mt-3 text-[12px] text-foreground/55">
        <Plane className="h-3.5 w-3.5 text-foreground/35" />
        <span className="truncate">{entry.cheapest_airline}</span>
      </div>

      {entry.change_vs_prev && entry.change_vs_prev.delta > 0 && (
        <div className="mt-3 text-[12px] bg-emerald-500/10 border border-emerald-500/25 rounded-xl px-3 py-2 text-emerald-700 dark:text-emerald-300 font-medium">
          ↓ ${entry.change_vs_prev.delta.toLocaleString()} cheaper than the fare
          checked {entry.change_vs_prev.prev_as_of ? fmtDateLong(entry.change_vs_prev.prev_as_of) : "previously"}
        </div>
      )}

      {season && (
        <div className="mt-3 text-[12px] bg-amber-500/10 border border-amber-500/20 rounded-xl px-3 py-2 text-foreground/75">
          {festivalAdvice(entry, season)}
        </div>
      )}

      {expanded && (
        <div className="mt-3 pt-3 border-t border-border space-y-2">
          <div className="flex items-center gap-2 text-[12px] text-foreground/60">
            <Luggage className="h-3.5 w-3.5" />
            2 checked bags included — no basic economy fares shown
          </div>
          <div className="flex items-center gap-2 text-[12px] text-foreground/60">
            <ShieldCheck className="h-3.5 w-3.5" />
            Prices are snapshots and change frequently — verify before booking
          </div>
          {entry.fetched_as_of && (
            <div className="text-[12px] text-foreground/50">
              This fare was checked {fmtDateLong(entry.fetched_as_of)}.
            </div>
          )}
          <BookingLinks entry={entry} origin={origin} dest={dest} />
        </div>
      )}

      <button
        onClick={() => setExpanded(!expanded)}
        className="mt-3 text-[12px] font-medium text-primary/80 hover:text-primary flex items-center gap-1"
      >
        {expanded ? "Show less" : "Details & booking links"}
        <ChevronRight className={`h-3.5 w-3.5 transition-transform ${expanded ? "rotate-90" : ""}`} />
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Origin slicing (Kiran, 2026-10-15)                                 */
/*                                                                    */
/* The chip row used to list every daily route in raw file order —    */
/* EWR → BOM beside SFO → DEL, origins mixed with no reader logic.    */
/* Now ONE origin drives the whole section (rail, calendar): the      */
/* dropdown defaults to the reader's Hub-location origin, and         */
/* changing it re-slices everything. The route chips themselves are  */
/* GONE (holistic audit item 20): the metros rail cards are the one   */
/* route selector — same job, strictly more information.              */
/* ------------------------------------------------------------------ */

function cheapestUpcomingPrice(route: RouteData): number | null {
  const es = futureEntries(route);
  if (!es.length) return null;
  return Math.min(...es.map((e) => e.price_min));
}

/** Default route when an origin is (re)selected: the origin's route
 *  with the cheapest upcoming fare; ties (and no-fare routes) fall
 *  back to route-key A–Z so the choice is always deterministic. */
function defaultRouteForOrigin(
  routes: Record<string, RouteData>,
  origin: string,
): string {
  const keys = Object.keys(routes)
    .filter((k) => routes[k].origin === origin)
    .sort();
  let best = keys[0] ?? "";
  let bestPrice = Infinity;
  for (const k of keys) {
    const p = cheapestUpcomingPrice(routes[k]);
    if (p !== null && p < bestPrice) {
      bestPrice = p;
      best = k;
    }
  }
  return best;
}

/* ------------------------------------------------------------------ */
/* Main FlightDeals section — the Cheapest Fares hub                  */
/* ------------------------------------------------------------------ */

export default function FlightDeals() {
  const [data, setData] = useState<FlightDealsData | null>(null);
  const [metros, setMetros] = useState<MetrosDealsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [routeKey, setRouteKey] = useState<string>("");
  /* The selected origin airport + how it was arrived at. "detected" =
   * the reader's stored Hub location; "default" = no location stored,
   * so SFO is shown and labelled as the default, never as "yours";
   * "picked" = the reader chose it in the dropdown. */
  const [origin, setOrigin] = useState<string>("");
  const [originNote, setOriginNote] = useState<
    "detected" | "default" | "picked"
  >("default");

  useEffect(() => {
    Promise.all([loadFlightDeals(), loadMetrosFlightDeals()]).then(
      ([d, m]) => {
        setData(d);
        setMetros(m);
        if (d) {
          // One pool everywhere (§B audit fix): detection runs over the
          // COMBINED pool (daily ∪ weekly grid) — pre-filtering to a
          // subset made some readers silently get a default city's
          // fares. The detected route also fixes the initial origin.
          const merged = mergeDealRoutes(d, m);
          const keys = Object.keys(merged);
          const detectedRoute = detectHubRoute(keys);
          const detectedOrigin = detectedRoute
            ? detectedRoute.split("-")[0]
            : null;
          const originsPresent = [
            ...new Set(keys.map((k) => merged[k].origin)),
          ];
          /* The reader's stored fares preference (written here and
           * by the destination-page fare module — one shared pick)
           * wins when it names an origin this pool actually has;
           * otherwise the Hub-location detection, then the plain
           * SFO default, exactly as before. */
          const storedOrigin = readFaresOriginPref();
          const useStored =
            storedOrigin && originsPresent.includes(storedOrigin)
              ? storedOrigin
              : null;
          const initialOrigin =
            useStored ??
            detectedOrigin ??
            (originsPresent.includes("SFO")
              ? "SFO"
              : (originsPresent.sort()[0] ?? ""));
          setOrigin(initialOrigin);
          setOriginNote(
            useStored ? "picked" : detectedOrigin ? "detected" : "default",
          );
          setRouteKey(
            detectedRoute && detectedOrigin === initialOrigin
              ? detectedRoute
              : defaultRouteForOrigin(merged, initialOrigin),
          );
        }
        setLoading(false);
      },
    );
  }, []);

  /* The calendar can show any MERGED route: the daily 12 plus the
   * weekly metros grid's routes, merged with daily winning per route.
   * The metros rail below is the route selector for this pool. */
  const mergedRoutes = useMemo(
    () => mergeDealRoutes(data, metros),
    [data, metros],
  );

  /* Dropdown options: every origin present in the merged pool,
   * labelled "CODE — City", ordered by city name. */
  const originOptions = useMemo(() => {
    const byCode = new Map<string, string>();
    for (const r of Object.values(mergedRoutes)) {
      if (!byCode.has(r.origin)) {
        byCode.set(r.origin, ORIGIN_CITY_LABELS[r.origin] ?? r.origin_metro);
      }
    }
    return [...byCode.entries()]
      .map(([code, city]) => ({ code, city }))
      .sort((a, b) => a.city.localeCompare(b.city));
  }, [mergedRoutes]);

  const selectOrigin = (next: string) => {
    setOrigin(next);
    setOriginNote("picked");
    writeFaresOriginPref(next);
    setRouteKey(defaultRouteForOrigin(mergedRoutes, next));
  };
  const route = mergedRoutes[routeKey];
  const routeSource = data ? dealRouteSource(routeKey, data) : "daily";
  const routeAsOf = useMemo(() => {
    if (!route) return null;
    const dates = (route.calendar ?? [])
      .map((e) => e.fetched_as_of)
      .filter((d): d is string => !!d)
      .sort();
    return (
      dates[dates.length - 1] ??
      (routeSource === "daily" ? data?.as_of : metros?.as_of) ??
      null
    );
  }, [route, routeSource, data, metros]);

  /* Metros rail for the selected origin (merged data). */
  const railFares = useMemo(
    () =>
      origin
        ? metroFaresForOrigin(data, metros, origin)
        : [],
    [data, metros, origin],
  );

  /* Band model: every cell is the single ~3-week band, so no duration
   * filter — upcoming trips only; snapshot windows whose departure has
   * passed are dropped so stale prices never pose as current. */
  const entries = useMemo(() => {
    if (!route) return [];
    return futureEntries(route);
  }, [route]);

  const cheapest = useMemo(() => {
    if (!entries.length) return null;
    return entries.reduce((a, b) => (b.price_min < a.price_min ? b : a));
  }, [entries]);

  if (loading) {
    return (
      <section className="mb-0">
        <div className="flex items-center justify-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
        </div>
      </section>
    );
  }

  if (!data || !route) return null;

  const bandLabel = data.band?.label ?? "~3-week trips";
  const bandRange = data.band
    ? `${data.band.min_days}–${data.band.max_days} days`
    : "19–23 days";

  return (
    <section className="mb-0" id="flight-deals">
      {/* ── Section header — redesign header system (Kiran approved
          mockup, 2026-10-15): gold kicker, serif navy title, hairline
          with a gold tick, like every /travel section. The section
          itself carries no bottom margin — TravelPage wraps it in
          the cream fares panel, which owns the spacing. No global
          check-date pill (audit item 22): freshness renders per
          card, in the two standard stamp formats only. ─────────── */}
      <div className="mb-6">
        <div className="relative border-b border-[#0B1D3A]/10 pb-3">
          <p className="text-[11px] font-bold uppercase tracking-[2px] text-[#7a5c14] mb-1">
            Fly for less
          </p>
          <h2 className="font-serif text-xl font-bold leading-none" style={{ color: "#0B1D3A" }}>
            Cheapest Fares
          </h2>
          <span className="absolute left-0 -bottom-px h-[2px] w-10 bg-[#D4A843]" />
        </div>
        <p className="text-sm text-foreground/55 leading-relaxed mt-3">
          Round-trip fares from US metros to India — {bandLabel} ({bandRange}),
          next 3 months.
        </p>
      </div>

      {/* ── Origin dropdown — defaults to the reader's Hub-location
          origin; when no location is stored it shows SFO and says
          "Default" plainly. Changing it re-slices the rail and the
          calendar to that origin. ──────────────────────────────── */}
      <div className="flex items-center gap-2.5 mb-4 flex-wrap">
        <label
          htmlFor="fares-origin"
          className="text-[12px] font-bold uppercase tracking-wider text-foreground/50"
        >
          Flying from
        </label>
        <div className="relative">
          <select
            id="fares-origin"
            value={origin}
            onChange={(e) => selectOrigin(e.target.value)}
            className="appearance-none bg-card border border-rule rounded-full pl-4 pr-9 py-2 text-sm font-semibold text-foreground hover:border-primary focus:outline-none focus:border-primary cursor-pointer"
          >
            {originOptions.map((o) => (
              <option key={o.code} value={o.code}>
                {o.code} — {o.city}
              </option>
            ))}
          </select>
          <ChevronDown className="h-4 w-4 text-foreground/40 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>
        {originNote === "detected" && (
          <span className="text-[11px] text-foreground/40">
            Set from your location
          </span>
        )}
        {originNote === "default" && (
          <span className="text-[11px] text-foreground/40">
            Default airport — pick yours
          </span>
        )}
      </div>

      {/* ── India metros rail — every metro from this origin. The
          rail cards are THE route selector (audit item 20): the old
          chip row duplicated this job with codes only. Renders even
          for a single-fare origin (BOS/IAD/ATL have only their daily
          DEL route until their weekly-grid pairs fill) — the rail is
          the only selector, so gating it on >1 left those origins
          with no heading and no way to pick the route. ──────────── */}
      {railFares.length >= 1 && (
        <div className="mb-6">
          <h3 className="font-serif text-base font-bold text-foreground mb-1">
            From {origin} — cheapest to each India metro
          </h3>
          <p className="text-[12px] text-foreground/50 mb-3">
            Tap a metro to see its calendar.
          </p>
          <MetroFareRail
            fares={railFares}
            variant="travel"
            selectedRouteKey={routeKey}
            onSelect={setRouteKey}
          />
        </div>
      )}

      {/* ── Best Deal spotlight REMOVED (audit item 3): it rendered
          the selected route's cheapest fare a third time — metro
          card above, price card #1 below. The calendar's first card
          already leads with that fare. ─────────────────────────── */}

      {/* ── Price cards ────────────────────────────────────── */}
      {entries.length === 0 ? (
        <div className="text-center py-12 bg-card border border-border rounded-2xl">
          <Plane className="h-8 w-8 text-foreground/20 mx-auto mb-3" />
          <p className="text-foreground/50 text-sm px-4">
            This route's snapshot windows (checked {fmtDateLong(routeAsOf ?? data.as_of)}) have all departed.
            <br />
            Fresh fares are on the way — meanwhile, try another metro above.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {entries.map((entry) => (
            <PriceCard
              key={`${entry.dep_date}-${entry.ret_date}`}
              entry={entry}
              origin={route.origin}
              dest={route.destination}
              season={seasonForEntry(entry, data.festival_seasons)}
              isBest={cheapest !== null && entry.price_min === cheapest.price_min && entry.dep_date === cheapest.dep_date}
            />
          ))}
        </div>
      )}

      {/* ── Midweek tip ────────────────────────────────────── */}
      <div className="mt-4 bg-card border border-border rounded-2xl px-5 py-4 flex gap-3">
        <Info className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
        <p className="text-[13px] text-foreground/65 leading-relaxed">
          <strong className="text-foreground/85">Tip:</strong> Tue–Thu departures
          are typically $80–$220 cheaper than Fri/Sun on US–India routes.
        </p>
      </div>

      {/* ── Per-destination fare lines REMOVED (audit item 2): the
          block repeated the trending cards' fare lines; per-
          destination fares belong on the destination pages. ────── */}

      {/* ── Trust footer — ONE paragraph (audit item 11): the fare
          spec (round-trip, per person, economy, max 1 stop, 2 bags)
          is stated here once instead of on every card. ─────────── */}
      <div className="mt-4 rounded-2xl border border-border bg-foreground/[0.02] px-5 py-4">
        <div className="flex items-start gap-2.5">
          <ShieldCheck className="h-4 w-4 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
          <p className="text-[12px] text-foreground/55 leading-relaxed">
            <span className="font-semibold text-foreground/75">Our pricing promise</span>
            {" "}— Cheapest fare we found for each window, shown as a from-price;
            other dates can cost more. All fares: round-trip, per person,
            economy, max 1 stop, 2 checked bags included. Prices checked{" "}
            {fmtDateLong(data.as_of)} — fares change, verify before booking.
            We link to airlines directly and Google Flights — no hidden
            commissions.
          </p>
        </div>
      </div>

      {/* ── Fare-alert box REMOVED (audit item 1): a "Coming soon"
          promise of a feature that doesn't exist is not a control.
          The "Planning beyond India?" transition line is removed
          with it (audit item 4) — the guides heading follows. ──── */}
    </section>
  );
}
