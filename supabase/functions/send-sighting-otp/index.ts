import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const RESEND_API_KEY = "re_GKr12Vmh_5beBV9kJkrmSRYG3JR97p1Gf";

function isEmail(s: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);
}

function jsonResp(body: Record<string, unknown>, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return jsonResp({ error: "method not allowed" }, 405);

  if (!RESEND_API_KEY) {
    return jsonResp({ error: "RESEND_API_KEY not configured" }, 500);
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const db = createClient(supabaseUrl, supabaseKey);

  let body: { email?: unknown };
  try {
    body = await req.json();
  } catch {
    return jsonResp({ error: "invalid JSON" }, 400);
  }

  const email = String(body.email ?? "").trim().toLowerCase();
  if (!email || !isEmail(email)) return jsonResp({ error: "valid email required" }, 400);

  /* Rate limit: max 3 OTPs per email in last 10 minutes */
  const tenMinAgo = new Date(Date.now() - 10 * 60 * 1000).toISOString();
  const { data: recent } = await db
    .from("sighting_otps")
    .select("id")
    .eq("email", email)
    .gte("created_at", tenMinAgo);

  if (recent && recent.length >= 3) {
    return jsonResp({ error: "Too many requests. Please wait a few minutes." }, 429);
  }

  /* Generate 6-digit code */
  const code = String(Math.floor(100000 + Math.random() * 900000));

  /* Delete any existing unused OTPs for this email */
  await db
    .from("sighting_otps")
    .delete()
    .eq("email", email)
    .eq("used", false);

  /* Insert new OTP — expires in 10 minutes */
  const expiresAt = new Date(Date.now() + 10 * 60 * 1000).toISOString();
  const { error: insertErr } = await db
    .from("sighting_otps")
    .insert({ email, code, expires_at: expiresAt });

  if (insertErr) {
    console.error("OTP insert error:", insertErr);
    return jsonResp({ error: "Failed to generate code" }, 500);
  }

  /* Send email via Resend */
  const html = `
    <div style="font-family: Georgia, serif; max-width: 480px; margin: 0 auto; padding: 32px 24px;">
      <h2 style="font-size: 20px; color: #1a1a1a; margin: 0 0 8px;">Verify Your Sighting Report</h2>
      <p style="color: #666; font-size: 14px; margin: 0 0 24px;">
        Enter this code to publish your visa slot sighting on The Videshi.
      </p>
      <div style="background: #f8f5f0; border: 2px solid #e5ddd3; border-radius: 12px; padding: 24px; text-align: center; margin: 0 0 24px;">
        <p style="font-size: 36px; font-family: monospace; letter-spacing: 8px; color: #1a1a1a; margin: 0; font-weight: bold;">
          ${code}
        </p>
      </div>
      <p style="color: #999; font-size: 13px; margin: 0;">
        This code expires in <strong>10 minutes</strong>. If you didn't request this, you can safely ignore this email.
      </p>
      <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;" />
      <p style="color: #bbb; font-size: 11px; margin: 0;">The Videshi — News for the global Indian diaspora</p>
    </div>
  `;

  const text = `Your verification code for The Videshi visa sighting report is: ${code}\n\nThis code expires in 10 minutes.\n\nIf you didn't request this, ignore this email.`;

  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "The Videshi <noreply@thevideshi.com>",
        to: [email],
        subject: "Verify your sighting report — The Videshi",
        html,
        text,
      }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      console.error("Resend error:", res.status, data);
      return jsonResp({ error: "Failed to send email" }, 502);
    }
    return jsonResp({ ok: true });
  } catch (e) {
    console.error("send-sighting-otp exception:", e);
    return jsonResp({ error: "Failed to send email" }, 500);
  }
});
