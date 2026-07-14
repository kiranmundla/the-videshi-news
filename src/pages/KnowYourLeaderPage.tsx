import { useState, useEffect, useCallback, useRef } from "react";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import { supabase as supabaseTyped } from "@/integrations/supabase/client";

/* ── untyped supabase for diaspora_leaders ──────────────────────────── */
const sb = supabaseTyped as unknown as {
  from: (t: string) => {
    select: (cols: string) => {
      then: (fn: (r: { data: unknown; error: unknown }) => void) => void;
    };
  };
};

/* ── types ──────────────────────────────────────────────────────────── */
interface CivicChannel {
  type: string;
  id: string;
}

interface CivicOfficial {
  name: string;
  party?: string;
  photoUrl?: string;
  phones?: string[];
  urls?: string[];
  emails?: string[];
  channels?: CivicChannel[];
}

interface CivicOffice {
  name: string;
  divisionId: string;
  levels?: string[];
  roles?: string[];
  officialIndices: number[];
}

interface CivicResponse {
  offices: CivicOffice[];
  officials: CivicOfficial[];
  normalizedInput?: {
    line1: string;
    city: string;
    state: string;
    zip: string;
  };
}

interface DiasporaLeader {
  name: string;
  wikipedia_url: string | null;
}

interface GroupedOfficial {
  name: string;
  office: string;
  party?: string;
  photoUrl?: string;
  phone?: string;
  website?: string;
  email?: string;
  twitter?: string;
  facebook?: string;
  isDiaspora: boolean;
  wikiUrl?: string;
}

interface OfficialGroup {
  label: string;
  icon: string;
  officials: GroupedOfficial[];
}

/* ── constants ─────────────────────────────────────────────────────── */
const GOOGLE_API_KEY = import.meta.env.VITE_GOOGLE_API_KEY || "";

const PARTY_COLORS: Record<string, string> = {
  "Democratic Party": "#3b82f6",
  "Republican Party": "#ef4444",
  "Libertarian Party": "#f59e0b",
  "Green Party": "#22c55e",
  "Nonpartisan": "#9ca3af",
  "Independent": "#8b5cf6",
};

const LEVEL_CONFIG: { key: string; label: string; icon: string; keywords: string[] }[] = [
  { key: "federal", label: "Federal", icon: "🏛️", keywords: ["country"] },
  { key: "state", label: "State", icon: "🏗️", keywords: ["administrativeArea1"] },
  { key: "county", label: "County", icon: "📋", keywords: ["administrativeArea2"] },
  { key: "city", label: "City & Local", icon: "🏙️", keywords: ["locality", "regional", "special"] },
];

/* ── helpers ────────────────────────────────────────────────────────── */
function classifyOffice(office: CivicOffice): string {
  const levels = office.levels || [];
  const name = office.name.toLowerCase();

  if (levels.includes("country") || name.includes("president") || name.includes("u.s. senator") || name.includes("u.s. representative")) {
    return "federal";
  }
  if (levels.includes("administrativeArea1") || name.includes("governor") || name.includes("state senator") || name.includes("state representative") || name.includes("state assembly") || name.includes("lieutenant governor") || name.includes("attorney general") || name.includes("secretary of state") || name.includes("state comptroller") || name.includes("state treasurer")) {
    return "state";
  }
  if (levels.includes("administrativeArea2") || name.includes("county")) {
    return "county";
  }
  return "city";
}

function getChannel(official: CivicOfficial, type: string): string | undefined {
  return official.channels?.find((c) => c.type.toLowerCase() === type.toLowerCase())?.id;
}

function normalizeName(name: string): string {
  return name
    .toLowerCase()
    .replace(/\b(jr|sr|iii|ii|iv)\b\.?/g, "")
    .replace(/[^a-z\s]/g, "")
    .trim()
    .replace(/\s+/g, " ");
}

