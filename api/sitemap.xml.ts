import type { VercelRequest, VercelResponse } from "@vercel/node";

const SUPABASE_URL =
  process.env.VITE_SUPABASE_URL ??
  process.env.SUPABASE_URL ??
  "https://lboecaekpynbpyijrbfz.supabase.co";
const SUPABASE_ANON_KEY =
  process.env.VITE_SUPABASE_PUBLISHABLE_KEY ??
  process.env.SUPABASE_ANON_KEY ??
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxib2VjYWVrcHluYnB5aWpyYmZ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc5NDc2NzQsImV4cCI6MjA5MzUyMzY3NH0.i2_CzXJEnIT2SZ9mx0j5OHh4rqewPwiLUogSrdM4HXY";

const SITE = "https://www.thevideshi.com";

const STATIC_PAGES = [
  { loc: "/", priority: "1.0", changefreq: "hourly" },
  { loc: "/events", priority: "0.8", changefreq: "daily" },
  { loc: "/festivals", priority: "0.8", changefreq: "daily" },
  { loc: "/your-hub", priority: "0.8", changefreq: "daily" },
  { loc: "/directory", priority: "0.8", changefreq: "daily" },
  { loc: "/classifieds", priority: "0.7", changefreq: "daily" },
  { loc: "/about", priority: "0.5", changefreq: "monthly" },
  { loc: "/contact", priority: "0.5", changefreq: "monthly" },
  { loc: "/privacy", priority: "0.3", changefreq: "yearly" },
  { loc: "/terms", priority: "0.3", changefreq: "yearly" },
  { loc: "/travel", priority: "0.7", changefreq: "weekly" },
  { loc: "/immigration", priority: "0.8", changefreq: "daily" },
  { loc: "/immigration/h1b", priority: "0.7", changefreq: "daily" },
  { loc: "/immigration/green-card", priority: "0.7", changefreq: "daily" },
  { loc: "/immigration/students", priority: "0.7", changefreq: "daily" },
  { loc: "/immigration/policy", priority: "0.7", changefreq: "daily" },
  { loc: "/immigration/consular", priority: "0.7", changefreq: "daily" },
  { loc: "/technology", priority: "0.8", changefreq: "daily" },
  { loc: "/technology/ai", priority: "0.7", changefreq: "daily" },
  { loc: "/technology/big-tech", priority: "0.7", changefreq: "daily" },
  { loc: "/technology/semiconductors", priority: "0.7", changefreq: "daily" },
  { loc: "/technology/startups", priority: "0.7", changefreq: "daily" },
  { loc: "/technology/indian-it", priority: "0.7", changefreq: "daily" },
  { loc: "/stories", priority: "0.6", changefreq: "weekly" },
  { loc: "/world-cup", priority: "0.9", changefreq: "hourly" },
  { loc: "/kids", priority: "0.8", changefreq: "weekly" },
  { loc: "/kids/guides/math-competitions", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/spelling-bee", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/getting-into-robotics", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/chess-for-kids", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/coding-for-kids", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/tennis-for-kids", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/cricket-in-the-us", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/debate-and-public-speaking", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/indian-dance-for-kids", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/music-education-for-kids", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/science-olympiad-and-stem", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/youth-sports-in-the-us", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/sat-act-prep", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/college-counseling-guide", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/volunteering-and-community-service", priority: "0.7", changefreq: "monthly" },
  { loc: "/kids/guides/heritage-language-programs", priority: "0.7", changefreq: "monthly" },
];

const CATEGORIES = [
  "news", "nri-world", "lifestyle-health",
  "markets-finance", "sports", "entertainment", "food"
];
// NOTE: "travel" is NOT in CATEGORIES — /travel already ships in
// STATIC_PAGES, and listing it in both emitted the URL twice
// (found in the 2026-10-21 sitemap audit).

