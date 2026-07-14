import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import { supabase as supabaseTyped } from "@/integrations/supabase/client";

const sb = supabaseTyped as unknown as {
  from: (t: string) => {
    select: (cols: string) => {
      order: (col: string, opts?: { ascending: boolean }) => {
        then: (fn: (r: { data: any; error: any }) => void) => void;
      };
    };
  };
};

/* ── types ─────────────────────────────────────────────────────────── */
interface Representative {
  id: string;
  name: string;
  position: string;
  level: string;
  state: string | null;
  district: string | null;
  party: string | null;
  photo_url: string | null;
  website: string | null;
  wikipedia_url: string | null;
  twitter: string | null;
  bio: string | null;
  status: string;
  first_elected: string | null;
  sort_order: number;
}

/* ── constants ─────────────────────────────────────────────────────── */
const LEVEL_LABELS: Record<string, string> = {
  federal: "Federal",
  state: "State",
  local: "Local",
};

const LEVEL_SUBTITLES: Record<string, string> = {
  federal: "U.S. Congress, Cabinet & National Leaders",
  state: "Governors, Lt. Governors & State Legislators",
  local: "Mayors, City Council, County Officials & Judges",
};

const LEVEL_EMOJIS: Record<string, string> = {
  federal: "🏛️",
  state: "🏗️",
  local: "🏙️",
};

const PARTY_COLORS: Record<string, string> = {
  Democrat: "bg-blue-600/20 text-blue-300 border-blue-500/30",
  Republican: "bg-red-600/20 text-red-300 border-red-500/30",
  DFL: "bg-blue-600/20 text-blue-300 border-blue-500/30",
  Nonpartisan: "bg-slate-600/20 text-slate-300 border-slate-500/30",
};

const STATUS_BADGES: Record<string, { label: string; cls: string }> = {
  elected: { label: "Serving", cls: "bg-emerald-600/20 text-emerald-300" },
  appointed: { label: "Appointed", cls: "bg-amber-600/20 text-amber-300" },
  candidate: { label: "Candidate", cls: "bg-purple-600/20 text-purple-300" },
  former: { label: "Former", cls: "bg-slate-600/20 text-slate-300" },
};

const US_STATES: Record<string, string> = {
  AL:"Alabama",AK:"Alaska",AZ:"Arizona",AR:"Arkansas",CA:"California",
  CO:"Colorado",CT:"Connecticut",DC:"District of Columbia",DE:"Delaware",
  FL:"Florida",GA:"Georgia",HI:"Hawaii",IA:"Iowa",ID:"Idaho",IL:"Illinois",
  IN:"Indiana",KS:"Kansas",KY:"Kentucky",LA:"Louisiana",MA:"Massachusetts",
  MD:"Maryland",ME:"Maine",MI:"Michigan",MN:"Minnesota",MO:"Missouri",
  MS:"Mississippi",MT:"Montana",NC:"North Carolina",ND:"North Dakota",
  NE:"Nebraska",NH:"New Hampshire",NJ:"New Jersey",NM:"New Mexico",
  NV:"Nevada",NY:"New York",OH:"Ohio",OK:"Oklahoma",OR:"Oregon",
  PA:"Pennsylvania",RI:"Rhode Island",SC:"South Carolina",SD:"South Dakota",
  TN:"Tennessee",TX:"Texas",UT:"Utah",VA:"Virginia",VT:"Vermont",
  WA:"Washington",WI:"Wisconsin",WV:"West Virginia",WY:"Wyoming",
};

/* ── components ────────────────────────────────────────────────────── */

function PartyBadge({ party }: { party: string | null }) {
  if (!party) return null;
  const cls = PARTY_COLORS[party] || "bg-slate-600/20 text-slate-300 border-slate-500/30";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-semibold border ${cls}`}>
      {party}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_BADGES[status] || STATUS_BADGES.elected;
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-medium ${cfg.cls}`}>
      {cfg.label}
    </span>
  );
}

