import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY");

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

  let body: { story_id?: unknown; email?: unknown };
  try {
    body = await req.json();
  } catch {
    return jsonResp({ error: "invalid JSON" }, 400);
  }

  const storyId = String(body.story_id ?? "").trim();
  const email = String(body.email ?? "").trim().toLowerCase();

  if (!storyId) return jsonResp({ error: "story_id required" }, 400);
  if (!email || !isEmail(email)) return jsonResp({ error: "valid email required" }, 400);

  /* Verify the story exists and email matches */
  const { data: story, error: storyErr } = await db
    .from("stories")
    .select("id, author_name, author_email")
    .eq("id", storyId)
    .single();

  if (storyErr || !story) {
    return jsonResp({ error: "Story not found" }, 404);
  }
  if ((story.author_email || "").trim().toLowerCase() !== email) {
    return jsonResp({ error: "Email doesn't match our records" }, 403);
  }

  /* Generate 6-digit OTP */
  const code = String(Math.floor(100000 + Math.random() * 900000));
  const expiresAt = new Date(Date.now() + 15 * 60 * 1000).toISOString(); // 15 min

  /* Store OTP in the story row */
  const { error: updateErr } = await db
    .from("stories")
    .update({ otp_code: code, otp_expires_at: expiresAt })
    .eq("id", storyId);

  if (updateErr) {
    console.error("Failed to store OTP:", updateErr);
    return jsonResp({ error: "Failed to generate verification code" }, 500);
  }

  /* Send email */
  const authorName = story.author_name || "there";

  const html = `
<!DOCTYPE html>
<html>
<head><meta charset="utf-8" /><meta name="viewport" content="width=device-width" /></head>
<body style="margin:0; padding:0; background:#f8f5f0; font-family: Georgia, 'Times New Roman', serif;">
  <div style="max-width:480px; margin:0 auto; padding:40px 24px;">
    <div style="text-align:center; margin-bottom:24px;">
      <h1 style="font-size:14px; font-weight:bold; letter-spacing:3px; text-transform:uppercase; color:#8b7355; margin:0;">
        THE VIDESHI
      </h1>
      <p style="font-size:13px; color:#999; margin:8px 0 0;">Diaspora Voices</p>
    </div>
    <div style="background:#ffffff; border-radius:12px; padding:36px 28px; box-shadow:0 1px 3px rgba(0,0,0,0.08); text-align:center;">
      <p style="font-size:16px; color:#333; margin:0 0 8px;">Hi ${authorName.split(" ")[0]},</p>
      <p style="font-size:14px; color:#666; margin:0 0 24px; line-height:1.6;">
        Use this code to verify your email and submit your story:
      </p>
      <div style="font-size:36px; font-weight:bold; letter-spacing:8px; color:#1a1a1a; background:#faf8f5; border:2px dashed #d4c9b8; border-radius:10px; padding:16px; margin:0 auto 24px; max-width:220px;">
        ${code}
      </div>
      <p style="font-size:12px; color:#999; margin:0;">
        This code expires in 15 minutes. If you didn't submit a story, you can ignore this email.
      </p>
    </div>
    <p style="text-align:center; font-size:11px; color:#ccc; margin-top:24px;">
      The Videshi · News for the global Indian diaspora · <a href="https://thevideshi.com" style="color:#bbb;">thevideshi.com</a>
    </p>
  </div>
</body>
</html>`;

  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "The Videshi <noreply@thevideshi.com>",
        to: [email],
        subject: `${code} — Verify your story submission`,
        html,
        text: `Hi ${authorName.split(" ")[0]},\n\nYour verification code is: ${code}\n\nThis code expires in 15 minutes.\n\nIf you didn't submit a story on The Videshi, you can ignore this email.\n\n— The Videshi\nhttps://thevideshi.com`,
      }),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      console.error("Resend error:", res.status, data);
      return jsonResp({ error: "Failed to send verification email" }, 502);
    }

    return jsonResp({ ok: true });
  } catch (e) {
    console.error("send-story-otp exception:", e);
    return jsonResp({ error: "Failed to send email" }, 500);
  }
});
