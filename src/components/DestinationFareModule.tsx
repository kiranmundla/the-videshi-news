import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ChevronDown, ExternalLink, Sparkles } from "lucide-react";
import {
  INDIA_METROS,
  ORIGIN_CITY_LABELS,
  festivalAdvice,
  fmtRange,
  googleFlightsUrl,
  loadFlightDeals,
  loadIntlFlightDeals,
  loadMetrosFlightDeals,
  seasonForEntry,
  todayStr,
  tripLengthLabel,
  writeFaresOriginPref,
  type CalendarEntry,
  type FlightDealsData,
  type IntlDealsData,
  type MetrosDealsData,
} from "@/lib/flightDeals";
import {
  INDIA_DESTINATION_METRO,
  INTL_DESTINATION_AIRPORT,
  TRACKED_ORIGINS,
  cheapestOrigin,
  destinationFareClass,
  representativeWindow,
  resolveIndiaFares,
  resolveIntlFares,
  resolveModuleOrigin,
  type DestinationOriginFare,
} from "@/lib/destinationFares";
import type { DestinationFact } from "@/lib/travelPlanner";
import BookingLinks from "@/components/BookingLinks";

/* ------------------------------------------------------------------ */
/* Destination-page fare module (Phase 2, 2026-10-15 — spec:          */
/* research/travel-page-relook-2026-10-15.md §5). Replaces the navy   */
/* "Plan this trip" band under the Quick Facts bar on every           */
/* destination page; the planner facts the band carried (cheapest     */
/* month / best season) fold into this module's header.               */
/*                                                                    */
/* One template, three data classes (lib/destinationFares.ts):        */
/*  A — India guide with its OWN tracked metro (karnataka → BLR):     */
/*      real fares from the daily + weekly-grid files.                */
/*  B — weekly intl matrix destination (australia → SYD): real       */
/*      fares from flight-deals-intl.json once its routes land.       */
/*  fallback — no tracked fares: planner facts + a clearly labelled   */
/*      Google Flights SEARCH link. Never an invented fare, never     */
/*      another destination's fare borrowed.                          */
/*                                                                    */
/* Fetch discipline: the class comes from the slug, so the module     */
/* fetches only its class's deals file(s) (≤ ~5 KB gzip) and never    */
/* travel-destinations.json.                                          */
/* ------------------------------------------------------------------ */

function byCity(origins: string[]): string[] {
  return [...origins].sort((a, b) =>
    (ORIGIN_CITY_LABELS[a] ?? a).localeCompare(ORIGIN_CITY_LABELS[b] ?? b),
  );
}

function OriginSelect({
  id,
  origins,
  value,
  onChange,
}: {
  id: string;
  origins: string[];
  value: string;
  onChange: (next: string) => void;
}) {
  return (
    <div className="flex items-center gap-2.5 flex-wrap">
      <label
        htmlFor={id}
        className="text-[12px] font-bold uppercase tracking-wider text-foreground/50"
      >
        Flying from
      </label>
      <div className="relative">
        <select
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="appearance-none bg-card border border-border rounded-full pl-4 pr-9 py-2 text-sm font-semibold text-foreground hover:border-primary focus:outline-none focus:border-primary cursor-pointer"
        >
          {origins.map((code) => (
            <option key={code} value={code}>
              {code} — {ORIGIN_CITY_LABELS[code] ?? code}
            </option>
          ))}
        </select>
        <ChevronDown className="h-4 w-4 text-foreground/40 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
      </div>
    </div>
  );
}

function FareRow({
  entry,
  origin,
  dest,
  isCheapest,
  seasons,
}: {
  entry: CalendarEntry;
  origin: string;
  dest: string;
  isCheapest: boolean;
  seasons: Parameters<typeof seasonForEntry>[1] | null;
}) {
  const season = seasons ? seasonForEntry(entry, seasons) : null;
  return (
    <div className="py-3.5 border-t border-border first:border-t-0 first:pt-1 last:pb-0">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-semibold text-foreground">
              {fmtRange(entry.dep_date, entry.ret_date)}
            </span>
            {isCheapest && (
              <span className="inline-flex items-center gap-1 bg-emerald-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                <Sparkles className="h-3 w-3" /> Lowest fare
              </span>
            )}
          </div>
          <div className="text-[11px] text-foreground/45 mt-0.5">
            {tripLengthLabel(entry)} · {entry.cheapest_airline}
          </div>
        </div>
        <div className="text-right flex-shrink-0">
          <span className="text-[13px] font-semibold text-foreground/45 mr-1">
            from
          </span>
          <span
            className={`text-lg font-bold tracking-tight ${isCheapest ? "text-emerald-600 dark:text-emerald-400" : "text-foreground"}`}
          >
            ${entry.price_min.toLocaleString()}
          </span>
        </div>
      </div>
      {season && (
        <div className="mt-2.5 text-[12px] bg-amber-500/10 border border-amber-500/20 rounded-xl px-3 py-2 text-foreground/75">
          {season.emoji} {festivalAdvice(entry, season)}
        </div>
      )}
      <BookingLinks entry={entry} origin={origin} dest={dest} />
    </div>
  );
}

