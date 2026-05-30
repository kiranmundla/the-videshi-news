import { supabase as supabaseTyped } from "@/integrations/supabase/client";

const supabase = supabaseTyped as unknown as {
  from: (table: string) => any;
  storage: any;
};

/* ------------------------------------------------------------------ */
/* Types                                                              */
/* ------------------------------------------------------------------ */

export type ContactPreference = "show_all" | "phone_only" | "email_only" | "inquire_only";

export type Classified = {
  id: string;
  title: string;
  description: string | null;
  category: string;
  subcategory: string | null;
  price: string | null;
  contact_name: string | null;
  contact_email: string | null;
  contact_phone: string | null;
  contact_preference: ContactPreference;
  city: string | null;
  state: string | null;
  zip: string | null;
  image_url: string | null;
  photos: string[];
  slug: string;
  source: string | null;
  status: string;
  expires_at: string | null;
  created_at: string;
  updated_at: string;
};

export const CONTACT_PREFERENCE_OPTIONS: { value: ContactPreference; label: string; desc: string }[] = [
  { value: "show_all", label: "Show phone & email", desc: "Both visible on your listing" },
  { value: "phone_only", label: "Show phone only", desc: "Email used only for verification" },
  { value: "email_only", label: "Show email only", desc: "Phone number hidden" },
  { value: "inquire_only", label: "Inquire only", desc: "Contact info hidden — viewers send inquiry" },
];

const COLS =
  "id,title,description,category,subcategory,price,contact_name,contact_email,contact_phone,contact_preference,city,state,zip,image_url,photos,slug,source,status,expires_at,created_at,updated_at";

/* ------------------------------------------------------------------ */
/* Categories & subcategories                                         */
/* ------------------------------------------------------------------ */

export const CLASSIFIED_CATEGORIES = [
  "Services",
  "Housing",
  "For Sale",
  "Jobs & Gigs",
  "Community",
] as const;

export type ClassifiedCategory = (typeof CLASSIFIED_CATEGORIES)[number];

export const CATEGORY_ICONS: Record<string, string> = {
  Services: "🔧",
  Housing: "🏠",
  "For Sale": "🏷️",
  "Jobs & Gigs": "💼",
  Community: "🤝",
};

export const CATEGORY_COLORS: Record<string, string> = {
  Services: "bg-blue-100 text-blue-700",
  Housing: "bg-emerald-100 text-emerald-700",
  "For Sale": "bg-amber-100 text-amber-700",
  "Jobs & Gigs": "bg-purple-100 text-purple-700",
  Community: "bg-teal-100 text-teal-700",
};

export const SUBCATEGORIES: Record<string, string[]> = {
  Services: [
    "Priest/Pandit",
    "Catering",
    "Mehendi/Henna",
    "Tutoring",
    "Tax & Accounting",
    "Immigration Help",
    "Photography/Videography",
    "Driving Lessons",
    "Movers & Packers",
    "Cleaning",
    "Other",
  ],
  Housing: [
    "Roommate Wanted",
    "Room Available",
    "Short-term Sublet",
    "PG/Shared Housing",
    "Other",
  ],
  "For Sale": [
    "Furniture",
    "Kitchen & Appliances",
    "Electronics",
    "Ethnic Wear & Jewelry",
    "Books & Textbooks",
    "Baby & Kids",
    "Other",
  ],
  "Jobs & Gigs": [
    "Part-time",
    "Babysitting/Nanny",
    "IT/Tech Contract",
    "Restaurant/Retail",
    "Delivery/Driving",
    "Freelance",
    "Other",
  ],
  Community: [
    "Carpool",
    "Cricket/Sports Team",
    "Volunteers Needed",
    "Study Group",
    "Lost & Found",
    "Other",
  ],
};

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

function parseJsonField<T>(val: unknown, fallback: T): T {
  if (val == null) return fallback;
  if (typeof val === "object") return val as T;
  if (typeof val === "string") {
    try {
      return JSON.parse(val) as T;
    } catch {
      return fallback;
    }
  }
  return fallback;
}

function parseClassified(row: any): Classified {
  return {
    ...row,
    photos: parseJsonField<string[]>(row.photos, []),
    contact_preference: row.contact_preference || "show_all",
  };
}

/* ------------------------------------------------------------------ */
/* Static JSON cache                                                  */
/* ------------------------------------------------------------------ */

let _classifiedsCache: Classified[] | null = null;

async function loadClassifiedsCache(): Promise<Classified[] | null> {
  if (_classifiedsCache) return _classifiedsCache;
  try {
    const res = await fetch("/data/classifieds.json");
    if (!res.ok) return null;
    const raw = (await res.json()) as any[];
    _classifiedsCache = raw.map(parseClassified);
    return _classifiedsCache;
  } catch {
    return null;
  }
}

export function generateClassifiedSlug(title: string): string {
  const cleaned = title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+$/, "")
    .slice(0, 50)
    .replace(/-+$/, "");
  const rand = Math.random().toString(36).slice(2, 8);
  return `${cleaned}-${rand}`;
}

export function timeAgo(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffMs = now - then;
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days === 1) return "1 day ago";
  if (days < 30) return `${days} days ago`;
  const months = Math.floor(days / 30);
  return months === 1 ? "1 month ago" : `${months} months ago`;
}

