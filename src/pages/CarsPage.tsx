import { useState, useEffect, useCallback, useMemo } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { Search, X, Star, Fuel, Users, ChevronRight } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  Car,
  getCars,
  CAR_CATEGORIES,
  CATEGORY_COLORS,
  CATEGORY_ICONS,
  formatMsrp,
  formatPrice,
  brandGradient,
} from "@/lib/cars";

/* ------------------------------------------------------------------ */
/* Car Card                                                           */
/* ------------------------------------------------------------------ */
function CarCard({ car }: { car: Car }) {
  const grad = brandGradient(car.brand);
  return (
    <Link to={`/cars/${car.slug}`} className="block group">
      <article className="flex flex-col bg-card border border-border rounded-xl overflow-hidden hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5 h-full">
        {/* Image placeholder */}
        <div className={`relative w-full h-44 bg-gradient-to-br ${grad} flex items-center justify-center`}>
          <div className="text-center px-4">
            <p className="text-foreground/40 text-xs uppercase tracking-widest">{car.brand}</p>
            <p className="text-foreground/70 text-lg font-bold mt-1">{car.model}</p>
          </div>
          {car.is_our_pick && (
            <div className="absolute top-3 right-3 flex items-center gap-1 bg-amber-500/90 text-black text-xs font-bold px-2.5 py-1 rounded-full shadow-md">
              <Star className="h-3 w-3 fill-current" />
              Our Pick
            </div>
          )}
          {car.fuel_type === "Electric" && (
            <div className="absolute top-3 left-3 flex items-center gap-1 bg-green-500/90 text-black text-xs font-bold px-2.5 py-1 rounded-full">
              ⚡ EV
            </div>
          )}
          {car.fuel_type === "Hybrid" && (
            <div className="absolute top-3 left-3 flex items-center gap-1 bg-emerald-600/90 text-white text-xs font-bold px-2.5 py-1 rounded-full">
              🌿 Hybrid
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-4 flex flex-col flex-1 gap-2">
          {/* Category + Body Type */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${CATEGORY_COLORS[car.category] || "bg-muted text-muted-foreground"}`}>
              {CATEGORY_ICONS[car.category] || "🚗"} {car.category}
            </span>
            {car.body_type && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-muted/50 text-foreground/60">
                {car.body_type}
              </span>
            )}
          </div>

          {/* Name + MSRP */}
          <h3 className="font-semibold text-base leading-snug group-hover:text-primary transition-colors">
            {car.name}
          </h3>
          <p className="text-lg font-bold text-foreground/90">
            {formatMsrp(car.msrp_low, car.msrp_high)}
          </p>

          {/* Key specs row */}
          <div className="flex flex-wrap items-center gap-3 text-xs text-foreground/50 mt-auto pt-2 border-t border-border/50">
            {car.mpg && (
              <span className="flex items-center gap-1">
                <Fuel className="h-3 w-3" />
                {car.mpg.includes("mi range") ? car.mpg : car.mpg.split("/")[0]?.trim()}
              </span>
            )}
            {car.seating && (
              <span className="flex items-center gap-1">
                <Users className="h-3 w-3" />
                {car.seating} seats
              </span>
            )}
          </div>

          {/* Lease deal */}
          {car.lease_monthly && (
            <div className="mt-2 p-2.5 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs text-foreground/50 mb-0.5">Lease from</p>
              <p className="text-sm font-bold text-primary">
                {formatPrice(car.lease_monthly)}/mo
                <span className="font-normal text-foreground/50 ml-1.5">
                  ${car.lease_due_at_signing?.toLocaleString()} due
                </span>
              </p>
            </div>
          )}
        </div>
      </article>
    </Link>
  );
}

/* ------------------------------------------------------------------ */
/* Guide Card                                                         */
/* ------------------------------------------------------------------ */
function GuideCard({
  title,
  desc,
  emoji,
  href,
}: {
  title: string;
  desc: string;
  emoji: string;
  href: string;
}) {
  return (
    <Link to={href} className="block group">
      <div className="flex items-start gap-4 p-5 bg-card border border-border rounded-xl hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5">
        <span className="text-3xl flex-shrink-0">{emoji}</span>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-base group-hover:text-primary transition-colors">{title}</h3>
          <p className="text-sm text-foreground/50 mt-1">{desc}</p>
        </div>
        <ChevronRight className="h-5 w-5 text-foreground/30 group-hover:text-primary transition-colors flex-shrink-0 mt-0.5" />
      </div>
    </Link>
  );
}

/* ------------------------------------------------------------------ */
/* CarsPage                                                           */
/* ------------------------------------------------------------------ */
export default function CarsPage() {
  const [cars, setCars] = useState<Car[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState<string>("All");
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getCars({
        category: category === "All" ? undefined : category,
        search: debouncedSearch || undefined,
      });
      setCars(data);
    } catch (err) {
      console.error("Failed to load cars", err);
    } finally {
      setLoading(false);
    }
  }, [category, debouncedSearch]);

  useEffect(() => {
    load();
  }, [load]);

  // Stats
  const stats = useMemo(() => {
    const brands = new Set(cars.map((c) => c.brand));
    const withDeals = cars.filter((c) => c.lease_monthly).length;
    return { total: cars.length, brands: brands.size, deals: withDeals };
  }, [cars]);

  const allCats = ["All", ...CAR_CATEGORIES];

  return (
    <>
      <Helmet>
        <title>Cars — Best Cars for Indian Americans | The Videshi</title>
        <meta
          name="description"
          content="Find the best cars, lease deals, and buyer's guides for the Indian diaspora in America. SUVs, sedans, minivans, luxury cars — curated for NRI families."
        />
        <meta property="og:title" content="Cars — The Videshi" />
        <meta property="og:description" content="Your guide to buying the right car in America. Curated for the Indian community." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://www.thevideshi.com/cars" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8">
        {/* Hero */}
        <div className="mb-8">
          <h1 className="font-serif text-4xl md:text-5xl font-bold tracking-tight">Cars</h1>
          <p className="text-muted-foreground mt-2 text-lg">
            Your guide to buying the right car in America
          </p>
        </div>

        {/* Stats bar */}
        <div className="flex flex-wrap gap-4 text-sm text-foreground/60 mb-6">
          <span>{stats.total} vehicles</span>
          <span className="text-foreground/20">·</span>
          <span>{stats.brands} brands</span>
          <span className="text-foreground/20">·</span>
          <span>{stats.deals} with lease deals</span>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-3 mb-8">
          {/* Category pills */}
          <div className="flex gap-2 overflow-x-auto scrollbar-none -mx-1 px-1">
            {allCats.map((cat) => {
              const active = category === cat;
              const icon = cat === "All" ? "🔥" : CATEGORY_ICONS[cat] || "";
              return (
                <button
                  key={cat}
                  onClick={() => setCategory(cat)}
                  className={`shrink-0 px-3.5 py-2 text-sm font-medium rounded-full border transition-all duration-150 ${
                    active
                      ? "bg-primary text-primary-foreground border-primary shadow-md shadow-primary/20"
                      : "border-border text-foreground/70 hover:text-primary hover:border-primary/50"
                  }`}
                >
                  {icon && <span className="mr-1">{icon}</span>}
                  {cat}
                </button>
              );
            })}
          </div>

          {/* Search */}
          <div className="relative flex-1 sm:max-w-xs sm:ml-auto">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground/40" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search brand or model…"
              className="w-full pl-9 pr-8 py-2 rounded-full border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
            {search && (
              <button
                onClick={() => setSearch("")}
                className="absolute right-3 top-1/2 -translate-y-1/2"
              >
                <X className="h-4 w-4 text-foreground/40" />
              </button>
            )}
          </div>
        </div>

        {/* Car grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : cars.length === 0 ? (
          <div className="text-center py-20 text-foreground/50">
            <p className="text-4xl mb-3">🚗</p>
            <p className="text-lg font-medium">No cars found</p>
            <p className="text-sm mt-1">Try a different category or search term</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {cars.map((car) => (
              <CarCard key={car.id} car={car} />
            ))}
          </div>
        )}

        {/* Buyer's Guides */}
        <section className="mt-16 pt-10 border-t border-border/50">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="font-serif text-2xl font-bold">Buyer's Guides</h2>
              <p className="text-sm text-foreground/50 mt-1">Practical guides for buying a car in America</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <GuideCard
              title="Your First Car in America"
              desc="Step-by-step guide for H-1B and L-1 visa holders — credit, insurance, dealers, and more."
              emoji="🇺🇸"
              href="/cars/guide/first-car-in-america"
            />
            <GuideCard
              title="Lease vs Buy"
              desc="Which makes more sense for you? A practical comparison for the Indian mindset."
              emoji="📊"
              href="/cars/guide/lease-vs-buy"
            />
            <GuideCard
              title="Insurance for New Immigrants"
              desc="How to get car insurance with no US driving history — providers, tips, and savings."
              emoji="🛡️"
              href="/cars/guide/insurance-for-new-immigrants"
            />
            <GuideCard
              title="Best Family SUVs"
              desc="Top 3-row SUVs ranked for desi families — space, safety, value, and road trip readiness."
              emoji="👨‍👩‍👧‍👦"
              href="/cars/guide/best-family-suvs"
            />
          </div>
        </section>
      </main>

      <SiteFooter />
    </>
  );
}
