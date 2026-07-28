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

/* ═══════════════════════════════════════════════════════════════════ */
/*  Constants & Helpers                                               */
/* ═══════════════════════════════════════════════════════════════════ */

const CAT_EMOJI: Record<string, string> = {
  Cultural: "🎭", Music: "🎵", Food: "🍛", Sports: "🏏",
  Community: "🤝", Festival: "🪔", Comedy: "😂", Dance: "💃",
  Religious: "🙏", Education: "🎓", Competition: "🏆",
  Spiritual: "🙏", Shopping: "🛍️", Entertainment: "🎬",
  Technology: "💻", Other: "📌",
};

const SOURCE_NAMES: Record<string, string> = {
  eventbrite: "Eventbrite",
  meetup: "Meetup",
  allevents: "AllEvents",
  sulekha: "Sulekha",
  ticketmaster: "Ticketmaster",
  "spiritual-scraper": "event website",
  temple: "event website",
  web: "event website",
  baps: "BAPS",
  iskcon: "ISKCON",
  znfashions: "ZN Fashions",
  tanishq: "Tanishq",
  user_submitted: "user submission",
};

function sourceDisplayName(src: string | null): string {
  if (!src) return "event website";
  return SOURCE_NAMES[src] || src.replace(/-/g, " ");
}

function getCityGroup(city: string): string | null {
  for (const g of CITY_GROUPS) if (g.cities.includes(city)) return g.label;
  return null;
}

function getCtaText(pr: string | null): string {
  if (!pr) return "Get Tickets";
  const l = pr.toLowerCase();
  if (l === "free" || l.includes("free")) return "RSVP Free";
  if (l.includes("register")) return "Register Now";
  return "Get Tickets";
}

function isPastEvent(d: string): boolean {
  return new Date(d + "T23:59:59") < new Date();
}

function decodeHTML(t: string): string {
  const el = document.createElement("textarea");
  el.innerHTML = t;
  return el.value;
}

