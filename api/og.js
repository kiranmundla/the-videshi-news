// Vercel serverless function: serves OG meta tags for WhatsApp/Twitter/Facebook crawlers
export default async function handler(req, res) {
  const { slug } = req.query;
  if (!slug) return res.status(404).send("Not found");

  // Fetch article from Supabase
  const supabaseUrl = process.env.VITE_SUPABASE_URL || process.env.SUPABASE_URL;
  const supabaseKey = process.env.VITE_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY;

  try {
    const resp = await fetch(
      `${supabaseUrl}/rest/v1/p2_articles?select=headline,subheadline,image_url,slug&slug=eq.${encodeURIComponent(slug)}&status=eq.published&limit=1`,
      { headers: { apikey: supabaseKey, Authorization: `Bearer ${supabaseKey}` } }
    );
    const rows = await resp.json();
    if (!rows || !rows.length) return res.status(404).send("Not found");

    const article = rows[0];
    const title = article.headline || "The Videshi";
    const description = article.subheadline || "News for the global Indian diaspora";
    const image = article.image_url || "";
    const url = `https://www.thevideshi.com/articles/${article.slug}`;

    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.status(200).send(`<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>${title} — The Videshi</title>
<meta property="og:title" content="${title}" />
<meta property="og:description" content="${description}" />
<meta property="og:type" content="article" />
<meta property="og:url" content="${url}" />
${image ? `<meta property="og:image" content="${image}" />` : ""}
<meta property="og:site_name" content="The Videshi" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="${title}" />
<meta name="twitter:description" content="${description}" />
${image ? `<meta name="twitter:image" content="${image}" />` : ""}
<meta http-equiv="refresh" content="0;url=${url}" />
</head>
<body></body>
</html>`);
  } catch (e) {
    res.status(500).send("Error");
  }
}
