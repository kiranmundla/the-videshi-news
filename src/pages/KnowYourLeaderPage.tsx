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
interface Legislator {
  name: string;
  type: "sen" | "rep";
  state: string;
  party: string;
  phone: string;
  url: string;
  contact_form: string;
  address: string;
  photoUrl: string;
  bioguide: string;
  district?: number;
  state_rank?: string;
}

interface GovernorEntry {
  name: string;
  party: string;
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
  contactForm?: string;
}

interface OfficialGroup {
  label: string;
  icon: string;
  officials: GroupedOfficial[];
}

/* ── constants ─────────────────────────────────────────────────────── */
const GOOGLE_API_KEY = import.meta.env.VITE_GOOGLE_API_KEY || "";

const PARTY_COLORS: Record<string, string> = {
  Democrat: "#3b82f6",
  Democratic: "#3b82f6",
  Republican: "#ef4444",
  Libertarian: "#f59e0b",
  Green: "#22c55e",
  Independent: "#8b5cf6",
};

const FIPS_TO_STATE: Record<string, string> = {
  "01":"AL","02":"AK","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT",
  "10":"DE","11":"DC","12":"FL","13":"GA","15":"HI","16":"ID","17":"IL",
  "18":"IN","19":"IA","20":"KS","21":"KY","22":"LA","23":"ME","24":"MD",
  "25":"MA","26":"MI","27":"MN","28":"MS","29":"MO","30":"MT","31":"NE",
  "32":"NV","33":"NH","34":"NJ","35":"NM","36":"NY","37":"NC","38":"ND",
  "39":"OH","40":"OK","41":"OR","42":"PA","44":"RI","45":"SC","46":"SD",
  "47":"TN","48":"TX","49":"UT","50":"VT","51":"VA","53":"WA","54":"WV",
  "55":"WI","56":"WY",
};

const STATE_NAMES: Record<string, string> = {
  AL:"Alabama",AK:"Alaska",AZ:"Arizona",AR:"Arkansas",CA:"California",
  CO:"Colorado",CT:"Connecticut",DE:"Delaware",DC:"District of Columbia",
  FL:"Florida",GA:"Georgia",HI:"Hawaii",ID:"Idaho",IL:"Illinois",IN:"Indiana",
  IA:"Iowa",KS:"Kansas",KY:"Kentucky",LA:"Louisiana",ME:"Maine",MD:"Maryland",
  MA:"Massachusetts",MI:"Michigan",MN:"Minnesota",MS:"Mississippi",MO:"Missouri",
  MT:"Montana",NE:"Nebraska",NV:"Nevada",NH:"New Hampshire",NJ:"New Jersey",
  NM:"New Mexico",NY:"New York",NC:"North Carolina",ND:"North Dakota",OH:"Ohio",
  OK:"Oklahoma",OR:"Oregon",PA:"Pennsylvania",RI:"Rhode Island",SC:"South Carolina",
  SD:"South Dakota",TN:"Tennessee",TX:"Texas",UT:"Utah",VT:"Vermont",VA:"Virginia",
  WA:"Washington",WV:"West Virginia",WI:"Wisconsin",WY:"Wyoming",
};

/* ── helpers ────────────────────────────────────────────────────────── */
function normalizeName(name: string): string {
  return name
    .toLowerCase()
    .replace(/\b(jr|sr|iii|ii|iv)\b\.?/g, "")
    .replace(/[^a-z\s]/g, "")
    .trim()
    .replace(/\s+/g, " ");
}

function partyColor(party?: string): string {
  if (!party) return "#9ca3af";
  for (const [key, color] of Object.entries(PARTY_COLORS)) {
    if (party.includes(key)) return color;
  }
  return "#9ca3af";
}

function shortParty(party?: string): string {
  if (!party) return "Unknown";
  if (party.includes("Democrat")) return "Democrat";
  if (party.includes("Republican")) return "Republican";
  if (party.includes("Independent")) return "Independent";
  return party;
}

