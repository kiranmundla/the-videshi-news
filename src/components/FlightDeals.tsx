import { useState, useEffect, useMemo } from "react";
import { Link } from "react-router-dom";
import {
  Plane,
  CalendarDays,
  Bell,
  ExternalLink,
  ShieldCheck,
  Luggage,
  Info,
  ChevronRight,
  Sparkles,
  BadgePercent,
  ArrowRight,
} from "lucide-react";
import {
  DEFAULT_ROUTES,
  airlineBookingUrl,
  cheapestIntlFare,
  dealRouteSource,
  detectHubOrigin,
  detectHubRoute,
  fmtDate,
  fmtDateLong,
  futureEntries,
  googleFlightsUrl,
  loadFlightDeals,
  loadIntlFlightDeals,
  loadMetrosFlightDeals,
  mergeDealRoutes,
  metroFaresForOrigin,
  tripLengthLabel,
  type CalendarEntry,
  type FestivalSeason,
  type FlightDealsData,
  type IntlDealsData,
  type MetrosDealsData,
} from "@/lib/flightDeals";
import MetroFareRail from "@/components/MetroFareRail";
import {
  loadDestinations,
  selectTrendingCards,
  type TrendingDestination,
} from "@/lib/trendingDestinations";

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

function seasonForEntry(entry: CalendarEntry, seasons: FestivalSeason[]): FestivalSeason | null {
  const dep = new Date(entry.dep_date + "T12:00:00");
  for (const s of seasons) {
    const start = new Date(s.start[0], s.start[1] - 1, s.start[2]);
    const end = new Date(s.end[0], s.end[1] - 1, s.end[2]);
    // Entry overlaps season if dep is within ±10 days of season window
    const lo = new Date(start); lo.setDate(lo.getDate() - 10);
    const hi = new Date(end); hi.setDate(hi.getDate() + 10);
    if (dep >= lo && dep <= hi) return s;
  }
  return null;
}

function monthLabel(entry: CalendarEntry): string {
  const d = new Date(entry.dep_date + "T12:00:00");
  return d.toLocaleDateString("en-US", { month: "long", year: "numeric" });
}

/** Booking links for a fare (Kiran's decision, 2026-10-15): the
 *  airline's own deep link is primary ONLY when the carrier has a
 *  verified template; "Compare on Google Flights" is always present.
 *  No template → Google Flights only. Never a bare homepage. */
