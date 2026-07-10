import type { VercelRequest, VercelResponse } from "@vercel/node";

/**
 * GET /api/geo
 *
 * Returns the visitor's approximate location from Vercel's edge-detected
 * geo headers.  No external service, no cost, no user prompt.
 *
 * Response: { city, region, country, latitude, longitude }
 */
export default function handler(req: VercelRequest, res: VercelResponse) {
  const city = (req.headers["x-vercel-ip-city"] as string) || "";
  const region = (req.headers["x-vercel-ip-country-region"] as string) || "";
  const country = (req.headers["x-vercel-ip-country"] as string) || "";
  const latitude = (req.headers["x-vercel-ip-latitude"] as string) || "";
  const longitude = (req.headers["x-vercel-ip-longitude"] as string) || "";

  res.setHeader("Cache-Control", "private, no-store");
  res.json({
    city: decodeURIComponent(city),
    region,
    country,
    latitude: latitude ? parseFloat(latitude) : null,
    longitude: longitude ? parseFloat(longitude) : null,
  });
}
