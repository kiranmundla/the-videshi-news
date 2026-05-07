import { next } from "@vercel/edge";

export const config = {
  matcher: "/articles/:slug*",
};

// Public Supabase project URL + anon key (safe to expose; same as src client)
const SUPABASE_URL =
  process.env.VITE_SUPABASE_URL ??
  process.env.SUPABASE_URL ??
  "https://lboecaekpynbpyijrbfz.supabase.co";
const SUPABASE_ANON_KEY =
  process.env.VITE_SUPABASE_PUBLISHABLE_KEY ??
  process.env.SUPABASE_ANON_KEY ??
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxib2VjYWVrcHluYnB5aWpyYmZ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc5NDc2NzQsImV4cCI6MjA5MzUyMzY3NH0.i2_CzXJEnIT2SZ9mx0j5OHh4rqewPwiLUogSrdM4HXY";

const escapeHtml = (s: string) =>
  s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

const escapeAttr = (s: string) => escapeHtml(s);

type Article = {
  title: string;
  summary: string | null;
  image_url: string | null;
  slug: string | null;
};

async function fetchArticle(slug: string): Promise<Article | null> {
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) return null;
  try {
    const url = `${SUPABASE_URL}/rest/v1/articles?select=title,summary,image_url,slug&slug=eq.${encodeURIComponent(
      slug
    )}&is_published=eq.true&limit=1`;
    const res = await fetch(url, {
      headers: {
        apikey: SUPABASE_ANON_KEY,
        Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
      },
    });
    if (!res.ok) return null;
    const rows = (await res.json()) as Article[];
    return rows[0] ?? null;
  } catch {
    return null;
  }
}

function injectMeta(html: string, article: Article, canonical: string, origin: string): string {
  const title = escapeHtml(`${article.title} — The Videshi`);
  const desc = escapeAttr((article.summary ?? "").slice(0, 300));
  const rawImage = article.image_url && article.image_url.trim().length > 0
    ? article.image_url
    : `${origin}/og-default.jpg`;
  const image = escapeAttr(rawImage);

  // Replace <title>
  let out = html.replace(/<title>[\s\S]*?<\/title>/i, `<title>${title}</title>`);

  // Remove existing description / og / twitter tags we will re-inject
  out = out.replace(
    /<meta\s+(?:name|property)=["'](?:description|og:title|og:description|og:type|og:image|og:url|twitter:card|twitter:title|twitter:description|twitter:image)["'][^>]*>\s*/gi,
    ""
  );

  const tags = [
    `<meta name="description" content="${desc}" />`,
    `<meta property="og:title" content="${escapeAttr(article.title)}" />`,
    `<meta property="og:description" content="${desc}" />`,
    `<meta property="og:type" content="article" />`,
    `<meta property="og:url" content="${escapeAttr(canonical)}" />`,
    image ? `<meta property="og:image" content="${image}" />` : "",
    `<meta name="twitter:card" content="summary_large_image" />`,
    `<meta name="twitter:title" content="${escapeAttr(article.title)}" />`,
    `<meta name="twitter:description" content="${desc}" />`,
    image ? `<meta name="twitter:image" content="${image}" />` : "",
  ]
    .filter(Boolean)
    .join("\n    ");

  out = out.replace(/<\/head>/i, `    ${tags}\n  </head>`);
  return out;
}

export default async function middleware(request: Request) {
  const url = new URL(request.url);
  const match = url.pathname.match(/^\/articles\/([^/]+)\/?$/);
  if (!match) return next();

  const slug = decodeURIComponent(match[1]);
  const article = await fetchArticle(slug);
  if (!article) return next();

  // Fetch the static index.html shell
  const shellRes = await fetch(new URL("/index.html", url.origin), {
    headers: { "x-middleware-shell": "1" },
  });
  if (!shellRes.ok) return next();
  const html = await shellRes.text();

  const canonical = `${url.origin}/articles/${article.slug ?? slug}`;
  const transformed = injectMeta(html, article, canonical);

  return new Response(transformed, {
    status: 200,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "public, max-age=0, s-maxage=300, stale-while-revalidate=86400",
    },
  });
}
