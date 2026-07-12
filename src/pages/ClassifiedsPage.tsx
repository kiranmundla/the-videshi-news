import { useState, useEffect, useCallback, useRef } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { Search, X, Plus, Loader2 } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  Classified,
  getClassifieds,
  getAllClassifieds,
  CLASSIFIED_CATEGORIES,
  CATEGORY_ICONS,
  CATEGORY_COLORS,
  CATEGORY_BORDER,
  CATEGORY_BG,
  SUBCATEGORIES,
  timeAgo,
} from "@/lib/classifieds";
import { CITY_GROUPS } from "@/lib/events";
import { getCityCoords, getDistanceMiles, formatDistance } from "@/lib/geo";
import { useUserLocation } from "@/hooks/useUserLocation";
import ZipCodeSearch, { type LocationResult } from "@/components/ZipCodeSearch";

/* ------------------------------------------------------------------ */
/* Category fallback images                                           */
/* ------------------------------------------------------------------ */
const CAT_FALLBACK_IMG: Record<string, string> = {
  Services: "/images/classifieds/services.jpg",
  Housing: "/images/classifieds/housing.jpg",
  "For Sale": "/images/classifieds/for-sale.jpg",
  "Jobs & Gigs": "/images/classifieds/jobs.jpg",
  Community: "/images/classifieds/community.jpg",
};

function categoryFallbackImg(category: string): string {
  return CAT_FALLBACK_IMG[category] || CAT_FALLBACK_IMG["Community"];
}