/* ------------------------------------------------------------------ */
/* Data fetching                                                      */
/* ------------------------------------------------------------------ */

export async function getClassifieds(
  category: string | null = null,
  city: string | null = null,
  search: string | null = null,
  subcategory: string | null = null,
  limit = 50,
  offset = 0,
): Promise<Classified[]> {
  // Try static JSON first
  const cached = await loadClassifiedsCache();
  if (cached) {
    const now = new Date().toISOString();
    let filtered = cached.filter((c) => c.status === "active" && (!c.expires_at || c.expires_at > now));
    if (category) {
      filtered = filtered.filter((c) => c.category === category);
    }
    if (subcategory) {
      filtered = filtered.filter((c) => c.subcategory === subcategory);
    }
    if (city) {
      const { CITY_GROUPS } = await import("./events");
      const group = CITY_GROUPS.find((g) => g.label === city);
      if (group) {
        const cities = new Set([...group.cities, group.label]);
        filtered = filtered.filter((c) => c.city && cities.has(c.city));
      }
    }
    if (search) {
      const q = search.toLowerCase();
      filtered = filtered.filter((c) =>
        c.title?.toLowerCase().includes(q) ||
        c.description?.toLowerCase().includes(q) ||
        c.category?.toLowerCase().includes(q) ||
        c.city?.toLowerCase().includes(q) ||
        c.subcategory?.toLowerCase().includes(q)
      );
    }
    return filtered.slice(offset, offset + limit);
  }

  // Fallback: Supabase
  let query = supabase
    .from("classifieds")
    .select(COLS)
    .eq("status", "active")
    .gt("expires_at", new Date().toISOString())
    .order("created_at", { ascending: false })
    .range(offset, offset + limit - 1);

  if (category) {
    query = query.eq("category", category);
  }

  if (subcategory) {
    query = query.eq("subcategory", subcategory);
  }

  if (city) {
    const { CITY_GROUPS } = await import("./events");
    const group = CITY_GROUPS.find((g) => g.label === city);
    if (group) {
      query = query.in("city", [...group.cities, group.label]);
    }
  }

  if (search) {
    const q = `%${search}%`;
    query = query.or(
      `title.ilike.${q},description.ilike.${q},category.ilike.${q},city.ilike.${q},subcategory.ilike.${q}`
    );
  }

  const { data, error } = await query;
  if (error) {
    console.error("Failed to fetch classifieds:", error);
    return [];
  }
  return ((data || []) as any[]).map(parseClassified);
}

/** Fetch all active classifieds (no city filter, no limit). Used for Near Me sorting. */
export async function getAllClassifieds(
  category: string | null = null,
  search: string | null = null,
  subcategory: string | null = null,
): Promise<Classified[]> {
  // Try static JSON first
  const cached = await loadClassifiedsCache();
  if (cached) {
    const now = new Date().toISOString();
    let filtered = cached.filter((c) => c.status === "active" && (!c.expires_at || c.expires_at > now));
    if (category) filtered = filtered.filter((c) => c.category === category);
    if (subcategory) filtered = filtered.filter((c) => c.subcategory === subcategory);
    if (search) {
      const q = search.toLowerCase();
      filtered = filtered.filter((c) =>
        c.title?.toLowerCase().includes(q) ||
        c.description?.toLowerCase().includes(q) ||
        c.category?.toLowerCase().includes(q) ||
        c.city?.toLowerCase().includes(q) ||
        c.subcategory?.toLowerCase().includes(q)
      );
    }
    return filtered.slice(0, 500);
  }

  // Fallback: Supabase
  let query = supabase
    .from("classifieds")
    .select(COLS)
    .eq("status", "active")
    .gt("expires_at", new Date().toISOString())
    .order("created_at", { ascending: false })
    .limit(500);

  if (category) query = query.eq("category", category);
  if (subcategory) query = query.eq("subcategory", subcategory);

  if (search) {
    const q = `%${search}%`;
    query = query.or(
      `title.ilike.${q},description.ilike.${q},category.ilike.${q},city.ilike.${q},subcategory.ilike.${q}`
    );
  }

  const { data, error } = await query;
  if (error) { console.error("Failed to fetch classifieds:", error); return []; }
  return ((data || []) as any[]).map(parseClassified);
}

export async function getClassifiedBySlug(
  slug: string,
): Promise<Classified | null> {
  // Try static JSON first
  const cached = await loadClassifiedsCache();
  if (cached) {
    const found = cached.find((c) => c.slug === slug);
    if (found) return found;
  }

  // Fallback: Supabase
  const { data, error } = await supabase
    .from("classifieds")
    .select(COLS)
    .eq("slug", slug)
    .limit(1);

  if (error || !data || data.length === 0) return null;
  return parseClassified(data[0] as any);
}

/* ------------------------------------------------------------------ */
/* Distance helpers                                                   */
/* ------------------------------------------------------------------ */

export function getDistanceMiles(
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number,
): number {
  const R = 3958.8;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export function formatDistance(miles: number): string {
  if (miles < 1) return "< 1 mi";
  if (miles < 10) return `${miles.toFixed(1)} mi`;
  return `${Math.round(miles)} mi`;
}
