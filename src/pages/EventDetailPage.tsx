import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  EventItem,
  getEventBySlug,
  formatEventDateLong,
  CITY_GROUPS,
} from "@/lib/events";

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

const CAT_COLORS: Record<string, string> = {
  Cultural:    "bg-purple-600/20 text-purple-300 border-purple-600/30",
  Music:       "bg-pink-600/20 text-pink-300 border-pink-600/30",
  Food:        "bg-amber-600/20 text-amber-300 border-amber-600/30",
  Sports:      "bg-green-600/20 text-green-300 border-green-600/30",
  Community:   "bg-blue-600/20 text-blue-300 border-blue-600/30",
  Festival:    "bg-orange-600/20 text-orange-300 border-orange-600/30",
  Comedy:      "bg-yellow-600/20 text-yellow-300 border-yellow-600/30",
  Dance:       "bg-rose-600/20 text-rose-300 border-rose-600/30",
  Religious:   "bg-indigo-600/20 text-indigo-300 border-indigo-600/30",
  Education:   "bg-teal-600/20 text-teal-300 border-teal-600/30",
  Competition: "bg-cyan-600/20 text-cyan-300 border-cyan-600/30",
  Other:       "bg-gray-600/20 text-gray-300 border-gray-600/30",
};

const CAT_EMOJI: Record<string, string> = {
  Cultural: "🎭", Music: "🎵", Food: "🍛", Sports: "🏏",
  Community: "🤝", Festival: "🪔", Comedy: "😂", Dance: "💃",
  Religious: "🙏", Education: "🎓", Competition: "🏆", Other: "📌",
};

function getCityGroup(city: string): string | null {
  for (const g of CITY_GROUPS) {
    if (g.cities.includes(city)) return g.label;
  }
  return null;
}

function getCtaText(priceRange: string | null): string {
  if (!priceRange) return "Get Tickets →";
  const lower = priceRange.toLowerCase();
  if (lower === "free" || lower.includes("free")) return "RSVP →";
  if (lower.includes("register")) return "Register →";
  return "Get Tickets →";
}

function isPastEvent(dateStr: string): boolean {
  const eventDate = new Date(dateStr + "T23:59:59");
  return eventDate < new Date();
}

