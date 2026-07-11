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
} from "@/lib/directory";

/* ═══════════════════════════════════════════════════════════════════ */
/*  Dark premium color tokens (scoped — page only, not global)       */
/* ═══════════════════════════════════════════════════════════════════ */
const C = {
  bgBase:       "#0a0a0a",
  surface1:     "#111111",
  surface2:     "#161616",
  textPrimary:  "#E4E2D8",
  textSecondary:"rgba(228,226,216,0.6)",
  textMuted:    "rgba(228,226,216,0.35)",
  gold:         "#D4A843",
  goldDim:      "rgba(212,168,67,0.15)",
  goldGlow:     "rgba(212,168,67,0.25)",
  borderSubtle: "rgba(255,255,255,0.06)",
  borderLight:  "rgba(255,255,255,0.1)",
} as const;

/* ── helpers ─────────────────────────────────────────────────────── */
function parseSafe(v: unknown): string[] {
  if (Array.isArray(v)) return v;
  if (typeof v === "string") {
    try { const p = JSON.parse(v); return Array.isArray(p) ? p : []; } catch { return []; }
  }
  return [];
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  Star Rating                                                      */
/* ═══════════════════════════════════════════════════════════════════ */
function StarRating({ rating, reviewCount }: { rating: number | null; reviewCount: number | null }) {
  if (!rating) return null;
  const fullStars = Math.floor(rating);
  const hasHalf = rating - fullStars >= 0.3;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ display: "flex", gap: 2 }}>
        {[...Array(5)].map((_, i) => (
          <span
            key={i}
            style={{
              fontSize: 18,
              color:
                i < fullStars
                  ? C.gold
                  : i === fullStars && hasHalf
                  ? "rgba(212,168,67,0.55)"
                  : "rgba(255,255,255,0.15)",
            }}
          >
            ★
          </span>
        ))}
      </div>
      <span style={{ fontSize: 15, fontWeight: 600, color: C.textPrimary }}>{rating}</span>
      {reviewCount != null && reviewCount > 0 && (
        <span style={{ fontSize: 13, color: C.textMuted }}>({reviewCount} reviews)</span>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  Photo Gallery                                                    */
/* ═══════════════════════════════════════════════════════════════════ */
function PhotoGallery({ photos, name }: { photos: string[]; name: string }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  if (!photos.length) return null;
  return (
    <div style={{ marginTop: 32 }}>
      <h3
        className="font-serif"
        style={{ fontSize: 18, fontWeight: 600, color: C.textPrimary, marginBottom: 12 }}
      >
        Photos
      </h3>
      <div
        ref={scrollRef}
        className="dir-photo-scroll"
        style={{
          display: "flex",
          gap: 12,
          overflowX: "auto",
          paddingBottom: 8,
          WebkitOverflowScrolling: "touch",
          scrollbarWidth: "none",
        }}
      >
        {photos.map((url, i) => (
          <div
            key={i}
            style={{
              flexShrink: 0,
              width: "clamp(200px, 45%, 320px)",
              borderRadius: 10,
              overflow: "hidden",
              border: `1px solid ${C.borderSubtle}`,
            }}
          >
            <img
              src={url}
              alt={`${name} — photo ${i + 1}`}
              style={{ width: "100%", height: 180, objectFit: "cover", display: "block", background: C.surface2 }}
              loading="lazy"
              onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  Share Buttons                                                    */
/* ═══════════════════════════════════════════════════════════════════ */
function ShareButtons({ name, slug }: { name: string; slug: string }) {
  const [copied, setCopied] = useState(false);
  const shareUrl = `https://www.thevideshi.com/directory/${slug}`;
  const shareText = `${name} — Desi Business Directory | The Videshi`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* fallback */ }
  };

  const btnStyle: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
    fontSize: 13,
    fontWeight: 600,
    padding: "10px 20px",
    borderRadius: 8,
    border: `1px solid ${C.borderLight}`,
    background: "rgba(255,255,255,0.04)",
    color: C.textPrimary,
    cursor: "pointer",
    textDecoration: "none",
    transition: "background 0.2s",
  };

  return (
    <>
      <a
        href={`https://wa.me/?text=${encodeURIComponent(shareText + " " + shareUrl)}`}
        target="_blank"
        rel="noopener noreferrer"
        style={btnStyle}
        onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.08)"; }}
        onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.04)"; }}
      >
        <Share2 size={15} /> Share
      </a>
      <button
        onClick={handleCopy}
        style={btnStyle}
        onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.08)"; }}
        onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.04)"; }}
      >
        {copied ? <Check size={15} style={{ color: "#4ade80" }} /> : <LinkIcon size={15} />}
        {copied ? "Copied!" : "Copy Link"}
      </button>
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  Hours Display                                                    */
/* ═══════════════════════════════════════════════════════════════════ */
function HoursCard({ hours }: { hours: Record<string, string> | null }) {
  if (!hours || Object.keys(hours).length === 0) return null;

  const dayOrder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const sortedEntries = dayOrder.filter((d) => hours[d]).map((d) => [d, hours[d]]);
  if (sortedEntries.length === 0) return null;

  const today = new Date().toLocaleDateString("en-US", { weekday: "long" });

  return (
    <div
      style={{
        marginTop: 20,
        background: C.surface1,
        border: `1px solid ${C.borderSubtle}`,
        borderRadius: 16,
        padding: 24,
      }}
    >
      <h4
        style={{
          fontSize: 12,
          fontWeight: 700,
          letterSpacing: "0.1em",
          textTransform: "uppercase" as const,
          color: C.textMuted,
          marginBottom: 12,
        }}
      >
        Hours
      </h4>
      <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
        {sortedEntries.map(([day, time]) => {
          const isToday = day === today;
          return (
            <div
              key={day}
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "6px 0",
                fontSize: 13,
              }}
            >
              <span style={{ color: isToday ? C.gold : C.textSecondary, fontWeight: isToday ? 600 : 400 }}>
                {day === today ? `${day} (Today)` : day}
              </span>
              <span style={{ color: isToday ? C.gold : C.textPrimary, fontWeight: isToday ? 600 : 500 }}>
                {time}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  Contact Card (sidebar)                                           */
/* ═══════════════════════════════════════════════════════════════════ */
function ContactCard({ listing }: { listing: DirectoryListing }) {
  const mapQuery = listing.address
    ? encodeURIComponent(listing.address)
    : listing.latitude && listing.longitude
    ? `${listing.latitude},${listing.longitude}`
    : null;

  const languages = parseSafe(listing.languages);
  const nonEnglish = languages.filter((l) => l !== "English");

  const rows: { icon: string; content: React.ReactNode }[] = [];

  if (listing.address) {
    rows.push({
      icon: "✦",
      content: (
        <div>
          <span>{listing.address}</span>
          {mapQuery && (
            <a
              href={`https://www.google.com/maps/search/?api=1&query=${mapQuery}`}
              target="_blank"
              rel="noopener noreferrer"
              style={{ display: "block", color: C.gold, fontSize: 12, marginTop: 2, textDecoration: "none" }}
            >
              Get Directions →
            </a>
          )}
        </div>
      ),
    });
  }
  if (listing.phone) {
    rows.push({
      icon: "✦",
      content: <a href={`tel:${listing.phone}`} style={{ color: C.textPrimary, textDecoration: "none" }}>{listing.phone}</a>,
    });
  }
  if (listing.email) {
    rows.push({
      icon: "✦",
      content: <a href={`mailto:${listing.email}`} style={{ color: C.textPrimary, textDecoration: "none" }}>{listing.email}</a>,
    });
  }
  if (listing.website) {
    const href = listing.website.startsWith("http") ? listing.website : `https://${listing.website}`;
    rows.push({
      icon: "✦",
      content: (
        <a href={href} target="_blank" rel="noopener noreferrer" style={{ color: C.textPrimary, textDecoration: "none", wordBreak: "break-all" }}>
          {listing.website.replace(/^https?:\/\//, "")}
        </a>
      ),
    });
  }
  if (nonEnglish.length > 0) {
    rows.push({ icon: "✦", content: <span>{["English", ...nonEnglish].join(", ")}</span> });
  }

  if (rows.length === 0) return null;

  return (
    <div
      style={{
        background: C.surface1,
        border: `1px solid ${C.borderSubtle}`,
        borderRadius: 16,
        padding: 24,
      }}
    >
      <h4
        style={{
          fontSize: 12,
          fontWeight: 700,
          letterSpacing: "0.1em",
          textTransform: "uppercase" as const,
          color: C.textMuted,
          marginBottom: 16,
        }}
      >
        Contact
      </h4>
      {rows.map((row, i) => (
        <div
          key={i}
          style={{
            display: "flex",
            alignItems: "flex-start",
            gap: 12,
            padding: "12px 0",
            borderBottom: i < rows.length - 1 ? `1px solid ${C.borderSubtle}` : "none",
            fontSize: 14,
            color: C.textSecondary,
          }}
        >
          <span style={{ width: 18, textAlign: "center" as const, color: C.gold, fontSize: 14, flexShrink: 0, marginTop: 1 }}>
            {row.icon}
          </span>
          <div style={{ flex: 1, minWidth: 0 }}>{row.content}</div>
        </div>
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  Main Page Component                                              */
/* ═══════════════════════════════════════════════════════════════════ */
export default function DirectoryDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [listing, setListing] = useState<DirectoryListing | null>(null);
  const [loading, setLoading] = useState(true);
  const [heroError, setHeroError] = useState(false);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    setHeroError(false);
    getDirectoryListing(slug).then((data) => {
      setListing(data);
      setLoading(false);
    });
  }, [slug]);

  /* ── Loading state ──────────────────────────────────────────────── */
  if (loading) {
    return (
      <div style={{ background: C.bgBase, color: C.textPrimary, minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        <Masthead />
        <CategoryPills />
        <main style={{ flex: 1, padding: "40px 20px", maxWidth: 1200, margin: "0 auto", width: "100%" }}>
          <div style={{ maxWidth: 720 }}>
            <div style={{ height: 32, width: 260, background: C.surface2, borderRadius: 6, marginBottom: 16 }} />
            <div style={{ height: 16, width: 180, background: C.surface2, borderRadius: 4, marginBottom: 16 }} />
            <div style={{ height: 240, background: C.surface2, borderRadius: 12 }} />
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  /* ── Not found ──────────────────────────────────────────────────── */
  if (!listing) {
    return (
      <div style={{ background: C.bgBase, color: C.textPrimary, minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        <Masthead />
        <CategoryPills />
        <main style={{ flex: 1, padding: "60px 20px", textAlign: "center" }}>
          <p style={{ fontSize: 40, marginBottom: 16 }}>🔍</p>
          <p style={{ fontSize: 18, color: C.textSecondary }}>Listing not found.</p>
          <Link
            to="/directory"
            style={{ color: C.gold, marginTop: 16, display: "inline-block", textDecoration: "none" }}
          >
            ← Back to Directory
          </Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  /* ── Derived data ───────────────────────────────────────────────── */
  const photos = (listing.photos as string[] | null) || [];
  const locationStr = [listing.city, listing.state].filter(Boolean).join(", ");
  const catIcon = CATEGORY_ICONS[listing.category] || "📌";
  const heroSrc = listing.image_url || photos[0] || null;
  const languages = parseSafe(listing.languages);
  const tags = parseSafe(listing.tags);
  const nonEnglish = languages.filter((l) => l !== "English");
  const mapQuery = listing.address
    ? encodeURIComponent(listing.address)
    : listing.latitude && listing.longitude
    ? `${listing.latitude},${listing.longitude}`
    : null;

  return (
    <div style={{ background: C.bgBase, color: C.textPrimary, minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* ── SEO / Head ─────────────────────────────────────────────── */}
      <Helmet>
        <title>{listing.name} — Desi Business Directory | The Videshi</title>
        <meta
          name="description"
          content={`${listing.name} — ${listing.category} in ${locationStr}. Find Indian & desi professionals on The Videshi.`}
        />
        <meta property="og:title" content={`${listing.name} — ${listing.category}`} />
        <meta property="og:description" content={`${listing.name} — ${listing.category} in ${locationStr}. Find Indian & desi professionals on The Videshi.`} />
        {heroSrc && <meta property="og:image" content={heroSrc} />}
        <meta property="og:type" content="website" />
        <meta property="og:url" content={`https://www.thevideshi.com/directory/${listing.slug}`} />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={`${listing.name} — ${listing.category}`} />
        <meta name="twitter:description" content={`${listing.name} — ${listing.category} in ${locationStr}. Find Indian & desi professionals on The Videshi.`} />
        {heroSrc && <meta name="twitter:image" content={heroSrc} />}
        <link rel="canonical" href={`https://www.thevideshi.com/directory/${listing.slug}`} />
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            name: listing.name,
            ...(listing.description ? { description: listing.description } : {}),
            ...(heroSrc ? { image: heroSrc } : {}),
            ...(listing.phone ? { telephone: listing.phone } : {}),
            ...(listing.website ? { url: listing.website } : {}),
            address: {
              "@type": "PostalAddress",
              ...(listing.address ? { streetAddress: listing.address } : {}),
              ...(listing.city ? { addressLocality: listing.city } : {}),
              ...(listing.state ? { addressRegion: listing.state } : {}),
              ...(listing.zip ? { postalCode: listing.zip } : {}),
            },
            ...(listing.rating && listing.review_count
              ? {
                  aggregateRating: {
                    "@type": "AggregateRating",
                    ratingValue: listing.rating,
                    reviewCount: listing.review_count,
                  },
                }
              : {}),
          })}
        </script>
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main style={{ flex: 1, maxWidth: 1200, margin: "0 auto", width: "100%", padding: "0 20px 64px" }}>
        {/* ═══════════════════════════════════════════════════════════ */}
        {/*  HERO IMAGE                                               */}
        {/* ═══════════════════════════════════════════════════════════ */}
        <div
          style={{
            width: "100%",
            maxHeight: 480,
            borderRadius: 16,
            overflow: "hidden",
            position: "relative",
            background: C.surface2,
            marginTop: 24,
          }}
        >
          {heroSrc && !heroError ? (
            <img
              src={heroSrc}
              alt={listing.name}
              style={{ width: "100%", height: "auto", maxHeight: 480, objectFit: "contain", display: "block", margin: "0 auto" }}
              onError={() => setHeroError(true)}
            />
          ) : (
            <div
              style={{
                width: "100%",
                height: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexDirection: "column",
                gap: 8,
              }}
            >
              <span style={{ fontSize: 48 }}>{catIcon}</span>
              <span style={{ fontSize: 13, color: C.textMuted, fontWeight: 500 }}>{listing.category}</span>
            </div>
          )}
          {/* Gradient overlay */}
          <div
            style={{
              position: "absolute",
              bottom: 0,
              left: 0,
              right: 0,
              height: "60%",
              background: `linear-gradient(transparent, ${C.bgBase})`,
              pointerEvents: "none",
            }}
          />
        </div>

        {/* ═══════════════════════════════════════════════════════════ */}
        {/*  TITLE CARD                                               */}
        {/* ═══════════════════════════════════════════════════════════ */}
        <div style={{ marginTop: -48, position: "relative", zIndex: 2 }}>
          {/* Breadcrumb */}
          <nav style={{ fontSize: 12, color: C.textMuted, marginBottom: 14 }}>
            <Link to="/directory" style={{ color: C.textMuted, textDecoration: "none" }}>
              Directory
            </Link>
            <span style={{ margin: "0 8px", opacity: 0.4 }}>›</span>
            <Link
              to={`/directory?category=${encodeURIComponent(listing.category)}`}
              style={{ color: C.textMuted, textDecoration: "none" }}
            >
              {listing.category}
            </Link>
            <span style={{ margin: "0 8px", opacity: 0.4 }}>›</span>
            <span style={{ color: C.textSecondary }}>{listing.name}</span>
          </nav>

          {/* Business name */}
          <h1
            className="font-serif"
            style={{ fontSize: "clamp(28px, 5vw, 36px)", fontWeight: 700, letterSpacing: "-0.02em", lineHeight: 1.15, marginBottom: 12 }}
          >
            {listing.name}
          </h1>

          {/* Affiliation */}
          {listing.affiliation && (
            <p style={{ fontSize: 14, color: "rgba(96,165,250,0.8)", marginBottom: 10 }}>
              🏥 {listing.affiliation}
            </p>
          )}

          {/* Pills */}
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 14 }}>
            {listing.community && (
              <span
                style={{
                  fontSize: 11,
                  fontWeight: 600,
                  letterSpacing: "0.03em",
                  padding: "4px 12px",
                  borderRadius: 20,
                  border: "1px solid rgba(139,92,246,0.3)",
                  color: "#a78bfa",
                  background: "rgba(139,92,246,0.08)",
                }}
              >
                {listing.community}
              </span>
            )}
            <span
              style={{
                fontSize: 11,
                fontWeight: 600,
                padding: "4px 12px",
                borderRadius: 20,
                border: `1px solid ${C.borderLight}`,
                background: "rgba(255,255,255,0.03)",
                color: C.textSecondary,
              }}
            >
              {catIcon} {listing.category}
            </span>
            {listing.verified && (
              <span
                style={{
                  fontSize: 11,
                  fontWeight: 600,
                  padding: "4px 12px",
                  borderRadius: 20,
                  border: "1px solid rgba(16,185,129,0.3)",
                  color: "#34d399",
                  background: "rgba(16,185,129,0.08)",
                }}
              >
                ✓ Verified
              </span>
            )}
            {listing.featured && (
              <span
                style={{
                  fontSize: 11,
                  fontWeight: 600,
                  padding: "4px 12px",
                  borderRadius: 20,
                  border: `1px solid ${C.goldDim}`,
                  color: C.gold,
                  background: C.goldDim,
                }}
              >
                ✨ Featured
              </span>
            )}
            {tags.map((tag) => (
              <span
                key={tag}
                style={{
                  fontSize: 11,
                  fontWeight: 600,
                  padding: "4px 12px",
                  borderRadius: 20,
                  border: `1px solid ${C.borderLight}`,
                  background: "rgba(255,255,255,0.03)",
                  color: C.textSecondary,
                }}
              >
                {tag}
              </span>
            ))}
          </div>

          {/* Star rating */}
          <div style={{ marginBottom: 20 }}>
            <StarRating rating={listing.rating} reviewCount={listing.review_count} />
          </div>

          {/* CTA Buttons */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
            {listing.phone && (
              <a
                href={`tel:${listing.phone}`}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  fontSize: 13,
                  fontWeight: 600,
                  padding: "10px 24px",
                  borderRadius: 8,
                  border: "none",
                  background: C.gold,
                  color: C.bgBase,
                  textDecoration: "none",
                  cursor: "pointer",
                  transition: "background 0.25s, box-shadow 0.25s",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.background = "#e0b84e";
                  (e.currentTarget as HTMLElement).style.boxShadow = `0 4px 20px ${C.goldGlow}`;
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.background = C.gold;
                  (e.currentTarget as HTMLElement).style.boxShadow = "none";
                }}
              >
                Call Now
              </a>
            )}
            {mapQuery && (
              <a
                href={`https://www.google.com/maps/search/?api=1&query=${mapQuery}`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  fontSize: 13,
                  fontWeight: 600,
                  padding: "10px 20px",
                  borderRadius: 8,
                  border: `1px solid ${C.borderLight}`,
                  background: "rgba(255,255,255,0.04)",
                  color: C.textPrimary,
                  textDecoration: "none",
                  cursor: "pointer",
                  transition: "background 0.2s",
                }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.08)"; }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.04)"; }}
              >
                Get Directions
              </a>
            )}
            {listing.website && (
              <a
                href={listing.website.startsWith("http") ? listing.website : `https://${listing.website}`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  fontSize: 13,
                  fontWeight: 600,
                  padding: "10px 20px",
                  borderRadius: 8,
                  border: `1px solid ${C.borderLight}`,
                  background: "rgba(255,255,255,0.04)",
                  color: C.textPrimary,
                  textDecoration: "none",
                  cursor: "pointer",
                  transition: "background 0.2s",
                }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.08)"; }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.04)"; }}
              >
                Visit Website
              </a>
            )}
            <ShareButtons name={listing.name} slug={listing.slug} />
          </div>
        </div>

        {/* ═══════════════════════════════════════════════════════════ */}
        {/*  TWO-COLUMN LAYOUT                                        */}
        {/* ═══════════════════════════════════════════════════════════ */}
        <div className="dir-detail-grid" style={{ marginTop: 40 }}>
          <style>{`
            .dir-detail-grid {
              display: grid;
              grid-template-columns: 1fr 340px;
              gap: 40px;
            }
            @media (max-width: 768px) {
              .dir-detail-grid {
                grid-template-columns: 1fr;
              }
              .dir-detail-sidebar {
                position: static !important;
              }
            }
            .dir-detail-sidebar a:hover {
              color: ${C.gold} !important;
            }
            /* hide scrollbar on photo gallery */
            .dir-photo-scroll::-webkit-scrollbar { display: none; }
          `}</style>

          {/* ── Main column ────────────────────────────────────────── */}
          <div>
            {/* About */}
            {(listing.ai_description || listing.description) && (
              <div>
                <h3
                  className="font-serif"
                  style={{ fontSize: 18, fontWeight: 600, color: C.textPrimary, marginBottom: 12 }}
                >
                  About
                </h3>
                <p style={{ fontSize: 15, lineHeight: 1.85, color: C.textSecondary, whiteSpace: "pre-wrap" }}>
                  {listing.ai_description || listing.description}
                </p>
              </div>
            )}

            {/* Languages */}
            {nonEnglish.length > 0 && (
              <div style={{ marginTop: 28 }}>
                <h3
                  className="font-serif"
                  style={{ fontSize: 18, fontWeight: 600, color: C.textPrimary, marginBottom: 12 }}
                >
                  Languages
                </h3>
                <p style={{ fontSize: 14, color: C.textSecondary }}>
                  🗣 {["English", ...nonEnglish].join(", ")}
                </p>
              </div>
            )}

            {/* Tags / Services */}
            {tags.length > 0 && (
              <div style={{ marginTop: 28 }}>
                <h3
                  className="font-serif"
                  style={{ fontSize: 18, fontWeight: 600, color: C.textPrimary, marginBottom: 14 }}
                >
                  Services
                </h3>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {tags.map((tag) => (
                    <span
                      key={tag}
                      style={{
                        fontSize: 12,
                        fontWeight: 500,
                        padding: "6px 14px",
                        borderRadius: 6,
                        background: C.surface2,
                        border: `1px solid ${C.borderSubtle}`,
                        color: C.textSecondary,
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Photo gallery */}
            {photos.length > 0 && (
              <PhotoGallery photos={heroSrc === photos[0] ? photos.slice(1) : photos} name={listing.name} />
            )}

            {/* Back link */}
            <div style={{ marginTop: 48, paddingTop: 24, borderTop: `1px solid ${C.borderSubtle}` }}>
              <Link to="/directory" style={{ color: C.gold, fontSize: 14, textDecoration: "none" }}>
                ← Back to Directory
              </Link>
            </div>
          </div>

          {/* ── Sidebar ────────────────────────────────────────────── */}
          <aside className="dir-detail-sidebar" style={{ position: "sticky", top: 80, alignSelf: "start" }}>
            <ContactCard listing={listing} />
            <HoursCard hours={listing.hours} />
          </aside>
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}
