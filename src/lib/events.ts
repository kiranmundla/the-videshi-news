import { supabase as supabaseTyped } from "@/integrations/supabase/client";

const supabase = supabaseTyped as unknown as {
  from: (table: string) => any;
};

export type EventItem = {
  id: string;
  title: string;
  date: string;
  time: string | null;
  end_date: string | null;
  venue_name: string | null;
  city: string;
  state: string | null;
  category: string | null;
  description: string | null;
  long_description: string | null;
  artist_info: string | null;
  venue_info: string | null;
  slug: string | null;
  image_url: string | null;
  ticket_url: string | null;
  source: string | null;
  price_range: string | null;
  organizer: string | null;
  audience: string | null;
  latitude: number | null;
  longitude: number | null;
  is_featured: boolean | null;
  venue_images: string[] | null;
  seatmap_url: string | null;
  street_address: string | null;
  zip_code: string | null;
  created_at?: string | null;
};

// Base columns that always exist
const BASE_COLS = "id,title,date,time,end_date,venue_name,city,state,category,description,image_url,ticket_url,source,price_range,organizer,audience,created_at";

// Extended columns (added by migration-event-detail.sql)
// If the migration hasn't been run yet, we fall back to BASE_COLS
const EVENT_COLS = BASE_COLS + ",long_description,artist_info,venue_info,slug,latitude,longitude,is_featured,venue_images,seatmap_url,street_address,zip_code";

/**
 * Run a query with EVENT_COLS; if it fails (columns don't exist yet),
 * retry with BASE_COLS only.
 */
async function queryWithFallback(buildQuery: (cols: string) => any): Promise<any[]> {
  const { data, error } = await buildQuery(EVENT_COLS);
  if (error && error.code === "42703") {
    // Column doesn't exist — fall back to base columns
    const { data: fallback, error: fallbackError } = await buildQuery(BASE_COLS);
    if (fallbackError) {
      console.error("Failed to fetch events:", fallbackError);
      return [];
    }
    return (fallback || []).map((e: any) => ({
      ...e,
      long_description: null,
      artist_info: null,
      venue_info: null,
      slug: null,
      latitude: null,
      longitude: null,
      is_featured: null,
      street_address: null,
      zip_code: null,
    }));
  }
  if (error) {
    console.error("Failed to fetch events:", error);
    return [];
  }
  return data || [];
}

/* ------------------------------------------------------------------ */
/* Static JSON cache                                                  */
/* ------------------------------------------------------------------ */

let _eventsCache: EventItem[] | null = null;
let _eventsCacheTime = 0;
const EVENTS_CACHE_TTL = 5 * 60 * 1000; // 5 min

async function loadEventsCache(): Promise<EventItem[] | null> {
  if (_eventsCache && Date.now() - _eventsCacheTime < EVENTS_CACHE_TTL) return _eventsCache;
  try {
    const res = await fetch("/data/events.json");
    if (!res.ok) return null;
    _eventsCache = (await res.json()) as EventItem[];
    _eventsCacheTime = Date.now();
    return _eventsCache;
  } catch {
    return null;
  }
}

/**
 * Generate a deterministic slug from title + date.
 * Used both for URL generation and lookup matching.
 */
export function generateSlug(title?: string, date?: string): string {
  // Fallback only — prefer event.id or event.slug when available
  if (!title) return crypto.randomUUID();
  const base = title
    .toLowerCase()
    .replace(/['']/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60)
    .replace(/-+$/, "");
  const datePart = date ? `-${date}` : "";
  return `${base}${datePart}`;
}

/**
 * City groups for the city picker. Each group maps a display label
 * to one or more city values that match the DB `city` column.
 */
