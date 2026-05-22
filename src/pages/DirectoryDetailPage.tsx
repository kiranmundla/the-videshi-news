import { useEffect, useState, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Share2, Link as LinkIcon, Check } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  DirectoryListing,
  getDirectoryListing,
  CATEGORY_ICONS,
  CATEGORY_COLORS,
} from "@/lib/directory";

/* ------------------------------------------------------------------ */
/* Star Rating                                                        */
/* ------------------------------------------------------------------ */
function StarRating({ rating, reviewCount }: { rating: number | null; reviewCount: number | null }) {
  if (!rating) return null;
  const fullStars = Math.floor(rating);
  const hasHalf = rating - fullStars >= 0.3;

  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-0.5">
        {[...Array(5)].map((_, i) => (
          <span
            key={i}
            className={`text-lg ${
              i < fullStars
                ? "text-amber-400"
                : i === fullStars && hasHalf
                ? "text-amber-400/60"
                : "text-muted-foreground/30"
            }`}
          >
            ★
          </span>
        ))}
      </div>
      <span className="text-lg font-semibold text-amber-400">{rating}</span>
      {reviewCount != null && reviewCount > 0 && (
        <span className="text-sm text-muted-foreground">({reviewCount} reviews)</span>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Photo Gallery                                                      */
/* ------------------------------------------------------------------ */
function PhotoGallery({ photos, name }: { photos: string[]; name: string }) {
  const scrollRef = useRef<HTMLDivElement>(null);

  if (!photos.length) return null;

  return (
    <div className="mt-6">
      <h3 className="font-serif text-lg text-foreground mb-3">Photos</h3>
      <div
        ref={scrollRef}
        className="flex gap-3 overflow-x-auto pb-3 scrollbar-none snap-x snap-mandatory"
      >
        {photos.map((url, i) => (
          <div
            key={i}
            className="flex-shrink-0 snap-start w-[85%] sm:w-[45%] lg:w-[30%] rounded-lg overflow-hidden"
          >
            <img
              src={url}
              alt={`${name} — photo ${i + 1}`}
              className="w-full h-44 sm:h-52 object-cover bg-white/5"
              loading="lazy"
            />
          </div>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Share Buttons                                                      */
/* ------------------------------------------------------------------ */
function ShareButtons({ name, slug }: { name: string; slug: string }) {
  const [copied, setCopied] = useState(false);
  const shareUrl = `https://thevideshi.com/directory/${slug}`;
  const shareText = `${name} — Desi Business Directory | The Videshi`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* fallback */
    }
  };

  return (
    <div className="flex items-center gap-2">
      <a
        href={`https://wa.me/?text=${encodeURIComponent(shareText + " " + shareUrl)}`}
        target="_blank"
        rel="noopener noreferrer"
        className="p-2 rounded-full bg-white/5 hover:bg-white/10 text-foreground/60 hover:text-foreground transition-colors"
        title="Share on WhatsApp"
      >
        <Share2 className="w-4 h-4" />
      </a>
      <button
        onClick={handleCopy}
        className="p-2 rounded-full bg-white/5 hover:bg-white/10 text-foreground/60 hover:text-foreground transition-colors"
        title={copied ? "Copied!" : "Copy link"}
      >
        {copied ? <Check className="w-4 h-4 text-green-400" /> : <LinkIcon className="w-4 h-4" />}
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Hours display                                                      */
/* ------------------------------------------------------------------ */
function HoursDisplay({ hours }: { hours: Record<string, string> | null }) {
  if (!hours || Object.keys(hours).length === 0) return null;

  const dayOrder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const sortedEntries = dayOrder
    .filter((d) => hours[d])
    .map((d) => [d, hours[d]]);

  if (sortedEntries.length === 0) return null;

  const today = new Date().toLocaleDateString("en-US", { weekday: "long" });

  return (
    <div className="mt-6">
      <h3 className="font-serif text-lg text-foreground mb-3">Hours</h3>
      <div className="grid gap-1.5">
        {sortedEntries.map(([day, time]) => (
          <div
            key={day}
            className={`flex justify-between text-sm py-1 px-2 rounded ${
              day === today ? "bg-primary/10 text-foreground font-medium" : "text-muted-foreground"
            }`}
          >
            <span>{day}</span>
            <span>{time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Detail Page                                                        */
/* ------------------------------------------------------------------ */
export default function DirectoryDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [listing, setListing] = useState<DirectoryListing | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    getDirectoryListing(slug).then((data) => {
      setListing(data);
      setLoading(false);
    });
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <CategoryPills />
        <main className="container flex-1 pt-10 pb-16">
          <div className="max-w-3xl mx-auto space-y-4">
            <div className="h-8 w-64 bg-muted/20 animate-pulse rounded" />
            <div className="h-4 w-40 bg-muted/20 animate-pulse rounded" />
            <div className="h-48 bg-muted/20 animate-pulse rounded-lg" />
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  if (!listing) {
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <CategoryPills />
        <main className="container flex-1 pt-10 pb-16 text-center">
          <p className="text-4xl mb-4">🔍</p>
          <p className="text-muted-foreground text-lg">Listing not found.</p>
          <Link to="/directory" className="text-primary hover:underline mt-4 inline-block">
            ← Back to Directory
          </Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  const photos = (listing.photos as string[] | null) || [];
  const location = [listing.city, listing.state].filter(Boolean).join(", ");
  const mapQuery = listing.address
    ? encodeURIComponent(listing.address)
    : listing.latitude && listing.longitude
    ? `${listing.latitude},${listing.longitude}`
    : null;

  const catIcon = CATEGORY_ICONS[listing.category] || "📌";
  const catColor = CATEGORY_COLORS[listing.category] || "bg-slate-100 text-slate-700";

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>{listing.name} — Desi Business Directory | The Videshi</title>
        <meta
          name="description"
          content={`${listing.name} — ${listing.category} in ${location}. Find Indian & desi professionals on The Videshi.`}
        />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container flex-1 pt-8 md:pt-10 pb-16">
        {/* Breadcrumb */}
        <nav className="text-sm text-muted-foreground mb-6">
          <Link to="/directory" className="hover:text-primary">Directory</Link>
          <span className="mx-2">›</span>
          <Link to={`/directory?category=${encodeURIComponent(listing.category)}`} className="hover:text-primary">
            {listing.category}
          </Link>
          <span className="mx-2">›</span>
          <span className="text-foreground/70">{listing.name}</span>
        </nav>

        <div className="max-w-3xl">
          {/* Header */}
          <div className="flex items-start justify-between gap-4 mb-4">
            <div>
              <div className="flex items-center gap-2 mb-2 flex-wrap">
                <span className={`inline-block px-2.5 py-1 rounded text-xs font-medium ${catColor}`}>
                  {catIcon} {listing.category}
                </span>
                {listing.verified && (
                  <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-emerald-600/20 text-emerald-300">
                    ✓ Verified
                  </span>
                )}
                {listing.featured && (
                  <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-amber-500/20 text-amber-300">
                    ✨ Featured
                  </span>
                )}
              </div>
              <h1 className="font-serif text-2xl md:text-4xl text-foreground leading-tight">
                {listing.name}
              </h1>
              {listing.affiliation && (
                <p className="text-sm text-blue-400/80 mt-1">🏥 {listing.affiliation}</p>
              )}
            </div>
            <ShareButtons name={listing.name} slug={listing.slug} />
          </div>

          {/* Rating */}
          <div className="mb-4">
            <StarRating rating={listing.rating} reviewCount={listing.review_count} />
          </div>

          {/* Hero Image */}
          {(listing.image_url || photos.length > 0) && (
            <div className="rounded-xl overflow-hidden mb-6">
              <img
                src={listing.image_url || photos[0]}
                alt={listing.name}
                className="w-full h-48 sm:h-64 md:h-80 object-cover bg-muted/10"
              />
            </div>
          )}

          {/* Description */}
          {listing.description && (
            <div className="mb-6">
              <p className="text-foreground/90 text-base leading-relaxed whitespace-pre-wrap">
                {listing.description}
              </p>
            </div>
          )}

          {/* Contact Info */}
          <div className="bg-card border border-border rounded-xl p-5 mb-6">
            <h3 className="font-serif text-lg text-foreground mb-4">Contact Information</h3>
            <div className="grid gap-3">
              {listing.address && (
                <div className="flex items-start gap-3">
                  <span className="text-lg mt-0.5">📍</span>
                  <div>
                    <p className="text-foreground/90">{listing.address}</p>
                    {mapQuery && (
                      <a
                        href={`https://www.google.com/maps/search/?api=1&query=${mapQuery}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary text-sm hover:underline mt-0.5 inline-block"
                      >
                        Get Directions →
                      </a>
                    )}
                  </div>
                </div>
              )}
              {listing.phone && (
                <div className="flex items-center gap-3">
                  <span className="text-lg">📞</span>
                  <a href={`tel:${listing.phone}`} className="text-primary hover:underline">
                    {listing.phone}
                  </a>
                </div>
              )}
              {listing.email && (
                <div className="flex items-center gap-3">
                  <span className="text-lg">✉️</span>
                  <a href={`mailto:${listing.email}`} className="text-primary hover:underline">
                    {listing.email}
                  </a>
                </div>
              )}
              {listing.website && (
                <div className="flex items-center gap-3">
                  <span className="text-lg">🌐</span>
                  <a
                    href={listing.website.startsWith("http") ? listing.website : `https://${listing.website}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline truncate"
                  >
                    {listing.website.replace(/^https?:\/\//, "")}
                  </a>
                </div>
              )}
            </div>
          </div>

          {/* Hours */}
          <HoursDisplay hours={listing.hours} />

          {/* Photo Gallery */}
          {photos.length > 1 && (
            <PhotoGallery photos={photos.slice(1)} name={listing.name} />
          )}

          {/* CTA buttons */}
          <div className="mt-8 flex flex-wrap gap-3">
            {listing.phone && (
              <a
                href={`tel:${listing.phone}`}
                className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
              >
                📞 Call Now
              </a>
            )}
            {listing.website && (
              <a
                href={listing.website.startsWith("http") ? listing.website : `https://${listing.website}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 border border-primary text-primary rounded-lg font-medium hover:bg-primary/10 transition-colors"
              >
                🌐 Visit Website
              </a>
            )}
            {mapQuery && (
              <a
                href={`https://www.google.com/maps/search/?api=1&query=${mapQuery}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 border border-border text-foreground/80 rounded-lg font-medium hover:bg-muted/20 transition-colors"
              >
                🗺️ Get Directions
              </a>
            )}
          </div>

          {/* Back to directory */}
          <div className="mt-10 pt-6 border-t border-border">
            <Link to="/directory" className="text-primary hover:underline text-sm">
              ← Back to Directory
            </Link>
          </div>
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}
