import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import {
  useTrendingDestinations,
  type TrendingDestination,
} from "@/lib/trendingDestinations";

/* ------------------------------------------------------------------ */
/* Trending Destinations rail — the first section on /travel.         */
/*                                                                    */
/* Ordering comes from src/lib/trendingDestinations (the ONE          */
/* selection implementation shared with the Your Hub strip): the      */
/* rail renders the tracker's trending_now ranking, badge = position, */
/* and its first 5 cards are exactly the Hub's 5. The tracker labels  */
/* its own score reasons; those render as chips. Hero photos come     */
/* from the tracker's hero_image, falling back to the guide           */
/* galleries; destinations without a real photo get a navy monogram   */
/* block — never an invented image.                                   */
/*                                                                    */
/* Card geometry deliberately matches the Hub strip (Kiran,           */
/* 2026-10-15: the Hub's compact cards are the preferred size for     */
/* scroll rails): 200px wide, 96px image, same padding/typography.    */
/*                                                                    */
/* Scroll signal: the counter pill (n / 8) + the peek of the next     */
/* card. There is intentionally NO edge-fade overlay — the previous   */
/* full-height white gradients washed over card images and text and   */
/* read as "cloudiness" (Kiran, 2026-10-15); the Hub renders the      */
/* same data cleanly without them.                                    */
/* ------------------------------------------------------------------ */

const MAX_CARDS = 8;
const GAP = 12;

/* Short chip labels for the tracker's positive signals only. The full
   reason sentence rides along as the chip's title so nothing is hidden:
   fare_drop earns a chip only when its points are actually positive —
   a tracked route with no drop (0) or no route at all (null) gets none. */
function reasonChips(d: TrendingDestination): { label: string; title: string }[] {
  const chips: { label: string; title: string }[] = [];
  for (const c of d.trending.components) {
    if (c.points == null) continue;
    if (c.id === "season_fit" && c.points >= 40) {
      chips.push({ label: "In season now", title: c.reason });
    } else if (c.id === "season_fit" && c.points >= 25) {
      chips.push({ label: "Shoulder season", title: c.reason });
    } else if (c.id === "offpeak_value" && c.points >= 15) {
      chips.push({ label: "Off-peak value", title: c.reason });
    } else if (c.id === "fare_drop" && c.points > 0) {
      chips.push({ label: "Fare dropped", title: c.reason });
    }
  }
  return chips;
}

const MONTH_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MONTH_LONG = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

/** [4,5,6,9,10,11,12] → "Apr–Jun · Sep–Dec" */
function fmtBestMonths(months: number[]): string {
  if (!months.length) return "";
  const sorted = [...months].sort((a, b) => a - b);
  const ranges: [number, number][] = [];
  let start = sorted[0];
  let prev = sorted[0];
  for (const m of sorted.slice(1)) {
    if (m === prev + 1) {
      prev = m;
    } else {
      ranges.push([start, prev]);
      start = m;
      prev = m;
    }
  }
  ranges.push([start, prev]);
  return ranges
    .map(([a, b]) => (a === b ? MONTH_SHORT[a - 1] : `${MONTH_SHORT[a - 1]}–${MONTH_SHORT[b - 1]}`))
    .join(" · ");
}