export const CITY_GROUPS: { label: string; cities: string[] }[] = [
  { label: "Bay Area",      cities: ["San Francisco", "San Jose", "Oakland", "Fremont", "Sunnyvale", "Santa Clara", "Milpitas", "Pleasanton", "Union City", "Dublin", "Livermore", "Cupertino", "Mountain View", "Palo Alto", "Redwood City", "Berkeley", "Hayward", "San Mateo", "Daly City", "South San Francisco", "Los Gatos", "San Ramon", "Calabasas"] },
  { label: "NYC / NJ",      cities: ["New York", "Brooklyn", "Queens", "Edison", "Jersey City", "Newark", "Hoboken", "Parsippany", "Iselin", "Hicksville", "Garwood", "Mahwah", "New Brunswick", "South Brunswick Township", "Woodbridge Township", "Uniondale", "Atlantic City", "Robbinsville", "Flushing"] },
  { label: "Dallas",        cities: ["Dallas", "Plano", "Irving", "Frisco", "Richardson", "Garland", "Arlington", "Allen", "Carrollton", "Grand Prairie", "Cedar Park"] },
  { label: "Houston",       cities: ["Houston", "Sugar Land", "Katy", "Stafford", "Pearland"] },
  { label: "Chicago",       cities: ["Chicago", "Schaumburg", "Naperville", "Aurora", "Skokie", "Hoffman Estates", "Arlington Heights", "Willowbrook", "Oak Park", "Bartlett", "Lemont"] },
  { label: "Los Angeles",   cities: ["Los Angeles", "Culver City", "Santa Monica", "Anaheim", "Irvine", "Pasadena", "Hermosa Beach", "Cerritos", "Torrance", "Playa del Rey", "Marina del Rey", "Downey", "Long Beach", "Glendale", "El Segundo", "Chino Hills", "Calabasas"] },
  { label: "Seattle",       cities: ["Seattle", "Bellevue", "Redmond", "Kirkland", "Bothell", "Everett", "Renton", "Federal Way", "SeaTac"] },
  { label: "Atlanta",       cities: ["Atlanta", "Alpharetta", "Duluth", "Norcross", "Decatur", "Johns Creek", "Riverdale", "Lilburn"] },
  { label: "DC",            cities: ["Washington", "Fairfax", "Rockville", "Bethesda", "Tysons", "Herndon", "Vienna", "Lanham", "Chantilly", "Sterling"] },
  { label: "Detroit",       cities: ["Detroit", "Troy", "Novi", "Farmington Hills", "Canton", "Ann Arbor"] },
  { label: "Charlotte",     cities: ["Charlotte", "Greensboro", "Raleigh", "Durham"] },
  { label: "Pittsburgh",    cities: ["Pittsburgh", "Penn Hills"] },
  { label: "Philadelphia",  cities: ["Philadelphia", "King of Prussia", "Cherry Hill", "Oaks", "Bethlehem"] },
  { label: "Nashville",     cities: ["Nashville"] },
  { label: "Boston",        cities: ["Boston", "Cambridge", "Ashland", "Westborough"] },
  { label: "Phoenix",       cities: ["Phoenix", "Scottsdale", "Chandler", "Tempe", "Mesa"] },
  { label: "Denver",        cities: ["Denver"] },
  { label: "Columbus",      cities: ["Columbus", "Lewis Center"] },
  { label: "Baltimore",     cities: ["Baltimore"] },
  { label: "Florida",       cities: ["Hollywood", "Miami", "Tampa", "Orlando", "Jacksonville", "Fort Lauderdale"] },
];

/* ------------------------------------------------------------------ */
/* Time range helpers                                                 */
/* ------------------------------------------------------------------ */

export type TimeRange = "weekend" | "this_month" | "next_month" | null;

function getWeekendRange(): { from: string; to: string } {
  const now = new Date();
  const day = now.getDay(); // 0=Sun, 6=Sat
  // Find this Saturday
  const satOffset = day === 0 ? -1 : 6 - day; // if Sun, last Sat; else next Sat
  const sat = new Date(now);
  sat.setDate(now.getDate() + satOffset);
  // If it's already past Sunday, show next weekend
  if (day === 0 && now.getHours() >= 22) {
    sat.setDate(sat.getDate() + 7);
  }
  // If we're past the weekend entirely (Mon-Fri), show upcoming
  const sun = new Date(sat);
  sun.setDate(sat.getDate() + 1);

  // Make sure the range starts today at earliest
  const today = new Date();
  const from = sat < today ? today.toISOString().slice(0, 10) : sat.toISOString().slice(0, 10);

  return {
    from,
    to: sun.toISOString().slice(0, 10),
  };
}

