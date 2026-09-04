import { supabase as supabaseTyped } from "@/integrations/supabase/client";

// Cast to any: Supabase types haven't regenerated since `category` was added to p2_articles.
const supabase = supabaseTyped as unknown as {
  from: (table: string) => any;
};

export type GalleryImage = { url: string; caption: string };

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
  gallery_images?: GalleryImage[] | null;
  author?: string;
  published_at: string;
  event_at?: string | null;
  updated_at?: string;
  created_at: string;
  status: "published" | "draft";
  sources?: { label: string; url?: string }[];
  nri_angle?: string;
  article_type?: "news" | "feature" | "interview";
  tags?: string[];
  featured_score?: number;
  is_pinned_featured?: boolean;
  pinned_until?: string | null;
  focal_x?: number | null;
  focal_y?: number | null;
  img_w?: number | null;
  img_h?: number | null;
  social_embeds?: { platform: string; url: string }[] | null;
  reactions?: Record<string, number> | null;
  data_cards?: any[] | null;
  article_type?: string | null;
};

type P2Row = {
  id: string;
  slug: string | null;
  headline: string;
  subheadline: string | null;
  body?: string;

  vertical: string;
  category: string | null;
  status: string;
  is_featured: boolean | null;
  published_at: string | null;
  event_at?: string | null;
  updated_at?: string | null;
  created_at: string;
  sources?: unknown;
  diaspora_angle?: string | null;
  tags: string[] | null;
  image_url: string | null;
  image_attribution: string | null;
  image_caption: string | null;
  gallery_images: unknown;
  focal_x?: number | null;
  focal_y?: number | null;
  img_w?: number | null;
  img_h?: number | null;
  social_embeds?: { platform: string; url: string }[] | null;
  reactions?: Record<string, number> | null;
  data_cards?: any[] | null;
};

const P2_COLS =
  "id, slug, headline, subheadline, body, vertical, category, status, is_featured, published_at, event_at, created_at, updated_at, sources, diaspora_angle, tags, image_url, image_attribution, image_caption, gallery_images, display_score, focal_x, focal_y, img_w, img_h, social_embeds, reactions, data_cards";

const P2_LIST_COLS =
  "id, slug, headline, subheadline, vertical, category, status, is_featured, published_at, event_at, created_at, tags, image_url, image_attribution, image_caption, gallery_images, display_score, focal_x, focal_y, img_w, img_h, article_type";

