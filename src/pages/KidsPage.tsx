import { useState, useEffect, useMemo, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useSearchParams } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { useUserLocation } from "@/hooks/useUserLocation";
import {
  fetchKidsPrograms,
  fetchKidsDeadlines,
  type KidsProgram,
  type KidsDeadline,
} from "@/lib/kidsPrograms";
import {
  fetchLocalPlaces,
  distanceMiles,
  placeMatchesAge,
  LOCAL_CATEGORIES,
  CATEGORY_GRADIENTS,
  LOCAL_CATEGORY_COLORS,
  type KidsLocalPlace,
} from "@/lib/kidsLocalPlaces";

/* ------------------------------------------------------------------ */
/* Constants                                                          */
/* ------------------------------------------------------------------ */

const PROGRAM_CATEGORIES = [
  { key: "All", icon: "📋" },
  { key: "Academic Competitions", icon: "🏆" },
  { key: "Math", icon: "🔢" },
  { key: "Science & STEM", icon: "🧪" },
  { key: "Robotics", icon: "🤖" },
  { key: "Coding & CS", icon: "💻" },
  { key: "Chess", icon: "♟️" },
  { key: "College Prep", icon: "📝" },
  { key: "Summer Programs", icon: "☀️" },
  { key: "Sports", icon: "⚽" },
  { key: "Dance", icon: "💃" },
  { key: "Music", icon: "🎵" },
  { key: "Language", icon: "🗣️" },
  { key: "Cultural & Arts", icon: "🎨" },
  { key: "Cultural & Religious", icon: "🪔" },
  { key: "Volunteering", icon: "🤝" },
];

const PROGRAM_CATEGORY_COLORS: Record<string, string> = {
  "Academic Competitions": "bg-blue-100 text-blue-700",
  Math: "bg-indigo-100 text-indigo-700",
  "Science & STEM": "bg-emerald-100 text-emerald-700",
  Robotics: "bg-cyan-100 text-cyan-700",
  "Coding & CS": "bg-violet-100 text-violet-700",
  Chess: "bg-slate-100 text-slate-700",
  "College Prep": "bg-rose-100 text-rose-700",
  "Summer Programs": "bg-orange-100 text-orange-700",
  Sports: "bg-lime-100 text-lime-700",
  Dance: "bg-pink-100 text-pink-700",
  Music: "bg-purple-100 text-purple-700",
  "Cultural & Arts": "bg-purple-100 text-purple-700",
  Language: "bg-amber-100 text-amber-700",
  "Cultural & Religious": "bg-yellow-100 text-yellow-700",
  Volunteering: "bg-teal-100 text-teal-700",
};

const AGE_GROUPS = [
  { key: "preschool", label: "Preschool", sub: "Ages 3–5", icon: "🧒" },
  { key: "elementary", label: "Elementary", sub: "Grades K–5", icon: "📖" },
  { key: "middle_school", label: "Middle School", sub: "Grades 6–8", icon: "🔬" },
  { key: "high_school", label: "High School", sub: "Grades 9–12", icon: "🎓" },
];

const PLACES_INITIAL = 9;
const PROGRAMS_INITIAL = 6;

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

