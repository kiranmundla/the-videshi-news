import { useState, useEffect, useCallback, useMemo, useRef } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import {
  Search, X, Star, Fuel, Users, ChevronRight, ChevronLeft,
  BookOpen, ArrowRight,
} from "lucide-react";
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
/* Section order + display names + descriptions                       */
/* ------------------------------------------------------------------ */
const SECTIONS = [
  { key: "SUV",     label: "Popular SUVs",      desc: "The workhorses of desi families — from daily commutes to cross-country road trips" },
  { key: "Sedan",   label: "Sedans",             desc: "Reliable, fuel-efficient, and perfect for your first car in America" },
  { key: "Minivan", label: "Minivans",           desc: "Because family means 7 people, 4 suitcases, and a pressure cooker" },
  { key: "Luxury",  label: "Luxury",             desc: "From aspirational to arrived — the cars that say you've made it" },
  { key: "EV",      label: "Electric Vehicles",  desc: "The future of driving — tax credits, low running costs, and zero emissions" },
] as const;

const GUIDES = [
  {
    title: "Your First Car in America",
    desc: "Step-by-step for H-1B and L-1 holders — credit, insurance, dealers.",
    emoji: "🇺🇸",
    href: "/cars/guide/first-car-in-america",
  },
  {
    title: "Lease vs Buy",
    desc: "Which makes more sense? A practical breakdown for the Indian mindset.",
    emoji: "📊",
    href: "/cars/guide/lease-vs-buy",
  },
  {
    title: "Insurance for New Immigrants",
    desc: "How to get coverage with no US driving history.",
    emoji: "🛡️",
    href: "/cars/guide/insurance-for-new-immigrants",
  },
  {
    title: "Best Family SUVs",
    desc: "Top 3-row SUVs ranked for space, safety, and road trip readiness.",
    emoji: "👨‍👩‍👧‍👦",
    href: "/cars/guide/best-family-suvs",
  },
];

