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
    // Decode HTML entities first so URLs are clean
    const html = raw.replace(/&amp;/g, "&");

    let imageUrl = "";

    // 1. Best: post image at 1080px (t51.82787 = photo, p1080x1080 = full size)
    const hd = html.match(/https:\/\/scontent[^"'\s,]+t51\.82787[^"'\s,]*p1080x1080[^"'\s,]*/);
    if (hd) imageUrl = hd[0];

    // 2. Fallback: post image at 640px or 750px
    if (!imageUrl) {
      const mid = html.match(/https:\/\/scontent[^"'\s,]+t51\.82787[^"'\s,]*p(?:640x640|750x750)[^"'\s,]*/);
      if (mid) imageUrl = mid[0];
    }

    // 3. Fallback: any post image (t51.82787) that's NOT tiny (s150/s240)
    if (!imageUrl) {
      const any = html.match(/https:\/\/scontent[^"'\s,]+t51\.82787[^"'\s,]*/g);
      if (any) {
        const big = any.find(u => !u.includes("s150x150") && !u.includes("s240x240"));
        if (big) imageUrl = big;
      }
    }

    // 4. Last resort: video thumbnail (t51.71878) - not tiny
    if (!imageUrl) {
      const vid = html.match(/https:\/\/scontent[^"'\s,]+t51\.71878[^"'\s,]*/g);
      if (vid) {
        const big = vid.find(u => !u.includes("s150x150") && !u.includes("s240x240"));
        if (big) imageUrl = big;
      }
    }

    if (!imageUrl) {
      return res.status(404).json({ error: "image not found" });
    }

    // Cache 4h, stale-while-revalidate 1h
    res.setHeader("Cache-Control", "s-maxage=14400, stale-while-revalidate=3600");
    res.setHeader("Access-Control-Allow-Origin", "*");
    return res.json({ url: imageUrl });
  } catch (e: unknown) {
    const message = e instanceof Error ? e.message : "unknown error";
    return res.status(500).json({ error: message });
  }
}