function daysUntil(dateStr: string): number {
  const target = new Date(dateStr + "T00:00:00");
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

function mapsUrl(place: KidsLocalPlace): string {
  if (place.latitude && place.longitude) {
    return `https://www.google.com/maps/dir/?api=1&destination=${place.latitude},${place.longitude}`;
  }
  if (place.address) {
    return `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(
      `${place.address}, ${place.city}, ${place.state}`,
    )}`;
  }
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
    `${place.name} ${place.city} ${place.state}`,
  )}`;
}

function telUrl(phone: string): string {
  return `tel:${phone.replace(/[^\d+]/g, "")}`;
}

/* ------------------------------------------------------------------ */
/* Closing-Soon Strip                                                 */
/* ------------------------------------------------------------------ */

function ClosingSoonStrip({
  deadlines,
  selectedAge,
}: {
  deadlines: KidsDeadline[];
  selectedAge: string | null;
}) {
  let urgent = deadlines.filter((d) => {
    const days = daysUntil(d.deadline_date);
    return days >= 0 && days <= 14;
  });

  // Filter by age group if selected (match program's age_groups via category heuristic)
  if (selectedAge && urgent.length > 0) {
    // We don't have age_groups on deadlines, so keep all when filtered
    // Future: join with program age_groups
  }

  urgent = urgent.slice(0, 6);
  if (urgent.length === 0) return null;

  return (
    <section className="mb-12">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-lg">🔔</span>
        <h2 className="font-serif text-lg font-semibold text-foreground">
          Don't Miss — Registration Closing Soon
        </h2>
        <div className="h-px flex-1 bg-border" />
      </div>

      <div
        className="flex gap-3 overflow-x-auto pb-2 -mx-1 px-1 scrollbar-hide"
        style={{ scrollSnapType: "x mandatory" }}
      >
        {urgent.map((d) => {
          const days = daysUntil(d.deadline_date);
          const isRed = days <= 7;
          return (
            <div
              key={d.id}
              className={`flex-shrink-0 w-[260px] sm:w-[280px] rounded-lg border p-4 transition-all hover:shadow-md ${
                isRed
                  ? "border-red-200 bg-red-50"
                  : "border-amber-200 bg-amber-50"
              }`}
              style={{ scrollSnapAlign: "start" }}
            >
              <div className="flex items-center justify-between mb-2">
                <span
                  className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-bold ${
                    isRed ? "text-red-700" : "text-amber-700"
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      isRed ? "bg-red-500 animate-pulse" : "bg-amber-500"
                    }`}
                  />
                  {days === 0
                    ? "Today!"
                    : days === 1
                      ? "Tomorrow!"
                      : `${days} days left`}
                </span>
              </div>

              <h3
                className={`font-semibold text-sm leading-snug line-clamp-2 mb-1 ${
                  isRed ? "text-red-900" : "text-amber-900"
                }`}
              >
                {d.program_name || d.title}
              </h3>

              {d.program_name && d.title !== d.program_name && (
                <p
                  className={`text-xs line-clamp-1 mb-2 ${
                    isRed ? "text-red-700/70" : "text-amber-700/70"
                  }`}
                >
                  {d.title}
                </p>
              )}

              {d.registration_url && (
                <a
                  href={d.registration_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs font-semibold hover:underline"
                  style={{ color: "#A32D2F" }}
                >
                  Register →
                </a>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* Local Place Card                                                   */
/* ------------------------------------------------------------------ */

function LocalPlaceCard({
  place,
  userLat,
  userLng,
}: {
  place: KidsLocalPlace;
  userLat?: number;
  userLng?: number;
}) {
  const catIcon =
    LOCAL_CATEGORIES.find((c) => c.key === place.category)?.icon || "📍";
  const gradient =
    CATEGORY_GRADIENTS[place.category] || "from-gray-400 to-gray-300";
  const catColor =
    LOCAL_CATEGORY_COLORS[place.category] || "bg-gray-100 text-gray-700";

  const dist =
    userLat && userLng && place.latitude && place.longitude
      ? distanceMiles(userLat, userLng, place.latitude, place.longitude)
      : null;

  const addressLine = place.address
    ? `${place.address}, ${place.city}, ${place.state}${place.zip_code ? ` ${place.zip_code}` : ""}`
    : `${place.city}, ${place.state}`;

  return (
    <div className="group rounded-xl border border-border bg-card overflow-hidden transition-all hover:shadow-lg hover:border-[#D4A843]/50 flex flex-col h-full">
      {/* Image / gradient header */}
      {place.image_url ? (
        <div className="h-36 sm:h-40 overflow-hidden">
          <img
            src={place.image_url}
            alt={place.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        </div>
      ) : (
        <div
          className={`h-28 sm:h-32 bg-gradient-to-br ${gradient} flex items-center justify-center`}
        >
          <span className="text-4xl opacity-80">{catIcon}</span>
        </div>
      )}

      {/* Content */}
      <div className="p-4 sm:p-5 flex flex-col flex-1">
        {/* Badges */}
        <div className="flex flex-wrap gap-1.5 mb-2">
          <span
            className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold ${catColor}`}
          >
            {catIcon} {place.category}
          </span>
          {place.is_indian_focused && (
            <span className="inline-block px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 text-[10px] font-semibold">
              🇮🇳 Indian Community
            </span>
          )}
        </div>

        {/* Name */}
        <h3 className="font-serif text-[15px] sm:text-base font-semibold text-foreground leading-snug line-clamp-2 mb-1.5">
          {place.name}
        </h3>

        {/* Rating */}
        {place.rating && (
          <div className="flex items-center gap-1.5 mb-2">
            <span className="text-amber-500 text-sm">⭐</span>
            <span className="text-sm font-medium text-foreground">
              {place.rating}
            </span>
            {place.review_count && (
              <span className="text-xs text-muted-foreground">
                ({place.review_count} reviews)
              </span>
            )}
            {dist !== null && (
              <span className="text-xs text-muted-foreground ml-auto">
                {dist < 1 ? "< 1 mi" : `${dist.toFixed(1)} mi`}
              </span>
            )}
          </div>
        )}

        {/* Distance if no rating */}
        {!place.rating && dist !== null && (
          <div className="text-xs text-muted-foreground mb-2">
            📍 {dist < 1 ? "< 1 mi away" : `${dist.toFixed(1)} mi away`}
          </div>
        )}

        {/* Description */}
        {place.description && (
          <p className="text-xs text-muted-foreground line-clamp-2 mb-3">
            {place.description}
          </p>
        )}

        {/* Address */}
        <div className="text-xs text-muted-foreground mb-1">
          <span className="mr-1">📍</span>
          {addressLine}
        </div>

        {/* Age range */}
        {place.age_range && (
          <div className="text-xs text-muted-foreground mb-3">
            <span className="mr-1">🎒</span>
            Ages {place.age_range}
          </div>
        )}

        {/* Spacer */}
        <div className="flex-1" />

        {/* Action buttons */}
        <div className="flex items-center gap-2 pt-3 border-t border-border/50">
          <a
            href={mapsUrl(place)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 text-center px-2 py-1.5 rounded-lg text-xs font-medium bg-muted/30 hover:bg-muted/50 text-foreground transition-colors"
          >
            🗺️ Directions
          </a>
          {place.website && (
            <a
              href={place.website}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 text-center px-2 py-1.5 rounded-lg text-xs font-medium bg-muted/30 hover:bg-muted/50 text-foreground transition-colors"
            >
              🌐 Website
            </a>
          )}
          {place.phone && (
            <a
              href={telUrl(place.phone)}
              className="flex-1 text-center px-2 py-1.5 rounded-lg text-xs font-medium bg-muted/30 hover:bg-muted/50 text-foreground transition-colors"
            >
              📞 Call
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Program Card                                                       */
/* ------------------------------------------------------------------ */

function ProgramCard({ program }: { program: KidsProgram }) {
  const catColor =
    PROGRAM_CATEGORY_COLORS[program.category || ""] ||
    "bg-gray-100 text-gray-700";

  return (
    <Link
      to={`/kids/programs/${program.slug}`}
      className="block no-underline h-full"
    >
      <div
        className={`group rounded-xl border bg-card p-5 sm:p-6 transition-all hover:shadow-lg hover:border-[#D4A843]/50 flex flex-col h-full ${
          program.is_featured ? "ring-1 ring-[#D4A843]/40" : "border-border"
        }`}
      >
        <div className="flex flex-wrap gap-1.5 mb-3">
          {program.is_featured && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-600 text-[10px] font-semibold">
              ⭐ Featured
            </span>
          )}
          {program.is_indian_org && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 text-[10px] font-semibold">
              🇮🇳 Indian Community
            </span>
          )}
        </div>

        <h3 className="font-serif text-base sm:text-[17px] font-semibold text-foreground leading-snug line-clamp-2 group-hover:text-[#A32D2F] transition-colors mb-1.5">
          {program.name}
        </h3>

        {program.organization && (
          <p className="text-xs text-muted-foreground mb-3 truncate">
            {program.organization}
          </p>
        )}

        {program.category && (
          <div className="mb-3">
            <span
              className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-medium ${catColor}`}
            >
              {program.category}
            </span>
          </div>
        )}

        <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground mb-3">
          {program.age_range && <span>🎒 {program.age_range}</span>}
          {program.format && <span>📍 {program.format}</span>}
          {program.cost && <span>💰 {program.cost}</span>}
        </div>

        {program.description && (
          <p className="text-sm text-muted-foreground line-clamp-3 mb-4 flex-1">
            {program.description}
          </p>
        )}

        <div className="mt-auto pt-2">
          <span className="text-sm font-medium text-[#A32D2F] group-hover:underline">
            Learn More →
          </span>
        </div>
      </div>
    </Link>
  );
}

/* ------------------------------------------------------------------ */
/* Filter Pill                                                        */
/* ------------------------------------------------------------------ */

function FilterPill({
  label,
  icon,
  active,
  count,
  onClick,
  color,
}: {
  label: string;
  icon?: string;
  active: boolean;
  count?: number;
  onClick: () => void;
  color?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex-shrink-0 px-3 py-1.5 text-xs font-medium rounded-full border transition-colors whitespace-nowrap ${
        active
          ? "text-white border-transparent"
          : "bg-card text-muted-foreground border-border hover:border-foreground/30 hover:text-foreground"
      }`}
      style={active ? { backgroundColor: color || "#A32D2F" } : undefined}
    >
      {icon && <span className="mr-1">{icon}</span>}
      {label}
      {count !== undefined && count > 0 && (
        <span className="ml-1 opacity-70">({count})</span>
      )}
    </button>
  );
}

/* ------------------------------------------------------------------ */
/* Grid Skeleton                                                      */
/* ------------------------------------------------------------------ */

function GridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
      {[...Array(count)].map((_, i) => (
        <div key={i} className="h-56 rounded-xl bg-muted/20 animate-pulse" />
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Section Header                                                     */
/* ------------------------------------------------------------------ */

function SectionHeader({
  icon,
  title,
  subtitle,
}: {
  icon: string;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-xl">{icon}</span>
        <h2 className="font-serif text-xl sm:text-2xl font-semibold text-foreground">
          {title}
        </h2>
        <div className="h-px flex-1 bg-border" />
      </div>
      <p className="text-sm text-muted-foreground">{subtitle}</p>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Main Page                                                          */
/* ------------------------------------------------------------------ */

export default function KidsPage() {
  /* ---- data state ---- */
  const [programs, setPrograms] = useState<KidsProgram[]>([]);
  const [deadlines, setDeadlines] = useState<KidsDeadline[]>([]);
  const [localPlaces, setLocalPlaces] = useState<KidsLocalPlace[]>([]);
  const [loading, setLoading] = useState(true);

  /* ---- shared filter: age ---- */
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedAge = searchParams.get("age") || null;

  const setSelectedAge = useCallback(
    (v: string | null) => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        if (!v) next.delete("age");
        else next.set("age", v);
        return next;
      }, { replace: true });
    },
    [setSearchParams],
  );

  /* ---- local places filters ---- */
  const [localCategory, setLocalCategory] = useState("All");
  const [localCity, setLocalCity] = useState("All");
  const [indianOnly, setIndianOnly] = useState(false);
  const [showAllPlaces, setShowAllPlaces] = useState(false);

  /* ---- programs filters ---- */
  const [programCategory, setProgramCategory] = useState("All");
  const [showAllPrograms, setShowAllPrograms] = useState(false);

  /* ---- location ---- */
  const { location: userLocation } = useUserLocation();

  /* ---- data load ---- */
  useEffect(() => {
    async function load() {
      try {
        const [p, d, lp] = await Promise.all([
          fetchKidsPrograms(),
          fetchKidsDeadlines(50),
          fetchLocalPlaces(),
        ]);
        setPrograms(p);
        setDeadlines(d);
        setLocalPlaces(lp);
      } catch (err) {
        console.error("Failed to load kids data:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  /* ---- compute cities from data ---- */
  const cities = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const p of localPlaces) {
      const c = p.city || "Other";
      counts[c] = (counts[c] || 0) + 1;
    }
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([name, count]) => ({ name, count }));
  }, [localPlaces]);

  /* ---- filtered local places ---- */
  const filteredPlaces = useMemo(() => {
    let list = localPlaces;

    // Age filter
    if (selectedAge) {
      list = list.filter((p) => placeMatchesAge(p.age_range, selectedAge));
    }

    // Category
    if (localCategory !== "All") {
      list = list.filter((p) => p.category === localCategory);
    }

    // City
    if (localCity !== "All") {
      list = list.filter((p) => p.city === localCity);
    }

    // Indian only
    if (indianOnly) {
      list = list.filter((p) => p.is_indian_focused);
    }

    // Add distance if user location available
    if (userLocation?.latitude && userLocation?.longitude) {
      list = list.map((p) => ({
        ...p,
        distance_miles:
          p.latitude && p.longitude
            ? distanceMiles(
                userLocation.latitude,
                userLocation.longitude,
                p.latitude,
                p.longitude,
              )
            : undefined,
      }));
      // Sort by distance (places with distance first, then by rating)
      list.sort((a, b) => {
        if (a.distance_miles != null && b.distance_miles != null) {
          return a.distance_miles - b.distance_miles;
        }
        if (a.distance_miles != null) return -1;
        if (b.distance_miles != null) return 1;
        return (b.rating || 0) - (a.rating || 0);
      });
    }

    return list;
  }, [
    localPlaces,
    selectedAge,
    localCategory,
    localCity,
    indianOnly,
    userLocation,
  ]);

  /* ---- category counts for local places (respecting age/city/indian) ---- */
  const localCatCounts = useMemo(() => {
    let base = localPlaces;
    if (selectedAge) base = base.filter((p) => placeMatchesAge(p.age_range, selectedAge));
    if (localCity !== "All") base = base.filter((p) => p.city === localCity);
    if (indianOnly) base = base.filter((p) => p.is_indian_focused);
    const counts: Record<string, number> = { All: base.length };
    for (const p of base) {
      counts[p.category] = (counts[p.category] || 0) + 1;
    }
    return counts;
  }, [localPlaces, selectedAge, localCity, indianOnly]);

  /* ---- filtered programs ---- */
  const filteredPrograms = useMemo(() => {
    let list = programs;
    if (selectedAge) {
      list = list.filter(
        (p) =>
          Array.isArray(p.age_groups) && p.age_groups.includes(selectedAge),
      );
    }
    if (programCategory !== "All") {
      list = list.filter((p) => p.category === programCategory);
    }
    return list;
  }, [programs, selectedAge, programCategory]);

  /* ---- program category counts ---- */
  const programCatCounts = useMemo(() => {
    let base = programs;
    if (selectedAge) {
      base = base.filter(
        (p) =>
          Array.isArray(p.age_groups) && p.age_groups.includes(selectedAge),
      );
    }
    const counts: Record<string, number> = { All: base.length };
    for (const p of base) {
      const cat = p.category || "Other";
      counts[cat] = (counts[cat] || 0) + 1;
    }
    return counts;
  }, [programs, selectedAge]);

  /* ---- display slices ---- */
  const placesToShow = showAllPlaces
    ? filteredPlaces
    : filteredPlaces.slice(0, PLACES_INITIAL);
  const programsToShow = showAllPrograms
    ? filteredPrograms
    : filteredPrograms.slice(0, PROGRAMS_INITIAL);

  const hasActiveFilters =
    selectedAge !== null ||
    localCategory !== "All" ||
    localCity !== "All" ||
    indianOnly ||
    programCategory !== "All";

  /* ---- reset section filters when age changes ---- */
  useEffect(() => {
    setShowAllPlaces(false);
    setShowAllPrograms(false);
  }, [selectedAge]);

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>Kids &amp; Education — The Videshi</title>
        <meta
          name="description"
          content="Activities, classes, programs & competitions for K-12 students in the Indian American community. Find what's right for your child."
        />
        <link rel="canonical" href="https://www.thevideshi.com/kids" />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main
        className="container flex-1 pt-8 md:pt-10 pb-16"
        style={{ maxWidth: 1200 }}
      >
        {/* ═══════════ PAGE HEADER ═══════════ */}
        <div className="mb-10 md:mb-12">
          <h1 className="font-serif text-3xl md:text-5xl text-foreground mb-3">
            🎓 Kids &amp; Education
          </h1>
          <p className="text-muted-foreground text-base sm:text-lg max-w-2xl leading-relaxed">
            Everything for your child's growth — from activities near you to
            competitions they'll thrive in
          </p>
        </div>

        {/* ═══════════ AGE SELECTOR ═══════════ */}
        <div className="mb-10">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
            My child is in
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {AGE_GROUPS.map((ag) => {
              const active = selectedAge === ag.key;
              return (
                <button
                  key={ag.key}
                  onClick={() => setSelectedAge(active ? null : ag.key)}
                  className={`relative rounded-xl border-2 p-4 sm:p-5 text-left transition-all hover:shadow-md ${
                    active
                      ? "border-[#D4A843] bg-[#D4A843]/5 shadow-sm"
                      : "border-border bg-card hover:border-[#D4A843]/40"
                  }`}
                >
                  <span className="text-2xl sm:text-3xl block mb-2">
                    {ag.icon}
                  </span>
                  <h3 className="font-serif text-sm sm:text-base font-semibold text-foreground leading-snug">
                    {ag.label}
                  </h3>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {ag.sub}
                  </p>
                </button>
              );
            })}
          </div>
          {selectedAge && (
            <button
              onClick={() => setSelectedAge(null)}
              className="mt-3 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              ✕ Show all ages
            </button>
          )}
        </div>

        {/* ═══════════ CLOSING SOON ═══════════ */}
        {!loading && (
          <ClosingSoonStrip deadlines={deadlines} selectedAge={selectedAge} />
        )}

        {/* ═══════════ NEAR YOU ═══════════ */}
        <section className="mb-14">
          <SectionHeader
            icon="📍"
            title="Classes & Activities Near You"
            subtitle="Local programs, classes & activities in the Bay Area"
          />

          {loading ? (
            <GridSkeleton count={6} />
          ) : (
            <>
              {/* Category pills */}
              <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide mb-3">
                {LOCAL_CATEGORIES.filter(
                  (c) => c.key === "All" || (localCatCounts[c.key] || 0) > 0,
                ).map((cat) => (
                  <FilterPill
                    key={cat.key}
                    label={cat.key}
                    icon={cat.icon}
                    active={localCategory === cat.key}
                    count={localCatCounts[cat.key]}
                    onClick={() => {
                      setLocalCategory(cat.key);
                      setShowAllPlaces(false);
                    }}
                  />
                ))}
              </div>

              {/* City pills + Indian toggle */}
              <div className="flex flex-wrap items-center gap-2 mb-6">
                <div className="flex gap-2 overflow-x-auto scrollbar-hide">
                  <FilterPill
                    label="All Bay Area"
                    active={localCity === "All"}
                    onClick={() => {
                      setLocalCity("All");
                      setShowAllPlaces(false);
                    }}
                    color="#0B1D3A"
                  />
                  {cities.slice(0, 8).map((c) => (
                    <FilterPill
                      key={c.name}
                      label={c.name}
                      active={localCity === c.name}
                      count={c.count}
                      onClick={() => {
                        setLocalCity(c.name);
                        setShowAllPlaces(false);
                      }}
                      color="#0B1D3A"
                    />
                  ))}
                </div>

                <button
                  onClick={() => {
                    setIndianOnly(!indianOnly);
                    setShowAllPlaces(false);
                  }}
                  className={`flex-shrink-0 ml-auto px-3 py-1.5 text-xs font-medium rounded-full border transition-colors whitespace-nowrap ${
                    indianOnly
                      ? "bg-orange-600 text-white border-transparent"
                      : "bg-card text-muted-foreground border-border hover:border-orange-300 hover:text-orange-700"
                  }`}
                >
                  🇮🇳 Indian Community
                </button>
              </div>

              {/* Results count */}
              <p className="text-sm text-muted-foreground mb-5">
                Showing{" "}
                <span className="font-semibold text-foreground">
                  {showAllPlaces
                    ? filteredPlaces.length
                    : Math.min(filteredPlaces.length, PLACES_INITIAL)}
                </span>
                {!showAllPlaces && filteredPlaces.length > PLACES_INITIAL && (
                  <span> of {filteredPlaces.length}</span>
                )}{" "}
                {filteredPlaces.length === 1 ? "place" : "places"}
                {localCategory !== "All" && ` in ${localCategory}`}
                {localCity !== "All" && ` · ${localCity}`}
              </p>

              {filteredPlaces.length === 0 ? (
                <div className="text-center py-12 rounded-xl bg-muted/10 border border-dashed border-border">
                  <p className="text-3xl mb-3">🔍</p>
                  <p className="text-muted-foreground text-sm mb-1">
                    No places match your current filters
                  </p>
                  <button
                    onClick={() => {
                      setLocalCategory("All");
                      setLocalCity("All");
                      setIndianOnly(false);
                    }}
                    className="mt-3 text-xs font-medium hover:underline"
                    style={{ color: "#A32D2F" }}
                  >
                    Clear filters
                  </button>
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
                    {placesToShow.map((p) => (
                      <LocalPlaceCard
                        key={p.id}
                        place={p}
                        userLat={userLocation?.latitude}
                        userLng={userLocation?.longitude}
                      />
                    ))}
                  </div>

                  {filteredPlaces.length > PLACES_INITIAL && (
                    <div className="text-center mt-6">
                      <button
                        onClick={() => setShowAllPlaces(!showAllPlaces)}
                        className="px-6 py-2.5 rounded-lg text-sm font-semibold border border-border hover:border-foreground/30 bg-card hover:shadow-sm transition-all"
                      >
                        {showAllPlaces
                          ? "Show fewer"
                          : `Show all ${filteredPlaces.length} places`}
                      </button>
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </section>

        {/* ═══════════ PROGRAMS & COMPETITIONS ═══════════ */}
        <section className="mb-14">
          <SectionHeader
            icon="🏆"
            title="Programs & Competitions"
            subtitle="National competitions and organizations your child can join"
          />

          {loading ? (
            <GridSkeleton count={6} />
          ) : (
            <>
              {/* Category pills */}
              <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide mb-6">
                {PROGRAM_CATEGORIES.filter(
                  (c) =>
                    c.key === "All" || (programCatCounts[c.key] || 0) > 0,
                ).map((cat) => (
                  <FilterPill
                    key={cat.key}
                    label={cat.key}
                    icon={cat.icon}
                    active={programCategory === cat.key}
                    count={programCatCounts[cat.key]}
                    onClick={() => {
                      setProgramCategory(cat.key);
                      setShowAllPrograms(false);
                    }}
                    color="#A32D2F"
                  />
                ))}
              </div>

              {/* Results count */}
              <p className="text-sm text-muted-foreground mb-5">
                Showing{" "}
                <span className="font-semibold text-foreground">
                  {showAllPrograms
                    ? filteredPrograms.length
                    : Math.min(filteredPrograms.length, PROGRAMS_INITIAL)}
                </span>
                {!showAllPrograms &&
                  filteredPrograms.length > PROGRAMS_INITIAL && (
                    <span> of {filteredPrograms.length}</span>
                  )}{" "}
                {filteredPrograms.length === 1 ? "program" : "programs"}
                {programCategory !== "All" && ` in ${programCategory}`}
              </p>

              {filteredPrograms.length === 0 ? (
                <div className="text-center py-12 rounded-xl bg-muted/10 border border-dashed border-border">
                  <p className="text-3xl mb-3">📭</p>
                  <p className="text-muted-foreground text-sm mb-1">
                    No programs match your current filters
                  </p>
                  <button
                    onClick={() => setProgramCategory("All")}
                    className="mt-3 text-xs font-medium hover:underline"
                    style={{ color: "#A32D2F" }}
                  >
                    Show all programs
                  </button>
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
                    {programsToShow.map((p) => (
                      <ProgramCard key={p.id} program={p} />
                    ))}
                  </div>

                  {filteredPrograms.length > PROGRAMS_INITIAL && (
                    <div className="text-center mt-6">
                      <button
                        onClick={() => setShowAllPrograms(!showAllPrograms)}
                        className="px-6 py-2.5 rounded-lg text-sm font-semibold border border-border hover:border-foreground/30 bg-card hover:shadow-sm transition-all"
                      >
                        {showAllPrograms
                          ? "Show fewer"
                          : `Show all ${filteredPrograms.length} programs`}
                      </button>
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </section>

        {/* ═══════════ PARENT READS (coming soon) ═══════════ */}
        <section className="mb-10">
          <SectionHeader
            icon="📰"
            title="Guides for Parents"
            subtitle="Expert guides to help you navigate your child's educational journey"
          />
          <div className="text-center py-12 rounded-xl bg-muted/5 border border-dashed border-border">
            <p className="text-3xl mb-3">📚</p>
            <p className="text-muted-foreground text-sm">
              Coming soon — guides on competitions, college prep, extracurriculars & more
            </p>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
