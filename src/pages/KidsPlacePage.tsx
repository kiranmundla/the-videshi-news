import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  fetchLocalPlaceBySlug,
  fetchLocalPlaces,
  LOCAL_CATEGORY_COLORS,
  type KidsLocalPlace,
} from "@/lib/kidsLocalPlaces";

/* ------------------------------------------------------------------ */
/* Constants                                                          */
/* ------------------------------------------------------------------ */

const CATEGORY_EMOJI: Record<string, string> = {
  Daycare: "🏠",
  Dance: "💃",
  Music: "🎵",
  Swimming: "🏊",
  Cricket: "🏏",
  "Martial Arts": "🥋",
  Gymnastics: "🤸",
  Tutoring: "📚",
  "Math Enrichment": "🔢",
  "Coding & STEM": "💻",
  Art: "🎨",
  Chess: "♟️",
  Language: "🗣️",
};

/* ------------------------------------------------------------------ */
/* Info Row                                                           */
/* ------------------------------------------------------------------ */

function InfoRow({ icon, label, value, href }: { icon: string; label: string; value: string | null | undefined; href?: string }) {
  if (!value) return null;
  return (
    <div className="flex items-start gap-3 py-4 border-b border-border/50 last:border-b-0">
      <span className="text-xl flex-shrink-0 mt-0.5">{icon}</span>
      <div>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-0.5">{label}</p>
        {href ? (
          <a href={href} target="_blank" rel="noopener noreferrer" className="text-sm text-[#A32D2F] hover:underline">{value}</a>
        ) : (
          <p className="text-sm text-foreground">{value}</p>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Main component                                                     */
/* ------------------------------------------------------------------ */

export default function KidsPlacePage() {
  const { slug } = useParams<{ slug: string }>();
  const [place, setPlace] = useState<KidsLocalPlace | null>(null);
  const [related, setRelated] = useState<KidsLocalPlace[]>([]);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    async function load() {
      if (!slug) { setNotFound(true); setLoading(false); return; }
      try {
        const p = await fetchLocalPlaceBySlug(slug);
        if (!p) { setNotFound(true); setLoading(false); return; }
        setPlace(p);

        // Related: same category, different place
        const all = await fetchLocalPlaces();
        setRelated(all.filter((r) => r.category === p.category && r.id !== p.id).slice(0, 4));
      } catch {
        setNotFound(true);
      } finally {
        setLoading(false);
      }
    }
    load();
    window.scrollTo(0, 0);
  }, [slug]);

  /* Loading */
  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <CategoryPills />
        <main className="container flex-1 pt-10 pb-16" style={{ maxWidth: 900 }}>
          <div className="animate-pulse space-y-6">
            <div className="h-4 w-32 bg-muted/30 rounded" />
            <div className="h-10 w-3/4 bg-muted/30 rounded" />
            <div className="h-6 w-1/3 bg-muted/30 rounded" />
            <div className="h-32 bg-muted/20 rounded-xl" />
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  /* Not found */
  if (notFound || !place) {
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <CategoryPills />
        <main className="container flex-1 pt-16 pb-16 text-center" style={{ maxWidth: 900 }}>
          <p className="text-6xl mb-6">📍</p>
          <h1 className="font-serif text-2xl text-foreground mb-3">Place Not Found</h1>
          <p className="text-muted-foreground mb-8">We couldn't find the place you're looking for.</p>
          <Link to="/kids" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition-colors" style={{ backgroundColor: "#A32D2F" }}>
            ← Back to Learn
          </Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  const catColor = LOCAL_CATEGORY_COLORS[place.category] || "bg-gray-100 text-gray-700";
  const catEmoji = CATEGORY_EMOJI[place.category] || "📍";
  const fullAddress = [place.address, place.city, place.state, place.zip_code].filter(Boolean).join(", ");
  const directionsUrl = place.address
    ? `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(`${place.address}, ${place.city}, ${place.state} ${place.zip_code || ""}`.trim())}`
    : place.latitude && place.longitude
      ? `https://www.google.com/maps/dir/?api=1&destination=${place.latitude},${place.longitude}`
      : null;
  const addressMapUrl = fullAddress
    ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${place.name}, ${fullAddress}`)}`
    : null;

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Helmet>
        <title>{place.name} — Learn — The Videshi</title>
        <meta name="description" content={place.description || `${place.name} — ${place.category} in ${place.city}, ${place.state}`} />
        <link rel="canonical" href={`https://www.thevideshi.com/kids/places/${slug}`} />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container flex-1 pt-8 md:pt-12 pb-20" style={{ maxWidth: 900 }}>
        {/* Back link */}
        <Link to="/kids" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors mb-8 group">
          <span className="group-hover:-translate-x-0.5 transition-transform">←</span> Learn
        </Link>

        {/* ── Header ────────────────────────────────────── */}
        <header className="mb-10">
          <div className="flex flex-wrap items-center gap-2.5 mb-4">
            <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${catColor}`}>
              {catEmoji} {place.category}
            </span>
            {place.is_indian_focused && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-orange-100 text-orange-700">
                🇮🇳 Indian Community
              </span>
            )}
          </div>

          <h1 className="font-serif text-3xl md:text-4xl lg:text-5xl text-foreground leading-tight mb-3">
            {place.name}
          </h1>

          {place.city && (
            <p className="text-lg text-muted-foreground">
              {place.city}, {place.state}
            </p>
          )}

          {/* Rating */}
          {place.rating && (
            <div className="flex items-center gap-2 mt-3">
              <span className="text-amber-500 text-lg">{"★".repeat(Math.round(place.rating))}</span>
              <span className="text-sm font-medium text-foreground">{place.rating}</span>
              {place.review_count && <span className="text-sm text-muted-foreground">({place.review_count} reviews)</span>}
            </div>
          )}
        </header>

        {/* ── Description ───────────────────────────────── */}
        {place.description && (
          <section className="mb-12">
            <p className="text-lg leading-relaxed text-foreground">{place.description}</p>
          </section>
        )}

        {/* ── Key Details Card ──────────────────────────── */}
        <section className="mb-12">
          <div className="rounded-xl border border-border bg-card p-6 md:p-8">
            <h2 className="font-serif text-lg font-semibold text-foreground mb-2">Details</h2>
            <div className="divide-y divide-border/50">
              <InfoRow icon="📍" label="Address" value={fullAddress || null} href={addressMapUrl || undefined} />
              <InfoRow icon="🎒" label="Ages" value={place.age_range} />
              <InfoRow icon="📞" label="Phone" value={place.phone} href={place.phone ? `tel:${place.phone}` : undefined} />
              <InfoRow icon="🌐" label="Website" value={place.website ? place.website.replace(/^https?:\/\/(www\.)?/, "") : null} href={place.website || undefined} />
              {place.subcategory && <InfoRow icon="📂" label="Type" value={place.subcategory} />}
            </div>
          </div>
        </section>

        {/* ── Action Buttons ────────────────────────────── */}
        <section className="mb-12 flex flex-wrap gap-3">
          {directionsUrl && (
            <a href={directionsUrl} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg text-base font-semibold text-white transition-all hover:opacity-90 shadow-sm"
              style={{ backgroundColor: "#A32D2F" }}>
              🗺️ Directions
            </a>
          )}
          {place.website && (
            <a href={place.website} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg text-base font-semibold border border-border text-foreground hover:bg-muted/50 transition-all">
              Visit Website ↗
            </a>
          )}
          {place.phone && (
            <a href={`tel:${place.phone}`}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg text-base font-semibold border border-border text-foreground hover:bg-muted/50 transition-all">
              📞 Call
            </a>
          )}
        </section>

        {/* ── Tags ──────────────────────────────────────── */}
        {place.tags && place.tags.length > 0 && (
          <section className="mb-12">
            <div className="flex flex-wrap gap-2">
              {place.tags.map((tag) => (
                <span key={tag} className="px-3 py-1 rounded-full text-xs font-medium bg-muted/50 text-muted-foreground">
                  {tag}
                </span>
              ))}
            </div>
          </section>
        )}

        {/* ── More in Category ──────────────────────────── */}
        {related.length > 0 && (
          <section className="mb-8">
            <h2 className="font-serif text-xl font-semibold text-foreground mb-5">
              More {place.category} Near You
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {related.map((r) => (
                <Link key={r.id} to={`/kids/places/${r.slug}`} className="block no-underline">
                  <div className="group rounded-lg border border-border bg-card p-5 transition-all hover:shadow-md hover:border-[#D4A843]/50 h-full">
                    <h3 className="font-serif text-base font-semibold text-foreground leading-snug group-hover:text-[#A32D2F] transition-colors mb-1.5">
                      {r.name}
                    </h3>
                    <p className="text-xs text-muted-foreground mb-2">{r.city}, {r.state}</p>
                    {r.description && (
                      <p className="text-sm text-muted-foreground line-clamp-2">{r.description}</p>
                    )}
                    <span className="text-sm font-medium text-[#A32D2F] mt-3 inline-block group-hover:underline">
                      View Details →
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