/* ------------------------------------------------------------------ */
/* Small Car Card (for horizontal scroll rows)                        */
/* ------------------------------------------------------------------ */
function CarCard({ car, compact }: { car: Car; compact?: boolean }) {
  const grad = brandGradient(car.brand);
  return (
    <Link to={`/cars/${car.slug}`} className={`block group ${compact ? "w-[260px] shrink-0 snap-start" : ""}`}>
      <article className="flex flex-col bg-card border border-border rounded-xl overflow-hidden hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5 h-full">
        {/* Image placeholder */}
        <div className={`relative w-full ${compact ? "h-36" : "h-44"} bg-gradient-to-br ${grad} flex items-center justify-center`}>
          <div className="text-center px-4">
            <p className="text-foreground/40 text-xs uppercase tracking-widest">{car.brand}</p>
            <p className="text-foreground/70 text-lg font-bold mt-1">{car.model}</p>
          </div>
          {car.is_our_pick && (
            <div className="absolute top-2.5 right-2.5 flex items-center gap-1 bg-amber-500/90 text-black text-xs font-bold px-2 py-0.5 rounded-full shadow-md">
              <Star className="h-3 w-3 fill-current" />
              Our Pick
            </div>
          )}
          {car.fuel_type === "Electric" && (
            <div className="absolute top-2.5 left-2.5 flex items-center gap-1 bg-green-500/90 text-black text-xs font-bold px-2 py-0.5 rounded-full">
              ⚡ EV
            </div>
          )}
          {car.fuel_type === "Hybrid" && (
            <div className="absolute top-2.5 left-2.5 flex items-center gap-1 bg-emerald-600/90 text-white text-xs font-bold px-2 py-0.5 rounded-full">
              🌿 Hybrid
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-3.5 flex flex-col flex-1 gap-1.5">
          <h3 className="font-semibold text-sm leading-snug group-hover:text-primary transition-colors line-clamp-2">
            {car.name}
          </h3>
          <p className="text-base font-bold text-foreground/90">
            {formatMsrp(car.msrp_low, car.msrp_high)}
          </p>

          {/* Specs */}
          <div className="flex flex-wrap items-center gap-2.5 text-xs text-foreground/50 mt-auto pt-1.5 border-t border-border/50">
            {car.mpg && (
              <span className="flex items-center gap-1">
                <Fuel className="h-3 w-3" />
                {car.mpg.includes("mi range") ? car.mpg : car.mpg.split("/")[0]?.trim()}
              </span>
            )}
            {car.seating && (
              <span className="flex items-center gap-1">
                <Users className="h-3 w-3" />
                {car.seating}
              </span>
            )}
          </div>

          {/* Lease deal */}
          {car.lease_monthly && (
            <div className="mt-1.5 p-2 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs font-semibold text-primary">
                {formatPrice(car.lease_monthly)}/mo
                <span className="font-normal text-foreground/50 ml-1">
                  · ${car.lease_due_at_signing?.toLocaleString()} due
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
/* Horizontally scrollable car row                                    */
/* ------------------------------------------------------------------ */
function CarRow({ cars }: { cars: Car[] }) {
  const ref = useRef<HTMLDivElement>(null);
  const [canLeft, setCanLeft] = useState(false);
  const [canRight, setCanRight] = useState(false);

  const checkScroll = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    setCanLeft(el.scrollLeft > 4);
    setCanRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 4);
  }, []);

  useEffect(() => {
    checkScroll();
    const el = ref.current;
    if (el) el.addEventListener("scroll", checkScroll, { passive: true });
    return () => el?.removeEventListener("scroll", checkScroll);
  }, [checkScroll, cars]);

  const scroll = (dir: "left" | "right") => {
    ref.current?.scrollBy({ left: dir === "left" ? -280 : 280, behavior: "smooth" });
  };

  return (
    <div className="relative group/row">
      {canLeft && (
        <button
          onClick={() => scroll("left")}
          className="hidden sm:flex absolute -left-3 top-1/2 -translate-y-1/2 z-10 h-9 w-9 items-center justify-center rounded-full bg-card border border-border shadow-lg hover:bg-primary/10 transition-colors"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
      )}
      <div
        ref={ref}
        className="flex gap-4 overflow-x-auto scrollbar-none snap-x snap-mandatory pb-2 -mx-1 px-1"
      >
        {cars.map((car) => (
          <CarCard key={car.id} car={car} compact />
        ))}
      </div>
      {canRight && (
        <button
          onClick={() => scroll("right")}
          className="hidden sm:flex absolute -right-3 top-1/2 -translate-y-1/2 z-10 h-9 w-9 items-center justify-center rounded-full bg-card border border-border shadow-lg hover:bg-primary/10 transition-colors"
        >
          <ChevronRight className="h-5 w-5" />
        </button>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Full grid (for filtered view)                                      */
/* ------------------------------------------------------------------ */
function CarGrid({ cars }: { cars: Car[] }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      {cars.map((car) => (
        <CarCard key={car.id} car={car} />
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Guide Card                                                         */
/* ------------------------------------------------------------------ */
function GuideCard({ title, desc, emoji, href }: typeof GUIDES[number]) {
  return (
    <Link to={href} className="block group">
      <div className="flex items-start gap-3.5 p-4 bg-card border border-border rounded-xl hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5">
        <span className="text-2xl flex-shrink-0 mt-0.5">{emoji}</span>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm group-hover:text-primary transition-colors">{title}</h3>
          <p className="text-xs text-foreground/50 mt-0.5 line-clamp-2">{desc}</p>
        </div>
        <ChevronRight className="h-4 w-4 text-foreground/30 group-hover:text-primary transition-colors flex-shrink-0 mt-1" />
      </div>
    </Link>
  );
}

/* ------------------------------------------------------------------ */
/* Section Header                                                     */
/* ------------------------------------------------------------------ */
function SectionHeader({
  icon,
  label,
  desc,
  count,
  onViewAll,
}: {
  icon: string;
  label: string;
  desc: string;
  count: number;
  onViewAll: () => void;
}) {
  return (
    <div className="flex items-end justify-between mb-4">
      <div>
        <h2 className="font-serif text-xl md:text-2xl font-bold flex items-center gap-2">
          <span>{icon}</span>
          {label}
          <span className="text-sm font-normal text-foreground/40 ml-1">({count})</span>
        </h2>
        <p className="text-sm text-foreground/50 mt-0.5">{desc}</p>
      </div>
      <button
        onClick={onViewAll}
        className="hidden sm:flex items-center gap-1 text-sm text-primary hover:text-primary/80 font-medium transition-colors shrink-0 ml-4"
      >
        View all <ArrowRight className="h-4 w-4" />
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* CarsPage                                                           */
/* ------------------------------------------------------------------ */
export default function CarsPage() {
  const [allCars, setAllCars] = useState<Car[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState<string>("All");
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  // Load all cars once
  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const data = await getCars();
        setAllCars(data);
      } catch (err) {
        console.error("Failed to load cars", err);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Group by category
  const grouped = useMemo(() => {
    const map: Record<string, Car[]> = {};
    for (const car of allCars) {
      if (!map[car.category]) map[car.category] = [];
      map[car.category].push(car);
    }
    return map;
  }, [allCars]);

  // EV group (cross-category by fuel_type)
  const evCars = useMemo(() => allCars.filter((c) => c.fuel_type === "Electric"), [allCars]);

  // Filtered view (when a specific category or search is active)
  const filtered = useMemo(() => {
    let list = allCars;
    if (activeFilter === "EV") {
      list = evCars;
    } else if (activeFilter !== "All") {
      list = grouped[activeFilter] || [];
    }
    if (debouncedSearch) {
      const q = debouncedSearch.toLowerCase();
      list = list.filter(
        (c) =>
          c.name.toLowerCase().includes(q) ||
          c.brand.toLowerCase().includes(q) ||
          c.model.toLowerCase().includes(q)
      );
    }
    return list;
  }, [allCars, grouped, evCars, activeFilter, debouncedSearch]);

  const isFilteredView = activeFilter !== "All" || debouncedSearch.length > 0;

  // Stats
  const stats = useMemo(() => {
    const brands = new Set(allCars.map((c) => c.brand));
    const withDeals = allCars.filter((c) => c.lease_monthly).length;
    return { total: allCars.length, brands: brands.size, deals: withDeals };
  }, [allCars]);

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
        <div className="mb-6">
          <h1 className="font-serif text-4xl md:text-5xl font-bold tracking-tight">Cars</h1>
          <p className="text-muted-foreground mt-2 text-lg">
            Your guide to buying the right car in America
          </p>
        </div>

        {/* Buyer's Guides — top of page */}
        <section className="mb-10">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="h-5 w-5 text-primary" />
            <h2 className="font-serif text-lg font-bold">Buyer's Guides</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {GUIDES.map((g) => (
              <GuideCard key={g.href} {...g} />
            ))}
          </div>
        </section>

        {/* Stats + Filters */}
        <div className="flex flex-wrap gap-3 text-sm text-foreground/50 mb-4">
          <span>{stats.total} vehicles</span>
          <span className="text-foreground/20">·</span>
          <span>{stats.brands} brands</span>
          <span className="text-foreground/20">·</span>
          <span>{stats.deals} with lease deals</span>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 mb-8">
          {/* Category pills */}
          <div className="flex gap-2 overflow-x-auto scrollbar-none -mx-1 px-1">
            {allCats.map((cat) => {
              const active = activeFilter === cat;
              const icon = cat === "All" ? "🔥" : CATEGORY_ICONS[cat] || "";
              return (
                <button
                  key={cat}
                  onClick={() => { setActiveFilter(cat); setSearch(""); }}
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
              <button onClick={() => setSearch("")} className="absolute right-3 top-1/2 -translate-y-1/2">
                <X className="h-4 w-4 text-foreground/40" />
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : isFilteredView ? (
          /* Filtered view — flat grid */
          filtered.length === 0 ? (
            <div className="text-center py-20 text-foreground/50">
              <p className="text-4xl mb-3">🚗</p>
              <p className="text-lg font-medium">No cars found</p>
              <p className="text-sm mt-1">Try a different category or search term</p>
            </div>
          ) : (
            <CarGrid cars={filtered} />
          )
        ) : (
          /* Browse view — organized by sections */
          <div className="space-y-12">
            {SECTIONS.map((section) => {
              const sectionIcon = CATEGORY_ICONS[section.key] || "🚗";
              const cars = section.key === "EV" ? evCars : (grouped[section.key] || []);
              if (cars.length === 0) return null;
              return (
                <section key={section.key}>
                  <SectionHeader
                    icon={sectionIcon}
                    label={section.label}
                    desc={section.desc}
                    count={cars.length}
                    onViewAll={() => setActiveFilter(section.key)}
                  />
                  <CarRow cars={cars} />
                  {/* Mobile view-all link */}
                  <button
                    onClick={() => setActiveFilter(section.key)}
                    className="sm:hidden flex items-center gap-1 text-sm text-primary font-medium mt-3"
                  >
                    View all {section.label.toLowerCase()} <ArrowRight className="h-4 w-4" />
                  </button>
                </section>
              );
            })}
          </div>
        )}
      </main>

      <SiteFooter />
    </>
  );
}
