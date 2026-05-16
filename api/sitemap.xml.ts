import type { VercelRequest, VercelResponse } from "@vercel/node";

const SUPABASE_URL =
  process.env.VITE_SUPABASE_URL ??
  process.env.SUPABASE_URL ??
  "https://lboecaekpynbpyijrbfz.supabase.co";
const SUPABASE_ANON_KEY =
  process.env.VITE_SUPABASE_PUBLISHABLE_KEY ??
  process.env.SUPABASE_ANON_KEY ??
  "";

const SITE = "https://www.thevideshi.com";

const STATIC_PAGES = [
  { loc: "/", priority: "1.0", changefreq: "hourly" },
  { loc: "/travel", priority: "0.7", changefreq: "weekly" },
];

const CATEGORIES = [
  "news", "nri-world", "travel", "lifestyle-health",
  "markets-finance", "technology", "sports", "entertainment", "food"
];

const escapeXml = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export default async function handler(_req: VercelRequest, res: VercelResponse) {
  try {
    // Fetch all published articles
    const articlesRes = await fetch(
      `${SUPABASE_URL}/rest/v1/p2_articles?select=slug,published_at,category&status=eq.published&order=published_at.desc&limit=1000`,
      {
        headers: {
          apikey: SUPABASE_ANON_KEY,
          Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
        },
      }
    );

    const articles = articlesRes.ok ? await articlesRes.json() : [];
    const now = new Date().toISOString();

    let xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
`;

    // Static pages
    for (const page of STATIC_PAGES) {
      xml += `  <url>
    <loc>${escapeXml(SITE + page.loc)}</loc>
    <lastmod>${now.split("T")[0]}</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>
`;
    }

    // Category pages
    for (const cat of CATEGORIES) {
      xml += `  <url>
    <loc>${escapeXml(SITE + "/category/" + cat)}</loc>
    <lastmod>${now.split("T")[0]}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.6</priority>
  </url>
`;
    }

    // Article pages with Google News extension
    for (const article of articles) {
      if (!article.slug) continue;
      const pubDate = article.published_at
        ? new Date(article.published_at).toISOString()
        : now;
      const isRecent =
        Date.now() - new Date(pubDate).getTime() < 2 * 24 * 60 * 60 * 1000; // 2 days

      xml += `  <url>
    <loc>${escapeXml(SITE + "/articles/" + article.slug)}</loc>
    <lastmod>${pubDate.split("T")[0]}</lastmod>
    <changefreq>${isRecent ? "hourly" : "weekly"}</changefreq>
    <priority>${isRecent ? "0.9" : "0.7"}</priority>
  </url>
`;
    }

    xml += `</urlset>`;

    res.setHeader("Content-Type", "application/xml; charset=utf-8");
    res.setHeader("Cache-Control", "public, s-maxage=3600, stale-while-revalidate=86400");
    res.status(200).send(xml);
  } catch (e) {
    res.status(500).send("<?xml version=\"1.0\"?><urlset></urlset>");
  }
}
