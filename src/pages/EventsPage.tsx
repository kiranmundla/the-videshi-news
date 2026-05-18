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
  sortEventsByDistance,
  getAllUpcomingEvents,
  CITY_GROUPS,
} from "@/lib/events";

const supabaseRaw = supabaseTyped as unknown as { from: (table: string) => any };

const DEFAULT_CITY = "Bay Area";
const NEAR_ME = "__near_me__";

/* ------------------------------------------------------------------ */
/* Tab groups                                                         */
/* ------------------------------------------------------------------ */
const TAB_GROUPS: { label: string; emoji: string; categories: string[] }[] = [
  { label: "Entertainment", emoji: "🎶", categories: ["Music", "Comedy", "Dance", "Cultural", "Festival", "Food"] },
  { label: "Community",     emoji: "🤝", categories: ["Community", "Other"] },
  { label: "Sports & Fitness", emoji: "🏃", categories: ["Sports"] },
  { label: "Education",     emoji: "🎓", categories: ["Education", "Competition"] },
  { label: "Spiritual",     emoji: "🙏", categories: ["Religious"] },
];

function getTabLabel(category: string | null): string {
  if (!category) return "Community";
  for (const tab of TAB_GROUPS) {
    if (tab.categories.includes(category)) return tab.label;
  }
  return "Community";
}

function getTabCategories(tabLabel: string): string[] {
  const tab = TAB_GROUPS.find((t) => t.label === tabLabel);
  return tab ? tab.categories : [];
}

