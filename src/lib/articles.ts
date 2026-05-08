import { supabase as supabaseTyped } from "@/integrations/supabase/client";

// Cast to any: Supabase types haven't regenerated since `category` was added to p2_articles.
const supabase = supabaseTyped as unknown as {
  from: (table: string) => any;
};

export type Article = {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  body: string;
  category: string;
  hero_image_url: string;
  image_caption?: string | null;
  image_credit?: string | null;
  author?: string;
  published_at: string;
  created_at: string;
  status: "published" | "draft";
  sources?: { label: string; url?: string }[];
  nri_angle?: string;
  article_type?: "news" | "feature";
  tags?: string[];
  featured_score?: number;
  is_pinned_featured?: boolean;
  pinned_until?: string | null;
};

type P2Row = {
  id: string;
  slug: string | null;
  headline: string;
  subheadline: string | null;
  body: string;

  vertical: string;
  status: string;
  is_featured: boolean | null;
  published_at: string | null;
  created_at: string;
  sources: unknown;
  diaspora_angle: string | null;
  tags: string[] | null;
  image_url: string | null;
};

const P2_COLS =
  "id, slug, headline, subheadline, body, vertical, status, is_featured, published_at, created_at, sources, diaspora_angle, tags, image_url";

function parseSources(raw: unknown): Article["sources"] {
  if (!raw || !Array.isArray(raw)) return undefined;
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

function deriveExcerpt(subheadline: string | null, body: string): string {
  if (subheadline && subheadline.trim()) return subheadline.trim();
  const plain = (body ?? "").replace(/[#*_>`~\-]+/g, "").trim();
  if (!plain) return "";
  return plain.length > 220 ? plain.slice(0, 217).trimEnd() + "…" : plain;
}

function mapRow(row: P2Row): Article {
  return {
    id: row.id,
    slug: row.slug ?? row.id,
    title: row.headline,
    excerpt: deriveExcerpt(row.subheadline, row.body),
    body: row.body ?? "",
    category: row.vertical ?? "",
    hero_image_url: row.image_url ?? "",
    image_caption: null,
    image_credit: null,
    published_at: row.published_at ?? row.created_at,
    created_at: row.created_at,
    status: row.status === "published" ? "published" : "draft",
    sources: parseSources(row.sources),
    nri_angle: row.diaspora_angle ?? undefined,
    article_type: "news",
    tags: Array.isArray(row.tags) ? row.tags : undefined,
    author: "Diaspora Desk",
    featured_score: 0,
    is_pinned_featured: !!row.is_featured,
    pinned_until: null,
  };
}

export async function getFeaturedArticle(): Promise<Article | null> {
  const { data } = await supabase
    .from("p2_articles")
    .select(P2_COLS)
    .eq("status", "published")
    .eq("is_featured", true)
    .order("published_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  if (data) return mapRow(data as P2Row);

  const { data: fallback } = await supabase
    .from("p2_articles")
    .select(P2_COLS)
    .eq("status", "published")
    .order("published_at", { ascending: false })
    .limit(1)
    .maybeSingle();
  return fallback ? mapRow(fallback as P2Row) : null;
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
    .from("p2_articles")
    .select(P2_COLS)
    .eq("status", "published")
    .order("published_at", { ascending: false });

  if (error) {
    console.error("[articles] getPublishedArticles", error);
    return [];
  }
  return (data as P2Row[]).map(mapRow);
}

export async function getArticleBySlug(slug: string): Promise<Article | null> {
  const { data, error } = await supabase
    .from("p2_articles")
    .select(P2_COLS)
    .eq("status", "published")
    .eq("slug", slug)
    .maybeSingle();

  if (error) {
    console.error("[articles] getArticleBySlug", error);
    return null;
  }
  return data ? mapRow(data as P2Row) : null;
}

export async function getRelatedArticles(
  currentSlug: string,
  category: string,
  limit = 3
): Promise<Article[]> {
  let query = supabase
    .from("p2_articles")
    .select(P2_COLS)
    .eq("status", "published")
    .neq("slug", currentSlug)
    .order("published_at", { ascending: false })
    .limit(limit);
  if (category) query = query.eq("vertical", category);

  const { data, error } = await query;
  if (error) {
    console.error("[articles] getRelatedArticles", error);
    return [];
  }
  return (data as P2Row[]).map(mapRow);
}

// Backwards-compatible aliases
export const getArticles = getPublishedArticles;
export const getRelated = (category: string, excludeSlug: string, limit = 3) =>
  getRelatedArticles(excludeSlug, category, limit);

export async function getArticlesByCategory(
  category: string,
  limit = 12,
  offset = 0
): Promise<Article[]> {
  const { data, error } = await supabase
    .from("p2_articles")
    .select(P2_COLS)
    .eq("status", "published")
    .eq("vertical", category)
    .order("published_at", { ascending: false })
    .range(offset, offset + limit - 1);
  if (error) {
    console.error("[articles] getArticlesByCategory", error);
    return [];
  }
  return (data as P2Row[]).map(mapRow);
}
