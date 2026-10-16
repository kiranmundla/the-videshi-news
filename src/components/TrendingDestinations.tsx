import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import {
  useTrendingDestinations,
  type TrendingDestination,
} from "@/lib/trendingDestinations";
import { useRailCounter } from "@/lib/useRailCounter";

/* ------------------------------------------------------------------ */
/* Trending Destinations rail — the first section on /travel.         */
/*                                                                    */
/* Ordering comes from src/lib/trendingDestinations (the ONE          */
/* selection implementation shared with the Your Hub strip): the      */
/* rail renders the tracker's trending_now ranking — a card's badge   */
/* is its position IN THE RANKING, read from the ranked list itself,  */
/* never from its slot in this rail — and the ranked selection's      */
/* first 5 are exactly the Hub's 5. The tracker labels its own score  */
/* reasons; those render as chips. Hero photos come from the          */
/* tracker's hero_image, falling back to the guide galleries;         */
/* destinations without a real photo get a navy monogram block —      */
/* never an invented image.                                           */
/*                                                                    */
/* INDIA CARD (Kiran, 2026-10-15): India belongs in this scroll, but  */
/* it has no trending rank. The builder emits it separately           */
/* (data.india_card — derived best months, a real fare line, the      */
/* same season-chip math). Placement is editorial: the card was       */
/* appended after the ranked cards at first; Kiran then directed      */
/* (2026-10-15 20:38: "Let's make India first in scroll") that it     */
/* renders FIRST in this rail. First slot is NOT a rank claim — the   */
/* card carries NO "#N Trending" badge (badges render only for slugs  */
/* in the ranked list, numbered by ranking position), so no rank is  */
/* implied and none shifts. It links to India's own destination       */
/* page, /travel/india, exactly like every other card links to its    */
/* page (Kiran, 2026-10-15 20:21: "India should get its own page" —    */
/* the card first linked to the on-page India Destinations section;   */
/* the page superseded that). The Hub strip does not render it — its  */
/* cards stay a strict prefix of the ranking, as before.              */
/*                                                                    */
/* Card geometry deliberately matches the Hub strip (Kiran,           */
/* 2026-10-15: the Hub's compact cards are the preferred size for     */
/* scroll rails): 200px wide, 96px image, same padding/typography.    */
/*                                                                    */
/* Scroll signal: the counter pill (n / total) + the peek of the next */
/* card. There is intentionally NO edge-fade overlay — the previous   */
/* full-height white gradients washed over card images and text and   */
/* read as "cloudiness" (Kiran, 2026-10-15); the Hub renders the      */
/* same data cleanly without them.                                    */
/*                                                                    */
/* Scroll mechanics match the Hub strip exactly — a plain overflow    */
/* scroll with NO scroll-snap, and the counter runs through           */
/* useRailCounter (rAF-coalesced, step measured once, state only on   */
/* index change). The previous mandatory-snap + per-scroll-event      */
/* setState/offsetWidth pattern felt grabby next to the Hub strip     */
/* (Kiran, 2026-10-15) — see src/lib/useRailCounter.ts.               */
/* ------------------------------------------------------------------ */

const MAX_CARDS = 8;

/* Short chip labels for the tracker's positive signals only. The full
   reason sentence rides along as the chip's title so nothing is hidden:
   fare_drop earns a chip only when its points are actually positive —
   a tracked route with no drop (0) or no route at all (null) gets none.
   Thresholds are RATIOS of each component's max, not raw points: the
   2026-10-15 real-signal flip reweighted the components (season 50→40,
   value 20→10, fare 30→20, plus search_interest 30), and the India
   card still emits the legacy weights — ratios keep both correct. */
