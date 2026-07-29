import { useState, useEffect, useMemo, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useSearchParams } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import ZipCodeSearch, { type LocationResult } from "@/components/ZipCodeSearch";
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
  CATEGORY_GRADIENTS,
  LOCAL_CATEGORY_COLORS,
  type KidsLocalPlace,
} from "@/lib/kidsLocalPlaces";

/* ================================================================== */
/* TOPIC DEFINITIONS (flat list replaces old tab hierarchy)           */
/* ================================================================== */

type Topic = {
  key: string;
  label: string;
  icon: string;
  localCategories: string[];
  programCategories: string[];
  programKeyword?: string;
  subtopics?: Topic[];
};

const TOPICS: Topic[] = [
  { key: "math", label: "Math", icon: "🔢", localCategories: ["Math Enrichment"], programCategories: ["Math"] },
  { key: "science_stem", label: "Science & STEM", icon: "🧪", localCategories: ["Coding & STEM"], programCategories: ["Science & STEM"] },
  { key: "spelling_bee", label: "Spelling Bee", icon: "🐝", localCategories: [], programCategories: ["Academic Competitions"], programKeyword: "spell" },
  { key: "debate", label: "Debate", icon: "🗯️", localCategories: [], programCategories: ["Academic Competitions"], programKeyword: "debate" },
  { key: "robotics", label: "Robotics", icon: "🤖", localCategories: [], programCategories: ["Robotics"] },
  { key: "chess", label: "Chess", icon: "♟️", localCategories: ["Chess"], programCategories: ["Chess"] },
  { key: "coding", label: "Coding", icon: "💻", localCategories: ["Coding & STEM"], programCategories: ["Coding & CS"] },
  {
    key: "sports", label: "Sports", icon: "🏅", localCategories: ["Cricket", "Swimming", "Martial Arts", "Gymnastics"], programCategories: ["Sports"],
    subtopics: [
      { key: "cricket", label: "Cricket", icon: "🏏", localCategories: ["Cricket"], programCategories: ["Sports"], programKeyword: "cricket" },
      { key: "tennis", label: "Tennis", icon: "🎾", localCategories: [], programCategories: ["Sports"], programKeyword: "tennis" },
      { key: "badminton", label: "Badminton", icon: "🏸", localCategories: [], programCategories: ["Sports"], programKeyword: "badminton" },
      { key: "swimming", label: "Swimming", icon: "🏊", localCategories: ["Swimming"], programCategories: ["Sports"], programKeyword: "swimming" },
      { key: "soccer", label: "Soccer", icon: "⚽", localCategories: [], programCategories: ["Sports"], programKeyword: "soccer" },
      { key: "basketball", label: "Basketball", icon: "🏀", localCategories: [], programCategories: ["Sports"], programKeyword: "basketball" },
      { key: "martial_arts", label: "Martial Arts", icon: "🥋", localCategories: ["Martial Arts"], programCategories: ["Sports"], programKeyword: "martial" },
      { key: "gymnastics", label: "Gymnastics", icon: "🤸", localCategories: ["Gymnastics"], programCategories: ["Sports"], programKeyword: "gymnast" },
    ],
  },
  { key: "dance", label: "Dance", icon: "💃", localCategories: ["Dance"], programCategories: ["Dance"] },
  { key: "music", label: "Music", icon: "🎵", localCategories: ["Music"], programCategories: ["Music"] },
  { key: "art", label: "Art", icon: "🎨", localCategories: ["Art"], programCategories: ["Cultural & Arts"] },
  { key: "language", label: "Language", icon: "🌍", localCategories: ["Language"], programCategories: ["Language"] },
  { key: "sat_prep", label: "SAT / ACT Prep", icon: "📝", localCategories: [], programCategories: ["College Prep"], programKeyword: "sat|act|kaplan|khan|princeton" },
  { key: "college_counseling", label: "College Counseling", icon: "🎓", localCategories: [], programCategories: ["College Prep"], programKeyword: "essay|counsel|c2" },
  { key: "volunteering", label: "Volunteering", icon: "🤝", localCategories: [], programCategories: ["Volunteering"] },
  { key: "tutoring", label: "Tutoring", icon: "📚", localCategories: ["Tutoring"], programCategories: [] },
  { key: "daycare", label: "Daycare", icon: "🏠", localCategories: ["Daycare"], programCategories: [] },
];

