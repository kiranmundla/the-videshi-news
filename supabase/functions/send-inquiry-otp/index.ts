import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? "";

function jsonResp(body: Record<string, unknown>, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

function isEmail(s: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS")
    return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST")
    return jsonResp({ error: "method not allowed" }, 405);

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
  if (!email || !isEmail(email)) {
    return jsonResp({ error: "valid email required" }, 400);
  }

  /* Rate limit: max 5 OTPs per email in 1 hour */
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString();
  const { count } = await db
    .from("inquiry_otps")
    .select("id", { count: "exact", head: true })
    .eq("email", email)
    .gte("created_at", oneHourAgo);
  if ((count ?? 0) >= 5) {
    return jsonResp({ error: "Too many requests. Please try again later." }, 429);
  }

  /* Delete previous unused OTPs for this email */
  await db
    .from("inquiry_otps")
    .delete()
    .eq("email", email)
    .eq("used", false);

  /* Generate 6-digit code */
  const code = String(Math.floor(100000 + Math.random() * 900000));

  /* Store OTP */
  const { error: insertErr } = await db
    .from("inquiry_otps")
    .insert({ email, code });
  if (insertErr) {
    console.error("Failed to insert OTP:", insertErr);
    return jsonResp({ error: "Failed to generate code" }, 500);
  }

  /* Send email via Resend */
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
        subject: "Your Videshi verification code",
        html: `
          <div style="font-family: Georgia, serif; max-width: 480px; margin: 0 auto; padding: 32px 24px;">
            <h2 style="font-size: 20px; color: #1a1a1a; margin: 0 0 16px;">Verify Your Email</h2>
            <p style="font-size: 14px; color: #555; margin: 0 0 24px;">
              Use the code below to verify your email for your inquiry on The Videshi Classifieds.
            </p>
            <div style="background: #f8f5f0; border: 2px solid #e5ddd3; border-radius: 12px; padding: 24px; text-align: center; margin: 0 0 24px;">
              <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #1a1a1a;">${code}</span>
            </div>
            <p style="font-size: 13px; color: #999; margin: 0;">
              This code expires in 10 minutes. If you didn't request this, you can safely ignore this email.
            </p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;" />
            <p style="color: #bbb; font-size: 11px; margin: 0;">
              The Videshi — News &amp; Community for the Indian Diaspora
            </p>
          </div>
        `,
        text: `Your Videshi verification code is: ${code}\n\nIt expires in 10 minutes.\n\nIf you didn't request this, you can safely ignore this email.\n\n— The Videshi`,
      }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      console.error("Resend error:", res.status, data);
      return jsonResp({ error: "Failed to send verification email" }, 502);
    }
    return jsonResp({ ok: true });
  } catch (e) {
    console.error("send-inquiry-otp exception:", e);
    return jsonResp({ error: "Failed to send verification email" }, 500);
  }
});
