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
        then: (fn: (r: { data: unknown; error: unknown }) => void) => void;
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

const COUNTRY_NAMES: Record<string, string> = {
  US: "United States", UK: "United Kingdom", Canada: "Canada",
  Ireland: "Ireland", Australia: "Australia", Singapore: "Singapore",
  Mauritius: "Mauritius", Portugal: "Portugal", Guyana: "Guyana",
  Switzerland: "Switzerland", Seychelles: "Seychelles", Suriname: "Suriname",
  "Trinidad and Tobago": "Trinidad and Tobago",
};

const COUNTRY_SORT: Record<string, number> = {
  US: 0, UK: 1, Canada: 2, Ireland: 3, Australia: 4, Singapore: 5,
};

const PARTY_COLORS: Record<string, string> = {
  Democrat: "#3b82f6",
  Republican: "#ef4444",
  DFL: "#3b82f6",
  Conservative: "#1d4ed8",
  Labour: "#dc2626",
  Nonpartisan: "#9ca3af",
  NDP: "#f97316",
  Liberal: "#dc2626",
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

/* ── scroll card ───────────────────────────────────────────────────── */
function ScrollCard({ leader }: { leader: Leader }) {
  const flag = COUNTRY_FLAGS[leader.country] || "🌐";
  const link = leader.wikipedia_url || leader.website;
  const partyColor = leader.party ? PARTY_COLORS[leader.party] || "#9ca3af" : null;

  const inner = (
    <div className="flex flex-col items-center text-center px-1 py-3 rounded-xl hover:bg-white/80 transition-colors cursor-pointer group"
      style={{ width: 150, minWidth: 150 }}
    >
      {/* Photo */}
      <div className="w-16 h-16 rounded-full flex-shrink-0 bg-gradient-to-br from-[#0B1D3A] to-[#1a3358] flex items-center justify-center overflow-hidden ring-2 ring-white shadow-md group-hover:ring-[#D4A843]/40 transition-all">
        {leader.photo_url ? (
          <img src={leader.photo_url} alt={leader.name} className="w-full h-full object-cover" loading="lazy" />
        ) : (
          <svg viewBox="0 0 24 24" fill="none" stroke="#D4A843" strokeWidth="1" className="w-7 h-7 opacity-50">
            <circle cx="12" cy="8" r="4" />
            <path d="M20 21a8 8 0 10-16 0" />
          </svg>
        )}
      </div>

      {/* Party dot */}
      {partyColor && (
        <div className="flex items-center gap-1 mt-2">
          <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: partyColor }} />
          <span className="text-[10px] text-gray-400">{leader.party}</span>
        </div>
      )}

      {/* Name */}
      <h3 className="font-bold text-[12px] text-[#0B1D3A] leading-tight mt-1.5 line-clamp-2 group-hover:text-[#D4A843] transition-colors">
        {leader.name}
      </h3>

      {/* Position */}
      <p className="text-[10px] text-gray-500 leading-snug mt-1 line-clamp-2 min-h-[28px]">
        {leader.position}
        {leader.company && ` · ${leader.company}`}
      </p>

      {/* Country */}
      <span className="text-[10px] text-gray-400 mt-1">
        {flag} {leader.country}{leader.state ? ` · ${leader.state}` : ""}
      </span>
    </div>
  );

  if (link) {
    return (
      <a href={link} target="_blank" rel="noopener noreferrer" className="no-underline">
        {inner}
      </a>
    );
  }
  return inner;
}

