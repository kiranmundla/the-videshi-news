import { useState, useEffect, useMemo } from "react";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import { supabase as supabaseTyped } from "@/integrations/supabase/client";

/* ── untyped supabase client ───────────────────────────────────────── */
const sb = supabaseTyped as unknown as {
  from: (t: string) => {
    select: (cols: string) => {
      order: (col: string, opts?: { ascending: boolean }) => {
        then: (fn: (r: { data: any; error: any }) => void) => void;
      };
    };
  };
};

/* ── types ──────────────────────────────────────────────────────────── */
interface Leader {
  id: string;
  name: string;
  position: string;
  category: string;
  subcategory: string | null;
  country: string;
  state: string | null;
  district: string | null;
  company: string | null;
  party: string | null;
  photo_url: string | null;
  website: string | null;
  wikipedia_url: string | null;
  twitter: string | null;
  bio: string | null;
  notable_achievement: string | null;
  status: string;
  sort_order: number;
}

/* ── constants ─────────────────────────────────────────────────────── */
const CATEGORY_TABS = [
  { value: "all", label: "All" },
  { value: "government", label: "Government" },
  { value: "tech_business", label: "Tech & Business" },
  { value: "arts_entertainment", label: "Arts & Entertainment" },
  { value: "science_academia", label: "Science & Academia" },
];

const COUNTRY_FLAGS: Record<string, string> = {
  US: "🇺🇸", UK: "🇬🇧", Canada: "🇨🇦", Ireland: "🇮🇪", Australia: "🇦🇺",
  Singapore: "🇸🇬", Mauritius: "🇲🇺", Portugal: "🇵🇹", Guyana: "🇬🇾",
  Switzerland: "🇨🇭", Seychelles: "🇸🇨", Suriname: "🇸🇷",
  "Trinidad and Tobago": "🇹🇹",
};

const COUNTRY_SORT: Record<string, number> = {
  US: 0, UK: 1, Canada: 2, Ireland: 3, Australia: 4, Singapore: 5,
};

const PARTY_STYLES: Record<string, string> = {
  Democrat: "bg-blue-100 text-blue-800",
  Republican: "bg-red-100 text-red-800",
  DFL: "bg-blue-100 text-blue-800",
  Conservative: "bg-blue-100 text-blue-800",
  Labour: "bg-red-100 text-red-800",
  Nonpartisan: "bg-gray-100 text-gray-700",
  NDP: "bg-orange-100 text-orange-800",
  Liberal: "bg-red-100 text-red-800",
};

const SUBCATEGORY_ORDER: Record<string, string[]> = {
  government: ["Federal", "International", "State", "Local"],
  tech_business: ["CEO", "Founder & VC", "Senior Executive"],
  arts_entertainment: ["Film & TV", "Comedy & Media", "Music", "Writing & Literature"],
  science_academia: ["Space & Aviation", "Nobel Laureate", "University Leader", "Professor", "Research & Medicine"],
};

const SUBCATEGORY_ICONS: Record<string, string> = {
  Federal: "🏛️", International: "🌍", State: "🏗️", Local: "🏙️",
  CEO: "👔", "Founder & VC": "🚀", "Senior Executive": "💼",
  "Film & TV": "🎬", "Comedy & Media": "🎤", Music: "🎵", "Writing & Literature": "✍️",
  "Space & Aviation": "🚀", "Nobel Laureate": "🏆", "University Leader": "🎓",
  Professor: "📚", "Research & Medicine": "🔬", Academic: "📖",
};

const DEFAULT_SHOW = 10;

/* ── small components ──────────────────────────────────────────────── */

