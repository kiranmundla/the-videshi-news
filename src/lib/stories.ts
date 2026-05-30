import { supabase as supabaseTyped } from "@/integrations/supabase/client";

const supabase = supabaseTyped as unknown as {
  from: (table: string) => any;
  functions: { invoke: (name: string, options?: any) => Promise<any> };
};

/* ------------------------------------------------------------------ */
/* Types                                                              */
/* ------------------------------------------------------------------ */
export type Story = {
  id: string;
  author_name: string;
  author_email: string;
  author_photo_url: string | null;
  author_city: string | null;
  author_linkedin: string | null;
  category: string;
  headline: string | null;
  subheadline: string | null;
  body: string | null;
  raw_story: string;
  prompt_what_happened: string | null;
  prompt_how_affected: string | null;
  prompt_advice: string | null;
  prompt_years_in_us: string | null;
  prompt_origin_city: string | null;
  status: string;
  featured: boolean;
  rejection_reason: string | null;
  suspicion_score: number;
  email_verified: boolean;
  reaction_count: number;
  view_count: number;
  slug: string | null;
  image_url: string | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
};

export const STORY_CATEGORIES = [
  { value: "immigration", label: "Immigration & Visa", emoji: "🗽" },
  { value: "career", label: "Career & Work", emoji: "💼" },
  { value: "family", label: "Family & Identity", emoji: "👨‍👩‍👧‍👦" },
  { value: "culture", label: "Culture & Belonging", emoji: "🪔" },
  { value: "food", label: "Food & Home", emoji: "🍛" },
  { value: "return-home", label: "Return to India", emoji: "✈️" },
  { value: "raising-kids", label: "Raising Kids Abroad", emoji: "👶" },
  { value: "general", label: "General", emoji: "📝" },
] as const;

export const YEARS_OPTIONS = [
  "Less than 1 year",
  "1–3 years",
  "3–5 years",
  "5–10 years",
  "10–20 years",
  "20+ years",
  "Returned home",
];

const PUBLISHED_COLS = "id,author_name,author_photo_url,author_city,category,headline,subheadline,body,slug,reaction_count,view_count,published_at,featured";

/* ------------------------------------------------------------------ */
/* Fetch published stories                                            */
/* ------------------------------------------------------------------ */
export async function fetchStories(opts?: {
  category?: string;
  limit?: number;
  offset?: number;
}): Promise<{ stories: Story[]; total: number }> {
  const limit = opts?.limit ?? 12;
  const offset = opts?.offset ?? 0;

  let q = supabase
    .from("stories")
    .select(PUBLISHED_COLS, { count: "exact" })
    .eq("status", "published")
    .order("published_at", { ascending: false })
    .range(offset, offset + limit - 1);

  if (opts?.category && opts.category !== "all") {
    q = q.eq("category", opts.category);
  }

  const { data, count, error } = await q;
  if (error) {
    console.error("fetchStories error:", error);
    return { stories: [], total: 0 };
  }
  return { stories: (data ?? []) as Story[], total: count ?? 0 };
}

/* ------------------------------------------------------------------ */
/* Fetch single story by slug                                         */
/* ------------------------------------------------------------------ */
export async function fetchStoryBySlug(slug: string): Promise<Story | null> {
  const { data, error } = await supabase
    .from("stories")
    .select("*")
    .eq("slug", slug)
    .eq("status", "published")
    .single();

  if (error || !data) return null;
  return data as Story;
}

/* ------------------------------------------------------------------ */
/* Create a draft story (before synthesis)                             */
/* ------------------------------------------------------------------ */
export async function createDraftStory(payload: {
  author_name: string;
  author_email: string;
  author_photo_url?: string;
  author_city?: string;
  author_linkedin?: string;
  category: string;
  raw_story: string;
  prompt_what_happened?: string;
  prompt_how_affected?: string;
  prompt_advice?: string;
  prompt_years_in_us?: string;
  prompt_origin_city?: string;
}): Promise<{ id: string; slug: string } | null> {
  const slug = generateSlug(payload.author_name);

  const { data, error } = await supabase
    .from("stories")
    .insert({
      ...payload,
      slug,
      status: "draft",
    })
    .select("id, slug")
    .single();

  if (error) {
    console.error("createDraftStory error:", error);
    return null;
  }
  return data;
}

/* ------------------------------------------------------------------ */
/* Update a draft story with synthesized content                      */
/* ------------------------------------------------------------------ */
export async function updateStoryContent(
  id: string,
  payload: {
    headline?: string;
    subheadline?: string;
    body?: string;
    suspicion_score?: number;
  }
): Promise<boolean> {
  const { error } = await supabase
    .from("stories")
    .update({ ...payload, updated_at: new Date().toISOString() })
    .eq("id", id);

  if (error) {
    console.error("updateStoryContent error:", error);
    return false;
  }
  return true;
}

/* ------------------------------------------------------------------ */
/* Increment reaction count (love)                                    */
/* ------------------------------------------------------------------ */
export async function reactToStory(id: string): Promise<number | null> {
  // Use RPC or raw update — increment by 1
  const { data, error } = await supabase
    .from("stories")
    .select("reaction_count")
    .eq("id", id)
    .single();

  if (error || !data) return null;

  const newCount = (data.reaction_count || 0) + 1;
  const { error: updateErr } = await supabase
    .from("stories")
    .update({ reaction_count: newCount })
    .eq("id", id);

  if (updateErr) return null;
  return newCount;
}

/* ------------------------------------------------------------------ */
/* Slug generator                                                     */
/* ------------------------------------------------------------------ */
function generateSlug(name: string): string {
  const base = name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 30)
    .replace(/-$/, "");

  const rand = Math.random().toString(36).slice(2, 8);
  return `${base}-${rand}`;
}

/* ------------------------------------------------------------------ */
/* Format helpers                                                     */
/* ------------------------------------------------------------------ */
export function formatStoryDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}

export function getCategoryLabel(value: string): string {
  return STORY_CATEGORIES.find((c) => c.value === value)?.label ?? value;
}

export function getCategoryEmoji(value: string): string {
  return STORY_CATEGORIES.find((c) => c.value === value)?.emoji ?? "📝";
}