/* ── horizontal scroll strip ───────────────────────────────────────── */
function ScrollStrip({ leaders, label, icon }: { leaders: Leader[]; label: string; icon?: string }) {
  const count = leaders.length;
  const rows = count <= 8 ? 1 : count <= 20 ? 2 : 3;

  return (
    <div className="mb-6">
      {/* Section label */}
      <div className="flex items-center gap-2 mb-2 px-1">
        {icon && <span className="text-base">{icon}</span>}
        <h4 className="text-[14px] font-bold text-[#0B1D3A]">{label}</h4>
        <span className="text-[11px] text-gray-400 font-medium">({count})</span>
      </div>

      {/* Scroll container */}
      <div
        className="leaders-scroll-wrap overflow-x-auto pb-2"
        style={{
          scrollbarWidth: "none",
          WebkitOverflowScrolling: "touch",
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateRows: `repeat(${rows}, auto)`,
            gridAutoFlow: "column",
            gridAutoColumns: "150px",
            gap: "4px 4px",
            width: "max-content",
            paddingRight: 16,
          }}
        >
          {leaders.map((leader) => (
            <ScrollCard key={leader.id} leader={leader} />
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── country section (for Government) ─────────────────────────────── */
function CountrySection({ country, leaders }: { country: string; leaders: Leader[] }) {
  const flag = COUNTRY_FLAGS[country] || "🌐";
  const displayName = COUNTRY_NAMES[country] || country;

  // Group by subcategory within this country
  const subcatOrder = SUBCATEGORY_ORDER.government || [];
  const bySubcat: Record<string, Leader[]> = {};
  for (const l of leaders) {
    const sc = l.subcategory || "Other";
    if (!bySubcat[sc]) bySubcat[sc] = [];
    bySubcat[sc].push(l);
  }

  const sortedSubcats = Object.keys(bySubcat).sort((a, b) => {
    const ai = subcatOrder.indexOf(a);
    const bi = subcatOrder.indexOf(b);
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
  });

  // If only one subcategory, show as single scroll
  const isSingle = sortedSubcats.length === 1;

  return (
    <div className="mb-8">
      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-200">
        <span className="text-xl">{flag}</span>
        <h3 className="text-[16px] font-bold text-[#0B1D3A]">{displayName}</h3>
        <span className="text-[12px] text-gray-400 font-medium">({leaders.length})</span>
      </div>

      {isSingle ? (
        <ScrollStrip
          leaders={bySubcat[sortedSubcats[0]]}
          label={sortedSubcats[0]}
          icon={SUBCATEGORY_ICONS[sortedSubcats[0]]}
        />
      ) : (
        sortedSubcats.map((sc) => (
          <ScrollStrip
            key={sc}
            leaders={bySubcat[sc]}
            label={sc}
            icon={SUBCATEGORY_ICONS[sc]}
          />
        ))
      )}
    </div>
  );
}

/* ── category section (non-Government) ────────────────────────────── */
function CategorySection({ category, leaders }: { category: string; leaders: Leader[] }) {
  const subcatOrder = SUBCATEGORY_ORDER[category] || [];
  const bySubcat: Record<string, Leader[]> = {};
  for (const l of leaders) {
    const sc = l.subcategory || "Other";
    if (!bySubcat[sc]) bySubcat[sc] = [];
    bySubcat[sc].push(l);
  }

  const sortedSubcats = Object.keys(bySubcat).sort((a, b) => {
    const ai = subcatOrder.indexOf(a);
    const bi = subcatOrder.indexOf(b);
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
  });

  return (
    <div className="mb-8">
      {sortedSubcats.map((sc) => (
        <ScrollStrip
          key={sc}
          leaders={bySubcat[sc]}
          label={sc}
          icon={SUBCATEGORY_ICONS[sc]}
        />
      ))}
    </div>
  );
}

/* ── main page ─────────────────────────────────────────────────────── */
export default function LeadersPage() {
  const [leaders, setLeaders] = useState<Leader[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("government");
  const [search, setSearch] = useState("");

  /* fetch data */
  useEffect(() => {
    sb.from("diaspora_leaders")
      .select("*")
      .order("sort_order", { ascending: true })
      .then(({ data, error }: { data: unknown; error: unknown }) => {
        if (!error && data) setLeaders(data as Leader[]);
        setLoading(false);
      });
  }, []);

  /* filtered leaders */
  const filtered = useMemo(() => {
    let result = leaders.filter((l) => l.category === activeTab);
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

  /* build sections */
  const sections = useMemo(() => {
    const cat = activeTab;
    const catLeaders = filtered.filter((l) => l.category === cat);
    if (catLeaders.length === 0) return [];

    if (cat === "government") {
      // Group by country
      const byCountry: Record<string, Leader[]> = {};
      for (const l of catLeaders) {
        const c = l.country || "US";
        if (!byCountry[c]) byCountry[c] = [];
        byCountry[c].push(l);
      }
      const sortedCountries = Object.keys(byCountry).sort(
        (a, b) => (COUNTRY_SORT[a] ?? 99) - (COUNTRY_SORT[b] ?? 99)
      );
      return [{
        category: cat,
        type: "government" as const,
        countries: sortedCountries.map((c) => ({ country: c, leaders: byCountry[c] })),
        total: catLeaders.length,
      }];
    }

    return [{
      category: cat,
      type: "other" as const,
      leaders: catLeaders,
      total: catLeaders.length,
    }];
  }, [filtered, activeTab]);

  const totalCount = leaders.length;
  const countryCount = new Set(leaders.map((l) => l.country)).size;

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
          <div
            style={{
              position: "absolute",
              inset: 0,
              background:
                "radial-gradient(ellipse at 30% 50%, rgba(212,168,67,0.08) 0%, transparent 70%), radial-gradient(ellipse at 70% 50%, rgba(212,168,67,0.05) 0%, transparent 60%)",
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
              the Indian community&apos;s extraordinary impact on the global stage.
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
          <div className="max-w-5xl mx-auto px-4">
            <div className="flex gap-0 overflow-x-auto" style={{ scrollbarWidth: "none" }}>
              {CATEGORY_TABS.map((tab) => (
                <button
                  key={tab.value}
                  onClick={() => setActiveTab(tab.value)}
                  className="py-3.5 px-5 text-[13px] font-semibold whitespace-nowrap transition-colors"
                  style={{
                    color: activeTab === tab.value ? "#0B1D3A" : "#9ca3af",
                    borderBottom:
                      activeTab === tab.value
                        ? "2.5px solid #D4A843"
                        : "2.5px solid transparent",
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-5xl mx-auto px-4 pt-8 pb-16">
          {loading ? (
            <div className="text-center py-16">
              <div className="inline-block w-8 h-8 border-2 border-[#D4A843] border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-gray-400 mt-3">Loading leaders…</p>
            </div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-16">
              <p className="text-lg text-gray-400">No leaders found.</p>
              <button
                onClick={() => setSearch("")}
                className="mt-3 text-sm text-[#D4A843] hover:underline"
              >
                Clear search
              </button>
            </div>
          ) : (
            sections.map((section) => (
              <div key={section.category}>
                {section.type === "government" ? (
                  section.countries.map((c) => (
                    <CountrySection
                      key={c.country}
                      country={c.country}
                      leaders={c.leaders}
                    />
                  ))
                ) : (
                  <CategorySection
                    category={section.category}
                    leaders={section.leaders}
                  />
                )}
              </div>
            ))
          )}

          {/* Footer note */}
          <div className="bg-white border border-gray-100 rounded-xl p-5 text-center mt-8">
            <p className="text-sm text-gray-500 leading-relaxed">
              This page celebrates leaders of the Indian diaspora across government, business,
              arts, and science — regardless of political party or affiliation. Know someone
              we&apos;re missing?{" "}
              <a
                href="mailto:signals@thevideshi.com"
                className="text-[#D4A843] hover:underline"
              >
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