const ALL_TOPICS_FLAT = TOPICS.flatMap((t) => [t, ...(t.subtopics || [])]);

/* ================================================================== */
/* CONSTANTS                                                          */
/* ================================================================== */

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

const RESULTS_LIMIT = 12;

/* --- Image map for filter card backgrounds --- */
const KIDS_CAT_IMG: Record<string, string> = {
  preschool: "/images/kids/preschool.jpg",
  elementary: "/images/kids/elementary.jpg",
  middle_school: "/images/kids/middle_school.jpg",
  high_school: "/images/kids/high_school.jpg",
  sports: "/images/kids/sports.jpg",
  dance: "/images/kids/dance.jpg",
  music: "/images/kids/music.jpg",
  art: "/images/kids/art.jpg",
  coding: "/images/kids/coding.jpg",
  language: "/images/kids/language.jpg",
  chess: "/images/kids/chess.jpg",
  volunteering: "/images/kids/volunteering.jpg",
  math: "/images/kids/math.jpg",
  science_stem: "/images/kids/science.jpg",
  spelling_bee: "/images/kids/spelling.jpg",
  debate: "/images/kids/spelling.jpg",
  robotics: "/images/kids/robotics.jpg",
  sat_prep: "/images/kids/test_prep.jpg",
  college_counseling: "/images/kids/college.jpg",
  tutoring: "/images/kids/tutoring.jpg",
  daycare: "/images/kids/daycare.jpg",
  cricket: "/images/kids/cricket.jpg",
  tennis: "/images/kids/tennis.jpg",
  badminton: "/images/kids/badminton.jpg",
  swimming: "/images/kids/swimming.jpg",
  soccer: "/images/kids/soccer.jpg",
  basketball: "/images/kids/basketball.jpg",
  martial_arts: "/images/kids/martial_arts.jpg",
  gymnastics: "/images/kids/gymnastics.jpg",
};

/* --- Icon map for place cards (replaces CATEGORY_TREE lookup) --- */
const LOCAL_CAT_ICON: Record<string, string> = {
  Dance: "💃", Music: "🎵", Art: "🎨", Swimming: "🏊", Cricket: "🏏",
  "Martial Arts": "🥋", Gymnastics: "🤸", Tutoring: "📚", "Math Enrichment": "🔢",
  "Coding & STEM": "💻", Chess: "♟️", Language: "🌍", Daycare: "🏠",
};

/* --- Gradient maps --- */
const AGE_GRADIENTS: Record<string, string> = {
  preschool: "linear-gradient(135deg, #D4A843 0%, #A32D2F 100%)",
  elementary: "linear-gradient(135deg, #0B1D3A 0%, #1e3a5f 100%)",
  middle_school: "linear-gradient(135deg, #1e3a5f 0%, #2d5a3f 100%)",
  high_school: "linear-gradient(135deg, #374151 0%, #1f2937 100%)",
};

const TOPIC_GRADIENTS: Record<string, string> = {
  math: "linear-gradient(135deg, #4338ca 0%, #3730a3 100%)",
  science_stem: "linear-gradient(135deg, #047857 0%, #065f46 100%)",
  spelling_bee: "linear-gradient(135deg, #9333ea 0%, #7e22ce 100%)",
  debate: "linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)",
  robotics: "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
  chess: "linear-gradient(135deg, #374151 0%, #1f2937 100%)",
  coding: "linear-gradient(135deg, #0891b2 0%, #0e7490 100%)",
  sports: "linear-gradient(135deg, #15803d 0%, #166534 100%)",
  dance: "linear-gradient(135deg, #be185d 0%, #9d174d 100%)",
  music: "linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)",
  art: "linear-gradient(135deg, #c2410c 0%, #9a3412 100%)",
  language: "linear-gradient(135deg, #0d9488 0%, #0f766e 100%)",
  sat_prep: "linear-gradient(135deg, #b91c1c 0%, #991b1b 100%)",
  college_counseling: "linear-gradient(135deg, #4a1942 0%, #2d1b69 100%)",
  volunteering: "linear-gradient(135deg, #0369a1 0%, #075985 100%)",
  tutoring: "linear-gradient(135deg, #92400e 0%, #78350f 100%)",
  daycare: "linear-gradient(135deg, #D4A843 0%, #92400e 100%)",
  cricket: "linear-gradient(135deg, #15803d 0%, #14532d 100%)",
  tennis: "linear-gradient(135deg, #ca8a04 0%, #a16207 100%)",
  badminton: "linear-gradient(135deg, #0891b2 0%, #155e75 100%)",
  swimming: "linear-gradient(135deg, #0284c7 0%, #0c4a6e 100%)",
  soccer: "linear-gradient(135deg, #16a34a 0%, #15803d 100%)",
  basketball: "linear-gradient(135deg, #ea580c 0%, #c2410c 100%)",
  martial_arts: "linear-gradient(135deg, #dc2626 0%, #991b1b 100%)",
  gymnastics: "linear-gradient(135deg, #d946ef 0%, #a21caf 100%)",
};