/* ------------------------------------------------------------------ */
/* Category Badge (matches events/directory style)                    */
/* ------------------------------------------------------------------ */
function CategoryBadge({ category }: { category: string }) {
  const icon = CATEGORY_ICONS[category] || "📌";
  const color = CATEGORY_COLORS[category] || "bg-muted text-muted-foreground";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${color}`}>
      {icon} {category}
    </span>
  );
}

/* ------------------------------------------------------------------ */
/* Listing Card — matches events/directory card pattern               */
/* ------------------------------------------------------------------ */
function ClassifiedCard({ item }: { item: Classified & { _dist?: number } }) {
  const imageUrl = item.image_url || (item.photos?.length ? item.photos[0] : null);
  const catEmoji = CATEGORY_ICONS[item.category] || "📌";
  const isNew = Date.now() - new Date(item.created_at).getTime() < 24 * 60 * 60 * 1000;
  const location = [item.city, item.state].filter(Boolean).join(", ");

  return (
    <Link to={`/classifieds/${item.slug}`} className="block no-underline">
      <article className={`group flex flex-row ${CATEGORY_BG[item.category] || "bg-card"} border border-border/50 border-l-[3px] ${CATEGORY_BORDER[item.category] || "border-l-muted"} rounded-lg overflow-hidden hover:border-primary/40 transition-colors w-full`}>
        {/* Thumbnail */}
        {imageUrl ? (
          <div className="w-24 min-w-[6rem] sm:w-32 sm:min-w-[8rem] flex-shrink-0 flex items-center justify-center bg-muted/10 overflow-hidden">
            <img
              src={imageUrl}
              alt={item.title}
              className="w-full h-auto object-contain max-h-44 group-hover:scale-105 transition-transform duration-300"
              loading="lazy"
              onError={(e) => {
                const container = (e.target as HTMLElement).parentElement;
                if (container) container.style.display = "none";
              }}
            />
          </div>
        ) : (
          <div className={`w-20 min-w-[5rem] sm:w-24 sm:min-w-[6rem] flex-shrink-0 flex items-center justify-center ${CATEGORY_BG[item.category] || "bg-muted/20"}`}>
            <span className="text-3xl">{catEmoji}</span>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 p-3 min-w-0 overflow-hidden flex flex-col">
          <div className="flex-1">
            {/* Badges */}
            <div className="flex items-center gap-1.5 mb-1.5 flex-wrap">
              <CategoryBadge category={item.category} />
              {item.subcategory && (
                <span className="inline-block px-1.5 py-0.5 rounded text-[11px] font-medium bg-blue-600/20 text-blue-300">
                  {item.subcategory}
                </span>
              )}
              {item._dist != null && item._dist < 9999 && (
                <span className="inline-block px-1.5 py-0.5 rounded text-[11px] font-medium bg-orange-600/20 text-orange-300">
                  📍 {formatDistance(item._dist)}
                </span>
              )}
              {isNew && (
                <span className="inline-block px-1.5 py-0.5 rounded text-[11px] font-bold bg-green-600/20 text-green-400">
                  NEW
                </span>
              )}
            </div>

            {/* Title */}
            <h3 className="font-serif text-base font-semibold text-foreground leading-snug mb-1 line-clamp-2 group-hover:text-primary transition-colors">
              {item.title}
            </h3>

            {/* Price */}
            {item.price && (
              <span className="inline-block text-sm font-bold text-amber-600 mb-1">
                {item.price}
              </span>
            )}

            {/* Description */}
            {item.description && (
              <p className="text-xs text-muted-foreground line-clamp-2 mb-1.5">
                {item.description}
              </p>
            )}
          </div>

          {/* Footer: location + time — pinned to bottom */}
          <div className="flex items-center gap-3 text-xs text-muted-foreground pt-1.5 border-t border-border/50 mt-auto">
            {location && <span className="truncate">📍 {location}</span>}
            <span className="ml-auto flex-shrink-0">{timeAgo(item.created_at)}</span>
          </div>
        </div>
      </article>
    </Link>
  );
}

/* ------------------------------------------------------------------ */
/* Category Tab Bar (matches directory style)                         */
/* ------------------------------------------------------------------ */
function CategoryTabBar({
  selected,
  onSelect,
}: {
  selected: string | null;
  onSelect: (v: string | null) => void;
}) {
  return (
    <div className="overflow-x-auto scrollbar-none -mx-4 px-4">
      <div className="flex items-center gap-1 pb-1 min-w-max">
        <button
          onClick={() => onSelect(null)}
          className={`shrink-0 px-3.5 py-1.5 rounded-full text-sm font-medium border transition-colors ${
            !selected
              ? "bg-primary text-primary-foreground border-primary"
              : "border-border text-foreground/70 hover:border-primary hover:text-primary"
          }`}
        >
          All
        </button>
        {CLASSIFIED_CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => onSelect(cat === selected ? null : cat)}
            className={`shrink-0 px-3.5 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              selected === cat
                ? "bg-primary text-primary-foreground border-primary"
                : "border-border text-foreground/70 hover:border-primary hover:text-primary"
            }`}
          >
            {CATEGORY_ICONS[cat]} {cat}
          </button>
        ))}
      </div>
    </div>
  );
}


/* ------------------------------------------------------------------ */
/* Time filter helper                                                 */
/* ------------------------------------------------------------------ */
function applyTimeFilter(items: Classified[], filter: string): Classified[] {
  if (filter === "all") return items;
  const now = Date.now();
  const cutoffs: Record<string, number> = {
    today: 24 * 60 * 60 * 1000,
    week: 7 * 24 * 60 * 60 * 1000,
    month: 30 * 24 * 60 * 60 * 1000,
  };
  const cutoff = cutoffs[filter] || 0;
  if (!cutoff) return items;
  return items.filter((item) => now - new Date(item.created_at).getTime() < cutoff);
}

/* ------------------------------------------------------------------ */
/* Main Page                                                          */
/* ------------------------------------------------------------------ */
export default function ClassifiedsPage() {
  const [items, setItems] = useState<Classified[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState<string | null>(null);
  const [subcategory, setSubcategory] = useState<string | null>(null);
  const [city, setCity] = useState<string | null>(null);
  const [timeFilter, setTimeFilter] = useState<string>("all");
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const searchTimeout = useRef<ReturnType<typeof setTimeout>>();
  const [visibleCount, setVisibleCount] = useState(12);

  // Near Me / zip state
  const [nearMeActive, setNearMeActive] = useState(false);
  const [userCoords, setUserCoords] = useState<{ lat: number; lng: number } | null>(null);
  const { location: ipLocation } = useUserLocation();

  const onSearchChange = useCallback((val: string) => {
    setSearch(val);
    if (searchTimeout.current) clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(() => setDebouncedSearch(val), 350);
  }, []);

  const handleLocation = useCallback((result: LocationResult | null) => {
    if (!result) {
      setNearMeActive(false);
      setUserCoords(null);
      return;
    }
    setUserCoords({ lat: result.lat, lng: result.lng });
    setNearMeActive(true);
    setCity(null);
  }, []);

  useEffect(() => {
    if (!userCoords && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserCoords({ lat: position.coords.latitude, lng: position.coords.longitude });
          setNearMeActive(true);
        },
        () => {
          if (ipLocation) {
            setUserCoords({ lat: ipLocation.latitude, lng: ipLocation.longitude });
            setNearMeActive(true);
          }
        },
        { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 },
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ipLocation]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    if (nearMeActive && userCoords) {
      getAllClassifieds(category, debouncedSearch || null, subcategory).then((data) => {
        if (cancelled) return;
        const filtered = applyTimeFilter(data, timeFilter);
        const sorted = filtered
          .map((item) => {
            const coords = getCityCoords(item.city);
            const dist = coords ? getDistanceMiles(userCoords.lat, userCoords.lng, coords.lat, coords.lng) : 9999;
            return { ...item, _dist: dist };
          })
          .sort((a, b) => {
            // Primary: distance, Secondary: newest first
            if (a._dist !== b._dist) return a._dist - b._dist;
            return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
          });
        setItems(sorted);
        setLoading(false);
      });
    } else {
      getClassifieds(category, city, debouncedSearch || null, subcategory).then((data) => {
        if (cancelled) return;
        const filtered = applyTimeFilter(data, timeFilter);
        // Sort by newest first when no distance sort
        filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        setItems(filtered);
        setLoading(false);
      });
    }
    return () => { cancelled = true; };
  }, [category, subcategory, city, debouncedSearch, nearMeActive, userCoords, timeFilter]);

  const subcats = category ? SUBCATEGORIES[category] || [] : [];

  // Reset pagination when filters change
  useEffect(() => { setVisibleCount(12); }, [category, subcategory, city, debouncedSearch, nearMeActive, timeFilter]);

  return (
    <>
      <Helmet>
        <title>Classifieds — Desi Community Marketplace | The Videshi</title>
        <meta name="description" content="Post and browse classifieds for the Indian diaspora — services, housing, items for sale, jobs, and community listings across the US." />
        <meta property="og:title" content="Classifieds — The Videshi" />
        <meta property="og:description" content="Desi community marketplace — services, housing, for sale, jobs & gigs." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://www.thevideshi.com/classifieds" />
        <meta name="twitter:card" content="summary" />
        <link rel="canonical" href="https://www.thevideshi.com/classifieds" />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container py-6 space-y-5">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold font-serif">Classifieds</h1>
            <p className="text-sm text-foreground/50 mt-1">
              Community marketplace for the Indian diaspora
            </p>
          </div>
          <Link
            to="/classifieds/submit"
            className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors self-start sm:self-auto whitespace-nowrap"
          >
            <Plus className="h-4 w-4" />
            Post a Classified
          </Link>
        </div>

        {/* Category Tabs */}
        <CategoryTabBar selected={category} onSelect={(v) => { setCategory(v); setSubcategory(null); }} />

        {/* Subcategory pills */}
        {subcats.length > 0 && (
          <div className="flex gap-2 overflow-x-auto scrollbar-none -mx-1 px-1 pb-1">
            <button
              onClick={() => setSubcategory(null)}
              className={`shrink-0 px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                !subcategory
                  ? "bg-foreground/10 border-foreground/20 text-foreground"
                  : "border-border text-foreground/50 hover:border-foreground/30"
              }`}
            >
              All {category}
            </button>
            {subcats.map((sub) => (
              <button
                key={sub}
                onClick={() => setSubcategory(sub === subcategory ? null : sub)}
                className={`shrink-0 px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                  subcategory === sub
                    ? "bg-foreground/10 border-foreground/20 text-foreground"
                    : "border-border text-foreground/50 hover:border-foreground/30"
                }`}
              >
                {sub}
              </button>
            ))}
          </div>
        )}

        {/* Search + Near Me + City Filter */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground/40" />
            <input
              type="text"
              placeholder="Search classifieds…"
              value={search}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full pl-10 pr-9 py-2.5 rounded-lg border border-border bg-card text-sm placeholder:text-foreground/40 focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
            {search && (
              <button
                onClick={() => { setSearch(""); setDebouncedSearch(""); }}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-foreground/40 hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          <div className="flex gap-2">
            <ZipCodeSearch
              onLocation={handleLocation}
              active={nearMeActive}
              compact
            />
            <select
              value={nearMeActive ? "" : (city || "")}
              onChange={(e) => {
                setCity(e.target.value || null);
                if (e.target.value) { setNearMeActive(false); setUserCoords(null); }
              }}
              className="px-3 py-2.5 rounded-lg border border-border bg-card text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 sm:w-48 min-w-0 flex-1 sm:flex-none"
            >
              <option value="">{nearMeActive ? "Near Me" : "All Cities"}</option>
              {CITY_GROUPS.map((g) => (
                <option key={g.label} value={g.label}>{g.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Time Filter */}
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-none -mx-1 px-1">
          <span className="text-xs text-muted-foreground shrink-0">Posted:</span>
          {[
            { key: "all", label: "All Time" },
            { key: "today", label: "Today" },
            { key: "week", label: "This Week" },
            { key: "month", label: "This Month" },
          ].map((t) => (
            <button
              key={t.key}
              onClick={() => setTimeFilter(t.key)}
              className={`shrink-0 px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                timeFilter === t.key
                  ? "bg-primary text-primary-foreground border-primary"
                  : "border-border text-foreground/60 hover:border-primary hover:text-primary"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Listings — 2-col grid like events/directory */}
        {loading ? (
          <div className="flex justify-center py-16">
            <Loader2 className="h-6 w-6 animate-spin text-foreground/40" />
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-16 space-y-3">
            <p className="text-4xl">📋</p>
            <p className="text-foreground/60">No classifieds found</p>
            <p className="text-sm text-foreground/40">
              {search || category || city
                ? "Try adjusting your filters"
                : "Be the first to post!"}
            </p>
            <Link
              to="/classifieds/submit"
              className="inline-flex items-center gap-1.5 mt-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
            >
              <Plus className="h-4 w-4" />
              Post a Classified
            </Link>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full min-w-0">
              {items.slice(0, visibleCount).map((item) => (
                <ClassifiedCard key={item.id} item={item} />
              ))}
            </div>

            {items.length > visibleCount && (
              <div className="flex flex-col items-center gap-2 pt-4">
                <p className="text-sm text-muted-foreground">
                  Showing {Math.min(visibleCount, items.length)} of {items.length}
                </p>
                <button
                  onClick={() => setVisibleCount((c) => c + 12)}
                  className="px-6 py-2.5 rounded-lg border border-border text-sm font-medium hover:bg-muted/30 transition-colors"
                >
                  Show More
                </button>
              </div>
            )}
          </>
        )}
      </main>

      <SiteFooter />
    </>
  );
}
