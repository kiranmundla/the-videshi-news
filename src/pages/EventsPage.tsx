import { useEffect, useState, useCallback, useRef, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { supabase as supabaseTyped } from "@/integrations/supabase/client";
import {
  EventItem,
  EventWithDistance,
  formatEventDate,
  generateSlug,
  sortEventsByDistance,
  getAllUpcomingEvents,
  getFeaturedEvents,
  CITY_GROUPS,
} from "@/lib/events";
import {
  parseSearchQuery,
  matchesKeywords,
  matchesFreeFilter,
  getDateFilterRange,
  getSmartChips,
  type DateFilterKey,
  type ParsedSearch,
} from "@/lib/smartSearch";
import { formatDistance } from "@/lib/geo";
import { useUserLocation } from "@/hooks/useUserLocation";
import ZipCodeSearch, { type LocationResult } from "@/components/ZipCodeSearch";

const supabaseRaw = supabaseTyped as unknown as { from: (table: string) => any };

const DEFAULT_CITY = "Bay Area";

/* ------------------------------------------------------------------ */
/* Per-category emoji + color maps + fallback images                   */
/* ------------------------------------------------------------------ */
const CAT_EMOJI: Record<string, string> = {
  Cultural: "🎭",
  Music: "🎵",
  Food: "🍛",
  Sports: "🏅",
  Community: "🤝",
  Festival: "🪔",
  Comedy: "😂",
  Dance: "💃",
  Religious: "🙏",
  Education: "🎓",
  Competition: "🏆",
  Entertainment: "🎶",
  Technology: "🚀",
  Other: "📌",
};

const CAT_FALLBACK_IMG: Record<string, string> = {
  Cultural: "/images/events/cultural.jpg",
  Music: "/images/events/music.jpg",
  Food: "/images/events/food.jpg",
  Sports: "/images/events/sports.jpg",
  Community: "/images/events/community.jpg",
  Festival: "/images/events/festival.jpg",
  Comedy: "/images/events/comedy.jpg",
  Dance: "/images/events/dance.jpg",
  Religious: "/images/events/religious.jpg",
  Education: "/images/events/education.jpg",
  Competition: "/images/events/competition.jpg",
  Entertainment: "/images/events/entertainment.jpg",
  Technology: "/images/events/technology.jpg",
  Other: "/images/events/other.jpg",
};

function categoryFallbackImg(category?: string | null): string {
  return CAT_FALLBACK_IMG[category || "Other"] || CAT_FALLBACK_IMG["Other"];
}

const CAT_BADGE_COLORS: Record<string, string> = {
  Cultural: "bg-purple-100 text-purple-700",
  Music: "bg-pink-100 text-pink-700",
  Food: "bg-amber-100 text-amber-700",
  Sports: "bg-green-100 text-green-700",
  Community: "bg-blue-100 text-blue-700",
  Festival: "bg-orange-100 text-orange-700",
  Comedy: "bg-yellow-100 text-yellow-700",
  Dance: "bg-fuchsia-100 text-fuchsia-700",
  Religious: "bg-indigo-100 text-indigo-700",
  Education: "bg-teal-100 text-teal-700",
  Competition: "bg-emerald-100 text-emerald-700",
  Entertainment: "bg-pink-100 text-pink-700",
  Technology: "bg-cyan-100 text-cyan-700",
  Other: "bg-gray-100 text-gray-700",
};

function CategoryBadge({ category }: { category: string | null }) {
  const cat = category || "Other";
  const color = CAT_BADGE_COLORS[cat] || CAT_BADGE_COLORS.Other;
  const emoji = CAT_EMOJI[cat] || "📌";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${color}`}>
      {emoji} {cat}
    </span>
  );
}

function categoryEmoji(category: string | null): string {
  return CAT_EMOJI[category || "Other"] || "🎪";
}

/* ------------------------------------------------------------------ */
/* Event Card                                                         */
/* ------------------------------------------------------------------ */
/** Decode common HTML entities scrapers leave behind */
function decodeHTMLEntities(text: string): string {
  const el = document.createElement("textarea");
  el.innerHTML = text;
  return el.value;
}

function EventCard({ event, distance }: { event: EventItem; distance?: number }) {
  const dateStr = formatEventDate(event.date, event.end_date);
  const location = [event.venue_name, event.city, event.state]
    .filter(Boolean)
    .join(", ");

  const card = (
    <article className="group flex flex-col sm:flex-row bg-card border border-border rounded-lg overflow-hidden hover:border-primary/40 transition-colors w-full box-border" style={{ wordBreak: "break-word" }}>
      {/* Image */}
      {event.image_url ? (
        <div className="w-full sm:w-56 sm:min-w-[14rem] sm:h-auto overflow-hidden flex-shrink-0">
          <img
            src={event.image_url}
            alt={event.title}
            className="w-full h-auto max-h-64 sm:max-h-none sm:h-full object-contain sm:object-cover bg-muted/10 group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        </div>
      ) : (
        <div className="w-full sm:w-56 sm:min-w-[14rem] sm:h-auto overflow-hidden flex-shrink-0">
          <img
            src={categoryFallbackImg(event.category)}
            alt={event.category || "Event"}
            className="w-full h-auto max-h-64 sm:max-h-none sm:h-full object-cover bg-muted/10 group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        </div>
      )}

      {/* Content */}
      <div className="flex-1 p-4 sm:py-4 sm:pr-4 sm:pl-4 flex flex-col justify-between min-w-0 overflow-hidden">
        <div>
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <CategoryBadge category={event.category} />
            {distance != null && distance < 9999 && (
              <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-orange-600/20 text-orange-300">
                📍 {formatDistance(distance)}
              </span>
            )}
            {event.audience && (
              <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-700">
                👤 {event.audience}
              </span>
            )}
            {event.price_range && (
              <span className="text-xs text-muted-foreground font-medium">
                {event.price_range}
              </span>
            )}
          </div>
          <h3 className="font-serif text-lg font-semibold text-foreground leading-snug mb-1 line-clamp-2 group-hover:text-primary transition-colors">
            {decodeHTMLEntities(event.title)}
          </h3>
          {event.description && (
            <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
              {event.description}
            </p>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground mt-auto pt-2">
          <span className="text-primary font-semibold whitespace-nowrap">
            📅 {dateStr}
            {event.time && ` · ${event.time}`}
          </span>
          {location && (
            <span className="truncate">📍 {location}</span>
          )}
          {event.organizer && (
            <span className="truncate opacity-70">by {event.organizer}</span>
          )}
        </div>
      </div>
    </article>
  );

  const eventSlug = event.slug || generateSlug(event.title, event.date);

  return (
    <Link to={`/events/${eventSlug}`} className="block no-underline">
      {card}
    </Link>
  );
}

/* ------------------------------------------------------------------ */
/* Date Quick-Filter Bar                                              */
/* ------------------------------------------------------------------ */
const DATE_FILTER_OPTIONS: { key: DateFilterKey; label: string }[] = [
  { key: null,        label: "All Dates" },
  { key: "today",     label: "Today" },
  { key: "tomorrow",  label: "Tomorrow" },
  { key: "weekend",   label: "This Weekend" },
  { key: "week",      label: "This Week" },
  { key: "month",     label: "This Month" },
];

function DateFilterBar({
  selected,
  onSelect,
}: {
  selected: DateFilterKey;
  onSelect: (v: DateFilterKey) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-1.5 mb-3">
      {DATE_FILTER_OPTIONS.map((opt) => {
        const isActive = selected === opt.key;
        return (
          <button
            key={opt.key ?? "all"}
            onClick={() => onSelect(opt.key)}
            className={`px-3 py-1 text-xs font-medium rounded-full border transition-colors whitespace-nowrap ${
              isActive
                ? "bg-primary text-white border-primary"
                : "bg-background text-muted-foreground border-border hover:border-foreground/30 hover:text-foreground"
            }`}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Dynamic Category Pills with Counts                                 */
/* ------------------------------------------------------------------ */
function DynamicCategoryPills({
  counts,
  selected,
  onSelect,
}: {
  counts: Record<string, number>;
  selected: string | null;
  onSelect: (cat: string | null) => void;
}) {
  /* Sort categories by count (descending), then alphabetically */
  const sortedCategories = useMemo(() => {
    return Object.entries(counts)
      .filter(([, count]) => count > 0)
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .map(([cat]) => cat);
  }, [counts]);

  const total = useMemo(
    () => Object.values(counts).reduce((s, c) => s + c, 0),
    [counts],
  );

  if (sortedCategories.length === 0) return null;

  return (
    <div className="flex items-center gap-1.5 mb-4 overflow-x-auto pb-1 scrollbar-hide -mx-1 px-1">
      {/* All pill */}
      <button
        onClick={() => onSelect(null)}
        className={`flex-shrink-0 inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-full transition-colors whitespace-nowrap ${
          selected === null
            ? "bg-primary text-primary-foreground shadow-sm"
            : "bg-muted/50 text-foreground/70 hover:bg-muted"
        }`}
      >
        🎪 All
        <span className={`ml-0.5 ${selected === null ? "text-primary-foreground/80" : "text-muted-foreground"}`}>
          ({total})
        </span>
      </button>

      {sortedCategories.map((cat) => {
        const isActive = selected === cat;
        const emoji = CAT_EMOJI[cat] || "📌";
        return (
          <button
            key={cat}
            onClick={() => onSelect(isActive ? null : cat)}
            className={`flex-shrink-0 inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-full transition-colors whitespace-nowrap ${
              isActive
                ? "bg-primary text-primary-foreground shadow-sm"
                : "bg-muted/50 text-foreground/70 hover:bg-muted"
            }`}
          >
            {emoji} {cat}
            <span className={`ml-0.5 ${isActive ? "text-primary-foreground/80" : "text-muted-foreground"}`}>
              ({counts[cat]})
            </span>
          </button>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Featured Events Carousel                                           */
/* ------------------------------------------------------------------ */
function FeaturedCarouselCard({ event }: { event: EventItem }) {
  const dateStr = formatEventDate(event.date, event.end_date);
  const slug = event.slug || generateSlug(event.title, event.date);

  return (
    <Link
      to={`/events/${slug}`}
      className="block flex-shrink-0 w-[85vw] sm:w-[320px] snap-start no-underline group"
    >
      <div className="relative rounded-xl overflow-hidden border-2 border-amber-200/60 bg-card hover:border-amber-300 transition-all shadow-sm hover:shadow-md h-full">
        {/* Image or emoji fallback */}
        {event.image_url ? (
          <div className="aspect-[16/10] overflow-hidden">
            <img
              src={event.image_url}
              alt={event.title}
              className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-300"
              loading="lazy"
            />
          </div>
        ) : (
          <div className="aspect-[16/10] overflow-hidden">
            <img
              src={categoryFallbackImg(event.category)}
              alt={event.category || "Event"}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              loading="lazy"
            />
          </div>
        )}

        {/* Featured badge */}
        <div className="absolute top-2.5 left-2.5">
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/90 text-white text-xs font-semibold shadow-sm">
            ✨ Featured
          </span>
        </div>

        {/* Content */}
        <div className="p-3.5">
          <h3 className="font-serif text-base font-semibold text-foreground leading-snug line-clamp-2 group-hover:text-primary transition-colors mb-1.5">
            {event.title}
          </h3>
          <p className="text-sm text-primary font-medium mb-1">
            📅 {dateStr}
            {event.time && ` · ${event.time}`}
          </p>
          <p className="text-sm text-muted-foreground truncate">
            📍 {[event.venue_name, event.city].filter(Boolean).join(", ")}
          </p>
        </div>
      </div>
    </Link>
  );
}

/* ------------------------------------------------------------------ */
/* Discovery Sections (BookMyShow-style)                              */
/* ------------------------------------------------------------------ */

/** Gradient palettes for time-based cards */
const TIME_CARD_STYLES: { key: DateFilterKey; label: string; sublabel: string; gradient: string; darkGradient: string }[] = [
  {
    key: "today",
    label: "Plan for Today",
    sublabel: "Happening now",
    gradient: "linear-gradient(135deg, #A32D2F 0%, #D4A843 100%)",
    darkGradient: "linear-gradient(135deg, #7a2123 0%, #a8862f 100%)",
  },
  {
    key: "tomorrow",
    label: "Plan for Tomorrow",
    sublabel: "Coming up next",
    gradient: "linear-gradient(135deg, #0B1D3A 0%, #A32D2F 100%)",
    darkGradient: "linear-gradient(135deg, #091529 0%, #7a2123 100%)",
  },
  {
    key: "weekend",
    label: "Weekend Plans",
    sublabel: "Make it count",
    gradient: "linear-gradient(135deg, #D4A843 0%, #0B1D3A 100%)",
    darkGradient: "linear-gradient(135deg, #a8862f 0%, #091529 100%)",
  },
];

function TimeDiscoveryCards({
  counts,
  onSelect,
}: {
  counts: Record<string, number>;
  onSelect: (key: DateFilterKey) => void;
}) {
  return (
    <section className="mb-8">
      <div className="flex items-center gap-3 mb-4">
        <h2 className="font-serif text-xl md:text-2xl text-foreground whitespace-nowrap">
          Best Events This Week
        </h2>
        <div className="h-px flex-1 bg-border" />
      </div>
      <p className="text-sm text-muted-foreground mb-4 -mt-2">
        Monday to Sunday, we got you covered
      </p>

      <div className="flex gap-3 overflow-x-auto pb-2 -mx-1 px-1 scrollbar-hide">
        {TIME_CARD_STYLES.map((card) => {
          const count = counts[card.key || ""] || 0;
          return (
            <button
              key={card.key}
              onClick={() => onSelect(card.key)}
              className="flex-shrink-0 w-[160px] sm:w-[200px] rounded-xl overflow-hidden text-left transition-transform hover:scale-[1.03] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-primary/40"
            >
              <div
                className="p-5 h-[120px] sm:h-[140px] flex flex-col justify-end"
                style={{ background: card.gradient }}
              >
                <span className="text-white/70 text-xs font-medium uppercase tracking-wider mb-1">
                  {card.sublabel}
                </span>
                <span className="text-white text-lg sm:text-xl font-bold font-serif leading-tight">
                  {card.label}
                </span>
                <span className="text-white/80 text-sm font-medium mt-1.5">
                  {count > 0 ? `${count}+ Events` : "View Events"}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function CategoryDiscoveryGrid({
  counts,
  onSelect,
}: {
  counts: Record<string, number>;
  onSelect: (cat: string | null) => void;
}) {
  const sortedCategories = useMemo(() => {
    return Object.entries(counts)
      .filter(([, count]) => count > 0)
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .map(([cat, count]) => ({ cat, count }));
  }, [counts]);

  if (sortedCategories.length === 0) return null;

  return (
    <section className="mb-8">
      <div className="flex items-center gap-3 mb-4">
        <h2 className="font-serif text-xl md:text-2xl text-foreground whitespace-nowrap">
          Browse Events By Category
        </h2>
        <div className="h-px flex-1 bg-border" />
      </div>
      <p className="text-sm text-muted-foreground mb-4 -mt-2">
        Find events that match your interests
      </p>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {sortedCategories.slice(0, 8).map(({ cat, count }) => {
          const emoji = CAT_EMOJI[cat] || "📌";
          const imgSrc = CAT_FALLBACK_IMG[cat] || CAT_FALLBACK_IMG["Other"];
          return (
            <button
              key={cat}
              onClick={() => onSelect(cat)}
              className="group relative rounded-xl overflow-hidden text-left transition-transform hover:scale-[1.03] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-primary/40"
            >
              <div className="aspect-[4/3] relative">
                <img
                  src={imgSrc}
                  alt={cat}
                  className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  loading="lazy"
                />
                {/* Dark overlay for text readability */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-black/20" />
                {/* Content */}
                <div className="absolute inset-0 p-3 sm:p-4 flex flex-col justify-end">
                  <span className="text-white text-base sm:text-lg font-bold font-serif leading-tight drop-shadow-lg">
                    {emoji} {cat}
                  </span>
                  <span className="text-white/80 text-xs sm:text-sm font-medium mt-1 drop-shadow">
                    {count} {count === 1 ? "Event" : "Events"}
                  </span>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function DiscoverySection({
  onDateSelect,
  onCategorySelect,
}: {
  onDateSelect: (key: DateFilterKey) => void;
  onCategorySelect: (cat: string | null) => void;
}) {
  const [timeCounts, setTimeCounts] = useState<Record<string, number>>({});
  const [catCounts, setCatCounts] = useState<Record<string, number>>({});
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const today = new Date().toISOString().slice(0, 10);
    supabaseRaw
      .from("events")
      .select("id,date,category")
      .gte("date", today)
      .limit(5000)
      .then(({ data }: { data: { id: string; date: string; category: string | null }[] | null }) => {
        if (!data) { setLoaded(true); return; }

        // Compute time-based counts
        const tc: Record<string, number> = {};
        for (const key of ["today", "tomorrow", "weekend"] as DateFilterKey[]) {
          const range = getDateFilterRange(key);
          if (range) {
            tc[key || ""] = data.filter((e) => e.date >= range.from && e.date <= range.to).length;
          }
        }
        setTimeCounts(tc);

        // Compute category counts
        const cc: Record<string, number> = {};
        for (const e of data) {
          const cat = e.category || "Other";
          cc[cat] = (cc[cat] || 0) + 1;
        }
        setCatCounts(cc);
        setLoaded(true);
      });
  }, []);

  if (!loaded) return null;

  const hasTimeEvents = Object.values(timeCounts).some((c) => c > 0);

  return (
    <>
      {hasTimeEvents && (
        <TimeDiscoveryCards counts={timeCounts} onSelect={onDateSelect} />
      )}
      <CategoryDiscoveryGrid counts={catCounts} onSelect={onCategorySelect} />
    </>
  );
}

/* ------------------------------------------------------------------ */
/* Featured Events Carousel                                           */
/* ------------------------------------------------------------------ */
function FeaturedEventsSection() {
  const [featured, setFeatured] = useState<EventItem[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    getFeaturedEvents().then((data) => {
      setFeatured(data);
      setLoaded(true);
    });
  }, []);

  if (!loaded || featured.length === 0) return null;

  return (
    <section className="mb-8">
      <div className="flex items-center gap-3 mb-4">
        <h2 className="font-serif text-xl md:text-2xl text-foreground whitespace-nowrap">
          ✨ Featured Events
        </h2>
        <div className="h-px flex-1 bg-border" />
      </div>

      <div
        className="flex gap-4 overflow-x-auto snap-x snap-mandatory pb-2 -mx-1 px-1"
        style={{ scrollbarWidth: "thin" }}
      >
        {featured.map((event) => (
          <FeaturedCarouselCard key={event.id} event={event} />
        ))}
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* Smart Search Chips                                                 */
/* ------------------------------------------------------------------ */
function SmartSearchChips({ chips, onClear }: { chips: string[]; onClear: () => void }) {
  if (chips.length === 0) return null;
  return (
    <div className="flex flex-wrap items-center gap-1.5 mt-2">
      <span className="text-[10px] text-muted-foreground/60 font-medium uppercase tracking-wider mr-0.5">
        Smart search:
      </span>
      {chips.map((chip, i) => (
        <span
          key={i}
          className="inline-flex items-center px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-medium"
        >
          {chip}
        </span>
      ))}
      <button
        onClick={onClear}
        className="text-[10px] text-muted-foreground hover:text-foreground ml-1 underline"
      >
        clear
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Events Page                                                        */
/* ------------------------------------------------------------------ */
export default function EventsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [allFetchedEvents, setAllFetchedEvents] = useState<(EventWithDistance | EventItem)[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  /** Monotonic counter to discard stale fetch results */
  const fetchVersionRef = useRef(0);
  /** Whether the current result set was fetched client-side (all events loaded) */
  const [isClientFiltered, setIsClientFiltered] = useState(false);

  /* --- Search state --- */
  const [searchInput, setSearchInput] = useState(searchParams.get("q") || "");
  const searchQuery = searchParams.get("q") || "";
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  /* --- Date filter state --- */
  const dateFilterParam = (searchParams.get("when") || null) as DateFilterKey;

  /* --- Category filter state (replaces old tab filter) --- */
  const categoryParam = searchParams.get("category") || null;

  /* --- Smart search parsed result --- */
  const parsed = useMemo<ParsedSearch>(
    () => parseSearchQuery(searchQuery),
    [searchQuery],
  );
  const smartChips = useMemo(() => getSmartChips(parsed), [parsed]);

  /* Effective date filter: URL param wins, then smart-search extracted date */
  const effectiveDateFilter = dateFilterParam ?? parsed.dateFilter;

  /* --- Geolocation / zip code state --- */
  const [nearMeActive, setNearMeActive] = useState(() => {
    try { return !!sessionStorage.getItem("videshi_events_coords"); } catch { return false; }
  });
  const [userCoords, setUserCoords] = useState<{ lat: number; lng: number } | null>(() => {
    try {
      const saved = sessionStorage.getItem("videshi_events_coords");
      return saved ? JSON.parse(saved) : null;
    } catch { return null; }
  });
  const [locationLabel, setLocationLabel] = useState<string>(() => {
    try { return sessionStorage.getItem("videshi_events_label") || ""; } catch { return ""; }
  });
  const { location: ipLocation } = useUserLocation();

  /* --- Persist coords in sessionStorage so back-nav doesn't re-prompt --- */
  useEffect(() => {
    try {
      if (userCoords) {
        sessionStorage.setItem("videshi_events_coords", JSON.stringify(userCoords));
        sessionStorage.setItem("videshi_events_label", locationLabel);
      } else {
        sessionStorage.removeItem("videshi_events_coords");
        sessionStorage.removeItem("videshi_events_label");
      }
    } catch { /* noop */ }
  }, [userCoords, locationLabel]);

  /* --- Sync filters with URL --- */
  const rawCity = searchParams.get("city");
  const cityFilter = nearMeActive ? null : (rawCity ?? DEFAULT_CITY);

  const setCityFilter = useCallback((city: string | null) => {
    setNearMeActive(false);
    setUserCoords(null);
    setLocationLabel("");
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (city && city !== DEFAULT_CITY) {
        next.set("city", city);
      } else {
        next.delete("city");
      }
      next.delete("nearme");
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  /* --- Location handler (from ZipCodeSearch) --- */
  const handleLocation = useCallback((result: LocationResult | null) => {
    if (!result) {
      setNearMeActive(false);
      setUserCoords(null);
      setLocationLabel("");
      setCityFilter(DEFAULT_CITY);
      return;
    }
    setUserCoords({ lat: result.lat, lng: result.lng });
    setNearMeActive(true);
    setLocationLabel(result.label);
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.delete("city");
      next.set("nearme", "1");
      return next;
    }, { replace: true });
  }, [setCityFilter, setSearchParams]);

  const setCategoryFilter = useCallback((cat: string | null) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (cat) next.set("category", cat); else next.delete("category");
      // Remove old "tab" param if it still exists
      next.delete("tab");
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  const setDateFilter = useCallback((when: DateFilterKey) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (when) next.set("when", when); else next.delete("when");
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  /* --- Debounced search handler --- */
  const handleSearchChange = useCallback((value: string) => {
    setSearchInput(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        if (value.trim()) next.set("q", value.trim()); else next.delete("q");
        return next;
      }, { replace: true });
    }, 300);
  }, [setSearchParams]);

  const clearSearch = useCallback(() => {
    setSearchInput("");
    if (debounceRef.current) clearTimeout(debounceRef.current);
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.delete("q");
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  const PAGE_SIZE = 30;

  /* --- Auto-request geolocation on page load --- */
  useEffect(() => {
    if (rawCity) return;
    if (!nearMeActive && !userCoords && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = { lat: position.coords.latitude, lng: position.coords.longitude };
          setUserCoords(coords);
          setNearMeActive(true);
          setLocationLabel("📍 Near You");
          setSearchParams((prev) => {
            const next = new URLSearchParams(prev);
            next.delete("city");
            next.set("nearme", "1");
            return next;
          }, { replace: true });
        },
        () => {
          if (ipLocation) {
            const coords = { lat: ipLocation.latitude, lng: ipLocation.longitude };
            setUserCoords(coords);
            setNearMeActive(true);
            setLocationLabel(ipLocation.city ? `📍 Near ${ipLocation.city}` : "📍 Near You");
            setSearchParams((prev) => {
              const next = new URLSearchParams(prev);
              next.delete("city");
              next.set("nearme", "1");
              return next;
            }, { replace: true });
          } else {
            setNearMeActive(false);
          }
        },
        { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 },
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ipLocation]);

  /* --- Client-side smart filter (location + date + search, NO category) --- */
  const applySmartFilters = useCallback(
    (data: EventItem[]): EventItem[] => {
      let filtered = data;

      // Date filter (from URL param or smart search)
      const dateRange = getDateFilterRange(effectiveDateFilter);
      if (dateRange) {
        filtered = filtered.filter(
          (e) => e.date >= dateRange.from && e.date <= dateRange.to,
        );
      }

      // Smart search: city hints
      if (parsed.cityHints.length > 0) {
        const cities = new Set(parsed.cityHints.map((c) => c.toLowerCase()));
        filtered = filtered.filter((e) => e.city && cities.has(e.city.toLowerCase()));
      }

      // Smart search: state hints
      if (parsed.stateHints.length > 0) {
        const states = new Set(parsed.stateHints.map((s) => s.toUpperCase()));
        filtered = filtered.filter((e) => e.state && states.has(e.state.toUpperCase()));
      }

      // Smart search: category hints from SEARCH (not from URL param — that's applied later)
      if (parsed.categoryHints.length > 0) {
        const cats = new Set(parsed.categoryHints);
        filtered = filtered.filter((e) => e.category && cats.has(e.category));
      }

      // Smart search: price filter
      if (parsed.priceFilter === "free") {
        filtered = filtered.filter((e) => matchesFreeFilter(e.price_range));
      }

      // Smart search: remaining keywords
      if (parsed.keywords.length > 0) {
        filtered = filtered.filter((e) => matchesKeywords(e, parsed.keywords));
      }

      return filtered;
    },
    [effectiveDateFilter, parsed],
  );

  /* --- Fetch events --- */
  useEffect(() => {
    const version = ++fetchVersionRef.current;
    setLoading(true);
    setHasMore(true);

    if (nearMeActive && userCoords) {
      // Near Me mode: fetch ALL events, sort by distance, then apply smart filters client-side
      getAllUpcomingEvents(null, undefined).then((data) => {
        if (fetchVersionRef.current !== version) return; // stale
        const smartFiltered = applySmartFilters(data);
        const sorted = sortEventsByDistance(smartFiltered, userCoords.lat, userCoords.lng);
        setAllFetchedEvents(sorted);
        setIsClientFiltered(true);
        setHasMore(false);
        setLoading(false);
      });
    } else if (
      // If smart search has city/state/price/keyword hints or date filter, fetch all + filter client-side
      parsed.cityHints.length > 0 ||
      parsed.stateHints.length > 0 ||
      parsed.priceFilter ||
      parsed.keywords.length > 0 ||
      effectiveDateFilter
    ) {
      getAllUpcomingEvents(null, undefined).then((data) => {
        if (fetchVersionRef.current !== version) return; // stale
        const smartFiltered = applySmartFilters(data);
        setAllFetchedEvents(smartFiltered);
        setIsClientFiltered(true);
        setHasMore(false);
        setLoading(false);
      });
    } else {
      // Normal mode: server-side city filter + pagination (no category filter applied here)
      const filterCity = cityFilter;
      getEventsMultiCategory(filterCity, null, PAGE_SIZE, 0, searchQuery || undefined).then((data) => {
        if (fetchVersionRef.current !== version) return; // stale
        setAllFetchedEvents(data);
        setIsClientFiltered(false);
        setHasMore(data.length === PAGE_SIZE);
        setLoading(false);
      });
    }
  }, [cityFilter, nearMeActive, userCoords, searchQuery, effectiveDateFilter, applySmartFilters, parsed]);

  /* ------------------------------------------------------------- */
  /* Two-stage pipeline: pre-category events → counts → displayed  */
  /* ------------------------------------------------------------- */

  /** Stage 1 result: events BEFORE category filter (used for category counts) */
  const preFilteredEvents = allFetchedEvents;

  /** Compute category counts from Stage 1 */
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    preFilteredEvents.forEach((e) => {
      const cat = e.category || "Other";
      counts[cat] = (counts[cat] || 0) + 1;
    });
    return counts;
  }, [preFilteredEvents]);

  /** Stage 2: apply the URL category filter to get displayed events */
  const displayedEvents = useMemo(() => {
    if (!categoryParam) return preFilteredEvents;
    return preFilteredEvents.filter((e) => (e.category || "Other") === categoryParam);
  }, [preFilteredEvents, categoryParam]);

  const loadMore = async () => {
    if (loadingMore || !hasMore || nearMeActive || isClientFiltered) return;
    setLoadingMore(true);
    const next = await getEventsMultiCategory(cityFilter, null, PAGE_SIZE, allFetchedEvents.length, searchQuery || undefined);
    setAllFetchedEvents((prev) => [...prev, ...next]);
    setHasMore(next.length === PAGE_SIZE);
    setLoadingMore(false);
  };

  /* --- Summary text --- */
  const summaryParts: string[] = [];
  if (searchQuery) summaryParts.push(`matching "${searchQuery}"`);
  if (nearMeActive) summaryParts.push("near you");
  else if (cityFilter) summaryParts.push(`in ${cityFilter}`);
  if (categoryParam) summaryParts.push(`· ${categoryParam}`);
  if (effectiveDateFilter) {
    const labels: Record<string, string> = {
      today: "today", tomorrow: "tomorrow", weekend: "this weekend",
      week: "this week", month: "this month",
    };
    summaryParts.push(`· ${labels[effectiveDateFilter] || effectiveDateFilter}`);
  }
  const summaryText = summaryParts.length > 0 ? " " + summaryParts.join(" ") : "";

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Helmet>
        <title>Events — The Videshi</title>
        <meta
          name="description"
          content="Discover Indian cultural events, festivals, concerts, and community gatherings near you across the US."
        />
        <link rel="canonical" href="https://www.thevideshi.com/events" />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <style>{`
        .events-main { max-width: 100vw; overflow-x: hidden; }
        .events-main article { max-width: calc(100vw - 2.5rem); }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
      `}</style>
      <main className="events-main container flex-1 pt-8 md:pt-10 pb-16">
        {/* Header */}
        <div className="mb-6">
          <h1 className="font-serif text-3xl md:text-5xl text-foreground mb-3">
            Events
          </h1>
          <p className="text-muted-foreground text-lg">
            Indian concerts, festivals, cultural events &amp; community gatherings across the US
          </p>
        </div>

        {/* Featured Events Carousel */}
        <FeaturedEventsSection />

        {/* Discovery: Time Cards + Category Grid (BookMyShow-style) */}
        <DiscoverySection
          onDateSelect={setDateFilter}
          onCategorySelect={setCategoryFilter}
        />

        {/* Search + Location controls — one row on desktop, stacked on mobile */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-3">
          {/* Search bar */}
          <div className="relative flex-1 max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
              <svg className="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
            </div>
            <input
              type="text"
              value={searchInput}
              onChange={(e) => handleSearchChange(e.target.value)}
              placeholder={'Search "free garba near dallas this weekend"...'}
              className="w-full pl-10 pr-10 py-2.5 rounded-lg border border-border bg-background text-foreground text-sm placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary/40 transition-colors"
            />
            {searchInput && (
              <button
                onClick={clearSearch}
                className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-muted-foreground hover:text-foreground transition-colors"
                aria-label="Clear search"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
            {/* Smart search chips */}
            <SmartSearchChips chips={smartChips} onClear={clearSearch} />
          </div>

          {/* Location: Zip / Near Me + City dropdown */}
          <div className="flex items-center gap-3 flex-shrink-0">
          <ZipCodeSearch
            onLocation={handleLocation}
            active={nearMeActive}
          />

          {/* City dropdown */}
          <div className="relative flex-shrink-0">
            <select
              value={nearMeActive ? "" : (cityFilter || "")}
              onChange={(e) => setCityFilter(e.target.value || null)}
              className={`px-4 py-2.5 pr-9 rounded-lg border text-sm font-medium appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary/40 transition-colors ${
                nearMeActive
                  ? "bg-muted/20 border-border/50 text-muted-foreground/50"
                  : "bg-background border-border text-foreground"
              }`}
              style={{
                backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E\")",
                backgroundRepeat: "no-repeat",
                backgroundPosition: "right 12px center",
              }}
            >
              <option value="">All Cities</option>
              {CITY_GROUPS.map((g) => (
                <option key={g.label} value={g.label}>
                  {g.label}
                </option>
              ))}
            </select>
          </div>
          </div>

          {/* Submit Event link */}
          <div className="flex items-center gap-3">
            <Link
              to="/events/submit"
              className="inline-flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium text-primary border border-primary/30 hover:bg-primary/5 rounded-lg transition-colors whitespace-nowrap"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              Post Your Event
            </Link>
            <Link
              to="/events/submit?mode=manage"
              className="text-sm text-muted-foreground hover:text-primary transition-colors whitespace-nowrap"
            >
              Manage my events
            </Link>
          </div>
        </div>

        {/* Date quick-filter pills */}
        <DateFilterBar selected={dateFilterParam} onSelect={setDateFilter} />

        {/* Dynamic category pills with counts */}
        {!loading && (
          <DynamicCategoryPills
            counts={categoryCounts}
            selected={categoryParam}
            onSelect={setCategoryFilter}
          />
        )}

        {/* Events list */}
        {loading ? (
          <div className="grid gap-4">
            {[...Array(6)].map((_, i) => (
              <div
                key={i}
                className="h-40 rounded-lg bg-muted/20 animate-pulse"
              />
            ))}
          </div>
        ) : displayedEvents.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-4xl mb-4">🎪</p>
            <p className="text-muted-foreground text-lg">
              No upcoming events found{summaryText}.
            </p>
            <p className="text-muted-foreground text-sm mt-2">
              Try a different city or category, or check back soon!
            </p>
          </div>
        ) : (
          <>
            <p className="text-sm text-muted-foreground mb-4">
              {displayedEvents.length}{hasMore && !categoryParam ? "+" : ""} upcoming events{summaryText}
            </p>

            {/* Near-Me mode: split into "Nearby" and "More Events" */}
            {nearMeActive ? (
              <NearMeList events={displayedEvents as EventWithDistance[]} />
            ) : (
              <div className="grid grid-cols-1 gap-4 w-full min-w-0">
                {displayedEvents.map((event) => (
                  <EventCard key={event.id} event={event} />
                ))}
              </div>
            )}

            {/* Load more (normal mode only, no category filter active) */}
            {hasMore && !nearMeActive && !isClientFiltered && !categoryParam && (
              <div className="flex justify-center mt-8">
                <button
                  onClick={loadMore}
                  disabled={loadingMore}
                  className="px-6 py-3 rounded-lg bg-muted/40 text-foreground font-medium hover:bg-muted/60 transition-colors disabled:opacity-50"
                >
                  {loadingMore ? "Loading..." : "Load more events"}
                </button>
              </div>
            )}
          </>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Near-Me list with distance grouping                                */
/* ------------------------------------------------------------------ */
function NearMeList({ events }: { events: EventWithDistance[] }) {
  return (
    <div className="grid grid-cols-1 gap-4 w-full min-w-0">
      {events.map((event) => (
        <EventCard key={event.id} event={event} distance={event.distanceMiles} />
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Multi-category fetcher                                             */
/* ------------------------------------------------------------------ */
async function getEventsMultiCategory(
  cityFilter: string | null,
  categories: string[] | null,
  limit: number,
  offset: number,
  search?: string,
): Promise<EventItem[]> {
  const today = new Date().toISOString().slice(0, 10);

  let query = supabaseRaw
    .from("events")
    .select("id,title,date,time,end_date,venue_name,city,state,category,description,image_url,ticket_url,source,price_range,organizer,audience,long_description,artist_info,venue_info,slug")
    .gte("date", today)
    .order("date", { ascending: true })
    .range(offset, offset + limit - 1);

  if (cityFilter) {
    const group = CITY_GROUPS.find((g) => g.label === cityFilter);
    if (group) {
      query = query.in("city", group.cities);
    }
  }

  if (categories && categories.length > 0) {
    query = query.in("category", categories);
  }

  if (search) {
    const q = `%${search}%`;
    query = query.or(
      `title.ilike.${q},description.ilike.${q},long_description.ilike.${q},artist_info.ilike.${q},venue_name.ilike.${q},city.ilike.${q},organizer.ilike.${q}`
    );
  }

  const { data, error } = await query;

  if (error) {
    console.error("Failed to fetch events:", error);
    return [];
  }

  return (data || []) as EventItem[];
}