/* ------------------------------------------------------------------ */
/* Badge colors                                                       */
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
        <div className="w-full sm:w-48 sm:min-w-[12rem] h-32 sm:h-auto bg-muted/30 flex items-center justify-center flex-shrink-0">
          <span className="text-4xl opacity-60">{categoryEmoji(event.category)}</span>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 p-4 sm:py-4 sm:pr-4 sm:pl-4 flex flex-col justify-between min-w-0 overflow-hidden">
        <div>
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <GroupBadge category={event.category} />
            {distance != null && distance < 9999 && (
              <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-orange-600/20 text-orange-300">
                📍 {formatDistance(distance)}
              </span>
            )}
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
    <Link to={`/events/${eventSlug}`} className="block no-underline">
      {card}
    </Link>
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
    <div className="flex flex-wrap items-center gap-1 pb-1">
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
  const [events, setEvents] = useState<(EventWithDistance | EventItem)[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

  /* --- Geolocation state --- */
  const [nearMeActive, setNearMeActive] = useState(false);
  const [geoLoading, setGeoLoading] = useState(false);
  const [userCoords, setUserCoords] = useState<{ lat: number; lng: number } | null>(null);

  /* --- Sync filters with URL --- */
  // Default to Bay Area when no city param is present
  const rawCity = searchParams.get("city");
  const cityFilter = nearMeActive ? null : (rawCity ?? DEFAULT_CITY);
  const tabFilter = searchParams.get("tab") || null;

  const setCityFilter = useCallback((city: string | null) => {
    // Selecting a city deactivates Near Me
    setNearMeActive(false);
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (city && city !== DEFAULT_CITY) {
        next.set("city", city);
      } else {
        next.delete("city"); // Bay Area is default, keep URL clean
      }
      next.delete("nearme");
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  const setTabFilter = useCallback((tab: string | null) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (tab) next.set("tab", tab); else next.delete("tab");
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  const PAGE_SIZE = 30;
  const categoryFilters = tabFilter ? getTabCategories(tabFilter) : null;

  /* --- Near Me handler --- */
  const handleNearMe = useCallback(() => {
    if (nearMeActive) {
      // Toggle off → go back to Bay Area
      setNearMeActive(false);
      setCityFilter(DEFAULT_CITY);
      return;
    }

    if (!navigator.geolocation) {
      // No geolocation support — stay on Bay Area
      return;
    }

    setGeoLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const coords = { lat: position.coords.latitude, lng: position.coords.longitude };
        setUserCoords(coords);
        setNearMeActive(true);
        setGeoLoading(false);
        // Clean URL
        setSearchParams((prev) => {
          const next = new URLSearchParams(prev);
          next.delete("city");
          next.set("nearme", "1");
          return next;
        }, { replace: true });
      },
      () => {
        // Denied or error → silently stay on Bay Area
        setGeoLoading(false);
        setNearMeActive(false);
      },
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 },
    );
  }, [nearMeActive, setCityFilter, setSearchParams]);

  /* --- Auto-request geolocation on page load --- */
  useEffect(() => {
    // If user navigated here with an explicit city param, respect it
    if (rawCity) return;
    // Otherwise, auto-request location
    if (!nearMeActive && !userCoords && navigator.geolocation) {
      setGeoLoading(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = { lat: position.coords.latitude, lng: position.coords.longitude };
          setUserCoords(coords);
          setNearMeActive(true);
          setGeoLoading(false);
          setSearchParams((prev) => {
            const next = new URLSearchParams(prev);
            next.delete("city");
            next.set("nearme", "1");
            return next;
          }, { replace: true });
        },
        () => {
          // Denied or error → silently fall back to Bay Area
          setGeoLoading(false);
          setNearMeActive(false);
        },
        { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 },
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* --- Fetch events --- */
  useEffect(() => {
    setLoading(true);
    setHasMore(true);

    if (nearMeActive && userCoords) {
      // Near Me mode: fetch ALL events, sort by distance client-side
      getAllUpcomingEvents(categoryFilters).then((data) => {
        const sorted = sortEventsByDistance(data, userCoords.lat, userCoords.lng);
        setEvents(sorted);
        setHasMore(false); // All loaded, no pagination needed
        setLoading(false);
      });
    } else {
      // Normal mode: server-side city filter + pagination
      const filterCity = cityFilter;
      getEventsMultiCategory(filterCity, categoryFilters, PAGE_SIZE, 0).then((data) => {
        setEvents(data);
        setHasMore(data.length === PAGE_SIZE);
        setLoading(false);
      });
    }
  }, [cityFilter, tabFilter, nearMeActive, userCoords]);

  const loadMore = async () => {
    if (loadingMore || !hasMore || nearMeActive) return;
    setLoadingMore(true);
    const next = await getEventsMultiCategory(cityFilter, categoryFilters, PAGE_SIZE, events.length);
    setEvents((prev) => [...prev, ...next]);
    setHasMore(next.length === PAGE_SIZE);
    setLoadingMore(false);
  };

  /* --- Summary text --- */
  const summaryParts: string[] = [];
  if (nearMeActive) summaryParts.push("near you");
  else if (cityFilter) summaryParts.push(`in ${cityFilter}`);
  if (tabFilter) summaryParts.push(`· ${tabFilter}`);
  const summaryText = summaryParts.length > 0 ? " " + summaryParts.join(" ") : "";

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

        {/* Tab bar — all categories visible, wrapping on mobile */}
        <div className="border-b border-border mb-4">
          <TabBar selected={tabFilter} onSelect={setTabFilter} />
        </div>

        {/* Near Me button + City dropdown — side by side */}
        <div className="flex items-center gap-3 mb-8">
          {/* Near Me pill */}
          <button
            onClick={handleNearMe}
            disabled={geoLoading}
            className={`flex-shrink-0 px-4 py-2.5 rounded-lg text-sm font-medium transition-all border ${
              nearMeActive
                ? "bg-primary/15 border-primary/40 text-primary"
                : "bg-muted/40 border-border text-muted-foreground hover:bg-muted/60 hover:border-border"
            } ${geoLoading ? "opacity-60 cursor-wait" : "cursor-pointer"}`}
          >
            {geoLoading ? (
              <span className="flex items-center gap-1.5">
                <span className="inline-block w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
                Locating…
              </span>
            ) : nearMeActive ? (
              "📍 Near You"
            ) : (
              "📍 Near Me"
            )}
          </button>

          {/* City dropdown */}
          <div className="relative flex-shrink-0">
            <select
              value={nearMeActive ? "" : (cityFilter || "")}
              onChange={(e) => setCityFilter(e.target.value || null)}
              disabled={geoLoading}
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
              No upcoming events found{summaryText}.
            </p>
            <p className="text-muted-foreground text-sm mt-2">
              Try a different city or category, or check back soon!
            </p>
          </div>
        ) : (
          <>
            <p className="text-sm text-muted-foreground mb-4">
              {events.length}{hasMore ? "+" : ""} upcoming events{summaryText}
            </p>

            {/* Near-Me mode: split into "Nearby" and "More Events" */}
            {nearMeActive ? (
              <NearMeList events={events as EventWithDistance[]} />
            ) : (
              <div className="grid grid-cols-1 gap-4 w-full min-w-0">
                {events.map((event) => (
                  <EventCard key={event.id} event={event} />
                ))}
              </div>
            )}

            {/* Load more (normal mode only) */}
            {hasMore && !nearMeActive && (
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
  const NEARBY_THRESHOLD = 100; // miles
  const nearby = events.filter((e) => (e.distanceMiles ?? 9999) <= NEARBY_THRESHOLD);
  const farther = events.filter((e) => (e.distanceMiles ?? 9999) > NEARBY_THRESHOLD);

  return (
    <>
      {nearby.length > 0 && (
        <div className="grid grid-cols-1 gap-4 w-full min-w-0">
          {nearby.map((event) => (
            <EventCard key={event.id} event={event} distance={event.distanceMiles} />
          ))}
        </div>
      )}

      {farther.length > 0 && (
        <>
          <div className="mt-10 mb-4 flex items-center gap-3">
            <div className="h-px flex-1 bg-border" />
            <span className="text-sm text-muted-foreground font-medium whitespace-nowrap">
              More Events
            </span>
            <div className="h-px flex-1 bg-border" />
          </div>
          <div className="grid grid-cols-1 gap-4 w-full min-w-0">
            {farther.map((event) => (
              <EventCard key={event.id} event={event} distance={event.distanceMiles} />
            ))}
          </div>
        </>
      )}
    </>
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
