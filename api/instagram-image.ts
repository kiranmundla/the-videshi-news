import type { VercelRequest, VercelResponse } from "@vercel/node";

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const { url } = req.query;
  if (!url || typeof url !== "string" || !url.startsWith("https://scontent")) {
    return res.status(400).json({ error: "invalid url" });
  }

  try {
    const response = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
      },
    });

    if (!response.ok) {
      return res.status(502).json({ error: `upstream ${response.status}` });
    }

    const contentType = response.headers.get("content-type") || "image/jpeg";
    const buffer = Buffer.from(await response.arrayBuffer());

    res.setHeader("Content-Type", contentType);
    res.setHeader("Cache-Control", "public, s-maxage=86400, stale-while-revalidate=3600");
    return res.send(buffer);
  } catch (e: unknown) {
    return res.status(500).json({ error: e instanceof Error ? e.message : "unknown" });
  }
}
