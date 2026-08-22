import { useState, useEffect, useMemo, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useSearchParams } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import ZipCodeSearch, { type LocationResult } from "@/components/ZipCodeSearch";
import { useUserLocation } from "@/hooks/useUserLocation";
import { fetchKidsArticles, type Article } from "@/lib/articles";
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
  CATEGORY_GRADIENTS,
  LOCAL_CATEGORY_COLORS,
  type KidsLocalPlace,
} from "@/lib/kidsLocalPlaces";
import { getGuideByTopic } from "@/lib/kidsGuides";

/* ================================================================== */
/* CATEGORY HIERARCHY                                                 */
/* ================================================================== */

type SubSub = { key: string; label: string; icon: string; localCategory: string; programKeyword?: string; programKeywordExclude?: string };
type Subcategory = {
  key: string;
  label: string;
  icon: string;
  localCategories: string[];
  programCategories: string[];
  programKeyword?: string;
  subsubs?: SubSub[];
};
type TopCategory = {
  key: string;
  label: string;
  icon: string;
  subcategories: Subcategory[];
  showForAge?: string[];
};

const CATEGORY_TREE: TopCategory[] = [
  {
    key: "extracurriculars",
    label: "Extracurriculars",
    icon: "🎯",
    subcategories: [
      {
        key: "sports", label: "Sports", icon: "⚽",
        localCategories: ["Cricket", "Swimming", "Martial Arts", "Gymnastics", "Tennis", "Table Tennis", "Badminton", "Basketball", "Soccer"],
        programCategories: ["Sports"],
        subsubs: [
          { key: "cricket", label: "Cricket", icon: "🏏", localCategory: "Cricket", programKeyword: "cricket" },
          { key: "tennis", label: "Tennis", icon: "🎾", localCategory: "Tennis", programKeyword: "tennis", programKeywordExclude: "table tennis|ping pong" },
          { key: "table_tennis", label: "Table Tennis", icon: "🏓", localCategory: "Table Tennis", programKeyword: "table tennis|ping pong" },
          { key: "badminton", label: "Badminton", icon: "🏸", localCategory: "Badminton", programKeyword: "badminton" },
          { key: "swimming", label: "Swimming", icon: "🏊", localCategory: "Swimming", programKeyword: "swimming" },
          { key: "soccer", label: "Soccer", icon: "⚽", localCategory: "Soccer", programKeyword: "soccer" },
          { key: "basketball", label: "Basketball", icon: "🏀", localCategory: "Basketball", programKeyword: "basketball" },
          { key: "martial_arts", label: "Martial Arts", icon: "🥋", localCategory: "Martial Arts", programKeyword: "martial" },
          { key: "gymnastics", label: "Gymnastics", icon: "🤸", localCategory: "Gymnastics", programKeyword: "gymnast" },
        ],
      },
      { key: "dance", label: "Dance", icon: "💃", localCategories: ["Dance"], programCategories: ["Dance"] },
      { key: "music", label: "Music", icon: "🎵", localCategories: ["Music"], programCategories: ["Music"] },
      { key: "art", label: "Art", icon: "🎨", localCategories: ["Art"], programCategories: ["Cultural & Arts"] },
      { key: "coding_robotics", label: "Coding & Robotics", icon: "🤖", localCategories: ["Coding & STEM"], programCategories: ["Robotics", "Coding & CS"] },
      { key: "language_culture", label: "Language & Culture", icon: "🗣️", localCategories: ["Language"], programCategories: ["Language", "Cultural & Religious"] },
      { key: "chess", label: "Chess", icon: "♟️", localCategories: ["Chess"], programCategories: ["Chess"] },
      { key: "volunteering", label: "Volunteering", icon: "🤝", localCategories: [], programCategories: ["Volunteering"] },
    ],
  },
  {
    key: "academics",
    label: "Academics",
    icon: "📚",
    subcategories: [
      { key: "math", label: "Math", icon: "🔢", localCategories: ["Math Enrichment"], programCategories: ["Math"] },
      { key: "science_stem", label: "Science & STEM", icon: "🧪", localCategories: [], programCategories: ["Science & STEM"] },
      { key: "spelling_debate", label: "Spelling & Debate", icon: "🗯️", localCategories: [], programCategories: ["Academic Competitions"], programKeyword: "spell|debate" },
      { key: "robotics_comp", label: "Robotics Competitions", icon: "🤖", localCategories: [], programCategories: ["Robotics"] },
      { key: "business", label: "Business (DECA/FBLA)", icon: "💼", localCategories: [], programCategories: [] },
      { key: "test_prep", label: "Test Prep", icon: "📝", localCategories: [], programCategories: ["College Prep"], programKeyword: "sat|act|kaplan|khan|princeton" },
      { key: "college_counseling", label: "College Counseling", icon: "🎓", localCategories: [], programCategories: ["College Prep"], programKeyword: "essay|counsel|c2" },
      { key: "tutoring", label: "General Tutoring", icon: "📚", localCategories: ["Tutoring"], programCategories: [] },
    ],
  },
  {
    key: "daycare",
    label: "Daycare & Preschool",
    icon: "🏠",
    showForAge: ["preschool"],
    subcategories: [
      { key: "daycare_all", label: "All Daycare", icon: "🏠", localCategories: ["Daycare"], programCategories: [] },
    ],
  },
];

const AGE_GROUPS = [
  { key: "preschool", label: "Preschool", sub: "Ages 3–5", icon: "🧒" },
  { key: "elementary", label: "Elementary", sub: "Grades K–5", icon: "📖" },
  { key: "middle_school", label: "Middle School", sub: "Grades 6–8", icon: "🔬" },
  { key: "high_school", label: "High School", sub: "Grades 9–12", icon: "🎓" },
];

