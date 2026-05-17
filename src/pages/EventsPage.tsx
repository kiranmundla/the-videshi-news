import { useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  EventItem,
  getEvents,
  formatEventDate,
  generateSlug,
  CITY_GROUPS,
  EVENT_CATEGORIES,
} from "@/lib/events";

/* ------------------------------------------------------------------ */
/* Category badge color helper                                        */
/* ------------------------------------------------------------------ */
const CAT_COLORS: Record<string, string> = {
  Cultural:    "bg-purple-600/20 text-purple-300",
  Music:       "bg-pink-600/20 text-pink-300",
  Food:        "bg-amber-600/20 text-amber-300",
  Sports:      "bg-green-600/20 text-green-300",
  Community:   "bg-blue-600/20 text-blue-300",
  Festival:    "bg-orange-600/20 text-orange-300",
  Comedy:      "bg-yellow-600/20 text-yellow-300",
  Dance:       "bg-rose-600/20 text-rose-300",
  Religious:   "bg-indigo-600/20 text-indigo-300",
  Education:   "bg-teal-600/20 text-teal-300",
  Competition: "bg-cyan-600/20 text-cyan-300",
  Other:       "bg-gray-600/20 text-gray-300",
};

const CAT_EMOJI: Record<string, string> = {
  Cultural: "🎭",
  Music: "🎵",
  Food: "🍛",
  Sports: "🏏",
  Community: "🤝",
  Festival: "🪔",
  Comedy: "😂",
  Dance: "💃",
  Religious: "🙏",
  Education: "🎓",
  Competition: "🏆",
  Other: "📌",
};

function categoryEmoji(category: string | null): string {
  switch (category) {
    case "Music": return "🎵";
    case "Dance": return "💃";
    case "Food": return "🍛";
    case "Sports": return "🏏";
    case "Comedy": return "😂";
    case "Festival": return "🪔";
    case "Religious": return "🛕";
    case "Education": return "🎓";
    case "Competition": return "🏆";
    case "Community": return "🤝";
    case "Cultural": return "🎭";
    default: return "🎪";
  }
}

function CategoryBadge({ category }: { category: string | null }) {
  if (!category) return null;
  const color = CAT_COLORS[category] || CAT_COLORS.Other;
  const emoji = CAT_EMOJI[category] || "";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${color}`}>
      {emoji && <span className="mr-1">{emoji}</span>}{category}
    </span>
  );
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
        <div className="w-full sm:w-56 sm:min-w-[14rem] h-48 sm:h-auto overflow-hidden flex-shrink-0">
          <img
            src={event.image_url}
            alt={event.title}
            className="w-full h-full object-cover bg-muted/10 group-hover:scale-105 transition-transform duration-300"
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
            <CategoryBadge category={event.category} />
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
/* Filter Pills                                                       */
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
/* Events Page                                                        */
/* ------------------------------------------------------------------ */
export default function EventsPage() {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [cityFilter, setCityFilter] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

  const PAGE_SIZE = 30;

  useEffect(() => {
    setLoading(true);
    setHasMore(true);
    getEvents(cityFilter, categoryFilter, PAGE_SIZE, 0).then((data) => {
      setEvents(data);
      setHasMore(data.length === PAGE_SIZE);
      setLoading(false);
    });
  }, [cityFilter, categoryFilter]);

  const loadMore = async () => {
    if (loadingMore || !hasMore) return;
    setLoadingMore(true);
    const next = await getEvents(cityFilter, categoryFilter, PAGE_SIZE, events.length);
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
        <div className="mb-8">
          <h1 className="font-serif text-3xl md:text-5xl text-foreground mb-3">
            Events
          </h1>
          <p className="text-muted-foreground text-lg">
            Indian concerts, festivals, cultural events &amp; community gatherings across the US
          </p>
        </div>

        {/* Filters */}
        <div className="space-y-4 mb-8">
          <div>
            <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-2 font-medium">
              City
            </h3>
            <FilterPills
              options={CITY_GROUPS.map((g) => g.label)}
              selected={cityFilter}
              onSelect={setCityFilter}
              allLabel="All Cities"
            />
          </div>
          <div>
            <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-2 font-medium">
              Category
            </h3>
            <FilterPills
              options={EVENT_CATEGORIES}
              selected={categoryFilter}
              onSelect={setCategoryFilter}
            />
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
              No upcoming events found
              {cityFilter ? ` in ${cityFilter}` : ""}
              {categoryFilter ? ` for ${categoryFilter}` : ""}
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
              {categoryFilter ? ` · ${categoryFilter}` : ""}
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
