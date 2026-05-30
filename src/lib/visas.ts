import { supabase as supabaseTyped } from "@/integrations/supabase/client";

const supabase = supabaseTyped as unknown as { from: (table: string) => any };

/* ------------------------------------------------------------------ */
/* Types                                                              */
/* ------------------------------------------------------------------ */

export type VisaSighting = {
  id: string;
  consulate: string;
  visa_type: string;
  slots_date_start: string | null;
  slots_date_end: string | null;
  description: string;
  reporter_name: string;
  reporter_email: string;
  verified: boolean;
  created_at: string;
  status: string;
};

export type VisaWaitTime = {
  id: string;
  consulate: string;
  consulate_display: string;
  visa_type: string;
  visa_type_display: string;
  avg_wait_months: number | null;
  next_available_months: number | null;
  scraped_at: string;
  source_updated: string | null;
  created_at: string;
};

/* ------------------------------------------------------------------ */
/* Constants                                                          */
/* ------------------------------------------------------------------ */

export const CONSULATES = ["mumbai", "new_delhi", "chennai", "hyderabad", "kolkata"] as const;

export const CONSULATE_LABELS: Record<string, string> = {
  mumbai: "Mumbai",
  new_delhi: "New Delhi",
  chennai: "Chennai",
  hyderabad: "Hyderabad",
  kolkata: "Kolkata",
};

export const VISA_TYPES = ["B1/B2", "H-1B", "H-4", "F-1", "L-1", "L-2", "O-1", "J-1", "Other"] as const;

export const CONSULATE_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  mumbai:    { bg: "bg-blue-500/10",   text: "text-blue-600",   border: "border-blue-500/20" },
  new_delhi: { bg: "bg-orange-500/10", text: "text-orange-600", border: "border-orange-500/20" },
  chennai:   { bg: "bg-green-500/10",  text: "text-green-600",  border: "border-green-500/20" },
  hyderabad: { bg: "bg-purple-500/10", text: "text-purple-600", border: "border-purple-500/20" },
  kolkata:   { bg: "bg-rose-500/10",   text: "text-rose-600",   border: "border-rose-500/20" },
};

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

export function relativeTime(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffMs = now - then;
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) return `${diffH}h ago`;
  const diffD = Math.floor(diffH / 24);
  if (diffD === 1) return "yesterday";
  if (diffD < 7) return `${diffD}d ago`;
  return new Date(dateStr).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function waitColor(m: number | null): string {
  if (m === null) return "text-foreground/40";
  if (m < 2) return "text-green-600";
  if (m < 5) return "text-amber-600";
  if (m < 8) return "text-orange-600";
  return "text-red-600";
}

export function waitBg(m: number | null): string {
  if (m === null) return "bg-foreground/5";
  if (m < 2) return "bg-green-500/10";
  if (m < 5) return "bg-amber-500/10";
  if (m < 8) return "bg-orange-500/10";
  return "bg-red-500/10";
}

export function formatMonths(m: number | null): string {
  if (m === null || m === undefined) return "N/A";
  if (m < 0.5) return "< 2 wk";
  if (m === 0.5) return "2 wk";
  if (m === 1) return "1 mo";
  return `${m} mo`;
}

/* ------------------------------------------------------------------ */
/* Data loading — static JSON first, Supabase fallback                */
/* ------------------------------------------------------------------ */

let sightingsCache: VisaSighting[] | null = null;
let waitTimesCache: VisaWaitTime[] | null = null;

export async function getVisaSightings(opts?: {
  consulate?: string;
  visa_type?: string;
}): Promise<VisaSighting[]> {
  // Try static JSON
  if (!sightingsCache) {
    try {
      const res = await fetch("/data/visa-sightings.json");
      if (res.ok) sightingsCache = await res.json();
    } catch {}
  }

  // Fallback to Supabase
  if (!sightingsCache) {
    try {
      const { data, error } = await supabase
        .from("visa_sightings")
        .select("*")
        .eq("status", "published")
        .order("created_at", { ascending: false })
        .limit(100);
      if (!error && data) sightingsCache = data as VisaSighting[];
    } catch {}
  }

  let results = sightingsCache || [];

  // Client-side filter
  if (opts?.consulate) results = results.filter((s) => s.consulate === opts.consulate);
  if (opts?.visa_type) results = results.filter((s) => s.visa_type === opts.visa_type);

  return results;
}

export async function getVisaWaitTimes(): Promise<VisaWaitTime[]> {
  if (waitTimesCache) return waitTimesCache;

  // Try static JSON
  try {
    const res = await fetch("/data/visa-wait-times.json");
    if (res.ok) {
      waitTimesCache = await res.json();
      return waitTimesCache!;
    }
  } catch {}

  // Fallback to Supabase
  try {
    const { data, error } = await supabase
      .from("consulate_wait_times")
      .select("*")
      .order("scraped_at", { ascending: false });
    if (!error && data) {
      waitTimesCache = data as VisaWaitTime[];
      return waitTimesCache;
    }
  } catch {}

  return [];
}

export async function submitSighting(data: {
  consulate: string;
  visa_type: string;
  slots_date_start?: string;
  slots_date_end?: string;
  description: string;
  reporter_name: string;
  reporter_email: string;
}): Promise<{ success: boolean; error?: string }> {
  try {
    const { error } = await supabase.from("visa_sightings").insert([
      {
        ...data,
        status: "published", // auto-publish for MVP (Turnstile-protected)
        verified: false,
      },
    ]);
    if (error) return { success: false, error: error.message };

    // Clear cache so fresh data loads
    sightingsCache = null;
    return { success: true };
  } catch (e: any) {
    return { success: false, error: e.message || "Unknown error" };
  }
}