function reasonChips(d: TrendingDestination): { label: string; title: string }[] {
  const chips: { label: string; title: string }[] = [];
  for (const c of d.trending.components) {
    if (c.points == null) continue;
    const ratio = c.max > 0 ? c.points / c.max : 0;
    if (c.id === "season_fit" && ratio >= 0.8) {
      chips.push({ label: "In season now", title: c.reason });
    } else if (c.id === "season_fit" && ratio >= 0.5) {
      chips.push({ label: "Shoulder season", title: c.reason });
    } else if (c.id === "search_interest" && ratio >= 2 / 3) {
      chips.push({ label: "Traveler interest", title: c.reason });
    } else if (c.id === "offpeak_value" && ratio >= 0.75) {
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

  /* India card FIRST (editorial placement, Kiran 2026-10-15 20:38),
     then the ranked cards in ranking order (see header note).
     railCards is what the rail renders, counts and scroll-clamps.
     rankBySlug numbers the ranked cards by their position in the
     ranked list itself, so India's first slot can never shift a
     badge: Australia keeps "#1 Trending" from the second slot. */
  const indiaCard = data?.india_card ?? null;
  const railCards = indiaCard ? [indiaCard, ...cards] : cards;
  const rankBySlug = new Map(cards.map((c, idx) => [c.slug, idx + 1]));

  const { scrollRef, currentIndex } = useRailCounter(railCards.length);

  if (!data || cards.length === 0) return null;

  const monthLabel = `${MONTH_LONG[(data.current_month ?? 1) - 1] ?? ""} ${data.current_year}`;

  return (
    <section className="mb-12" id="trending-destinations">
      {/* Section header — redesign header system (Kiran approved
          mockup, 2026-10-15): gold kicker, serif navy title, hairline
          with a gold tick; the counter pill keeps its place at the
          title's right. Same treatment on every /travel section. */}
      <div className="relative border-b border-rule pb-3 mb-3">
        <div className="flex items-end justify-between gap-2">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[2px] text-[#7a5c14] dark:text-[#D4A843] mb-1">
              Where to go
            </p>
            <h2 className="font-serif text-xl font-bold leading-none" style={{ color: "#0B1D3A" }}>
              Top Destinations to Visit
            </h2>
          </div>
          {railCards.length > 1 && (
            <span
              aria-hidden
              className="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-foreground/5 text-foreground/50"
              style={{ fontVariantNumeric: "tabular-nums" }}
            >
              {currentIndex + 1} / {railCards.length}
            </span>
          )}
        </div>
        <span className="absolute left-0 -bottom-px h-[2px] w-10 bg-[#D4A843]" />
      </div>
      <p className="text-sm text-foreground/55 mb-5 max-w-2xl leading-relaxed">
        Trending now — {monthLabel}. Ranked by season fit, rising traveler
        interest and off-peak value — updated weekly.
      </p>

      <div
        ref={scrollRef}
        className="trending-rail flex gap-3 overflow-x-auto pb-2"
        style={{
          WebkitOverflowScrolling: "touch",
          scrollbarWidth: "none",
          msOverflowStyle: "none",
        } as React.CSSProperties}
      >
        <style>{`.trending-rail::-webkit-scrollbar { display: none; }`}</style>
        {railCards.map((dest) => {
          const galleryPhoto = galleries?.[dest.slug]?.photos?.[0];
          const image = dest.hero_image || galleryPhoto?.src || null;
          /* Every card — India included — is a plain Link to its
             destination page (dest.guide_url); the India card's is
             /travel/india, emitted by the builder. */
          /* ONE reason chip per card (audit item 13): when every card
             carries the same two chips they differentiate nothing.
             reasonChips builds in priority order (season, traveler
             interest, fare drop, off-peak), so the first is the
             strongest signal. */
          const chips = reasonChips(dest).slice(0, 1);
          const best = fmtBestMonths(dest.best_months);
          return (
            <Link
              key={dest.slug}
              to={dest.guide_url}
              className="block group flex-shrink-0 w-[200px]"
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
                  {/* Rank badge ONLY for ranked cards, numbered by
                      position in the ranked list (rankBySlug) — NOT by
                      rail slot, so the India card's first slot leaves
                      every badge untouched. India is not in the ranked
                      list and gets none — no implied rank. */}
                  {rankBySlug.has(dest.slug) && (
                    <span className="absolute top-1.5 left-1.5 text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-black/55 text-white backdrop-blur-sm">
                      #{rankBySlug.get(dest.slug)} Trending
                    </span>
                  )}
                </div>

                <div className="p-3 flex flex-col gap-1.5 flex-1">
                  <div className="flex items-start justify-between gap-1.5">
                    <div className="min-w-0">
                      <h3 className="font-serif font-bold text-[15px] leading-tight group-hover:text-primary transition-colors">
                        {dest.name}
                      </h3>
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
                      ✈️ {dest.fare_from.route.replace("-", " → ")} from ${dest.fare_from.price_min.toLocaleString()}
                      <span className="block text-[10px] font-normal text-foreground/40">
                        {dest.fare_from.date_range} ·{" "}
                        {dest.fare_from.cadence === "weekly"
                          ? `Checked weekly · ${fmtAsOf(dest.fare_from.as_of)}`
                          : `Checked ${fmtAsOf(dest.fare_from.as_of)}`}
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
