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
    const raw = await response.text();
    const html = raw.replace(/&amp;/g, "&");

    // Extract all post images (t51.82787 = photo posts)
    const allUrls = html.match(/https:\/\/scontent[^"'\s,>]+t51\.82787[^"'\s,>]*/g) || [];

    // Dedupe by base filename (before query params), prefer largest size
    const byBase = new Map<string, string>();
    for (const url of allUrls) {
      const base = url.split("?")[0];
      const existing = byBase.get(base);
      if (!existing) {
        byBase.set(base, url);
      } else {
        // Prefer p1080 > p750 > p640 > others
        const sizeScore = (u: string) => {
          if (u.includes("p1080x1080")) return 3;
          if (u.includes("p750x750")) return 2;
          if (u.includes("p640x640")) return 1;
          if (u.includes("s150x150") || u.includes("s240x240")) return -1;
          return 0;
        };
        if (sizeScore(url) > sizeScore(existing)) {
          byBase.set(base, url);
        }
      }
    }

    // Filter out tiny thumbnails, dedupe by image ID (the numeric part of filename)
    const imageIdSeen = new Set<string>();
    const images: string[] = [];
    for (const url of byBase.values()) {
      if (url.includes("s150x150") || url.includes("s240x240")) continue;
      // Extract image ID from filename like 696527953_18461734879118856_...
      const idMatch = url.match(/\/([0-9]+_[0-9]+_[0-9]+_n\.jpg)/);
      const imageId = idMatch ? idMatch[1] : url.split("?")[0];
      if (imageIdSeen.has(imageId)) continue;
      imageIdSeen.add(imageId);
      images.push(url);
    }

    if (!images.length) {
      // Fallback: try video thumbnails (t51.71878)
      const vidUrls = html.match(/https:\/\/scontent[^"'\s,>]+t51\.71878[^"'\s,>]*/g) || [];
      for (const url of vidUrls) {
        if (!url.includes("s150x150") && !url.includes("s240x240")) {
          images.push(url);
          break;
        }
      }
    }

    if (!images.length) {
      return res.status(404).json({ error: "no images found" });
    }

    res.setHeader("Cache-Control", "s-maxage=14400, stale-while-revalidate=3600");
    res.setHeader("Access-Control-Allow-Origin", "*");
    return res.json({ url: images[0], images });
  } catch (e: unknown) {
    const message = e instanceof Error ? e.message : "unknown error";
    return res.status(500).json({ error: message });
  }
}
