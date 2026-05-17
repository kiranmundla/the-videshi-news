import type { VercelRequest, VercelResponse } from "@vercel/node";

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const { shortcode } = req.query;
  if (!shortcode || typeof shortcode !== "string") {
    return res.status(400).json({ error: "shortcode required" });
  }

  try {
    // Fetch the regular post page (not /embed/) — og:image has the real CDN URL
    const response = await fetch(
      `https://www.instagram.com/p/${shortcode}/`,
      {
        headers: {
          "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        },
      }
    );
    if (!response.ok) {
      return res.status(502).json({ error: `instagram returned ${response.status}` });
    }
    const html = await response.text();

    let imageUrl = "";

    // og:image from the post page — this is the actual CDN image
    const ogMatch = html.match(
      /property="og:image"\s*content="([^"]+)"/
    );
    if (ogMatch) {
      imageUrl = ogMatch[1].replace(/&amp;/g, "&");
    }

    // Fallback: any scontent CDN URL
    if (!imageUrl) {
      const cdnMatch = html.match(
        /src="(https:\/\/scontent[^"]+cdninstagram\.com[^"]+)"/
      );
      if (cdnMatch) {
        imageUrl = cdnMatch[1].replace(/&amp;/g, "&");
      }
    }

    if (!imageUrl) {
      return res.status(404).json({ error: "image not found" });
    }

    // Cache for 4 hours on Vercel edge
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
