import { supabase } from "@/integrations/supabase/client";

export type Article = {
  id: number;
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
};

type ArticleRow = Omit<Article, "sources" | "author"> & {
  sources: string | null;
};

function parseSources(raw: string | null | undefined): Article["sources"] {
  if (!raw) return undefined;
  const trimmed = raw.trim();
  if (!trimmed) return undefined;
  try {
    const parsed = JSON.parse(trimmed);
    if (Array.isArray(parsed)) {
      return parsed
        .map((s) =>
          typeof s === "string"
            ? { label: s }
            : s && typeof s === "object" && "label" in s
              ? { label: String(s.label), url: s.url ? String(s.url) : undefined }
              : null
        )
        .filter(Boolean) as Article["sources"];
    }
  } catch {
    // Fallback: treat as newline-separated list
  }
  return trimmed
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean)
    .map((label) => ({ label }));
}

function mapRow(row: ArticleRow): Article {
  return {
    ...row,
    sources: parseSources(row.sources),
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
    .eq("status", "published")
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
    .eq("status", "published")
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
    .eq("status", "published")
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