/* ── Official Card ─────────────────────────────────────────────────── */
function OfficialCard({ official }: { official: GroupedOfficial }) {
  return (
    <div
      className="rounded-xl p-4 flex gap-4 items-start transition-all hover:shadow-md"
      style={{
        backgroundColor: "rgba(255,255,255,0.85)",
        border: "1px solid rgba(11,29,58,0.08)",
      }}
    >
      {/* Photo */}
      <div className="w-14 h-14 rounded-full flex-shrink-0 bg-gradient-to-br from-[#0B1D3A] to-[#1a3358] flex items-center justify-center overflow-hidden ring-2 ring-white shadow-md">
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
          <span
            className="w-2 h-2 rounded-full inline-block"
            style={{ backgroundColor: partyColor(official.party) }}
          />
          <span className="text-[11px] text-gray-400">{shortParty(official.party)}</span>
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
          {official.contactForm && (
            <a href={official.contactForm} target="_blank" rel="noopener noreferrer" className="text-[11px] text-[#0B1D3A] hover:text-[#D4A843] flex items-center gap-1 transition-colors" title="Contact Form">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
                <rect x="2" y="4" width="20" height="16" rx="2" />
                <path d="M22 7l-10 7L2 7" />
              </svg>
              Contact
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
  const [legislators, setLegislators] = useState<Legislator[]>([]);
  const [governors, setGovernors] = useState<Record<string, GovernorEntry>>({});
  const inputRef = useRef<HTMLInputElement>(null);

  /* ── Load static data on mount ─────────────────────────────────── */
  useEffect(() => {
    fetch("/data/legislators.json")
      .then((r) => r.json())
      .then((data: Legislator[]) => setLegislators(data))
      .catch(() => {});
    fetch("/data/governors.json")
      .then((r) => r.json())
      .then((data: Record<string, GovernorEntry>) => setGovernors(data))
      .catch(() => {});
  }, []);

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

  /* ── Check diaspora match ──────────────────────────────────────── */
  const isDiaspora = useCallback(
    (name: string): { match: boolean; wikiUrl?: string } => {
      const norm = normalizeName(name);
      const leader = diasporaNames.get(norm);
      if (leader) return { match: true, wikiUrl: leader.wikipedia_url || undefined };
      // Try partial match (last name)
      const parts = norm.split(" ");
      if (parts.length >= 2) {
        const lastName = parts[parts.length - 1];
        for (const [key, val] of diasporaNames.entries()) {
          if (key.endsWith(lastName) && key.includes(parts[0])) {
            return { match: true, wikiUrl: val.wikipedia_url || undefined };
          }
        }
      }
      return { match: false };
    },
    [diasporaNames]
  );

  /* ── Geocode address → lat/lng + state ─────────────────────────── */
  const geocodeAddress = async (
    address: string
  ): Promise<{ lat: number; lng: number; state: string; formattedAddress: string } | null> => {
    const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(
      address
    )}&key=${GOOGLE_API_KEY}&components=country:US`;
    const res = await fetch(url);
    const data = await res.json();
    if (!data.results || data.results.length === 0) return null;

    const result = data.results[0];
    const loc = result.geometry.location;
    let state = "";

    for (const comp of result.address_components || []) {
      if (comp.types.includes("administrative_area_level_1")) {
        state = comp.short_name;
      }
    }

    return {
      lat: loc.lat,
      lng: loc.lng,
      state,
      formattedAddress: result.formatted_address,
    };
  };

  /* ── Census Bureau: lat/lng → congressional district ───────────── */
  const getCongressionalDistrict = async (
    lat: number,
    lng: number
  ): Promise<number | null> => {
    try {
      const url = `https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x=${lng}&y=${lat}&benchmark=Public_AR_Current&vintage=Current_Current&format=json`;
      const res = await fetch(url);
      const data = await res.json();
      const matches = data?.result?.geographies?.["119th Congressional Districts"];
      if (matches && matches.length > 0) {
        const cdName = matches[0].BASENAME || matches[0].NAME || "";
        // Parse district number: "Congressional District 17" → 17
        const match = cdName.match(/(\d+)/);
        if (match) return parseInt(match[1], 10);
        // At-large districts
        if (cdName.toLowerCase().includes("at large") || cdName.toLowerCase().includes("at-large")) {
          return 0;
        }
        // Delegate districts (DC, territories)
        if (cdName.toLowerCase().includes("delegate")) return 0;
      }
      // Fallback: try the text directly from CD field
      const cd = matches?.[0]?.CD || matches?.[0]?.GEOID?.slice(-2);
      if (cd) {
        const num = parseInt(cd, 10);
        if (!isNaN(num)) return num === 0 ? 0 : num;
      }
      return null;
    } catch {
      return null;
    }
  };

  /* ── Build official results ────────────────────────────────────── */
  const buildResults = useCallback(
    (state: string, district: number | null): OfficialGroup[] => {
      const federal: GroupedOfficial[] = [];
      const stateLevel: GroupedOfficial[] = [];

      // President & VP (static)
      const president = { name: "Donald J. Trump", party: "Republican" };
      const vp = { name: "JD Vance", party: "Republican" };
      const presCheck = isDiaspora(president.name);
      const vpCheck = isDiaspora(vp.name);

      federal.push({
        name: president.name,
        office: "President of the United States",
        party: president.party,
        photoUrl: "https://www.whitehouse.gov/wp-content/uploads/2025/01/P20250120AS-0839-1536x1024.jpg",
        phone: "202-456-1111",
        website: "https://www.whitehouse.gov",
        isDiaspora: presCheck.match,
        wikiUrl: presCheck.wikiUrl,
      });

      federal.push({
        name: vp.name,
        office: "Vice President of the United States",
        party: vp.party,
        photoUrl: "https://www.whitehouse.gov/wp-content/uploads/2025/01/P20250120AS-1028-1536x1024.jpg",
        phone: "202-456-1111",
        website: "https://www.whitehouse.gov",
        isDiaspora: vpCheck.match,
        wikiUrl: vpCheck.wikiUrl,
      });

      // US Senators for this state
      const senators = legislators.filter(
        (l) => l.type === "sen" && l.state === state
      );
      for (const s of senators) {
        const check = isDiaspora(s.name);
        federal.push({
          name: s.name,
          office: `U.S. Senator (${STATE_NAMES[state] || state})`,
          party: s.party,
          photoUrl: s.photoUrl,
          phone: s.phone || undefined,
          website: s.url || undefined,
          contactForm: s.contact_form || undefined,
          isDiaspora: check.match,
          wikiUrl: check.wikiUrl,
        });
      }

      // US House Representative for this district
      if (district !== null) {
        const reps = legislators.filter(
          (l) =>
            l.type === "rep" &&
            l.state === state &&
            l.district === district
        );
        for (const r of reps) {
          const check = isDiaspora(r.name);
          const distLabel =
            r.district === 0
              ? "At-Large"
              : `District ${r.district}`;
          federal.push({
            name: r.name,
            office: `U.S. Representative (${state}-${distLabel})`,
            party: r.party,
            photoUrl: r.photoUrl,
            phone: r.phone || undefined,
            website: r.url || undefined,
            contactForm: r.contact_form || undefined,
            isDiaspora: check.match,
            wikiUrl: check.wikiUrl,
          });
        }
      }

      // Governor
      const gov = governors[state];
      if (gov) {
        const check = isDiaspora(gov.name);
        stateLevel.push({
          name: gov.name,
          office: `Governor of ${STATE_NAMES[state] || state}`,
          party: gov.party,
          isDiaspora: check.match,
          wikiUrl: check.wikiUrl,
        });
      }

      const result: OfficialGroup[] = [];
      if (federal.length > 0) {
        result.push({ label: "Federal", icon: "🏛️", officials: federal });
      }
      if (stateLevel.length > 0) {
        result.push({ label: "State", icon: "🏗️", officials: stateLevel });
      }

      return result;
    },
    [legislators, governors, isDiaspora]
  );

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
          const geocodeUrl = `https://maps.googleapis.com/maps/api/geocode/json?latlng=${latitude},${longitude}&key=${GOOGLE_API_KEY}`;
          const res = await fetch(geocodeUrl);
          const data = await res.json();
          if (data.results && data.results.length > 0) {
            const address = data.results[0].formatted_address;
            setQuery(address);
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* ── Fetch representatives (main flow) ─────────────────────────── */
  const fetchRepresentatives = useCallback(
    async (address: string) => {
      if (!address.trim()) return;
      setLoading(true);
      setError(null);
      setGroups(null);
      setLocationLabel(null);

      try {
        // Step 1: Geocode address → lat/lng + state
        const geo = await geocodeAddress(address);
        if (!geo || !geo.state) {
          setError(
            "Could not find this address. Please enter a valid US zip code or street address."
          );
          setLoading(false);
          return;
        }

        setLocationLabel(geo.formattedAddress);

        // Step 2: Get congressional district from Census Bureau
        const district = await getCongressionalDistrict(geo.lat, geo.lng);

        // Step 3: Build results from bundled data
        const results = buildResults(geo.state, district);

        if (results.length === 0) {
          setError("No representatives found for this address.");
        } else {
          // Add note if district lookup failed
          if (district === null) {
            // Still show senators + governor, just note the house rep is missing
            setError(
              "We found your Senators and Governor, but couldn't identify your exact Congressional district. Try entering a full street address for your House Representative."
            );
          }
          setGroups(results);
        }
      } catch {
        setError("Something went wrong. Please try again.");
      } finally {
        setLoading(false);
      }
    },
    [buildResults]
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchRepresentatives(query);
  };

  const totalOfficials =
    groups?.reduce((sum, g) => sum + g.officials.length, 0) || 0;

  return (
    <>
      <Helmet>
        <title>
          Know Your Leader — Find Your Elected Officials | The Videshi
        </title>
        <meta
          name="description"
          content="Enter your zip code to find all your elected officials — from President to Governor. Know who represents you at every level of government."
        />
      </Helmet>

      <Masthead />

      {/* ── Hero ────────────────────────────────────────────────────── */}
      <section
        style={{
          background:
            "linear-gradient(135deg, #0B1D3A 0%, #152a4a 50%, #0B1D3A 100%)",
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
          Find out who represents you — from the White House to your state
          capitol
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
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  className="w-3.5 h-3.5"
                >
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
            style={{
              backgroundColor: "#FFF3E0",
              color: "#E65100",
              border: "1px solid #FFB74D",
            }}
          >
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <div className="w-8 h-8 border-3 border-[#D4A843] border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-400 text-[13px]">
              Looking up your representatives…
            </p>
          </div>
        )}

        {/* Results */}
        {groups && !loading && (
          <>
            {locationLabel && (
              <div className="text-center mb-6">
                <p className="text-[13px] text-gray-500">
                  Representatives for{" "}
                  <span className="font-bold text-[#0B1D3A]">
                    {locationLabel}
                  </span>
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
              Congress data from unitedstates project · District data from U.S.
              Census Bureau
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
              Enter your zip code or address above to find your elected officials
              — President, Senators, House Representative, and Governor.
            </p>
            <div className="flex flex-wrap justify-center gap-3 mt-6">
              {[
                { icon: "🏛️", label: "President & VP" },
                { icon: "🏛️", label: "US Senators" },
                { icon: "🏛️", label: "House Representative" },
                { icon: "🏗️", label: "Governor" },
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