function getThisMonthRange(): { from: string; to: string } {
  const now = new Date();
  const from = now.toISOString().slice(0, 10);
  const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
  return { from, to: lastDay.toISOString().slice(0, 10) };
}

function getNextMonthRange(): { from: string; to: string } {
  const now = new Date();
  const firstDay = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  const lastDay = new Date(now.getFullYear(), now.getMonth() + 2, 0);
  return {
    from: firstDay.toISOString().slice(0, 10),
    to: lastDay.toISOString().slice(0, 10),
  };
}

export function getDateRange(timeRange: TimeRange): { from: string; to: string } | null {
  switch (timeRange) {
    case "weekend": return getWeekendRange();
    case "this_month": return getThisMonthRange();
    case "next_month": return getNextMonthRange();
    default: return null;
  }
}

/* ------------------------------------------------------------------ */
/* Featured events                                                    */
/* ------------------------------------------------------------------ */

export async function getFeaturedEvents(): Promise<EventItem[]> {
  const today = new Date().toISOString().slice(0, 10);

  // Try static JSON first
  const cached = await loadEventsCache();
  if (cached) {
    return cached
      .filter((e) => e.is_featured && e.date >= today)
      .slice(0, 8);
  }

  // Fallback: Supabase
  const data = await queryWithFallback((cols: string) => {
    return supabase
      .from("events")
      .select(cols)
      .eq("is_featured", true)
      .gte("date", today)
      .order("date", { ascending: true })
      .limit(8);
  });

  return data as EventItem[];
}

/* ------------------------------------------------------------------ */
/* Data fetching                                                      */
/* ------------------------------------------------------------------ */

export async function getEvents(
  cityFilter: string | null = null,
  categoryFilter: string | null = null,
  limit = 50,
  offset = 0,
  timeRange: TimeRange = null,
): Promise<EventItem[]> {
  const dateRange = getDateRange(timeRange);
  const today = new Date().toISOString().slice(0, 10);

  // Try static JSON first
  const cached = await loadEventsCache();
  if (cached) {
    let filtered = cached.filter((e) => e.date >= (dateRange ? dateRange.from : today));
    if (dateRange) {
      filtered = filtered.filter((e) => e.date <= dateRange.to);
    }
    if (cityFilter) {
      const group = CITY_GROUPS.find((g) => g.label === cityFilter);
      if (group) {
        const cities = new Set([...group.cities, group.label]);
        filtered = filtered.filter((e) => cities.has(e.city));
      }
    }
    if (categoryFilter) {
      filtered = filtered.filter((e) => e.category === categoryFilter);
    }
    return filtered.slice(offset, offset + limit);
  }

  // Fallback: Supabase
  const data = await queryWithFallback((cols: string) => {
    let query = supabase
      .from("events")
      .select(cols)
      .gte("date", dateRange ? dateRange.from : today)
      .order("date", { ascending: true })
      .range(offset, offset + limit - 1);

    if (dateRange) {
      query = query.lte("date", dateRange.to);
    }

    if (cityFilter) {
      const group = CITY_GROUPS.find((g) => g.label === cityFilter);
      if (group) {
        query = query.in("city", [...group.cities, group.label]);
      }
    }

    if (categoryFilter) {
      query = query.eq("category", categoryFilter);
    }

    return query;
  });

  return data as EventItem[];
}

/**
 * Fetch a single event by slug.
 * Tries DB slug column first, then falls back to computing slug from title+date.
 */
export async function getEventBySlug(slug: string): Promise<EventItem | null> {
  // Try static JSON first
  const cached = await loadEventsCache();
  if (cached) {
    // Direct slug match
    const direct = cached.find((e) => e.slug === slug);
    if (direct) return direct;
    // ID match (events linked by id instead of slug)
    const byId = cached.find((e) => e.id === slug);
    if (byId) return byId;
  }

  // Supabase — try direct slug lookup first
  const { data: directMatch } = await supabase
    .from("events")
    .select(EVENT_COLS)
    .eq("slug", slug)
    .limit(1);

  if (directMatch && directMatch.length > 0) {
    return directMatch[0] as EventItem;
  }

  // Try by id
  const { data: idMatch } = await supabase
    .from("events")
    .select(EVENT_COLS)
    .eq("id", slug)
    .limit(1);

  if (idMatch && idMatch.length > 0) {
    return idMatch[0] as EventItem;
  }

  return null;
}

