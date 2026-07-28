import { useState, useEffect, useMemo } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  fetchKidsPrograms,
  fetchKidsDeadlines,
  fetchKidsCamps,
  type KidsProgram,
  type KidsDeadline,
  type KidsCamp,
} from "@/lib/kidsPrograms";

/* ------------------------------------------------------------------ */
/* Constants                                                          */
/* ------------------------------------------------------------------ */

const PROGRAM_CATEGORIES = [
  "All",
  "Academic Competitions",
  "Math",
  "Science & STEM",
  "Robotics",
  "Coding & CS",
  "Chess",
  "College Prep",
  "Summer Programs",
  "Sports",
  "Dance",
  "Music",
  "Language",
  "Cultural & Arts",
  "Cultural & Religious",
  "Volunteering",
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
  { key: "preschool", label: "Preschool", ages: "Ages 3–5", emoji: "🧒" },
  { key: "elementary", label: "Elementary", ages: "Grades K–5", emoji: "📖" },
  { key: "middle_school", label: "Middle School", ages: "Grades 6–8", emoji: "🔬" },
  { key: "high_school", label: "High School", ages: "Grades 9–12", emoji: "🎓" },
];

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

function daysUntil(dateStr: string): number {
  const target = new Date(dateStr + "T00:00:00");
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

function urgencyClass(days: number): string {
  if (days <= 7) return "bg-red-100 text-red-700 border-red-200";
  if (days <= 30) return "bg-amber-100 text-amber-700 border-amber-200";
  return "bg-green-100 text-green-700 border-green-200";
}

function urgencyDot(days: number): string {
  if (days <= 7) return "bg-red-500";
  if (days <= 30) return "bg-amber-500";
  return "bg-green-500";
}

function formatDeadlineDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatCampDate(dateStr: string, endDateStr?: string | null): string {
  const d = new Date(dateStr + "T00:00:00");
  const opts: Intl.DateTimeFormatOptions = {
    month: "short",
    day: "numeric",
  };
  const formatted = d.toLocaleDateString("en-US", opts);
  if (endDateStr && endDateStr !== dateStr) {
    const end = new Date(endDateStr + "T00:00:00");
    const endFormatted = end.toLocaleDateString("en-US", opts);
    return `${formatted} – ${endFormatted}`;
  }
  return formatted;
}

/* ------------------------------------------------------------------ */
/* Deadline Card                                                      */
/* ------------------------------------------------------------------ */

function DeadlineCard({ deadline }: { deadline: KidsDeadline }) {
  const days = daysUntil(deadline.deadline_date);
  const urgency = urgencyClass(days);
  const dot = urgencyDot(days);

  const countdownText =
    days === 0
      ? "Today!"
      : days === 1
      ? "Tomorrow!"
      : `${days} days left`;

  return (
    <div
      className={`rounded-lg border p-4 sm:p-5 transition-all hover:shadow-md ${urgency}`}
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-serif text-base sm:text-lg font-semibold leading-snug line-clamp-2">
            {deadline.program_name || deadline.title}
          </h3>
          {deadline.program_name && deadline.title !== deadline.program_name && (
            <p className="text-sm opacity-80 mt-0.5 line-clamp-1">
              {deadline.title}
            </p>
          )}
        </div>
        <span
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold whitespace-nowrap flex-shrink-0`}
        >
          <span className={`w-2 h-2 rounded-full ${dot} ${days <= 7 ? "animate-pulse" : ""}`} />
          {countdownText}
        </span>
      </div>

      <div className="flex flex-wrap gap-x-4 gap-y-1.5 text-sm mb-3">
        <span className="font-medium">
          📅 {formatDeadlineDate(deadline.deadline_date)}
        </span>
        {deadline.grade_range && (
          <span className="opacity-80">🎒 Grades {deadline.grade_range}</span>
        )}
        {deadline.cost && (
          <span className="opacity-80">💰 {deadline.cost}</span>
        )}
        {deadline.program_category && (
          <span className="opacity-70">📂 {deadline.program_category}</span>
        )}
      </div>

      {deadline.description && (
        <p className="text-sm opacity-75 line-clamp-2 mb-3">
          {deadline.description}
        </p>
      )}

      {deadline.registration_url && (
        <a
          href={deadline.registration_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
          style={{ backgroundColor: "#A32D2F", color: "#fff" }}
        >
          Register →
        </a>
      )}
    </div>
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
        className={`group rounded-lg border bg-card p-4 sm:p-5 transition-all hover:shadow-md hover:border-[#D4A843]/50 flex flex-col h-full ${
          program.is_featured ? "ring-1 ring-[#D4A843]/40" : "border-border"
        }`}
      >
        {program.is_featured && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-600 text-[10px] font-semibold mb-2 w-fit">
            ⭐ Featured
          </span>
        )}
        <h3 className="font-serif text-base font-semibold text-foreground leading-snug line-clamp-2 group-hover:text-[#A32D2F] transition-colors mb-1.5">
          {program.name}
        </h3>
        {program.organization && (
          <p className="text-xs text-muted-foreground mb-2 truncate">
            {program.organization}
          </p>
        )}

        <div className="flex flex-wrap gap-1.5 mb-2">
          {program.category && (
            <span
              className={`inline-block px-2 py-0.5 rounded text-[11px] font-medium ${catColor}`}
            >
              {program.category}
            </span>
          )}
          {program.is_indian_org && (
            <span className="inline-block px-2 py-0.5 rounded text-[11px] font-medium bg-orange-100 text-orange-700">
              🇮🇳 Indian Community
            </span>
          )}
        </div>

        {program.grade_range && (
          <p className="text-xs text-muted-foreground mb-1.5">
            🎒 Grades {program.grade_range}
          </p>
        )}

        {program.description && (
          <p className="text-sm text-muted-foreground line-clamp-3 mb-3 flex-1">
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
/* Camp Card                                                          */
/* ------------------------------------------------------------------ */

function CampCard({ camp }: { camp: KidsCamp }) {
  const inner = (
    <div className="group rounded-lg border border-border bg-card p-3 sm:p-4 transition-all hover:shadow-sm hover:border-[#D4A843]/40 flex items-start gap-3">
      <div
        className="flex-shrink-0 w-12 h-12 rounded-lg flex flex-col items-center justify-center text-center"
        style={{ backgroundColor: "#0B1D3A", color: "#D4A843" }}
      >
        <span className="text-[10px] font-bold leading-none uppercase">
          {new Date(camp.date + "T00:00:00").toLocaleDateString("en-US", {
            month: "short",
          })}
        </span>
        <span className="text-lg font-bold leading-none">
          {new Date(camp.date + "T00:00:00").getDate()}
        </span>
      </div>

      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-sm text-foreground leading-snug line-clamp-2 group-hover:text-[#A32D2F] transition-colors">
          {camp.title}
        </h4>
        <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-xs text-muted-foreground mt-1">
          <span>{formatCampDate(camp.date, camp.end_date)}</span>
          {camp.location && (
            <span className="truncate">📍 {camp.location}</span>
          )}
          {camp.age_range && <span>👦 {camp.age_range}</span>}
          {camp.cost && <span>💰 {camp.cost}</span>}
        </div>
      </div>
    </div>
  );

  if (camp.url) {
    return (
      <a
        href={camp.url}
        target="_blank"
        rel="noopener noreferrer"
        className="block no-underline"
      >
        {inner}
      </a>
    );
  }

  return inner;
}

/* ------------------------------------------------------------------ */
/* Empty States                                                       */
/* ------------------------------------------------------------------ */

function EmptyDeadlines() {
  return (
    <div className="text-center py-12 px-4 rounded-lg border border-dashed border-border">
      <p className="text-3xl mb-3">📋</p>
      <p className="text-muted-foreground text-base">
        Check back soon — new deadlines are added regularly
      </p>
      <p className="text-muted-foreground text-sm mt-1 opacity-70">
        Registration windows for competitions and programs open throughout the year
      </p>
    </div>
  );
}

function EmptyCamps() {
  return (
    <div className="text-center py-10 px-4 rounded-lg border border-dashed border-border">
      <p className="text-2xl mb-2">🏕️</p>
      <p className="text-muted-foreground text-sm">
        Summer camp listings will be updated seasonally
      </p>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Loading Skeletons                                                  */
/* ------------------------------------------------------------------ */

function DeadlineSkeleton() {
  return (
    <div className="space-y-4">
      {[...Array(3)].map((_, i) => (
        <div
          key={i}
          className="h-32 rounded-lg bg-muted/20 animate-pulse"
        />
      ))}
    </div>
  );
}

function ProgramSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {[...Array(6)].map((_, i) => (
        <div
          key={i}
          className="h-48 rounded-lg bg-muted/20 animate-pulse"
        />
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Section Header                                                     */
/* ------------------------------------------------------------------ */

function SectionHeader({
  title,
  subtitle,
}: {
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="mb-5">
      <div className="flex items-center gap-3 mb-1">
        <h2 className="font-serif text-xl md:text-2xl text-foreground whitespace-nowrap">
          {title}
        </h2>
        <div className="h-px flex-1 bg-border" />
      </div>
      {subtitle && (
        <p className="text-sm text-muted-foreground">{subtitle}</p>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Kids Page                                                          */
/* ------------------------------------------------------------------ */

export default function KidsPage() {
  const [programs, setPrograms] = useState<KidsProgram[]>([]);
  const [deadlines, setDeadlines] = useState<KidsDeadline[]>([]);
  const [camps, setCamps] = useState<KidsCamp[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedAgeGroup, setSelectedAgeGroup] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [programsData, deadlinesData, campsData] = await Promise.all([
          fetchKidsPrograms(),
          fetchKidsDeadlines(20),
          fetchKidsCamps(),
        ]);
        setPrograms(programsData);
        setDeadlines(deadlinesData);
        setCamps(campsData);
      } catch (err) {
        console.error("Failed to load kids page data:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  /* Category + age group filter */
  const filteredPrograms = useMemo(() => {
    let filtered = programs;
    if (selectedCategory !== "All") {
      filtered = filtered.filter((p) => p.category === selectedCategory);
    }
    if (selectedAgeGroup) {
      filtered = filtered.filter(
        (p) =>
          Array.isArray(p.age_groups) &&
          p.age_groups.includes(selectedAgeGroup)
      );
    }
    return filtered;
  }, [programs, selectedCategory, selectedAgeGroup]);

  /* Category counts */
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { All: programs.length };
    for (const p of programs) {
      const cat = p.category || "Other";
      counts[cat] = (counts[cat] || 0) + 1;
    }
    return counts;
  }, [programs]);

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>Kids &amp; Education — The Videshi</title>
        <meta
          name="description"
          content="Academic competitions, STEM programs, cultural camps & more for K-12 students in the Indian American community."
        />
        <link rel="canonical" href="https://www.thevideshi.com/kids" />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container flex-1 pt-8 md:pt-10 pb-16" style={{ maxWidth: 1200 }}>
        {/* Page Header */}
        <div className="mb-12">
          <h1 className="font-serif text-3xl md:text-5xl text-foreground mb-2">
            🎓 Kids &amp; Education
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl">
            Academic competitions, STEM programs, cultural camps &amp; more for
            K-12 students
          </p>
        </div>

        {/* ───────── AGE GROUP CARDS ───────── */}
        <section className="mb-14">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-5">
            {AGE_GROUPS.map((ag) => {
              const count = programs.filter(
                (p) =>
                  Array.isArray(p.age_groups) &&
                  p.age_groups.includes(ag.key)
              ).length;
              return (
                <button
                  key={ag.key}
                  onClick={() => {
                    setSelectedAgeGroup(
                      selectedAgeGroup === ag.key ? null : ag.key
                    );
                    setSelectedCategory("All");
                  }}
                  className={`group relative rounded-xl border-2 p-5 sm:p-6 text-left transition-all hover:shadow-lg ${
                    selectedAgeGroup === ag.key
                      ? "border-[#D4A843] bg-[#D4A843]/5 shadow-md"
                      : "border-border bg-card hover:border-[#D4A843]/40"
                  }`}
                >
                  <span className="text-3xl sm:text-4xl block mb-3">
                    {ag.emoji}
                  </span>
                  <h3 className="font-serif text-base sm:text-lg font-semibold text-foreground leading-snug mb-1">
                    {ag.label}
                  </h3>
                  <p className="text-xs sm:text-sm text-muted-foreground">
                    {ag.ages}
                  </p>
                  {count > 0 && (
                    <span className="absolute top-3 right-3 px-2 py-0.5 rounded-full text-[10px] font-bold bg-muted/30 text-muted-foreground">
                      {count}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
          {selectedAgeGroup && (
            <div className="mt-3 text-center">
              <button
                onClick={() => setSelectedAgeGroup(null)}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                ✕ Clear age filter
              </button>
            </div>
          )}
        </section>

        {/* ───────── SECTION 1: Registration Deadlines ───────── */}
        <section className="mb-14">
          <SectionHeader
            title="⏰ Upcoming Deadlines"
            subtitle="Don't miss these registration windows — sorted by urgency"
          />

          {loading ? (
            <DeadlineSkeleton />
          ) : deadlines.length === 0 ? (
            <EmptyDeadlines />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {deadlines.map((d) => (
                <DeadlineCard key={d.id} deadline={d} />
              ))}
            </div>
          )}
        </section>

        {/* ───────── SECTION 2: Programs Directory ───────── */}
        <section className="mb-14">
          <SectionHeader
            title="📚 Browse Programs"
            subtitle="Find the right program for your child"
          />

          {/* Category filter pills */}
          <div className="flex flex-wrap gap-2 mb-6">
            {PROGRAM_CATEGORIES.map((cat) => {
              const isActive = selectedCategory === cat;
              const count = categoryCounts[cat] || 0;
              return (
                <button
                  key={cat}
                  onClick={() => {
                    setSelectedCategory(cat);
                    if (cat !== "All") setSelectedAgeGroup(null);
                  }}
                  className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors whitespace-nowrap ${
                    isActive
                      ? "text-white border-[#A32D2F]"
                      : "bg-background text-muted-foreground border-border hover:border-foreground/30 hover:text-foreground"
                  }`}
                  style={isActive ? { backgroundColor: "#A32D2F" } : undefined}
                >
                  {cat}
                  {count > 0 && (
                    <span className="ml-1 opacity-70">({count})</span>
                  )}
                </button>
              );
            })}
          </div>

          {loading ? (
            <ProgramSkeleton />
          ) : filteredPrograms.length === 0 ? (
            <div className="text-center py-14">
              <p className="text-3xl mb-3">📖</p>
              <p className="text-muted-foreground">
                {selectedCategory === "All" && !selectedAgeGroup
                  ? "Programs coming soon — check back!"
                  : selectedAgeGroup
                  ? `No programs found for this age group${selectedCategory !== "All" ? ` in ${selectedCategory}` : ""}`
                  : `No ${selectedCategory} programs listed yet`}
              </p>
              {(selectedAgeGroup || selectedCategory !== "All") && (
                <button
                  onClick={() => { setSelectedCategory("All"); setSelectedAgeGroup(null); }}
                  className="mt-3 text-sm text-[#A32D2F] hover:underline"
                >
                  Clear all filters
                </button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredPrograms.map((p) => (
                <ProgramCard key={p.id} program={p} />
              ))}
            </div>
          )}
        </section>

        {/* ───────── SECTION 3: Camps & Workshops ───────── */}
        <section className="mb-8">
          <SectionHeader
            title="🏕️ Camps &amp; Workshops"
            subtitle="Summer camps, coding bootcamps, cultural workshops & more"
          />

          {loading ? (
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => (
                <div
                  key={i}
                  className="h-20 rounded-lg bg-muted/20 animate-pulse"
                />
              ))}
            </div>
          ) : camps.length === 0 ? (
            <EmptyCamps />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {camps.map((c) => (
                <CampCard key={c.id} camp={c} />
              ))}
            </div>
          )}
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
