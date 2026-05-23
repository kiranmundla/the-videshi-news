import { useState, useEffect, useMemo } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import {
  ChevronLeft, Fuel, Users, Star, ArrowUpDown, ExternalLink,
} from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  Car, getCars, formatMsrp, formatPrice, brandGradient, CATEGORY_ICONS,
} from "@/lib/cars";

type SortKey = "monthly" | "due" | "msrp" | "name";

export default function LeaseDealsPage() {
  const [cars, setCars] = useState<Car[]>([]);
  const [loading, setLoading] = useState(true);
  const [sort, setSort] = useState<SortKey>("monthly");
  const [sortAsc, setSortAsc] = useState(true);
  const [filterCat, setFilterCat] = useState("All");

  useEffect(() => {
    getCars().then((all) => {
      setCars(all.filter((c) => c.lease_monthly));
      setLoading(false);
    });
  }, []);

  const categories = useMemo(() => {
    const cats = new Set(cars.map((c) => c.category));
    return ["All", ...Array.from(cats).sort()];
  }, [cars]);

  const sorted = useMemo(() => {
    let list = filterCat === "All" ? cars : cars.filter((c) => c.category === filterCat);
    const dir = sortAsc ? 1 : -1;
    list = [...list].sort((a, b) => {
      switch (sort) {
        case "monthly": return ((a.lease_monthly ?? 0) - (b.lease_monthly ?? 0)) * dir;
        case "due": return ((a.lease_due_at_signing ?? 0) - (b.lease_due_at_signing ?? 0)) * dir;
        case "msrp": return ((a.msrp_low ?? 0) - (b.msrp_low ?? 0)) * dir;
        case "name": return a.name.localeCompare(b.name) * dir;
        default: return 0;
      }
    });
    return list;
  }, [cars, sort, sortAsc, filterCat]);

  const toggleSort = (key: SortKey) => {
    if (sort === key) setSortAsc(!sortAsc);
    else { setSort(key); setSortAsc(true); }
  };

  const savings = (car: Car) => {
    if (!car.msrp_low || !car.lease_monthly || !car.lease_term) return null;
    const totalLease = car.lease_monthly * car.lease_term + (car.lease_due_at_signing ?? 0);
    return car.msrp_low - totalLease;
  };

  return (
    <>
      <Helmet>
        <title>Best Lease Deals for NRIs — May 2026 | The Videshi</title>
        <meta name="description" content="Best car lease deals in America this month. Compare monthly payments, due at signing, and terms — curated for the Indian diaspora." />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8 max-w-6xl mx-auto">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-foreground/50 mb-6">
          <Link to="/cars" className="hover:text-primary transition-colors flex items-center gap-1">
            <ChevronLeft className="h-4 w-4" /> Cars
          </Link>
          <span>/</span>
          <span className="text-foreground/70">Lease Deals</span>
        </nav>

        {/* Hero */}
        <section className="relative mb-8 -mx-4 px-6 py-10 md:py-14 rounded-2xl overflow-hidden bg-[#1a1a2e] border border-[#2a2a4a]/40">
          <div className="absolute top-0 right-0 w-64 h-64 bg-green-500/8 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-amber-500/6 rounded-full blur-3xl" />
          <div className="relative z-10 max-w-3xl">
            <span className="text-xs font-bold uppercase tracking-widest text-green-300 bg-green-500/15 px-3 py-1 rounded-full">
              🏷️ Updated Weekly
            </span>
            <h1 className="font-serif text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight leading-[1.1] text-white mt-4">
              Best Lease Deals<br />
              <span className="text-green-400">This Month</span>
            </h1>
            <p className="text-white/60 mt-3 text-lg max-w-2xl leading-relaxed">
              {cars.length} vehicles with active lease offers — sorted by lowest monthly payment. 
              All deals verified from manufacturer incentive programs.
            </p>
          </div>
        </section>

        {/* Category pills */}
        <div className="flex gap-2 overflow-x-auto scrollbar-none mb-6 -mx-1 px-1">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterCat(cat)}
              className={`shrink-0 px-3.5 py-2 text-sm font-medium rounded-full border transition-all ${
                filterCat === cat
                  ? "bg-primary text-primary-foreground border-primary"
                  : "border-border text-foreground/70 hover:text-primary hover:border-primary/50"
              }`}
            >
              {cat !== "All" && <span className="mr-1">{CATEGORY_ICONS[cat] || ""}</span>}
              {cat}
            </button>
          ))}
        </div>

        {/* Results */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : (
          <>
            {/* Sort header */}
            <div className="hidden md:grid grid-cols-12 gap-4 px-4 py-2 text-xs font-medium text-foreground/50 uppercase tracking-wider border-b border-border mb-2">
              <div className="col-span-4">
                <SortBtn label="Vehicle" active={sort === "name"} asc={sortAsc} onClick={() => toggleSort("name")} />
              </div>
              <div className="col-span-2">
                <SortBtn label="MSRP" active={sort === "msrp"} asc={sortAsc} onClick={() => toggleSort("msrp")} />
              </div>
              <div className="col-span-2">
                <SortBtn label="Monthly" active={sort === "monthly"} asc={sortAsc} onClick={() => toggleSort("monthly")} />
              </div>
              <div className="col-span-2">
                <SortBtn label="Due at Signing" active={sort === "due"} asc={sortAsc} onClick={() => toggleSort("due")} />
              </div>
              <div className="col-span-2 text-right">Term</div>
            </div>

            <div className="space-y-3">
              {sorted.map((car, idx) => (
                <Link key={car.id} to={`/cars/${car.slug}`} className="block group">
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center p-4 bg-card border border-border rounded-xl hover:border-primary/30 transition-all hover:shadow-lg hover:shadow-primary/5">
                    {/* Car info */}
                    <div className="md:col-span-4 flex items-center gap-4">
                      <div className="relative">
                        <span className="absolute -top-1 -left-1 h-5 w-5 rounded-full bg-foreground/10 flex items-center justify-center text-[10px] font-bold text-foreground/50 z-10">
                          {idx + 1}
                        </span>
                        <div className={`w-16 h-16 rounded-lg bg-gradient-to-br ${brandGradient(car.brand)} flex items-center justify-center overflow-hidden flex-shrink-0`}>
                          {car.image_url ? (
                            <img src={car.image_url} alt={car.name} className="w-full h-full object-contain p-1" loading="lazy" />
                          ) : (
                            <span className="text-xs font-bold text-foreground/40">{car.brand.slice(0, 3)}</span>
                          )}
                        </div>
                      </div>
                      <div className="min-w-0">
                        <p className="font-semibold text-sm group-hover:text-primary transition-colors">{car.name}</p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-xs text-foreground/40">{car.category}</span>
                          {car.is_our_pick && (
                            <span className="flex items-center gap-0.5 text-amber-500 text-xs">
                              <Star className="h-3 w-3 fill-current" /> Pick
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 mt-1 text-xs text-foreground/40 md:hidden">
                          {car.mpg && <span className="flex items-center gap-0.5"><Fuel className="h-3 w-3" /> {car.mpg.split("/")[0]?.trim()}</span>}
                          {car.seating && <span className="flex items-center gap-0.5"><Users className="h-3 w-3" /> {car.seating}</span>}
                        </div>
                      </div>
                    </div>

                    {/* MSRP */}
                    <div className="hidden md:block md:col-span-2">
                      <p className="text-sm font-medium">{formatMsrp(car.msrp_low, car.msrp_high)}</p>
                    </div>

                    {/* Monthly — the star number */}
                    <div className="md:col-span-2">
                      <div className="inline-flex items-baseline gap-1 md:block">
                        <span className="md:hidden text-xs text-foreground/40">Lease: </span>
                        <p className="text-xl md:text-lg font-bold text-primary">{formatPrice(car.lease_monthly!)}<span className="text-xs font-normal text-foreground/40">/mo</span></p>
                      </div>
                    </div>

                    {/* Due at signing */}
                    <div className="hidden md:block md:col-span-2">
                      <p className="text-sm">${car.lease_due_at_signing?.toLocaleString()}</p>
                      <p className="text-xs text-foreground/40">due at signing</p>
                    </div>

                    {/* Term + savings */}
                    <div className="hidden md:block md:col-span-2 text-right">
                      <p className="text-sm">{car.lease_term} months</p>
                      {car.lease_source && (
                        <p className="text-xs text-foreground/40">via {car.lease_source}</p>
                      )}
                    </div>

                    {/* Mobile: deal summary row */}
                    <div className="md:hidden flex items-center justify-between text-xs text-foreground/50 border-t border-border/50 pt-2 -mx-4 px-4">
                      <span>{formatMsrp(car.msrp_low, car.msrp_high)}</span>
                      <span>${car.lease_due_at_signing?.toLocaleString()} due</span>
                      <span>{car.lease_term}mo</span>
                      {car.lease_source && <span>via {car.lease_source}</span>}
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* Bottom note */}
            <div className="mt-8 p-4 rounded-xl bg-card border border-border text-center">
              <p className="text-sm text-foreground/50">
                Lease deals are sourced from manufacturer incentive programs and may vary by region and credit score. 
                Visit your local dealer for final pricing.
              </p>
            </div>
          </>
        )}
      </main>

      <SiteFooter />
    </>
  );
}

/* Sort button helper */
function SortBtn({ label, active, asc, onClick }: { label: string; active: boolean; asc: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} className={`flex items-center gap-1 transition-colors ${active ? "text-primary" : "hover:text-foreground/70"}`}>
      {label}
      <ArrowUpDown className={`h-3 w-3 ${active ? "text-primary" : "text-foreground/20"}`} />
      {active && <span className="text-primary text-[9px]">{asc ? "↑" : "↓"}</span>}
    </button>
  );
}
