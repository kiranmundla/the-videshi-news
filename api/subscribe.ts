import type { VercelRequest, VercelResponse } from "@vercel/node";

const SUPABASE_URL =
  process.env.VITE_SUPABASE_URL ??
  process.env.SUPABASE_URL ??
  "https://lboecaekpynbpyijrbfz.supabase.co";
const SUPABASE_SERVICE_KEY =
  process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";
const SUPABASE_ANON_KEY =
  process.env.VITE_SUPABASE_PUBLISHABLE_KEY ??
  process.env.SUPABASE_ANON_KEY ??
  "";

async function ensureTable() {
  // Try inserting — if table doesn't exist, create it via SQL
  const check = await fetch(
    `${SUPABASE_URL}/rest/v1/newsletter_subscribers?select=email&limit=1`,
    {
      headers: {
        apikey: SUPABASE_SERVICE_KEY || SUPABASE_ANON_KEY,
        Authorization: `Bearer ${SUPABASE_SERVICE_KEY || SUPABASE_ANON_KEY}`,
      },
    }
  );
  if (check.ok) return true;
  // Table doesn't exist — need to create it via dashboard. Return false.
  return false;
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { email } = req.body || {};
  if (!email || typeof email !== "string" || !email.includes("@")) {
    return res.status(400).json({ error: "Valid email is required" });
  }

  const tableExists = await ensureTable();
  if (!tableExists) {
    // Fallback: store in a simple way - just log it
    console.log(`[newsletter] Subscriber: ${email}`);
  }

  const key = SUPABASE_SERVICE_KEY || SUPABASE_ANON_KEY;

  try {
    const resp = await fetch(`${SUPABASE_URL}/rest/v1/newsletter_subscribers`, {
      method: "POST",
      headers: {
        apikey: key,
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
        Prefer: "return=minimal",
      },
      body: JSON.stringify({
        email: email.toLowerCase().trim(),
      }),
    });

    if (resp.status === 201 || resp.status === 204) {
      return res.status(200).json({ success: true });
    }

    const body = await resp.text();
    if (body.includes("duplicate") || body.includes("unique")) {
      return res.status(200).json({ success: true, already: true });
    }

    console.error("[newsletter] Insert failed:", resp.status, body);
    return res.status(500).json({ error: "Failed to subscribe" });
  } catch (e) {
    console.error("[newsletter] Error:", e);
    return res.status(500).json({ error: "Failed to subscribe" });
  }
}
