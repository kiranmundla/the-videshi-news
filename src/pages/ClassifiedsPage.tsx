import { useState, useEffect, useCallback, useRef } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { Search, MapPin, X, Plus, Loader2, Navigation } from "lucide-react";
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
  SUBCATEGORIES,
  timeAgo,
} from "@/lib/classifieds";
import { CITY_GROUPS } from "@/lib/events";
import { getCityCoords, getDistanceMiles, formatDistance } from "@/lib/geo";
import ZipCodeSearch, { type LocationResult } from "@/components/ZipCodeSearch";

/* ------------------------------------------------------------------ */
/* Listing Card                                                       */
/* ------------------------------------------------------------------ */
function ClassifiedCard({ item }: { item: Classified & { _dist?: number } }) {
  const imageUrl = item.image_url || (item.photos?.length ? item.photos[0] : null);
  const catColor = CATEGORY_COLORS[item.category] || "bg-muted text-muted-foreground";
  const catEmoji = CATEGORY_ICONS[item.category] || "📌";
  const isNew = Date.now() - new Date(item.created_at).getTime() < 24 * 60 * 60 * 1000;

  return (
    <Link to={`/classifieds/${item.slug}`} className="block group">
      <article className="flex flex-col sm:flex-row bg-card border border-border rounded-lg overflow-hidden hover:border-primary/40 transition-colors w-full">
        {/* Image */}
        {imageUrl ? (
          <div className="w-full sm:w-48 sm:min-w-[12rem] sm:h-auto overflow-hidden flex-shrink-0">
            <img
              src={imageUrl}
              alt={item.title}
              className="w-full max-h-64 object-contain bg-muted/10 group-hover:scale-105 transition-transform duration-300"
              loading="lazy"
            />
          </div>
        ) : (
          <div className="w-full sm:w-48 sm:min-w-[12rem] h-24 sm:h-auto bg-muted/30 flex items-center justify-center flex-shrink-0">
            <span className="text-4xl opacity-60">{catEmoji}</span>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 p-4 flex flex-col gap-2 min-w-0">
          {/* Badges */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${catColor}`}>
              {catEmoji} {item.category}
            </span>
            {item.subcategory && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-muted/50 text-foreground/70">
                {item.subcategory}
              </span>
            )}
            {isNew && (
              <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-green-100 text-green-700">
                NEW
              </span>
            )}
          </div>

          {/* Title + Price */}
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-lg leading-snug group-hover:text-primary transition-colors line-clamp-2">
              {item.title}
            </h3>
            {item.price && (
              <span className="shrink-0 text-sm font-bold px-2.5 py-1 rounded-md bg-amber-100 text-amber-800 whitespace-nowrap">
                {item.price}
              </span>
            )}
          </div>

          {/* Description preview */}
          {item.description && (
            <p className="text-sm text-foreground/60 line-clamp-2">{item.description}</p>
          )}

          {/* Meta row */}
          <div className="flex items-center gap-3 text-xs text-foreground/50 mt-auto pt-1">
            {item._dist != null && item._dist < 9999 && (
              <span className="flex items-center gap-1 text-primary font-medium">
                <Navigation className="h-3 w-3" />
                {formatDistance(item._dist)}
              </span>
            )}
            {item.city && (
              <span className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                {item.city}{item.state ? `, ${item.state}` : ""}
              </span>
            )}
            <span>{timeAgo(item.created_at)}</span>
          </div>
        </div>
      </article>
    </Link>
  );
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
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const searchTimeout = useRef<ReturnType<typeof setTimeout>>();

  // Near Me / zip state
  const [nearMeActive, setNearMeActive] = useState(false);
  const [userCoords, setUserCoords] = useState<{ lat: number; lng: number } | null>(null);

  const onSearchChange = useCallback((val: string) => {
    setSearch(val);
    if (searchTimeout.current) clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(() => setDebouncedSearch(val), 350);
  }, []);

  /* --- Location handler (from ZipCodeSearch) --- */
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

  /* --- Auto-request geolocation on mount --- */
  useEffect(() => {
    if (!userCoords && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserCoords({ lat: position.coords.latitude, lng: position.coords.longitude });
          setNearMeActive(true);
        },
        () => {},
        { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 },
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    if (nearMeActive && userCoords) {
      // Near Me: fetch all, sort by city distance
      getAllClassifieds(category, debouncedSearch || null, subcategory).then((data) => {
        if (cancelled) return;
        const sorted = data
          .map((item) => {
            const coords = getCityCoords(item.city);
            const dist = coords ? getDistanceMiles(userCoords.lat, userCoords.lng, coords.lat, coords.lng) : 9999;
            return { ...item, _dist: dist };
          })
          .sort((a, b) => a._dist - b._dist);
        setItems(sorted);
        setLoading(false);
      });
    } else {
      getClassifieds(category, city, debouncedSearch || null, subcategory).then((data) => {
        if (!cancelled) { setItems(data); setLoading(false); }
      });
    }
    return () => { cancelled = true; };
  }, [category, subcategory, city, debouncedSearch, nearMeActive, userCoords]);

  const subcats = category ? SUBCATEGORIES[category] || [] : [];

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
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors self-start sm:self-auto"
          >
            <Plus className="h-4 w-4" />
            Post a Classified
          </Link>
        </div>

        {/* Category Tabs */}
        <div className="flex gap-2 overflow-x-auto scrollbar-none -mx-1 px-1 pb-1">
          <button
            onClick={() => { setCategory(null); setSubcategory(null); }}
            className={`shrink-0 px-3.5 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              !category
                ? "bg-primary text-primary-foreground border-primary"
                : "border-border text-foreground/70 hover:border-primary hover:text-primary"
            }`}
          >
            All
          </button>
          {CLASSIFIED_CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => { setCategory(cat === category ? null : cat); setSubcategory(null); }}
              className={`shrink-0 px-3.5 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                category === cat
                  ? "bg-primary text-primary-foreground border-primary"
                  : "border-border text-foreground/70 hover:border-primary hover:text-primary"
              }`}
            >
              {CATEGORY_ICONS[cat]} {cat}
            </button>
          ))}
        </div>

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
          {/* Search */}
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

          {/* Near Me / Zip + City */}
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

        {/* Listings */}
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
          <div className="space-y-3">
            {items.map((item) => (
              <ClassifiedCard key={item.id} item={item} />
            ))}
          </div>
        )}
      </main>

      <SiteFooter />
    </>
  );
}
