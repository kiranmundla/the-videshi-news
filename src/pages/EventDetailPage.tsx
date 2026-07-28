import { useEffect, useState, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Check, CalendarPlus } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  EventItem,
  getEventBySlug,
  formatEventDateLong,
  CITY_GROUPS,
} from "@/lib/events";

/* ── Venue images (static JSON fallback) ──────────────────────────── */

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

/* ── Helpers ──────────────────────────────────────────────────────── */

const CAT_EMOJI: Record<string, string> = {
  Cultural: "🎭", Music: "🎵", Food: "🍛", Sports: "🏏",
  Community: "🤝", Festival: "🪔", Comedy: "😂", Dance: "💃",
  Religious: "🙏", Education: "🎓", Competition: "🏆",
  Spiritual: "🙏", Shopping: "🛍️", Entertainment: "🎬",
  Technology: "💻", Other: "📌",
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
  if (lower === "free" || lower.includes("free")) return "RSVP Free";
  if (lower.includes("register")) return "Register Now";
  return "Get Tickets";
}

function buildOffers(event: EventItem): Record<string, unknown> | null {
  const raw = (event.price_range || "").trim();
  const lower = raw.toLowerCase();
  const validFromSrc = event.created_at || event.date || null;
  let validFrom: string | undefined;
  if (validFromSrc) {
    const d = new Date(validFromSrc);
    if (!isNaN(d.getTime())) validFrom = d.toISOString();
  }
  const url = event.ticket_url || (event.slug ? `https://www.thevideshi.com/events/${event.slug}` : undefined);
  const base = {
    "@type": "Offer",
    priceCurrency: "USD",
    availability: "https://schema.org/InStock",
    ...(validFrom ? { validFrom } : {}),
    ...(url ? { url } : {}),
  };
  if (lower && (lower === "free" || lower.startsWith("free"))) return { ...base, price: "0" };
  if (!raw || ["tbd", "varies", "none"].includes(lower)) return null;
  const match = raw.replace(/,/g, "").match(/\d+(?:\.\d+)?/);
  if (!match) return null;
  return { ...base, price: match[0] };
}

function decodeHTMLEntities(text: string): string {
  const el = document.createElement("textarea");
  el.innerHTML = text;
  return el.value;
}

function isPastEvent(dateStr: string): boolean {
  return new Date(dateStr + "T23:59:59") < new Date();
}

/** Split venue_name into name and street address if it contains a comma */
function parseVenueParts(venueName: string | null, streetAddr?: string | null): { name: string; address: string } {
  // Prefer the dedicated street_address field
  if (streetAddr) {
    return { name: venueName || "", address: streetAddr };
  }
  if (!venueName) return { name: "", address: "" };
  const idx = venueName.indexOf(",");
  if (idx < 0) return { name: venueName, address: "" };
  return { name: venueName.slice(0, idx).trim(), address: venueName.slice(idx + 1).trim() };
}

/* ── Image Gallery / Carousel ─────────────────────────────────────── */