function fmtAsOf(iso: string): string {
  const d = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export default function TrendingDestinations() {
  const { data, galleries, cards } = useTrendingDestinations(MAX_CARDS);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  const updateScrollState = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    const first = el.children[0] as HTMLElement | undefined;
    const step = first ? first.offsetWidth + GAP : el.clientWidth * 0.75;
    if (step > 0) {
      setCurrentIndex(Math.min(cards.length - 1, Math.max(0, Math.round(el.scrollLeft / step))));
    }
  }, [cards.length]);

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
  }, [cards.length, updateScrollState]);

  if (!data || cards.length === 0) return null;

  const monthLabel = `${MONTH_LONG[(data.current_month ?? 1) - 1] ?? ""} ${data.current_year}`;

  return (
    <section className="mb-12" id="trending-destinations">
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">🔥</span>
          <h2 className="font-serif text-xl font-bold">Top Destinations to Visit</h2>
        </div>
        {cards.length > 1 && (
          <span
            aria-hidden
            className="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-foreground/5 text-foreground/50"
            style={{ fontVariantNumeric: "tabular-nums" }}
          >
            {currentIndex + 1} / {cards.length}
          </span>
        )}
      </div>
      <p className="text-sm text-foreground/55 mb-5 max-w-2xl leading-relaxed">
        Trending now — {monthLabel}. Ranked by our destination tracker on
        season fit, value and fare movement; every card shows why it made the
        list.
      </p>

      <div
        ref={scrollRef}
        className="trending-rail flex gap-3 overflow-x-auto pb-2"
        style={{
          scrollSnapType: "x mandatory",
          WebkitOverflowScrolling: "touch",
          scrollbarWidth: "none",
          msOverflowStyle: "none",
        } as React.CSSProperties}
      >
        <style>{`.trending-rail::-webkit-scrollbar { display: none; }`}</style>
        {cards.map((dest, i) => {
          const galleryPhoto = galleries?.[dest.slug]?.photos?.[0];
          const image = dest.hero_image || galleryPhoto?.src || null;
          const chips = reasonChips(dest);
          const best = fmtBestMonths(dest.best_months);
          return (
            <Link
              key={dest.slug}
              to={dest.guide_url}
              className="block group flex-shrink-0 w-[200px]"
              style={{ scrollSnapAlign: "start" }}
            >
              <article className="bg-card border border-border rounded-lg overflow-hidden hover:border-primary/40 transition-all duration-200 hover:shadow-md h-full flex flex-col">
                <div className="relative h-24 overflow-hidden flex-shrink-0">
                  {image ? (
                    <img
                      src={image}
                      alt={galleryPhoto?.caption || dest.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      loading="lazy"
                    />
                  ) : (
                    <div className="w-full h-full bg-[#0B1D3A] flex flex-col items-center justify-center gap-0.5">
                      <span className="font-serif text-3xl font-bold text-[#D4A843]">
                        {dest.name.charAt(0)}
                      </span>
                      <span className="text-[9px] font-semibold uppercase tracking-widest text-white/50 px-2 text-center">
                        {dest.region}
                      </span>
                    </div>
                  )}
                  <span className="absolute top-1.5 left-1.5 text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-black/55 text-white backdrop-blur-sm">
                    #{i + 1} Trending
                  </span>
                </div>

                <div className="p-3 flex flex-col gap-1.5 flex-1">
                  <div className="flex items-start justify-between gap-1.5">
                    <div className="min-w-0">
                      <h3 className="font-serif font-bold text-[15px] leading-tight group-hover:text-primary transition-colors">
                        {dest.name}
                      </h3>
                      <p className="text-[11px] text-foreground/50 leading-tight mt-0.5">{dest.region}</p>
                    </div>
                    <ChevronRight className="h-4 w-4 text-foreground/20 group-hover:text-primary transition-colors flex-shrink-0 mt-0.5" />
                  </div>

                  {chips.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {chips.map((chip) => (
                        <span
                          key={chip.label}
                          title={chip.title}
                          className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#D4A843]/20 text-[#7a5c14] dark:text-[#D4A843]"
                        >
                          {chip.label}
                        </span>
                      ))}
                    </div>
                  )}

                  {best && (
                    <p className="text-[11px] text-foreground/55">
                      📅 Best: <span className="font-semibold text-foreground/75">{best}</span>
                    </p>
                  )}

                  {dest.highlights[0] && (
                    <p className="text-xs text-foreground/50 leading-snug line-clamp-2">
                      {dest.highlights[0].title}
                    </p>
                  )}

                  {dest.fare_from && (
                    <p className="mt-auto pt-1 text-[11px] font-semibold text-[#7a5c14] dark:text-[#D4A843]">
                      ✈️ {dest.fare_from.route} from ${dest.fare_from.price_min.toLocaleString()}
                      <span className="block text-[10px] font-normal text-foreground/40">
                        {dest.fare_from.date_range} ·{" "}
                        {dest.fare_from.cadence === "weekly"
                          ? `indicative · checked weekly · ${fmtAsOf(dest.fare_from.as_of)}`
                          : `fares checked ${fmtAsOf(dest.fare_from.as_of)}`}
                      </span>
                    </p>
                  )}
                </div>
              </article>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
