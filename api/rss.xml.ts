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

const escapeXml = (s: string) =>
  s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");

export default async function handler(_req: VercelRequest, res: VercelResponse) {
  try {
    const articlesRes = await fetch(
      `${SUPABASE_URL}/rest/v1/p2_articles?select=slug,headline,subheadline,published_at,image_url,category&status=eq.published&order=published_at.desc&limit=50`,
      {
        headers: {
          apikey: SUPABASE_ANON_KEY,
          Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
        },
      }
    );

    const articles = articlesRes.ok ? await articlesRes.json() : [];
    const now = new Date().toUTCString();

    let xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>The Videshi</title>
    <link>${SITE}</link>
    <description>News for the global Indian diaspora — India, NRI affairs, US-India, business, culture, and voices.</description>
    <language>en-us</language>
    <lastBuildDate>${now}</lastBuildDate>
    <atom:link href="${SITE}/rss.xml" rel="self" type="application/rss+xml" />
    <image>
      <url>${SITE}/og-default.jpg</url>
      <title>The Videshi</title>
      <link>${SITE}</link>
    </image>
`;

    for (const article of articles) {
      if (!article.slug) continue;
      const pubDate = article.published_at
        ? new Date(article.published_at).toUTCString()
        : now;
      const link = `${SITE}/articles/${article.slug}`;
      const title = escapeXml(article.headline || "");
      const desc = escapeXml((article.subheadline || "").slice(0, 500));
      const category = article.category ? `<category>${escapeXml(article.category)}</category>` : "";
      const imageTag = article.image_url
        ? `<media:content url="${escapeXml(article.image_url)}" medium="image" />`
        : "";

      xml += `    <item>
      <title>${title}</title>
      <link>${link}</link>
      <guid isPermaLink="true">${link}</guid>
      <description>${desc}</description>
      <pubDate>${pubDate}</pubDate>
      ${category}
      ${imageTag}
    </item>
`;
    }

    xml += `  </channel>
</rss>`;

    res.setHeader("Content-Type", "application/rss+xml; charset=utf-8");
    res.setHeader("Cache-Control", "public, s-maxage=1800, stale-while-revalidate=86400");
    res.status(200).send(xml);
  } catch (e) {
    res.status(500).send('<?xml version="1.0"?><rss version="2.0"><channel><title>Error</title></channel></rss>');
  }
}