/**
 * Fetch event counts per city group (for city pill badges).
 * Returns a map of city label → count.
 */
export async function getCityCounts(): Promise<Record<string, number>> {
  const today = new Date().toISOString().slice(0, 10);

  // Try static JSON first
  const cached = await loadEventsCache();
  if (cached) {
    const upcoming = cached.filter((e) => e.date >= today);
    const counts: Record<string, number> = {};
    for (const group of CITY_GROUPS) {
      counts[group.label] = 0;
    }
    for (const row of upcoming) {
      for (const group of CITY_GROUPS) {
        if (group.cities.includes(row.city)) {
          counts[group.label] = (counts[group.label] || 0) + 1;
          break;
        }
      }
    }
    return counts;
  }

  // Fallback: Supabase
  const { data, error } = await supabase
    .from("events")
    .select("city")
    .gte("date", today);

  if (error || !data) return {};

  const counts: Record<string, number> = {};
  for (const group of CITY_GROUPS) {
    counts[group.label] = 0;
  }

  for (const row of data as { city: string }[]) {
    for (const group of CITY_GROUPS) {
      if (group.cities.includes(row.city)) {
        counts[group.label] = (counts[group.label] || 0) + 1;
        break;
      }
    }
  }

  return counts;
}

/* ------------------------------------------------------------------ */
/* Geolocation / distance helpers                                     */
/* ------------------------------------------------------------------ */

