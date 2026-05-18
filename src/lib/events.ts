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
};

// Base columns that always exist
const BASE_COLS = "id,title,date,time,end_date,venue_name,city,state,category,description,image_url,ticket_url,source,price_range,organizer,audience";

// Extended columns (added by migration-event-detail.sql)
// If the migration hasn't been run yet, we fall back to BASE_COLS
const EVENT_COLS = BASE_COLS + ",long_description,artist_info,venue_info,slug";

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
    }));
  }
  if (error) {
    console.error("Failed to fetch events:", error);
    return [];
  }
  return data || [];
}

/**
 * Generate a deterministic slug from title + date.
 * Used both for URL generation and lookup matching.
 */
export function generateSlug(title: string, date: string): string {
  const cleaned = title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+$/, "")
    .slice(0, 60)
    .replace(/-+$/, "");
  return `${cleaned}-${date}`;
}

/**
 * City groups for the city picker. Each group maps a display label
 * to one or more city values that match the DB `city` column.
 */
export const CITY_GROUPS: { label: string; cities: string[] }[] = [
  { label: "Bay Area",      cities: ["San Francisco", "San Jose", "Oakland", "Fremont", "Sunnyvale", "Santa Clara", "Milpitas", "Pleasanton", "Union City", "Dublin", "Livermore", "Cupertino", "Mountain View", "Palo Alto", "Redwood City", "Berkeley", "Hayward", "San Mateo", "Daly City", "South San Francisco", "Los Gatos"] },
  { label: "NYC / NJ",      cities: ["New York", "Brooklyn", "Queens", "Edison", "Jersey City", "Newark", "Hoboken", "Parsippany", "Iselin", "Hicksville", "Garwood", "Mahwah", "New Brunswick", "South Brunswick Township", "Woodbridge Township", "Uniondale", "Atlantic City"] },
  { label: "Dallas",        cities: ["Dallas", "Plano", "Irving", "Frisco", "Richardson", "Garland", "Arlington", "Allen", "Carrollton", "Grand Prairie", "Cedar Park"] },
  { label: "Houston",       cities: ["Houston", "Sugar Land", "Katy", "Stafford", "Pearland"] },
  { label: "Chicago",       cities: ["Chicago", "Schaumburg", "Naperville", "Aurora", "Skokie", "Hoffman Estates", "Arlington Heights", "Willowbrook", "Oak Park"] },
  { label: "Los Angeles",   cities: ["Los Angeles", "Culver City", "Santa Monica", "Anaheim", "Irvine", "Pasadena", "Hermosa Beach", "Cerritos", "Torrance", "Playa del Rey", "Marina del Rey", "Downey", "Long Beach", "Glendale", "El Segundo"] },
  { label: "Seattle",       cities: ["Seattle", "Bellevue", "Redmond", "Kirkland", "Bothell", "Everett", "Renton", "Federal Way", "SeaTac"] },
  { label: "Atlanta",       cities: ["Atlanta", "Alpharetta", "Duluth", "Norcross", "Decatur", "Johns Creek"] },
  { label: "DC",            cities: ["Washington", "Fairfax", "Rockville", "Bethesda", "Tysons", "Herndon", "Vienna"] },
  { label: "Detroit",       cities: ["Detroit", "Troy", "Novi", "Farmington Hills", "Canton", "Ann Arbor"] },
  { label: "Charlotte",     cities: ["Charlotte", "Greensboro", "Raleigh", "Durham"] },
  { label: "Philadelphia",  cities: ["Philadelphia", "King of Prussia", "Cherry Hill", "Oaks", "Bethlehem"] },
  { label: "Nashville",     cities: ["Nashville"] },
  { label: "Boston",        cities: ["Boston", "Cambridge"] },
  { label: "Denver",        cities: ["Denver"] },
  { label: "Columbus",      cities: ["Columbus"] },
  { label: "Baltimore",     cities: ["Baltimore"] },
  { label: "Florida",       cities: ["Hollywood", "Miami", "Tampa", "Orlando", "Jacksonville"] },
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
        query = query.in("city", group.cities);
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
  // Try direct slug lookup first (if the DB column is populated)
  const { data: directMatch } = await supabase
    .from("events")
    .select(EVENT_COLS)
    .eq("slug", slug)
    .limit(1);

  if (directMatch && directMatch.length > 0) {
    return directMatch[0] as EventItem;
  }

  // Fallback: fetch all events and match computed slug
  const data = await queryWithFallback((cols: string) => {
    return supabase
      .from("events")
      .select(cols)
      .order("date", { ascending: true });
  });

  const match = (data as EventItem[]).find(
    (e) => generateSlug(e.title, e.date) === slug
  );
  return match || null;
}

/**
 * Fetch event counts per city group (for city pill badges).
 * Returns a map of city label → count.
 */
export async function getCityCounts(): Promise<Record<string, number>> {
  const today = new Date().toISOString().slice(0, 10);

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