/* ------------------------------------------------------------------ */
/* Event Detail Page                                                  */
/* ------------------------------------------------------------------ */
export default function EventDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [event, setEvent] = useState<EventItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!slug) {
      setNotFound(true);
      setLoading(false);
      return;
    }
    setLoading(true);
    getEventBySlug(slug).then((data) => {
      if (data) {
        setEvent(data);
      } else {
        setNotFound(true);
      }
      setLoading(false);
    });
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <CategoryPills />
        <main className="container flex-1 pt-8 pb-16">
          <div className="max-w-3xl mx-auto space-y-6">
            <div className="h-64 md:h-96 rounded-xl bg-muted/20 animate-pulse" />
            <div className="h-8 w-2/3 bg-muted/20 animate-pulse rounded" />
            <div className="h-4 w-1/2 bg-muted/20 animate-pulse rounded" />
            <div className="h-32 bg-muted/20 animate-pulse rounded" />
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  if (notFound || !event) {
    return (
      <div className="min-h-screen flex flex-col">
        <Helmet>
          <title>Event Not Found — The Videshi</title>
        </Helmet>
        <Masthead />
        <CategoryPills />
        <main className="container flex-1 pt-16 pb-16 text-center">
          <p className="text-6xl mb-6">🎪</p>
          <h1 className="font-serif text-3xl text-foreground mb-4">Event Not Found</h1>
          <p className="text-muted-foreground mb-8">
            This event may have passed or the link might be incorrect.
          </p>
          <Link
            to="/events"
            className="inline-block px-6 py-3 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
          >
            ← Browse All Events
          </Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  const dateStr = formatEventDateLong(event.date, event.end_date);
  const location = [event.venue_name, event.city, event.state].filter(Boolean).join(", ");
  const cityGroup = getCityGroup(event.city);
  const past = isPastEvent(event.date);
  const catColor = CAT_COLORS[event.category || "Other"] || CAT_COLORS.Other;
  const catEmoji = CAT_EMOJI[event.category || "Other"] || "📌";
  const description = event.long_description || event.description;
  const metaDescription = event.description
    ? `${event.description.slice(0, 155)}…`
    : `${event.title} on ${dateStr} at ${location}`;

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>{event.title} — Events — The Videshi</title>
        <meta name="description" content={metaDescription} />
        <meta property="og:title" content={event.title} />
        <meta property="og:description" content={metaDescription} />
        {event.image_url && <meta property="og:image" content={event.image_url} />}
        <meta property="og:type" content="website" />
        <link rel="canonical" href={`/events/${slug}`} />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="flex-1">
        {/* Hero */}
        <div className="relative w-full">
          {event.image_url ? (
            <div className="relative w-full h-64 sm:h-80 md:h-[28rem] overflow-hidden bg-muted/10">
              <img
                src={event.image_url}
                alt={event.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-transparent" />
              {/* Title overlay */}
              <div className="absolute bottom-0 left-0 right-0 p-6 md:p-10">
                <div className="max-w-3xl mx-auto">
                  {past && (
                    <span className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-red-600/80 text-white mb-3">
                      PAST EVENT
                    </span>
                  )}
                  <h1 className="font-serif text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-white font-bold leading-tight drop-shadow-lg">
                    {event.title}
                  </h1>
                  <div className="flex flex-wrap items-center gap-3 mt-3 text-white/90">
                    <span className="font-semibold">📅 {dateStr}</span>
                    {event.time && <span>· {event.time}</span>}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="relative w-full h-48 sm:h-56 bg-gradient-to-br from-muted/30 to-muted/10 flex items-end">
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-8xl opacity-20">
                {catEmoji}
              </div>
              <div className="p-6 md:p-10 w-full">
                <div className="max-w-3xl mx-auto">
                  {past && (
                    <span className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-red-600/80 text-white mb-3">
                      PAST EVENT
                    </span>
                  )}
                  <h1 className="font-serif text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-foreground font-bold leading-tight">
                    {event.title}
                  </h1>
                  <div className="flex flex-wrap items-center gap-3 mt-3 text-muted-foreground">
                    <span className="font-semibold text-primary">📅 {dateStr}</span>
                    {event.time && <span>· {event.time}</span>}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="container pb-16">
          <div className="max-w-3xl mx-auto">
            {/* Info pills */}
            <div className="flex flex-wrap gap-2 mt-6 mb-8">
              {event.category && (
                <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border ${catColor}`}>
                  {catEmoji} {event.category}
                </span>
              )}
              {location && (
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-muted/30 text-muted-foreground border border-border">
                  📍 {location}
                </span>
              )}
              {cityGroup && (
                <Link
                  to={`/events?city=${encodeURIComponent(cityGroup)}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-muted/30 text-muted-foreground border border-border hover:border-primary/40 transition-colors"
                >
                  🏙️ {cityGroup} Events
                </Link>
              )}
              {event.price_range && (
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-emerald-600/20 text-emerald-300 border border-emerald-600/30">
                  💰 {event.price_range}
                </span>
              )}
              {event.audience && (
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-sky-600/20 text-sky-300 border border-sky-600/30">
                  👤 {event.audience}
                </span>
              )}
            </div>

            {/* CTA Button — primary position */}
            {event.ticket_url && !past && (
              <a
                href={event.ticket_url}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full sm:w-auto sm:inline-block text-center px-8 py-4 rounded-xl bg-primary text-primary-foreground font-bold text-lg hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20 mb-10"
              >
                {getCtaText(event.price_range)}
              </a>
            )}
            {past && (
              <div className="mb-10 p-4 rounded-lg bg-red-900/20 border border-red-600/30 text-red-300 text-sm">
                ⚠️ This event has already taken place. Check our <Link to="/events" className="underline hover:text-red-200">events page</Link> for upcoming events.
              </div>
            )}

            {/* About This Event */}
            {description && (
              <section className="mb-10">
                <h2 className="font-serif text-xl md:text-2xl text-foreground mb-4 flex items-center gap-2">
                  <span className="text-primary">◆</span> About This Event
                </h2>
                <div className="prose prose-invert max-w-none text-muted-foreground leading-relaxed whitespace-pre-line">
                  {description}
                </div>
              </section>
            )}

            {/* About the Artist */}
            {event.artist_info && (
              <section className="mb-10">
                <h2 className="font-serif text-xl md:text-2xl text-foreground mb-4 flex items-center gap-2">
                  <span className="text-primary">◆</span> About the Artist
                </h2>
                <div className="prose prose-invert max-w-none text-muted-foreground leading-relaxed whitespace-pre-line">
                  {event.artist_info}
                </div>
              </section>
            )}

            {/* Venue */}
            <section className="mb-10">
              <h2 className="font-serif text-xl md:text-2xl text-foreground mb-4 flex items-center gap-2">
                <span className="text-primary">◆</span> Venue
              </h2>
              <div className="p-5 rounded-lg bg-muted/10 border border-border">
                {event.venue_name && (
                  <p className="text-foreground font-semibold text-lg mb-1">{event.venue_name}</p>
                )}
                <p className="text-muted-foreground">
                  {[event.city, event.state].filter(Boolean).join(", ")}
                </p>
                {event.venue_info && (
                  <p className="text-muted-foreground mt-3 text-sm leading-relaxed whitespace-pre-line">
                    {event.venue_info}
                  </p>
                )}
              </div>
            </section>

            {/* Event details summary */}
            <section className="mb-10">
              <h2 className="font-serif text-xl md:text-2xl text-foreground mb-4 flex items-center gap-2">
                <span className="text-primary">◆</span> Event Details
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-muted/10 border border-border">
                  <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Date</p>
                  <p className="text-foreground font-medium">{dateStr}</p>
                </div>
                {event.time && (
                  <div className="p-4 rounded-lg bg-muted/10 border border-border">
                    <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Time</p>
                    <p className="text-foreground font-medium">{event.time}</p>
                  </div>
                )}
                {event.price_range && (
                  <div className="p-4 rounded-lg bg-muted/10 border border-border">
                    <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Price</p>
                    <p className="text-foreground font-medium">{event.price_range}</p>
                  </div>
                )}
                {event.organizer && (
                  <div className="p-4 rounded-lg bg-muted/10 border border-border">
                    <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Organizer</p>
                    <p className="text-foreground font-medium">{event.organizer}</p>
                  </div>
                )}
              </div>
            </section>

            {/* Bottom CTA */}
            {event.ticket_url && !past && (
              <div className="text-center py-8 border-t border-border">
                <p className="text-muted-foreground mb-4">Ready to go?</p>
                <a
                  href={event.ticket_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block px-10 py-4 rounded-xl bg-primary text-primary-foreground font-bold text-lg hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20"
                >
                  {getCtaText(event.price_range)}
                </a>
              </div>
            )}

            {/* Attribution */}
            <div className="mt-10 pt-6 border-t border-border">
              <p className="text-xs text-muted-foreground/60">
                Event sourced from {event.source || "web search"}. All event details are subject to change — please verify with the organizer before attending.
              </p>
            </div>

            {/* Back to events */}
            <div className="mt-6">
              <Link
                to="/events"
                className="text-sm text-primary hover:text-primary/80 transition-colors"
              >
                ← Back to all events
              </Link>
            </div>
          </div>
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}
