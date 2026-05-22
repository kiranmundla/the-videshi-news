import type { VercelRequest, VercelResponse } from "@vercel/node";

const TURNSTILE_SECRET = "0x4AAAAAADUi3m_tOGTMpqtkP3HSVrTjP0A";

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ success: false, error: "Method not allowed" });
  }

  const { token } = req.body ?? {};
  if (!token || typeof token !== "string") {
    return res.status(400).json({ success: false, error: "Missing turnstile token" });
  }

  try {
    const cfRes = await fetch(
      "https://challenges.cloudflare.com/turnstile/v0/siteverify",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ secret: TURNSTILE_SECRET, response: token }),
      },
    );
    const cfData = await cfRes.json();

    if (cfData.success) {
      return res.status(200).json({ success: true });
    } else {
      return res
        .status(403)
        .json({ success: false, error: "Bot verification failed" });
    }
  } catch {
    return res
      .status(500)
      .json({ success: false, error: "Verification service unavailable" });
  }
}
