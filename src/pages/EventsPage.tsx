import { useEffect, useState, useCallback } from "react";
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
  formatDistance,
  generateSlug,
  getDistanceMiles,
  getCityCoords,
  sortEventsByDistance,
  getAllUpcomingEvents,
  CITY_GROUPS,
} from "@/lib/events";

const supabaseRaw = supabaseTyped as unknown as { from: (table: string) => any };

/* ------------------------------------------------------------------ */
/* Tab groups — map high-level tabs to DB category values              */
/* ------------------------------------------------------------------ */
const TAB_GROUPS: { label: string; emoji: string; categories: string[] }[] = [
  { label: "Entertainment", emoji: "🎶", categories: ["Music", "Comedy", "Dance", "Cultural", "Festival", "Food"] },
  { label: "Community",     emoji: "🤝", categories: ["Community", "Other"] },
  { label: "Sports & Fitness", emoji: "🏃", categories: ["Sports"] },
  { label: "Education",     emoji: "🎓", categories: ["Education", "Competition"] },
  { label: "Spiritual",     emoji: "🙏", categories: ["Religious"] },
];

/** Map a raw DB category to its tab group label */
function getTabLabel(category: string | null): string {
  if (!category) return "Community";
  for (const tab of TAB_GROUPS) {
    if (tab.categories.includes(category)) return tab.label;
  }
  return "Community";
}

/** Get categories for a tab (for DB filtering) */
function getTabCategories(tabLabel: string): string[] {
  const tab = TAB_GROUPS.find((t) => t.label === tabLabel);
  return tab ? tab.categories : [];
}

/* ------------------------------------------------------------------ */
/* Badge colors (by tab group)                                        */
/* ------------------------------------------------------------------ */
const TAB_COLORS: Record<string, string> = {
  Entertainment:      "bg-pink-600/20 text-pink-300",
  Community:          "bg-blue-600/20 text-blue-300",
  "Sports & Fitness": "bg-green-600/20 text-green-300",
  Education:          "bg-teal-600/20 text-teal-300",
  Spiritual:          "bg-indigo-600/20 text-indigo-300",
};

const TAB_EMOJI: Record<string, string> = {
  Entertainment: "🎶",
  Community: "🤝",
  "Sports & Fitness": "🏃",
  Education: "🎓",
  Spiritual: "🙏",
};