/* ── Official Card ─────────────────────────────────────────────────── */
function OfficialCard({ official }: { official: GroupedOfficial }) {
  const partyColor = official.party ? PARTY_COLORS[official.party] || "#9ca3af" : "#9ca3af";
  const partyShort = official.party
    ?.replace(" Party", "")
    .replace("Democratic", "Democrat") || "";

  return (
    <div
      className="rounded-xl p-4 flex gap-4 items-start transition-all hover:shadow-md"
      style={{
        backgroundColor: "rgba(255,255,255,0.85)",
        border: "1px solid rgba(11,29,58,0.08)",
      }}
    >
      {/* Photo */}
      <div
        className="w-14 h-14 rounded-full flex-shrink-0 bg-gradient-to-br from-[#0B1D3A] to-[#1a3358] flex items-center justify-center overflow-hidden ring-2 ring-white shadow-md"
      >
        {official.photoUrl ? (
          <img
            src={official.photoUrl}
            alt={official.name}
            className="w-full h-full object-cover"
            loading="lazy"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = "none";
            }}
          />
        ) : (
          <svg viewBox="0 0 24 24" fill="none" stroke="#D4A843" strokeWidth="1" className="w-7 h-7 opacity-50">
            <circle cx="12" cy="8" r="4" />
            <path d="M20 21a8 8 0 10-16 0" />
          </svg>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className="font-bold text-[14px] text-[#0B1D3A] leading-tight">
            {official.name}
          </h3>
          {official.isDiaspora && (
            <span
              className="text-[10px] px-1.5 py-0.5 rounded-full font-semibold whitespace-nowrap"
              style={{ backgroundColor: "#FFF3E0", color: "#E65100", border: "1px solid #FFB74D" }}
            >
              🇮🇳 Indian Diaspora
            </span>
          )}
        </div>

        <p className="text-[12px] text-gray-600 mt-0.5">{official.office}</p>

        {/* Party */}
        <div className="flex items-center gap-1 mt-1">
          <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: partyColor }} />
          <span className="text-[11px] text-gray-400">{partyShort || "Unknown"}</span>
        </div>

        {/* Contact row */}
        <div className="flex flex-wrap items-center gap-3 mt-2">
          {official.phone && (
            <a href={`tel:${official.phone}`} className="text-[11px] text-[#0B1D3A] hover:text-[#D4A843] flex items-center gap-1 transition-colors" title="Call">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
                <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6A19.79 19.79 0 012.12 4.18 2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z" />
              </svg>
              {official.phone}
            </a>
          )}
          {official.website && (
            <a href={official.website} target="_blank" rel="noopener noreferrer" className="text-[11px] text-[#0B1D3A] hover:text-[#D4A843] flex items-center gap-1 transition-colors" title="Website">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
                <circle cx="12" cy="12" r="10" />
                <line x1="2" y1="12" x2="22" y2="12" />
                <path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" />
              </svg>
              Website
            </a>
          )}
          {official.twitter && (
            <a href={`https://twitter.com/${official.twitter}`} target="_blank" rel="noopener noreferrer" className="text-[11px] text-[#0B1D3A] hover:text-[#D4A843] flex items-center gap-1 transition-colors" title="X / Twitter">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
              @{official.twitter}
            </a>
          )}
          {official.facebook && (
            <a href={`https://facebook.com/${official.facebook}`} target="_blank" rel="noopener noreferrer" className="text-[11px] text-[#0B1D3A] hover:text-[#D4A843] flex items-center gap-1 transition-colors" title="Facebook">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
            </a>
          )}
          {official.email && (
            <a href={`mailto:${official.email}`} className="text-[11px] text-[#0B1D3A] hover:text-[#D4A843] flex items-center gap-1 transition-colors" title="Email">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
                <rect x="2" y="4" width="20" height="16" rx="2" />
                <path d="M22 7l-10 7L2 7" />
              </svg>
              Email
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

/* ── Level Section ─────────────────────────────────────────────────── */
function LevelSection({ group }: { group: OfficialGroup }) {
  if (group.officials.length === 0) return null;

  return (
    <div className="mb-8">
      <div className="flex items-center gap-2 mb-4 px-1">
        <span className="text-lg">{group.icon}</span>
        <h3 className="text-[16px] font-bold text-[#0B1D3A]">{group.label}</h3>
        <span className="text-[12px] text-gray-400 font-medium">
          ({group.officials.length})
        </span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {group.officials.map((official, i) => (
          <OfficialCard key={`${official.name}-${i}`} official={official} />
        ))}
      </div>
    </div>
  );
}

/* ── Main Page ─────────────────────────────────────────────────────── */
export default function KnowYourLeaderPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [groups, setGroups] = useState<OfficialGroup[] | null>(null);
  const [locationLabel, setLocationLabel] = useState<string | null>(null);
  const [diasporaNames, setDiasporaNames] = useState<Map<string, DiasporaLeader>>(new Map());
  const [geoLoading, setGeoLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  /* ── Load diaspora leaders for cross-reference ─────────────────── */
  useEffect(() => {
    sb.from("diaspora_leaders")
      .select("name,wikipedia_url")
      .then(({ data, error: err }: { data: unknown; error: unknown }) => {
        if (!err && Array.isArray(data)) {
          const map = new Map<string, DiasporaLeader>();
          for (const l of data as DiasporaLeader[]) {
            map.set(normalizeName(l.name), l);
          }
          setDiasporaNames(map);
        }
      });
  }, []);

  /* ── Geolocation auto-detect ───────────────────────────────────── */
  const detectLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser.");
      return;
    }
    setGeoLoading(true);
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          // Reverse geocode with Google
          const geocodeUrl = `https://maps.googleapis.com/maps/api/geocode/json?latlng=${latitude},${longitude}&key=${GOOGLE_API_KEY}`;
          const res = await fetch(geocodeUrl);
          const data = await res.json();
          if (data.results && data.results.length > 0) {
            const address = data.results[0].formatted_address;
            setQuery(address);
            // Auto-search with detected address
            fetchRepresentatives(address);
          } else {
            setError("Could not determine your address. Please enter your zip code manually.");
          }
        } catch {
          setError("Failed to detect location. Please enter your zip code manually.");
        } finally {
          setGeoLoading(false);
        }
      },
      () => {
        setGeoLoading(false);
        setError("Location access denied. Please enter your zip code or address.");
      },
      { enableHighAccuracy: false, timeout: 10000 }
    );
  }, []);

  /* ── Fetch representatives ─────────────────────────────────────── */
  const fetchRepresentatives = useCallback(
    async (address: string) => {
      if (!address.trim()) return;
      setLoading(true);
      setError(null);
      setGroups(null);
      setLocationLabel(null);

      try {
        const url = `https://www.googleapis.com/civicinfo/v2/representatives?address=${encodeURIComponent(address)}&key=${GOOGLE_API_KEY}`;
        const res = await fetch(url);
        if (!res.ok) {
          const body = await res.json().catch(() => null);
          if (res.status === 404 || (body?.error?.errors?.[0]?.reason === "parseError")) {
            setError("No results found for this address. Try a different zip code or full address.");
          } else if (res.status === 403) {
            setError("The Civic Information API is not yet enabled. The site admin needs to enable it in the Google Cloud Console.");
          } else {
            setError("Something went wrong. Please try again.");
          }
          setLoading(false);
          return;
        }

        const data = (await res.json()) as CivicResponse;

        // Build location label
        if (data.normalizedInput) {
          const ni = data.normalizedInput;
          setLocationLabel([ni.city, ni.state, ni.zip].filter(Boolean).join(", "));
        }

        // Process and group
        const groupMap: Record<string, GroupedOfficial[]> = {
          federal: [],
          state: [],
          county: [],
          city: [],
        };

        for (const office of data.offices) {
          const level = classifyOffice(office);
          for (const idx of office.officialIndices) {
            const official = data.officials[idx];
            if (!official) continue;

            const normalName = normalizeName(official.name);
            const diasporaMatch = diasporaNames.get(normalName);

            groupMap[level].push({
              name: official.name,
              office: office.name,
              party: official.party,
              photoUrl: official.photoUrl,
              phone: official.phones?.[0],
              website: official.urls?.[0],
              email: official.emails?.[0],
              twitter: getChannel(official, "Twitter"),
              facebook: getChannel(official, "Facebook"),
              isDiaspora: !!diasporaMatch,
              wikiUrl: diasporaMatch?.wikipedia_url || undefined,
            });
          }
        }

        const result: OfficialGroup[] = LEVEL_CONFIG.map((lc) => ({
          label: lc.label,
          icon: lc.icon,
          officials: groupMap[lc.key] || [],
        })).filter((g) => g.officials.length > 0);

        setGroups(result);
      } catch {
        setError("Failed to look up representatives. Please check your connection and try again.");
      } finally {
        setLoading(false);
      }
    },
    [diasporaNames]
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchRepresentatives(query);
  };

  const totalOfficials = groups?.reduce((sum, g) => sum + g.officials.length, 0) || 0;

  return (
    <>
      <Helmet>
        <title>Know Your Leader — Find Your Elected Officials | The Videshi</title>
        <meta
          name="description"
          content="Enter your zip code to find all your elected officials — from President to city council. Know who represents you at every level of government."
        />
      </Helmet>

      <Masthead />

      {/* ── Hero ────────────────────────────────────────────────────── */}
      <section
        style={{
          background: "linear-gradient(135deg, #0B1D3A 0%, #152a4a 50%, #0B1D3A 100%)",
          padding: "48px 16px 40px",
          textAlign: "center",
        }}
      >
        <h1
          className="font-bold tracking-tight"
          style={{ color: "#D4A843", fontSize: 32, marginBottom: 8 }}
        >
          Know Your Leader
        </h1>
        <p className="text-gray-300 text-[15px] max-w-lg mx-auto leading-relaxed mb-6">
          Find out who represents you — from the White House to your city council
        </p>

        {/* Search Form */}
        <form onSubmit={handleSubmit} className="max-w-md mx-auto">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter zip code or address"
                className="w-full px-4 py-3 rounded-lg text-[14px] bg-white text-[#0B1D3A] placeholder-gray-400 border-2 border-transparent focus:border-[#D4A843] focus:outline-none transition-colors"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-5 py-3 rounded-lg font-bold text-[14px] text-[#0B1D3A] transition-all disabled:opacity-50"
              style={{ backgroundColor: "#D4A843" }}
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-[#0B1D3A] border-t-transparent rounded-full animate-spin" />
              ) : (
                "Search"
              )}
            </button>
          </div>

          {/* Location detect button */}
          <button
            type="button"
            onClick={detectLocation}
            disabled={geoLoading}
            className="mt-3 text-[12px] text-gray-400 hover:text-[#D4A843] transition-colors flex items-center gap-1 mx-auto"
          >
            {geoLoading ? (
              <>
                <div className="w-3 h-3 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                Detecting...
              </>
            ) : (
              <>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
                  <circle cx="12" cy="12" r="3" />
                  <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
                </svg>
                Use my current location
              </>
            )}
          </button>
        </form>
      </section>

      {/* ── Results ─────────────────────────────────────────────────── */}
      <section
        style={{
          maxWidth: 720,
          margin: "0 auto",
          padding: "24px 16px 60px",
        }}
      >
        {/* Error */}
        {error && (
          <div
            className="rounded-lg p-4 mb-6 text-[13px] text-center"
            style={{ backgroundColor: "#FFF3E0", color: "#E65100", border: "1px solid #FFB74D" }}
          >
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <div className="w-8 h-8 border-3 border-[#D4A843] border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-400 text-[13px]">Looking up your representatives…</p>
          </div>
        )}

        {/* Results header */}
        {groups && !loading && (
          <>
            {locationLabel && (
              <div className="text-center mb-6">
                <p className="text-[13px] text-gray-500">
                  Representatives for{" "}
                  <span className="font-bold text-[#0B1D3A]">{locationLabel}</span>
                </p>
                <p className="text-[12px] text-gray-400 mt-1">
                  {totalOfficials} elected officials found
                </p>
              </div>
            )}

            {groups.map((group) => (
              <LevelSection key={group.label} group={group} />
            ))}

            {totalOfficials === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500 text-[14px]">
                  No representatives found for this address.
                </p>
                <p className="text-gray-400 text-[12px] mt-1">
                  Try entering a full US address with zip code.
                </p>
              </div>
            )}

            {/* Attribution */}
            <p className="text-center text-[11px] text-gray-300 mt-8">
              Data provided by Google Civic Information API
            </p>

            {/* Cross-link to Leaders */}
            <div className="mt-6 text-center">
              <a
                href="/representatives"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-[13px] font-semibold text-white transition-all hover:opacity-90"
                style={{ backgroundColor: "#0B1D3A" }}
              >
                🇮🇳 Explore Leaders of the Indian Diaspora →
              </a>
            </div>
          </>
        )}

        {/* Empty state (no search yet) */}
        {!groups && !loading && !error && (
          <div className="text-center py-16">
            <div className="text-5xl mb-4">🗳️</div>
            <h2 className="text-[18px] font-bold text-[#0B1D3A] mb-2">
              Who represents you?
            </h2>
            <p className="text-[13px] text-gray-500 max-w-sm mx-auto leading-relaxed">
              Enter your zip code or address above to find all your elected officials
              — federal, state, county, and city level.
            </p>
            <div className="flex flex-wrap justify-center gap-3 mt-6">
              {[
                { icon: "🏛️", label: "US Congress" },
                { icon: "🏗️", label: "State Legislature" },
                { icon: "🏙️", label: "City Council" },
                { icon: "📋", label: "County Officials" },
              ].map((item) => (
                <div
                  key={item.label}
                  className="px-3 py-2 rounded-lg text-[11px] text-gray-500 font-medium"
                  style={{ backgroundColor: "rgba(11,29,58,0.04)" }}
                >
                  <span className="mr-1">{item.icon}</span>
                  {item.label}
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      <SiteFooter />
    </>
  );
}