function PersonCard({ rep }: { rep: Representative }) {
  const stateName = rep.state ? (US_STATES[rep.state] || rep.state) : "";
  const locationParts = [stateName, rep.district].filter(Boolean);
  const locationStr = locationParts.length > 0
    ? (rep.district && stateName ? `${stateName} · ${rep.district}` : locationParts[0])
    : "";

  return (
    <article className="group flex flex-row bg-card border border-border rounded-xl overflow-hidden hover:border-amber-500/40 transition-all duration-200">
      {/* Photo / Placeholder */}
      <div className="w-24 min-w-[6rem] sm:w-32 sm:min-w-[8rem] flex-shrink-0 bg-gradient-to-br from-[#0B1D3A] to-[#162d50] flex items-center justify-center overflow-hidden">
        {rep.photo_url ? (
          <img
            src={rep.photo_url}
            alt={rep.name}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="flex flex-col items-center justify-center p-2">
            <svg viewBox="0 0 24 24" fill="none" stroke="#D4A843" strokeWidth="1" className="w-10 h-10 sm:w-12 sm:h-12 opacity-60">
              <circle cx="12" cy="8" r="4" />
              <path d="M20 21a8 8 0 10-16 0" />
            </svg>
            <span className="text-[9px] text-amber-400/50 mt-1 text-center leading-tight">Photo<br/>coming soon</span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 p-3 sm:p-4 min-w-0 overflow-hidden flex flex-col">
        {/* Name */}
        <h3 className="font-serif text-base sm:text-lg font-bold text-foreground leading-snug mb-1">
          {rep.name}
        </h3>

        {/* Position */}
        <p className="text-sm text-amber-400/90 font-medium leading-snug mb-1.5 line-clamp-2">
          {rep.position}
        </p>

        {/* Badges row */}
        <div className="flex items-center gap-1.5 flex-wrap mb-2">
          <PartyBadge party={rep.party} />
          <StatusBadge status={rep.status} />
          {rep.first_elected && (
            <span className="text-[11px] text-muted-foreground">
              Since {rep.first_elected}
            </span>
          )}
        </div>

        {/* Bio */}
        {rep.bio && (
          <p className="text-xs text-muted-foreground leading-relaxed line-clamp-3 mb-2">
            {rep.bio}
          </p>
        )}

        {/* Footer: location + links */}
        <div className="flex items-center gap-3 text-xs text-muted-foreground mt-auto pt-1.5 border-t border-border/50">
          {locationStr && (
            <span className="truncate">📍 {locationStr}</span>
          )}
          <div className="ml-auto flex items-center gap-2 flex-shrink-0">
            {rep.website && (
              <a
                href={rep.website}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="text-primary hover:text-primary/80 hover:underline"
                title="Official Website"
              >
                🌐 Website
              </a>
            )}
            {rep.twitter && (
              <a
                href={`https://x.com/${rep.twitter.replace("@", "")}`}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="text-primary hover:text-primary/80 hover:underline"
                title="X / Twitter"
              >
                𝕏
              </a>
            )}
          </div>
        </div>
      </div>
    </article>
  );
}

/* ── level section ─────────────────────────────────────────────────── */
function LevelSection({ level, reps }: { level: string; reps: Representative[] }) {
  if (reps.length === 0) return null;
  const emoji = LEVEL_EMOJIS[level] || "🏛️";
  const subtitle = LEVEL_SUBTITLES[level] || "";

  return (
    <section className="mb-10">
      <div className="mb-4">
        <h2 className="text-xl sm:text-2xl font-serif font-bold text-foreground flex items-center gap-2">
          {emoji} {LEVEL_LABELS[level] || level} Government
          <span className="text-sm font-sans font-normal text-muted-foreground ml-1">
            ({reps.length})
          </span>
        </h2>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>
        )}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {reps.map((rep) => (
          <PersonCard key={rep.id} rep={rep} />
        ))}
      </div>
    </section>
  );
}