/** Haversine distance in miles between two lat/lng points */
export function getDistanceMiles(
  lat1: number, lng1: number,
  lat2: number, lng2: number,
): number {
  const R = 3958.8; // Earth radius in miles
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

/** Format distance for display */
export function formatDistance(miles: number): string {
  if (miles < 1) return "< 1 mi";
  if (miles < 10) return `${miles.toFixed(1)} mi`;
  return `${Math.round(miles)} mi`;
}

/**
 * City → approximate lat/lng lookup.
 * Used for client-side distance sorting when "Near Me" is active.
 * Accuracy is within a few miles — good enough for metro-area sorting.
 */
export const CITY_COORDS: Record<string, { lat: number; lng: number }> = {
  // California — Bay Area
  "San Francisco": { lat: 37.7749, lng: -122.4194 },
  "San Jose":      { lat: 37.3382, lng: -121.8863 },
  "Oakland":       { lat: 37.8044, lng: -122.2712 },
  "Fremont":       { lat: 37.5485, lng: -121.9886 },
  "Sunnyvale":     { lat: 37.3688, lng: -122.0363 },
  "Santa Clara":   { lat: 37.3541, lng: -121.9552 },
  "Milpitas":      { lat: 37.4323, lng: -121.8996 },
  "Pleasanton":    { lat: 37.6624, lng: -121.8747 },
  "Union City":    { lat: 37.5934, lng: -122.0438 },
  "Dublin":        { lat: 37.7021, lng: -121.9358 },
  "Livermore":     { lat: 37.6819, lng: -121.7680 },
  "Cupertino":     { lat: 37.3230, lng: -122.0322 },
  "Mountain View": { lat: 37.3861, lng: -122.0839 },
  "Palo Alto":     { lat: 37.4419, lng: -122.1430 },
  "Redwood City":  { lat: 37.4852, lng: -122.2364 },
  "Berkeley":      { lat: 37.8716, lng: -122.2727 },
  "Hayward":       { lat: 37.6688, lng: -122.0808 },
  "San Mateo":     { lat: 37.5630, lng: -122.3255 },
  "Daly City":     { lat: 37.6879, lng: -122.4702 },
  "South San Francisco": { lat: 37.6547, lng: -122.4077 },
  "Los Gatos":     { lat: 37.2358, lng: -121.9624 },
  // California — Los Angeles
  "Los Angeles":   { lat: 34.0522, lng: -118.2437 },
  "Culver City":   { lat: 34.0211, lng: -118.3965 },
  "Santa Monica":  { lat: 34.0195, lng: -118.4912 },
  "Anaheim":       { lat: 33.8366, lng: -117.9143 },
  "Irvine":        { lat: 33.6846, lng: -117.8265 },
  "Pasadena":      { lat: 34.1478, lng: -118.1445 },
  "Hermosa Beach": { lat: 33.8622, lng: -118.3995 },
  "Cerritos":      { lat: 33.8583, lng: -118.0648 },
  "Torrance":      { lat: 33.8358, lng: -118.3406 },
  "Playa del Rey": { lat: 33.9575, lng: -118.4420 },
  "Marina del Rey": { lat: 33.9802, lng: -118.4517 },
  "Downey":        { lat: 33.9401, lng: -118.1332 },
  "Long Beach":    { lat: 33.7701, lng: -118.1937 },
  "Glendale":      { lat: 34.1425, lng: -118.2551 },
  "El Segundo":    { lat: 33.9192, lng: -118.4165 },
  // New York / New Jersey
  "New York":      { lat: 40.7128, lng: -74.0060 },
  "Brooklyn":      { lat: 40.6782, lng: -73.9442 },
  "Queens":        { lat: 40.7282, lng: -73.7949 },
  "Edison":        { lat: 40.5187, lng: -74.4121 },
  "Jersey City":   { lat: 40.7178, lng: -74.0431 },
  "Newark":        { lat: 40.7357, lng: -74.1724 },
  "Hoboken":       { lat: 40.7440, lng: -74.0324 },
  "Parsippany":    { lat: 40.8579, lng: -74.4260 },
  "Iselin":        { lat: 40.5715, lng: -74.3224 },
  "Hicksville":    { lat: 40.7682, lng: -73.5251 },
  "Garwood":       { lat: 40.6518, lng: -74.3226 },
  "Mahwah":        { lat: 41.0887, lng: -74.1438 },
  "New Brunswick": { lat: 40.4862, lng: -74.4518 },
  "South Brunswick Township": { lat: 40.3840, lng: -74.5322 },
  "Woodbridge Township":      { lat: 40.5576, lng: -74.2846 },
  "Uniondale":     { lat: 40.7001, lng: -73.5929 },
  "Atlantic City": { lat: 39.3643, lng: -74.4229 },
  // Texas — Dallas
  "Dallas":        { lat: 32.7767, lng: -96.7970 },
  "Plano":         { lat: 33.0198, lng: -96.6989 },
  "Irving":        { lat: 32.8140, lng: -96.9489 },
  "Frisco":        { lat: 33.1507, lng: -96.8236 },
  "Richardson":    { lat: 32.9483, lng: -96.7299 },
  "Garland":       { lat: 32.9126, lng: -96.6389 },
  "Arlington":     { lat: 32.7357, lng: -97.1081 },
  "Allen":         { lat: 33.1032, lng: -96.6706 },
  "Carrollton":    { lat: 32.9537, lng: -96.8903 },
  "Grand Prairie": { lat: 32.7460, lng: -96.9978 },
  "Cedar Park":    { lat: 30.5052, lng: -97.8203 },
  // Texas — Houston
  "Houston":       { lat: 29.7604, lng: -95.3698 },
  "Sugar Land":    { lat: 29.6197, lng: -95.6349 },
  "Katy":          { lat: 29.7858, lng: -95.8245 },
  "Stafford":      { lat: 29.6163, lng: -95.5577 },
  "Pearland":      { lat: 29.5636, lng: -95.2860 },
  // Illinois — Chicago
  "Chicago":       { lat: 41.8781, lng: -87.6298 },
  "Schaumburg":    { lat: 42.0334, lng: -88.0834 },
  "Naperville":    { lat: 41.7508, lng: -88.1535 },
  "Aurora":        { lat: 41.7606, lng: -88.3201 },
  "Skokie":        { lat: 42.0324, lng: -87.7416 },
  "Hoffman Estates": { lat: 42.0420, lng: -88.0798 },
  "Arlington Heights": { lat: 42.0884, lng: -87.9806 },
  "Willowbrook":   { lat: 41.7598, lng: -87.9354 },
  "Oak Park":      { lat: 41.8850, lng: -87.7845 },
  // Washington — Seattle
  "Seattle":       { lat: 47.6062, lng: -122.3321 },
  "Bellevue":      { lat: 47.6101, lng: -122.2015 },
  "Redmond":       { lat: 47.6740, lng: -122.1215 },
  "Kirkland":      { lat: 47.6815, lng: -122.2087 },
  "Bothell":       { lat: 47.7623, lng: -122.2054 },
  "Everett":       { lat: 47.9790, lng: -122.2021 },
  "Renton":        { lat: 47.4829, lng: -122.2171 },
  "Federal Way":   { lat: 47.3223, lng: -122.3126 },
  "SeaTac":        { lat: 47.4435, lng: -122.2961 },
  // Georgia — Atlanta
  "Atlanta":       { lat: 33.7490, lng: -84.3880 },
  "Alpharetta":    { lat: 34.0754, lng: -84.2941 },
  "Duluth":        { lat: 34.0029, lng: -84.1446 },
  "Norcross":      { lat: 33.9410, lng: -84.2135 },
  "Decatur":       { lat: 33.7748, lng: -84.2963 },
  "Johns Creek":   { lat: 34.0289, lng: -84.1983 },
  // DC Metro
  "Washington":    { lat: 38.9072, lng: -77.0369 },
  "Fairfax":       { lat: 38.8462, lng: -77.3064 },
  "Rockville":     { lat: 39.0840, lng: -77.1528 },
  "Bethesda":      { lat: 38.9847, lng: -77.0947 },
  "Tysons":        { lat: 38.9187, lng: -77.2311 },
  "Herndon":       { lat: 38.9696, lng: -77.3861 },
  "Vienna":        { lat: 38.9012, lng: -77.2653 },
  // Michigan — Detroit
  "Detroit":       { lat: 42.3314, lng: -83.0458 },
  "Troy":          { lat: 42.6064, lng: -83.1498 },
  "Novi":          { lat: 42.4801, lng: -83.4755 },
  "Farmington Hills": { lat: 42.4989, lng: -83.3677 },
  "Canton":        { lat: 42.3087, lng: -83.4816 },
  "Ann Arbor":     { lat: 42.2808, lng: -83.7430 },
  // North Carolina — Charlotte
  "Charlotte":     { lat: 35.2271, lng: -80.8431 },
  "Greensboro":    { lat: 36.0726, lng: -79.7920 },
  "Raleigh":       { lat: 35.7796, lng: -78.6382 },
  "Durham":        { lat: 35.9940, lng: -78.8986 },
  // Pennsylvania — Philadelphia
  "Philadelphia":  { lat: 39.9526, lng: -75.1652 },
  "King of Prussia": { lat: 40.0893, lng: -75.3963 },
  "Cherry Hill":   { lat: 39.9348, lng: -75.0307 },
  "Oaks":          { lat: 40.1312, lng: -75.4582 },
  "Bethlehem":     { lat: 40.6259, lng: -75.3705 },
  // Other metros
  "Nashville":     { lat: 36.1627, lng: -86.7816 },
  "Boston":        { lat: 42.3601, lng: -71.0589 },
  "Cambridge":     { lat: 42.3736, lng: -71.1097 },
  "Denver":        { lat: 39.7392, lng: -104.9903 },
  "Columbus":      { lat: 39.9612, lng: -82.9988 },
  "Baltimore":     { lat: 39.2904, lng: -76.6122 },
  // Florida
  "Hollywood":     { lat: 26.0112, lng: -80.1495 },
  "Miami":         { lat: 25.7617, lng: -80.1918 },
  "Tampa":         { lat: 27.9506, lng: -82.4572 },
  "Orlando":       { lat: 28.5383, lng: -81.3792 },
  "Jacksonville":  { lat: 30.3322, lng: -81.6557 },
};

/** Look up approximate coordinates for a city. Returns null if unknown. */
export function getCityCoords(city: string | null): { lat: number; lng: number } | null {
  if (!city) return null;
  return CITY_COORDS[city] || null;
}

/** Attach distance to each event relative to user location */
export type EventWithDistance = EventItem & { distanceMiles?: number };

export function sortEventsByDistance(
  events: EventItem[],
  userLat: number,
  userLng: number,
): EventWithDistance[] {
  const withDist: EventWithDistance[] = events.map((e) => {
    // Use per-event lat/lng from DB if available, fall back to city-level coords
    const coords = (e.latitude != null && e.longitude != null)
      ? { lat: e.latitude, lng: e.longitude }
      : getCityCoords(e.city);
    const distanceMiles = coords
      ? getDistanceMiles(userLat, userLng, coords.lat, coords.lng)
      : 9999;
    return { ...e, distanceMiles };
  });

  // Filter out events beyond 100 miles
  const nearby = withDist.filter((e) => (e.distanceMiles ?? 9999) <= 100);

  // Primary sort: distance, secondary: date
  nearby.sort((a, b) => {
    const da = a.distanceMiles ?? 9999;
    const db = b.distanceMiles ?? 9999;
    // If both within 20 miles of each other, sort by date first
    if (Math.abs(da - db) < 3) {
      const dateComp = a.date.localeCompare(b.date);
      if (dateComp !== 0) return dateComp;
    }
    return da - db;
  });

  return nearby;
}

/**
 * Fetch ALL upcoming events (no city filter, no limit).
 * Used for "Near Me" mode where we sort client-side by distance.
 */
export async function getAllUpcomingEvents(
  categories: string[] | null = null,
  search?: string,
): Promise<EventItem[]> {
  const today = new Date().toISOString().slice(0, 10);

  // Try static JSON first
  const cached = await loadEventsCache();
  if (cached) {
    let filtered = cached.filter((e) => e.date >= today);
    if (categories && categories.length > 0) {
      const catSet = new Set(categories);
      filtered = filtered.filter((e) => e.category && catSet.has(e.category));
    }
    if (search) {
      const q = search.toLowerCase();
      filtered = filtered.filter((e) =>
        e.title?.toLowerCase().includes(q) ||
        e.description?.toLowerCase().includes(q) ||
        e.long_description?.toLowerCase().includes(q) ||
        e.artist_info?.toLowerCase().includes(q) ||
        e.venue_name?.toLowerCase().includes(q) ||
        e.city?.toLowerCase().includes(q) ||
        e.organizer?.toLowerCase().includes(q)
      );
    }
    return filtered;
  }

  // Fallback: Supabase
  const data = await queryWithFallback((cols: string) => {
    let query = supabase
      .from("events")
      .select(cols)
      .gte("date", today)
      .order("date", { ascending: true })
      .limit(5000);

    if (categories && categories.length > 0) {
      query = query.in("category", categories);
    }

    if (search) {
      const q = `%${search}%`;
      query = query.or(
        `title.ilike.${q},description.ilike.${q},long_description.ilike.${q},artist_info.ilike.${q},venue_name.ilike.${q},city.ilike.${q},organizer.ilike.${q}`
      );
    }

    return query;
  });

  return data as EventItem[];
}

export const EVENT_CATEGORIES = [
  "Cultural", "Music", "Food", "Sports", "Community",
  "Festival", "Comedy", "Dance", "Religious", "Education",
  "Competition", "Other",
];

export function formatEventDate(dateStr: string, endDateStr?: string | null): string {
  const d = new Date(dateStr + "T00:00:00");
  const opts: Intl.DateTimeFormatOptions = { weekday: "short", month: "short", day: "numeric" };
  const formatted = d.toLocaleDateString("en-US", opts);
  if (endDateStr && endDateStr !== dateStr) {
    const end = new Date(endDateStr + "T00:00:00");
    const endFormatted = end.toLocaleDateString("en-US", opts);
    return `${formatted} – ${endFormatted}`;
  }
  return formatted;
}

export function formatEventDateLong(dateStr: string, endDateStr?: string | null): string {
  const d = new Date(dateStr + "T00:00:00");
  const opts: Intl.DateTimeFormatOptions = { weekday: "long", month: "long", day: "numeric", year: "numeric" };
  const formatted = d.toLocaleDateString("en-US", opts);
  if (endDateStr && endDateStr !== dateStr) {
    const end = new Date(endDateStr + "T00:00:00");
    const endFormatted = end.toLocaleDateString("en-US", opts);
    return `${formatted} – ${endFormatted}`;
  }
  return formatted;
}