function parseSources(raw: unknown): Article["sources"] {
  // Handle JSON array format
  if (raw && Array.isArray(raw)) {
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
  // Handle string format: JSON-encoded array or comma-separated names
  if (raw && typeof raw === "string") {
    const trimmed = (raw as string).trim();
    // Try JSON parse first (handles double-encoded JSONB)
    if (trimmed.startsWith("[")) {
      try {
        const parsed = JSON.parse(trimmed);
        if (Array.isArray(parsed)) return parseSources(parsed);
      } catch { /* fall through to comma-split */ }
    }
    const cleaned = trimmed.replace(/^\*?Sources?:\s*/i, "").replace(/\*$/,"").trim();
    if (!cleaned) return undefined;
    return cleaned.split(/,\s*/).map((s) => ({ label: s.trim() })).filter((s) => s.label);
  }
  return undefined;
}

function parseGalleryImages(raw: unknown): GalleryImage[] | null {
  if (!raw || !Array.isArray(raw) || raw.length === 0) return null;
  return raw
    .filter((item: any) => item && typeof item === "object" && typeof item.url === "string")
    .map((item: any) => ({ url: item.url, caption: item.caption || "" }));
}

function deriveExcerpt(subheadline: string | null, body: string): string {
  if (subheadline && subheadline.trim()) return subheadline.trim();
  // Strip HTML tags and markdown formatting, then take first complete sentence(s)
  const plain = (body ?? "")
    .replace(/<[^>]*>/g, " ")       // strip HTML tags
    .replace(/[#*_>`~\-]+/g, "")    // strip markdown
    .replace(/\s+/g, " ")           // collapse whitespace
    .trim();
  if (!plain) return "";
  if (plain.length <= 350) return plain;
  // Find last sentence-ending punctuation within 350 chars
  const window = plain.slice(0, 350);
  const lastPeriod = Math.max(
    window.lastIndexOf(". "),
    window.lastIndexOf("? "),
    window.lastIndexOf("! "),
  );
  if (lastPeriod > 120) return window.slice(0, lastPeriod + 1);
  // fallback: break at last space
  const lastSpace = window.lastIndexOf(" ");
  return (lastSpace > 0 ? window.slice(0, lastSpace) : window) + "…";
}

/* Strip trailing *Sources: ...* line baked into article body markdown */
function stripInlineSources(body: string): string {
  return body.replace(/\n*\*?Sources?:\s*[^*\n]+\*?\s*$/i, "").trim();
}

/** Turn raw sources column into a readable byline string. */
function formatAuthorFromSources(raw: unknown): string {
  if (!raw) return "Diaspora Desk";
  // If it's already a plain string that doesn't look like JSON, use it directly
  if (typeof raw === "string") {
    const trimmed = raw.trim();
    if (!trimmed) return "Diaspora Desk";
    // Handle Postgres array literal format: {"val1","val2"}
    if (trimmed.startsWith("{") && trimmed.endsWith("}") && !trimmed.startsWith("{\"")) {
      // Simple postgres array — split on comma
      const items = trimmed.slice(1, -1).split(",").map(s => s.replace(/^"|"$/g, "").trim()).filter(Boolean);
      return extractNames(items);
    }
    // Also handle postgres array with quoted URLs: {"url1","url2"}
    if (trimmed.startsWith("{\"") && trimmed.endsWith("\"}")) {
      const items = trimmed.slice(1, -1).split(/","/).map(s => s.replace(/^"|"$/g, "").trim()).filter(Boolean);
      return extractNames(items);
    }
    // Try to parse JSON
    try {
      const parsed = JSON.parse(trimmed);
      return extractNames(parsed);
    } catch {
      // Not JSON — use as-is (e.g. "Reuters")
      return trimmed;
    }
  }
  // Already parsed (array or object)
  return extractNames(raw);
}

function extractNames(parsed: unknown): string {
  if (Array.isArray(parsed)) {
    const names = parsed
      .map((s: any) => {
        const val = typeof s === "string" ? s : s?.name ?? "";
        if (!val) return "";
        // If it looks like a URL, extract a clean domain name
        if (/^https?:\/\//i.test(val)) {
          try {
            const host = new URL(val).hostname.replace(/^www\./, "");
            // Capitalize nicely: "ianslive.in" → "ianslive.in"
            return host;
          } catch {
            return "";
          }
        }
        return val;
      })
      .filter(Boolean);
    // Dedupe domains (same source may appear multiple times)
    const unique = [...new Set(names)];
    return unique.length > 0 ? unique.join(", ") : "Diaspora Desk";
  }
  if (typeof parsed === "object" && parsed !== null && "name" in (parsed as any)) {
    return (parsed as any).name || "Diaspora Desk";
  }
  return "Diaspora Desk";
}

function mapRow(row: P2Row): Article {
  return {
    id: row.id,
    slug: row.slug ?? row.id,
    title: row.headline,
    excerpt: deriveExcerpt(row.subheadline, row.body ?? ""),
    body: stripInlineSources(row.body ?? ""),
    category: row.category ?? row.vertical ?? "",
    hero_image_url: row.image_url ?? "",
    image_caption: row.image_caption ?? null,
    image_credit: row.image_attribution ?? null,
    gallery_images: parseGalleryImages(row.gallery_images),
    focal_x: row.focal_x ?? null,
    focal_y: row.focal_y ?? null,
    img_w: row.img_w ?? null,
    img_h: row.img_h ?? null,
    social_embeds: Array.isArray(row.social_embeds) ? row.social_embeds : [],
    reactions: (row as any).reactions ?? {},
    // expose raw attribution for callers that want it separately
    // (kept on image_credit too for backwards compat)
    published_at: row.published_at ?? row.created_at,
    event_at: row.event_at ?? null,
    updated_at: row.updated_at ?? row.published_at ?? row.created_at,
    created_at: row.created_at,
    status: row.status === "published" ? "published" : "draft",
    sources: parseSources(row.sources),
    nri_angle: row.diaspora_angle ?? undefined,
    article_type: (row.article_type as Article["article_type"]) ?? "news",
    tags: Array.isArray(row.tags) ? row.tags : undefined,
    author: formatAuthorFromSources(row.sources),
    featured_score: 0,
    is_pinned_featured: !!row.is_featured,
    pinned_until: null,
    data_cards: Array.isArray(row.data_cards) ? row.data_cards : null,
  };
}

export async function getFeaturedArticle(): Promise<Article | null> {
  // Cascading time windows so the hero never goes blank during pipeline gaps
  const windows = [24, 72, 7 * 24]; // hours

  for (const hours of windows) {
    const since = new Date(Date.now() - hours * 60 * 60 * 1000).toISOString();

    const buildBase = () =>
      supabase
        .from("p2_articles")
        .select(P2_COLS)
        .eq("status", "published")
        .gte("published_at", since)
        .not("tags", "cs", '{"who is"}')
        .order("display_score", { ascending: false, nullsFirst: false })
        .order("published_at", { ascending: false })
        .order("id", { ascending: true });

    // Try with image first
    const { data: withImage } = await buildBase()
      .not("image_url", "is", null)
      .neq("image_url", "")
      .limit(1)
      .maybeSingle();
    if (withImage) return mapRow(withImage as P2Row);

    // Fall back to any top article in this window
    const { data } = await buildBase().limit(1).maybeSingle();
    if (data) return mapRow(data as P2Row);
  }

  return null;
}

export function readingTime(markdown: string) {
  let text = (markdown ?? "").trim();
  // If body is JSON blocks, extract text content
  if (text.startsWith("[")) {
    try {
      const blocks = JSON.parse(text);
      if (Array.isArray(blocks)) {
        text = blocks.map((b: any) => b.text || b.content || "").join(" ");
      }
    } catch {}
  }
  const words = text.replace(/[#*_>`~\-\[\]{}]+/g, "").trim().split(/\s+/).filter(Boolean).length;
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
    .eq("is_featured", false)
    .order("published_at", { ascending: false })
    .order("id", { ascending: true })
    .limit(100);

  if (error) {
    console.error("[articles] getPublishedArticles", error);
    return [];
  }
  return (data as P2Row[]).map(mapRow);
}

export async function getTopStories(limit = 12, offset = 0): Promise<Article[]> {
  const since72h = new Date(Date.now() - 72 * 60 * 60 * 1000).toISOString();

  const { data, error } = await supabase
    .from("p2_articles")
    .select(P2_COLS)
    .eq("status", "published")
    .gte("published_at", since72h)
    .order("display_score", { ascending: false, nullsFirst: false })
    .order("published_at", { ascending: false })
    .range(offset, offset + limit - 1);
  if (error) {
    console.error("[articles] getTopStories", error);
    return [];
  }

  // Fallback: if fewer than 3 articles in 72h, widen to 7 days
  if ((data as P2Row[]).length < 3) {
    const since7d = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
    const { data: wider, error: widerErr } = await supabase
      .from("p2_articles")
      .select(P2_COLS)
      .eq("status", "published")
      .gte("published_at", since7d)
      .order("display_score", { ascending: false, nullsFirst: false })
      .order("published_at", { ascending: false })
      .range(offset, offset + limit - 1);
    if (!widerErr && (wider as P2Row[]).length > (data as P2Row[]).length) {
      return (wider as P2Row[]).map(mapRow);
    }
  }

  return (data as P2Row[]).map(mapRow);
}

export async function getArticleBySlug(slug: string): Promise<Article | null> {
  // Try by slug first
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
  if (data) return mapRow(data as P2Row);

  // Fallback: try by ID (handles articles with null slugs linked by UUID)
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (uuidRegex.test(slug)) {
    const { data: idData, error: idError } = await supabase
      .from("p2_articles")
      .select(P2_COLS)
      .eq("status", "published")
      .eq("id", slug)
      .maybeSingle();
    if (idError) {
      console.error("[articles] getArticleBySlug (id fallback)", idError);
      return null;
    }
    return idData ? mapRow(idData as P2Row) : null;
  }

  return null;
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

export async function searchArticles(query: string, limit = 30): Promise<Article[]> {
  // PostgREST uses * as the URL-safe wildcard in .or() filter strings (not %)
  const raw = query.trim();

  // Build a set of query variants so visa/abbreviation terms match regardless of
  // how the user types them. Articles consistently write "H-1B", "H-4", "EB-2",
  // "O-1" etc. with hyphens, but users search "h1b", "eb2", "o1" without.
  // We generate both a hyphen-stripped and a hyphen-inserted form and OR them all.
  const variants = new Set<string>();
  variants.add(raw);
  // collapse any spaces/hyphens between a letter-run and a digit-run: "h 1 b" -> "h1b"
  const collapsed = raw.replace(/\s+/g, " ");
  variants.add(collapsed);
  // strip hyphens entirely: "H-1B" -> "H1B", "EB-2" -> "EB2"
  variants.add(raw.replace(/-/g, ""));
  // insert a hyphen between a letter group and the following digit: "h1b" -> "h-1b", "eb2" -> "eb-2"
  variants.add(raw.replace(/([A-Za-z])(\d)/g, "$1-$2"));
  // also handle the trailing-letter visa forms like "h1-b" -> "h-1-b" is overkill;
  // the two forms above cover H1B<->H-1B and EB2<->EB-2 which are the common cases.

  const escapeLike = (s: string) => s.replace(/[*]/g, "");
  const orParts: string[] = [];
  for (const v of variants) {
    const t = escapeLike(v.trim());
    if (!t) continue;
    const q = `*${t}*`;
    orParts.push(`headline.ilike.${q}`, `subheadline.ilike.${q}`, `body.ilike.${q}`);
  }

  const { data, error } = await supabase
    .from("p2_articles")
    .select(P2_COLS)
    .eq("status", "published")
    .or(orParts.join(","))
    .order("published_at", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("[articles] searchArticles", error);
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
  const since72h = new Date(Date.now() - 72 * 60 * 60 * 1000).toISOString();

  const { data, error } = await supabase
    .from("p2_articles")
    .select(P2_LIST_COLS)
    .eq("status", "published")
    .eq("category", category)
    .gte("published_at", since72h)
    .order("display_score", { ascending: false, nullsFirst: false })
    .order("published_at", { ascending: false })
    .order("id", { ascending: true })
    .range(offset, offset + limit - 1);
  if (error) {
    console.error("[articles] getArticlesByCategory", error);
    return [];
  }

  // Fallback: if fewer than 3 articles in 72h, widen to 7 days
  if ((data as P2Row[]).length < 3) {
    const since7d = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
    const { data: wider, error: widerErr } = await supabase
      .from("p2_articles")
      .select(P2_LIST_COLS)
      .eq("status", "published")
      .eq("category", category)
      .gte("published_at", since7d)
      .order("display_score", { ascending: false, nullsFirst: false })
      .order("published_at", { ascending: false })
      .order("id", { ascending: true })
      .range(offset, offset + limit - 1);
    if (!widerErr && (wider as P2Row[]).length > (data as P2Row[]).length) {
      return (wider as P2Row[]).map(mapRow);
    }
  }

  return (data as P2Row[]).map(mapRow);
}

export async function fetchKidsArticles(limit = 20): Promise<Article[]> {
  const { data, error } = await supabase
    .from("p2_articles")
    .select(P2_COLS)
    .eq("status", "published")
    .eq("kids_relevant", true)
    .order("published_at", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("[articles] fetchKidsArticles", error);
    return [];
  }
  return (data as P2Row[]).map(mapRow);
}
