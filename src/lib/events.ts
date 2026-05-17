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
  image_url: string | null;
  ticket_url: string | null;
  source: string | null;
  price_range: string | null;
  organizer: string | null;
  audience: string | null;
};

const EVENT_COLS = "id,title,date,time,end_date,venue_name,city,state,category,description,image_url,ticket_url,source,price_range,organizer,audience";

/**
 * City groups for the city picker. Each group maps a display label
 * to one or more city values that match the DB `city` column.
 */
export const CITY_GROUPS: { label: string; cities: string[] }[] = [
  { label: "Bay Area",      cities: ["San Francisco", "San Jose", "Oakland", "Fremont", "Sunnyvale", "Santa Clara", "Milpitas", "Pleasanton", "Union City", "Dublin", "Livermore", "Cupertino", "Mountain View", "Palo Alto", "Redwood City", "Berkeley", "Hayward", "San Mateo", "Daly City", "South San Francisco"] },
  { label: "NYC / NJ",      cities: ["New York", "Brooklyn", "Queens", "Edison", "Jersey City", "Newark", "Hoboken", "Parsippany", "Iselin"] },
  { label: "Dallas",        cities: ["Dallas", "Plano", "Irving", "Frisco", "Richardson", "Garland", "Arlington"] },
  { label: "Houston",       cities: ["Houston", "Sugar Land", "Katy", "Stafford", "Pearland"] },
  { label: "Chicago",       cities: ["Chicago", "Schaumburg", "Naperville", "Aurora", "Skokie"] },
  { label: "Los Angeles",   cities: ["Los Angeles", "Culver City", "Santa Monica", "Anaheim", "Irvine", "Pasadena", "Hermosa Beach", "Cerritos"] },
  { label: "Seattle",       cities: ["Seattle", "Bellevue", "Redmond", "Kirkland", "Bothell"] },
  { label: "Atlanta",       cities: ["Atlanta", "Alpharetta", "Duluth", "Norcross", "Decatur", "Johns Creek"] },
  { label: "DC",            cities: ["Washington", "Arlington", "Fairfax", "Rockville", "Bethesda", "Tysons", "Herndon"] },
  { label: "Detroit",       cities: ["Detroit", "Troy", "Novi", "Farmington Hills", "Canton", "Ann Arbor"] },
  { label: "Charlotte",     cities: ["Charlotte", "Greensboro", "Raleigh", "Durham"] },
  { label: "Philadelphia",  cities: ["Philadelphia", "King of Prussia", "Cherry Hill"] },
];

export async function getEvents(
  cityFilter: string | null = null,
  categoryFilter: string | null = null,
  limit = 50,
  offset = 0,
): Promise<EventItem[]> {
  const today = new Date().toISOString().slice(0, 10);

  let query = supabase
    .from("events")
    .select(EVENT_COLS)
    .gte("date", today)
    .order("date", { ascending: true })
    .range(offset, offset + limit - 1);

  if (cityFilter) {
    // Find the city group
    const group = CITY_GROUPS.find((g) => g.label === cityFilter);
    if (group) {
      query = query.in("city", group.cities);
    }
  }

  if (categoryFilter) {
    query = query.eq("category", categoryFilter);
  }

  const { data, error } = await query;
  if (error) {
    console.error("Failed to fetch events:", error);
    return [];
  }
  return (data || []) as EventItem[];
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