function buildOffers(ev: EventItem): Record<string, unknown> | null {
  const raw = (ev.price_range || "").trim();
  const l = raw.toLowerCase();
  const vf = ev.created_at || ev.date || null;
  let validFrom: string | undefined;
  if (vf) { const d = new Date(vf); if (!isNaN(d.getTime())) validFrom = d.toISOString(); }
  const url = ev.ticket_url || (ev.slug ? `https://www.thevideshi.com/events/${ev.slug}` : undefined);
  const base = { "@type": "Offer" as const, priceCurrency: "USD", availability: "https://schema.org/InStock", ...(validFrom ? { validFrom } : {}), ...(url ? { url } : {}) };
  if (l && (l === "free" || l.startsWith("free"))) return { ...base, price: "0" };
  if (!raw || ["tbd", "varies", "none"].includes(l)) return null;
  const m = raw.replace(/,/g, "").match(/\d+(?:\.\d+)?/);
  return m ? { ...base, price: m[0] } : null;
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  Venue images fallback (static JSON)                               */
/* ═══════════════════════════════════════════════════════════════════ */

type VenueImageEntry = { city: string; images: string[]; attribution: string };
type VenueImageMap = Record<string, VenueImageEntry>;
const VENUE_IMAGES_URL = "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/venues/venue-images.json";
let _viCache: VenueImageMap | null = null;
async function fetchVenueImages(): Promise<VenueImageMap> {
  if (_viCache) return _viCache;
  try { const r = await fetch(VENUE_IMAGES_URL); if (!r.ok) return {}; _viCache = await r.json(); return _viCache!; } catch { return {}; }
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  Sub-components                                                    */
/* ═══════════════════════════════════════════════════════════════════ */

/* ── Hero Image ─────────────────────────────────────────────────── */

function HeroImage({ src, title }: { src: string; title: string }) {
  return (
    <div className="relative w-full rounded-2xl overflow-hidden shadow-2xl shadow-black/40">
      <img
        src={src}
        alt={title}
        className="w-full object-cover bg-black/40"
        style={{ maxHeight: "56vh", minHeight: "220px" }}
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent" />
    </div>
  );
}

/* ── Category fallback images (same as EventsPage) ─────────────── */

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
  Shopping: "/images/events/cultural.jpg",
  Spiritual: "/images/events/religious.jpg",
  Other: "/images/events/other.jpg",
};

function categoryFallbackImg(category?: string | null): string {
  return CAT_FALLBACK_IMG[category || "Other"] || CAT_FALLBACK_IMG["Other"];
}

/* ── Photo Gallery (horizontal scroll) ──────────────────────────── */

function PhotoGallery({ images, label }: { images: string[]; label: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [failedSet, setFailedSet] = useState<Set<number>>(new Set());
  const validImages = images.filter((_, i) => !failedSet.has(i));
  if (!validImages.length) return null;

  const scroll = (dir: number) => {
    const el = ref.current;
    if (!el) return;
    el.scrollBy({ left: dir * el.clientWidth * 0.7, behavior: "smooth" });
  };

  return (
    <div className="relative group">
      <div
        ref={ref}
        className="flex gap-3 overflow-x-auto snap-x snap-mandatory scrollbar-none pb-2"
        style={{ WebkitOverflowScrolling: "touch" }}
      >
        {images.map((url, i) => failedSet.has(i) ? null : (
          <div key={i} className="flex-shrink-0 snap-start w-[80%] sm:w-[55%] md:w-[40%] rounded-xl overflow-hidden">
            <img
              src={url}
              alt={`${label} — photo ${i + 1}`}
              className="w-full h-48 sm:h-56 object-cover bg-white/5"
              loading="lazy"
              onError={() => setFailedSet(prev => new Set([...prev, i]))}
            />
          </div>
        ))}
      </div>
      {images.length > 2 && (
        <>
          <button onClick={() => scroll(-1)} className="hidden md:flex absolute left-0 top-1/2 -translate-y-1/2 -translate-x-3 w-9 h-9 rounded-full bg-black/70 backdrop-blur items-center justify-center text-white/80 hover:bg-black/90 transition opacity-0 group-hover:opacity-100 z-10 shadow-lg">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" /></svg>
          </button>
          <button onClick={() => scroll(1)} className="hidden md:flex absolute right-0 top-1/2 -translate-y-1/2 translate-x-3 w-9 h-9 rounded-full bg-black/70 backdrop-blur items-center justify-center text-white/80 hover:bg-black/90 transition opacity-0 group-hover:opacity-100 z-10 shadow-lg">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" /></svg>
          </button>
        </>
      )}
    </div>
  );
}

/* ── Description Renderer ───────────────────────────────────────── */

function EventDescription({ text }: { text: string }) {
  const paragraphs = text.split(/\n\s*\n/).filter(p => p.trim());
  if (paragraphs.length <= 1) {
    const lines = text.split("\n").filter(l => l.trim());
    return (
      <div className="space-y-3">
        {lines.map((line, i) => (
          <p key={i} className="text-white/75 text-base leading-[1.85]">{line.trim()}</p>
        ))}
      </div>
    );
  }
  return (
    <div className="space-y-5">
      {paragraphs.map((para, i) => (
        <p key={i} className="text-white/75 text-base leading-[1.85]">{para.trim()}</p>
      ))}
    </div>
  );
}

/* ── Share Buttons ──────────────────────────────────────────────── */

function ShareButtons({ title, slug }: { title: string; slug: string }) {
  const [copied, setCopied] = useState(false);
  const shareUrl = `https://thevideshi.com/events/${slug}`;
  const shareText = `${title} — The Videshi`;

  const handleCopy = async () => {
    try { await navigator.clipboard.writeText(shareUrl); } catch {
      const ta = document.createElement("textarea"); ta.value = shareUrl;
      document.body.appendChild(ta); ta.select(); document.execCommand("copy"); document.body.removeChild(ta);
    }
    setCopied(true); setTimeout(() => setCopied(false), 2000);
  };

  const pill = "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-semibold transition-all active:scale-95";

  return (
    <div className="flex flex-wrap items-center gap-2">
      <a href={`https://api.whatsapp.com/send?text=${encodeURIComponent(shareText + "\n" + shareUrl)}`} target="_blank" rel="noopener noreferrer"
        className={`${pill} bg-[#25D366]/12 text-[#25D366] hover:bg-[#25D366]/22`}>
        <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        WhatsApp
      </a>
      <a href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`} target="_blank" rel="noopener noreferrer"
        className={`${pill} bg-white/5 text-white/50 hover:bg-white/10 hover:text-white/70`}>
        <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        Post
      </a>
      <button onClick={handleCopy}
        className={`${pill} ${copied ? "bg-emerald-500/15 text-emerald-400" : "bg-white/5 text-white/50 hover:bg-white/10 hover:text-white/70"}`}>
        {copied
          ? <><Check className="w-3.5 h-3.5" />Copied!</>
          : <><svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.86-2.554a4.5 4.5 0 00-1.242-7.244l-4.5-4.5a4.5 4.5 0 00-6.364 6.364L5.25 9.879"/></svg>Copy Link</>}
      </button>
    </div>
  );
}

/* ── Add to Calendar ────────────────────────────────────────────── */

function parseEventDT(date: string, time: string | null): Date {
  const d = new Date(date + "T12:00:00");
  if (!time) return d;
  const m = time.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
  if (!m) return d;
  let h = parseInt(m[1], 10);
  const min = parseInt(m[2], 10);
  const ap = m[3].toUpperCase();
  if (ap === "PM" && h !== 12) h += 12;
  if (ap === "AM" && h === 12) h = 0;
  d.setHours(h, min, 0, 0);
  return d;
}

function fmtCal(d: Date): string {
  const p = (n: number) => n.toString().padStart(2, "0");
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}T${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

function AddToCalendar({ event, slug }: { event: EventItem; slug: string }) {
  const [open, setOpen] = useState(false);
  const loc = [event.venue_name, event.city, event.state].filter(Boolean).join(", ");
  const desc = (event.description || "").slice(0, 500) + `\n\nhttps://thevideshi.com/events/${slug}`;
  const start = parseEventDT(event.date, event.time);
  const end = event.end_date ? parseEventDT(event.end_date, null) : new Date(start.getTime() + 2 * 3600000);

  const gcal = () => {
    const hasTime = !!event.time;
    let dates: string;
    if (hasTime) { dates = `${fmtCal(start)}/${fmtCal(end)}`; }
    else {
      const p = (n: number) => n.toString().padStart(2, "0");
      const s = `${start.getFullYear()}${p(start.getMonth() + 1)}${p(start.getDate())}`;
      const nd = new Date(start.getTime() + 86400000);
      const e = `${nd.getFullYear()}${p(nd.getMonth() + 1)}${p(nd.getDate())}`;
      dates = `${s}/${e}`;
    }
    window.open(`https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(event.title)}&dates=${dates}&location=${encodeURIComponent(loc)}&details=${encodeURIComponent(desc)}`, "_blank");
    setOpen(false);
  };

  const ics = () => {
    const blob = new Blob([[
      "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//The Videshi//Events//EN", "BEGIN:VEVENT",
      `DTSTART:${fmtCal(start)}`, `DTEND:${fmtCal(end)}`,
      `SUMMARY:${event.title.replace(/[,;\\]/g, " ")}`,
      `LOCATION:${loc.replace(/[,;\\]/g, " ")}`,
      `DESCRIPTION:${desc.replace(/\n/g, "\\n").replace(/[,;\\]/g, " ")}`,
      `URL:https://thevideshi.com/events/${slug}`,
      "END:VEVENT", "END:VCALENDAR",
    ].join("\r\n")], { type: "text/calendar;charset=utf-8" });
    const u = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = u; a.download = `${slug}.ics`;
    document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(u);
    setOpen(false);
  };

  return (
    <div className="relative inline-block">
      <button onClick={() => setOpen(!open)}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-semibold bg-[#D4A843]/12 text-[#D4A843] hover:bg-[#D4A843]/22 transition-all active:scale-95">
        <CalendarPlus className="w-3.5 h-3.5" /> Save
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute left-0 bottom-full mb-2 z-50 bg-[#1a1e28] border border-white/10 rounded-xl shadow-2xl overflow-hidden min-w-[200px]">
            <button onClick={gcal} className="w-full px-4 py-3 text-left text-sm text-white/80 hover:bg-white/5 flex items-center gap-3 transition-colors">
              <svg className="w-4 h-4 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
              Google Calendar
            </button>
            <div className="h-px bg-white/5" />
            <button onClick={ics} className="w-full px-4 py-3 text-left text-sm text-white/80 hover:bg-white/5 flex items-center gap-3 transition-colors">
              <svg className="w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
              Download .ics
            </button>
          </div>
        </>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  Main Page                                                         */
/* ═══════════════════════════════════════════════════════════════════ */

export default function EventDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [event, setEvent] = useState<EventItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [extraImages, setExtraImages] = useState<string[]>([]);
  const [venuePhotos, setVenuePhotos] = useState<string[]>([]);
  const [venuePhotoAttribution, setVenuePhotoAttribution] = useState("");

  useEffect(() => {
    if (!slug) { setNotFound(true); setLoading(false); return; }
    setLoading(true);
    getEventBySlug(slug).then(async (data) => {
      if (!data) { setNotFound(true); setLoading(false); return; }
      setEvent(data);

      // Extra event images (from venue_images DB field, excluding the hero)
      const dbImgs = Array.isArray(data.venue_images) ? data.venue_images.filter(Boolean) : [];
      const extras = dbImgs.filter(img => img !== data.image_url);
      setExtraImages(extras);

      // Venue photos from static JSON (fallback for venue ambiance)
      if (data.venue_name) {
        const map = await fetchVenueImages();
        const entry = map[data.venue_name];
        if (entry?.images?.length) {
          setVenuePhotos(entry.images);
          setVenuePhotoAttribution(entry.attribution || "");
        }
      }

      setLoading(false);
    });
  }, [slug]);

  /* ── Loading ── */
  if (loading) {
    return (
      <div className="min-h-screen flex flex-col bg-[#0a0a0a]">
        <Masthead /><CategoryPills />
        <main className="flex-1 px-4 pt-10 pb-20">
          <div className="max-w-3xl mx-auto space-y-5">
            <div className="h-[40vh] rounded-2xl bg-white/[0.04] animate-pulse" />
            <div className="h-8 w-3/4 rounded-lg bg-white/[0.04] animate-pulse" />
            <div className="h-4 w-1/2 rounded bg-white/[0.04] animate-pulse" />
            <div className="h-12 w-48 rounded-full bg-white/[0.04] animate-pulse" />
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  /* ── 404 ── */
  if (notFound || !event) {
    return (
      <div className="min-h-screen flex flex-col bg-[#0a0a0a]">
        <Helmet><title>Event Not Found — The Videshi</title></Helmet>
        <Masthead /><CategoryPills />
        <main className="flex-1 pt-20 pb-20 text-center px-4">
          <p className="text-6xl mb-6">🎪</p>
          <h1 className="font-serif text-3xl text-white mb-3">Event Not Found</h1>
          <p className="text-white/50 mb-8 text-sm">This event may have passed or the link might be incorrect.</p>
          <Link to="/events" className="inline-block px-6 py-3 rounded-full bg-white text-black font-semibold text-sm hover:bg-white/90 transition-colors">
            ← Browse All Events
          </Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  /* ── Derived data ── */
  const dateStr = formatEventDateLong(event.date, event.end_date);
  const past = isPastEvent(event.date);
  const catEmoji = CAT_EMOJI[event.category || "Other"] || "📌";
  const priceIsFree = event.price_range?.toLowerCase().includes("free");

  // Venue parts
  const venueName = event.venue_name?.includes(",") && !event.street_address
    ? event.venue_name.split(",")[0].trim()
    : (event.venue_name || "");
  const venueStreet = event.street_address
    || (event.venue_name?.includes(",") ? event.venue_name.split(",").slice(1).join(",").trim() : "");
  const venueZip = event.zip_code || "";
  const cityState = [event.city, event.state].filter(Boolean).join(", ");
  const mapsQuery = [event.venue_name, venueStreet, cityState, venueZip].filter(Boolean).join(", ");
  // Prefer lat/lng for Google Maps link when available (exact location)
  const mapsHref = event.latitude && event.longitude
    ? `https://www.google.com/maps/search/?api=1&query=${event.latitude},${event.longitude}`
    : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(mapsQuery)}`;

  // Descriptions
  const longDesc = event.long_description?.replace(/\s*(Read below:?|Read more:?)\s*$/i, "").trim() || null;
  const shortDesc = event.description || null;
  const hasRichDesc = !!longDesc && longDesc.length > 100;

  const metaDesc = shortDesc
    ? `${shortDesc.slice(0, 155)}…`
    : `${event.title} on ${dateStr} at ${venueName}, ${event.city}`;

  // Address line builder
  const addressParts: string[] = [];
  if (venueStreet) addressParts.push(venueStreet);
  if (cityState) addressParts.push(cityState);
  if (venueZip && !addressParts.some(p => p.includes(venueZip))) addressParts.push(venueZip);
  const fullAddress = addressParts.join(", ");

  return (
    <div className="min-h-screen flex flex-col bg-[#0a0a0a]">
      <Helmet>
        <title>{event.title} — Events — The Videshi</title>
        <meta name="description" content={metaDesc} />
        <meta property="og:title" content={event.title} />
        <meta property="og:description" content={metaDesc} />
        {event.image_url && <meta property="og:image" content={event.image_url} />}
        <meta property="og:type" content="website" />
        <meta property="og:url" content={`https://www.thevideshi.com/events/${slug}`} />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={event.title} />
        <meta name="twitter:description" content={metaDesc} />
        {event.image_url && <meta name="twitter:image" content={event.image_url} />}
        <link rel="canonical" href={`https://www.thevideshi.com/events/${slug}`} />
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org", "@type": "Event",
            name: event.title,
            ...(event.date ? { startDate: event.date } : {}),
            ...(event.end_date ? { endDate: event.end_date } : {}),
            ...(shortDesc ? { description: shortDesc.slice(0, 300) } : {}),
            ...(event.image_url ? { image: event.image_url } : {}),
            ...(event.ticket_url ? { url: event.ticket_url } : {}),
            location: {
              "@type": "Place", name: venueName,
              address: {
                "@type": "PostalAddress",
                ...(venueStreet ? { streetAddress: venueStreet } : {}),
                addressLocality: event.city || "",
                addressRegion: event.state || "",
                ...(venueZip ? { postalCode: venueZip } : {}),
              },
            },
            ...(event.organizer ? { organizer: { "@type": "Organization", name: event.organizer } } : {}),
            ...(buildOffers(event) ? { offers: buildOffers(event) } : {}),
          })}
        </script>
      </Helmet>

      <Masthead />
      <CategoryPills />

      {/* ╔══════════════════════════════════════════════════════════╗ */}
      {/* ║  SINGLE COLUMN — everything stacks in one flow          ║ */}
      {/* ╚══════════════════════════════════════════════════════════╝ */}
      <main className="flex-1 px-4">
        <div className="max-w-3xl mx-auto pt-6 sm:pt-10 pb-20 space-y-8">

          {/* ━━━ 1. HERO IMAGE or GRADIENT BANNER ━━━ */}
          <HeroImage src={event.image_url || categoryFallbackImg(event.category)} title={event.title} />

          {/* ━━━ 2. PILLS ROW ━━━ */}
          <div className="flex flex-wrap items-center gap-2">
            {event.category && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/[0.06] text-white/60">
                {catEmoji} {event.category}
              </span>
            )}
            {past && (
              <span className="px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider bg-red-500/15 text-red-400 border border-red-500/20">
                Past Event
              </span>
            )}
            {priceIsFree && !past && (
              <span className="px-3 py-1 rounded-full text-[11px] font-bold bg-emerald-500/12 text-emerald-400">
                Free
              </span>
            )}
            {event.price_range && !priceIsFree && (
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-[#D4A843]/12 text-[#D4A843]">
                {event.price_range}
              </span>
            )}
          </div>

          {/* ━━━ 3. TITLE ━━━ */}
          <h1 className="font-serif text-3xl sm:text-4xl md:text-[2.75rem] text-white font-bold leading-[1.12] -mt-2">
            {decodeHTML(event.title)}
          </h1>

          {/* ━━━ 4. DATE + VENUE ROW ━━━ */}
          <div className="flex flex-col sm:flex-row gap-4 sm:gap-8 -mt-2">
            {/* Date */}
            <div className="flex items-start gap-3">
              <span className="flex items-center justify-center w-10 h-10 rounded-xl bg-[#D4A843]/10 flex-shrink-0">
                <svg className="w-5 h-5 text-[#D4A843]" fill="none" stroke="currentColor" strokeWidth={1.7} viewBox="0 0 24 24">
                  <rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>
                </svg>
              </span>
              <div>
                <p className="text-[15px] font-semibold text-white/90">{dateStr}</p>
                {event.time && <p className="text-sm text-white/45 mt-0.5">{event.time}</p>}
              </div>
            </div>

            {/* Venue (single appearance — not repeated anywhere else) */}
            {venueName && (
              <div className="flex items-start gap-3">
                <span className="flex items-center justify-center w-10 h-10 rounded-xl bg-[#A32D2F]/10 flex-shrink-0">
                  <svg className="w-5 h-5 text-[#A32D2F]" fill="none" stroke="currentColor" strokeWidth={1.7} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"/>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/>
                  </svg>
                </span>
                <div>
                  <p className="text-[15px] font-semibold text-white/90">{venueName}</p>
                  {fullAddress && <p className="text-sm text-white/45 mt-0.5">{fullAddress}</p>}
                </div>
              </div>
            )}
          </div>

          {/* ━━━ 5. CTA BUTTON (ONE only) ━━━ */}
          {event.ticket_url && !past && (
            <a
              href={event.ticket_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full py-3.5 rounded-full font-bold text-[15px] transition-all hover:scale-[1.01] active:scale-[0.99] shadow-lg shadow-[#D4A843]/10"
              style={{ background: "linear-gradient(135deg, #D4A843 0%, #b8872f 100%)", color: "#0B1D3A" }}
            >
              {getCtaText(event.price_range)}
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25"/>
              </svg>
            </a>
          )}

          {past && (
            <div className="p-4 rounded-xl bg-red-500/8 border border-red-500/15 text-red-400/80 text-sm text-center">
              This event has already taken place.{" "}
              <Link to="/events" className="underline hover:text-red-300">Browse upcoming events →</Link>
            </div>
          )}

          {/* ━━━ 6. SHARE ROW ━━━ */}
          <div className="flex flex-wrap items-center gap-2">
            <ShareButtons title={event.title} slug={event.slug || slug!} />
            <AddToCalendar event={event} slug={event.slug || slug!} />
          </div>

          {/* ━━━ DIVIDER ━━━ */}
          <div className="h-px bg-gradient-to-r from-transparent via-white/8 to-transparent" />

          {/* ━━━ 7. ABOUT THIS EVENT ━━━ */}
          {(shortDesc || longDesc) && (
            <section>
              {/* Lead paragraph (short desc as callout when long desc also exists) */}
              {longDesc && shortDesc && longDesc !== shortDesc && (
                <p className="text-lg text-white/80 font-medium leading-relaxed mb-6 pl-4 border-l-2 border-[#D4A843]/40">
                  {shortDesc}
                </p>
              )}

              {hasRichDesc && (
                <h2 className="text-[11px] font-bold uppercase tracking-[0.2em] text-white/25 mb-5">
                  About This Event
                </h2>
              )}

              <EventDescription text={longDesc || shortDesc || ""} />
            </section>
          )}

          {/* ━━━ 8. EVENT PHOTO GALLERY (extra images, below description) ━━━ */}
          {extraImages.length > 0 && (
            <section>
              <h2 className="text-[11px] font-bold uppercase tracking-[0.2em] text-white/25 mb-4">
                Photos
              </h2>
              <PhotoGallery images={extraImages} label={event.title} />
            </section>
          )}

          {/* ━━━ 9. ABOUT THE ARTIST ━━━ */}
          {event.artist_info && event.artist_info.length > 20 && (
            <section>
              <h2 className="text-[11px] font-bold uppercase tracking-[0.2em] text-white/25 mb-5">
                About the Artist
              </h2>
              <div className="text-white/70 text-[15px] leading-[1.85] whitespace-pre-line">
                {event.artist_info}
              </div>
            </section>
          )}

          {/* ━━━ 10. VENUE & DIRECTIONS CARD ━━━ */}
          {venueName && (
            <section>
              <h2 className="text-[11px] font-bold uppercase tracking-[0.2em] text-white/25 mb-4">
                Venue
              </h2>
              <div className="rounded-2xl bg-white/[0.03] border border-white/[0.06] overflow-hidden">
                {/* Venue photos */}
                {venuePhotos.length > 0 && (
                  <div className="border-b border-white/[0.06]">
                    <div className="flex overflow-x-auto snap-x snap-mandatory scrollbar-none" style={{ WebkitOverflowScrolling: "touch" }}>
                      {venuePhotos.map((url, i) => (
                        <div key={i} className="flex-shrink-0 snap-start w-full sm:w-1/2 md:w-1/3">
                          <img src={url} alt={`${venueName} — ${i + 1}`} className="w-full h-44 object-cover" loading="lazy" />
                        </div>
                      ))}
                    </div>
                    {venuePhotoAttribution && (
                      <p className="text-[10px] text-white/15 px-5 py-1.5">Photos · {venuePhotoAttribution}</p>
                    )}
                  </div>
                )}

                <div className="p-5 sm:p-6">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-white font-semibold text-lg">{venueName}</p>
                      {fullAddress && <p className="text-white/45 text-sm mt-1">{fullAddress}</p>}
                    </div>
                    <a
                      href={mapsHref}
                      target="_blank" rel="noopener noreferrer"
                      className="flex-shrink-0 inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-semibold bg-white/[0.06] text-white/60 hover:bg-white/10 hover:text-white/80 transition-all"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"/>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/>
                      </svg>
                      Directions
                    </a>
                  </div>

                  {event.venue_info && (
                    <div className="text-white/50 text-sm leading-relaxed mt-4 whitespace-pre-line">
                      {event.venue_info}
                    </div>
                  )}

                  {event.seatmap_url && (
                    <div className="mt-5">
                      <p className="text-white/30 text-xs font-semibold uppercase tracking-wider mb-2">Seating Chart</p>
                      <a href={event.seatmap_url} target="_blank" rel="noopener noreferrer" className="block cursor-zoom-in">
                        <img src={event.seatmap_url} alt="Seating chart" className="w-full rounded-lg bg-white" loading="lazy" />
                      </a>
                    </div>
                  )}
                </div>
              </div>
            </section>
          )}

          {/* ━━━ 11. ORGANIZER ━━━ */}
          {event.organizer && (
            <div className="flex items-center gap-3 px-5 py-4 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
              <span className="flex items-center justify-center w-9 h-9 rounded-full bg-white/[0.06] text-sm">🎤</span>
              <div>
                <p className="text-white/80 text-sm font-semibold">{event.organizer}</p>
                <p className="text-white/35 text-xs">Organizer</p>
              </div>
            </div>
          )}

          {/* ━━━ 12. MORE EVENTS ━━━ */}
          {getCityGroup(event.city) && (
            <Link
              to={`/events?city=${encodeURIComponent(getCityGroup(event.city)!)}`}
              className="flex items-center gap-3 px-5 py-4 rounded-2xl bg-white/[0.03] border border-white/[0.06] hover:border-white/10 transition-colors group"
            >
              <span className="text-lg">🏙️</span>
              <div>
                <p className="text-white/60 text-sm font-medium group-hover:text-white/80 transition-colors">
                  More events in {getCityGroup(event.city)}
                </p>
                <p className="text-white/25 text-xs">Browse all →</p>
              </div>
            </Link>
          )}

          {/* ━━━ 13. FOOTER ━━━ */}
          <div>
            <div className="h-px bg-gradient-to-r from-transparent via-white/8 to-transparent mb-6" />
            <div className="flex items-center justify-between">
              <Link to="/events" className="inline-flex items-center gap-2 text-sm text-white/35 hover:text-white/60 transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 12H5m0 0l7 7m-7-7l7-7"/>
                </svg>
                All Events
              </Link>
              {event.source === "user_submitted" && (
                <Link to={`/events/${event.slug || slug}/edit`} className="text-sm text-white/35 hover:text-white/60 transition-colors">
                  ✏️ Edit
                </Link>
              )}
            </div>
            <p className="text-[10px] text-white/15 mt-5">
              Sourced from {sourceDisplayName(event.source)} · Details may change — verify with the organizer
            </p>
          </div>

        </div>
      </main>

      {/* Override theme vars so footer is visible on dark event bg */}
      <div style={{ "--foreground": "0 0% 85%", "--muted-foreground": "0 0% 55%", "--border": "0 0% 20%" } as React.CSSProperties}>
        <SiteFooter />
      </div>
    </div>
  );
}
