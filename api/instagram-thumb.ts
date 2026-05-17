import type { VercelRequest, VercelResponse } from "@vercel/node";

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const { shortcode } = req.query;
  if (!shortcode || typeof shortcode !== "string") {
    return res.status(400).json({ error: "shortcode required" });
  }

  try {
    // Fetch the actual post page (not embed) — returns all carousel images
    const response = await fetch(
      `https://www.instagram.com/p/${shortcode}/`,
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
    const html = raw.replace(/&amp;/g, "&").replace(/\\u0026/g, "&");

    // Extract all post images (t51.82787 = photo posts)
    const allUrls = html.match(/https:\/\/scontent[^"'\s,>\\]+t51\.82787[^"'\s,>\\]*/g) || [];

    // Dedupe by image ID (filename), keep largest version of each
    const byImageId = new Map<string, string>();
    for (const url of allUrls) {
      const idMatch = url.match(/\/([0-9]+_[0-9]+_[0-9]+_n\.jpg)/);
      if (!idMatch) continue;
      const imageId = idMatch[1];

      // Skip tiny thumbnails
      if (url.includes("s150x150") || url.includes("s240x240")) continue;

      const existing = byImageId.get(imageId);
      if (!existing) {
        byImageId.set(imageId, url);
      } else {
        // Prefer larger sizes
        const sizeScore = (u: string) => {
          if (u.includes("p1080x1080")) return 3;
          if (u.includes("p750x750")) return 2;
          if (u.includes("p640x640")) return 1;
          return 4; // original/unlabeled = likely full size
        };
        if (sizeScore(url) > sizeScore(existing)) {
          byImageId.set(imageId, url);
        }
      }
    }

    const images = Array.from(byImageId.values());

    // Also include video cover frames (t51.71878) as images
    const vidUrls = html.match(/https:\/\/scontent[^"'\s,>\\]+t51\.71878[^"'\s,>\\]*/g) || [];
    const vidSeen = new Set<string>();
    for (const url of vidUrls) {
      if (url.includes("s150x150") || url.includes("s240x240")) continue;
      const idMatch = url.match(/\/([0-9]+_[0-9]+_[0-9]+_n\.jpg)/);
      const vid = idMatch ? idMatch[1] : url.split("?")[0];
      if (vidSeen.has(vid)) continue;
      vidSeen.add(vid);
      images.push(url);
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
