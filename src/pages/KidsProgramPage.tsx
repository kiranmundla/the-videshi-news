import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  fetchKidsProgramBySlug,
  fetchKidsDeadlines,
  fetchKidsPrograms,
  generateProgramSlug,
  type KidsProgram,
  type KidsDeadline,
} from "@/lib/kidsPrograms";

/* ------------------------------------------------------------------ */
/* Constants                                                          */
/* ------------------------------------------------------------------ */

const CATEGORY_COLORS: Record<string, string> = {
  "Academic Competitions": "bg-blue-100 text-blue-700",
  Math: "bg-indigo-100 text-indigo-700",
  "Science & STEM": "bg-emerald-100 text-emerald-700",
  Robotics: "bg-cyan-100 text-cyan-700",
  "Coding & CS": "bg-violet-100 text-violet-700",
  Chess: "bg-slate-100 text-slate-700",
  "College Prep": "bg-rose-100 text-rose-700",
  "Summer Programs": "bg-orange-100 text-orange-700",
  Sports: "bg-green-100 text-green-700",
  Dance: "bg-pink-100 text-pink-700",
  Music: "bg-purple-100 text-purple-700",
  Language: "bg-amber-100 text-amber-700",
  "Cultural & Religious": "bg-yellow-100 text-yellow-700",
  Volunteering: "bg-teal-100 text-teal-700",
  "Summer Camps": "bg-lime-100 text-lime-700",
};

const CATEGORY_EMOJI: Record<string, string> = {
  "Academic Competitions": "🎓",
  Math: "🔢",
  "Science & STEM": "🔬",
  Robotics: "🤖",
  "Coding & CS": "💻",
  Chess: "♟️",
  "College Prep": "📝",
  "Summer Programs": "☀️",
  Sports: "🏏",
  Dance: "💃",
  Music: "🎵",
  Language: "🗣️",
  "Cultural & Religious": "🛕",
  Volunteering: "🤝",
  "Summer Camps": "🏕️",
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
  if (days <= 7) return "bg-red-50 text-red-700 border-red-200";
  if (days <= 30) return "bg-amber-50 text-amber-700 border-amber-200";
  return "bg-green-50 text-green-700 border-green-200";
}

function formatDeadlineDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

/* ------------------------------------------------------------------ */
/* Info Row component                                                 */
/* ------------------------------------------------------------------ */