export default function DestinationFareModule({
  slug,
  title,
  indiaTrip,
  destFact,
  featuredIn,
}: {
  slug: string;
  title: string;
  indiaTrip: boolean;
  destFact: DestinationFact | null;
  featuredIn: string[];
}) {
  const cls = destinationFareClass(slug);
  const [daily, setDaily] = useState<FlightDealsData | null>(null);
  const [metros, setMetros] = useState<MetrosDealsData | null>(null);
  const [intl, setIntl] = useState<IntlDealsData | null>(null);
  const [loaded, setLoaded] = useState(cls === "fallback");
  const [picked, setPicked] = useState<string | null>(null);

  /* Fetch ONLY the file(s) this destination's class needs. */
  useEffect(() => {
    let live = true;
    if (cls === "A") {
      Promise.all([loadFlightDeals(), loadMetrosFlightDeals()]).then(
        ([d, m]) => {
          if (!live) return;
          setDaily(d);
          setMetros(m);
          setLoaded(true);
        },
      );
    } else if (cls === "B") {
      loadIntlFlightDeals().then((d) => {
        if (!live) return;
        setIntl(d);
        setLoaded(true);
      });
    }
    return () => {
      live = false;
    };
  }, [cls]);

  const fares: DestinationOriginFare[] = useMemo(() => {
    if (cls === "A") return resolveIndiaFares(slug, daily, metros);
    if (cls === "B") return resolveIntlFares(slug, intl);
    return [];
  }, [cls, slug, daily, metros, intl]);

  const hasFares = fares.length > 0;

  /* ── Fares view state ─────────────────────────────────────────── */
  const fareOrigins = useMemo(
    () => byCity(fares.map((f) => f.origin)),
    [fares],
  );
  const fareDefault = useMemo(
    () =>
      hasFares
        ? resolveModuleOrigin(
            fares.map((f) => f.origin),
            cheapestOrigin(fares),
          )
        : null,
    [fares, hasFares],
  );
  const fareOrigin = picked ?? fareDefault?.origin ?? "";
  const selectedFare = fares.find((f) => f.origin === fareOrigin) ?? null;

  /* ── Fallback view state ──────────────────────────────────────── */
  const fbOrigins = useMemo(() => byCity(TRACKED_ORIGINS), []);
  const fbDefault = useMemo(
    () =>
      resolveModuleOrigin(
        ["SFO", ...TRACKED_ORIGINS.filter((o) => o !== "SFO")],
        null,
      ),
    [],
  );
  const fbOrigin = picked ?? fbDefault?.origin ?? "SFO";
  const fbReason = picked ? null : fbDefault?.reason ?? null;
  const window = useMemo(
    () => representativeWindow(destFact?.cheapest_month, indiaTrip, todayStr()),
    [destFact, indiaTrip],
  );

  const selectOrigin = (next: string) => {
    setPicked(next);
    writeFaresOriginPref(next);
  };

  const destCode =
    cls === "A"
      ? INDIA_DESTINATION_METRO[slug]
      : cls === "B"
        ? INTL_DESTINATION_AIRPORT[slug].codes.join(" / ")
        : "";
  const destCity =
    cls === "A"
      ? (INDIA_METROS.find((m) => m.code === destCode)?.name ?? destCode)
      : cls === "B"
        ? INTL_DESTINATION_AIRPORT[slug].city
        : title;
  const seasons = cls === "A" ? (daily?.festival_seasons ?? []) : null;

  return (
    <div className="container mt-5">
      <div className="bg-card border border-border rounded-2xl p-5">
        {/* ── Header — the planner facts the old navy band carried,
            folded in (cheapest month / best season / featured). ── */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-lg">✈️</span>
          <h2 className="font-serif text-lg font-bold text-foreground">
            Flights to {title}
          </h2>
        </div>
        {destFact && (
          <p className="text-[13px] text-foreground/55 leading-relaxed mt-1.5">
            💰 <strong className="text-foreground/80">Cheapest:</strong>{" "}
            {destFact.cheapest_month}
            <span className="mx-1.5 text-foreground/30">·</span>🗓️{" "}
            <strong className="text-foreground/80">Best season:</strong>{" "}
            {destFact.best_season}
            {featuredIn.length > 0 && (
              <>
                <span className="mx-1.5 text-foreground/30">·</span>⭐ Featured
                in: {featuredIn.join(", ")}
              </>
            )}
          </p>
        )}

        {!loaded ? (
          <p className="text-[13px] text-foreground/45 mt-3">
            Checking live fares…
          </p>
        ) : hasFares && selectedFare ? (
          <>
            {/* ── Fares view (classes A + B with data) ─────────── */}
            <div className="mt-4">
              <OriginSelect
                id={`dest-fares-origin-${slug}`}
                origins={fareOrigins}
                value={fareOrigin}
                onChange={selectOrigin}
              />
              {picked === null && fareDefault?.reason === "hub" && (
                <p className="text-[11px] text-foreground/40 mt-1.5">
                  Set from your location
                </p>
              )}
              {picked === null && fareDefault?.reason === "stored" && (
                <p className="text-[11px] text-foreground/40 mt-1.5">
                  Your saved airport
                </p>
              )}
              {picked === null && fareDefault?.reason === "cheapest" && (
                <p className="text-[11px] text-foreground/40 mt-1.5">
                  Showing fares from {fareDefault.origin} — the cheapest
                  tracked origin for {title}. Pick yours above.
                </p>
              )}
            </div>

            <div className="flex items-baseline justify-between gap-3 mt-4 flex-wrap">
              <h3 className="font-serif text-base font-bold text-foreground">
                {selectedFare.origin} → {destCity} ({destCode})
              </h3>
              {selectedFare.checkedLabel && (
                <span className="text-[11px] text-foreground/45">
                  {selectedFare.checkedLabel}
                </span>
              )}
            </div>

            <div>
              {selectedFare.entries.map((entry) => (
                <FareRow
                  key={`${entry.dep_date}-${entry.ret_date}`}
                  entry={entry}
                  origin={selectedFare.origin}
                  dest={destCode}
                  isCheapest={entry === selectedFare.cheapest}
                  seasons={seasons}
                />
              ))}
            </div>

            <p className="text-[12px] text-foreground/50 leading-relaxed mt-4">
              Round-trip, per person, economy, max 1 stop, 2 checked bags
              included. Fares are snapshots and change — verify before
              booking.{" "}
              <Link
                to="/travel/india#flight-deals"
                className="font-semibold text-primary hover:underline"
              >
                See all fares in the Travel Hub →
              </Link>
            </p>
          </>
        ) : (
          <>
            {/* ── Fallback view (class C/D, or A/B before data) ── */}
            <div className="mt-4">
              <OriginSelect
                id={`dest-fares-origin-${slug}`}
                origins={fbOrigins}
                value={fbOrigin}
                onChange={selectOrigin}
              />
              {fbReason === "hub" && (
                <p className="text-[11px] text-foreground/40 mt-1.5">
                  Set from your location
                </p>
              )}
              {fbReason === "stored" && (
                <p className="text-[11px] text-foreground/40 mt-1.5">
                  Your saved airport
                </p>
              )}
            </div>
            <p className="text-[13px] text-foreground/65 leading-relaxed mt-3">
              {cls === "fallback"
                ? `We don't track fares for ${title} yet — no invented numbers here. `
                : `No upcoming tracked fares for ${title} right now — fresh snapshots land on the weekly cycle. `}
              Search live prices for a typical trip in the cheapest month (
              {fmtRange(window.dep, window.ret)}):
            </p>
            <a
              href={googleFlightsUrl(fbOrigin, title, window.dep, window.ret)}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 mt-2 text-sm font-semibold text-primary hover:underline"
            >
              Search {fbOrigin} → {title} flights on Google Flights{" "}
              <ExternalLink className="h-4 w-4" />
            </a>
            <p className="text-[11px] text-foreground/40 mt-1.5">
              A search link with that window pre-filled — live prices on
              Google Flights, not a tracked fare.
            </p>
            <p className="text-[12px] text-foreground/50 leading-relaxed mt-3">
              <Link
                to="/travel/india#flight-deals"
                className="font-semibold text-primary hover:underline"
              >
                See tracked fares in the Travel Hub →
              </Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
