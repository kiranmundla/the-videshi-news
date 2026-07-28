import { supabase as supabaseTyped } from "@/integrations/supabase/client";

const supabase = supabaseTyped as unknown as {
  from: (table: string) => any;
};

/* ------------------------------------------------------------------ */
/* Types                                                              */
/* ------------------------------------------------------------------ */

export interface KidsLocalPlace {
  id: string;
  name: string;
  slug: string;
  category: string;
  subcategory: string | null;
  description: string | null;
  address: string | null;
  city: string;
  state: string;
  zip_code: string | null;
  phone: string | null;
  website: string | null;
  latitude: number | null;
  longitude: number | null;
  rating: number | null;
  review_count: number | null;
  age_range: string | null;
  image_url: string | null;
  is_indian_focused: boolean;
  tags: string[];
  distance_miles?: number;
}

/* ------------------------------------------------------------------ */
/* Constants                                                          */
/* ------------------------------------------------------------------ */

export const LOCAL_CATEGORIES = [
  { key: "All", icon: "📋" },
  { key: "Daycare", icon: "🏠" },
  { key: "Dance", icon: "💃" },
  { key: "Music", icon: "🎵" },
  { key: "Swimming", icon: "🏊" },
  { key: "Cricket", icon: "🏏" },
  { key: "Martial Arts", icon: "🥋" },
  { key: "Gymnastics", icon: "🤸" },
  { key: "Tutoring", icon: "📚" },
  { key: "Math Enrichment", icon: "🔢" },
  { key: "Coding & STEM", icon: "💻" },
  { key: "Art", icon: "🎨" },
  { key: "Chess", icon: "♟️" },
  { key: "Language", icon: "🗣️" },
];

export const CATEGORY_GRADIENTS: Record<string, string> = {
  Daycare: "from-orange-400 to-amber-300",
  Dance: "from-pink-400 to-rose-300",
  Music: "from-purple-400 to-violet-300",
  Swimming: "from-cyan-400 to-blue-300",
  Cricket: "from-green-500 to-emerald-300",
  "Martial Arts": "from-red-500 to-orange-400",
  Gymnastics: "from-sky-400 to-cyan-300",
  Tutoring: "from-blue-400 to-indigo-300",
  "Math Enrichment": "from-indigo-400 to-blue-300",
  "Coding & STEM": "from-violet-500 to-purple-300",
  Art: "from-fuchsia-400 to-pink-300",
  Chess: "from-slate-500 to-gray-400",
  Language: "from-amber-400 to-yellow-300",
};

export const LOCAL_CATEGORY_COLORS: Record<string, string> = {
  Daycare: "bg-orange-100 text-orange-700",
  Dance: "bg-pink-100 text-pink-700",
  Music: "bg-purple-100 text-purple-700",
  Swimming: "bg-cyan-100 text-cyan-700",
  Cricket: "bg-green-100 text-green-700",
  "Martial Arts": "bg-red-100 text-red-700",
  Gymnastics: "bg-sky-100 text-sky-700",
  Tutoring: "bg-blue-100 text-blue-700",
  "Math Enrichment": "bg-indigo-100 text-indigo-700",
  "Coding & STEM": "bg-violet-100 text-violet-700",
  Art: "bg-fuchsia-100 text-fuchsia-700",
  Chess: "bg-slate-100 text-slate-700",
  Language: "bg-amber-100 text-amber-700",
};

/* ------------------------------------------------------------------ */
/* Data fetching                                                      */
/* ------------------------------------------------------------------ */

export async function fetchLocalPlaces(): Promise<KidsLocalPlace[]> {
  try {
    const { data, error } = await supabase
      .from("kids_local_places")
      .select("*")
      .order("rating", { ascending: false, nullsLast: true })
      .order("name", { ascending: true });

    if (error) {
      console.error("Failed to fetch local places:", error);
      return [];
    }
    return (data || []) as KidsLocalPlace[];
  } catch (err) {
    console.error("Failed to fetch local places:", err);
    return [];
  }
}

/* ------------------------------------------------------------------ */
/* Utilities                                                          */
/* ------------------------------------------------------------------ */

/** Haversine distance in miles */
export function distanceMiles(
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

/** Check if a place's age_range overlaps with an age group */
export function placeMatchesAge(
  ageRange: string | null,
  ageGroup: string,
): boolean {
  if (!ageRange) return true;

  const ranges: Record<string, [number, number]> = {
    preschool: [2, 5],
    elementary: [5, 11],
    middle_school: [11, 14],
    high_school: [14, 18],
  };

  const target = ranges[ageGroup];
  if (!target) return true;

  const m = ageRange.match(/(\d+)\s*[-–]\s*(\d+)/);
  if (m) {
    const min = parseInt(m[1]);
    const max = parseInt(m[2]);
    return min <= target[1] && max >= target[0];
  }

  const plus = ageRange.match(/(\d+)\+/);
  if (plus) {
    return target[1] >= parseInt(plus[1]);
  }

  return true;
}
