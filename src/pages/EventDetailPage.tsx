import { useEffect, useState, useRef } from "react";
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
/* Venue Images                                                        */
/* ------------------------------------------------------------------ */

type VenueImageEntry = { city: string; images: string[]; attribution: string };
type VenueImageMap = Record<string, VenueImageEntry>;

const VENUE_IMAGES_URL =
  "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/venues/venue-images.json";

let cachedVenueImages: VenueImageMap | null = null;

async function fetchVenueImages(): Promise<VenueImageMap> {
  if (cachedVenueImages) return cachedVenueImages;
  try {
    const res = await fetch(VENUE_IMAGES_URL);
    if (!res.ok) return {};
    cachedVenueImages = await res.json();
    return cachedVenueImages!;
  } catch {
    return {};
  }
}

function VenuePhotoGallery({ images, venueName, attribution }: {
  images: string[];
  venueName: string;
  attribution: string;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);

  if (!images.length) return null;

  return (
    <div className="mt-5">
      <div
        ref={scrollRef}
        className="flex gap-3 overflow-x-auto pb-3 scrollbar-none snap-x snap-mandatory"
      >
        {images.map((url, i) => (
          <div
            key={i}
            className="flex-shrink-0 snap-start w-[85%] sm:w-[45%] lg:w-[30%] rounded-lg overflow-hidden"
          >
            <img
              src={url}
              alt={`${venueName} — photo ${i + 1}`}
              className="w-full h-44 sm:h-52 object-cover bg-white/5"
              loading="lazy"
            />
          </div>
        ))}
      </div>
      <p className="text-[10px] text-white/20 mt-2">
        Photo of {venueName} · {attribution}
      </p>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

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
  if (!priceRange) return "Get Tickets";
  const lower = priceRange.toLowerCase();
  if (lower === "free" || lower.includes("free")) return "RSVP Now";
  if (lower.includes("register")) return "Register Now";
  return "Get Tickets";
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
  const [venueImages, setVenueImages] = useState<string[]>([]);
  const [venueAttribution, setVenueAttribution] = useState("");

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
        // Fetch venue images
        if (data.venue_name) {
          fetchVenueImages().then((map) => {
            const entry = map[data.venue_name!];
            if (entry && entry.images.length) {
              setVenueImages(entry.images);
              setVenueAttribution(entry.attribution || "");
            }
          });
        }
      } else {
        setNotFound(true);
      }
      setLoading(false);
    });
  }, [slug]);

  /* Loading */
  if (loading) {
    return (
      <div className="min-h-screen flex flex-col bg-[#0a0a0a]">
        <Masthead />
        <CategoryPills />
        <main className="flex-1 pt-8 pb-16 px-4">
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="h-[70vh] rounded-2xl bg-white/5 animate-pulse" />
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  /* Not found */
  if (notFound || !event) {
    return (
      <div className="min-h-screen flex flex-col bg-[#0a0a0a]">
        <Helmet><title>Event Not Found — The Videshi</title></Helmet>
        <Masthead />
        <CategoryPills />
        <main className="flex-1 pt-16 pb-16 text-center px-4">
          <p className="text-6xl mb-6">🎪</p>
          <h1 className="font-serif text-3xl text-white mb-4">Event Not Found</h1>
          <p className="text-white/50 mb-8">This event may have passed or the link might be incorrect.</p>
          <Link to="/events" className="inline-block px-6 py-3 rounded-full bg-white text-black font-semibold hover:bg-white/90 transition-colors">
            ← Browse All Events
          </Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  const dateStr = formatEventDateLong(event.date, event.end_date);
  const past = isPastEvent(event.date);
  const catEmoji = CAT_EMOJI[event.category || "Other"] || "📌";
  const description = event.long_description || event.description;
  const metaDescription = event.description
    ? `${event.description.slice(0, 155)}…`
    : `${event.title} on ${dateStr} at ${event.venue_name}, ${event.city}`;

  return (
    <div className="min-h-screen flex flex-col bg-[#0a0a0a]">
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

        {/* ========== HERO ========== */}
        {event.image_url ? (
          <div className="relative w-full">
            {/* Full poster — no heavy gradient, just a subtle bottom fade */}
            <div className="relative w-full max-h-[75vh] overflow-hidden">
              <img
                src={event.image_url}
                alt={event.title}
                className="w-full h-full object-contain bg-black"
                style={{ maxHeight: "75vh" }}
              />
              {/* Very subtle bottom edge fade only */}
              <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-[#0a0a0a] to-transparent" />
            </div>
          </div>
        ) : (
          /* No-image hero — big emoji + color wash */
          <div className="relative w-full h-48 sm:h-56 bg-gradient-to-br from-white/5 to-transparent flex items-center justify-center">
            <span className="text-[8rem] opacity-15 select-none">{catEmoji}</span>
          </div>
        )}

        {/* ========== TITLE CARD ========== */}
        <div className="px-4 -mt-6 relative z-10">
          <div className="max-w-4xl mx-auto">

            {past && (
              <span className="inline-block px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider bg-red-500/20 text-red-400 border border-red-500/30 mb-4">
                Past Event
              </span>
            )}

            {/* Category + Date row */}
            <div className="flex flex-wrap items-center gap-3 mb-4">
              {event.category && (
                <span className="text-sm font-medium text-white/40 uppercase tracking-widest">
                  {catEmoji} {event.category}
                </span>
              )}
              <span className="text-sm text-white/30">•</span>
              <span className="text-sm text-white/60">{dateStr}</span>
              {event.time && (
                <>
                  <span className="text-sm text-white/30">•</span>
                  <span className="text-sm text-white/60">{event.time}</span>
                </>
              )}
            </div>

            {/* Title */}
            <h1 className="font-serif text-3xl sm:text-4xl md:text-5xl text-white font-bold leading-[1.1] mb-4">
              {event.title}
            </h1>

            {/* Venue + City */}
            <div className="flex flex-wrap items-center gap-2 text-white/50 text-base mb-8">
              {event.venue_name && <span className="text-white/70 font-medium">{event.venue_name}</span>}
              {event.venue_name && event.city && <span>·</span>}
              <span>{[event.city, event.state].filter(Boolean).join(", ")}</span>
              {event.price_range && (
                <>
                  <span>·</span>
                  <span className="text-emerald-400 font-medium">{event.price_range}</span>
                </>
              )}
            </div>

            {/* CTA */}
            {event.ticket_url && !past && (
              <a
                href={event.ticket_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-white text-black font-bold text-base hover:bg-white/90 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[0_0_30px_rgba(255,255,255,0.1)]"
              >
                {getCtaText(event.price_range)}
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" />
                </svg>
              </a>
            )}
            {past && (
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400/80 text-sm">
                This event has already taken place. <Link to="/events" className="underline hover:text-red-300">Browse upcoming events →</Link>
              </div>
            )}
          </div>
        </div>

        {/* ========== DIVIDER ========== */}
        <div className="max-w-4xl mx-auto px-4 my-12">
          <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        </div>

        {/* ========== CONTENT SECTIONS ========== */}
        <div className="px-4 pb-20">
          <div className="max-w-4xl mx-auto grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-10">

            {/* LEFT: Main content */}
            <div className="space-y-10">

              {/* About This Event */}
              {description && (
                <section>
                  <h2 className="text-xs font-bold uppercase tracking-[0.2em] text-white/30 mb-5">
                    About This Event
                  </h2>
                  <div className="text-white/70 text-[15px] leading-[1.85] whitespace-pre-line">
                    {description}
                  </div>
                </section>
              )}

              {/* About the Artist */}
              {event.artist_info && (
                <section>
                  <h2 className="text-xs font-bold uppercase tracking-[0.2em] text-white/30 mb-5">
                    About the Artist
                  </h2>
                  <div className="text-white/70 text-[15px] leading-[1.85] whitespace-pre-line">
                    {event.artist_info}
                  </div>
                </section>
              )}

              {/* Venue */}
              {(event.venue_name || event.venue_info) && (
                <section>
                  <h2 className="text-xs font-bold uppercase tracking-[0.2em] text-white/30 mb-5">
                    Venue
                  </h2>
                  <div className="rounded-xl bg-white/[0.03] border border-white/[0.06] p-6">
                    {event.venue_name && (
                      <p className="text-white font-semibold text-lg mb-1">{event.venue_name}</p>
                    )}
                    <p className="text-white/40 text-sm mb-4">
                      {[event.city, event.state].filter(Boolean).join(", ")}
                    </p>
                    {event.venue_info && (
                      <div className="text-white/60 text-sm leading-relaxed whitespace-pre-line mb-4">
                        {event.venue_info}
                      </div>
                    )}
                    {venueImages.length > 0 && (
                      <VenuePhotoGallery
                        images={venueImages}
                        venueName={event.venue_name || "Venue"}
                        attribution={venueAttribution}
                      />
                    )}
                    <a
                      href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent([event.venue_name, event.city, event.state].filter(Boolean).join(", "))}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-sm text-white/50 hover:text-white/80 transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
                      </svg>
                      Get Directions →
                    </a>
                  </div>
                </section>
              )}
            </div>

            {/* RIGHT: Sidebar */}
            <div className="space-y-6 lg:pt-0">
              {/* Quick info card */}
              <div className="rounded-xl bg-white/[0.03] border border-white/[0.06] p-5 space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-white/30">
                  Event Details
                </h3>

                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <span className="text-lg mt-0.5">📅</span>
                    <div>
                      <p className="text-white/80 text-sm font-medium">{dateStr}</p>
                      {event.time && <p className="text-white/40 text-xs">{event.time}</p>}
                    </div>
                  </div>

                  {event.price_range && (
                    <div className="flex items-start gap-3">
                      <span className="text-lg mt-0.5">💰</span>
                      <div>
                        <p className="text-white/80 text-sm font-medium">{event.price_range}</p>
                      </div>
                    </div>
                  )}

                  {event.organizer && (
                    <div className="flex items-start gap-3">
                      <span className="text-lg mt-0.5">🎤</span>
                      <div>
                        <p className="text-white/80 text-sm font-medium">{event.organizer}</p>
                        <p className="text-white/40 text-xs">Organizer</p>
                      </div>
                    </div>
                  )}

                  {event.audience && (
                    <div className="flex items-start gap-3">
                      <span className="text-lg mt-0.5">👥</span>
                      <div>
                        <p className="text-white/80 text-sm font-medium">{event.audience}</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Sidebar CTA */}
                {event.ticket_url && !past && (
                  <a
                    href={event.ticket_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-2 w-full mt-4 px-6 py-3 rounded-full bg-white text-black font-bold text-sm hover:bg-white/90 transition-colors"
                  >
                    {getCtaText(event.price_range)}
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" />
                    </svg>
                  </a>
                )}
              </div>

              {/* City group link */}
              {getCityGroup(event.city) && (
                <Link
                  to={`/events?city=${encodeURIComponent(getCityGroup(event.city)!)}`}
                  className="flex items-center gap-3 p-4 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:border-white/10 transition-colors group"
                >
                  <span className="text-lg">🏙️</span>
                  <div>
                    <p className="text-white/70 text-sm font-medium group-hover:text-white transition-colors">
                      More events in {getCityGroup(event.city)}
                    </p>
                    <p className="text-white/30 text-xs">Browse all →</p>
                  </div>
                </Link>
              )}
            </div>
          </div>
        </div>

        {/* ========== FOOTER AREA ========== */}
        <div className="px-4 pb-16">
          <div className="max-w-4xl mx-auto">
            <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-8" />

            {/* Attribution */}
            <p className="text-[11px] text-white/20 mb-6">
              Event sourced from {event.source || "web search"}. Details may change — verify with the organizer before attending.
            </p>

            {/* Back link */}
            <Link
              to="/events"
              className="inline-flex items-center gap-2 text-sm text-white/40 hover:text-white/70 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 12H5m0 0l7 7m-7-7l7-7" />
              </svg>
              All Events
            </Link>
          </div>
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}