function ImageGallery({ images, title }: { images: string[]; title: string }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [activeIdx, setActiveIdx] = useState(0);

  if (images.length === 0) return null;

  const handleScroll = () => {
    const el = scrollRef.current;
    if (!el) return;
    const idx = Math.round(el.scrollLeft / el.clientWidth);
    setActiveIdx(idx);
  };

  const scrollTo = (idx: number) => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTo({ left: idx * el.clientWidth, behavior: "smooth" });
  };

  // Single image — simple hero
  if (images.length === 1) {
    return (
      <div className="relative w-full overflow-hidden" style={{ maxHeight: "60vh" }}>
        <img src={images[0]} alt={title} className="w-full h-auto object-contain bg-black" style={{ maxHeight: "60vh" }} />
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#0f1218] to-transparent" />
      </div>
    );
  }

  // Multiple images — carousel
  return (
    <div className="relative">
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="flex overflow-x-auto snap-x snap-mandatory scrollbar-none"
        style={{ WebkitOverflowScrolling: "touch" }}
      >
        {images.map((url, i) => (
          <div key={i} className="flex-shrink-0 w-full snap-center" style={{ maxHeight: "60vh" }}>
            <img
              src={url}
              alt={`${title} — ${i + 1}`}
              className="w-full h-auto object-contain bg-black mx-auto"
              style={{ maxHeight: "60vh" }}
              loading={i === 0 ? "eager" : "lazy"}
            />
          </div>
        ))}
      </div>
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#0f1218] to-transparent pointer-events-none" />

      {/* Dots */}
      {images.length > 1 && images.length <= 8 && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-1.5 z-10">
          {images.map((_, i) => (
            <button
              key={i}
              onClick={() => scrollTo(i)}
              className={`w-2 h-2 rounded-full transition-all ${i === activeIdx ? "bg-white scale-110" : "bg-white/40"}`}
            />
          ))}
        </div>
      )}

      {/* Arrows (desktop only) */}
      {images.length > 1 && (
        <>
          <button
            onClick={() => scrollTo(Math.max(0, activeIdx - 1))}
            className="hidden md:flex absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/50 backdrop-blur items-center justify-center text-white/80 hover:bg-black/70 transition-colors z-10"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" /></svg>
          </button>
          <button
            onClick={() => scrollTo(Math.min(images.length - 1, activeIdx + 1))}
            className="hidden md:flex absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/50 backdrop-blur items-center justify-center text-white/80 hover:bg-black/70 transition-colors z-10"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" /></svg>
          </button>
        </>
      )}

      {/* Counter */}
      {images.length > 1 && (
        <span className="absolute top-3 right-3 bg-black/60 backdrop-blur text-white/80 text-xs px-2.5 py-1 rounded-full z-10">
          {activeIdx + 1}/{images.length}
        </span>
      )}
    </div>
  );
}

/* ── Share Buttons ─────────────────────────────────────────────────── */

function ShareButtons({ title, slug }: { title: string; slug: string }) {
  const [copied, setCopied] = useState(false);
  const shareUrl = `https://thevideshi.com/events/${slug}`;
  const shareText = `${title} — The Videshi`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = shareUrl;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const pill = "inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full text-xs font-semibold transition-all active:scale-95";

  return (
    <div className="flex flex-wrap items-center gap-2">
      <a
        href={`https://api.whatsapp.com/send?text=${encodeURIComponent(shareText + "\n" + shareUrl)}`}
        target="_blank" rel="noopener noreferrer"
        className={`${pill} bg-[#25D366]/15 text-[#25D366] hover:bg-[#25D366]/25`}
      >
        <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" /></svg>
        WhatsApp
      </a>
      <a
        href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`}
        target="_blank" rel="noopener noreferrer"
        className={`${pill} bg-white/5 text-white/60 hover:bg-white/10 hover:text-white/80`}
      >
        <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" /></svg>
        Post
      </a>
      <button
        onClick={handleCopy}
        className={`${pill} ${copied ? "bg-emerald-500/15 text-emerald-400" : "bg-white/5 text-white/60 hover:bg-white/10 hover:text-white/80"}`}
      >
        {copied ? <><Check className="w-3.5 h-3.5" />Copied!</> : <><svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.86-2.554a4.5 4.5 0 00-1.242-7.244l-4.5-4.5a4.5 4.5 0 00-6.364 6.364L5.25 9.879" /></svg>Copy Link</>}
      </button>
    </div>
  );
}

/* ── Add to Calendar ───────────────────────────────────────────────── */

function parseEventDateTime(date: string, time: string | null): Date {
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
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}T${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
}

function toICSDate(d: Date): string {
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
    : new Date(start.getTime() + 2 * 60 * 60 * 1000);
  const hasTime = !!event.time;

  const handleGoogleCal = () => {
    let dates: string;
    if (hasTime) {
      dates = `${toGCalDate(start)}/${toGCalDate(end)}`;
    } else {
      const pad = (n: number) => n.toString().padStart(2, "0");
      const startDay = `${start.getFullYear()}${pad(start.getMonth() + 1)}${pad(start.getDate())}`;
      const nextDay = new Date(start.getTime() + 86400000);
      const endDay = `${nextDay.getFullYear()}${pad(nextDay.getMonth() + 1)}${pad(nextDay.getDate())}`;
      dates = `${startDay}/${endDay}`;
    }
    window.open(`https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(event.title)}&dates=${dates}&location=${encodeURIComponent(location)}&details=${encodeURIComponent(desc)}`, "_blank");
    setOpen(false);
  };

  const handleICS = () => {
    const ics = [
      "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//The Videshi//Events//EN", "BEGIN:VEVENT",
      `DTSTART:${toICSDate(start)}`, `DTEND:${toICSDate(end)}`,
      `SUMMARY:${event.title.replace(/[,;\\]/g, " ")}`,
      `LOCATION:${location.replace(/[,;\\]/g, " ")}`,
      `DESCRIPTION:${desc.replace(/\n/g, "\\n").replace(/[,;\\]/g, " ")}`,
      `URL:https://thevideshi.com/events/${slug}`,
      "END:VEVENT", "END:VCALENDAR",
    ].join("\r\n");
    const blob = new Blob([ics], { type: "text/calendar;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `${slug}.ics`;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a); URL.revokeObjectURL(url);
    setOpen(false);
  };

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setOpen(!open)}
        className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full text-xs font-semibold bg-[#D4A843]/15 text-[#D4A843] hover:bg-[#D4A843]/25 transition-all active:scale-95"
      >
        <CalendarPlus className="w-3.5 h-3.5" />
        Save to Calendar
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute left-0 bottom-full mb-2 z-50 bg-[#1a1e28] border border-white/10 rounded-xl shadow-2xl overflow-hidden min-w-[210px]">
            <button onClick={handleGoogleCal} className="w-full px-4 py-3 text-left text-sm text-white/80 hover:bg-white/5 flex items-center gap-3 transition-colors">
              <svg className="w-4 h-4 text-blue-400 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" /></svg>
              Google Calendar
            </button>
            <div className="h-px bg-white/5" />
            <button onClick={handleICS} className="w-full px-4 py-3 text-left text-sm text-white/80 hover:bg-white/5 flex items-center gap-3 transition-colors">
              <svg className="w-4 h-4 text-gray-400 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" /></svg>
              Download .ics
            </button>
          </div>
        </>
      )}
    </div>
  );
}

