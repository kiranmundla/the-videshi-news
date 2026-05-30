import { supabase as supabaseTyped } from "@/integrations/supabase/client";

const supabase = supabaseTyped as unknown as {
  from: (table: string) => any;
};

/* ------------------------------------------------------------------ */
/* Types                                                              */
/* ------------------------------------------------------------------ */

export type Car = {
  id: string;
  name: string;
  brand: string;
  model: string;
  slug: string;
  category: string;
  body_type: string | null;
  fuel_type: string | null;
  year: number;
  msrp_low: number | null;
  msrp_high: number | null;
  mpg: string | null;
  seating: number | null;
  cargo_cu_ft: number | null;
  safety_rating: string | null;
  nri_take: string | null;
  pros: string[] | null;
  cons: string[] | null;
  image_url: string | null;
  images: { url: string; caption?: string }[] | null;
  lease_monthly: number | null;
  lease_due_at_signing: number | null;
  lease_term: number | null;
  lease_miles_per_year: number | null;
  lease_source: string | null;
  lease_expires: string | null;
  purchase_apr: number | null;
  affiliate_url: string | null;
  is_our_pick: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
};

export type CarCategory = "SUV" | "Sedan" | "Minivan" | "Luxury" | "EV";

export const CAR_CATEGORIES: CarCategory[] = ["SUV", "Sedan", "Minivan", "Luxury", "EV"];

export const CATEGORY_COLORS: Record<string, string> = {
  SUV: "bg-blue-900/40 text-blue-300",
  Sedan: "bg-emerald-900/40 text-emerald-300",
  Minivan: "bg-purple-900/40 text-purple-300",
  Luxury: "bg-amber-900/40 text-amber-300",
  EV: "bg-green-900/40 text-green-300",
};

export const CATEGORY_ICONS: Record<string, string> = {
  SUV: "🚙",
  Sedan: "🚗",
  Minivan: "🚐",
  Luxury: "✨",
  EV: "⚡",
};

const COLS =
  "id,name,brand,model,slug,category,body_type,fuel_type,year,msrp_low,msrp_high,mpg,seating,cargo_cu_ft,safety_rating,nri_take,pros,cons,image_url,images,lease_monthly,lease_due_at_signing,lease_term,lease_miles_per_year,lease_source,lease_expires,purchase_apr,affiliate_url,is_our_pick,sort_order,created_at,updated_at";

/* ------------------------------------------------------------------ */
/* Static JSON cache                                                  */
/* ------------------------------------------------------------------ */

let _carsCache: Car[] | null = null;

async function loadCarsCache(): Promise<Car[] | null> {
  if (_carsCache) return _carsCache;
  try {
    const res = await fetch("/data/cars.json");
    if (!res.ok) return null;
    _carsCache = (await res.json()) as Car[];
    return _carsCache;
  } catch {
    return null;
  }
}

/* ------------------------------------------------------------------ */
/* Queries                                                            */
/* ------------------------------------------------------------------ */

export async function getCars(opts?: {
  category?: string;
  search?: string;
}): Promise<Car[]> {
  // Try static JSON first
  const cached = await loadCarsCache();
  if (cached) {
    let cars = [...cached];
    if (opts?.category === "EV") {
      cars = cars.filter((c) => c.fuel_type === "Electric");
    } else if (opts?.category && opts.category !== "All") {
      cars = cars.filter((c) => c.category === opts.category);
    }
    if (opts?.search) {
      const s = opts.search.toLowerCase();
      cars = cars.filter(
        (c) =>
          c.name?.toLowerCase().includes(s) ||
          c.brand?.toLowerCase().includes(s) ||
          c.model?.toLowerCase().includes(s)
      );
    }
    return cars;
  }

  // Fallback: Supabase
  let q = supabase
    .from("cars")
    .select(COLS)
    .order("sort_order", { ascending: true })
    .order("name", { ascending: true });

  if (opts?.category === "EV") {
    q = q.eq("fuel_type", "Electric");
  } else if (opts?.category && opts.category !== "All") {
    q = q.eq("category", opts.category);
  }

  if (opts?.search) {
    q = q.or(
      `name.ilike.%${opts.search}%,brand.ilike.%${opts.search}%,model.ilike.%${opts.search}%`
    );
  }

  const { data, error } = await q;
  if (error) throw error;
  return (data ?? []) as Car[];
}

export async function getCarBySlug(slug: string): Promise<Car | null> {
  // Try static JSON first
  const cached = await loadCarsCache();
  if (cached) {
    const found = cached.find((c) => c.slug === slug);
    if (found) return found;
  }

  // Fallback: Supabase
  const { data, error } = await supabase
    .from("cars")
    .select(COLS)
    .eq("slug", slug)
    .limit(1)
    .maybeSingle();
  if (error) throw error;
  return (data ?? null) as Car | null;
}

export async function getCarsByCategory(category: string): Promise<Car[]> {
  // Try static JSON first
  const cached = await loadCarsCache();
  if (cached) {
    return cached.filter((c) => c.category === category).slice(0, 6);
  }

  // Fallback: Supabase
  const { data, error } = await supabase
    .from("cars")
    .select(COLS)
    .eq("category", category)
    .order("sort_order", { ascending: true })
    .limit(6);
  if (error) throw error;
  return (data ?? []) as Car[];
}

export async function getCarsByIds(ids: string[]): Promise<Car[]> {
  if (ids.length === 0) return [];

  // Try static JSON first
  const cached = await loadCarsCache();
  if (cached) {
    const idSet = new Set(ids);
    return cached.filter((c) => idSet.has(c.id));
  }

  // Fallback: Supabase
  const { data, error } = await supabase
    .from("cars")
    .select(COLS)
    .in("id", ids);
  if (error) throw error;
  return (data ?? []) as Car[];
}

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

export function formatPrice(n: number | null | undefined): string {
  if (!n) return "—";
  return "$" + n.toLocaleString("en-US");
}

export function formatMsrp(low: number | null, high: number | null): string {
  if (!low && !high) return "Price TBD";
  if (low && high && low !== high) return `${formatPrice(low)} – ${formatPrice(high)}`;
  return formatPrice(low ?? high);
}

/* Brand-based gradient for placeholder car images */
const BRAND_GRADIENTS: Record<string, string> = {
  Toyota: "from-red-900/60 to-red-800/30",
  Honda: "from-blue-900/60 to-blue-800/30",
  Hyundai: "from-sky-900/60 to-sky-800/30",
  Kia: "from-slate-800/60 to-slate-700/30",
  Tesla: "from-red-950/60 to-gray-900/30",
  Subaru: "from-blue-950/60 to-indigo-900/30",
  "Mercedes-Benz": "from-neutral-800/60 to-neutral-700/30",
  BMW: "from-blue-900/60 to-sky-900/30",
  Lexus: "from-zinc-800/60 to-zinc-700/30",
  Audi: "from-gray-800/60 to-gray-700/30",
  Genesis: "from-amber-900/60 to-amber-800/30",
  Acura: "from-indigo-900/60 to-indigo-800/30",
  "Land Rover": "from-green-900/60 to-green-800/30",
  Porsche: "from-red-900/60 to-neutral-800/30",
};

export function brandGradient(brand: string): string {
  return BRAND_GRADIENTS[brand] ?? "from-zinc-800/60 to-zinc-700/30";
}
