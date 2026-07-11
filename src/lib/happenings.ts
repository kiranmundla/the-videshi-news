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
