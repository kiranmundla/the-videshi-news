// Vercel serverless function: serves fully-rendered article HTML for search engine bots.
// Includes full meta tags, JSON-LD, and article body so Googlebot can index immediately
// without waiting for client-side JS rendering.

export default async function handler(req, res) {
  const { slug } = req.query;
  if (!slug) return res.status(404).send("Not found");

  const supabaseUrl = process.env.VITE_SUPABASE_URL || process.env.SUPABASE_URL;
  const supabaseKey = process.env.VITE_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY;

  try {
    const resp = await fetch(
      `${supabaseUrl}/rest/v1/p2_articles?select=headline,subheadline,body,image_url,image_caption,slug,category,published_at,sources,is_editorial&slug=eq.${encodeURIComponent(slug)}&status=eq.published&limit=1`,
      { headers: { apikey: supabaseKey, Authorization: `Bearer ${supabaseKey}` } }
    );
    const rows = await resp.json();
    if (!rows || !rows.length) {
      // Check if article exists but is archived/unpublished → 410 Gone (faster deindexing)
      const checkResp = await fetch(
        `${supabaseUrl}/rest/v1/p2_articles?select=status,category&slug=eq.${encodeURIComponent(slug)}&limit=1`,
        { headers: { apikey: supabaseKey, Authorization: `Bearer ${supabaseKey}` } }
      );
      const checkRows = await checkResp.json();
      if (checkRows && checkRows.length && checkRows[0].status === "archived") {
        // Article was published then archived — tell Google it's permanently gone
        const cat = checkRows[0].category || "news";
        res.setHeader("Cache-Control", "public, s-maxage=86400");
        res.status(410).send(`<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Article Removed — The Videshi</title>
<meta name="robots" content="noindex"></head>
<body><h1>410 — This article has been removed</h1>
<p>Browse more stories: <a href="https://www.thevideshi.com/category/${cat}">${cat}</a> · <a href="https://www.thevideshi.com">Homepage</a></p></body></html>`);
        return;
      }
      // Truly doesn't exist — return proper 404 so Google doesn't soft-404
      res.status(404).send(`<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Article Not Found — The Videshi</title>
<meta name="robots" content="noindex"></head>
<body><h1>404 — Article not found</h1><p><a href="https://www.thevideshi.com">Back to homepage</a></p></body></html>`);
      return;
    }

    const a = rows[0];
    const title = a.headline || "The Videshi";
    const description = a.subheadline || "News for the global Indian diaspora";
    const image = a.image_url || "https://www.thevideshi.com/og-default.jpg";
    const url = `https://www.thevideshi.com/articles/${a.slug}`;
    const publishedAt = a.published_at || "";
    const category = a.category || "news";
    const author = a.is_editorial ? "Editor's Desk" : "Editor's Desk";

    // Convert markdown body to plain text for the prerender (strip markdown syntax)
    const bodyText = (a.body || "")
      .replace(/^#{1,6}\s+/gm, "")          // headers
      .replace(/\*\*(.*?)\*\*/g, "$1")       // bold
      .replace(/\*(.*?)\*/g, "$1")           // italic
      .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1") // links
      .replace(/!\[[^\]]*\]\([^)]*\)/g, "")  // images
      .replace(/^\s*[-*+]\s+/gm, "• ")       // list items
      .replace(/^\s*\d+\.\s+/gm, "")         // numbered lists
      .replace(/^>\s+/gm, "")                // blockquotes
      .replace(/```[\s\S]*?```/g, "")        // code blocks
      .replace(/`([^`]*)`/g, "$1")           // inline code
      .replace(/<[^>]+>/g, "")               // HTML tags
      .trim();

    // Split into paragraphs for readable HTML
    const paragraphs = bodyText.split(/\n{2,}/).filter(p => p.trim());
    const bodyHtml = paragraphs.map(p => `<p>${p.trim()}</p>`).join("\n");

    // JSON-LD structured data
    const jsonLd = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "NewsArticle",
      headline: title,
      description: description,
      image: image,
      datePublished: publishedAt,
      author: { "@type": "Organization", name: "The Videshi" },
      publisher: {
        "@type": "Organization",
        name: "The Videshi",
        logo: { "@type": "ImageObject", url: "https://www.thevideshi.com/logo.png" },
      },
      mainEntityOfPage: { "@type": "WebPage", "@id": url },
    });

    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.setHeader("Cache-Control", "s-maxage=3600, stale-while-revalidate=86400");
    res.status(200).send(`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${esc(title)} — The Videshi</title>
<meta name="description" content="${esc(description)}">
<meta name="author" content="${esc(author)}">

<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:type" content="article">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${esc(image)}">
<meta property="og:site_name" content="The Videshi">
<meta property="article:published_time" content="${publishedAt}">
<meta property="article:section" content="${esc(category)}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:description" content="${esc(description)}">
<meta name="twitter:image" content="${esc(image)}">

<link rel="canonical" href="${url}">
<script type="application/ld+json">${jsonLd}</script>
</head>
<body>
<header>
  <h1><a href="https://www.thevideshi.com">The Videshi</a></h1>
  <p>News for the global Indian diaspora</p>
</header>
<article>
  <h1>${esc(title)}</h1>
  ${description ? `<p><em>${esc(description)}</em></p>` : ""}
  ${image ? `<img src="${esc(image)}" alt="${esc(title)}"${a.image_caption ? ` title="${esc(a.image_caption)}"` : ""}>` : ""}
  <p>By ${esc(author)} · ${publishedAt ? new Date(publishedAt).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" }) : ""}</p>
  ${bodyHtml}
</article>
<footer>
  <p>&copy; The Videshi. <a href="https://www.thevideshi.com">Homepage</a></p>
</footer>
</body>
</html>`);
  } catch (e) {
    res.status(500).send("Error");
  }
}

function esc(s) {
  return (s || "")
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
