import { supabase } from "@/integrations/supabase/client";

export interface KeyUpdate {
  id: string;
  category: string;
  headline: string;
  detail: string | null;
  impact: "high" | "medium" | "low";
  article_id: string | null;
  article_slug: string | null;
  article_headline: string | null;
  event_date: string | null;
  created_at: string;
  related_articles: { slug: string; headline: string }[] | null;
}

export async function getKeyUpdates(
  category?: string,
  limit: number = 20
): Promise<KeyUpdate[]> {
  let query = supabase
    .from("key_updates")
    .select("*")
    .order("event_date", { ascending: false, nullsFirst: false })
    .limit(limit);

  if (category) {
    query = query.eq("category", category);
  }

  const { data, error } = await query;
  if (error) {
    console.error("[getKeyUpdates]", error);
    return [];
  }
  return (data ?? []) as KeyUpdate[];
}

export async function getKeyUpdateSlugs(
  category: string,
  limit: number = 50
): Promise<Set<string>> {
  const { data } = await supabase
    .from("key_updates")
    .select("article_slug")
    .eq("category", category)
    .not("article_slug", "is", null)
    .limit(limit);

  return new Set((data ?? []).map((d: any) => d.article_slug).filter(Boolean));
}
