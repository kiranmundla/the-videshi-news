import type { VercelRequest, VercelResponse } from "@vercel/node";

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const { shortcode } = req.query;
  if (!shortcode || typeof shortcode !== "string") {
    return res.status(400).json({ error: "shortcode required" });
  }

  try {
    // Googlebot UA on embed page returns actual post image CDN URLs
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

    // Look for post images (t51.82787) not profile pics (t51.2885-19)
    // Match the largest srcset image (1080w)
    const srcsetMatch = html.match(
      /(https:\/\/scontent[^"'\s]+t51\.82787[^"'\s]+1080w)/
    );
    if (srcsetMatch) {
      imageUrl = srcsetMatch[1]
        .replace(/\s+\d+w$/, "")
        .replace(/&amp;/g, "&");
    }

    // Fallback: any post image CDN URL (not profile pic)
    if (!imageUrl) {
      const cdnMatch = html.match(
        /src="(https:\/\/scontent[^"]+t51\.82787[^"]+)"/
      );
      if (cdnMatch) {
        imageUrl = cdnMatch[1].replace(/&amp;/g, "&");
      }
    }

    // Fallback: any scontent CDN URL that's not a profile pic (s150x150)
    if (!imageUrl) {
      const anyMatch = html.match(
        /(?:src|content)="(https:\/\/scontent[^"]+cdninstagram\.com[^"]+)"/
      );
      if (anyMatch && !anyMatch[1].includes("s150x150")) {
        imageUrl = anyMatch[1].replace(/&amp;/g, "&");
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
