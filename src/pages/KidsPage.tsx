import { useState, useEffect, useMemo } from "react";
import { Helmet } from "react-helmet-async";
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
  "Cultural & Arts",
  "Language",
];

const CATEGORY_COLORS: Record<string, string> = {
  "Academic Competitions": "bg-blue-100 text-blue-700",
  Math: "bg-indigo-100 text-indigo-700",
  "Science & STEM": "bg-emerald-100 text-emerald-700",
  Robotics: "bg-cyan-100 text-cyan-700",
  "Cultural & Arts": "bg-purple-100 text-purple-700",
  Language: "bg-amber-100 text-amber-700",
};

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

  const card = (
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
  );

  if (program.website_url) {
    return (
      <a
        href={program.website_url}
        target="_blank"
        rel="noopener noreferrer"
        className="block no-underline h-full"
      >
        {card}
      </a>
    );
  }

  return card;
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

  /* Category filter */
  const filteredPrograms = useMemo(() => {
    if (selectedCategory === "All") return programs;
    return programs.filter((p) => p.category === selectedCategory);
  }, [programs, selectedCategory]);

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
        <div className="mb-10">
          <h1 className="font-serif text-3xl md:text-5xl text-foreground mb-2">
            🎓 Kids &amp; Education
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl">
            Academic competitions, STEM programs, cultural camps &amp; more for
            K-12 students
          </p>
        </div>

        {/* ───────── SECTION 1: Registration Deadlines ───────── */}
        <section className="mb-12">
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
        <section className="mb-12">
          <SectionHeader
            title="📚 Browse Programs"
            subtitle="Find the right program for your child"
          />

          {/* Category filter pills */}
          <div className="flex flex-wrap gap-2 mb-5">
            {PROGRAM_CATEGORIES.map((cat) => {
              const isActive = selectedCategory === cat;
              const count = categoryCounts[cat] || 0;
              return (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
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
            <div className="text-center py-12">
              <p className="text-3xl mb-3">📖</p>
              <p className="text-muted-foreground">
                {selectedCategory === "All"
                  ? "Programs coming soon — check back!"
                  : `No ${selectedCategory} programs listed yet`}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
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