const DEFAULT_GRADIENT = "linear-gradient(135deg, #374151 0%, #1f2937 100%)";

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

/* ---------- Featured Deadlines Strip ---------- */

function FeaturedDeadlines({ deadlines }: { deadlines: KidsDeadline[] }) {
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
    </section>
  );
}

/* ---------- Filter Card ---------- */

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

/* ---------- Place Card ---------- */

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
          <span className="text-4xl opacity-80">{LOCAL_CAT_ICON[place.category] || "📍"}</span>
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
        <div className="flex items-center gap-2 pt-3 border-t border-border/50">
          <Link to={`/kids/places/${place.slug}`} className="flex-1 text-center px-2 py-1.5 rounded-lg text-xs font-semibold text-[#A32D2F] bg-red-50 hover:bg-red-100 transition-colors no-underline">View Details →</Link>
          <a href={mapsUrl(place)} target="_blank" rel="noopener noreferrer" className="flex-1 text-center px-2 py-1.5 rounded-lg text-xs font-medium bg-muted/30 hover:bg-muted/50 text-foreground transition-colors">🗺️ Directions</a>
          {place.website && <a href={place.website} target="_blank" rel="noopener noreferrer" className="flex-1 text-center px-2 py-1.5 rounded-lg text-xs font-medium bg-muted/30 hover:bg-muted/50 text-foreground transition-colors">🌐 Website</a>}
          {place.phone && <a href={`tel:${place.phone.replace(/[^\d+]/g, "")}`} className="flex-1 text-center px-2 py-1.5 rounded-lg text-xs font-medium bg-muted/30 hover:bg-muted/50 text-foreground transition-colors">📞 Call</a>}
        </div>
      </div>
    </div>
  );
}

/* ---------- Program Card ---------- */

