import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ChevronRight, Sparkles } from "lucide-react";
import { DESTINATIONS } from "@/lib/travel";
import { fmtDate, fmtRange, todayStr } from "@/lib/flightDeals";
import {
  GROUP_LABELS,
  loadTravelPlanner,
  type HolidayWindow,
  type TravelPlannerData,
} from "@/lib/travelPlanner";

const destByKey = new Map(DESTINATIONS.map((d) => [d.key, d]));

/* ================================================================== */
/* Book-by urgency strip — the Holiday Planner's survivor             */
/*                                                                    */
/* Kiran's call (2026-10-15): the full Holiday Planner section was    */
/* removed; its one load-bearing fact — the next holiday window and   */
/* its book-by deadline — survives as this one-line strip directly    */
/* under the page header, same pattern as the Hub Plan-a-Trip line.   */
/* A window whose book-by passed only shows when it's a peak window   */
/* ("fares climb from here"); a passed non-peak window defers to the  */
/* following window. No qualifying window → the strip renders         */
/* nothing rather than a stale deadline.                            */
/* ================================================================== */

function pickUrgencyWindow(
  data: TravelPlannerData,
  today: string,
): HolidayWindow | null {
  for (const w of data.holiday_windows) {
    if (w.end < today) continue;
    if (w.book_by >= today) return w;
    if (w.peak) return w;
  }
  return null;
}

export function BookByUrgencyStrip() {
  const [planner, setPlanner] = useState<TravelPlannerData | null>(null);

  useEffect(() => {
    loadTravelPlanner().then(setPlanner);
  }, []);

  const today = todayStr();
  const win = useMemo(
    () => (planner ? pickUrgencyWindow(planner, today) : null),
    [planner, today],
  );

  if (!win) return null;

  const note =
    win.book_by >= today
      ? `Book by ${fmtDate(win.book_by)} for best fares`
      : "Best-fare window passed — fares climb from here";

  return (
    <div className="mb-8 -mt-3 flex flex-wrap items-center gap-x-2 gap-y-1 rounded-xl border border-[#D4A843]/40 bg-[#D4A843]/10 px-4 py-2.5 text-[13px]">
      <span className="text-foreground/70">🗓️ Next holiday window:</span>
      <strong className="text-foreground/90">
        {win.emoji} {win.name}
      </strong>
      <span className="text-foreground/60">{fmtRange(win.start, win.end)}</span>
      <span className="text-foreground/40">·</span>
      <span className={win.book_by >= today ? "text-foreground/75" : "font-semibold text-[#A32D2F]"}>
        {note}
      </span>
      <a
        href="#flight-deals"
        className="ml-auto font-semibold text-primary hover:underline whitespace-nowrap"
      >
        See fares ↓
      </a>
    </div>
  );
}

/* ================================================================== */
/* Destinations by Month — PARKED 2026-10-15 (Kiran)                  */
/*                                                                    */
/* Not rendered anywhere: the "Best Places to Go — by Month" section  */
/* was removed from /travel entirely ("park it entirely, no          */
/* filter"). Kept intact for a possible later return — restore by    */
/* re-adding the render + import in TravelPage.tsx. The underlying   */
/* travel-by-month data still feeds trending + season tags.           */
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
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xl">🌍</span>
        <h2 className="font-serif text-xl font-bold">Best Places to Go — by Month</h2>
      </div>

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
