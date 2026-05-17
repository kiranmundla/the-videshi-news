import type { VercelRequest, VercelResponse } from "@vercel/node";

/**
 * Fetches post text from X (via oembed) or Threads (via og:description).
 * Query: ?url=https://x.com/user/status/123
 * Returns: { text, author_name, url, platform }
 */
export default async function handler(req: VercelRequest, res: VercelResponse) {
  const url = (req.query.url as string) || "";
  if (!url) return res.status(400).json({ error: "url required" });

  // Cache 4 hours
  res.setHeader("Cache-Control", "public, s-maxage=14400, stale-while-revalidate=3600");

  try {
    const isX = /^https?:\/\/(x\.com|twitter\.com)\//i.test(url);
    const isThreads = /^https?:\/\/(www\.)?threads\.(net|com)\//i.test(url);

    if (isX) {
      // Use X oembed API
      const oembedUrl = `https://publish.twitter.com/oembed?url=${encodeURIComponent(url)}&omit_script=true&hide_media=true&hide_thread=true`;
      const resp = await fetch(oembedUrl);
      if (!resp.ok) return res.status(502).json({ error: "oembed failed" });
      const data = await resp.json();
      // Extract text from HTML: <blockquote><p>TEXT</p>...
      const textMatch = (data.html || "").match(/<p[^>]*>([\s\S]*?)<\/p>/);
      const rawText = textMatch ? textMatch[1].replace(/<[^>]+>/g, "").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'").trim() : "";
      return res.json({
        text: rawText,
        author_name: data.author_name || "",
        author_url: data.author_url || "",
        url: data.url || url,
        platform: "x",
      });
    }

    if (isThreads) {
      // Fetch Threads post page and extract og:description
      const resp = await fetch(url, {
        headers: { "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" },
      });
      const html = await resp.text();
      const ogMatch = html.match(/property="og:description"\s+content="([^"]+)"/);
      const titleMatch = html.match(/property="og:title"\s+content="([^"]+)"/);
      const text = ogMatch ? ogMatch[1].replace(/&#064;/g, "@").replace(/&#x2022;/g, "•").replace(/&amp;/g, "&") : "";
      const author = titleMatch ? titleMatch[1].replace(/&#064;/g, "@") : "";
      // Threads returns generic text for unauthenticated requests
      const isGeneric = text.includes("Join Threads to share ideas");
      return res.json({
        text: isGeneric ? "" : text,
        author_name: author,
        url,
        platform: "threads",
      });
    }

    return res.status(400).json({ error: "unsupported platform" });
  } catch (err) {
    return res.status(500).json({ error: "fetch failed" });
  }
}