function InfoRow({
  icon,
  label,
  value,
}: {
  icon: string;
  label: string;
  value: string | null | undefined;
}) {
  if (!value) return null;
  return (
    <div className="flex items-start gap-3 py-4 border-b border-border/50 last:border-b-0">
      <span className="text-xl flex-shrink-0 mt-0.5">{icon}</span>
      <div>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-0.5">
          {label}
        </p>
        <p className="text-sm text-foreground">{value}</p>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Main component                                                     */
/* ------------------------------------------------------------------ */

export default function KidsProgramPage() {
  const { slug } = useParams<{ slug: string }>();
  const [program, setProgram] = useState<KidsProgram | null>(null);
  const [deadlines, setDeadlines] = useState<KidsDeadline[]>([]);
  const [related, setRelated] = useState<KidsProgram[]>([]);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    async function load() {
      if (!slug) {
        setNotFound(true);
        setLoading(false);
        return;
      }

      try {
        const prog = await fetchKidsProgramBySlug(slug);
        if (!prog) {
          setNotFound(true);
          setLoading(false);
          return;
        }
        setProgram(prog);

        // Fetch deadlines for this program and related programs in parallel
        const [allDeadlines, allPrograms] = await Promise.all([
          fetchKidsDeadlines(100),
          fetchKidsPrograms(),
        ]);

        // Filter deadlines for this program
        const programDeadlines = allDeadlines.filter(
          (d) => d.program_id === prog.id
        );
        setDeadlines(programDeadlines);

        // Get related programs (same category, excluding this one)
        const relatedPrograms = allPrograms
          .filter((p) => p.category === prog.category && p.id !== prog.id)
          .slice(0, 4);
        setRelated(relatedPrograms);
      } catch (err) {
        console.error("Failed to load program:", err);
        setNotFound(true);
      } finally {
        setLoading(false);
      }
    }
    load();
    window.scrollTo(0, 0);
  }, [slug]);

  /* Loading state */
  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <CategoryPills />
        <main
          className="container flex-1 pt-10 pb-16"
          style={{ maxWidth: 900 }}
        >
          <div className="animate-pulse space-y-6">
            <div className="h-4 w-32 bg-muted/30 rounded" />
            <div className="h-10 w-3/4 bg-muted/30 rounded" />
            <div className="h-6 w-1/3 bg-muted/30 rounded" />
            <div className="h-32 bg-muted/20 rounded-xl" />
            <div className="h-48 bg-muted/20 rounded-xl" />
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  /* Not found */
  if (notFound || !program) {
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <CategoryPills />
        <main
          className="container flex-1 pt-16 pb-16 text-center"
          style={{ maxWidth: 900 }}
        >
          <p className="text-6xl mb-6">📚</p>
          <h1 className="font-serif text-2xl text-foreground mb-3">
            Program Not Found
          </h1>
          <p className="text-muted-foreground mb-8">
            We couldn't find the program you're looking for.
          </p>
          <Link
            to="/kids"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition-colors"
            style={{ backgroundColor: "#A32D2F" }}
          >
            ← Back to Learn
          </Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  const catColor =
    CATEGORY_COLORS[program.category || ""] || "bg-gray-100 text-gray-700";
  const catEmoji = CATEGORY_EMOJI[program.category || ""] || "📌";

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Helmet>
        <title>{program.name} — Learn — The Videshi</title>
        <meta
          name="description"
          content={
            program.description ||
            `Learn about ${program.name} — programs and opportunities for Indian-American kids.`
          }
        />
        <link
          rel="canonical"
          href={`https://www.thevideshi.com/kids/programs/${slug}`}
        />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main
        className="container flex-1 pt-8 md:pt-12 pb-20"
        style={{ maxWidth: 900 }}
      >
        {/* Back link */}
        <Link
          to="/kids"
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors mb-8 group"
        >
          <span className="group-hover:-translate-x-0.5 transition-transform">
            ←
          </span>{" "}
          Learn
        </Link>

        {/* ── Header ────────────────────────────────────── */}
        <header className="mb-10">
          <div className="flex flex-wrap items-center gap-2.5 mb-4">
            <span
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${catColor}`}
            >
              {catEmoji} {program.category}
            </span>
            {program.is_indian_org && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-orange-100 text-orange-700">
                🇮🇳 Indian Community
              </span>
            )}
            {program.is_featured && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-700">
                ⭐ Featured
              </span>
            )}
          </div>

          <h1 className="font-serif text-3xl md:text-4xl lg:text-5xl text-foreground leading-tight mb-4">
            {program.name}
          </h1>

          {program.organization && (
            <p className="text-lg text-muted-foreground">
              by {program.organization}
            </p>
          )}
        </header>

        {/* ── Description ───────────────────────────────── */}
        {(program.description || (program as any).long_description) && (
          <section className="mb-12">
            {program.description && (
              <p className="text-lg leading-relaxed text-foreground mb-5">
                {program.description}
              </p>
            )}
            {(program as any).long_description &&
              (program as any).long_description !== program.description && (
                <div className="text-base leading-relaxed text-muted-foreground">
                  {(program as any).long_description}
                </div>
              )}
          </section>
        )}

        {/* ── Key Details Card ──────────────────────────── */}
        <section className="mb-12">
          <div className="rounded-xl border border-border bg-card p-6 md:p-8">
            <h2 className="font-serif text-lg font-semibold text-foreground mb-2">
              Key Details
            </h2>
            <div className="divide-y divide-border/50">
              <InfoRow
                icon="🎒"
                label="Ages / Grades"
                value={
                  program.grade_range ||
                  (program as any).age_range ||
                  null
                }
              />
              <InfoRow
                icon="💰"
                label="Cost"
                value={program.cost}
              />
              <InfoRow
                icon="📍"
                label="Format"
                value={(program as any).format}
              />
              <InfoRow
                icon="🏢"
                label="Organization"
                value={program.organization}
              />
              <InfoRow
                icon="🔄"
                label="Annual Cycle"
                value={(program as any).annual_cycle}
              />
              <InfoRow
                icon="📍"
                label="Locations"
                value={(program as any).locations}
              />
            </div>
          </div>
        </section>

        {/* ── Action Buttons ────────────────────────────── */}
        {(program.website_url || (program as any).registration_url) && (
          <section className="mb-12 flex flex-wrap gap-4">
            {(program as any).registration_url && (
              <a
                href={(program as any).registration_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg text-base font-semibold text-white transition-all hover:opacity-90 shadow-sm"
                style={{ backgroundColor: "#A32D2F" }}
              >
                Register Now →
              </a>
            )}
            {program.website_url && (
              <a
                href={program.website_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg text-base font-semibold border border-border text-foreground hover:bg-muted/50 transition-all"
              >
                Visit Website ↗
              </a>
            )}
          </section>
        )}

        {/* ── Upcoming Deadlines ────────────────────────── */}
        {deadlines.length > 0 && (
          <section className="mb-12">
            <h2 className="font-serif text-xl font-semibold text-foreground mb-5">
              ⏰ Upcoming Deadlines
            </h2>
            <div className="space-y-3">
              {deadlines.map((d) => {
                const days = daysUntil(d.deadline_date);
                const urg = urgencyClass(days);
                return (
                  <div
                    key={d.id}
                    className={`rounded-lg border p-5 ${urg}`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="font-semibold text-base mb-1">
                          {d.title}
                        </h3>
                        <p className="text-sm opacity-80">
                          📅 {formatDeadlineDate(d.deadline_date)}
                        </p>
                        {d.description && (
                          <p className="text-sm opacity-70 mt-2">
                            {d.description}
                          </p>
                        )}
                      </div>
                      <span className="text-xs font-bold whitespace-nowrap px-3 py-1.5 rounded-full bg-white/50">
                        {days === 0
                          ? "Today!"
                          : days === 1
                          ? "Tomorrow!"
                          : `${days} days`}
                      </span>
                    </div>
                    {d.registration_url && (
                      <a
                        href={d.registration_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 mt-3 px-4 py-2 rounded-lg text-sm font-semibold text-white transition-colors"
                        style={{ backgroundColor: "#A32D2F" }}
                      >
                        Register →
                      </a>
                    )}
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* ── Related Programs ──────────────────────────── */}
        {related.length > 0 && (
          <section className="mb-8">
            <h2 className="font-serif text-xl font-semibold text-foreground mb-5">
              More in {program.category}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {related.map((r) => (
                <Link
                  key={r.id}
                  to={`/kids/programs/${
                    (r as any).slug || generateProgramSlug(r.name)
                  }`}
                  className="block no-underline"
                >
                  <div className="group rounded-lg border border-border bg-card p-5 transition-all hover:shadow-md hover:border-[#D4A843]/50 h-full">
                    <h3 className="font-serif text-base font-semibold text-foreground leading-snug group-hover:text-[#A32D2F] transition-colors mb-1.5">
                      {r.name}
                    </h3>
                    {r.organization && (
                      <p className="text-xs text-muted-foreground mb-2">
                        {r.organization}
                      </p>
                    )}
                    {r.description && (
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {r.description}
                      </p>
                    )}
                    <span className="text-sm font-medium text-[#A32D2F] mt-3 inline-block group-hover:underline">
                      Learn More →
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
