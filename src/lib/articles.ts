import { supabase } from "@/integrations/supabase/client";

export type Article = {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  body: string;
  category: string;
  hero_image_url: string;
  author?: string;
  published_at: string;
  created_at: string;
  status: "published" | "draft";
  sources?: { label: string; url?: string }[];
  nri_angle?: string;
  article_type?: "news" | "feature";
};

type ArticleRow = {
  id: string;
  slug: string | null;
  title: string;
  summary: string;
  body: string;
  category: string;
  image_url: string | null;
  published_at: string | null;
  created_at: string;
  is_published: boolean | null;
  sources_used: unknown;
  nri_angle: string | null;
  article_type: string | null;
};

function parseSources(raw: unknown): Article["sources"] {
  if (!raw) return undefined;
  if (!Array.isArray(raw)) return undefined;
  return raw
    .map((s) => {
      if (typeof s === "string") return { label: s };
      if (s && typeof s === "object") {
        const o = s as Record<string, unknown>;
        const url = o.url ? String(o.url) : undefined;
        const label =
          (o.name as string) ||
          (o.label as string) ||
          (o.title as string) ||
          url ||
          "Source";
        return { label, url };
      }
      return null;
    })
    .filter(Boolean) as Article["sources"];
}

function mapRow(row: ArticleRow): Article {
  return {
    id: row.id,
    slug: row.slug ?? row.id,
    title: row.title,
    excerpt: row.summary ?? "",
    body: row.body ?? "",
    category: row.category ?? "",
    hero_image_url: row.image_url ?? "",
    published_at: row.published_at ?? row.created_at,
    created_at: row.created_at,
    status: row.is_published ? "published" : "draft",
    sources: parseSources(row.sources_used),
    nri_angle: row.nri_angle ?? undefined,
    author: "Diaspora Desk",
  };
}

export function readingTime(markdown: string) {
  const words = (markdown ?? "").trim().split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.round(words / 225));
}

export function formatLongDate(iso: string) {
  const d = new Date(iso);
  return d
    .toLocaleDateString("en-US", {
      weekday: "long",
      month: "long",
      day: "numeric",
      year: "numeric",
    })
    .replace(",", " ·");
}

export function formatShortDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export async function getPublishedArticles(): Promise<Article[]> {
  const { data, error } = await supabase
    .from("articles")
    .select("*")
    .eq("is_published", true)
    .order("published_at", { ascending: false });

  if (error) {
    console.error("[articles] getPublishedArticles", error);
    return [];
  }
  return (data as ArticleRow[]).map(mapRow);
}

export async function getArticleBySlug(slug: string): Promise<Article | null> {
  const { data, error } = await supabase
    .from("articles")
    .select("*")
    .eq("slug", slug)
    .eq("is_published", true)
    .maybeSingle();

  if (error) {
    console.error("[articles] getArticleBySlug", error);
    return null;
  }
  return data ? mapRow(data as ArticleRow) : null;
}

export async function getRelatedArticles(
  currentSlug: string,
  category: string,
  limit = 3
): Promise<Article[]> {
  const { data, error } = await supabase
    .from("articles")
    .select("*")
    .eq("is_published", true)
    .eq("category", category)
    .neq("slug", currentSlug)
    .order("published_at", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("[articles] getRelatedArticles", error);
    return [];
  }
  return (data as ArticleRow[]).map(mapRow);
}

// Backwards-compatible aliases
export const getArticles = getPublishedArticles;
export const getRelated = (category: string, excludeSlug: string, limit = 3) =>
  getRelatedArticles(excludeSlug, category, limit);

export async function getArticlesByCategory(
  category: string,
  limit = 20
): Promise<Article[]> {
  const { data, error } = await supabase
    .from("articles")
    .select("*")
    .eq("is_published", true)
    .eq("category", category)
    .order("published_at", { ascending: false })
    .limit(limit);
  if (error) { console.error(error); return []; }
  return (data as ArticleRow[]).map(mapRow);
}
