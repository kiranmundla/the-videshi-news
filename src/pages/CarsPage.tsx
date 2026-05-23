import { useState, useEffect, useMemo, useRef, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useNavigate } from "react-router-dom";
import {
  Search, X, Star, Fuel, Users, ChevronRight, ChevronLeft,
  BookOpen, ArrowRight, SlidersHorizontal, Plus, Check, BarChart3,
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
  { title: "First Car in America", desc: "Complete guide for H-1B, L-1 & F-1 visa holders — credit, financing, insurance.", emoji: "🇺🇸", href: "/cars/guide/first-car-in-america", tag: "Essential" },
  { title: "Best Family SUVs for Desi Families", desc: "Top 3-row SUVs ranked for space, comfort when parents visit, and road trips.", emoji: "👨‍👩‍👧‍👦", href: "/cars/guide/best-family-suvs", tag: "Popular" },
  { title: "Lease vs Buy", desc: "Which makes more sense? A practical breakdown for the Indian mindset.", emoji: "📊", href: "/cars/guide/lease-vs-buy", tag: "Guide" },
  { title: "Cars Under $30K", desc: "Best reliable picks for new immigrants building credit.", emoji: "💰", href: "/cars/guide/best-cars-under-30k", tag: "Budget" },
  { title: "Insurance for New Immigrants", desc: "How to get coverage with no US driving history.", emoji: "🛡️", href: "/cars/guide/insurance-for-new-immigrants", tag: "Essential" },
  { title: "EVs Worth Switching To", desc: "Tax credits, charging logistics, and the best electric picks for 2026.", emoji: "⚡", href: "/cars/guide/best-evs-2026", tag: "Trending" },
  { title: "India vs US: Driving Differences", desc: "Everything that's different — from road rules to highway culture.", emoji: "🔄", href: "/cars/guide/india-vs-us-driving", tag: "New" },
  { title: "Best Cars for Tech Professionals", desc: "Smart picks for Bay Area, Seattle & Austin commuters.", emoji: "💻", href: "/cars/guide/cars-for-tech-professionals", tag: "Lifestyle" },
];

const TAG_COLORS: Record<string, string> = {
  Essential: "bg-blue-100 text-blue-700",
  Popular: "bg-amber-100 text-amber-700",
  Guide: "bg-purple-100 text-purple-700",
  Budget: "bg-green-100 text-green-700",
  Trending: "bg-rose-100 text-rose-700",
  New: "bg-cyan-100 text-cyan-700",
  Lifestyle: "bg-indigo-100 text-indigo-700",
};

const PRICE_RANGES = [
  { label: "Any Price", min: 0, max: Infinity },
  { label: "Under $25K", min: 0, max: 25000 },
  { label: "$25K – $35K", min: 25000, max: 35000 },
  { label: "$35K – $50K", min: 35000, max: 50000 },
  { label: "$50K – $75K", min: 50000, max: 75000 },
  { label: "$75K+", min: 75000, max: Infinity },
];

const FUEL_TYPES = ["All", "Gas", "Hybrid", "Electric"];
const SEATING_OPTIONS = [
  { label: "Any", min: 0, max: 99 },
  { label: "4–5 seats", min: 4, max: 5 },
  { label: "6–7 seats", min: 6, max: 7 },
  { label: "7+ seats", min: 7, max: 99 },
];

