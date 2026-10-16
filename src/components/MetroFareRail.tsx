import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  fmtRange,
  tripLengthLabel,
  type MetroFare,
} from "@/lib/flightDeals";

/* ------------------------------------------------------------------ */
/* India Metros rail — the "India Metros Scroll" (Kiran, 2026-10-15). */
/* One card per Indian metro with a real fare from the reader's       */
/* origin: daily-core routes show their daily check date, weekly-grid */
/* routes are stamped "Checked weekly · <date>" — each card carries   */
/* its OWN fare's freshness, never a neighbour's. Metros without a    */
/* fare from this origin are simply absent (no placeholders). The     */
/* old "Weekly grid" pill is gone (audit item 9): the stamp already   */
/* says "Checked weekly".                                             */
/*                                                                    */
/* Scroll signal = the counter pill + the next-card peek, the same    */
/* pattern as the trending rails — NO edge-fade overlays (Kiran       */
/* called the white fade "cloudiness" and had it removed, 2026-10-15).*/
/*                                                                    */
/* Variants: "hub" — compact cards inside the Your Hub Plan a Trip     */
/* block, each linking to /travel; "travel" — selectable cards in the */
/* Cheapest Fares hub that switch the calendar below to that route.   */
/* ------------------------------------------------------------------ */

const GAP = 12;

function MetroCardBody({ fare }: { fare: MetroFare }) {
  return (
    <>
      <div className="flex items-baseline justify-between gap-2">
        <span className="font-serif font-bold text-[16px] leading-tight text-foreground">
          {fare.metroName}
        </span>
        <span className="text-[10px] font-bold tracking-widest text-foreground/40">
          {fare.metro}
        </span>
      </div>
      <div
        className="text-[1.55rem] font-black leading-none mt-1.5"
        style={{ color: "#0B1D3A" }}
      >
        <span className="text-[11px] font-semibold text-foreground/45 mr-0.5">
          from
        </span>
        ${fare.entry.price_min.toLocaleString()}
      </div>
      <div className="text-[11px] text-muted-foreground mt-1.5 leading-snug">
        {fmtRange(fare.entry.dep_date, fare.entry.ret_date)} ·{" "}
        {tripLengthLabel(fare.entry)}
        <br />
        {fare.entry.cheapest_airline}
      </div>
      <div className="text-[10px] text-foreground/45 mt-1.5">
        {fare.checkedLabel}
      </div>
    </>
  );
}

export default function MetroFareRail({
  fares,
  variant,
  onSelect,
  selectedRouteKey,
}: {
  fares: MetroFare[];
  variant: "hub" | "travel";
  onSelect?: (routeKey: string) => void;
  selectedRouteKey?: string;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  const updateScrollState = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    const first = el.children[0] as HTMLElement | undefined;
    const step = first ? first.offsetWidth + GAP : el.clientWidth * 0.75;
    if (step > 0) {
      setCurrentIndex(
        Math.min(
          fares.length - 1,
          Math.max(0, Math.round(el.scrollLeft / step)),
        ),
      );
    }
  }, [fares.length]);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    updateScrollState();
    el.addEventListener("scroll", updateScrollState, { passive: true });
    window.addEventListener("resize", updateScrollState);
    return () => {
      el.removeEventListener("scroll", updateScrollState);
      window.removeEventListener("resize", updateScrollState);
    };
  }, [fares.length, updateScrollState]);

  if (!fares.length) return null;

  const cardCls =
    variant === "hub"
      ? "w-[168px] p-3"
      : "w-[190px] p-3.5 text-left";

  return (
    <div>
      {fares.length > 1 && (
        <div className="flex justify-end mb-1.5">
          <span
            aria-hidden
            className="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-foreground/5 text-foreground/50"
            style={{ fontVariantNumeric: "tabular-nums" }}
          >
            {currentIndex + 1} / {fares.length}
          </span>
        </div>
      )}
      <div
        ref={scrollRef}
        className="metros-rail flex gap-3 overflow-x-auto pb-1"
        style={
          {
            scrollSnapType: "x mandatory",
            WebkitOverflowScrolling: "touch",
            scrollbarWidth: "none",
            msOverflowStyle: "none",
          } as React.CSSProperties
        }
      >
        <style>{`.metros-rail::-webkit-scrollbar { display: none; }`}</style>
        {fares.map((fare) =>
          variant === "hub" ? (
            <Link
              key={fare.routeKey}
              to="/travel/india#flight-deals"
              className={`block flex-shrink-0 bg-card border border-border rounded-lg hover:border-primary/40 transition-colors ${cardCls}`}
              style={{ scrollSnapAlign: "start" }}
            >
              <MetroCardBody fare={fare} />
            </Link>
          ) : (
            <button
              key={fare.routeKey}
              type="button"
              onClick={() => onSelect?.(fare.routeKey)}
              aria-pressed={selectedRouteKey === fare.routeKey}
              className={`block flex-shrink-0 bg-card border rounded-lg transition-colors ${cardCls} ${
                selectedRouteKey === fare.routeKey
                  ? "border-primary ring-1 ring-primary/50"
                  : "border-border hover:border-primary/40"
              }`}
              style={{ scrollSnapAlign: "start" }}
            >
              <MetroCardBody fare={fare} />
            </button>
          ),
        )}
      </div>
    </div>
  );
}