/* ── main page ─────────────────────────────────────────────────────── */
export default function RepresentativesPage() {
  const [reps, setReps] = useState<Representative[]>([]);
  const [loading, setLoading] = useState(true);
  const [levelFilter, setLevelFilter] = useState("all");
  const [stateFilter, setStateFilter] = useState("all");

  /* fetch data */
  useEffect(() => {
    sb.from("representatives")
      .select("*")
      .order("sort_order", { ascending: true })
      .then(({ data, error }: { data: any; error: any }) => {
        if (!error && data) setReps(data as Representative[]);
        setLoading(false);
      });
  }, []);

  /* derived */
  const filtered = reps.filter((r) => {
    if (levelFilter !== "all" && r.level !== levelFilter) return false;
    if (stateFilter !== "all" && r.state !== stateFilter) return false;
    return true;
  });

  const statesInData = [...new Set(reps.map((r) => r.state).filter(Boolean))] as string[];
  statesInData.sort((a, b) => (US_STATES[a] || a).localeCompare(US_STATES[b] || b));

  const groupedByLevel = ["federal", "state", "local"].map((level) => ({
    level,
    reps: filtered.filter((r) => r.level === level),
  }));

  const totalCount = reps.length;
  const stateCount = statesInData.length;

  const LEVEL_PILLS = [
    { value: "all", label: "All" },
    { value: "federal", label: "Federal" },
    { value: "state", label: "State" },
    { value: "local", label: "Local" },
  ];

  return (
    <>
      <Helmet>
        <title>Indian-Americans in Public Office | The Videshi</title>
        <meta
          name="description"
          content="A comprehensive directory of Indian-American elected officials, from the U.S. Congress to city councils across America. Celebrating our community's growing presence in American democracy."
        />
      </Helmet>

      <Masthead />

      <main className="min-h-screen pb-16">
        {/* Hero banner */}
        <div className="bg-gradient-to-br from-[#0B1D3A] via-[#122847] to-[#0B1D3A] border-b border-amber-500/20">
          <div className="max-w-5xl mx-auto px-4 py-10 sm:py-14 text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-medium mb-4">
              <span>🇺🇸</span>
              <span>🇮🇳</span>
              <span>{totalCount} Leaders Across {stateCount} States</span>
            </div>

            <h1 className="font-serif text-3xl sm:text-4xl md:text-5xl font-bold text-white leading-tight mb-4">
              Indian-Americans in{" "}
              <span className="text-amber-400">Public Office</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed mb-2">
              From city halls to the halls of Congress — celebrating our community's
              growing presence in American democracy.
            </p>

            <p className="text-sm text-amber-400/70 italic">
              We are proud of each one of them. 🙏
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="sticky top-0 z-30 bg-background/95 backdrop-blur-sm border-b border-border">
          <div className="max-w-5xl mx-auto px-4 py-3 flex flex-col sm:flex-row items-start sm:items-center gap-3">
            {/* Level pills */}
            <div className="flex items-center gap-1.5 overflow-x-auto">
              {LEVEL_PILLS.map((pill) => (
                <button
                  key={pill.value}
                  onClick={() => setLevelFilter(pill.value)}
                  className={`px-3.5 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                    levelFilter === pill.value
                      ? "bg-amber-500 text-white"
                      : "bg-muted/50 text-muted-foreground hover:bg-muted"
                  }`}
                >
                  {pill.label}
                </button>
              ))}
            </div>

            {/* State dropdown */}
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="bg-muted/50 border border-border rounded-lg text-sm text-foreground px-3 py-1.5 min-w-[160px]"
            >
              <option value="all">All States</option>
              {statesInData.map((st) => (
                <option key={st} value={st}>
                  {US_STATES[st] || st}
                </option>
              ))}
            </select>

            {/* Count */}
            <span className="text-xs text-muted-foreground ml-auto">
              Showing {filtered.length} of {totalCount}
            </span>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-5xl mx-auto px-4 pt-8">
          {loading ? (
            <div className="text-center py-16">
              <div className="inline-block w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-muted-foreground mt-3">Loading representatives…</p>
            </div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-16">
              <p className="text-lg text-muted-foreground">No representatives found for this filter.</p>
              <button
                onClick={() => { setLevelFilter("all"); setStateFilter("all"); }}
                className="mt-3 text-sm text-primary hover:underline"
              >
                Clear filters
              </button>
            </div>
          ) : (
            groupedByLevel.map(({ level, reps: levelReps }) => (
              <LevelSection key={level} level={level} reps={levelReps} />
            ))
          )}
        </div>

        {/* Footer note */}
        <div className="max-w-5xl mx-auto px-4 mt-8 mb-8">
          <div className="bg-card border border-border rounded-xl p-5 text-center">
            <p className="text-sm text-muted-foreground leading-relaxed">
              This list celebrates Indian-Americans serving in public office across all levels of government,
              regardless of political party. Know someone we&apos;re missing?{" "}
              <a href="mailto:signals@thevideshi.com" className="text-primary hover:underline">
                Let us know →
              </a>
            </p>
            <p className="text-xs text-muted-foreground/60 mt-2">
              Sources: Official government websites &amp; Wikipedia. Last updated July 2026.
            </p>
          </div>
        </div>
      </main>

      <SiteFooter />
    </>
  );
}
