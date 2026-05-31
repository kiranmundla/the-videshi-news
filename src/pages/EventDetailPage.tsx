import { useEffect, useState, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Share2, Link as LinkIcon, Check, CalendarPlus } from "lucide-react";
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
/* Share Buttons                                                      */
/* ------------------------------------------------------------------ */

function ShareButtons({ title, slug }: { title: string; slug: string }) {
  const [copied, setCopied] = useState(false);
  const shareUrl = `https://thevideshi.com/events/${slug}`;
  const shareText = `${title} — The Videshi`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback
      const ta = document.createElement("textarea");
      ta.value = shareUrl;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const btnClass =
    "inline-flex items-center gap-2 px-4 py-2.5 rounded-full text-sm font-medium transition-all";

  return (
    <div className="flex flex-wrap items-center gap-3 mt-6">
      <span className="text-xs text-white/30 uppercase tracking-widest font-bold mr-1">Share</span>

      {/* WhatsApp */}
      <a
        href={`https://api.whatsapp.com/send?text=${encodeURIComponent(shareText + "\n" + shareUrl)}`}
        target="_blank"
        rel="noopener noreferrer"
        className={`${btnClass} bg-[#25D366]/15 text-[#25D366] hover:bg-[#25D366]/25 border border-[#25D366]/20`}
      >
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
        </svg>
        WhatsApp
      </a>

      {/* X / Twitter */}
      <a
        href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`}
        target="_blank"
        rel="noopener noreferrer"
        className={`${btnClass} bg-white/5 text-white/60 hover:bg-white/10 hover:text-white/80 border border-white/10`}
      >
        <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
        </svg>
        Post
      </a>

      {/* Copy Link */}
      <button
        onClick={handleCopy}
        className={`${btnClass} ${
          copied
            ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20"
            : "bg-white/5 text-white/60 hover:bg-white/10 hover:text-white/80 border border-white/10"
        }`}
      >
        {copied ? (
          <>
            <Check className="w-4 h-4" />
            Copied!
          </>
        ) : (
          <>
            <LinkIcon className="w-4 h-4" />
            Copy Link
          </>
        )}
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Add to Calendar                                                    */
/* ------------------------------------------------------------------ */

function parseEventDateTime(date: string, time: string | null): Date {
  // date is "YYYY-MM-DD", time is like "5:00 PM" or "10:30 AM" or null
  const d = new Date(date + "T12:00:00");
  if (!time) return d;
  const m = time.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
  if (!m) return d;
  let hours = parseInt(m[1], 10);
  const mins = parseInt(m[2], 10);
  const ampm = m[3].toUpperCase();
  if (ampm === "PM" && hours !== 12) hours += 12;
  if (ampm === "AM" && hours === 12) hours = 0;
  d.setHours(hours, mins, 0, 0);
  return d;
}

function toGCalDate(d: Date): string {
  // YYYYMMDDTHHMMSS (local time, no Z)
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}T${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
}

function toICSDate(d: Date): string {
  // YYYYMMDDTHHMMSS
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}T${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
}

function AddToCalendar({ event, slug }: { event: EventItem; slug: string }) {
  const [open, setOpen] = useState(false);

  const location = [event.venue_name, event.city, event.state].filter(Boolean).join(", ");
  const desc = (event.description || "").slice(0, 500) + `\n\nMore: https://thevideshi.com/events/${slug}`;
  const start = parseEventDateTime(event.date, event.time);
  const end = event.end_date
    ? parseEventDateTime(event.end_date, null)
    : new Date(start.getTime() + 2 * 60 * 60 * 1000); // default 2 hours

  const hasTime = !!event.time;

  const handleGoogleCal = () => {
    let dates: string;
    if (hasTime) {
      dates = `${toGCalDate(start)}/${toGCalDate(end)}`;
    } else {
      // All-day: YYYYMMDD/YYYYMMDD (next day)
      const pad = (n: number) => n.toString().padStart(2, "0");
      const startDay = `${start.getFullYear()}${pad(start.getMonth() + 1)}${pad(start.getDate())}`;
      const nextDay = new Date(start.getTime() + 86400000);
      const endDay = `${nextDay.getFullYear()}${pad(nextDay.getMonth() + 1)}${pad(nextDay.getDate())}`;
      dates = `${startDay}/${endDay}`;
    }
    const url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(event.title)}&dates=${dates}&location=${encodeURIComponent(location)}&details=${encodeURIComponent(desc)}`;
    window.open(url, "_blank");
    setOpen(false);
  };

  const handleICS = () => {
    const ics = [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//The Videshi//Events//EN",
      "BEGIN:VEVENT",
      `DTSTART:${toICSDate(start)}`,
      `DTEND:${toICSDate(end)}`,
      `SUMMARY:${event.title.replace(/[,;\\]/g, " ")}`,
      `LOCATION:${location.replace(/[,;\\]/g, " ")}`,
      `DESCRIPTION:${desc.replace(/\n/g, "\\n").replace(/[,;\\]/g, " ")}`,
      `URL:https://thevideshi.com/events/${slug}`,
      "END:VEVENT",
      "END:VCALENDAR",
    ].join("\r\n");

    const blob = new Blob([ics], { type: "text/calendar;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${slug}.ics`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setOpen(false);
  };

  const btnClass =
    "inline-flex items-center gap-2 px-4 py-2.5 rounded-full text-sm font-medium transition-all";

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setOpen(!open)}
        className={`${btnClass} bg-amber-500/15 text-amber-400 hover:bg-amber-500/25 border border-amber-500/20`}
      >
        <CalendarPlus className="w-4 h-4" />
        Add to Calendar
      </button>

      {open && (
        <>
          {/* backdrop */}
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          {/* dropdown */}
          <div className="absolute left-0 bottom-full mb-2 z-50 bg-[#1a1a1a] border border-white/10 rounded-xl shadow-xl overflow-hidden min-w-[200px]">
            <button
              onClick={handleGoogleCal}
              className="w-full px-4 py-3 text-left text-sm text-white/80 hover:bg-white/5 flex items-center gap-3 transition-colors"
            >
              <svg className="w-4 h-4 text-blue-400 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="18" rx="2" />
                <path d="M16 2v4M8 2v4M3 10h18" />
              </svg>
              Google Calendar
            </button>
            <div className="h-px bg-white/5" />
            <button
              onClick={handleICS}
              className="w-full px-4 py-3 text-left text-sm text-white/80 hover:bg-white/5 flex items-center gap-3 transition-colors"
            >
              <svg className="w-4 h-4 text-gray-400 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
              </svg>
              Download .ics
            </button>
          </div>
        </>
      )}
    </div>
  );
}
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
        // Use venue_images from DB first, fall back to static JSON map
        const dbImages = Array.isArray(data.venue_images) ? data.venue_images.filter(Boolean) : [];
        if (dbImages.length > 0) {
          setVenueImages(dbImages);
          setVenueAttribution("Google");
        } else if (data.venue_name) {
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
        <meta property="og:url" content={`https://www.thevideshi.com/events/${slug}`} />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={event.title} />
        <meta name="twitter:description" content={metaDescription} />
        {event.image_url && <meta name="twitter:image" content={event.image_url} />}
        <link rel="canonical" href={`https://www.thevideshi.com/events/${slug}`} />
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Event",
            name: event.title,
            ...(event.date ? { startDate: event.date } : {}),
            ...(event.end_date ? { endDate: event.end_date } : {}),
            ...(event.description ? { description: event.description.slice(0, 300) } : {}),
            ...(event.image_url ? { image: event.image_url } : {}),
            ...(event.ticket_url ? { url: event.ticket_url } : {}),
            location: {
              "@type": "Place",
              name: event.venue_name || "",
              address: {
                "@type": "PostalAddress",
                addressLocality: event.city || "",
                addressRegion: event.state || "",
              },
            },
            ...(event.organizer ? { organizer: { "@type": "Organization", name: event.organizer } } : {}),
          })}
        </script>
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

            {/* Share & Calendar buttons */}
            <div className="flex flex-wrap items-start gap-3">
              <ShareButtons title={event.title} slug={event.slug || slug!} />
              <div className="mt-6">
                <AddToCalendar event={event} slug={event.slug || slug!} />
              </div>
            </div>
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
                    {event.seatmap_url && (
                      <div className="mt-4">
                        <p className="text-white/40 text-xs font-semibold uppercase tracking-wider mb-2">Seating Chart</p>
                        <a
                          href={event.seatmap_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block cursor-zoom-in"
                        >
                          <img
                            src={event.seatmap_url}
                            alt={`Seating chart for ${event.venue_name || "venue"}`}
                            className="w-full rounded-lg bg-white"
                            loading="lazy"
                          />
                        </a>
                        <p className="text-white/30 text-xs mt-2 text-center">
                          Tap to view full size · via Ticketmaster
                        </p>
                      </div>
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

            {/* Edit link — only for user-submitted events */}
            {event.source === "user_submitted" && (
              <Link
                to={`/events/${event.slug || slug}/edit`}
                className="inline-flex items-center gap-2 ml-6 text-sm text-white/40 hover:text-white/70 transition-colors"
              >
                ✏️ Edit This Event
              </Link>
            )}
          </div>
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}