const PROGRAM_CAT_COLORS: Record<string, string> = {
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

const RESULTS_LIMIT = 6;

/* ================================================================== */
/* HELPERS                                                            */
/* ================================================================== */

function daysUntil(d: string): number {
  const t = new Date(d + "T00:00:00");
  const n = new Date(); n.setHours(0, 0, 0, 0);
  return Math.ceil((t.getTime() - n.getTime()) / 86400000);
}

function mapsUrl(p: KidsLocalPlace): string {
  if (p.address)
    return `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(`${p.address}, ${p.city}, ${p.state}`)}`;
  if (p.latitude && p.longitude)
    return `https://www.google.com/maps/dir/?api=1&destination=${p.latitude},${p.longitude}`;
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${p.name} ${p.city} ${p.state}`)}`;
}

/* ================================================================== */
/* SUB-COMPONENTS                                                     */
/* ================================================================== */

/* ---------- Closing-Soon Strip ---------- */

function ClosingSoonStrip({ deadlines }: { deadlines: KidsDeadline[] }) {
  const urgent = deadlines
    .filter((d) => { const dy = daysUntil(d.deadline_date); return dy >= 0 && dy <= 14; })
    .slice(0, 8);
  if (!urgent.length) return null;

  return (
    <section className="mb-10">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-lg">🔔</span>
        <h2 className="font-serif text-lg font-semibold text-foreground">
          Don't Miss — Registration Closing Soon
        </h2>
        <div className="h-px flex-1 bg-border" />
      </div>
      <div className="relative">
        <div className="flex gap-3 overflow-x-auto pb-2 -mx-1 px-1 scrollbar-hide" style={{ scrollSnapType: "x mandatory" }}>
        {urgent.map((d) => {
          const days = daysUntil(d.deadline_date);
          const red = days <= 7;
          return (
            <div key={d.id} className={`flex-shrink-0 w-[260px] sm:w-[280px] rounded-lg border p-4 transition-all hover:shadow-md ${red ? "border-red-200 bg-red-50" : "border-amber-200 bg-amber-50"}`} style={{ scrollSnapAlign: "start" }}>
              <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-bold mb-2 ${red ? "text-red-700" : "text-amber-700"}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${red ? "bg-red-500 animate-pulse" : "bg-amber-500"}`} />
                {days === 0 ? "Today!" : days === 1 ? "Tomorrow!" : `${days} days left`}
              </span>
              <h3 className={`font-semibold text-sm leading-snug line-clamp-2 mb-1 ${red ? "text-red-900" : "text-amber-900"}`}>
                {(d as any).program_name || d.title}
              </h3>
              {d.registration_url && (
                <a href={d.registration_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-xs font-semibold hover:underline" style={{ color: "#A32D2F" }}>
                  Register →
                </a>
              )}
            </div>
          );
        })}
        </div>
        <div className="pointer-events-none absolute right-0 top-0 bottom-2 w-8 bg-gradient-to-l from-background to-transparent" />
      </div>
    </section>
  );
}

/* ---------- Competition Spotlight ---------- */

const SPOTLIGHT_IMG: Record<string, string> = {
  Math: "/images/kids/math.jpg",
  "Science & STEM": "/images/kids/science.jpg",
  "Academic Competitions": "/images/kids/spelling.jpg",
  Chess: "/images/kids/chess.jpg",
  "Coding & CS": "/images/kids/coding.jpg",
  Robotics: "/images/kids/robotics.jpg",
  Sports: "/images/kids/sports.jpg",
  Music: "/images/kids/music.jpg",
  Dance: "/images/kids/dance.jpg",
  "Summer Programs": "/images/kids/academics.jpg",
  "Cultural & Religious": "/images/kids/language.jpg",
  "College Prep": "/images/kids/college.jpg",
  Volunteering: "/images/kids/volunteering.jpg",
  Language: "/images/kids/language.jpg",
};

function CompetitionSpotlight({ programs, deadlines }: { programs: KidsProgram[]; deadlines: KidsDeadline[] }) {
  // Pick featured programs that have an upcoming deadline within 90 days
  const spotlights = useMemo(() => {
    const deadlineByProgram = new Map<string, KidsDeadline>();
    for (const d of deadlines) {
      const days = daysUntil(d.deadline_date);
      if (days < 0 || days > 90) continue;
      const existing = deadlineByProgram.get(d.program_id);
      if (!existing || d.deadline_date < existing.deadline_date) {
        deadlineByProgram.set(d.program_id, d);
      }
    }
    // Featured programs with upcoming deadlines first, then any featured
    const featured = programs.filter((p) => p.is_featured);
    const withDeadline = featured.filter((p) => deadlineByProgram.has(p.id)).map((p) => ({
      program: p, deadline: deadlineByProgram.get(p.id)!,
    }));
    const withoutDeadline = featured.filter((p) => !deadlineByProgram.has(p.id)).map((p) => ({
      program: p, deadline: null as KidsDeadline | null,
    }));
    return [...withDeadline, ...withoutDeadline].slice(0, 6);
  }, [programs, deadlines]);

  if (spotlights.length === 0) return null;

  return (
    <section className="mb-10">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-lg">⭐</span>
        <h2 className="font-serif text-lg font-semibold text-foreground">
          Competition Spotlight
        </h2>
        <div className="h-px flex-1 bg-border" />
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 sm:gap-4">
        {spotlights.map(({ program, deadline }) => {
          const img = program.image_url || SPOTLIGHT_IMG[program.category || ""] || "/images/kids/academics.jpg";
          const days = deadline ? daysUntil(deadline.deadline_date) : null;
          return (
            <Link key={program.id} to={`/kids/programs/${program.slug}`} className="group relative rounded-xl overflow-hidden no-underline">
              <div className="aspect-[4/3] relative overflow-hidden">
                <img src={img} alt={program.name} className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" loading="lazy" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/40 to-black/10" />
                {deadline && days !== null && (
                  <span className={`absolute top-2 right-2 px-2 py-0.5 rounded-full text-[10px] font-bold ${days <= 14 ? "bg-red-500 text-white" : "bg-amber-400 text-amber-900"}`}>
                    {days <= 14 ? `${days}d left` : new Date(deadline.deadline_date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                  </span>
                )}
                {program.is_indian_org && (
                  <span className="absolute top-2 left-2 px-1.5 py-0.5 rounded-full bg-orange-500/90 text-white text-[10px] font-bold">🇮🇳</span>
                )}
                <div className="absolute inset-0 p-3 flex flex-col justify-end">
                  <span className="text-white/70 text-[10px] font-semibold uppercase tracking-wider mb-0.5">{program.category}</span>
                  <h3 className="text-white text-sm sm:text-[15px] font-bold font-serif leading-tight line-clamp-2 drop-shadow-lg">{program.name}</h3>
                  {program.age_range && <span className="text-white/70 text-[10px] mt-1">🎒 {program.age_range}</span>}
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}

/* ---------- Local Place Card ---------- */

function PlaceCard({ place, userLat, userLng }: { place: KidsLocalPlace; userLat?: number; userLng?: number }) {
  const gradient = CATEGORY_GRADIENTS[place.category] || "from-gray-400 to-gray-300";
  const catColor = LOCAL_CATEGORY_COLORS[place.category] || "bg-gray-100 text-gray-700";
  const dist = userLat && userLng && place.latitude && place.longitude
    ? distanceMiles(userLat, userLng, place.latitude, place.longitude) : null;
  const addr = place.address
    ? `${place.address}, ${place.city}, ${place.state}${place.zip_code ? ` ${place.zip_code}` : ""}`
    : `${place.city}, ${place.state}`;

  return (
    <div className="group rounded-xl border border-border bg-card overflow-hidden transition-all hover:shadow-lg hover:border-[#D4A843]/50 flex flex-col h-full">
      {place.image_url ? (
        <div className="h-36 sm:h-40 overflow-hidden">
          <img src={place.image_url} alt={place.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" loading="lazy" />
        </div>
      ) : (
        <div className={`h-28 sm:h-32 bg-gradient-to-br ${gradient} flex items-center justify-center`}>
          <span className="text-4xl opacity-80">
            {(CATEGORY_TREE.flatMap(t => t.subcategories).flatMap(s => s.subsubs || []).find(ss => ss.localCategory === place.category)?.icon) ||
             CATEGORY_TREE.flatMap(t => t.subcategories).find(s => s.localCategories.includes(place.category))?.icon || "📍"}
          </span>
        </div>
      )}
      <div className="p-4 sm:p-5 flex flex-col flex-1">
        <div className="flex flex-wrap gap-1.5 mb-2">
          <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold ${catColor}`}>{place.category}</span>
          {place.is_indian_focused && (
            <span className="inline-block px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 text-[10px] font-semibold">🇮🇳 Indian Community</span>
          )}
        </div>
        <h3 className="font-serif text-[15px] sm:text-base font-semibold text-foreground leading-snug line-clamp-2 mb-1.5">{place.name}</h3>
        {place.rating && (
          <div className="flex items-center gap-1.5 mb-2">
            <span className="text-amber-500 text-sm">⭐</span>
            <span className="text-sm font-medium text-foreground">{place.rating}</span>
            {place.review_count ? <span className="text-xs text-muted-foreground">({place.review_count})</span> : null}
            {dist !== null && <span className="text-xs text-muted-foreground ml-auto">{dist < 1 ? "< 1 mi" : `${dist.toFixed(1)} mi`}</span>}
          </div>
        )}
        {!place.rating && dist !== null && (
          <div className="text-xs text-muted-foreground mb-2">📍 {dist < 1 ? "< 1 mi" : `${dist.toFixed(1)} mi`}</div>
        )}
        {place.description && <p className="text-xs text-muted-foreground line-clamp-2 mb-2">{place.description}</p>}
        <div className="text-xs text-muted-foreground mb-1">📍 {addr}</div>
        {place.age_range && <div className="text-xs text-muted-foreground mb-2">🎒 Ages {place.age_range}</div>}
        <div className="flex-1" />
        <div className="grid grid-cols-2 gap-2 pt-3 border-t border-border/50">
          <Link to={`/kids/places/${place.slug}`} className="text-center px-2 py-1.5 rounded-lg text-xs font-semibold text-[#A32D2F] bg-red-50 hover:bg-red-100 transition-colors no-underline">View Details →</Link>
          <a href={mapsUrl(place)} target="_blank" rel="noopener noreferrer" className="text-center px-2 py-1.5 rounded-lg text-xs font-medium bg-muted/30 hover:bg-muted/50 text-foreground transition-colors">🗺️ Directions</a>
          {place.website && <a href={place.website} target="_blank" rel="noopener noreferrer" className="text-center px-2 py-1.5 rounded-lg text-xs font-medium bg-muted/30 hover:bg-muted/50 text-foreground transition-colors">🌐 Website</a>}
          {place.phone && <a href={`tel:${place.phone.replace(/[^\d+]/g, "")}`} className="text-center px-2 py-1.5 rounded-lg text-xs font-medium bg-muted/30 hover:bg-muted/50 text-foreground transition-colors">📞 Call</a>}
        </div>
      </div>
    </div>
  );
}

/* ---------- Program Card ---------- */

function ProgramCard({ program }: { program: KidsProgram }) {
  const catColor = PROGRAM_CAT_COLORS[program.category || ""] || "bg-gray-100 text-gray-700";
  return (
    <Link to={`/kids/programs/${program.slug}`} className="block no-underline h-full">
      <div className={`group rounded-xl border bg-card p-5 sm:p-6 transition-all hover:shadow-lg hover:border-[#D4A843]/50 flex flex-col h-full ${program.is_featured ? "ring-1 ring-[#D4A843]/40" : "border-border"}`}>
        <div className="flex flex-wrap gap-1.5 mb-3">
          {program.is_featured && <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-600 text-[10px] font-semibold">⭐ Featured</span>}
          {program.is_indian_org && <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 text-[10px] font-semibold">🇮🇳 Indian Community</span>}
        </div>
        <h3 className="font-serif text-base sm:text-[17px] font-semibold text-foreground leading-snug line-clamp-2 group-hover:text-[#A32D2F] transition-colors mb-1.5">{program.name}</h3>
        {program.organization && <p className="text-xs text-muted-foreground mb-3 truncate">{program.organization}</p>}
        {program.category && <div className="mb-3"><span className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-medium ${catColor}`}>{program.category}</span></div>}
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground mb-3">
          {program.age_range && <span>🎒 {program.age_range}</span>}
          {program.format && <span>📍 {program.format}</span>}
          {program.cost && <span>💰 {program.cost}</span>}
        </div>
        {program.description && <p className="text-sm text-muted-foreground line-clamp-3 mb-4 flex-1">{program.description}</p>}
        <div className="mt-auto pt-2"><span className="text-sm font-medium text-[#A32D2F] group-hover:underline">Learn More →</span></div>
      </div>
    </Link>
  );
}

/* ---------- Gradient maps for rich cards ---------- */

const AGE_GRADIENTS: Record<string, string> = {
  preschool: "linear-gradient(135deg, #D4A843 0%, #A32D2F 100%)",
  elementary: "linear-gradient(135deg, #0B1D3A 0%, #1e3a5f 100%)",
  middle_school: "linear-gradient(135deg, #1e3a5f 0%, #2d5a3f 100%)",
  high_school: "linear-gradient(135deg, #374151 0%, #1f2937 100%)",
};

const TAB_GRADIENTS: Record<string, string> = {
  extracurriculars: "linear-gradient(135deg, #A32D2F 0%, #D4A843 100%)",
  academics: "linear-gradient(135deg, #0B1D3A 0%, #A32D2F 100%)",
  daycare: "linear-gradient(135deg, #D4A843 0%, #0B1D3A 100%)",
};

const SUB_GRADIENTS: Record<string, string> = {
  sports: "linear-gradient(135deg, #15803d 0%, #166534 100%)",
  dance: "linear-gradient(135deg, #be185d 0%, #9d174d 100%)",
  music: "linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)",
  art: "linear-gradient(135deg, #c2410c 0%, #9a3412 100%)",
  coding_robotics: "linear-gradient(135deg, #0891b2 0%, #0e7490 100%)",
  language_culture: "linear-gradient(135deg, #0d9488 0%, #0f766e 100%)",
  chess: "linear-gradient(135deg, #374151 0%, #1f2937 100%)",
  volunteering: "linear-gradient(135deg, #0369a1 0%, #075985 100%)",
  math: "linear-gradient(135deg, #4338ca 0%, #3730a3 100%)",
  science_stem: "linear-gradient(135deg, #047857 0%, #065f46 100%)",
  spelling_debate: "linear-gradient(135deg, #9333ea 0%, #7e22ce 100%)",
  robotics_comp: "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
  business: "linear-gradient(135deg, #1e3a5f 0%, #0B1D3A 100%)",
  test_prep: "linear-gradient(135deg, #b91c1c 0%, #991b1b 100%)",
  college_counseling: "linear-gradient(135deg, #4a1942 0%, #2d1b69 100%)",
  tutoring: "linear-gradient(135deg, #92400e 0%, #78350f 100%)",
  daycare_all: "linear-gradient(135deg, #D4A843 0%, #92400e 100%)",
};

const SUBSUB_GRADIENTS: Record<string, string> = {
  cricket: "linear-gradient(135deg, #15803d 0%, #14532d 100%)",
  tennis: "linear-gradient(135deg, #ca8a04 0%, #a16207 100%)",
  table_tennis: "linear-gradient(135deg, #059669 0%, #047857 100%)",
  badminton: "linear-gradient(135deg, #0891b2 0%, #155e75 100%)",
  swimming: "linear-gradient(135deg, #0284c7 0%, #0c4a6e 100%)",
  soccer: "linear-gradient(135deg, #16a34a 0%, #15803d 100%)",
  basketball: "linear-gradient(135deg, #ea580c 0%, #c2410c 100%)",
  martial_arts: "linear-gradient(135deg, #dc2626 0%, #991b1b 100%)",
  gymnastics: "linear-gradient(135deg, #d946ef 0%, #a21caf 100%)",
};

const DEFAULT_GRADIENT = "linear-gradient(135deg, #374151 0%, #1f2937 100%)";

/* ---------- Unified FilterCard ---------- */

/* --- Image map for filter card backgrounds --- */
const KIDS_CAT_IMG: Record<string, string> = {
  preschool: "/images/kids/preschool.jpg",
  elementary: "/images/kids/elementary.jpg",
  middle_school: "/images/kids/middle_school.jpg",
  high_school: "/images/kids/high_school.jpg",
  extracurriculars: "/images/kids/extracurriculars.jpg",
  academics: "/images/kids/academics.jpg",
  daycare: "/images/kids/daycare.jpg",
  sports: "/images/kids/sports.jpg",
  dance: "/images/kids/dance.jpg",
  music: "/images/kids/music.jpg",
  art: "/images/kids/art.jpg",
  coding_robotics: "/images/kids/coding.jpg",
  language_culture: "/images/kids/language.jpg",
  chess: "/images/kids/chess.jpg",
  volunteering: "/images/kids/volunteering.jpg",
  math: "/images/kids/math.jpg",
  science_stem: "/images/kids/science.jpg",
  spelling_debate: "/images/kids/spelling.jpg",
  robotics_comp: "/images/kids/robotics.jpg",
  business: "/images/kids/academics.jpg",
  test_prep: "/images/kids/test_prep.jpg",
  college_counseling: "/images/kids/college.jpg",
  tutoring: "/images/kids/tutoring.jpg",
  daycare_all: "/images/kids/daycare.jpg",
  near_you: "/images/kids/near_you.jpg",
  programs: "/images/kids/programs.jpg",
  cricket: "/images/kids/cricket.jpg",
  tennis: "/images/kids/tennis.jpg",
  table_tennis: "/images/kids/tennis.jpg",
  badminton: "/images/kids/badminton.jpg",
  swimming: "/images/kids/swimming.jpg",
  soccer: "/images/kids/soccer.jpg",
  basketball: "/images/kids/basketball.jpg",
  martial_arts: "/images/kids/martial_arts.jpg",
  gymnastics: "/images/kids/gymnastics.jpg",
};

function FilterCard({ label, icon, subtitle, active, count, onClick, size = "md", gradient, imgKey }: {
  label: string; icon: string; subtitle?: string; active: boolean; count?: number; onClick: () => void;
  size?: "lg" | "md" | "sm" | "xs"; gradient?: string; imgKey?: string;
}) {
  const bg = gradient || DEFAULT_GRADIENT;
  const ring = active ? "ring-2 ring-[#D4A843] ring-offset-2 ring-offset-background shadow-lg" : "";
  const imgSrc = imgKey ? KIDS_CAT_IMG[imgKey] : undefined;

  const aspectClass = size === "xs" ? "aspect-[3/2]" : "aspect-[4/3]";
  const textClass = size === "lg" || size === "md" ? "text-[13px] sm:text-sm" : "text-[11px]";
  const iconClass = size === "lg" || size === "md" ? "text-base" : "text-sm";

  return (
    <button onClick={onClick}
      className={`group relative rounded-xl overflow-hidden text-left transition-all hover:scale-[1.03] active:scale-[0.98] focus:outline-none ${ring}`}>
      <div className={`${aspectClass} relative overflow-hidden`}
        style={imgSrc ? undefined : { background: bg }}>
        {imgSrc && (
          <>
            <img src={imgSrc} alt={label} className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" loading="lazy" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-black/20" />
          </>
        )}
        <div className="absolute inset-0 p-2 flex flex-col justify-end">
          <span className={`drop-shadow-lg block ${iconClass} mb-0.5`}>{icon}</span>
          <span className={`text-white ${textClass} font-bold font-serif leading-tight drop-shadow-lg line-clamp-2`}>{label}</span>
          {subtitle && <span className="text-white/80 text-[10px] font-medium mt-0.5 drop-shadow">{subtitle}</span>}
          {count !== undefined && count > 0 && <span className="text-white/80 text-[10px] font-medium mt-0.5 drop-shadow">{count}</span>}
        </div>
      </div>
    </button>
  );
}

/* ---------- Skeleton ---------- */

function Skeleton({ n = 6 }: { n?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
      {[...Array(n)].map((_, i) => <div key={i} className="h-56 rounded-xl bg-muted/20 animate-pulse" />)}
    </div>
  );
}

/* ---------- Back to Top FAB ---------- */

function BackToTop() {
  const [show, setShow] = useState(false);
  useEffect(() => {
    const onScroll = () => setShow(window.scrollY > 800);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  if (!show) return null;
  return (
    <button
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      className="fixed bottom-6 right-6 z-50 w-10 h-10 rounded-full bg-[#0B1D3A] text-white shadow-lg flex items-center justify-center hover:bg-[#A32D2F] transition-colors"
      aria-label="Back to top"
    >
      ↑
    </button>
  );
}

/* ================================================================== */
/* MAIN PAGE                                                          */
/* ================================================================== */

export default function KidsPage() {
  /* ---- raw data ---- */
  const [programs, setPrograms] = useState<KidsProgram[]>([]);
  const [deadlines, setDeadlines] = useState<KidsDeadline[]>([]);
  const [localPlaces, setLocalPlaces] = useState<KidsLocalPlace[]>([]);
  const [loading, setLoading] = useState(true);

  /* ---- URL-persisted filters ---- */
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedAge = searchParams.get("age") || null;
  const selectedTab = searchParams.get("tab") || "extracurriculars";
  const selectedSub = searchParams.get("sub") || null;
  const selectedSubSub = searchParams.get("ssub") || null;

  const setParam = useCallback(
    (key: string, val: string | null, alsoReset?: string[]) => {
      const y = window.scrollY;
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        if (!val) next.delete(key); else next.set(key, val);
        (alsoReset || []).forEach((k) => next.delete(k));
        return next;
      }, { replace: true });
      requestAnimationFrame(() => window.scrollTo(0, y));
    },
    [setSearchParams],
  );

  /* ---- location state (like Events page) ---- */
  const [nearMeActive, setNearMeActive] = useState(false);
  const [userCoords, setUserCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [locationLabel, setLocationLabel] = useState("");
  const { location: ipLocation } = useUserLocation();

  const handleLocation = useCallback((result: LocationResult | null) => {
    if (!result) {
      setNearMeActive(false);
      setUserCoords(null);
      setLocationLabel("");
      return;
    }
    setUserCoords({ lat: result.lat, lng: result.lng });
    setNearMeActive(true);
    setLocationLabel(result.label);
  }, []);

  /* Auto-detect location on mount */
  useEffect(() => {
    if (nearMeActive || userCoords) return;
    if (ipLocation) {
      setUserCoords({ lat: ipLocation.latitude, lng: ipLocation.longitude });
      setNearMeActive(true);
      setLocationLabel(ipLocation.city ? `📍 Near ${ipLocation.city}` : "📍 Near You");
    }
  }, [ipLocation]); // eslint-disable-line react-hooks/exhaustive-deps

  /* ---- local UI state ---- */
  const [showAllPlaces, setShowAllPlaces] = useState(false);
  const [showAllPrograms, setShowAllPrograms] = useState(false);
  const [showAllGuides, setShowAllGuides] = useState(false);
  const [searchText, setSearchText] = useState("");
  const [kidsArticles, setKidsArticles] = useState<Article[]>([]);


  /* ---- data load ---- */
  useEffect(() => {
    (async () => {
      try {
        const [p, d, lp, ka] = await Promise.all([fetchKidsPrograms(), fetchKidsDeadlines(50), fetchLocalPlaces(), fetchKidsArticles()]);
        setPrograms(p); setDeadlines(d); setLocalPlaces(lp); setKidsArticles(ka);
      } catch (err) { console.error("Kids data load failed:", err); }
      finally { setLoading(false); }
    })();
  }, []);

  /* ---- resolve active category tree nodes ---- */
  const visibleTabs = useMemo(() =>
    CATEGORY_TREE.filter((t) => !t.showForAge || !selectedAge || t.showForAge.includes(selectedAge)),
    [selectedAge],
  );

  const activeTab = visibleTabs.find((t) => t.key === selectedTab) || visibleTabs[0];
  const activeSub = activeTab?.subcategories.find((s) => s.key === selectedSub) || null;
  const activeSubSub = activeSub?.subsubs?.find((ss) => ss.key === selectedSubSub) || null;

  /* ---- which DB categories to filter by ---- */
  const { targetLocalCats, targetProgCats } = useMemo(() => {
    if (activeSubSub) {
      return { targetLocalCats: [activeSubSub.localCategory], targetProgCats: activeSub?.programCategories || [] };
    }
    if (activeSub) {
      return { targetLocalCats: activeSub.localCategories, targetProgCats: activeSub.programCategories };
    }
    // No sub selected — show all in this tab
    const allLocal = activeTab.subcategories.flatMap((s) => s.localCategories);
    const allProg = activeTab.subcategories.flatMap((s) => s.programCategories);
    return { targetLocalCats: allLocal, targetProgCats: allProg };
  }, [activeTab, activeSub, activeSubSub]);

  /* ---- search filter ---- */
  const searchLower = searchText.toLowerCase().trim();

  /* ---- filtered places ---- */
  const filteredPlaces = useMemo(() => {
    let list = localPlaces;

    // Category filter
    if (targetLocalCats.length > 0) {
      list = list.filter((p) => targetLocalCats.includes(p.category));
    } else {
      list = []; // no matching local categories for this selection
    }

    // Age filter
    if (selectedAge) {
      list = list.filter((p) => placeMatchesAge(p.age_range, selectedAge));
    }

    // Search
    if (searchLower) {
      list = list.filter((p) =>
        p.name.toLowerCase().includes(searchLower) ||
        p.city.toLowerCase().includes(searchLower) ||
        (p.description || "").toLowerCase().includes(searchLower) ||
        p.category.toLowerCase().includes(searchLower),
      );
    }

    // Add distance + sort
    if (userCoords) {
      list = list.map((p) => ({
        ...p,
        distance_miles: p.latitude && p.longitude
          ? distanceMiles(userCoords.lat, userCoords.lng, p.latitude, p.longitude)
          : undefined,
      }));
      list.sort((a, b) => {
        if (a.distance_miles != null && b.distance_miles != null) return a.distance_miles - b.distance_miles;
        if (a.distance_miles != null) return -1;
        if (b.distance_miles != null) return 1;
        return (b.rating || 0) - (a.rating || 0);
      });
    }

    return list;
  }, [localPlaces, targetLocalCats, selectedAge, searchLower, userCoords]);

  /* ---- filtered programs ---- */
  const filteredPrograms = useMemo(() => {
    let list = programs;

    if (targetProgCats.length > 0) {
      list = list.filter((p) => targetProgCats.includes(p.category || ""));
    } else {
      list = [];
    }

    // Sub-subcategory or subcategory keyword filter (e.g. Tennis under Sports, Spelling under Academic Competitions)
    const kwSource = activeSubSub?.programKeyword || activeSub?.programKeyword;
    const kwExclude = activeSubSub?.programKeywordExclude;
    if (kwSource) {
      const keywords = kwSource.toLowerCase().split("|");
      const excludeKeywords = kwExclude ? kwExclude.toLowerCase().split("|") : [];
      list = list.filter((p) => {
        const haystack = `${p.name} ${p.description || ""} ${p.subcategory || ""}`.toLowerCase();
        const matches = keywords.some((kw) => haystack.includes(kw));
        if (!matches) return false;
        if (excludeKeywords.length > 0 && excludeKeywords.some((ekw) => haystack.includes(ekw))) return false;
        return true;
      });
    }

    if (selectedAge) {
      list = list.filter((p) => Array.isArray(p.age_groups) && p.age_groups.includes(selectedAge));
    }

    if (searchLower) {
      list = list.filter((p) =>
        p.name.toLowerCase().includes(searchLower) ||
        (p.description || "").toLowerCase().includes(searchLower) ||
        (p.organization || "").toLowerCase().includes(searchLower),
      );
    }

    return list;
  }, [programs, targetProgCats, activeSub, activeSubSub, selectedAge, searchLower]);

  /* ---- subcategory counts ---- */
  const subCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const sub of activeTab.subcategories) {
      let c = 0;
      c += localPlaces.filter((p) => sub.localCategories.includes(p.category) && (!selectedAge || placeMatchesAge(p.age_range, selectedAge))).length;
      c += programs.filter((p) => sub.programCategories.includes(p.category || "") && (!selectedAge || (Array.isArray(p.age_groups) && p.age_groups.includes(selectedAge)))).length;
      counts[sub.key] = c;
    }
    return counts;
  }, [activeTab, localPlaces, programs, selectedAge]);

  /* ---- display slices ---- */
  const placesToShow = showAllPlaces ? filteredPlaces : filteredPlaces.slice(0, RESULTS_LIMIT);
  const programsToShow = showAllPrograms ? filteredPrograms : filteredPrograms.slice(0, RESULTS_LIMIT);

  /* ---- reset show-all on filter changes ---- */
  useEffect(() => { setShowAllPlaces(false); setShowAllPrograms(false); }, [selectedAge, selectedTab, selectedSub, selectedSubSub, searchText]); // eslint-disable-line react-hooks/exhaustive-deps

  /* ================================================================ */
  /* RENDER                                                           */
  /* ================================================================ */

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>Learn — The Videshi</title>
        <meta name="description" content="Activities, classes, programs & competitions for K-12 students. Find what's right for your child." />
        <link rel="canonical" href="https://www.thevideshi.com/kids" />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container flex-1 pt-8 md:pt-10 pb-16" style={{ maxWidth: 1200 }}>

        {/* ═══════ HEADER ═══════ */}
        <div className="mb-8">
          <h1 className="font-serif text-3xl md:text-5xl text-foreground mb-2">🎓 Learn</h1>
          <p className="text-muted-foreground text-base sm:text-lg max-w-2xl">
            Find the right activities, classes &amp; programs for your child
          </p>
        </div>

        {/* ═══════ LOCATION BAR ═══════ */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 mb-6 p-4 rounded-xl bg-muted/10 border border-border">
          <ZipCodeSearch onLocation={handleLocation} active={nearMeActive} />
          {nearMeActive && locationLabel && (
            <span className="text-xs text-muted-foreground">{locationLabel}</span>
          )}
          {/* Search input */}
          <div className="flex-1 min-w-0 w-full sm:w-auto">
            <input
              type="text"
              placeholder="Search activities, programs, places..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg border border-border bg-card text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
          </div>
        </div>

        {/* ═══════ CLOSING SOON ═══════ */}
        {!loading && <ClosingSoonStrip deadlines={deadlines} />}

        {/* ═══════ COMPETITION SPOTLIGHT ═══════ */}
        {!loading && <CompetitionSpotlight programs={programs} deadlines={deadlines} />}

        {/* ═══════ AGE SELECTOR ═══════ */}
        <div className="mb-8">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Age Group</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {AGE_GROUPS.map((ag) => (
              <FilterCard key={ag.key} label={ag.label} icon={ag.icon} subtitle={ag.sub} size="lg"
                active={selectedAge === ag.key} gradient={AGE_GRADIENTS[ag.key]} imgKey={ag.key}
                onClick={() => setParam("age", selectedAge === ag.key ? null : ag.key, ["sub", "ssub"])} />
            ))}
          </div>
          {selectedAge && (
            <button onClick={() => setParam("age", null, ["sub", "ssub"])} className="mt-3 text-xs text-muted-foreground hover:text-foreground transition-colors">
              ✕ Show all ages
            </button>
          )}
        </div>

        {/* ═══════ MAIN CATEGORY ═══════ */}
        <div className="mb-6">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Category</p>
          <div className="grid grid-cols-3 gap-2 sm:gap-3">
            {visibleTabs.map((tab) => (
              <FilterCard key={tab.key} label={tab.label} icon={tab.icon} size="md"
                active={activeTab.key === tab.key} gradient={TAB_GRADIENTS[tab.key]} imgKey={tab.key}
                onClick={() => setParam("tab", tab.key, ["sub", "ssub"])} />
            ))}
          </div>
        </div>

        {/* ═══════ SUBCATEGORY CARDS ═══════ */}
        {activeTab.subcategories.filter((sub) => !selectedAge || (subCounts[sub.key] ?? 0) > 0).length > 0 && (
          <div className="mb-4">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{activeTab.label}</p>
            <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
              <FilterCard label="All" icon="✨" size="sm" active={!activeSub}
                gradient={DEFAULT_GRADIENT}
                onClick={() => setParam("sub", null, ["ssub"])} />
              {activeTab.subcategories
                .filter((sub) => !selectedAge || (subCounts[sub.key] ?? 0) > 0)
                .map((sub) => (
                  <FilterCard key={sub.key} label={sub.label} icon={sub.icon} size="sm"
                    active={activeSub?.key === sub.key} count={subCounts[sub.key]}
                    gradient={SUB_GRADIENTS[sub.key]} imgKey={sub.key}
                    onClick={() => setParam("sub", sub.key, ["ssub"])} />
                ))}
            </div>
          </div>
        )}

        {/* ═══════ SUB-SUBCATEGORY CARDS (e.g. Sports → Cricket/Tennis) ═══════ */}
        {activeSub?.subsubs && activeSub.subsubs.length > 0 && (
          <div className="mb-6">
            <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-5 gap-2">
              <FilterCard label="All" icon="🏅" size="xs" active={!activeSubSub}
                gradient={DEFAULT_GRADIENT}
                onClick={() => setParam("ssub", null)} />
              {activeSub.subsubs.map((ss) => (
                <FilterCard key={ss.key} label={ss.label} icon={ss.icon} size="xs"
                  active={activeSubSub?.key === ss.key}
                  gradient={SUBSUB_GRADIENTS[ss.key]} imgKey={ss.key}
                  onClick={() => setParam("ssub", ss.key)} />
              ))}
            </div>
          </div>
        )}

        {/* ═══════ RESULTS ═══════ */}
        {loading ? (
          <Skeleton n={6} />
        ) : (
          <>
            {/* --- 1. Getting Started Guides (contextual) --- */}
            {(() => {
              const ALL_GUIDES = [
                { keys: ["sports", "cricket"], guideTopic: "cricket", icon: "🏏", title: "Cricket in the US — A Parent's Guide", summary: "Finding cricket leagues, USA Cricket youth programs, equipment, and how the competitive pathway works for young cricketers in America." },
                { keys: ["sports", "tennis"], guideTopic: "tennis", icon: "🎾", title: "Tennis for Kids — Getting on the Court", summary: "USTA junior pathway, local academies, tournament structure, costs, and what it takes to play competitively from elementary through high school." },
                { keys: ["sports"], guideTopic: "sports", icon: "🏅", title: "Youth Sports in the US", summary: "Club vs. rec leagues, travel teams, tryout seasons, and how to balance competitive sports with academics — a practical overview for parents." },
                { keys: ["dance"], guideTopic: "dance", icon: "💃", title: "Indian Classical & Contemporary Dance", summary: "Bharatanatyam, Kathak, Bollywood, and more — finding the right dance school, exam pathways, and performance opportunities." },
                { keys: ["music"], guideTopic: "music", icon: "🎵", title: "Music Education for Kids", summary: "Instruments, vocal training, Indian classical vs. Western — how to choose, what to expect, and the path from lessons to performances and competitions." },
                { keys: ["coding_robotics", "robotics_comp"], guideTopic: "robotics", icon: "🤖", title: "Getting Into Robotics", summary: "FIRST LEGO League, VEX, and beyond — the robotics competition landscape, costs, team structure, and how to get started from elementary through high school." },
                { keys: ["coding_robotics"], guideTopic: "coding", icon: "💻", title: "Coding & CS for Kids", summary: "From Scratch to Python to USACO — the coding path for kids, free resources, structured programs, and how coding competitions work." },
                { keys: ["chess"], guideTopic: "chess", icon: "♟️", title: "Chess for Kids — Why It Matters", summary: "How chess builds critical thinking, the tournament path from local to nationals, and finding the right chess program for your child." },
                { keys: ["math"], guideTopic: "math", icon: "🔢", title: "Math Competitions — The Complete Path", summary: "From Math Kangaroo to AMC/AIME, here's how to get your child started on the competitive math track and what to expect at each level." },
                { keys: ["science_stem"], guideTopic: "science_stem", icon: "🧪", title: "Science Olympiad & STEM Competitions", summary: "A guide to Science Olympiad, science fairs, and STEM programs — how to find the right fit and prepare your child for success." },
                { keys: ["spelling_debate"], guideTopic: "spelling", icon: "🐝", title: "Spelling Bee — From School to Nationals", summary: "Everything parents need to know about spelling bees: South Asian Spelling Bee, Scripps, NSF — the preparation path, costs, and what makes it rewarding." },
                { keys: ["spelling_debate"], guideTopic: "debate", icon: "🗯️", title: "Debate & Public Speaking", summary: "National History Bee, Model UN, speech & debate leagues — how to develop communication skills and the competitive landscape." },
                { keys: ["test_prep"], guideTopic: "test_prep", icon: "📝", title: "SAT/ACT Prep — What Actually Works", summary: "An honest look at prep options — free vs. paid, self-study vs. courses, timeline, and how to maximize your child's score without burnout." },
                { keys: ["college_counseling"], guideTopic: "college_counseling", icon: "🎓", title: "College Counseling — When & How to Start", summary: "Navigating the college admissions process — when to start, what counselors do, essay prep, and how to choose between independent and school counselors." },
                { keys: ["volunteering"], guideTopic: "volunteering", icon: "🤝", title: "Volunteering & Community Service", summary: "Finding meaningful volunteer opportunities, tracking hours, and how community service strengthens college applications and builds character." },
                { keys: ["language_culture"], guideTopic: "language_culture", icon: "🌍", title: "Heritage Language & Cultural Programs", summary: "Why heritage languages matter, finding the right program (Hindi, Tamil, Telugu, etc.), and cultural immersion opportunities for diaspora kids." },
              ];
              const matchKey = activeSubSub?.key || activeSub?.key;
              const visibleGuides = matchKey
                ? ALL_GUIDES.filter((g) => g.keys.includes(matchKey))
                : ALL_GUIDES;
              if (visibleGuides.length === 0) return null;
              const GUIDES_LIMIT = 4;
              const guidesToShow = matchKey || showAllGuides ? visibleGuides : visibleGuides.slice(0, GUIDES_LIMIT);
              return (
                <section className="mb-10">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-lg">📖</span>
                    <h2 className="font-serif text-lg sm:text-xl font-semibold text-foreground">Getting Started{matchKey ? "" : " — Guides for Parents"}</h2>
                    <div className="h-px flex-1 bg-border" />
                  </div>
                  {!matchKey && (
                    <p className="text-sm text-muted-foreground mb-5 max-w-2xl">
                      Not sure where to begin? These guides cover the competitive landscape, preparation path, costs, and how each activity helps your child.
                    </p>
                  )}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {guidesToShow.map((guide, i) => {
                      const fullGuide = getGuideByTopic(guide.guideTopic);
                      const guideSlug = fullGuide?.slug;
                      const Wrapper = guideSlug ? Link : 'div' as any;
                      const wrapperProps = guideSlug ? { to: `/kids/guides/${guideSlug}` } : {};
                      return (
                        <Wrapper key={i} {...wrapperProps} className={`rounded-xl border border-border bg-card p-5 sm:p-6 hover:shadow-md hover:border-[#D4A843]/50 transition-all ${guideSlug ? 'cursor-pointer' : ''}`}>
                          <div className="flex items-start gap-3 mb-3">
                            <span className="text-2xl flex-shrink-0">{guide.icon}</span>
                            <h3 className="font-serif text-[15px] sm:text-base font-semibold text-foreground leading-snug">{guide.title}</h3>
                          </div>
                          <p className="text-sm text-muted-foreground leading-relaxed">{guide.summary}</p>
                          {guideSlug ? (
                            <p className="mt-3 text-xs font-medium text-[#D4A843]">Read the full guide →</p>
                          ) : (
                            <p className="mt-3 text-xs text-muted-foreground italic">Full guide coming soon</p>
                          )}
                        </Wrapper>
                      );
                    })}
                  </div>
                  {!matchKey && visibleGuides.length > GUIDES_LIMIT && (
                    <div className="text-center mt-5">
                      <button onClick={() => setShowAllGuides(!showAllGuides)} className="px-6 py-2.5 rounded-lg text-sm font-semibold border border-border hover:border-foreground/30 bg-card hover:shadow-sm transition-all">
                        {showAllGuides ? "Show fewer" : `See all ${visibleGuides.length} guides`}
                      </button>
                    </div>
                  )}
                </section>
              );
            })()}

            {/* --- 2. Competitions & Programs --- */}
            {filteredPrograms.length > 0 && (
              <section className="mb-12">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">🏆</span>
                  <h2 className="font-serif text-lg sm:text-xl font-semibold text-foreground">Competitions &amp; Programs</h2>
                  <div className="h-px flex-1 bg-border" />
                </div>
                <p className="text-sm text-muted-foreground mb-5">
                  {filteredPrograms.length} {filteredPrograms.length === 1 ? "program" : "programs"} found
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
                  {programsToShow.map((p) => (
                    <ProgramCard key={p.id} program={p} />
                  ))}
                </div>
                {filteredPrograms.length > RESULTS_LIMIT && (
                  <div className="text-center mt-6">
                    <button onClick={() => setShowAllPrograms(!showAllPrograms)} className="px-6 py-2.5 rounded-lg text-sm font-semibold border border-border hover:border-foreground/30 bg-card hover:shadow-sm transition-all">
                      {showAllPrograms ? "Show fewer" : `Show all ${filteredPrograms.length} programs`}
                    </button>
                  </div>
                )}
              </section>
            )}

            {/* --- 3. Classes Near You --- */}
            {filteredPlaces.length > 0 && (
              <section className="mb-12">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">📍</span>
                  <h2 className="font-serif text-lg sm:text-xl font-semibold text-foreground">Classes Near You</h2>
                  <div className="h-px flex-1 bg-border" />
                </div>
                <p className="text-sm text-muted-foreground mb-5">
                  {filteredPlaces.length} {filteredPlaces.length === 1 ? "place" : "places"} found
                  {nearMeActive && locationLabel ? ` · ${locationLabel}` : " · Bay Area"}
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
                  {placesToShow.map((p) => (
                    <PlaceCard key={p.id} place={p} userLat={userCoords?.lat} userLng={userCoords?.lng} />
                  ))}
                </div>
                {filteredPlaces.length > RESULTS_LIMIT && (
                  <div className="text-center mt-6">
                    <button onClick={() => setShowAllPlaces(!showAllPlaces)} className="px-6 py-2.5 rounded-lg text-sm font-semibold border border-border hover:border-foreground/30 bg-card hover:shadow-sm transition-all">
                      {showAllPlaces ? "Show fewer" : `Show all ${filteredPlaces.length} places`}
                    </button>
                  </div>
                )}
              </section>
            )}

            {/* --- 4. Latest Stories --- */}
            {kidsArticles.length > 0 && (
              <section className="mb-12">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">📰</span>
                  <h2 className="font-serif text-lg sm:text-xl font-semibold text-foreground">Latest Stories</h2>
                  <div className="h-px flex-1 bg-border" />
                </div>
                <p className="text-sm text-muted-foreground mb-5">
                  News and achievements in kids' education and competitions
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
                  {kidsArticles.slice(0, 6).map((article) => (
                    <Link
                      key={article.id}
                      to={`/article/${article.slug}`}
                      className="group bg-card rounded-xl border border-border overflow-hidden hover:shadow-md transition-all duration-200"
                    >
                      {article.hero_image_url && (
                        <div className="aspect-[16/9] overflow-hidden">
                          <img
                            src={article.hero_image_url}
                            alt=""
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                            loading="lazy"
                          />
                        </div>
                      )}
                      <div className="p-4">
                        <h3 className="font-serif text-[15px] sm:text-base font-semibold text-foreground leading-snug line-clamp-2 group-hover:text-[#A32D2F] transition-colors mb-2">
                          {article.title}
                        </h3>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <span className="px-2 py-0.5 rounded-full bg-muted/30 font-medium capitalize">{article.category?.replace("-", " ") || "News"}</span>
                          <span>·</span>
                          <time>{new Date(article.published_at || "").toLocaleDateString("en-US", { month: "short", day: "numeric" })}</time>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </section>
            )}

            {/* Empty state */}
            {filteredPlaces.length === 0 && filteredPrograms.length === 0 && (
              <div className="text-center py-16 rounded-xl bg-muted/5 border border-dashed border-border">
                <p className="text-3xl mb-3">🔍</p>
                <p className="text-muted-foreground">No results match your selection yet — we're adding more!</p>
              </div>
            )}
          </>
        )}

      </main>
      <SiteFooter />

      {/* Floating back-to-top */}
      <BackToTop />
    </div>
  );
}