function PartyBadge({ party }: { party: string | null }) {
  if (!party) return null;
  const cls = PARTY_STYLES[party] || "bg-gray-100 text-gray-700";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-semibold ${cls}`}>
      {party}
    </span>
  );
}

function LeaderCard({ leader }: { leader: Leader }) {
  const flag = COUNTRY_FLAGS[leader.country] || "🌐";
  const location = [leader.state, leader.district].filter(Boolean).join(" · ");

  return (
    <div className="flex gap-4 p-4 bg-white rounded-xl border border-gray-100 hover:shadow-md transition-shadow">
      {/* Photo */}
      <div className="w-[72px] h-[72px] rounded-full flex-shrink-0 bg-gradient-to-br from-[#0B1D3A] to-[#162d50] flex items-center justify-center overflow-hidden">
        {leader.photo_url ? (
          <img src={leader.photo_url} alt={leader.name} className="w-full h-full object-cover" loading="lazy" />
        ) : (
          <svg viewBox="0 0 24 24" fill="none" stroke="#D4A843" strokeWidth="1" className="w-8 h-8 opacity-60">
            <circle cx="12" cy="8" r="4" />
            <path d="M20 21a8 8 0 10-16 0" />
          </svg>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start gap-2 flex-wrap">
          <h3 className="font-bold text-[#0B1D3A] text-[15px] leading-snug">{leader.name}</h3>
          <PartyBadge party={leader.party} />
        </div>

        <p className="text-[13px] text-gray-600 mt-0.5 leading-snug">
          {leader.position}
          {leader.company && <span className="text-gray-400"> · {leader.company}</span>}
        </p>

        {leader.bio && (
          <p className="text-[12px] text-gray-500 mt-1.5 leading-relaxed line-clamp-2">
            {leader.bio}
          </p>
        )}

        {leader.notable_achievement && (
          <p className="text-[11px] text-[#D4A843] mt-1 leading-snug font-medium line-clamp-1">
            ★ {leader.notable_achievement}
          </p>
        )}

        {/* Footer: location + links */}
        <div className="flex items-center gap-3 mt-2 text-[11px] text-gray-400">
          <span>{flag} {leader.country}{location ? ` · ${location}` : ""}</span>
          <div className="ml-auto flex items-center gap-2 flex-shrink-0">
            {leader.wikipedia_url && (
              <a
                href={leader.wikipedia_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[#D4A843] hover:underline font-medium"
              >
                Wikipedia →
              </a>
            )}
            {leader.website && (
              <a
                href={leader.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[#D4A843] hover:underline font-medium"
              >
                Website →
              </a>
            )}
            {leader.twitter && (
              <a
                href={`https://x.com/${leader.twitter.replace("@", "")}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-gray-600"
                title="X / Twitter"
              >
                𝕏
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── subcategory section with country grouping + expand ─────────── */
function SubcategorySection({
  subcategory,
  leaders,
}: {
  subcategory: string;
  leaders: Leader[];
}) {
  const [expanded, setExpanded] = useState(false);
  const icon = SUBCATEGORY_ICONS[subcategory] || "📌";

  // Group by country
  const byCountry = useMemo(() => {
    const groups: Record<string, Leader[]> = {};
    for (const l of leaders) {
      const c = l.country || "US";
      if (!groups[c]) groups[c] = [];
      groups[c].push(l);
    }
    // Sort countries: US first, then UK, Canada, etc.
    return Object.entries(groups).sort(
      ([a], [b]) => (COUNTRY_SORT[a] ?? 99) - (COUNTRY_SORT[b] ?? 99)
    );
  }, [leaders]);

  // Flatten for counting and limiting
  const totalCount = leaders.length;
  const showAll = expanded || totalCount <= DEFAULT_SHOW;

  // Build display list (country-aware limiting)
  const displayGroups = useMemo(() => {
    if (showAll) return byCountry;
    let remaining = DEFAULT_SHOW;
    const result: [string, Leader[]][] = [];
    for (const [country, list] of byCountry) {
      if (remaining <= 0) break;
      const slice = list.slice(0, remaining);
      result.push([country, slice]);
      remaining -= slice.length;
    }
    return result;
  }, [byCountry, showAll]);

  return (
    <div className="mb-8">
      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-200">
        <span className="text-lg">{icon}</span>
        <h3 className="text-[16px] font-bold text-[#0B1D3A]">{subcategory}</h3>
        <span className="text-[12px] text-gray-400 font-medium">{totalCount}</span>
      </div>

      {displayGroups.map(([country, list]) => (
        <div key={country} className="mb-4">
          {/* Country header — only show if multiple countries in this subcategory */}
          {byCountry.length > 1 && (
            <div className="flex items-center gap-1.5 mb-2 ml-1">
              <span className="text-[14px]">{COUNTRY_FLAGS[country] || "🌐"}</span>
              <span className="text-[13px] font-semibold text-gray-700">{country}</span>
              <span className="text-[11px] text-gray-400">({leaders.filter(l => l.country === country).length})</span>
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {list.map((leader) => (
              <LeaderCard key={leader.id} leader={leader} />
            ))}
          </div>
        </div>
      ))}

      {!showAll && totalCount > DEFAULT_SHOW && (
        <button
          onClick={() => setExpanded(true)}
          className="mt-2 px-4 py-2 text-[13px] font-semibold text-[#D4A843] hover:text-[#b8942b] hover:bg-amber-50 rounded-lg transition-colors"
        >
          Show all {totalCount} {subcategory.toLowerCase()} leaders →
        </button>
      )}

      {expanded && totalCount > DEFAULT_SHOW && (
        <button
          onClick={() => setExpanded(false)}
          className="mt-2 px-4 py-2 text-[12px] text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
        >
          Show fewer
        </button>
      )}
    </div>
  );
}

/* ── main page ─────────────────────────────────────────────────────── */
export default function LeadersPage() {
  const [leaders, setLeaders] = useState<Leader[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("all");
  const [search, setSearch] = useState("");

  /* fetch data */
  useEffect(() => {
    sb.from("diaspora_leaders")
      .select("*")
      .order("sort_order", { ascending: true })
      .then(({ data, error }: { data: any; error: any }) => {
        if (!error && data) setLeaders(data as Leader[]);
        setLoading(false);
      });
  }, []);

  /* derived data */
  const filtered = useMemo(() => {
    let result = leaders;

    // Category filter
    if (activeTab !== "all") {
      result = result.filter((l) => l.category === activeTab);
    }

    // Search filter
    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter(
        (l) =>
          l.name.toLowerCase().includes(q) ||
          (l.position || "").toLowerCase().includes(q) ||
          (l.company || "").toLowerCase().includes(q) ||
          (l.country || "").toLowerCase().includes(q) ||
          (l.state || "").toLowerCase().includes(q) ||
          (l.party || "").toLowerCase().includes(q)
      );
    }

    return result;
  }, [leaders, activeTab, search]);

  /* Group by category → subcategory */
  const sections = useMemo(() => {
    const categories = activeTab === "all"
      ? ["government", "tech_business", "arts_entertainment", "science_academia"]
      : [activeTab];

    return categories.map((cat) => {
      const catLeaders = filtered.filter((l) => l.category === cat);
      const subcatOrder = SUBCATEGORY_ORDER[cat] || [];

      // Group by subcategory
      const subcatMap: Record<string, Leader[]> = {};
      for (const l of catLeaders) {
        const sc = l.subcategory || "Other";
        if (!subcatMap[sc]) subcatMap[sc] = [];
        subcatMap[sc].push(l);
      }

      // Sort subcategories by defined order
      const subcats = Object.keys(subcatMap).sort((a, b) => {
        const ai = subcatOrder.indexOf(a);
        const bi = subcatOrder.indexOf(b);
        return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
      });

      return { category: cat, subcategories: subcats.map((sc) => ({ name: sc, leaders: subcatMap[sc] })), total: catLeaders.length };
    }).filter((s) => s.total > 0);
  }, [filtered, activeTab]);

  const totalCount = leaders.length;
  const countryCount = new Set(leaders.map((l) => l.country)).size;

  const CATEGORY_LABELS: Record<string, string> = {
    government: "Government & Politics",
    tech_business: "Tech & Business",
    arts_entertainment: "Arts & Entertainment",
    science_academia: "Science & Academia",
  };

  return (
    <>
      <Helmet>
        <title>Leaders of the Indian Diaspora | The Videshi</title>
        <meta
          name="description"
          content="Celebrating Indian-origin leaders across government, tech, business, arts, and science — from Silicon Valley boardrooms to the halls of parliaments worldwide."
        />
      </Helmet>

      <Masthead />

      <main className="min-h-screen bg-[#f8f9fa]">
        {/* Hero */}
        <div
          style={{
            background: "linear-gradient(135deg, #0B1D3A 0%, #162d50 50%, #0B1D3A 100%)",
            position: "relative",
            overflow: "hidden",
          }}
        >
          {/* Subtle radial accent */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: "radial-gradient(ellipse at 30% 50%, rgba(212,168,67,0.08) 0%, transparent 70%), radial-gradient(ellipse at 70% 50%, rgba(212,168,67,0.05) 0%, transparent 60%)",
            }}
          />
          <div className="relative z-10 max-w-3xl mx-auto px-4 py-12 sm:py-16 text-center">
            <h1
              style={{
                fontFamily: "'Noto Serif', serif",
                fontSize: "clamp(26px, 5vw, 36px)",
                color: "#D4A843",
                marginBottom: 12,
                letterSpacing: "0.5px",
                fontWeight: 700,
              }}
            >
              Leaders of the Indian Diaspora
            </h1>
            <p className="text-[15px] sm:text-base text-white/70 leading-relaxed max-w-xl mx-auto">
              From Silicon Valley boardrooms to the halls of parliaments worldwide — celebrating
              the Indian community's extraordinary impact on the global stage.
            </p>
            <div
              className="mt-4"
              style={{
                fontSize: 13,
                color: "#D4A843",
                opacity: 0.8,
                letterSpacing: "1.5px",
                textTransform: "uppercase",
                fontWeight: 600,
              }}
            >
              Our community. Our pride.
            </div>

            {/* Search */}
            <div className="max-w-md mx-auto mt-6 relative">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="rgba(255,255,255,0.4)"
                strokeWidth="2"
                className="absolute left-3.5 top-1/2 -translate-y-1/2 w-[18px] h-[18px]"
              >
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input
                type="text"
                placeholder="Search by name, country, or role..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-3 rounded-xl border border-white/15 bg-white/8 text-white text-[14px] placeholder:text-white/40 outline-none focus:border-[#D4A843]/50 transition-colors"
                style={{ backdropFilter: "blur(8px)" }}
              />
            </div>
          </div>
        </div>

        {/* Stats strip */}
        <div
          className="flex justify-center gap-8 sm:gap-12 py-4 border-b"
          style={{ background: "#0B1D3A", borderColor: "rgba(212,168,67,0.15)" }}
        >
          <div className="text-center">
            <div className="text-2xl font-bold text-[#D4A843]">{totalCount}</div>
            <div className="text-[11px] text-white/50 uppercase tracking-wider">Leaders</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-[#D4A843]">{countryCount}</div>
            <div className="text-[11px] text-white/50 uppercase tracking-wider">Countries</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-[#D4A843]">5</div>
            <div className="text-[11px] text-white/50 uppercase tracking-wider">Domains</div>
          </div>
        </div>

        {/* Category Tabs — sticky */}
        <div
          className="sticky top-0 z-50 bg-white border-b border-gray-200"
          style={{ boxShadow: "0 1px 3px rgba(0,0,0,0.04)" }}
        >
          <div className="max-w-4xl mx-auto px-4">
            <div className="flex gap-0 overflow-x-auto" style={{ scrollbarWidth: "none" }}>
              {CATEGORY_TABS.map((tab) => (
                <button
                  key={tab.value}
                  onClick={() => setActiveTab(tab.value)}
                  className="py-3.5 px-5 text-[13px] font-semibold whitespace-nowrap transition-colors"
                  style={{
                    color: activeTab === tab.value ? "#0B1D3A" : "#9ca3af",
                    borderBottom: activeTab === tab.value ? "2.5px solid #D4A843" : "2.5px solid transparent",
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-4xl mx-auto px-4 pt-8 pb-16">
          {loading ? (
            <div className="text-center py-16">
              <div className="inline-block w-8 h-8 border-2 border-[#D4A843] border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-gray-400 mt-3">Loading leaders…</p>
            </div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-16">
              <p className="text-lg text-gray-400">No leaders found.</p>
              <button
                onClick={() => { setActiveTab("all"); setSearch(""); }}
                className="mt-3 text-sm text-[#D4A843] hover:underline"
              >
                Clear filters
              </button>
            </div>
          ) : (
            sections.map(({ category, subcategories, total }) => (
              <div key={category} className="mb-12">
                {/* Category header — only in "All" view */}
                {activeTab === "all" && (
                  <div className="mb-6 pb-2" style={{ borderBottom: "2px solid #D4A843" }}>
                    <h2
                      style={{ fontFamily: "'Noto Serif', serif" }}
                      className="text-xl font-bold text-[#0B1D3A]"
                    >
                      {CATEGORY_LABELS[category] || category}
                      <span className="text-sm font-normal text-gray-400 ml-2">({total})</span>
                    </h2>
                  </div>
                )}

                {subcategories.map(({ name: subName, leaders: subLeaders }) => (
                  <SubcategorySection
                    key={`${category}-${subName}`}
                    subcategory={subName}
                    leaders={subLeaders}
                  />
                ))}
              </div>
            ))
          )}

          {/* Footer note */}
          <div className="bg-white border border-gray-100 rounded-xl p-5 text-center mt-8">
            <p className="text-sm text-gray-500 leading-relaxed">
              This page celebrates leaders of the Indian diaspora across government, business, arts,
              and science — regardless of political party or affiliation.
              Know someone we&apos;re missing?{" "}
              <a href="mailto:signals@thevideshi.com" className="text-[#D4A843] hover:underline">
                Let us know →
              </a>
            </p>
            <p className="text-xs text-gray-400 mt-2">
              Sources: Wikipedia &amp; official websites only. Last updated July 2026.
            </p>
          </div>
        </div>
      </main>

      <SiteFooter />
    </>
  );
}
