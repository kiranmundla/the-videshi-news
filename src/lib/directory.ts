import { supabase as supabaseTyped } from "@/integrations/supabase/client";

const supabase = supabaseTyped as unknown as {
  from: (table: string) => any;
};

export type DirectoryListing = {
  id: string;
  name: string;
  category: string;
  subcategory: string | null;
  description: string | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  zip: string | null;
  latitude: number | null;
  longitude: number | null;
  image_url: string | null;
  photos: string[] | null;
  rating: number | null;
  review_count: number | null;
  google_place_id: string | null;
  hours: Record<string, string> | null;
  source: string | null;
  verified: boolean;
  featured: boolean;
  slug: string;
  created_at: string;
};

const LISTING_COLS =
  "id,name,category,subcategory,description,phone,email,website,address,city,state,zip,latitude,longitude,image_url,photos,rating,review_count,google_place_id,hours,source,verified,featured,slug,created_at";

export const DIRECTORY_CATEGORIES = [
  "Doctors & Healthcare",
  "Attorneys & Immigration",
  "Real Estate",
  "Tax & Accounting",
  "Catering & Food",
  "Yoga & Wellness",
  "Beauty & Grooming",
  "Education & Tutoring",
  "Religious Services",
  "Home Services",
];

export const CATEGORY_ICONS: Record<string, string> = {
  "Doctors & Healthcare": "🩺",
  "Attorneys & Immigration": "⚖️",
  "Real Estate": "🏠",
  "Tax & Accounting": "📊",
  "Catering & Food": "🍛",
  "Yoga & Wellness": "🧘",
  "Beauty & Grooming": "💇",
  "Education & Tutoring": "📚",
  "Religious Services": "🙏",
  "Home Services": "🔧",
};

export const CATEGORY_COLORS: Record<string, string> = {
  "Doctors & Healthcare": "bg-blue-100 text-blue-700",
  "Attorneys & Immigration": "bg-purple-100 text-purple-700",
  "Real Estate": "bg-emerald-100 text-emerald-700",
  "Tax & Accounting": "bg-amber-100 text-amber-700",
  "Catering & Food": "bg-orange-100 text-orange-700",
  "Yoga & Wellness": "bg-teal-100 text-teal-700",
  "Beauty & Grooming": "bg-pink-100 text-pink-700",
  "Education & Tutoring": "bg-indigo-100 text-indigo-700",
  "Religious Services": "bg-violet-100 text-violet-700",
  "Home Services": "bg-slate-100 text-slate-700",
};

/* ------------------------------------------------------------------ */
/* JSON field parser                                                  */
/* ------------------------------------------------------------------ */
function parseJsonField<T>(val: unknown, fallback: T): T {
  if (val == null) return fallback;
  if (typeof val === "object") return val as T;
  if (typeof val === "string") {
    try { return JSON.parse(val) as T; } catch { return fallback; }
  }
  return fallback;
}

function parseListing(row: any): DirectoryListing {
  return {
    ...row,
    photos: parseJsonField<string[]>(row.photos, []),
    hours: parseJsonField<Record<string, string>>(row.hours, null),
  };
}

/* ------------------------------------------------------------------ */
/* Data fetching                                                      */
/* ------------------------------------------------------------------ */

export async function getDirectoryListings(
  category: string | null = null,
  city: string | null = null,
  search: string | null = null,
  limit = 50,
  offset = 0,
): Promise<DirectoryListing[]> {
  let query = supabase
    .from("directory_listings")
    .select(LISTING_COLS)
    .order("featured", { ascending: false })
    .order("rating", { ascending: false, nullsFirst: false })
    .range(offset, offset + limit - 1);

  if (category) {
    query = query.eq("category", category);
  }

  if (city) {
    // Import CITY_GROUPS from events
    const { CITY_GROUPS } = await import("./events");
    const group = CITY_GROUPS.find((g) => g.label === city);
    if (group) {
      query = query.in("city", [...group.cities, group.label]);
    }
  }

  if (search) {
    const q = `%${search}%`;
    query = query.or(
      `name.ilike.${q},description.ilike.${q},category.ilike.${q},city.ilike.${q},subcategory.ilike.${q}`
    );
  }

  const { data, error } = await query;
  if (error) {
    console.error("Failed to fetch directory listings:", error);
    return [];
  }
  return ((data || []) as any[]).map(parseListing);
}

export async function getDirectoryListing(slug: string): Promise<DirectoryListing | null> {
  const { data, error } = await supabase
    .from("directory_listings")
    .select(LISTING_COLS)
    .eq("slug", slug)
    .limit(1);

  if (error || !data || data.length === 0) return null;
  return parseListing(data[0] as any);
}

export async function getFeaturedListings(): Promise<DirectoryListing[]> {
  const { data, error } = await supabase
    .from("directory_listings")
    .select(LISTING_COLS)
    .eq("featured", true)
    .order("rating", { ascending: false, nullsFirst: false })
    .limit(10);

  if (error) {
    console.error("Failed to fetch featured listings:", error);
    return [];
  }
  return ((data || []) as any[]).map(parseListing);
}

export async function getDirectoryCityCounts(): Promise<Record<string, number>> {
  const { data, error } = await supabase
    .from("directory_listings")
    .select("city");

  if (error || !data) return {};

  const { CITY_GROUPS } = await import("./events");
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

export async function getDirectoryCategoryCounts(): Promise<Record<string, number>> {
  const { data, error } = await supabase
    .from("directory_listings")
    .select("category");

  if (error || !data) return {};

  const counts: Record<string, number> = {};
  for (const row of data as { category: string }[]) {
    counts[row.category] = (counts[row.category] || 0) + 1;
  }
  return counts;
}

/** Distance helpers (same as events) */
export function getDistanceMiles(
  lat1: number, lng1: number,
  lat2: number, lng2: number,
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

export type ListingWithDistance = DirectoryListing & { distanceMiles?: number };

export function sortListingsByDistance(
  listings: DirectoryListing[],
  userLat: number,
  userLng: number,
): ListingWithDistance[] {
  const withDist: ListingWithDistance[] = listings.map((l) => {
    const distanceMiles =
      l.latitude != null && l.longitude != null
        ? getDistanceMiles(userLat, userLng, l.latitude, l.longitude)
        : 9999;
    return { ...l, distanceMiles };
  });

  withDist.sort((a, b) => {
    const da = a.distanceMiles ?? 9999;
    const db = b.distanceMiles ?? 9999;
    if (Math.abs(da - db) < 5) {
      return (b.rating ?? 0) - (a.rating ?? 0);
    }
    return da - db;
  });

  return withDist;
}
