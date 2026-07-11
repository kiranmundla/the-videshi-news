import { supabase } from "@/integrations/supabase/client";

export interface DailyHappening {
  id: string;
  date: string;
  emoji: string;
  label: string;
  detail: string | null;
  link: string | null;
  category: string | null;
  sort_order: number;
  start_time: string | null;
}

/** Format a UTC timestamp into the user's local time, e.g. "2:00 PM" */
function formatLocalTime(utcIso: string): string {
  const d = new Date(utcIso);
  if (isNaN(d.getTime())) return "";
  return d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

/** Check if a UTC timestamp is in the past */
function isPast(utcIso: string): boolean {
  return new Date(utcIso).getTime() < Date.now();
}

/** Build the display detail with local time */
export function buildDetail(item: DailyHappening): string {
  const parts: string[] = [];

  if (item.start_time) {
    if (isPast(item.start_time)) {
      parts.push("(concluded)");
    } else {
      parts.push(formatLocalTime(item.start_time));
    }
  }

  if (item.detail) {
    parts.push(item.detail);
  }

  return parts.join(" · ");
}

export async function getTodayHappenings(): Promise<DailyHappening[]> {
  const today = new Date().toISOString().split("T")[0];
  const { data, error } = await supabase
    .from("daily_happenings")
    .select("*")
    .eq("date", today)
    .order("sort_order", { ascending: true });

  if (error) {
    console.error("[getTodayHappenings]", error);
    return [];
  }
  return (data ?? []) as DailyHappening[];
}
