// Newsletter unsubscribe endpoint.
//
// Two POST flows, both verified by the unsubscribe_newsletter() RPC
// (HMAC token check + row update happen inside Postgres):
//
//   1. RFC 8058 one-click: Gmail/Apple POST to
//      /api/unsubscribe?email=..&token=.. with body "List-Unsubscribe=One-Click"
//   2. Confirm page: the /unsubscribe React page POSTs JSON {email, token}
//
// GET never unsubscribes — mailbox link scanners prefetch URLs, so a GET that
// mutated state would unsubscribe people who never asked.

const SUPABASE_URL =
  process.env.VITE_SUPABASE_URL ||
  process.env.SUPABASE_URL ||
  "https://lboecaekpynbpyijrbfz.supabase.co";
const SUPABASE_ANON_KEY =
  process.env.VITE_SUPABASE_ANON_KEY ||
  process.env.SUPABASE_ANON_KEY ||
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxib2VjYWVrcHluYnB5aWpyYmZ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc5NDc2NzQsImV4cCI6MjA5MzUyMzY3NH0.i2_CzXJEnIT2SZ9mx0j5OHh4rqewPwiLUogSrdM4HXY";

export default async function handler(req, res) {
  if (req.method === "GET") {
    // Scanners and curious clicks land here; never mutate on GET.
    res.setHeader("Allow", "POST");
    return res.status(405).json({
      error: "Use the unsubscribe link from your newsletter email.",
    });
  }
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed" });
  }

  // One-click posts carry credentials in the query string; the confirm
  // page posts them as JSON. Accept either.
  let email = req.query?.email;
  let token = req.query?.token;
  if ((!email || !token) && req.body && typeof req.body === "object") {
    email = email || req.body.email;
    token = token || req.body.token;
  }
  if (typeof email !== "string" || typeof token !== "string" || !email.includes("@")) {
    return res.status(400).json({ error: "Valid email and token are required" });
  }

  try {
    const resp = await fetch(`${SUPABASE_URL}/rest/v1/rpc/unsubscribe_newsletter`, {
      method: "POST",
      headers: {
        apikey: SUPABASE_ANON_KEY,
        Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ p_email: email, p_token: token }),
    });

    if (!resp.ok) {
      console.error("[unsubscribe] RPC failed:", resp.status, await resp.text());
      return res.status(500).json({ error: "Failed to unsubscribe" });
    }

    const result = await resp.json();

    if (result === "invalid") {
      // Forged or tampered link — say so honestly instead of claiming success.
      return res.status(400).json({ success: false, error: "Invalid unsubscribe link" });
    }

    // 'unsubscribed' | 'already' | 'not_found' are all 200: in every case the
    // requester ends up receiving no newsletter mail, which is what one-click
    // senders (Gmail/Apple) require.
    return res.status(200).json({ success: true, status: result });
  } catch (e) {
    console.error("[unsubscribe] Error:", e);
    return res.status(500).json({ error: "Failed to unsubscribe" });
  }
}