function BookingLinks({
  entry,
  origin,
  dest,
}: {
  entry: CalendarEntry;
  origin: string;
  dest: string;
}) {
  const gfUrl = googleFlightsUrl(origin, dest, entry.dep_date, entry.ret_date);
  const airlineUrl = airlineBookingUrl(
    entry.cheapest_airline,
    origin,
    dest,
    entry.dep_date,
    entry.ret_date,
  );
  return (
    <div className="flex flex-col gap-1.5 mt-1">
      {airlineUrl && (
        <a
          href={airlineUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 text-[13px] font-semibold text-primary hover:underline"
        >
          Book on {entry.cheapest_airline} <ExternalLink className="h-3.5 w-3.5" />
        </a>
      )}
      <a
        href={gfUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1.5 text-[13px] font-semibold text-primary hover:underline"
      >
        Compare on Google Flights <ExternalLink className="h-3.5 w-3.5" />
      </a>
    </div>
  );
}

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
            {tripLengthLabel(entry)} · {fmtDateLong(entry.dep_date)}
          </div>
        </div>
        <div className="text-right flex-shrink-0">
          <div className={`text-xl font-bold tracking-tight ${isBest ? "text-emerald-600 dark:text-emerald-400" : "text-foreground"}`}>
            <span className="text-[13px] font-semibold text-foreground/45 mr-1">from</span>
            ${entry.price_min.toLocaleString()}
          </div>
          <div className="text-[11px] text-foreground/45">per person round-trip</div>
        </div>
      </div>

      <div className="flex items-center gap-1.5 mt-3 text-[12px] text-foreground/55">
        <Plane className="h-3.5 w-3.5 text-foreground/35" />
        <span className="truncate">{entry.cheapest_airline} · max 1 stop · 2 checked bags</span>
      </div>

      {entry.change_vs_prev && entry.change_vs_prev.delta > 0 && (
        <div className="mt-3 text-[12px] bg-emerald-500/10 border border-emerald-500/25 rounded-xl px-3 py-2 text-emerald-700 dark:text-emerald-300 font-medium">
          ↓ ${entry.change_vs_prev.delta.toLocaleString()} cheaper than the fare
          checked {entry.change_vs_prev.prev_as_of ? fmtDateLong(entry.change_vs_prev.prev_as_of) : "previously"}
        </div>
      )}

      {season && (
        <div className="mt-3 text-[12px] bg-amber-500/10 border border-amber-500/20 rounded-xl px-3 py-2 text-foreground/75">
          {season.note} · Book {season.book_by_months} months ahead for best fares
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
/* Per-destination fare lines                                         */
/*                                                                    */
/* One line per trending destination that has real fare data: India   */
/* destinations from the daily matrix (own-metro routes only — the    */
/* destinations builder attaches them), international destinations    */
/* from the weekly matrix, preferring the reader's own origin         */
/* airport. Destinations without data simply don't appear — a fare   */
/* is never borrowed from another destination.                        */
/* ------------------------------------------------------------------ */

const INTL_AIRPORT_BY_SLUG: Record<string, string> = {
  australia: "SYD",
  bali: "DPS",
  cabo: "SJD",
  egypt: "CAI",
  fiji: "NAN",
  france: "CDG",
  greece: "ATH",
  hawaii: "HNL",
};

type FareLine = {
  slug: string;
  name: string;
  guideUrl: string;
  routeLabel: string;
  price: number;
  datesLabel: string;
  lengthLabel: string;
  cadenceLabel: string;
  gfUrl: string;
};

function buildFareLines(
  cards: TrendingDestination[],
  intl: IntlDealsData | null,
): FareLine[] {
  const lines: FareLine[] = [];
  const intlOrigins = intl
    ? [...new Set(Object.values(intl.routes).map((r) => r.origin))]
    : [];
  const preferredOrigin = intlOrigins.length
    ? detectHubOrigin(intlOrigins)
    : null;
  for (const d of cards) {
    const airport = INTL_AIRPORT_BY_SLUG[d.slug];
    if (airport) {
      if (!intl) continue;
      const hit = cheapestIntlFare(intl, airport, preferredOrigin);
      if (!hit) continue;
      const [dep, ret] = [hit.entry.dep_date, hit.entry.ret_date];
      lines.push({
        slug: d.slug,
        name: d.name,
        guideUrl: d.guide_url,
        routeLabel: `${hit.route.origin} → ${hit.route.destination} · ${hit.route.dest_metro}`,
        price: hit.entry.price_min,
        datesLabel: `${fmtDate(dep)} → ${fmtDate(ret)}`,
        lengthLabel: tripLengthLabel(hit.entry),
        cadenceLabel: `Indicative · checked weekly · fares as of ${fmtDateLong(intl.as_of)}`,
        gfUrl: googleFlightsUrl(hit.route.origin, hit.route.destination, dep, ret),
      });
    } else if (d.fare_from) {
      const f = d.fare_from;
      const [o, dst] = f.route.split("-");
      const [dep, ret] = f.date_range.split(" → ");
      lines.push({
        slug: d.slug,
        name: d.name,
        guideUrl: d.guide_url,
        routeLabel: `${f.route} · ${f.dest_metro}`,
        price: f.price_min,
        datesLabel: `${fmtDate(dep)} → ${fmtDate(ret)}`,
        lengthLabel: f.duration_days
          ? `${f.duration_days}-day trip`
          : f.weeks
            ? `${f.weeks}-week trip`
            : "round trip",
        cadenceLabel: `Fares checked ${fmtDateLong(f.as_of)}`,
        gfUrl: googleFlightsUrl(o, dst, dep, ret),
      });
    }
  }
  return lines;
}

function DestinationFareLines() {
  const [lines, setLines] = useState<FareLine[]>([]);
  useEffect(() => {
    let alive = true;
    Promise.all([loadDestinations(), loadIntlFlightDeals()]).then(
      ([destData, intl]) => {
        if (!alive || !destData) return;
        setLines(buildFareLines(selectTrendingCards(destData, 8), intl));
      },
    );
    return () => {
      alive = false;
    };
  }, []);

  if (!lines.length) return null;
  return (
    <div className="mt-8">
      <h3 className="font-serif text-xl font-bold text-foreground mb-1">
        Fares to top destinations
      </h3>
      <p className="text-[12px] text-foreground/50 mb-4">
        Cheapest upcoming fares for the destinations trending above — from
        your nearest airport where we track it.
      </p>
      <div className="divide-y divide-border border border-border rounded-2xl bg-card overflow-hidden">
        {lines.map((l) => (
          <div
            key={l.slug}
            className="flex items-center gap-3 px-4 py-3 hover:bg-foreground/[0.02]"
          >
            <div className="min-w-0 flex-1">
              <Link
                to={l.guideUrl}
                className="text-[14px] font-semibold text-foreground hover:text-primary truncate block"
              >
                {l.name}
              </Link>
              <div className="text-[11px] text-foreground/50 truncate">
                {l.routeLabel} · {l.cadenceLabel}
              </div>
            </div>
            <a
              href={l.gfUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-right flex-shrink-0 group"
              title="See these dates on Google Flights"
            >
              <div className="text-[15px] font-bold text-foreground group-hover:text-primary">
                <span className="text-[11px] font-semibold text-foreground/45 mr-0.5">from</span>
                ${l.price.toLocaleString()}
              </div>
              <div className="text-[11px] text-foreground/50">
                {l.datesLabel} · {l.lengthLabel}
              </div>
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Main FlightDeals section — the Cheapest Fares hub                  */
/* ------------------------------------------------------------------ */

export default function FlightDeals() {
  const [data, setData] = useState<FlightDealsData | null>(null);
  const [metros, setMetros] = useState<MetrosDealsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [routeKey, setRouteKey] = useState<string>("");

  useEffect(() => {
    Promise.all([loadFlightDeals(), loadMetrosFlightDeals()]).then(
      ([d, m]) => {
        setData(d);
        setMetros(m);
        if (d) {
          // One pool everywhere (§B audit fix): detection runs over ALL
          // routes in the snapshot — the old code pre-filtered to
          // DEFAULT_ROUTES, so e.g. an Atlanta reader with an ATL-DEL
          // route in the data silently got a default city's fares.
          const keys = Object.keys(d.routes);
          const fallback =
            DEFAULT_ROUTES.find((k) => keys.includes(k)) ?? keys[0] ?? "";
          setRouteKey(detectHubRoute(keys) ?? fallback);
        }
        setLoading(false);
      },
    );
  }, []);

  /* The calendar can show any MERGED route: the daily 12 plus the
   * weekly metros grid's 38, merged with daily winning per route.
   * The route pills stay the daily core (the curated corridors); the
   * metros rail below is how grid routes are reached. */
  const mergedRoutes = useMemo(
    () => mergeDealRoutes(data, metros),
    [data, metros],
  );
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

  /* Metros rail for the selected route's origin (merged data). */
  const railFares = useMemo(
    () =>
      route
        ? metroFaresForOrigin(data, metros, route.origin)
        : [],
    [data, metros, route],
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
      <section className="mb-12">
        <div className="flex items-center justify-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
        </div>
      </section>
    );
  }

  if (!data || !route) return null;

  const availableRoutes = Object.keys(data.routes);
  const bandLabel = data.band?.label ?? "~3-week trips";
  const bandRange = data.band
    ? `${data.band.min_days}–${data.band.max_days} days`
    : "19–23 days";

  return (
    <section className="mb-12" id="flight-deals">
      {/* ── Section header ─────────────────────────────────── */}
      <div className="relative mb-6 -mx-4 px-4 py-10 md:py-12 rounded-2xl overflow-hidden bg-gradient-to-br from-[#0b1d3a] via-[#12294d] to-[#1a3a5c]">
        <div
          className="absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage:
              "url(\"data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 40h80M40 0v80' stroke='%23ffffff' stroke-width='1'/%3E%3C/svg%3E\")",
          }}
        />
        <div className="absolute -top-10 right-10 w-72 h-72 bg-sky-400/15 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/4 w-56 h-56 bg-amber-400/10 rounded-full blur-3xl" />

        <div className="relative z-10 max-w-3xl">
          <div className="flex items-center gap-2 mb-3 flex-wrap">
            <span className="text-xs font-bold uppercase tracking-widest text-sky-300 bg-sky-500/15 px-3 py-1 rounded-full flex items-center gap-1.5">
              <Plane className="h-3.5 w-3.5" /> Cheapest Fares
            </span>
            <span className="text-[11px] font-bold text-[#0B1D3A] bg-[#D4A843] px-3 py-1 rounded-full">
              Fares checked {fmtDateLong(data.as_of)}
            </span>
          </div>
          <h2 className="font-serif text-3xl md:text-4xl font-bold tracking-tight leading-tight text-white">
            When's the cheapest time<br />to fly home?
          </h2>
          <p className="text-white/65 mt-3 text-[15px] md:text-base max-w-xl leading-relaxed">
            Real round-trip fares from US metros to India for {bandLabel} over
            the next 3 months — with festival-aware pricing, so you know{" "}
            <em>why</em> December costs more.
          </p>
        </div>
      </div>

      {/* ── Route selector ─────────────────────────────────── */}
      <div className="flex gap-2 overflow-x-auto pb-1 mb-5" style={{ WebkitOverflowScrolling: "touch" }}>
        {availableRoutes.map((rk) => {
          const r = data.routes[rk];
          return (
            <button
              key={rk}
              onClick={() => setRouteKey(rk)}
              className={`whitespace-nowrap px-4 py-2 rounded-full text-sm font-semibold border transition-colors ${
                routeKey === rk
                  ? "bg-primary text-primary-foreground border-primary"
                  : "border-rule text-foreground/75 hover:text-primary hover:border-primary"
              }`}
            >
              {r.origin} → {r.destination}
            </button>
          );
        })}
      </div>

      <p className="text-[12px] text-foreground/45 mb-4 -mt-2">
        {route.origin_metro} → {route.dest_metro} · {bandLabel} ({bandRange}) · per person ·{" "}
        {routeSource === "weekly" ? "checked weekly · " : ""}fares as of{" "}
        {fmtDateLong(routeAsOf ?? data.as_of)}
      </p>

      {/* ── India metros rail — every metro from this origin ── */}
      {railFares.length > 1 && (
        <div className="mb-6">
          <h3 className="font-serif text-lg font-bold text-foreground mb-1">
            From {route.origin} — cheapest to each India metro
          </h3>
          <p className="text-[12px] text-foreground/50 mb-3">
            Tap a metro to see its calendar. Delhi, Mumbai, Bengaluru,
            Hyderabad and Kolkata — daily-checked routes and the weekly
            grid together, each card stamped with its own check date.
          </p>
          <MetroFareRail
            fares={railFares}
            variant="travel"
            selectedRouteKey={routeKey}
            onSelect={setRouteKey}
          />
        </div>
      )}

      {/* ── Cheapest-month spotlight ───────────────────────── */}
      {cheapest && (
        <div className="mb-5 relative overflow-hidden rounded-2xl border border-emerald-500/40 bg-emerald-500/[0.07] px-5 py-4">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="inline-flex items-center gap-1.5 bg-emerald-600 text-white text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wide">
              <BadgePercent className="h-3.5 w-3.5" /> Best deal
            </span>
            <p className="text-[15px] text-foreground/85">
              Cheapest from <strong>{route.origin}</strong>:{" "}
              <strong className="text-emerald-700 dark:text-emerald-400">{monthLabel(cheapest)}</strong>
              {" "}— {bandLabel} from{" "}
              <strong className="text-emerald-700 dark:text-emerald-400">${cheapest.price_min.toLocaleString()}</strong>
              <span className="text-foreground/50">
                {" "}({fmtDate(cheapest.dep_date)} → {fmtDate(cheapest.ret_date)} · {cheapest.cheapest_airline})
              </span>
            </p>
          </div>
        </div>
      )}

      {/* ── Price cards ────────────────────────────────────── */}
      {entries.length === 0 ? (
        <div className="text-center py-12 bg-card border border-border rounded-2xl">
          <Plane className="h-8 w-8 text-foreground/20 mx-auto mb-3" />
          <p className="text-foreground/50 text-sm px-4">
            This route's snapshot windows (checked {fmtDateLong(routeAsOf ?? data.as_of)}) have all departed.
            <br />
            Fresh fares are on the way — meanwhile, try another route above.
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

      {/* ── Per-destination fare lines ─────────────────────── */}
      <DestinationFareLines />

      {/* ── Trust footer ───────────────────────────────────── */}
      <div className="mt-4 rounded-2xl border border-border bg-foreground/[0.02] px-5 py-4">
        <div className="flex items-start gap-2.5">
          <ShieldCheck className="h-4 w-4 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
          <div className="text-[12px] text-foreground/55 leading-relaxed">
            <p className="font-semibold text-foreground/75 mb-1">Our pricing promise</p>
            <ul className="space-y-1 list-none">
              <li>· Prices checked {fmtDateLong(data.as_of)} — fares change frequently, always verify before booking.</li>
              <li>· Cheapest fare we found for each window, shown as a from-price — other dates in the window can cost more.</li>
              <li>· 2 checked bags included — basic economy fares excluded.</li>
              <li>· Max 1 stop. Economy cabin. Per-person round-trip.</li>
              <li>
                · We link to Google Flights and airlines directly —{" "}
                <span className="font-medium text-foreground/70">no sketchy booking sites, no hidden commissions.</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* ── Alert CTA ──────────────────────────────────────── */}
      <div className="mt-4 flex items-center justify-between bg-primary/[0.06] border border-primary/20 rounded-2xl px-5 py-4">
        <div className="flex items-center gap-3">
          <Bell className="h-5 w-5 text-primary flex-shrink-0" />
          <p className="text-[13px] text-foreground/75">
            Want a ping when {route.origin} → {route.destination} drops?
          </p>
        </div>
        <span className="text-[11px] font-semibold text-primary bg-primary/10 px-3 py-1.5 rounded-full whitespace-nowrap">
          Coming soon
        </span>
      </div>

      <p className="mt-4 text-[12px] text-foreground/40 flex items-center gap-1">
        Planning beyond India? See the destination guides below
        <ArrowRight className="h-3.5 w-3.5" />
      </p>
    </section>
  );
}
