import { useState, useEffect, useMemo, useRef } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
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

/* ------------------------------------------------------------------ */
/* Constants                                                          */
/* ------------------------------------------------------------------ */

const CATEGORIES = [
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

const CATEGORY_COLORS: Record<string, string> = {
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
  "Summer Camps": "bg-orange-100 text-orange-700",
};

const AGE_GROUPS = [
  { key: "preschool", label: "Preschool", sub: "Ages 3–5", icon: "🧒" },
  { key: "elementary", label: "Elementary", sub: "Grades K–5", icon: "📖" },
  { key: "middle_school", label: "Middle School", sub: "Grades 6–8", icon: "🔬" },
  { key: "high_school", label: "High School", sub: "Grades 9–12", icon: "🎓" },
];

type LocationFilter = "all" | "online" | "nearme";

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

function daysUntil(dateStr: string): number {
  const target = new Date(dateStr + "T00:00:00");
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

/** Check if a program matches the "online" location filter */
function isOnlineProgram(p: KidsProgram): boolean {
  const fmt = (p.format || "").toLowerCase();
  const loc = (p.locations || "").toLowerCase();
  return fmt === "online" || fmt === "hybrid" || loc.includes("online");
}

/** Check if a program is available in a given US state (or "nationwide") */
function isNearUser(p: KidsProgram, userState: string | undefined): boolean {
  if (!userState) return true; // can't filter without state
  const loc = (p.locations || "").toLowerCase();
  const fmt = (p.format || "").toLowerCase();
  const st = userState.toLowerCase();
  return (
    loc.includes(st) ||
    loc.includes("nationwide") ||
    loc.includes("national") ||
    loc.includes("all states") ||
    fmt === "online" ||
    fmt === "hybrid" ||
    loc.includes("online")
  );
}

/* ------------------------------------------------------------------ */
/* Closing-Soon Strip                                                 */
/* ------------------------------------------------------------------ */

function ClosingSoonStrip({ deadlines }: { deadlines: KidsDeadline[] }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const urgent = deadlines.filter((d) => {
    const days = daysUntil(d.deadline_date);
    return days >= 0 && days <= 14;
  }).slice(0, 5);

  if (urgent.length === 0) return null;

  return (
    <section className="mb-10">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-lg">🔔</span>
        <h2 className="font-serif text-lg font-semibold text-foreground">
          Closing Soon
        </h2>
        <div className="h-px flex-1 bg-border" />
      </div>

      <div
        ref={scrollRef}
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
/* Program Card                                                       */
/* ------------------------------------------------------------------ */

function ProgramCard({ program }: { program: KidsProgram }) {
  const catColor =
    CATEGORY_COLORS[program.category || ""] || "bg-gray-100 text-gray-700";

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
        {/* Badges row */}
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

        {/* Title */}
        <h3 className="font-serif text-base sm:text-[17px] font-semibold text-foreground leading-snug line-clamp-2 group-hover:text-[#A32D2F] transition-colors mb-1.5">
          {program.name}
        </h3>

        {/* Organization */}
        {program.organization && (
          <p className="text-xs text-muted-foreground mb-3 truncate">
            {program.organization}
          </p>
        )}

        {/* Category pill */}
        {program.category && (
          <div className="mb-3">
            <span
              className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-medium ${catColor}`}
            >
              {program.category}
            </span>
          </div>
        )}

        {/* Meta row */}
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground mb-3">
          {program.age_range && <span>🎒 {program.age_range}</span>}
          {program.format && <span>📍 {program.format}</span>}
          {program.cost && <span>💰 {program.cost}</span>}
        </div>

        {/* Description */}
        {program.description && (
          <p className="text-sm text-muted-foreground line-clamp-3 mb-4 flex-1">
            {program.description}
          </p>
        )}

        {/* CTA */}
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
/* Loading Skeleton                                                   */
/* ------------------------------------------------------------------ */

function GridSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
      {[...Array(6)].map((_, i) => (
        <div
          key={i}
          className="h-56 rounded-xl bg-muted/20 animate-pulse"
        />
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Results Summary                                                    */
/* ------------------------------------------------------------------ */

function ResultsSummary({
  count,
  ageGroup,
  category,
  locationFilter,
  userState,
}: {
  count: number;
  ageGroup: string | null;
  category: string;
  locationFilter: LocationFilter;
  userState: string | undefined;
}) {
  const parts: string[] = [];
  if (category !== "All") parts.push(category);
  if (ageGroup) {
    const ag = AGE_GROUPS.find((a) => a.key === ageGroup);
    if (ag) parts.push(`for ${ag.label}`);
  }
  if (locationFilter === "online") parts.push("· Online");
  if (locationFilter === "nearme" && userState)
    parts.push(`· Near ${userState}`);

  const label = parts.length > 0 ? parts.join(" ") : "";

  return (
    <p className="text-sm text-muted-foreground mb-6">
      Showing{" "}
      <span className="font-semibold text-foreground">{count}</span>{" "}
      {count === 1 ? "program" : "programs"}
      {label ? ` ${label}` : ""}
    </p>
  );
}

/* ------------------------------------------------------------------ */
/* Main Page                                                          */
/* ------------------------------------------------------------------ */

export default function KidsPage() {
  const [programs, setPrograms] = useState<KidsProgram[]>([]);
  const [deadlines, setDeadlines] = useState<KidsDeadline[]>([]);
  const [loading, setLoading] = useState(true);

  const [selectedAge, setSelectedAge] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [locationFilter, setLocationFilter] = useState<LocationFilter>("all");

  const { location: userLocation } = useUserLocation();
  const userState = userLocation?.region;

  /* ---- data load ---- */
  useEffect(() => {
    async function load() {
      try {
        const [p, d] = await Promise.all([
          fetchKidsPrograms(),
          fetchKidsDeadlines(50),
        ]);
        setPrograms(p);
        setDeadlines(d);
      } catch (err) {
        console.error("Failed to load kids data:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  /* ---- filtering ---- */
  const filteredPrograms = useMemo(() => {
    let list = programs;

    // Age group
    if (selectedAge) {
      list = list.filter(
        (p) =>
          Array.isArray(p.age_groups) && p.age_groups.includes(selectedAge),
      );
    }

    // Category
    if (selectedCategory !== "All") {
      list = list.filter((p) => p.category === selectedCategory);
    }

    // Location
    if (locationFilter === "online") {
      list = list.filter(isOnlineProgram);
    } else if (locationFilter === "nearme") {
      list = list.filter((p) => isNearUser(p, userState));
    }

    return list;
  }, [programs, selectedAge, selectedCategory, locationFilter, userState]);

  /* ---- dynamic category counts (respecting age + location filters) ---- */
  const categoryCounts = useMemo(() => {
    let base = programs;
    if (selectedAge) {
      base = base.filter(
        (p) =>
          Array.isArray(p.age_groups) && p.age_groups.includes(selectedAge),
      );
    }
    if (locationFilter === "online") {
      base = base.filter(isOnlineProgram);
    } else if (locationFilter === "nearme") {
      base = base.filter((p) => isNearUser(p, userState));
    }
    const counts: Record<string, number> = { All: base.length };
    for (const p of base) {
      const cat = p.category || "Other";
      counts[cat] = (counts[cat] || 0) + 1;
    }
    return counts;
  }, [programs, selectedAge, locationFilter, userState]);

  /* ---- clear all filters ---- */
  const hasActiveFilters =
    selectedAge !== null ||
    selectedCategory !== "All" ||
    locationFilter !== "all";

  function clearFilters() {
    setSelectedAge(null);
    setSelectedCategory("All");
    setLocationFilter("all");
  }

  const categoryScrollRef = useRef<HTMLDivElement>(null);

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>Kids &amp; Education — The Videshi</title>
        <meta
          name="description"
          content="Programs, competitions, camps & resources for K-12 students in the Indian American community. Filter by age, category, and location."
        />
        <link rel="canonical" href="https://www.thevideshi.com/kids" />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main
        className="container flex-1 pt-8 md:pt-10 pb-16"
        style={{ maxWidth: 1200 }}
      >
        {/* ───────── PAGE HEADER ───────── */}
        <div className="mb-10 md:mb-12">
          <h1 className="font-serif text-3xl md:text-5xl text-foreground mb-3">
            🎓 Kids &amp; Education
          </h1>
          <p className="text-muted-foreground text-base sm:text-lg max-w-2xl leading-relaxed">
            Programs, competitions, cultural activities &amp; resources for
            K-12 students in the Indian American community
          </p>
        </div>

        {/* ───────── FILTER BAR ───────── */}
        <div className="mb-8 space-y-5">
          {/* Row 1: Age group — icon cards */}
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Age Group
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
                    <span className="text-2xl sm:text-3xl block mb-2">{ag.icon}</span>
                    <h3 className="font-serif text-sm sm:text-base font-semibold text-foreground leading-snug">
                      {ag.label}
                    </h3>
                    <p className="text-xs text-muted-foreground mt-0.5">{ag.sub}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Row 2: Category pills — horizontal scroll on mobile */}
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2.5">
              Category
            </p>
            <div
              ref={categoryScrollRef}
              className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide"
            >
              {CATEGORIES.map((cat) => {
                const active = selectedCategory === cat.key;
                const count = categoryCounts[cat.key] ?? 0;
                return (
                  <button
                    key={cat.key}
                    onClick={() => setSelectedCategory(cat.key)}
                    className={`flex-shrink-0 px-3 py-1.5 text-xs font-medium rounded-full border transition-colors whitespace-nowrap ${
                      active
                        ? "text-white border-[#A32D2F]"
                        : "bg-card text-muted-foreground border-border hover:border-foreground/30 hover:text-foreground"
                    }`}
                    style={
                      active ? { backgroundColor: "#A32D2F" } : undefined
                    }
                  >
                    {cat.icon} {cat.key}
                    {count > 0 && (
                      <span className="ml-1 opacity-70">({count})</span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Row 3: Location filter */}
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2.5">
              Availability
            </p>
            <div className="flex gap-2">
              {(
                [
                  { key: "all" as const, label: "All Locations" },
                  { key: "online" as const, label: "Online" },
                  {
                    key: "nearme" as const,
                    label: userState ? `Near Me · ${userState}` : "Near Me",
                  },
                ] as const
              ).map((opt) => {
                const active = locationFilter === opt.key;
                return (
                  <button
                    key={opt.key}
                    onClick={() => setLocationFilter(opt.key)}
                    className={`px-3.5 py-1.5 text-xs font-medium rounded-full border transition-colors whitespace-nowrap ${
                      active
                        ? "text-white border-[#0B1D3A]"
                        : "bg-card text-muted-foreground border-border hover:border-foreground/30 hover:text-foreground"
                    }`}
                    style={
                      active && opt.key !== "all"
                        ? { backgroundColor: "#0B1D3A" }
                        : active
                        ? { backgroundColor: "#0B1D3A" }
                        : undefined
                    }
                  >
                  {opt.key === "all" && "🌐 "}
                    {opt.key === "online" && "💻 "}
                    {opt.key === "nearme" && "📍 "}
                    {opt.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Clear filters */}
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              ✕ Clear all filters
            </button>
          )}
        </div>

        {/* ───────── CLOSING SOON STRIP ───────── */}
        {!loading && <ClosingSoonStrip deadlines={deadlines} />}

        {/* ───────── RESULTS ───────── */}
        <section>
          {loading ? (
            <GridSkeleton />
          ) : (
            <>
              <ResultsSummary
                count={filteredPrograms.length}
                ageGroup={selectedAge}
                category={selectedCategory}
                locationFilter={locationFilter}
                userState={userState}
              />

              {filteredPrograms.length === 0 ? (
                <div className="text-center py-20">
                  <p className="text-4xl mb-4">📭</p>
                  <p className="text-muted-foreground text-base mb-1">
                    No programs match your current filters
                  </p>
                  <p className="text-muted-foreground text-sm mb-5 opacity-70">
                    Try broadening your age group, category, or location
                  </p>
                  <button
                    onClick={clearFilters}
                    className="px-5 py-2 rounded-lg text-sm font-semibold text-white transition-colors"
                    style={{ backgroundColor: "#A32D2F" }}
                  >
                    Show All Programs
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
                  {filteredPrograms.map((p) => (
                    <ProgramCard key={p.id} program={p} />
                  ))}
                </div>
              )}
            </>
          )}
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
