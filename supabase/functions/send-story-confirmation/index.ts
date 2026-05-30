const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY");

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

  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return jsonResp({ error: "invalid JSON" }, 400);
  }

  const headline = String(body.headline ?? "").trim();
  const slug = String(body.slug ?? "").trim();
  const email = String(body.email ?? "").trim();
  const author_name = String(body.author_name ?? "").trim();

  if (!headline || !slug || !email) {
    return jsonResp({ error: "headline, slug, and email are required" }, 400);
  }

  const escape = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  const storyUrl = `https://thevideshi.com/stories/${encodeURIComponent(slug)}`;
  const safeHeadline = escape(headline);
  const safeName = escape(author_name || "there");

  const html = `
<!DOCTYPE html>
<html>
<head><meta charset="utf-8" /><meta name="viewport" content="width=device-width" /></head>
<body style="margin:0; padding:0; background:#f8f5f0; font-family: Georgia, 'Times New Roman', serif;">
  <div style="max-width:560px; margin:0 auto; padding:40px 24px;">
    <div style="text-align:center; margin-bottom:32px;">
      <h1 style="font-size:14px; font-weight:bold; letter-spacing:3px; text-transform:uppercase; color:#8b7355; margin:0;">
        THE VIDESHI
      </h1>
      <p style="font-size:13px; color:#999; margin:8px 0 0;">Diaspora Voices</p>
    </div>
    <div style="background:#ffffff; border-radius:12px; padding:40px 32px; box-shadow:0 1px 3px rgba(0,0,0,0.08);">
      <div style="text-align:center; margin-bottom:24px;">
        <span style="font-size:48px;">✨</span>
      </div>
      <h2 style="font-family:Georgia,serif; font-size:24px; color:#1a1a1a; text-align:center; margin:0 0 8px; line-height:1.3;">
        Your Story Is Live!
      </h2>
      <p style="text-align:center; color:#888; font-size:14px; margin:0 0 28px;">
        Thank you for sharing your voice with the diaspora community
      </p>
      <div style="background:#faf8f5; border:1px solid #e8e2d9; border-radius:10px; padding:24px; margin-bottom:28px;">
        <h3 style="font-family:Georgia,serif; font-size:18px; color:#1a1a1a; margin:0 0 8px; line-height:1.3;">
          ${safeHeadline}
        </h3>
        <p style="font-size:14px; color:#666; margin:0;">by ${safeName}</p>
      </div>
      <div style="text-align:center; margin-bottom:32px;">
        <a href="${storyUrl}" style="display:inline-block; padding:14px 36px; background:#8b7355; color:#ffffff; text-decoration:none; font-family:Georgia,serif; font-size:16px; font-weight:bold; border-radius:8px;">
          Read Your Story →
        </a>
      </div>
      <div style="height:1px; background:#e8e2d9; margin:28px 0;"></div>
      <h4 style="font-size:14px; color:#1a1a1a; margin:0 0 8px; font-family:Georgia,serif;">
        Help spread the word
      </h4>
      <p style="font-size:13px; color:#666; line-height:1.6; margin:0;">
        Share your story on WhatsApp, social media, or with friends. Every share helps someone in the diaspora feel less alone. Your story matters. 🙏
      </p>
    </div>
    <div style="text-align:center; margin-top:32px;">
      <p style="font-size:12px; color:#bbb; margin:0 0 8px; line-height:1.5;">
        You're receiving this because you shared a story on The Videshi.
      </p>
      <p style="font-size:11px; color:#ccc; margin:0;">
        News &amp; stories for the global Indian diaspora · <a href="https://thevideshi.com" style="color:#bbb;">thevideshi.com</a>
      </p>
    </div>
  </div>
</body>
</html>`;

  const text = `✨ Your Story Is Live!\n\n${headline}\nby ${author_name}\n\nRead your story: ${storyUrl}\n\nHelp spread the word — share your story on WhatsApp, social media, or with friends. Every share helps someone in the diaspora feel less alone.\n\nThank you for sharing your voice.\n— The Videshi\nhttps://thevideshi.com`;

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
        subject: `✨ Your Story Is Live — ${headline}`,
        html,
        text,
      }),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      console.error("Resend error:", res.status, data);
      return jsonResp({ error: "Failed to send confirmation email" }, 502);
    }

    return jsonResp({ ok: true, id: data?.id ?? null });
  } catch (e) {
    console.error("send-story-confirmation exception:", e);
    return jsonResp({ error: "Failed to send email" }, 500);
  }
});
