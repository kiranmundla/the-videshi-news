import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import {
  ChevronLeft,
  Star,
  Fuel,
  Users,
  Package,
  Shield,
  ExternalLink,
  Check,
  X as XIcon,
  Share2,
  Link as LinkIcon,
} from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  Car,
  getCarBySlug,
  getCarsByCategory,
  formatMsrp,
  formatPrice,
  brandGradient,
  CATEGORY_ICONS,
  CATEGORY_COLORS,
} from "@/lib/cars";

/* ------------------------------------------------------------------ */
/* Share buttons                                                      */
/* ------------------------------------------------------------------ */
function ShareButtons({ title, url }: { title: string; url: string }) {
  const [copied, setCopied] = useState(false);
  const shareWhatsApp = () =>
    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(title + " — " + url)}`, "_blank");
  const copyLink = async () => {
    await navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <div className="flex items-center gap-2">
      <button onClick={shareWhatsApp} className="p-2 rounded-lg border border-border hover:bg-muted/50 transition-colors" title="Share on WhatsApp">
        <span className="text-lg">💬</span>
      </button>
      <button onClick={copyLink} className="p-2 rounded-lg border border-border hover:bg-muted/50 transition-colors" title="Copy link">
        {copied ? <Check className="h-4 w-4 text-green-500" /> : <LinkIcon className="h-4 w-4" />}
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Spec Tile                                                          */
/* ------------------------------------------------------------------ */
function SpecTile({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-3 p-4 rounded-xl bg-muted/20 border border-border/50">
      <div className="flex-shrink-0 text-primary/70">{icon}</div>
      <div>
        <p className="text-xs text-foreground/50 uppercase tracking-wider">{label}</p>
        <p className="text-sm font-semibold">{value}</p>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Similar Car Card (compact)                                         */
/* ------------------------------------------------------------------ */
function SimilarCard({ car }: { car: Car }) {
  const grad = brandGradient(car.brand);
  return (
    <Link to={`/cars/${car.slug}`} className="block group">
      <div className="flex items-center gap-4 p-3 rounded-xl bg-card border border-border hover:border-primary/40 transition-colors">
        <div className={`w-16 h-16 rounded-lg bg-gradient-to-br ${grad} flex items-center justify-center flex-shrink-0`}>
          <span className="text-foreground/50 text-xs font-bold">{car.brand.slice(0, 3)}</span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold group-hover:text-primary transition-colors truncate">{car.name}</p>
          <p className="text-xs text-foreground/50">{formatMsrp(car.msrp_low, car.msrp_high)}</p>
        </div>
      </div>
    </Link>
  );
}

/* ------------------------------------------------------------------ */
/* CarDetailPage                                                      */
/* ------------------------------------------------------------------ */
export default function CarDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [car, setCar] = useState<Car | null>(null);
  const [similar, setSimilar] = useState<Car[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    getCarBySlug(slug)
      .then((c) => {
        setCar(c);
        if (c) {
          getCarsByCategory(c.category).then((s) =>
            setSimilar(s.filter((x) => x.id !== c.id).slice(0, 4))
          );
        }
      })
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) {
    return (
      <>
        <Masthead />
        <CategoryPills />
        <div className="flex items-center justify-center py-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
        </div>
        <SiteFooter />
      </>
    );
  }

  if (!car) {
    return (
      <>
        <Masthead />
        <CategoryPills />
        <main className="container py-20 text-center">
          <p className="text-5xl mb-4">🚗</p>
          <h1 className="text-2xl font-bold mb-2">Car not found</h1>
          <Link to="/cars" className="text-primary hover:underline">← Back to Cars</Link>
        </main>
        <SiteFooter />
      </>
    );
  }

  const grad = brandGradient(car.brand);
  const pageUrl = `https://www.thevideshi.com/cars/${car.slug}`;
  const edmundsSearch = car.affiliate_url || `https://www.edmunds.com/${car.brand.toLowerCase().replace(/\s+/g, "-")}/${car.model.toLowerCase().replace(/\s+/g, "-")}/`;

  return (
    <>
      <Helmet>
        <title>{car.name} — Price, Specs & Deals | The Videshi</title>
        <meta name="description" content={`${car.name} — starting at ${formatMsrp(car.msrp_low, car.msrp_high)}. ${car.nri_take?.slice(0, 120) ?? ""}`} />
        <meta property="og:title" content={`${car.name} | The Videshi`} />
        <meta property="og:description" content={`Starting at ${formatMsrp(car.msrp_low, car.msrp_high)}. ${car.nri_take?.slice(0, 100) ?? ""}`} />
        <meta property="og:type" content="product" />
        <meta property="og:url" content={pageUrl} />
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Product",
            name: car.name,
            brand: { "@type": "Brand", name: car.brand },
            category: car.category,
            offers: car.msrp_low
              ? {
                  "@type": "AggregateOffer",
                  lowPrice: car.msrp_low,
                  highPrice: car.msrp_high ?? car.msrp_low,
                  priceCurrency: "USD",
                }
              : undefined,
          })}
        </script>
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8 max-w-5xl mx-auto">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-foreground/50 mb-6">
          <Link to="/cars" className="hover:text-primary transition-colors flex items-center gap-1">
            <ChevronLeft className="h-4 w-4" />
            Cars
          </Link>
          <span>/</span>
          <Link to={`/cars?category=${car.category}`} className="hover:text-primary transition-colors">
            {car.category}
          </Link>
          <span>/</span>
          <span className="text-foreground/70 truncate">{car.model}</span>
        </nav>

        {/* Hero area */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 mb-10">
          {/* Image */}
          <div className={`lg:col-span-3 h-64 md:h-80 rounded-2xl bg-gradient-to-br ${grad} flex items-center justify-center relative`}>
            <div className="text-center">
              <p className="text-foreground/30 text-sm uppercase tracking-widest">{car.brand}</p>
              <p className="text-foreground/60 text-3xl font-bold mt-2">{car.model}</p>
              <p className="text-foreground/30 text-sm mt-2">{car.year}</p>
            </div>
            {car.is_our_pick && (
              <div className="absolute top-4 right-4 flex items-center gap-1 bg-amber-500/90 text-black text-sm font-bold px-3 py-1.5 rounded-full shadow-lg">
                <Star className="h-4 w-4 fill-current" />
                Our Pick
              </div>
            )}
            {car.fuel_type === "Electric" && (
              <div className="absolute top-4 left-4 bg-green-500/90 text-black text-sm font-bold px-3 py-1.5 rounded-full">⚡ Electric</div>
            )}
            {car.fuel_type === "Hybrid" && (
              <div className="absolute top-4 left-4 bg-emerald-600/90 text-white text-sm font-bold px-3 py-1.5 rounded-full">🌿 Hybrid</div>
            )}
          </div>

          {/* Price + Deal */}
          <div className="lg:col-span-2 flex flex-col gap-4">
            {/* Name + badges */}
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${CATEGORY_COLORS[car.category] || ""}`}>
                  {CATEGORY_ICONS[car.category]} {car.category}
                </span>
                {car.body_type && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-muted/50 text-foreground/60">{car.body_type}</span>
                )}
              </div>
              <h1 className="font-serif text-2xl md:text-3xl font-bold">{car.name}</h1>
            </div>

            {/* MSRP */}
            <div className="p-4 rounded-xl bg-muted/20 border border-border/50">
              <p className="text-xs text-foreground/50 uppercase tracking-wider mb-1">MSRP</p>
              <p className="text-2xl font-bold">{formatMsrp(car.msrp_low, car.msrp_high)}</p>
            </div>

            {/* Lease deal card */}
            {car.lease_monthly && (
              <div className="p-4 rounded-xl bg-primary/5 border border-primary/20">
                <p className="text-xs text-primary/70 uppercase tracking-wider mb-2 font-medium">Current Lease Deal</p>
                <p className="text-3xl font-bold text-primary">{formatPrice(car.lease_monthly)}<span className="text-base font-normal text-foreground/50">/mo</span></p>
                <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-xs text-foreground/50">
                  {car.lease_due_at_signing && <span>{formatPrice(car.lease_due_at_signing)} due at signing</span>}
                  {car.lease_term && <span>{car.lease_term} months</span>}
                  {car.lease_miles_per_year && <span>{car.lease_miles_per_year.toLocaleString()} mi/yr</span>}
                </div>
                {car.lease_source && (
                  <p className="text-xs text-foreground/40 mt-2">via {car.lease_source}{car.lease_expires ? ` · Expires ${car.lease_expires}` : ""}</p>
                )}
                <a
                  href={edmundsSearch}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground font-semibold text-sm py-2.5 px-4 rounded-lg hover:bg-primary/90 transition-colors"
                >
                  Get This Deal
                  <ExternalLink className="h-4 w-4" />
                </a>
              </div>
            )}

            <ShareButtons title={car.name} url={pageUrl} />
          </div>
        </div>

        {/* Specs Grid */}
        <section className="mb-10">
          <h2 className="font-serif text-xl font-bold mb-4">Key Specs</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {car.mpg && <SpecTile icon={<Fuel className="h-5 w-5" />} label={car.fuel_type === "Electric" ? "Range" : "Fuel Economy"} value={car.mpg} />}
            {car.seating && <SpecTile icon={<Users className="h-5 w-5" />} label="Seating" value={`${car.seating} passengers`} />}
            {car.cargo_cu_ft && <SpecTile icon={<Package className="h-5 w-5" />} label="Cargo" value={`${car.cargo_cu_ft} cu ft`} />}
            {car.safety_rating && <SpecTile icon={<Shield className="h-5 w-5" />} label="Safety" value={car.safety_rating} />}
            {car.fuel_type && <SpecTile icon={<Fuel className="h-5 w-5" />} label="Fuel Type" value={car.fuel_type} />}
            {car.body_type && <SpecTile icon={<span className="text-lg">{CATEGORY_ICONS[car.category] || "🚗"}</span>} label="Body Type" value={car.body_type} />}
          </div>
        </section>

        {/* NRI Take */}
        {car.nri_take && (
          <section className="mb-10 p-6 rounded-2xl bg-gradient-to-br from-primary/5 to-primary/10 border border-primary/10">
            <h2 className="font-serif text-xl font-bold mb-3 flex items-center gap-2">
              🇮🇳 The NRI Take
            </h2>
            <p className="text-foreground/80 leading-relaxed">{car.nri_take}</p>
          </section>
        )}

        {/* Pros & Cons */}
        {(car.pros?.length || car.cons?.length) && (
          <section className="mb-10">
            <h2 className="font-serif text-xl font-bold mb-4">Pros & Cons</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {car.pros?.length ? (
                <div className="p-5 rounded-xl bg-green-950/20 border border-green-900/30">
                  <h3 className="text-sm font-bold text-green-400 uppercase tracking-wider mb-3">Pros</h3>
                  <ul className="space-y-2.5">
                    {car.pros.map((pro, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-foreground/80">
                        <Check className="h-4 w-4 text-green-400 flex-shrink-0 mt-0.5" />
                        {pro}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {car.cons?.length ? (
                <div className="p-5 rounded-xl bg-red-950/20 border border-red-900/30">
                  <h3 className="text-sm font-bold text-red-400 uppercase tracking-wider mb-3">Cons</h3>
                  <ul className="space-y-2.5">
                    {car.cons.map((con, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-foreground/80">
                        <XIcon className="h-4 w-4 text-red-400 flex-shrink-0 mt-0.5" />
                        {con}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          </section>
        )}

        {/* Similar Cars */}
        {similar.length > 0 && (
          <section className="mb-10">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-serif text-xl font-bold">Similar Cars</h2>
              <Link to={`/cars?category=${car.category}`} className="text-sm text-primary hover:underline">
                View all {car.category} →
              </Link>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {similar.map((s) => (
                <SimilarCard key={s.id} car={s} />
              ))}
            </div>
          </section>
        )}
      </main>

      <SiteFooter />
    </>
  );
}