function GroupBadge({ category }: { category: string | null }) {
  const group = getTabLabel(category);
  const color = TAB_COLORS[group] || TAB_COLORS.Community;
  const emoji = TAB_EMOJI[group] || "📌";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${color}`}>
      {emoji} {group}
    </span>
  );
}

function categoryEmoji(category: string | null): string {
  const group = getTabLabel(category);
  return TAB_EMOJI[group] || "🎪";
}

/* ------------------------------------------------------------------ */
/* Event Card                                                         */
/* ------------------------------------------------------------------ */
function EventCard({ event }: { event: EventItem }) {
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
        <div className="w-full sm:w-48 sm:min-w-[12rem] h-32 sm:h-auto bg-muted/30 flex items-center justify-center flex-shrink-0">
          <span className="text-4xl opacity-60">{categoryEmoji(event.category)}</span>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 p-4 sm:py-4 sm:pr-4 sm:pl-4 flex flex-col justify-between min-w-0 overflow-hidden">
        <div>
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <GroupBadge category={event.category} />
            {event.audience && (
              <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-emerald-600/20 text-emerald-300">
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
            {event.title}
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
    <Link
      to={`/events/${eventSlug}`}
      className="block no-underline"
    >
      {card}
    </Link>
  );
}

/* ------------------------------------------------------------------ */
/* City Filter Pills                                                  */
/* ------------------------------------------------------------------ */
function FilterPills({
  options,
  selected,
  onSelect,
  allLabel = "All",
}: {
  options: string[];
  selected: string | null;
  onSelect: (v: string | null) => void;
  allLabel?: string;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={() => onSelect(null)}
        className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
          selected === null
            ? "bg-foreground text-background"
            : "bg-muted/40 text-muted-foreground hover:bg-muted/60"
        }`}
      >
        {allLabel}
      </button>
      {options.map((opt) => (
        <button
          key={opt}
          onClick={() => onSelect(opt)}
          className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
            selected === opt
              ? "bg-foreground text-background"
              : "bg-muted/40 text-muted-foreground hover:bg-muted/60"
          }`}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Tab Bar                                                            */
/* ------------------------------------------------------------------ */
function TabBar({
  selected,
  onSelect,
}: {
  selected: string | null;
  onSelect: (v: string | null) => void;
}) {
  return (
    <div className="flex items-center gap-1 overflow-x-auto pb-1 scrollbar-none -mx-1 px-1">
      <button
        onClick={() => onSelect(null)}
        className={`relative whitespace-nowrap px-4 py-2.5 text-sm font-medium transition-colors rounded-t-md ${
          selected === null
            ? "text-foreground"
            : "text-muted-foreground hover:text-foreground/70"
        }`}
      >
        All
        {selected === null && (
          <span className="absolute bottom-0 left-2 right-2 h-[2px] bg-primary rounded-full" />
        )}
      </button>
      {TAB_GROUPS.map((tab) => (
        <button
          key={tab.label}
          onClick={() => onSelect(tab.label)}
          className={`relative whitespace-nowrap px-4 py-2.5 text-sm font-medium transition-colors rounded-t-md ${
            selected === tab.label
              ? "text-foreground"
              : "text-muted-foreground hover:text-foreground/70"
          }`}
        >
          <span className="mr-1.5">{tab.emoji}</span>
          {tab.label}
          {selected === tab.label && (
            <span className="absolute bottom-0 left-2 right-2 h-[2px] bg-primary rounded-full" />
          )}
        </button>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Events Page                                                        */
/* ------------------------------------------------------------------ */
export default function EventsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

  // Sync filters with URL params
  const cityFilter = searchParams.get("city") || null;
  const tabFilter = searchParams.get("tab") || null;

  const setCityFilter = (city: string | null) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (city) next.set("city", city); else next.delete("city");
      return next;
    }, { replace: true });
  };

  const setTabFilter = (tab: string | null) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (tab) next.set("tab", tab); else next.delete("tab");
      return next;
    }, { replace: true });
  };

  const PAGE_SIZE = 30;

  // Convert tab to category filter for the data layer
  const categoryFilters = tabFilter ? getTabCategories(tabFilter) : null;

  useEffect(() => {
    setLoading(true);
    setHasMore(true);

    getEventsMultiCategory(cityFilter, categoryFilters, PAGE_SIZE, 0).then((data) => {
      setEvents(data);
      setHasMore(data.length === PAGE_SIZE);
      setLoading(false);
    });
  }, [cityFilter, tabFilter]);

  const loadMore = async () => {
    if (loadingMore || !hasMore) return;
    setLoadingMore(true);
    const next = await getEventsMultiCategory(cityFilter, categoryFilters, PAGE_SIZE, events.length);
    setEvents((prev) => [...prev, ...next]);
    setHasMore(next.length === PAGE_SIZE);
    setLoadingMore(false);
  };

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Helmet>
        <title>Events — The Videshi</title>
        <meta
          name="description"
          content="Discover Indian cultural events, festivals, concerts, and community gatherings near you across the US."
        />
        <link rel="canonical" href="/events" />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <style>{`
        .events-main { max-width: 100vw; overflow-x: hidden; }
        .events-main article { max-width: calc(100vw - 2.5rem); }
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

        {/* Tab bar — horizontal scroll so all categories visible */}
        <div className="border-b border-border mb-4">
          <div className="overflow-x-auto scrollbar-hide -mx-4 px-4">
            <TabBar selected={tabFilter} onSelect={setTabFilter} />
          </div>
        </div>

        {/* City dropdown */}
        <div className="mb-8">
          <select
            value={cityFilter || ""}
            onChange={(e) => setCityFilter(e.target.value || null)}
            className="w-full sm:w-auto px-4 py-2.5 rounded-lg border border-border bg-background text-foreground text-sm font-medium appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary/40"
            style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E\")", backgroundRepeat: "no-repeat", backgroundPosition: "right 12px center", paddingRight: "36px" }}
          >
            <option value="">📍 All Cities</option>
            {CITY_GROUPS.map((g) => (
              <option key={g.label} value={g.label}>
                {g.label}
              </option>
            ))}
          </select>
        </div>

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
        ) : events.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-4xl mb-4">🎪</p>
            <p className="text-muted-foreground text-lg">
              No upcoming events found
              {cityFilter ? ` in ${cityFilter}` : ""}
              {tabFilter ? ` for ${tabFilter}` : ""}
              .
            </p>
            <p className="text-muted-foreground text-sm mt-2">
              Try a different city or category, or check back soon!
            </p>
          </div>
        ) : (
          <>
            <p className="text-sm text-muted-foreground mb-4">
              {events.length}{hasMore ? "+" : ""} upcoming events
              {cityFilter ? ` in ${cityFilter}` : ""}
              {tabFilter ? ` · ${tabFilter}` : ""}
            </p>
            <div className="grid grid-cols-1 gap-4 w-full min-w-0">
              {events.map((event) => (
                <EventCard key={event.id} event={event} />
              ))}
            </div>

            {/* Load more */}
            {hasMore && (
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
/* Multi-category fetcher (for tab groups)                            */
/* ------------------------------------------------------------------ */

async function getEventsMultiCategory(
  cityFilter: string | null,
  categories: string[] | null,
  limit: number,
  offset: number,
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

  const { data, error } = await query;

  if (error) {
    console.error("Failed to fetch events:", error);
    return [];
  }

  return (data || []) as EventItem[];
}
