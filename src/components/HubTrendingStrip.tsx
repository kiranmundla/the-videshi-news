import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import {
  useTrendingDestinations,
  type TrendingDestination,
} from "@/lib/trendingDestinations";

/* ------------------------------------------------------------------ */
/* Hub Trending Destinations strip — the daily-glance teaser of the   */
/* /travel TrendingDestinations rail. Ordering and eligibility come   */
/* from src/lib/trendingDestinations — the ONE selection              */
/* implementation both surfaces share — so this strip's 5 cards are   */
/* always the strict prefix of the /travel rail's 8, and a card's      */
/* badge is its rank in that single list on both surfaces.            */
/*                                                                    */
/* Floor requirement (Kiran, 2026-10-14): the Hub → /travel link must */
/* not depend on data. The section shell and the labeled summary row  */
/* ("Travel — deals, destinations & guides →") render unconditionally */
/* — loading, loaded, or fetch-failed alike. Only the cards wait for  */
/* the tracker data.                                                  */
/* ------------------------------------------------------------------ */

const MAX_CARDS = 5;

/* The single why-trending chip: the record's top labeled reason. A fare
   drop is the most actionable signal and earns the chip whenever its
   points are genuinely positive (a tracked route with no drop scores 0,
   an untracked one null — neither gets the chip). Otherwise the
   strongest season signal wins. The full reason sentence is the title. */
function topReason(d: TrendingDestination): { label: string; title: string } | null {
  const byId = new Map(d.trending.components.map((c) => [c.id, c]));
  const fare = byId.get("fare_drop");
  if (fare && fare.points != null && fare.points > 0) {
    return { label: "Fare dropped", title: fare.reason };
  }
  const season = byId.get("season_fit");
  if (season && season.points != null && season.points >= 40) {
    return { label: "In season now", title: season.reason };
  }
  if (season && season.points != null && season.points >= 25) {
    return { label: "Shoulder season", title: season.reason };
  }
  const offpeak = byId.get("offpeak_value");
  if (offpeak && offpeak.points != null && offpeak.points >= 15) {
    return { label: "Off-peak value", title: offpeak.reason };
  }
  return null;
}

const MONTH_LONG = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

export default function HubTrendingStrip() {
  const { data, galleries, cards } = useTrendingDestinations(MAX_CARDS);

  const sub = data
    ? `trending in ${MONTH_LONG[(data.current_month ?? 1) - 1] ?? ""} ${data.current_year}`
    : "top places to visit now";

  return (
    <section className="mb-10">
      {/* Header replicates YourHubPage's SectionHead (page-local there) */}
      <div
        className="flex items-center justify-between mb-4 pb-2.5"
        style={{ borderBottom: "3px solid #D4A843" }}
      >
        <h2
          className="text-[13px] font-bold tracking-[2px] uppercase"
          style={{ color: "#0B1D3A" }}
        >
          Trending Destinations
        </h2>
        <span className="text-[11px] text-muted-foreground">{sub}</span>
      </div>

      {cards.length > 0 && (
        <div
          className="flex gap-3 overflow-x-auto pb-2 -mx-4 px-4 md:mx-0 md:px-0"
          style={{ scrollbarWidth: "none", WebkitOverflowScrolling: "touch" }}
        >
          {cards.map((dest, i) => {
            const galleryPhoto = galleries?.[dest.slug]?.photos?.[0];
            const image = dest.hero_image || galleryPhoto?.src || null;
            const chip = topReason(dest);
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
                    <span className="absolute top-1.5 left-1.5 text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-black/55 text-white backdrop-blur-sm">
                      #{i + 1}
                    </span>
                  </div>
                  <div className="p-3 flex flex-col gap-1.5 flex-1">
                    <div className="flex items-start justify-between gap-1.5">
                      <div className="min-w-0">
                        <h3 className="font-serif font-bold text-[15px] leading-tight group-hover:text-primary transition-colors">
                          {dest.name}
                        </h3>
                        <p className="text-[11px] text-muted-foreground leading-tight mt-0.5">
                          {dest.region}
                        </p>
                      </div>
                      <ChevronRight className="h-4 w-4 text-foreground/20 group-hover:text-primary transition-colors flex-shrink-0 mt-0.5" />
                    </div>
                    {chip && (
                      <span
                        title={chip.title}
                        className="self-start text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#D4A843]/20 text-[#7a5c14] dark:text-[#D4A843]"
                      >
                        {chip.label}
                      </span>
                    )}
                  </div>
                </article>
              </Link>
            );
          })}
        </div>
      )}

      {/* Floor link — ALWAYS rendered, data or no data. This is the
          unmissable Hub → /travel path: a full-width labeled summary
          row, not a card tap and not a small text link. */}
      <Link
        to="/travel"
        className="mt-1 flex items-center justify-between gap-3 bg-card border border-border rounded-lg px-4 py-3 hover:border-primary/40 transition-colors group"
      >
        <span className="text-[13px] text-muted-foreground">
          <span className="font-bold text-[14px]" style={{ color: "#0B1D3A" }}>
            ✈️ Travel
          </span>{" "}
          — deals, destinations &amp; guides
        </span>
        <span
          className="text-[15px] font-bold flex-shrink-0 group-hover:translate-x-0.5 transition-transform"
          style={{ color: "#A32D2F" }}
          aria-hidden
        >
          →
        </span>
      </Link>
    </section>
  );
}
