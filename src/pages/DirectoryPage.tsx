import { useEffect, useState, useCallback, useRef } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  DirectoryListing,
  ListingWithDistance,
  getDirectoryListings,
  sortListingsByDistance,
  DIRECTORY_CATEGORIES,
  CATEGORY_ICONS,
  CATEGORY_COLORS,
  SUBCATEGORIES_BY_CATEGORY,
  SUBCATEGORY_ICONS,
} from "@/lib/directory";
import { CITY_GROUPS } from "@/lib/events";
import { formatDistance } from "@/lib/geo";
import ZipCodeSearch, { type LocationResult } from "@/components/ZipCodeSearch";

const DEFAULT_CITY = "Bay Area";
const PAGE_SIZE = 30;

/* ------------------------------------------------------------------ */
/* Category Badge                                                     */
/* ------------------------------------------------------------------ */
function CategoryBadge({ category }: { category: string }) {
  const icon = CATEGORY_ICONS[category] || "📌";
  const color = CATEGORY_COLORS[category] || "bg-slate-100 text-slate-700";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${color}`}>
      {icon} {category}
    </span>
  );
}

/* ------------------------------------------------------------------ */
/* Star Rating                                                        */
/* ------------------------------------------------------------------ */
function StarRating({ rating, reviewCount }: { rating: number | null; reviewCount: number | null }) {
  if (!rating) return null;
  const fullStars = Math.floor(rating);
  const hasHalf = rating - fullStars >= 0.3;

  return (
    <div className="flex items-center gap-1.5">
      <div className="flex items-center gap-px">
        {[...Array(5)].map((_, i) => (
          <span
            key={i}
            className={`text-xs ${
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
      <span className="text-sm font-medium text-amber-400">{rating}</span>
      {reviewCount != null && reviewCount > 0 && (
        <span className="text-xs text-muted-foreground">({reviewCount})</span>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Listing Card                                                       */
/* ------------------------------------------------------------------ */
function ListingCard({ listing, distance }: { listing: DirectoryListing; distance?: number }) {
  const location = [listing.city, listing.state].filter(Boolean).join(", ");
  const photos = listing.photos as string[] | null;
  const imageUrl = listing.image_url || (photos && photos.length > 0 ? photos[0] : null);

  return (
    <Link to={`/directory/${listing.slug}`} className="block no-underline">
      <article className="group flex flex-col sm:flex-row bg-card border border-border rounded-lg overflow-hidden hover:border-primary/40 transition-colors w-full" style={{ wordBreak: "break-word" }}>
        {/* Image */}
        {imageUrl ? (
          <div className="w-full sm:w-48 sm:min-w-[12rem] sm:h-auto overflow-hidden flex-shrink-0">
            <img
              src={imageUrl}
              alt={listing.name}
              className="w-full max-h-64 object-contain bg-muted/10 group-hover:scale-105 transition-transform duration-300"
              loading="lazy"
            />
          </div>
        ) : (
          <div className="w-full sm:w-48 sm:min-w-[12rem] h-24 sm:h-auto bg-muted/30 flex items-center justify-center flex-shrink-0">
            <span className="text-4xl opacity-60">{CATEGORY_ICONS[listing.category] || "🏢"}</span>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 p-4 flex flex-col justify-between min-w-0 overflow-hidden">
          <div>
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <CategoryBadge category={listing.category} />
              {listing.subcategory && listing.subcategory !== "General / Other" && (
                <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-blue-600/20 text-blue-300">
                  {SUBCATEGORY_ICONS[listing.subcategory] || "📋"} {listing.subcategory}
                </span>
              )}
              {distance != null && distance < 9999 && (
                <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-orange-600/20 text-orange-300">
                  📍 {formatDistance(distance)}
                </span>
              )}
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
            <h3 className="font-serif text-lg font-semibold text-foreground leading-snug mb-1 line-clamp-2 group-hover:text-primary transition-colors">
              {listing.name}
            </h3>
            {listing.affiliation && (
              <p className="text-xs text-blue-400/80 mb-1">🏥 {listing.affiliation}</p>
            )}
            <StarRating rating={listing.rating} reviewCount={listing.review_count} />
            {listing.description && (
              <p className="text-sm text-muted-foreground line-clamp-2 mt-1.5">
                {listing.description}
              </p>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground mt-auto pt-2">
            {location && <span className="truncate">📍 {location}</span>}
            {listing.phone && (
              <a
                href={`tel:${listing.phone}`}
                onClick={(e) => e.stopPropagation()}
                className="text-primary hover:underline"
              >
                📞 {listing.phone}
              </a>
            )}
            <span className="text-primary font-medium ml-auto">View Details →</span>
          </div>
        </div>
      </article>
    </Link>
  );
}

/* ------------------------------------------------------------------ */
/* Category Tab Bar                                                   */
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
        className={`relative whitespace-nowrap px-4 py-2.5 text-sm font-medium transition-colors rounded-t-md ${
          selected === null
            ? "text-foreground"
            : "text-muted-foreground hover:text-foreground/70"
        }`}
      >
        All
        {selected === null && (
          <span className="absolute bottom-0 left-2 right-2 h-[2px] bg-primary rounded-full" />
        )}
      </button>
      {DIRECTORY_CATEGORIES.map((cat) => (
        <button
          key={cat}
          onClick={() => onSelect(cat)}
          className={`relative whitespace-nowrap px-4 py-2.5 text-sm font-medium transition-colors rounded-t-md ${
            selected === cat
              ? "text-foreground"
              : "text-muted-foreground hover:text-foreground/70"
          }`}
        >
          <span className="mr-1.5">{CATEGORY_ICONS[cat]}</span>
          {cat}
          {selected === cat && (
            <span className="absolute bottom-0 left-2 right-2 h-[2px] bg-primary rounded-full" />
          )}
        </button>
      ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Subcategory Tab Bar (shown when Doctors & Healthcare selected)     */
/* ------------------------------------------------------------------ */
function SubcategoryTabBar({
  selected,
  onSelect,
  subcategories,
}: {
  selected: string | null;
  onSelect: (v: string | null) => void;
  subcategories: string[];
}) {
  return (
    <div className="overflow-x-auto scrollbar-none -mx-4 px-4 mt-1">
      <div className="flex items-center gap-1 pb-1 min-w-max">
        <button
          onClick={() => onSelect(null)}
          className={`relative whitespace-nowrap px-3 py-1.5 text-xs font-medium transition-colors rounded-full ${
            selected === null
              ? "bg-primary/15 text-foreground"
              : "text-muted-foreground hover:text-foreground/70 bg-muted/30"
          }`}
        >
          All
        </button>
        {subcategories.map((sub) => (
          <button
            key={sub}
            onClick={() => onSelect(sub)}
            className={`relative whitespace-nowrap px-3 py-1.5 text-xs font-medium transition-colors rounded-full ${
              selected === sub
                ? "bg-primary/15 text-foreground"
                : "text-muted-foreground hover:text-foreground/70 bg-muted/30"
            }`}
          >
            <span className="mr-1">{SUBCATEGORY_ICONS[sub] || "📋"}</span>
            {sub}
          </button>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Near Me List with distance grouping                                */
/* ------------------------------------------------------------------ */
function NearMeList({ listings }: { listings: ListingWithDistance[] }) {
  const NEARBY_THRESHOLD = 50;
  const nearby = listings.filter((l) => (l.distanceMiles ?? 9999) <= NEARBY_THRESHOLD);
  const farther = listings.filter((l) => (l.distanceMiles ?? 9999) > NEARBY_THRESHOLD);

  return (
    <>
      {nearby.length > 0 && (
        <div className="grid grid-cols-1 gap-4 w-full min-w-0">
          {nearby.map((listing) => (
            <ListingCard key={listing.id} listing={listing} distance={listing.distanceMiles} />
          ))}
        </div>
      )}
      {farther.length > 0 && (
        <>
          <div className="mt-10 mb-4 flex items-center gap-3">
            <div className="h-px flex-1 bg-border" />
            <span className="text-sm text-muted-foreground font-medium whitespace-nowrap">
              More Listings
            </span>
            <div className="h-px flex-1 bg-border" />
          </div>
          <div className="grid grid-cols-1 gap-4 w-full min-w-0">
            {farther.map((listing) => (
              <ListingCard key={listing.id} listing={listing} distance={listing.distanceMiles} />
            ))}
          </div>
        </>
      )}
    </>
  );
}

/* ------------------------------------------------------------------ */
/* Directory Page                                                     */
/* ------------------------------------------------------------------ */
export default function DirectoryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [listings, setListings] = useState<(ListingWithDistance | DirectoryListing)[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

  /* --- Search state --- */
  const [searchInput, setSearchInput] = useState(searchParams.get("q") || "");
  const searchQuery = searchParams.get("q") || "";
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  /* --- Geolocation / zip code state --- */
  const [nearMeActive, setNearMeActive] = useState(false);
  const [userCoords, setUserCoords] = useState<{ lat: number; lng: number } | null>(null);

  /* --- Sync filters with URL --- */
  const rawCity = searchParams.get("city");
  const cityFilter = nearMeActive ? null : (rawCity ?? DEFAULT_CITY);
  const categoryFilter = searchParams.get("category") || null;
  const subcategoryFilter = searchParams.get("subcategory") || null;

  const setCityFilter = useCallback((city: string | null) => {
    setNearMeActive(false);
    setUserCoords(null);
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (city && city !== DEFAULT_CITY) {
        next.set("city", city);
      } else {
        next.delete("city");
      }
      next.delete("nearme");
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  /* --- Location handler (from ZipCodeSearch) --- */
  const handleLocation = useCallback((result: LocationResult | null) => {
    if (!result) {
      setNearMeActive(false);
      setUserCoords(null);
      setCityFilter(DEFAULT_CITY);
      return;
    }
    setUserCoords({ lat: result.lat, lng: result.lng });
    setNearMeActive(true);
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.delete("city");
      next.set("nearme", "1");
      return next;
    }, { replace: true });
  }, [setCityFilter, setSearchParams]);

  const setCategoryFilter = useCallback((cat: string | null) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (cat) next.set("category", cat);
      else next.delete("category");
      next.delete("subcategory"); // clear subcategory when changing category
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  const setSubcategoryFilter = useCallback((sub: string | null) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (sub) next.set("subcategory", sub);
      else next.delete("subcategory");
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  /* --- Debounced search --- */
  const handleSearchChange = useCallback((value: string) => {
    setSearchInput(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        if (value.trim()) next.set("q", value.trim());
        else next.delete("q");
        return next;
      }, { replace: true });
    }, 300);
  }, [setSearchParams]);

  const clearSearch = useCallback(() => {
    setSearchInput("");
    if (debounceRef.current) clearTimeout(debounceRef.current);
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.delete("q");
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  /* --- Auto-request geolocation on page load --- */
  useEffect(() => {
    if (rawCity) return;
    if (!nearMeActive && !userCoords && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = { lat: position.coords.latitude, lng: position.coords.longitude };
          setUserCoords(coords);
          setNearMeActive(true);
          setSearchParams((prev) => {
            const next = new URLSearchParams(prev);
            next.delete("city");
            next.set("nearme", "1");
            return next;
          }, { replace: true });
        },
        () => {
          setNearMeActive(false);
        },
        { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 },
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* --- Fetch listings --- */
  useEffect(() => {
    setLoading(true);
    setHasMore(true);

    if (nearMeActive && userCoords) {
      // Near Me mode: fetch all listings, sort by distance
      getDirectoryListings(categoryFilter, null, searchQuery || null, 500, 0, subcategoryFilter).then((data) => {
        const sorted = sortListingsByDistance(data, userCoords.lat, userCoords.lng);
        setListings(sorted);
        setHasMore(false);
        setLoading(false);
      });
    } else {
      getDirectoryListings(categoryFilter, cityFilter, searchQuery || null, PAGE_SIZE, 0, subcategoryFilter).then((data) => {
        setListings(data);
        setHasMore(data.length === PAGE_SIZE);
        setLoading(false);
      });
    }
  }, [cityFilter, categoryFilter, subcategoryFilter, nearMeActive, userCoords, searchQuery]);

  const loadMore = async () => {
    if (loadingMore || !hasMore || nearMeActive) return;
    setLoadingMore(true);
    const next = await getDirectoryListings(categoryFilter, cityFilter, searchQuery || null, PAGE_SIZE, listings.length, subcategoryFilter);
    setListings((prev) => [...prev, ...next]);
    setHasMore(next.length === PAGE_SIZE);
    setLoadingMore(false);
  };

  /* --- Summary text --- */
  const summaryParts: string[] = [];
  if (searchQuery) summaryParts.push(`matching "${searchQuery}"`);
  if (nearMeActive) summaryParts.push("near you");
  else if (cityFilter) summaryParts.push(`in ${cityFilter}`);
  if (categoryFilter) summaryParts.push(`· ${categoryFilter}`);
  if (subcategoryFilter) summaryParts.push(`· ${subcategoryFilter}`);
  const summaryText = summaryParts.length > 0 ? " " + summaryParts.join(" ") : "";

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <Helmet>
        <title>Desi Business Directory — The Videshi</title>
        <meta
          name="description"
          content="Find trusted Indian and desi professionals — doctors, lawyers, accountants, real estate agents, and more across the US."
        />
        <link rel="canonical" href="https://www.thevideshi.com/directory" />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <style>{`
        .directory-main { max-width: 100vw; overflow-x: hidden; }
        .directory-main article { max-width: calc(100vw - 2.5rem); }
      `}</style>
      <main className="directory-main container flex-1 pt-8 md:pt-10 pb-16">
        {/* Header */}
        <div className="mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-3">
            <h1 className="font-serif text-3xl md:text-5xl text-foreground">
              Directory
            </h1>
            <Link
              to="/directory/submit"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors whitespace-nowrap self-start sm:self-auto"
            >
              <span>+</span> Submit a Listing
            </Link>
          </div>
          <p className="text-muted-foreground text-lg">
            Find trusted Indian &amp; desi professionals and businesses across the US
          </p>
        </div>

        {/* Search + Location controls */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-5">
          {/* Search bar */}
          <div className="relative flex-1 max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
              <svg className="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
            </div>
            <input
              type="text"
              value={searchInput}
              onChange={(e) => handleSearchChange(e.target.value)}
              placeholder="Search by name, specialty, city..."
              className="w-full pl-10 pr-10 py-2.5 rounded-lg border border-border bg-background text-foreground text-sm placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary/40 transition-colors"
            />
            {searchInput && (
              <button
                onClick={clearSearch}
                className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-muted-foreground hover:text-foreground transition-colors"
                aria-label="Clear search"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          {/* Location: Zip / Near Me + City dropdown */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <ZipCodeSearch
              onLocation={handleLocation}
              active={nearMeActive}
            />

            <div className="relative flex-shrink-0">
              <select
                value={nearMeActive ? "" : (cityFilter || "")}
                onChange={(e) => setCityFilter(e.target.value || null)}
                className={`px-4 py-2.5 pr-9 rounded-lg border text-sm font-medium appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary/40 transition-colors ${
                  nearMeActive
                    ? "bg-muted/20 border-border/50 text-muted-foreground/50"
                    : "bg-background border-border text-foreground"
                }`}
                style={{
                  backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E\")",
                  backgroundRepeat: "no-repeat",
                  backgroundPosition: "right 12px center",
                }}
              >
                <option value="">All Cities</option>
                {CITY_GROUPS.map((g) => (
                  <option key={g.label} value={g.label}>
                    {g.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Category tabs */}
        <div className="border-b border-border mb-2 overflow-x-auto scrollbar-none">
          <CategoryTabBar selected={categoryFilter} onSelect={setCategoryFilter} />
        </div>

        {/* Subcategory tabs (shown for categories with subcategories) */}
        {categoryFilter && SUBCATEGORIES_BY_CATEGORY[categoryFilter] && (
          <div className="mb-4">
            <SubcategoryTabBar
              selected={subcategoryFilter}
              onSelect={setSubcategoryFilter}
              subcategories={SUBCATEGORIES_BY_CATEGORY[categoryFilter]}
            />
          </div>
        )}

        {/* Listings */}
        {loading ? (
          <div className="grid gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-40 rounded-lg bg-muted/20 animate-pulse" />
            ))}
          </div>
        ) : listings.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-4xl mb-4">🏢</p>
            <p className="text-muted-foreground text-lg">
              No listings found{summaryText}.
            </p>
            <p className="text-muted-foreground text-sm mt-2">
              Try a different city or category, or check back soon!
            </p>
          </div>
        ) : (
          <>
            <p className="text-sm text-muted-foreground mb-4">
              {listings.length}{hasMore ? "+" : ""} listings{summaryText}
            </p>

            {nearMeActive ? (
              <NearMeList listings={listings as ListingWithDistance[]} />
            ) : (
              <div className="grid grid-cols-1 gap-4 w-full min-w-0">
                {listings.map((listing) => (
                  <ListingCard key={listing.id} listing={listing} />
                ))}
              </div>
            )}

            {hasMore && !nearMeActive && (
              <div className="flex justify-center mt-8">
                <button
                  onClick={loadMore}
                  disabled={loadingMore}
                  className="px-6 py-3 rounded-lg bg-muted/40 text-foreground font-medium hover:bg-muted/60 transition-colors disabled:opacity-50"
                >
                  {loadingMore ? "Loading..." : "Load more listings"}
                </button>
              </div>
            )}
          </>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
