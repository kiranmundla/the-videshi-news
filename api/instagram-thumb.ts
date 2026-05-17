import type { VercelRequest, VercelResponse } from "@vercel/node";

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const { shortcode } = req.query;
  if (!shortcode || typeof shortcode !== "string") {
    return res.status(400).json({ error: "shortcode required" });
  }

  try {
    const response = await fetch(
      `https://www.instagram.com/p/${shortcode}/embed/`,
      {
        headers: {
          "User-Agent":
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        },
      }
    );
    if (!response.ok) {
      return res.status(502).json({ error: `instagram returned ${response.status}` });
    }
    const html = await response.text();

    let imageUrl = "";

    // Try EmbeddedMediaImage first (most reliable for the actual post photo)
    const embedMatch = html.match(
      /class="EmbeddedMediaImage"[^>]*src="([^"]+)"/
    );
    if (embedMatch) {
      imageUrl = embedMatch[1].replace(/&amp;/g, "&");
    }

    // Fallback: og:image meta tag
    if (!imageUrl) {
      const ogMatch = html.match(
        /property="og:image"\s*content="([^"]+)"/
      );
      if (ogMatch) {
        imageUrl = ogMatch[1].replace(/&amp;/g, "&");
      }
    }

    // Fallback: any img with instagramCDN URL
    if (!imageUrl) {
      const cdnMatch = html.match(
        /src="(https:\/\/scontent[^"]+cdninstagram\.com[^"]+)"/
      );
      if (cdnMatch) {
        imageUrl = cdnMatch[1].replace(/&amp;/g, "&");
      }
    }

    if (!imageUrl) {
      return res.status(404).json({ error: "image not found in embed page" });
    }

    // Cache for 4 hours on Vercel edge, allow stale-while-revalidate for 1 hour
    res.setHeader(
      "Cache-Control",
      "s-maxage=14400, stale-while-revalidate=3600"
    );
    res.setHeader("Access-Control-Allow-Origin", "*");
    return res.json({ url: imageUrl });
  } catch (e: unknown) {
    const message = e instanceof Error ? e.message : "unknown error";
    return res.status(500).json({ error: message });
  }
}
