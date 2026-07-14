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

/* ── leader detail modal ───────────────────────────────────────────── */
function LeaderModal({ leader, onClose }: { leader: Leader; onClose: () => void }) {
  const flag = COUNTRY_FLAGS[leader.country] || "🌐";
  const partyColor = leader.party ? PARTY_COLORS[leader.party] || "#9ca3af" : null;

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => { document.removeEventListener("keydown", onKey); document.body.style.overflow = ""; };
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4" onClick={onClose}>
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

      {/* Card */}
      <div
        className="relative bg-white rounded-2xl shadow-2xl max-w-sm w-full mx-auto overflow-hidden animate-[scaleIn_0.2s_ease-out]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top gradient band */}
        <div className="h-24 bg-gradient-to-br from-[#0B1D3A] to-[#1a3358] relative">
          <button onClick={onClose} className="absolute top-3 right-3 text-white/70 hover:text-white transition-colors">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Photo – overlaps the band */}
        <div className="flex justify-center -mt-14">
          <div className="w-28 h-28 rounded-full bg-gradient-to-br from-[#0B1D3A] to-[#1a3358] flex items-center justify-center overflow-hidden ring-4 ring-white shadow-lg">
            {leader.photo_url ? (
              <img src={leader.photo_url} alt={leader.name} className="w-full h-full object-cover" />
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="#D4A843" strokeWidth="1" className="w-12 h-12 opacity-50">
                <circle cx="12" cy="8" r="4" />
                <path d="M20 21a8 8 0 10-16 0" />
              </svg>
            )}
          </div>
        </div>

        {/* Body */}
        <div className="px-5 pb-5 pt-3 text-center">
          <h2 className="text-lg font-bold text-[#0B1D3A]">{leader.name}</h2>

          <p className="text-sm text-gray-600 mt-1">
            {leader.position}
            {leader.company && <span className="text-gray-400"> · {leader.company}</span>}
          </p>

          <div className="flex items-center justify-center gap-2 mt-2">
            {partyColor && (
              <span className="inline-flex items-center gap-1 text-xs text-gray-500">
                <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: partyColor }} />
                {leader.party}
              </span>
            )}
            <span className="text-xs text-gray-400">
              {flag} {leader.country}{leader.state ? ` · ${leader.state}` : ""}
            </span>
          </div>

          {/* Bio / notable achievement */}
          {(leader.bio || leader.notable_achievement) && (
            <div className="mt-4 text-left">
              {leader.bio && (
                <p className="text-sm text-gray-700 leading-relaxed">{leader.bio}</p>
              )}
              {leader.notable_achievement && (
                <p className="text-sm text-gray-500 mt-2 italic">{leader.notable_achievement}</p>
              )}
            </div>
          )}

          {/* Links */}
          {(leader.wikipedia_url || leader.website || leader.twitter) && (
            <div className="flex items-center justify-center gap-3 mt-4 pt-3 border-t border-gray-100">
              {leader.wikipedia_url && (
                <a href={leader.wikipedia_url} target="_blank" rel="noopener noreferrer"
                  className="text-xs text-gray-500 hover:text-[#0B1D3A] transition-colors flex items-center gap-1">
                  <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                    <path d="M12.09 13.119c-.936 1.932-2.217 4.548-2.853 5.728-.616 1.074-1.127.931-1.532.029-1.406-3.321-4.293-9.144-5.651-12.409-.251-.601-.441-.987-.619-1.139-.181-.15-.554-.24-1.122-.271C.103 5.033 0 4.982 0 4.898v-.455l.052-.045c.924-.005 5.401 0 5.401 0l.051.045v.434c0 .119-.075.176-.225.176l-.564.031c-.485.029-.727.164-.727.407 0 .2.11.585.331 1.156l3.972 8.99 1.98-4.054-1.822-4.139c-.421-.967-.775-1.591-1.065-1.873-.287-.281-.69-.433-1.208-.457-.158-.007-.237-.06-.237-.176v-.434l.051-.045c.267.002 1.477.019 2.721.019 1.263 0 2.214-.017 2.214-.017l.052.045v.434c0 .119-.06.176-.181.176-.543 0-.814.137-.814.411 0 .2.09.512.271.937l1.299 2.98.96-1.951-.615-1.42c-.326-.751-.6-1.262-.82-1.531-.222-.27-.535-.419-.941-.449-.158-.012-.237-.06-.237-.176v-.434l.051-.045s1.393.019 2.481.019c.996 0 2.028-.017 2.028-.017l.052.045v.434c0 .119-.06.176-.181.176-.603 0-.905.16-.905.48 0 .18.09.48.271.9l.638 1.392.645-1.299c.158-.33.237-.592.237-.789 0-.329-.271-.493-.814-.493-.158 0-.237-.06-.237-.176v-.434l.051-.045s1.145.019 1.948.019c.871 0 1.901-.017 1.901-.017l.052.045v.434c0 .119-.075.176-.225.176-.359.012-.66.099-.905.271-.244.171-.551.561-.923 1.17l-1.367 2.721 1.98 4.279 3.654-8.828c.18-.435.271-.769.271-1.005 0-.289-.243-.449-.727-.479l-.637-.031c-.143 0-.217-.057-.217-.176v-.434l.052-.045s1.37.019 2.267.019c.865 0 1.606-.017 1.606-.017l.052.045v.434c0 .119-.075.176-.225.176-.631.024-1.087.175-1.367.451-.284.276-.608.859-.979 1.749l-5.458 12.78c-.405.988-.866.988-1.381-.025z"/>
                  </svg>
                  Wikipedia
                </a>
              )}
              {leader.website && (
                <a href={leader.website} target="_blank" rel="noopener noreferrer"
                  className="text-xs text-gray-500 hover:text-[#0B1D3A] transition-colors flex items-center gap-1">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                    <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" />
                    <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" />
                  </svg>
                  Website
                </a>
              )}
              {leader.twitter && (
                <a href={`https://x.com/${leader.twitter.replace('@','')}`} target="_blank" rel="noopener noreferrer"
                  className="text-xs text-gray-500 hover:text-[#0B1D3A] transition-colors flex items-center gap-1">
                  <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                  </svg>
                  {leader.twitter}
                </a>
              )}
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes scaleIn {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </div>
  );
}

/* ── scroll card ───────────────────────────────────────────────────── */
function ScrollCard({ leader, onSelect }: { leader: Leader; onSelect: (l: Leader) => void }) {
  const flag = COUNTRY_FLAGS[leader.country] || "🌐";
  const partyColor = leader.party ? PARTY_COLORS[leader.party] || "#9ca3af" : null;

  return (
    <div
      className="flex flex-col items-center text-center px-1 py-3 rounded-xl hover:bg-white/80 transition-colors cursor-pointer group"
      style={{ width: 150, minWidth: 150 }}
      onClick={() => onSelect(leader)}
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
}

/* ── horizontal scroll strip ───────────────────────────────────────── */
function ScrollStrip({ leaders, label, icon, hideLabel, onSelect }: { leaders: Leader[]; label: string; icon?: string; hideLabel?: boolean; onSelect: (l: Leader) => void }) {
  const count = leaders.length;
  const rows = count <= 8 ? 1 : count <= 20 ? 2 : 3;

  return (
    <div className="mb-6">
      {/* Section label */}
      {!hideLabel && (
        <div className="flex items-center gap-2 mb-2 px-1">
          {icon && <span className="text-base">{icon}</span>}
          <h4 className="text-[14px] font-bold text-[#0B1D3A]">{label}</h4>
          <span className="text-[11px] text-gray-400 font-medium">({count})</span>
        </div>
      )}

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
            <ScrollCard key={leader.id} leader={leader} onSelect={onSelect} />
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── country section (for Government) ─────────────────────────────── */
function CountrySection({ country, leaders, onSelect }: { country: string; leaders: Leader[]; onSelect: (l: Leader) => void }) {
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
          hideLabel
          onSelect={onSelect}
        />
      ) : (
        sortedSubcats.map((sc) => (
          <ScrollStrip
            key={sc}
            leaders={bySubcat[sc]}
            label={sc}
            icon={SUBCATEGORY_ICONS[sc]}
            onSelect={onSelect}
          />
        ))
      )}
    </div>
  );
}

/* ── category section (non-Government) ────────────────────────────── */
function CategorySection({ category, leaders, onSelect }: { category: string; leaders: Leader[]; onSelect: (l: Leader) => void }) {
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
          onSelect={onSelect}
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
  const [selectedLeader, setSelectedLeader] = useState<Leader | null>(null);

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

        {/* Know Your Leader cross-link */}
        <a
          href="/know-your-leader"
          className="block"
          style={{
            background: "linear-gradient(90deg, #0B1D3A 0%, #162d50 100%)",
            borderBottom: "1px solid rgba(212,168,67,0.15)",
          }}
        >
          <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-center gap-2 text-center">
            <span className="text-[13px]">🗳️</span>
            <span className="text-[12px] text-white/70">
              <span className="text-[#D4A843] font-semibold">Know Your Leader</span> — Enter your zip code to find all your elected officials
            </span>
            <span className="text-[12px] text-[#D4A843]">→</span>
          </div>
        </a>

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
                      onSelect={setSelectedLeader}
                    />
                  ))
                ) : (
                  <CategorySection
                    category={section.category}
                    leaders={section.leaders}
                    onSelect={setSelectedLeader}
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

      {/* Leader detail modal */}
      {selectedLeader && (
        <LeaderModal leader={selectedLeader} onClose={() => setSelectedLeader(null)} />
      )}
    </>
  );
}