/* ------------------------------------------------------------------ */
/* Car Card                                                           */
/* ------------------------------------------------------------------ */
function CarCard({
  car,
  compareIds,
  onToggleCompare,
}: {
  car: Car;
  compareIds: Set<string>;
  onToggleCompare: (car: Car) => void;
}) {
  const grad = brandGradient(car.brand);
  const isSelected = compareIds.has(car.id);
  return (
    <div className="relative group h-full">
      <Link to={`/cars/${car.slug}`} className="block h-full">
        <article className="flex flex-col bg-card border border-border rounded-xl overflow-hidden hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5 h-full">
          {/* Image */}
          <div className={`relative w-full h-44 bg-gradient-to-br ${grad} flex items-center justify-center overflow-hidden`}>
            {car.image_url ? (
              <img
                src={car.image_url}
                alt={car.name}
                className="w-full h-full object-contain p-2"
                loading="lazy"
              />
            ) : (
              <div className="text-center px-4">
                <p className="text-foreground/40 text-xs uppercase tracking-widest">{car.brand}</p>
                <p className="text-foreground/70 text-lg font-bold mt-1">{car.model}</p>
              </div>
            )}
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
                  {car.seating} seats
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
      {/* Compare toggle button */}
      <button
        onClick={(e) => { e.preventDefault(); e.stopPropagation(); onToggleCompare(car); }}
        className={`absolute bottom-3 right-3 z-10 h-7 w-7 rounded-full flex items-center justify-center transition-all duration-150 ${
          isSelected
            ? "bg-primary text-primary-foreground shadow-lg shadow-primary/30"
            : "bg-card/80 border border-border text-foreground/40 opacity-0 group-hover:opacity-100 hover:border-primary/50 hover:text-primary"
        }`}
        title={isSelected ? "Remove from comparison" : "Add to compare"}
      >
        {isSelected ? <Check className="h-3.5 w-3.5" /> : <Plus className="h-3.5 w-3.5" />}
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Horizontal scroll row                                              */
/* ------------------------------------------------------------------ */
function CarRow({ cars, compareIds, onToggleCompare }: { cars: Car[]; compareIds: Set<string>; onToggleCompare: (car: Car) => void }) {
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
    ref.current?.scrollBy({ left: dir === "left" ? -300 : 300, behavior: "smooth" });
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
          <div key={car.id} className="w-[280px] shrink-0 snap-start">
            <CarCard car={car} compareIds={compareIds} onToggleCompare={onToggleCompare} />
          </div>
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
function CarGrid({ cars, compareIds, onToggleCompare }: { cars: Car[]; compareIds: Set<string>; onToggleCompare: (car: Car) => void }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      {cars.map((car) => (
        <CarCard key={car.id} car={car} compareIds={compareIds} onToggleCompare={onToggleCompare} />
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Guide Card                                                         */
/* ------------------------------------------------------------------ */
function GuideCard({ title, desc, emoji, href, tag }: typeof GUIDES[number]) {
  return (
    <Link to={href} className="block group">
      <div className="relative flex items-start gap-3.5 p-4 bg-card border border-border rounded-xl hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5 h-full">
        {tag && (
          <span className={`absolute top-2.5 right-2.5 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${TAG_COLORS[tag] || "bg-muted text-foreground/50"}`}>
            {tag}
          </span>
        )}
        <span className="text-2xl flex-shrink-0 mt-0.5">{emoji}</span>
        <div className="flex-1 min-w-0 pr-12">
          <h3 className="font-semibold text-sm group-hover:text-primary transition-colors">{title}</h3>
          <p className="text-xs text-foreground/50 mt-0.5 line-clamp-2">{desc}</p>
        </div>
        <ChevronRight className="h-4 w-4 text-foreground/30 group-hover:text-primary transition-colors flex-shrink-0 mt-1 absolute right-4 bottom-4" />
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
/* Filter Select (custom styled)                                      */
/* ------------------------------------------------------------------ */
function FilterSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: { label: string; value: string }[];
  onChange: (v: string) => void;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-[11px] uppercase tracking-wider text-foreground/40 font-medium">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="px-3 py-2 text-sm rounded-lg border border-border bg-card text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 appearance-none cursor-pointer min-w-[140px]"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Compare floating bar                                               */
/* ------------------------------------------------------------------ */
function CompareBar({
  cars,
  onRemove,
  onClear,
}: {
  cars: Car[];
  onRemove: (id: string) => void;
  onClear: () => void;
}) {
  const navigate = useNavigate();
  if (cars.length === 0) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-card/95 backdrop-blur-lg border-t border-primary/20 shadow-2xl shadow-black/40">
      <div className="container py-3 flex items-center gap-4">
        <div className="flex items-center gap-2 flex-1 overflow-x-auto scrollbar-none">
          <BarChart3 className="h-5 w-5 text-primary flex-shrink-0" />
          {cars.map((car) => (
            <div key={car.id} className="flex items-center gap-2 bg-muted/30 border border-border rounded-full pl-3 pr-1.5 py-1 shrink-0">
              <span className="text-sm font-medium whitespace-nowrap">{car.brand} {car.model}</span>
              <button
                onClick={() => onRemove(car.id)}
                className="h-5 w-5 rounded-full flex items-center justify-center hover:bg-red-500/20 transition-colors"
              >
                <X className="h-3 w-3 text-foreground/50 hover:text-red-400" />
              </button>
            </div>
          ))}
          {cars.length < 3 && (
            <span className="text-xs text-foreground/40 shrink-0">
              Add {3 - cars.length} more to compare
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={onClear}
            className="text-xs text-foreground/50 hover:text-foreground transition-colors px-2 py-1"
          >
            Clear
          </button>
          <button
            onClick={() => navigate(`/cars/compare?ids=${cars.map((c) => c.id).join(",")}`)}
            disabled={cars.length < 2}
            className="flex items-center gap-2 bg-primary text-primary-foreground font-semibold text-sm py-2 px-5 rounded-full hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Compare {cars.length} cars
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
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

  // Advanced filters
  const [filterPrice, setFilterPrice] = useState("0");
  const [filterFuel, setFilterFuel] = useState("All");
  const [filterSeating, setFilterSeating] = useState("0");
  const [showFilters, setShowFilters] = useState(false);

  // Compare state
  const [compareCars, setCompareCars] = useState<Car[]>([]);
  const compareIds = useMemo(() => new Set(compareCars.map((c) => c.id)), [compareCars]);

  const toggleCompare = useCallback((car: Car) => {
    setCompareCars((prev) => {
      if (prev.find((c) => c.id === car.id)) return prev.filter((c) => c.id !== car.id);
      if (prev.length >= 3) return prev;
      return [...prev, car];
    });
  }, []);

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

  // Top lease deals — sorted by monthly payment, show top 8
  const topDeals = useMemo(() =>
    allCars
      .filter((c) => c.lease_monthly)
      .sort((a, b) => (a.lease_monthly ?? 0) - (b.lease_monthly ?? 0))
      .slice(0, 8),
    [allCars]
  );

  // Check if any advanced filter is active
  const hasAdvancedFilter = filterPrice !== "0" || filterFuel !== "All" || filterSeating !== "0";

  // Filtered view (when a specific category, search, or advanced filter is active)
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
    // Advanced filters
    if (filterPrice !== "0") {
      const range = PRICE_RANGES[Number(filterPrice)];
      if (range) {
        list = list.filter((c) => {
          const price = c.msrp_low ?? c.msrp_high ?? 0;
          return price >= range.min && price < range.max;
        });
      }
    }
    if (filterFuel !== "All") {
      list = list.filter((c) => c.fuel_type === filterFuel);
    }
    if (filterSeating !== "0") {
      const opt = SEATING_OPTIONS[Number(filterSeating)];
      if (opt) {
        list = list.filter((c) => c.seating && c.seating >= opt.min && c.seating <= opt.max);
      }
    }
    return list;
  }, [allCars, grouped, evCars, activeFilter, debouncedSearch, filterPrice, filterFuel, filterSeating]);

  const isFilteredView = activeFilter !== "All" || debouncedSearch.length > 0 || hasAdvancedFilter;

  // Stats
  const stats = useMemo(() => {
    const brands = new Set(allCars.map((c) => c.brand));
    const withDeals = allCars.filter((c) => c.lease_monthly).length;
    return { total: allCars.length, brands: brands.size, deals: withDeals };
  }, [allCars]);

  const clearAdvancedFilters = () => {
    setFilterPrice("0");
    setFilterFuel("All");
    setFilterSeating("0");
  };

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
        {/* ── Hero ─────────────────────────────────────────────── */}
        <section className="relative mb-10 -mx-4 px-4 py-12 md:py-16 rounded-2xl overflow-hidden bg-[#1a1a2e] border border-[#2a2a4a]/40">
          {/* Decorative elements */}
          <div className="absolute inset-0 opacity-[0.06]" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")" }} />
          <div className="absolute top-0 right-0 w-64 h-64 bg-red-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-amber-500/8 rounded-full blur-3xl" />

          <div className="relative z-10 max-w-3xl">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs font-bold uppercase tracking-widest text-amber-300 bg-amber-500/15 px-3 py-1 rounded-full">
                🇮🇳 The Videshi Auto
              </span>
            </div>
            <h1 className="font-serif text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight leading-[1.1] text-white">
              American Roads.<br />
              <span className="text-red-400">Indian Priorities.</span>
            </h1>
            <p className="text-white/70 mt-4 text-lg md:text-xl max-w-2xl leading-relaxed">
              The smartest car picks for the Indian diaspora — from first-time H‑1B buyers to family upgrades and luxury dreams.
            </p>
            <div className="flex flex-wrap items-center gap-4 mt-6 text-sm text-white/50">
              <span className="flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-400/70" />
                {stats.total} vehicles reviewed
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-400/70" />
                {stats.brands} brands
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-400/70" />
                Lease deals updated weekly
              </span>
            </div>
          </div>
        </section>

        {/* ── Top Lease Deals ──────────────────────────────────── */}
        {topDeals.length > 0 && (
          <section className="mb-10">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-xl">🏷️</span>
                <h2 className="font-serif text-lg font-bold">Best Lease Deals This Month</h2>
              </div>
              <span className="text-xs text-foreground/40">Updated weekly</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {topDeals.map((car) => (
                <Link key={car.id} to={`/cars/${car.slug}`} className="block group">
                  <div className="p-4 bg-card border border-primary/20 rounded-xl hover:border-primary/40 transition-all hover:shadow-lg hover:shadow-primary/5">
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`w-14 h-14 rounded-lg bg-gradient-to-br ${brandGradient(car.brand)} flex items-center justify-center overflow-hidden flex-shrink-0`}>
                        {car.image_url ? (
                          <img src={car.image_url} alt={car.name} className="w-full h-full object-contain p-1" loading="lazy" />
                        ) : (
                          <span className="text-xs font-bold text-foreground/40">{car.brand.slice(0, 3)}</span>
                        )}
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold group-hover:text-primary transition-colors truncate">{car.name}</p>
                        <p className="text-xs text-foreground/50">{formatMsrp(car.msrp_low, car.msrp_high)}</p>
                      </div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-primary/5 border border-primary/10">
                      <p className="text-lg font-bold text-primary">{formatPrice(car.lease_monthly!)}<span className="text-xs font-normal text-foreground/50">/mo</span></p>
                      <p className="text-xs text-foreground/40 mt-0.5">${car.lease_due_at_signing?.toLocaleString()} due · {car.lease_term} months</p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* ── Buyer's Guides ──────────────────────────────────── */}
        <section className="mb-10">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="h-5 w-5 text-primary" />
            <h2 className="font-serif text-lg font-bold">NRI Buyer's Guides</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {GUIDES.map((g) => (
              <GuideCard key={g.href} {...g} />
            ))}
          </div>
        </section>

        {/* ── Stats + Category pills + Search ─────────────────── */}
        <div className="flex flex-wrap gap-3 text-sm text-foreground/50 mb-4">
          <span>{stats.total} vehicles</span>
          <span className="text-foreground/20">·</span>
          <span>{stats.brands} brands</span>
          <span className="text-foreground/20">·</span>
          <span>{stats.deals} with lease deals</span>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 mb-4">
          {/* Category pills */}
          <div className="flex gap-2 overflow-x-auto scrollbar-none -mx-1 px-1">
            {allCats.map((cat) => {
              const active = activeFilter === cat;
              const icon = cat === "All" ? "🔥" : CATEGORY_ICONS[cat] || "";
              return (
                <button
                  key={cat}
                  onClick={() => { setActiveFilter(cat); setSearch(""); clearAdvancedFilters(); }}
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

          {/* Search + filter toggle */}
          <div className="flex items-center gap-2 flex-1 sm:ml-auto sm:max-w-md">
            <div className="relative flex-1">
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
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium rounded-full border transition-all duration-150 shrink-0 ${
                showFilters || hasAdvancedFilter
                  ? "bg-primary/10 border-primary/40 text-primary"
                  : "border-border text-foreground/70 hover:text-primary hover:border-primary/50"
              }`}
            >
              <SlidersHorizontal className="h-4 w-4" />
              Filters
              {hasAdvancedFilter && (
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
              )}
            </button>
          </div>
        </div>

        {/* ── Advanced Filters ────────────────────────────────── */}
        {showFilters && (
          <div className="flex flex-wrap items-end gap-4 mb-6 p-4 bg-card border border-border rounded-xl">
            <FilterSelect
              label="Price Range"
              value={filterPrice}
              options={PRICE_RANGES.map((r, i) => ({ label: r.label, value: String(i) }))}
              onChange={setFilterPrice}
            />
            <FilterSelect
              label="Fuel Type"
              value={filterFuel}
              options={FUEL_TYPES.map((f) => ({ label: f, value: f }))}
              onChange={setFilterFuel}
            />
            <FilterSelect
              label="Seating"
              value={filterSeating}
              options={SEATING_OPTIONS.map((s, i) => ({ label: s.label, value: String(i) }))}
              onChange={setFilterSeating}
            />
            {hasAdvancedFilter && (
              <button
                onClick={clearAdvancedFilters}
                className="text-sm text-primary hover:text-primary/80 font-medium transition-colors pb-2"
              >
                Clear filters
              </button>
            )}
            <div className="ml-auto text-sm text-foreground/40 pb-2">
              {filtered.length} result{filtered.length !== 1 ? "s" : ""}
            </div>
          </div>
        )}

        {/* ── Content ─────────────────────────────────────────── */}
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
            <CarGrid cars={filtered} compareIds={compareIds} onToggleCompare={toggleCompare} />
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
                  <CarRow cars={cars} compareIds={compareIds} onToggleCompare={toggleCompare} />
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

        {/* Bottom spacer for compare bar */}
        {compareCars.length > 0 && <div className="h-20" />}
      </main>

      {/* Compare floating bar */}
      <CompareBar
        cars={compareCars}
        onRemove={(id) => setCompareCars((prev) => prev.filter((c) => c.id !== id))}
        onClear={() => setCompareCars([])}
      />

      <SiteFooter />
    </>
  );
}