function ProgramCard({ program, deadlines }: { program: KidsProgram; deadlines?: KidsDeadline[] }) {
  const catColor = PROGRAM_CAT_COLORS[program.category || ""] || "bg-gray-100 text-gray-700";
  const upcoming = deadlines?.filter((d) => d.program_id === program.id && daysUntil(d.deadline_date) >= 0).slice(0, 2) || [];

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
        {/* Contextual deadlines */}
        {upcoming.length > 0 && (
          <div className="mb-3 space-y-1.5">
            {upcoming.map((dl) => {
              const days = daysUntil(dl.deadline_date);
              return (
                <div key={dl.id} className={`px-3 py-1.5 rounded-lg text-[11px] font-medium ${days <= 7 ? "bg-red-50 text-red-700" : "bg-amber-50 text-amber-700"}`}>
                  ⏰ {dl.title} — {days === 0 ? "Today!" : days === 1 ? "Tomorrow!" : `${days} days left`}
                </div>
              );
            })}
          </div>
        )}
        <div className="mt-auto pt-2"><span className="text-sm font-medium text-[#A32D2F] group-hover:underline">Learn More →</span></div>
      </div>
    </Link>
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

/* ================================================================== */
/* GETTING STARTED GUIDES (static initial content, will move to DB)   */
/* ================================================================== */

type Guide = {
  topic: string;
  title: string;
  summary: string;
  icon: string;
};

const GUIDES: Guide[] = [
  { topic: "math", title: "Math Competitions — The Complete Path", summary: "From Math Kangaroo to AMC/AIME, here's how to get your child started on the competitive math track and what to expect at each level.", icon: "🔢" },
  { topic: "spelling_bee", title: "Spelling Bee — From School to Nationals", summary: "Everything parents need to know about spelling bees: South Asian Spelling Bee, Scripps, NSF — the preparation path, costs, and what makes it rewarding.", icon: "🐝" },
  { topic: "science_stem", title: "Science Olympiad & STEM Competitions", summary: "A guide to Science Olympiad, science fairs, and STEM programs — how to find the right fit and prepare your child for success.", icon: "🧪" },
  { topic: "robotics", title: "Getting Into Robotics", summary: "FIRST LEGO League, VEX, and beyond — the robotics competition landscape, costs, team structure, and how to get started from elementary through high school.", icon: "🤖" },
  { topic: "chess", title: "Chess for Kids — Why It Matters", summary: "How chess builds critical thinking, the tournament path from local to nationals, and finding the right chess program for your child.", icon: "♟️" },
  { topic: "coding", title: "Coding & CS for Kids", summary: "From Scratch to Python to USACO — the coding path for kids, free resources, structured programs, and how coding competitions work.", icon: "💻" },
  { topic: "cricket", title: "Cricket in the US — A Parent's Guide", summary: "Finding cricket leagues, USA Cricket youth programs, equipment, and how the competitive pathway works for young cricketers in America.", icon: "🏏" },
  { topic: "dance", title: "Indian Classical & Contemporary Dance", summary: "Bharatanatyam, Kathak, Bollywood, and more — finding the right dance school, exam pathways, and performance opportunities.", icon: "💃" },
  { topic: "sat_prep", title: "SAT/ACT Prep — What Actually Works", summary: "An honest look at prep options — free vs. paid, self-study vs. courses, timeline, and how to maximize your child's score without burnout.", icon: "📝" },
  { topic: "debate", title: "Debate & Public Speaking", summary: "National History Bee, Model UN, speech & debate leagues — how to develop communication skills and the competitive landscape.", icon: "🗯️" },
];

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
  const selectedTopicKey = searchParams.get("topic") || null;
  const selectedSubTopicKey = searchParams.get("sub") || null;

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

  /* ---- location state ---- */
  const [nearMeActive, setNearMeActive] = useState(false);
  const [userCoords, setUserCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [locationLabel, setLocationLabel] = useState("");
  const { location: ipLocation } = useUserLocation();

  const handleLocation = useCallback((result: LocationResult | null) => {
    if (!result) {
      setNearMeActive(false); setUserCoords(null); setLocationLabel("");
      return;
    }
    setUserCoords({ lat: result.lat, lng: result.lng });
    setNearMeActive(true);
    setLocationLabel(result.label);
  }, []);

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
  const [searchText, setSearchText] = useState("");

  /* ---- data load ---- */
  useEffect(() => {
    (async () => {
      try {
        const [p, d, lp] = await Promise.all([fetchKidsPrograms(), fetchKidsDeadlines(50), fetchLocalPlaces()]);
        setPrograms(p); setDeadlines(d); setLocalPlaces(lp);
      } catch (err) { console.error("Kids data load failed:", err); }
      finally { setLoading(false); }
    })();
  }, []);

  /* ---- resolve active topic ---- */
  const activeTopic = selectedTopicKey ? TOPICS.find((t) => t.key === selectedTopicKey) || null : null;
  const activeSubTopic = activeTopic?.subtopics && selectedSubTopicKey
    ? activeTopic.subtopics.find((st) => st.key === selectedSubTopicKey) || null : null;

  // The effective topic for filtering (subtopic takes priority)
  const effectiveTopic: Topic | null = activeSubTopic || activeTopic;

  /* ---- filtered places ---- */
  const searchLower = searchText.toLowerCase().trim();

  const filteredPlaces = useMemo(() => {
    let list = localPlaces;

    if (effectiveTopic) {
      if (effectiveTopic.localCategories.length > 0) {
        list = list.filter((p) => effectiveTopic.localCategories.includes(p.category));
      } else {
        list = [];
      }
    }

    if (selectedAge) {
      list = list.filter((p) => placeMatchesAge(p.age_range, selectedAge));
    }

    if (searchLower) {
      list = list.filter((p) =>
        p.name.toLowerCase().includes(searchLower) ||
        p.city.toLowerCase().includes(searchLower) ||
        (p.description || "").toLowerCase().includes(searchLower) ||
        p.category.toLowerCase().includes(searchLower),
      );
    }

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
  }, [localPlaces, effectiveTopic, selectedAge, searchLower, userCoords]);

  /* ---- filtered programs ---- */
  const filteredPrograms = useMemo(() => {
    let list = programs;

    if (effectiveTopic) {
      if (effectiveTopic.programCategories.length > 0) {
        list = list.filter((p) => effectiveTopic.programCategories.includes(p.category || ""));
      } else {
        list = [];
      }

      if (effectiveTopic.programKeyword) {
        const keywords = effectiveTopic.programKeyword.toLowerCase().split("|");
        list = list.filter((p) => {
          const haystack = `${p.name} ${p.description || ""} ${p.subcategory || ""}`.toLowerCase();
          return keywords.some((kw) => haystack.includes(kw));
        });
      }
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
  }, [programs, effectiveTopic, selectedAge, searchLower]);

  /* ---- matching guides ---- */
  const matchingGuides = useMemo(() => {
    if (!effectiveTopic) return GUIDES.slice(0, 3); // show top 3 when browsing all
    return GUIDES.filter((g) => g.topic === effectiveTopic.key);
  }, [effectiveTopic]);

  /* ---- contextual deadlines for programs ---- */
  const contextualDeadlines = useMemo(() => {
    if (!effectiveTopic) return deadlines;
    const progIds = new Set(filteredPrograms.map((p) => p.id));
    return deadlines.filter((d) => progIds.has(d.program_id));
  }, [deadlines, filteredPrograms, effectiveTopic]);

  /* ---- display slices ---- */
  const placesToShow = showAllPlaces ? filteredPlaces : filteredPlaces.slice(0, RESULTS_LIMIT);
  const programsToShow = showAllPrograms ? filteredPrograms : filteredPrograms.slice(0, RESULTS_LIMIT);

  /* ---- reset on filter changes ---- */
  useEffect(() => { setShowAllPlaces(false); setShowAllPrograms(false); }, [selectedAge, selectedTopicKey, selectedSubTopicKey, searchText]);

  /* ================================================================ */
  /* RENDER                                                           */
  /* ================================================================ */

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>Kids &amp; Education — The Videshi</title>
        <meta name="description" content="Activities, classes, programs & competitions for K-12 students. Find what's right for your child." />
        <link rel="canonical" href="https://www.thevideshi.com/kids" />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container flex-1 pt-8 md:pt-10 pb-16" style={{ maxWidth: 1200 }}>

        {/* ═══════ HEADER ═══════ */}
        <div className="mb-8">
          <h1 className="font-serif text-3xl md:text-5xl text-foreground mb-2">🎓 Kids &amp; Education</h1>
          <p className="text-muted-foreground text-base sm:text-lg max-w-2xl">
            Find the right activities, classes &amp; programs for your child
          </p>
        </div>

        {/* ═══════ LOCATION BAR + SEARCH ═══════ */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 mb-6 p-4 rounded-xl bg-muted/10 border border-border">
          <ZipCodeSearch onLocation={handleLocation} active={nearMeActive} />
          {nearMeActive && locationLabel && (
            <span className="text-xs text-muted-foreground">{locationLabel}</span>
          )}
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

        {/* ═══════ FEATURED DEADLINES ═══════ */}
        {!loading && <FeaturedDeadlines deadlines={deadlines} />}

        {/* ═══════ TOPIC SELECTOR ═══════ */}
        <div className="mb-8">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Browse by Activity</p>
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-2">
            {TOPICS.map((topic) => (
              <FilterCard
                key={topic.key}
                label={topic.label}
                icon={topic.icon}
                size="sm"
                active={activeTopic?.key === topic.key}
                gradient={TOPIC_GRADIENTS[topic.key]}
                imgKey={topic.key}
                onClick={() => setParam("topic", activeTopic?.key === topic.key ? null : topic.key, ["sub"])}
              />
            ))}
          </div>
          {activeTopic && (
            <button onClick={() => setParam("topic", null, ["sub"])} className="mt-3 text-xs text-muted-foreground hover:text-foreground transition-colors">
              ✕ Show all activities
            </button>
          )}
        </div>

        {/* ═══════ SUB-TOPICS (e.g. Sports → Cricket/Tennis) ═══════ */}
        {activeTopic?.subtopics && activeTopic.subtopics.length > 0 && (
          <div className="mb-6">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{activeTopic.label}</p>
            <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-6 gap-1.5">
              <FilterCard label="All" icon="🏅" size="xs" active={!activeSubTopic}
                gradient={DEFAULT_GRADIENT}
                onClick={() => setParam("sub", null)} />
              {activeTopic.subtopics.map((st) => (
                <FilterCard key={st.key} label={st.label} icon={st.icon} size="xs"
                  active={activeSubTopic?.key === st.key}
                  gradient={TOPIC_GRADIENTS[st.key]} imgKey={st.key}
                  onClick={() => setParam("sub", st.key)} />
              ))}
            </div>
          </div>
        )}

        {/* ═══════ AGE FILTER (applies to competitions + classes, not guides) ═══════ */}
        <div className="mb-8">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Age Group</p>
          <div className="grid grid-cols-4 gap-2">
            {AGE_GROUPS.map((ag) => (
              <FilterCard key={ag.key} label={ag.label} icon={ag.icon} subtitle={ag.sub} size="md"
                active={selectedAge === ag.key} gradient={AGE_GRADIENTS[ag.key]} imgKey={ag.key}
                onClick={() => setParam("age", selectedAge === ag.key ? null : ag.key)} />
            ))}
          </div>
          {selectedAge && (
            <button onClick={() => setParam("age", null)} className="mt-3 text-xs text-muted-foreground hover:text-foreground transition-colors">
              ✕ Show all ages
            </button>
          )}
        </div>

        {loading ? (
          <Skeleton n={6} />
        ) : (
          <>
            {/* ═══════ SECTION 1: GETTING STARTED GUIDES ═══════ */}
            {matchingGuides.length > 0 && (
              <section className="mb-12">
                <div className="flex items-center gap-2 mb-5">
                  <span className="text-lg">📖</span>
                  <h2 className="font-serif text-xl font-semibold text-foreground">
                    {effectiveTopic ? `Getting Started with ${effectiveTopic.label}` : "Getting Started Guides"}
                  </h2>
                  <div className="h-px flex-1 bg-border" />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {matchingGuides.map((guide) => (
                    <div key={guide.topic} className="rounded-xl border border-border bg-card p-5 sm:p-6 hover:shadow-md hover:border-[#D4A843]/50 transition-all">
                      <div className="flex items-start gap-3 mb-3">
                        <span className="text-2xl">{guide.icon}</span>
                        <h3 className="font-serif text-[15px] sm:text-base font-semibold text-foreground leading-snug">{guide.title}</h3>
                      </div>
                      <p className="text-sm text-muted-foreground leading-relaxed">{guide.summary}</p>
                      <p className="mt-3 text-xs text-muted-foreground italic">Full guide coming soon</p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* ═══════ SECTION 2: COMPETITIVE TRACK ═══════ */}
            {filteredPrograms.length > 0 && (
              <section className="mb-12">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">🏆</span>
                  <h2 className="font-serif text-xl font-semibold text-foreground">
                    {effectiveTopic ? `${effectiveTopic.label} — Competitions & Programs` : "Competitions & Programs"}
                  </h2>
                  <div className="h-px flex-1 bg-border" />
                </div>
                <p className="text-sm text-muted-foreground mb-5">
                  {filteredPrograms.length} {filteredPrograms.length === 1 ? "program" : "programs"} found
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
                  {programsToShow.map((p) => (
                    <ProgramCard key={p.id} program={p} deadlines={contextualDeadlines} />
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

            {/* ═══════ SECTION 3: CLASSES NEAR YOU ═══════ */}
            {filteredPlaces.length > 0 && (
              <section className="mb-12">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">📍</span>
                  <h2 className="font-serif text-xl font-semibold text-foreground">
                    {effectiveTopic ? `${effectiveTopic.label} — Classes Near You` : "Classes Near You"}
                  </h2>
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

            {/* Empty state */}
            {filteredPlaces.length === 0 && filteredPrograms.length === 0 && matchingGuides.length === 0 && (
              <div className="text-center py-16 rounded-xl bg-muted/5 border border-dashed border-border">
                <p className="text-3xl mb-3">🔍</p>
                <p className="text-muted-foreground">No results match your selection yet — we're adding more!</p>
              </div>
            )}
          </>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
