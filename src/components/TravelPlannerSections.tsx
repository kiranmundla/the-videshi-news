import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { CalendarDays, ChevronRight, Plane, Sparkles } from "lucide-react";
import { DESTINATIONS } from "@/lib/travel";
import {
  detectHubRoute,
  fareForWindow,
  fmtDateLong,
  fmtRange,
  loadFlightDeals,
  todayStr,
  type FlightDealsData,
} from "@/lib/flightDeals";
import {
  GROUP_LABELS,
  loadTravelPlanner,
  type TravelPlannerData,
} from "@/lib/travelPlanner";

const destByKey = new Map(DESTINATIONS.map((d) => [d.key, d]));

/* ================================================================== */
/* Holiday Planner — the lead section                                 */
/* ================================================================== */

export function HolidayPlanner() {
  const [planner, setPlanner] = useState<TravelPlannerData | null>(null);
  const [deals, setDeals] = useState<FlightDealsData | null>(null);
  const [routeKey, setRouteKey] = useState<string | null>(null);

  useEffect(() => {
    loadTravelPlanner().then(setPlanner);
    loadFlightDeals().then((d) => {
      setDeals(d);
      if (d) setRouteKey(detectHubRoute(Object.keys(d.routes)));
    });
  }, []);

  const today = todayStr();
  const windows = useMemo(
    () => (planner ? planner.holiday_windows.filter((w) => w.end >= today) : []),
    [planner, today],
  );
  const route = routeKey && deals ? deals.routes[routeKey] : null;

  if (!planner || windows.length === 0) return null;

  return (
    <section className="mb-12" id="holiday-planner">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">🗓️</span>
        <h2 className="font-serif text-xl font-bold">Holiday Planner</h2>
      </div>
      <p className="text-sm text-foreground/55 mb-5 max-w-2xl leading-relaxed">
        The windows everyone travels in — best dates and the book-by deadline
        for each{route ? `, with live snapshot fares from ${route.origin}` : ""}.
        Fares punish waiting on peak windows; the deadline is the point.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {windows.map((w) => {
          const fare = route ? fareForWindow(route, w.start, w.end) : null;
          const bookByFuture = w.book_by >= today;
          return (
            <div
              key={w.id}
              className="bg-card border border-border rounded-2xl p-5 flex flex-col hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5"
            >
              <div className="flex items-center justify-between gap-2 mb-2">
                <h3 className="font-serif font-bold text-base flex items-center gap-2">
                  <span className="text-xl">{w.emoji}</span> {w.name}
                </h3>
                {w.peak && (
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-400">
                    Peak fares
                  </span>
                )}
              </div>
              <div className="flex items-center gap-1.5 text-sm font-semibold text-foreground/85">
                <CalendarDays className="h-4 w-4 text-foreground/40" />
                {fmtRange(w.start, w.end)}
              </div>
              <p className="text-[13px] text-foreground/55 leading-relaxed mt-2 flex-1">
                {w.note}
              </p>

              {fare && route && deals && (
                <div className="mt-3 bg-emerald-500/10 border border-emerald-500/25 rounded-xl px-3 py-2">
                  <div className="flex items-center gap-1.5 text-[13px] font-bold text-emerald-700 dark:text-emerald-400">
                    <Plane className="h-3.5 w-3.5" />
                    {route.origin} → {route.destination}: ${fare.price_min.toLocaleString()}–${fare.price_max.toLocaleString()}
                  </div>
                  <div className="text-[11px] text-foreground/50 mt-0.5">
                    {fare.weeks}-week trip {fmtRange(fare.dep_date, fare.ret_date)} · per person · fares checked {deals.as_of}
                  </div>
                </div>
              )}

              <div className="mt-3">
                {bookByFuture ? (
                  <span className="inline-block text-[11px] font-bold px-2.5 py-1 rounded-full bg-[#D4A843]/20 text-[#7a5c14] dark:text-[#D4A843]">
                    Book by {fmtDateLong(w.book_by)} for best fares
                  </span>
                ) : w.peak ? (
                  <span className="inline-block text-[11px] font-bold px-2.5 py-1 rounded-full bg-[#A32D2F]/10 text-[#A32D2F]">
                    Best-fare window passed — book now, fares climb from here
                  </span>
                ) : (
                  <span className="inline-block text-[11px] font-bold px-2.5 py-1 rounded-full bg-foreground/8 text-foreground/60">
                    Moderate season — book ~2 months out
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <a href="#flight-deals" className="inline-flex items-center gap-1 mt-4 text-[13px] font-semibold text-primary hover:underline">
        See month-by-month fares to India <ChevronRight className="h-3.5 w-3.5" />
      </a>
    </section>
  );
}

/* ================================================================== */
/* Destinations by Month                                              */
/* ================================================================== */

export function DestinationsByMonth() {
  const [planner, setPlanner] = useState<TravelPlannerData | null>(null);
  const [activeMonth, setActiveMonth] = useState<string>("");

  useEffect(() => {
    loadTravelPlanner().then((d) => {
      setPlanner(d);
      if (d) {
        const now = todayStr().slice(0, 7);
        const first = d.months.find((m) => m.month >= now) ?? d.months[0];
        setActiveMonth(first?.month ?? "");
      }
    });
  }, []);

  const active = planner?.months.find((m) => m.month === activeMonth);

  if (!planner || !active) return null;

  return (
    <section className="mb-12" id="by-month">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">🌍</span>
        <h2 className="font-serif text-xl font-bold">Best Places to Go — by Month</h2>
      </div>
      <p className="text-sm text-foreground/55 mb-5 max-w-2xl leading-relaxed">
        Flexible dates? This is your section. Where each place is at its best —
        and when it's cheapest — month by month, across the US, the world, and
        India itself.
      </p>

      <style>{`.month-pills::-webkit-scrollbar { display: none; }`}</style>
      <div
        className="month-pills flex gap-2 overflow-x-auto pb-4 -mx-1 px-1"
        style={{ scrollbarWidth: "none", msOverflowStyle: "none", WebkitOverflowScrolling: "touch" } as React.CSSProperties}
      >
        {planner.months.map((m) => (
          <button
            key={m.month}
            onClick={() => setActiveMonth(m.month)}
            className={`shrink-0 px-4 py-2 rounded-full text-sm font-semibold border transition-colors ${
              activeMonth === m.month
                ? "bg-primary text-primary-foreground border-primary"
                : "border-rule text-foreground/80 hover:text-primary hover:border-primary"
            }`}
          >
            {m.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {active.picks.map((pick) => {
          const dest = destByKey.get(pick.key);
          const fact = planner.destination_facts[pick.key];
          if (!dest) return null;
          return (
            <Link
              key={pick.key}
              to={`/travel/${pick.key}`}
              className="block group bg-card border border-border rounded-2xl p-5 hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5"
            >
              <div className="flex items-start justify-between gap-2">
                <h3 className="font-serif font-bold text-base group-hover:text-primary transition-colors">
                  {dest.label}
                </h3>
                <span
                  className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full whitespace-nowrap ${
                    pick.group === "india"
                      ? "bg-[#D4A843]/20 text-[#7a5c14] dark:text-[#D4A843]"
                      : pick.group === "usa"
                        ? "bg-sky-500/15 text-sky-700 dark:text-sky-400"
                        : "bg-emerald-500/12 text-emerald-700 dark:text-emerald-400"
                  }`}
                >
                  {GROUP_LABELS[pick.group]}
                </span>
              </div>
              <p className="text-[13px] text-foreground/60 leading-relaxed mt-1.5">
                {pick.why}
              </p>
              {fact && (
                <div className="flex flex-col gap-1 mt-3 text-[11px]">
                  <span className="text-foreground/55">
                    🗓️ <strong className="text-foreground/75">Best:</strong> {fact.best_season}
                  </span>
                  <span className="text-foreground/55">
                    💰 <strong className="text-foreground/75">Cheapest:</strong> {fact.cheapest_month}
                  </span>
                </div>
              )}
              <div className="mt-3 text-[12px] font-semibold text-primary/70 group-hover:text-primary flex items-center gap-1">
                <Sparkles className="h-3.5 w-3.5" /> Read the guide
                <ChevronRight className="h-3.5 w-3.5" />
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}

/* ================================================================== */
/* While You're in India                                              */
/* ================================================================== */

export function InIndiaStrip() {
  const [planner, setPlanner] = useState<TravelPlannerData | null>(null);

  useEffect(() => {
    loadTravelPlanner().then(setPlanner);
  }, []);

  if (!planner) return null;

  return (
    <section className="mb-12" id="in-india">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">🇮🇳</span>
        <h2 className="font-serif text-xl font-bold">While You're in India</h2>
      </div>
      <p className="text-sm text-foreground/55 mb-5 max-w-2xl leading-relaxed">
        Already flying home for family? Add three or four days — India's best
        side trips, each with a full diaspora guide behind it.
      </p>

      <style>{`.india-strip::-webkit-scrollbar { display: none; }`}</style>
      <div
        className="india-strip flex gap-3 overflow-x-auto pb-2 -mx-4 px-4 md:mx-0 md:px-0"
        style={{ scrollbarWidth: "none", msOverflowStyle: "none", WebkitOverflowScrolling: "touch" } as React.CSSProperties}
      >
        {planner.in_india.map((pick) => {
          const dest = destByKey.get(pick.key);
          const fact = planner.destination_facts[pick.key];
          if (!dest) return null;
          return (
            <Link
              key={pick.key}
              to={`/travel/${pick.key}`}
              className="block group flex-shrink-0 w-[260px] bg-card border border-border rounded-2xl p-4 hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5"
            >
              <h3 className="font-serif font-bold text-[15px] group-hover:text-primary transition-colors">
                {dest.label}
              </h3>
              <p className="text-[12px] text-foreground/55 leading-relaxed mt-1">
                {pick.blurb}
              </p>
              {fact && (
                <div className="mt-2.5 text-[11px] font-semibold text-[#7a5c14] dark:text-[#D4A843]">
                  🗓️ Best: {fact.best_season}
                </div>
              )}
              <div className="mt-2 text-[11px] text-foreground/40">💰 {dest.budget}</div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
