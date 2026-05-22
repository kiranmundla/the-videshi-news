import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import {
  Share2,
  Link as LinkIcon,
  Check,
  Phone,
  Mail,
  MapPin,
  Clock,
  ChevronLeft,
  Eye,
} from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  Classified,
  getClassifiedBySlug,
  CATEGORY_ICONS,
  CATEGORY_COLORS,
  timeAgo,
} from "@/lib/classifieds";

/* ------------------------------------------------------------------ */
/* Share buttons                                                      */
/* ------------------------------------------------------------------ */
function ShareButtons({ title, url }: { title: string; url: string }) {
  const [copied, setCopied] = useState(false);

  const shareWhatsApp = () =>
    window.open(
      `https://api.whatsapp.com/send?text=${encodeURIComponent(title + " — " + url)}`,
      "_blank",
    );

  const shareTwitter = () =>
    window.open(
      `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`,
      "_blank",
    );

  const copyLink = async () => {
    await navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={shareWhatsApp}
        className="p-2 rounded-lg border border-border hover:bg-muted/50 transition-colors"
        title="Share on WhatsApp"
      >
        <span className="text-lg">💬</span>
      </button>
      <button
        onClick={shareTwitter}
        className="p-2 rounded-lg border border-border hover:bg-muted/50 transition-colors"
        title="Share on X"
      >
        <span className="text-lg">𝕏</span>
      </button>
      <button
        onClick={copyLink}
        className="p-2 rounded-lg border border-border hover:bg-muted/50 transition-colors"
        title="Copy link"
      >
        {copied ? (
          <Check className="h-4 w-4 text-green-500" />
        ) : (
          <LinkIcon className="h-4 w-4" />
        )}
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Main page                                                          */
/* ------------------------------------------------------------------ */
export default function ClassifiedDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [item, setItem] = useState<Classified | null>(null);
  const [loading, setLoading] = useState(true);
  const [showContact, setShowContact] = useState(false);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    getClassifiedBySlug(slug).then((data) => {
      setItem(data);
      setLoading(false);
    });
  }, [slug]);

  if (loading) {
    return (
      <>
        <Masthead />
        <CategoryPills />
        <main className="container py-8">
          <div className="max-w-3xl mx-auto space-y-4 animate-pulse">
            <div className="h-6 w-48 bg-muted/30 rounded" />
            <div className="h-48 bg-muted/20 rounded-lg" />
            <div className="h-4 w-full bg-muted/20 rounded" />
            <div className="h-4 w-3/4 bg-muted/20 rounded" />
          </div>
        </main>
        <SiteFooter />
      </>
    );
  }

  if (!item) {
    return (
      <>
        <Helmet>
          <title>Classified Not Found — The Videshi</title>
        </Helmet>
        <Masthead />
        <CategoryPills />
        <main className="container py-16 text-center space-y-4">
          <p className="text-5xl">📋</p>
          <h1 className="text-2xl font-bold">Listing Not Found</h1>
          <p className="text-foreground/50">
            This classified may have expired or been removed.
          </p>
          <Link
            to="/classifieds"
            className="inline-flex items-center gap-1 text-primary hover:underline"
          >
            <ChevronLeft className="h-4 w-4" /> Browse all classifieds
          </Link>
        </main>
        <SiteFooter />
      </>
    );
  }

  const photos = item.photos?.length ? item.photos : [];
  const heroImage = item.image_url || (photos.length > 0 ? photos[0] : null);
  const galleryPhotos = photos.filter((p) => p !== heroImage);
  const catEmoji = CATEGORY_ICONS[item.category] || "📌";
  const catColor =
    CATEGORY_COLORS[item.category] || "bg-muted text-muted-foreground";
  const pageUrl = `https://www.thevideshi.com/classifieds/${item.slug}`;
  const locationStr = [item.city, item.state].filter(Boolean).join(", ");

  /* JSON-LD */
  const jsonLd: any = {
    "@context": "https://schema.org",
    "@type":
      item.category === "For Sale"
        ? "Product"
        : item.category === "Services"
          ? "Service"
          : item.category === "Jobs & Gigs"
            ? "JobPosting"
            : "Offer",
    name: item.title,
    description: item.description || item.title,
    url: pageUrl,
  };
  if (heroImage) jsonLd.image = heroImage;
  if (item.price && item.category === "For Sale") {
    jsonLd.offers = {
      "@type": "Offer",
      price: item.price,
      priceCurrency: "USD",
    };
  }
  if (item.category === "Jobs & Gigs") {
    jsonLd.datePosted = item.created_at;
    if (locationStr) {
      jsonLd.jobLocation = {
        "@type": "Place",
        address: locationStr,
      };
    }
  }

  return (
    <>
      <Helmet>
        <title>{item.title} — Classifieds | The Videshi</title>
        <meta
          name="description"
          content={
            item.description?.slice(0, 160) ||
            `${item.category} listing in ${locationStr}`
          }
        />
        <meta property="og:title" content={item.title} />
        <meta
          property="og:description"
          content={
            item.description?.slice(0, 160) ||
            `${item.category} listing on The Videshi`
          }
        />
        {heroImage && <meta property="og:image" content={heroImage} />}
        <meta property="og:type" content="website" />
        <meta property="og:url" content={pageUrl} />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={item.title} />
        <meta
          name="twitter:description"
          content={
            item.description?.slice(0, 160) ||
            `${item.category} listing on The Videshi`
          }
        />
        {heroImage && <meta name="twitter:image" content={heroImage} />}
        <script type="application/ld+json">
          {JSON.stringify(jsonLd)}
        </script>
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container py-6">
        <div className="max-w-3xl mx-auto space-y-6">
          {/* Back link */}
          <Link
            to="/classifieds"
            className="inline-flex items-center gap-1 text-sm text-foreground/50 hover:text-primary"
          >
            <ChevronLeft className="h-4 w-4" /> Back to classifieds
          </Link>

          {/* Hero image */}
          {heroImage && (
            <div className="relative w-full max-h-[75vh] overflow-hidden rounded-lg">
              <img
                src={heroImage}
                alt={item.title}
                className="w-full h-full object-contain bg-black"
                style={{ maxHeight: "75vh" }}
              />
            </div>
          )}

          {/* Photo gallery */}
          {galleryPhotos.length > 0 && (
            <div className="flex gap-3 overflow-x-auto scrollbar-none -mx-1 px-1 pb-2">
              {galleryPhotos.map((url, i) => (
                <div
                  key={i}
                  className="flex-shrink-0 snap-start w-[85%] sm:w-[45%] lg:w-[30%] rounded-lg overflow-hidden"
                >
                  <img
                    src={url}
                    alt={`${item.title} — photo ${i + 2}`}
                    className="w-full h-44 sm:h-52 object-contain bg-white/5"
                    loading="lazy"
                  />
                </div>
              ))}
            </div>
          )}

          {/* Badges + Price */}
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`text-sm font-medium px-3 py-1 rounded-full ${catColor}`}
            >
              {catEmoji} {item.category}
            </span>
            {item.subcategory && (
              <span className="text-sm px-3 py-1 rounded-full bg-muted/50 text-foreground/70">
                {item.subcategory}
              </span>
            )}
            {item.price && (
              <span className="text-sm font-bold px-3 py-1 rounded-md bg-amber-100 text-amber-800">
                {item.price}
              </span>
            )}
          </div>

          {/* Title */}
          <h1 className="text-2xl sm:text-3xl font-bold font-serif leading-tight">
            {item.title}
          </h1>

          {/* Meta */}
          <div className="flex flex-wrap items-center gap-4 text-sm text-foreground/50">
            {locationStr && (
              <span className="flex items-center gap-1">
                <MapPin className="h-4 w-4" />
                {locationStr}
              </span>
            )}
            <span className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              Posted {timeAgo(item.created_at)}
            </span>
            {item.expires_at && (
              <span className="text-foreground/30">
                Expires{" "}
                {new Date(item.expires_at).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                })}
              </span>
            )}
          </div>

          {/* Description */}
          {item.description && (
            <div className="prose prose-sm prose-invert max-w-none">
              <p className="whitespace-pre-wrap text-foreground/80 leading-relaxed">
                {item.description}
              </p>
            </div>
          )}

          {/* Contact section */}
          <div className="border border-border rounded-lg p-5 space-y-4 bg-card">
            <h2 className="font-semibold text-lg">Contact Information</h2>
            {(() => {
              const pref = item.contact_preference || "show_all";
              const showPhone = pref === "show_all" || pref === "phone_only";
              const showEmail = pref === "show_all" || pref === "email_only";
              const inquireOnly = pref === "inquire_only";

              if (inquireOnly) {
                return (
                  <div className="space-y-3">
                    <p className="text-sm text-foreground/50">
                      This poster prefers to be contacted via inquiry.
                    </p>
                    {item.contact_email ? (
                      <a
                        href={`mailto:${item.contact_email}?subject=${encodeURIComponent("Inquiry: " + item.title)}`}
                        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
                      >
                        <Mail className="h-4 w-4" />
                        Send Inquiry
                      </a>
                    ) : (
                      <p className="text-sm text-foreground/40">No contact method available.</p>
                    )}
                  </div>
                );
              }

              if (!showContact) {
                return (
                  <button
                    onClick={() => setShowContact(true)}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
                  >
                    <Eye className="h-4 w-4" />
                    Show Contact Info
                  </button>
                );
              }

              return (
                <div className="space-y-3">
                  {item.contact_name && (
                    <p className="font-medium">{item.contact_name}</p>
                  )}
                  {showPhone && item.contact_phone && (
                    <a
                      href={`tel:${item.contact_phone}`}
                      className="flex items-center gap-2 text-primary hover:underline"
                    >
                      <Phone className="h-4 w-4" />
                      {item.contact_phone}
                    </a>
                  )}
                  {showEmail && item.contact_email && (
                    <a
                      href={`mailto:${item.contact_email}`}
                      className="flex items-center gap-2 text-primary hover:underline"
                    >
                      <Mail className="h-4 w-4" />
                      {item.contact_email}
                    </a>
                  )}
                  {!showPhone && !showEmail && (
                    <p className="text-foreground/50 text-sm">
                      No contact information available for this preference.
                    </p>
                  )}
                </div>
              );
            })()}
          </div>

          {/* Location */}
          {locationStr && (
            <div className="border border-border rounded-lg p-5 space-y-3 bg-card">
              <h2 className="font-semibold text-lg">Location</h2>
              <p className="text-foreground/70">
                {[item.city, item.state, item.zip].filter(Boolean).join(", ")}
              </p>
              <a
                href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(locationStr)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-sm text-primary hover:underline"
              >
                <MapPin className="h-4 w-4" />
                Get Directions
              </a>
            </div>
          )}

          {/* Share + Edit */}
          <div className="flex items-center justify-between border-t border-border pt-4">
            <ShareButtons title={item.title} url={pageUrl} />
            <Link
              to={`/classifieds/${item.slug}/edit`}
              className="text-sm text-foreground/40 hover:text-primary transition-colors"
            >
              Edit / Delete
            </Link>
          </div>
        </div>
      </main>

      <SiteFooter />
    </>
  );
}