// Travel destination pages (/travel/<slug>) — the sitemap generator
// originally had NO source for these, so all 50 guide pages and
// /travel/india were missing from the sitemap (2026-10-21 audit).
// The handler fetches the site's own travel-destinations.json first;
// this list is the fallback if that fetch fails.
const TRAVEL_FALLBACK_SLUGS = [
  "abu-dhabi", "alaska", "aruba", "australia", "bahamas", "bali", "banff",
  "cabo", "cancun", "dominican-republic", "dubai", "egypt", "fiji",
  "florida", "france", "goa", "greece", "hawaii", "himachal-pradesh",
  "iceland", "italy", "jamaica", "japan", "karnataka", "kashmir", "kenya",
  "kerala", "london", "maldives", "mexico", "morocco", "national-parks",
  "new-york-city", "new-zealand", "northeast-india", "oman", "portugal",
  "puerto-vallarta", "rajasthan", "riviera-maya", "scandinavia",
  "singapore", "south-africa", "spain", "sri-lanka", "switzerland",
  "tamil-nadu", "thailand", "uttarakhand", "vietnam",
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

    // Fetch articles, future events, directory listings, and classifieds
    // Removed: cars (dead section), past events (404 crawl waste)
    // Kept: directory (real business listings with structured data) and
    // classifieds (active listings) — potential long-tail SEO value
    const [articles, events, listings, classifieds] = await Promise.all([
      fetchAll("p2_articles", "slug,headline,published_at,category", "status=eq.published&order=published_at.desc"),
      fetchAll("events", "slug,date,updated_at", `date=gte.${today}&order=date.desc`),
      fetchAll("directory_listings", "slug,updated_at", "order=updated_at.desc"),
      fetchAll("classifieds", "slug,updated_at", `status=eq.active&expires_at=gte.${now}&order=created_at.desc`),
    ]);

    let xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
`;

    // Duplicate guard (2026-10-21 audit found 8 duplicated URLs: /travel
    // in two lists, plus articles/listings whose rows share a slug).
    const seen = new Set<string>();
    const fresh = (loc: string) => {
      if (seen.has(loc)) return false;
      seen.add(loc);
      return true;
    };

    // Static pages
    for (const page of STATIC_PAGES) {
      if (!fresh(page.loc)) continue;
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
      if (!fresh("/" + cat)) continue;
      xml += `  <url>
    <loc>${escapeXml(SITE + "/" + cat)}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.6</priority>
  </url>
`;
    }

    // Travel destination pages + the India hub (added 2026-10-21 — these
    // were entirely absent from the sitemap).
    let travelSlugs = TRAVEL_FALLBACK_SLUGS;
    try {
      const tdRes = await fetch(`${SITE}/data/travel-destinations.json`);
      if (tdRes.ok) {
        const td = await tdRes.json();
        const fromFile = (td?.destinations ?? [])
          .map((d: any) => d?.slug)
          .filter((s: any) => typeof s === "string" && s.length > 0);
        if (fromFile.length > 0) travelSlugs = fromFile;
      }
    } catch {
      // keep the fallback list
    }
    for (const loc of ["/travel/india", ...travelSlugs.map((s) => `/travel/${s}`)]) {
      if (!fresh(loc)) continue;
      xml += `  <url>
    <loc>${escapeXml(SITE + loc)}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
`;
    }

    // Article pages
    for (const article of articles) {
      if (!article.slug) continue;
      if (!fresh("/articles/" + article.slug)) continue;
      const pubDate = article.published_at
        ? new Date(article.published_at).toISOString()
        : now;
      const isRecent =
        Date.now() - new Date(pubDate).getTime() < 2 * 24 * 60 * 60 * 1000;

      xml += `  <url>
    <loc>${escapeXml(SITE + "/articles/" + article.slug)}</loc>
    <lastmod>${pubDate.split("T")[0]}</lastmod>
    <changefreq>${isRecent ? "hourly" : "weekly"}</changefreq>
    <priority>${isRecent ? "0.9" : "0.7"}</priority>${isRecent && article.headline ? `
    <news:news>
      <news:publication>
        <news:name>The Videshi</news:name>
        <news:language>en</news:language>
      </news:publication>
      <news:publication_date>${pubDate}</news:publication_date>
      <news:title>${escapeXml(article.headline)}</news:title>
    </news:news>` : ""}
  </url>
`;
    }

    // Event pages (future events only — past events removed from sitemap
    // to stop 404 crawl waste)
    for (const event of events) {
      if (!event.slug) continue;
      if (!fresh("/events/" + event.slug)) continue;
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

    // Directory listing pages — real business listings with structured
    // data (address, hours, phone, photos, ratings). Long-tail SEO
    // value for "Indian [profession] in [city]" searches.
    for (const listing of listings) {
      if (!listing.slug) continue;
      if (!fresh("/directory/" + listing.slug)) continue;
      const lastmod = listing.updated_at
        ? new Date(listing.updated_at).toISOString().split("T")[0]
        : today;
      xml += `  <url>
    <loc>${escapeXml(SITE + "/directory/" + listing.slug)}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
`;
    }

    // Classified pages (active only)
    for (const classified of classifieds) {
      if (!classified.slug) continue;
      if (!fresh("/classifieds/" + classified.slug)) continue;
      const lastmod = classified.updated_at
        ? new Date(classified.updated_at).toISOString().split("T")[0]
        : today;
      xml += `  <url>
    <loc>${escapeXml(SITE + "/classifieds/" + classified.slug)}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.5</priority>
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
