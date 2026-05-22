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
  { loc: "/events", priority: "0.8", changefreq: "daily" },
  { loc: "/events/submit", priority: "0.5", changefreq: "monthly" },
  { loc: "/directory", priority: "0.8", changefreq: "daily" },
  { loc: "/directory/submit", priority: "0.5", changefreq: "monthly" },
  { loc: "/about", priority: "0.5", changefreq: "monthly" },
  { loc: "/contact", priority: "0.5", changefreq: "monthly" },
  { loc: "/privacy", priority: "0.3", changefreq: "yearly" },
  { loc: "/terms", priority: "0.3", changefreq: "yearly" },
  { loc: "/travel", priority: "0.7", changefreq: "weekly" },
];

const CATEGORIES = [
  "news", "nri-world", "travel", "lifestyle-health",
  "markets-finance", "technology", "sports", "entertainment", "food"
];

const escapeXml = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

async function fetchAll(table: string, select: string, filters?: string): Promise<any[]> {
  const all: any[] = [];
  let offset = 0;
  const limit = 1000;
  while (true) {
    const filterStr = filters ? `&${filters}` : "";
    const res = await fetch(
      `${SUPABASE_URL}/rest/v1/${table}?select=${select}${filterStr}&limit=${limit}&offset=${offset}`,
      {
        headers: {
          apikey: SUPABASE_ANON_KEY,
          Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
        },
      }
    );
    if (!res.ok) break;
    const batch = await res.json();
    if (!Array.isArray(batch) || batch.length === 0) break;
    all.push(...batch);
    if (batch.length < limit) break;
    offset += limit;
  }
  return all;
}

export default async function handler(_req: VercelRequest, res: VercelResponse) {
  try {
    const now = new Date().toISOString();
    const today = now.split("T")[0];

    // Fetch all data in parallel
    const [articles, events, listings] = await Promise.all([
      fetchAll("p2_articles", "slug,published_at,category", "status=eq.published&order=published_at.desc"),
      fetchAll("events", "slug,date,updated_at", `date=gte.${today}&order=date.asc`),
      fetchAll("directory_listings", "slug,updated_at", "order=updated_at.desc"),
    ]);

    let xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
`;

    // Static pages
    for (const page of STATIC_PAGES) {
      xml += `  <url>
    <loc>${escapeXml(SITE + page.loc)}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>
`;
    }

    // Category pages
    for (const cat of CATEGORIES) {
      xml += `  <url>
    <loc>${escapeXml(SITE + "/category/" + cat)}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.6</priority>
  </url>
`;
    }

    // Article pages
    for (const article of articles) {
      if (!article.slug) continue;
      const pubDate = article.published_at
        ? new Date(article.published_at).toISOString()
        : now;
      const isRecent =
        Date.now() - new Date(pubDate).getTime() < 2 * 24 * 60 * 60 * 1000;

      xml += `  <url>
    <loc>${escapeXml(SITE + "/articles/" + article.slug)}</loc>
    <lastmod>${pubDate.split("T")[0]}</lastmod>
    <changefreq>${isRecent ? "hourly" : "weekly"}</changefreq>
    <priority>${isRecent ? "0.9" : "0.7"}</priority>
  </url>
`;
    }

    // Event pages
    for (const event of events) {
      if (!event.slug) continue;
      const lastmod = event.updated_at
        ? new Date(event.updated_at).toISOString().split("T")[0]
        : today;
      xml += `  <url>
    <loc>${escapeXml(SITE + "/events/" + event.slug)}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
`;
    }

    // Directory listing pages
    for (const listing of listings) {
      if (!listing.slug) continue;
      const lastmod = listing.updated_at
        ? new Date(listing.updated_at).toISOString().split("T")[0]
        : today;
      xml += `  <url>
    <loc>${escapeXml(SITE + "/directory/" + listing.slug)}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
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