/* ── Description renderer ──────────────────────────────────────────── */

function EventDescription({ text }: { text: string }) {
  // Split into paragraphs on double newline, or treat each line as paragraph
  const paragraphs = text.split(/\n\s*\n/).filter(p => p.trim());

  if (paragraphs.length <= 1) {
    // Single block — still split on single newlines for line breaks
    const lines = text.split("\n").filter(l => l.trim());
    return (
      <div className="space-y-3">
        {lines.map((line, i) => (
          <p key={i} className="text-white/75 text-[15.5px] leading-[1.8]">
            {line.trim()}
          </p>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {paragraphs.map((para, i) => (
        <p key={i} className="text-white/75 text-[15.5px] leading-[1.8]">
          {para.trim()}
        </p>
      ))}
    </div>
  );
}

/* ================================================================== */
/* Main Page                                                          */
/* ================================================================== */

export default function EventDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [event, setEvent] = useState<EventItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [allImages, setAllImages] = useState<string[]>([]);

  useEffect(() => {
    if (!slug) { setNotFound(true); setLoading(false); return; }
    setLoading(true);
    getEventBySlug(slug).then(async (data) => {
      if (!data) { setNotFound(true); setLoading(false); return; }
      setEvent(data);

      // Gather all available images: hero + venue_images from DB + static JSON
      const imgs: string[] = [];
      if (data.image_url) imgs.push(data.image_url);

      const dbImages = Array.isArray(data.venue_images) ? data.venue_images.filter(Boolean) : [];
      for (const img of dbImages) {
        if (!imgs.includes(img)) imgs.push(img);
      }

      if (imgs.length <= 1 && data.venue_name) {
        const map = await fetchVenueImages();
        const entry = map[data.venue_name];
        if (entry?.images) {
          for (const img of entry.images) {
            if (!imgs.includes(img)) imgs.push(img);
          }
        }
      }

      setAllImages(imgs);
      setLoading(false);
    });
  }, [slug]);

  /* Loading skeleton */
  if (loading) {
    return (
      <div className="min-h-screen flex flex-col" style={{ background: "linear-gradient(180deg, #0f1218 0%, #0a0a0a 30%)" }}>
        <Masthead /><CategoryPills />
        <main className="flex-1 pt-8 pb-16 px-4">
          <div className="max-w-3xl mx-auto space-y-5">
            <div className="h-[50vh] rounded-2xl bg-white/5 animate-pulse" />
            <div className="h-8 w-2/3 rounded bg-white/5 animate-pulse" />
            <div className="h-4 w-1/3 rounded bg-white/5 animate-pulse" />
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  /* Not found */
  if (notFound || !event) {
    return (
      <div className="min-h-screen flex flex-col" style={{ background: "linear-gradient(180deg, #0f1218 0%, #0a0a0a 30%)" }}>
        <Helmet><title>Event Not Found — The Videshi</title></Helmet>
        <Masthead /><CategoryPills />
        <main className="flex-1 pt-16 pb-16 text-center px-4">
          <p className="text-6xl mb-6">🎪</p>
          <h1 className="font-serif text-3xl text-white mb-4">Event Not Found</h1>
          <p className="text-white/50 mb-8">This event may have passed or the link might be incorrect.</p>
          <Link to="/events" className="inline-block px-6 py-3 rounded-full bg-white text-black font-semibold hover:bg-white/90 transition-colors">← Browse All Events</Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  const dateStr = formatEventDateLong(event.date, event.end_date);
  const past = isPastEvent(event.date);
  const catEmoji = CAT_EMOJI[event.category || "Other"] || "📌";
  const { name: venueName, address: venueStreet } = parseVenueParts(event.venue_name, event.street_address);
  const venueZip = event.zip_code || "";
  const fullLocation = [venueName, event.city, event.state].filter(Boolean).join(", ");
  const mapsQuery = [event.venue_name, event.city, event.state].filter(Boolean).join(", ");

  const rawDescription = event.long_description || event.description;
  const description = rawDescription
    ? rawDescription.replace(/\s*(Read below:?|Read more:?)\s*$/i, "").trim() || rawDescription
    : null;
  const hasLongDesc = !!description && description.length > 100;
  const metaDescription = event.description
    ? `${event.description.slice(0, 155)}…`
    : `${event.title} on ${dateStr} at ${venueName}, ${event.city}`;

  const priceIsFree = event.price_range?.toLowerCase().includes("free");

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "linear-gradient(180deg, #0f1218 0%, #0a0a0a 30%)" }}>
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
            "@context": "https://schema.org", "@type": "Event",
            name: event.title,
            ...(event.date ? { startDate: event.date } : {}),
            ...(event.end_date ? { endDate: event.end_date } : {}),
            ...(event.description ? { description: event.description.slice(0, 300) } : {}),
            ...(event.image_url ? { image: event.image_url } : {}),
            ...(event.ticket_url ? { url: event.ticket_url } : {}),
            location: {
              "@type": "Place", name: venueName || "",
              address: { "@type": "PostalAddress", ...(venueStreet ? { streetAddress: venueStreet } : {}), addressLocality: event.city || "", addressRegion: event.state || "", ...(venueZip ? { postalCode: venueZip } : {}) },
            },
            ...(event.organizer ? { organizer: { "@type": "Organization", name: event.organizer } } : {}),
            ...(buildOffers(event) ? { offers: buildOffers(event) } : {}),
          })}
        </script>
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="flex-1">

        {/* ═══════════ IMAGE GALLERY ═══════════ */}
        {allImages.length > 0 && (
          <ImageGallery images={allImages} title={event.title} />
        )}

        {/* ═══════════ HEADER CARD ═══════════ */}
        <div className={`px-4 relative z-10 ${allImages.length > 0 ? "-mt-16 pt-4" : "pt-8"}`}>
          <div className="max-w-3xl mx-auto">

            {/* Info pills row */}
            <div className="flex flex-wrap items-center gap-2 mb-4">
              {event.category && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-white/8 text-white/70 border border-white/8">
                  {catEmoji} {event.category}
                </span>
              )}
              {past && (
                <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-red-500/20 text-red-400 border border-red-500/30">
                  Past Event
                </span>
              )}
              {priceIsFree && !past && (
                <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
                  Free
                </span>
              )}
              {event.price_range && !priceIsFree && (
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-[#D4A843]/15 text-[#D4A843] border border-[#D4A843]/20">
                  {event.price_range}
                </span>
              )}
            </div>

            {/* Title */}
            <h1 className="font-serif text-[1.75rem] sm:text-4xl md:text-[2.75rem] text-white font-bold leading-[1.12] mb-5">
              {decodeHTMLEntities(event.title)}
            </h1>

            {/* Quick-glance row: date · time · venue */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-5 mb-6">
              <div className="flex items-center gap-2.5 text-white/70">
                <span className="flex items-center justify-center w-9 h-9 rounded-xl bg-white/8">
                  <svg className="w-4.5 h-4.5 text-[#D4A843]" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" /></svg>
                </span>
                <div>
                  <p className="text-sm font-semibold text-white/90">{dateStr}</p>
                  {event.time && <p className="text-xs text-white/50">{event.time}</p>}
                </div>
              </div>

              {venueName && (
                <div className="flex items-center gap-2.5 text-white/70">
                  <span className="flex items-center justify-center w-9 h-9 rounded-xl bg-white/8">
                    <svg className="w-4.5 h-4.5 text-[#A32D2F]" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" /></svg>
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-white/90">{venueName}</p>
                    <p className="text-xs text-white/50">
                      {venueStreet ? `${venueStreet}, ` : ""}{[event.city, event.state].filter(Boolean).join(", ")}{venueZip ? ` ${venueZip}` : ""}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* CTA + action row */}
            <div className="flex flex-wrap items-center gap-3">
              {event.ticket_url && !past && (
                <a
                  href={event.ticket_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-full font-bold text-sm transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg"
                  style={{ background: "linear-gradient(135deg, #D4A843 0%, #c49535 100%)", color: "#0B1D3A" }}
                >
                  {getCtaText(event.price_range)}
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" /></svg>
                </a>
              )}
              <ShareButtons title={event.title} slug={event.slug || slug!} />
              <AddToCalendar event={event} slug={event.slug || slug!} />
            </div>

            {past && (
              <div className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400/80 text-sm">
                This event has already taken place. <Link to="/events" className="underline hover:text-red-300">Browse upcoming events →</Link>
              </div>
            )}
          </div>
        </div>

        {/* ═══════════ DIVIDER ═══════════ */}
        <div className="max-w-3xl mx-auto px-4 my-8">
          <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        </div>

        {/* ═══════════ CONTENT ═══════════ */}
        <div className="px-4 pb-20">
          <div className="max-w-3xl mx-auto grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-10">

            {/* ── LEFT: Main content ── */}
            <div className="space-y-10 min-w-0">

              {/* Short description as lead callout */}
              {event.long_description && event.description && event.long_description !== event.description && (
                <p className="text-lg text-white/80 font-medium leading-relaxed border-l-2 pl-4" style={{ borderColor: "#D4A843" }}>
                  {event.description}
                </p>
              )}

              {/* Full description */}
              {description && (
                <section>
                  {hasLongDesc && (
                    <h2 className="text-[11px] font-bold uppercase tracking-[0.2em] text-white/30 mb-5">
                      About This Event
                    </h2>
                  )}
                  <EventDescription text={description} />
                </section>
              )}

              {/* Artist / Performer info */}
              {event.artist_info && (
                <section>
                  <h2 className="text-[11px] font-bold uppercase tracking-[0.2em] text-white/30 mb-5">
                    About the Artist
                  </h2>
                  <div className="text-white/70 text-[15px] leading-[1.85] whitespace-pre-line">
                    {event.artist_info}
                  </div>
                </section>
              )}

              {/* Venue section — only if there's extra info or seatmap beyond what's in the header */}
              {(event.venue_info || event.seatmap_url) && (
                <section>
                  <h2 className="text-[11px] font-bold uppercase tracking-[0.2em] text-white/30 mb-5">
                    Venue
                  </h2>
                  {event.venue_info && (
                    <div className="text-white/60 text-sm leading-relaxed whitespace-pre-line mb-4">
                      {event.venue_info}
                    </div>
                  )}
                  {event.seatmap_url && (
                    <div>
                      <p className="text-white/40 text-xs font-semibold uppercase tracking-wider mb-2">Seating Chart</p>
                      <a href={event.seatmap_url} target="_blank" rel="noopener noreferrer" className="block cursor-zoom-in">
                        <img src={event.seatmap_url} alt={`Seating chart for ${venueName || "venue"}`} className="w-full rounded-lg bg-white" loading="lazy" />
                      </a>
                      <p className="text-white/30 text-xs mt-2 text-center">Tap to view full size · via Ticketmaster</p>
                    </div>
                  )}
                </section>
              )}
            </div>

            {/* ── RIGHT: Sidebar ── */}
            <div className="space-y-5 lg:sticky lg:top-4 lg:self-start">

              {/* Sticky CTA card (desktop) */}
              {event.ticket_url && !past && (
                <div className="rounded-2xl p-5 text-center" style={{ background: "linear-gradient(145deg, rgba(212,168,67,0.12) 0%, rgba(212,168,67,0.04) 100%)", border: "1px solid rgba(212,168,67,0.15)" }}>
                  {event.price_range && (
                    <p className="text-2xl font-bold text-white mb-1">
                      {priceIsFree ? "Free Event" : event.price_range}
                    </p>
                  )}
                  <a
                    href={event.ticket_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-2 w-full mt-3 px-6 py-3 rounded-full font-bold text-sm transition-all hover:scale-[1.02] active:scale-[0.98]"
                    style={{ background: "linear-gradient(135deg, #D4A843 0%, #c49535 100%)", color: "#0B1D3A" }}
                  >
                    {getCtaText(event.price_range)}
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" /></svg>
                  </a>
                </div>
              )}

              {/* Info card */}
              <div className="rounded-2xl bg-white/[0.03] border border-white/[0.06] p-5 space-y-4">
                {event.organizer && (
                  <div className="flex items-start gap-3">
                    <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-white/8 text-sm">🎤</span>
                    <div className="min-w-0">
                      <p className="text-white/90 text-sm font-semibold truncate">{event.organizer}</p>
                      <p className="text-white/40 text-xs">Organizer</p>
                    </div>
                  </div>
                )}

                {event.audience && (
                  <div className="flex items-start gap-3">
                    <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-white/8 text-sm">👥</span>
                    <p className="text-white/80 text-sm">{event.audience}</p>
                  </div>
                )}

                {/* Location card */}
                <a
                  href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(mapsQuery)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-start gap-3 group"
                >
                  <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-white/8 text-sm flex-shrink-0">📍</span>
                  <div className="min-w-0">
                    {venueName && <p className="text-white/80 text-sm font-medium group-hover:text-white transition-colors">{venueName}</p>}
                    {venueStreet && <p className="text-white/50 text-xs">{venueStreet}</p>}
                    <p className="text-white/50 text-xs">{[event.city, event.state].filter(Boolean).join(", ")}{venueZip ? ` ${venueZip}` : ""}</p>
                    <p className="text-[#D4A843] text-xs mt-1 font-medium group-hover:underline">Get Directions →</p>
                  </div>
                </a>

                {/* Source link */}
                {event.ticket_url && (
                  <div className="pt-2 border-t border-white/5">
                    <a
                      href={event.ticket_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-white/30 hover:text-white/50 transition-colors truncate block"
                    >
                      View on {event.source === "eventbrite" ? "Eventbrite" : event.source === "meetup" ? "Meetup" : event.source || "source"} →
                    </a>
                  </div>
                )}
              </div>

              {/* More events in this city */}
              {getCityGroup(event.city) && (
                <Link
                  to={`/events?city=${encodeURIComponent(getCityGroup(event.city)!)}`}
                  className="flex items-center gap-3 p-4 rounded-2xl bg-white/[0.03] border border-white/[0.06] hover:border-white/12 transition-colors group"
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

        {/* ═══════════ FOOTER ═══════════ */}
        <div className="px-4 pb-16">
          <div className="max-w-3xl mx-auto">
            <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-8" />
            <div className="flex items-center justify-between">
              <Link to="/events" className="inline-flex items-center gap-2 text-sm text-white/40 hover:text-white/70 transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 12H5m0 0l7 7m-7-7l7-7" /></svg>
                All Events
              </Link>
              {event.source === "user_submitted" && (
                <Link to={`/events/${event.slug || slug}/edit`} className="text-sm text-white/40 hover:text-white/70 transition-colors">
                  ✏️ Edit
                </Link>
              )}
            </div>
            <p className="text-[10px] text-white/15 mt-6">
              Sourced from {event.source || "web"} · Details may change — verify with the organizer before attending
            </p>
          </div>
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}
