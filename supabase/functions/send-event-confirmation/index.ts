const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const RESEND_API_KEY = "re_FpqYdtuj_JCHhzabuovEGqG7rdqKLi9uw";

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

  const title = String(body.title ?? "").trim();
  const slug = String(body.slug ?? "").trim();
  const email = String(body.email ?? "").trim();
  const date = String(body.date ?? "").trim();
  const venue = String(body.venue ?? "").trim();
  const city = String(body.city ?? "").trim();

  if (!title || !slug || !email) {
    return jsonResp({ error: "title, slug, and email are required" }, 400);
  }

  const escape = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  const eventUrl = `https://thevideshi.com/events/${encodeURIComponent(slug)}`;
  const editUrl = `https://thevideshi.com/events/${encodeURIComponent(slug)}/edit`;

  const safeTitle = escape(title);
  const safeVenue = escape(venue);
  const safeCity = escape(city);

  /* Format date nicely */
  let dateFormatted = date;
  try {
    const d = new Date(date + "T00:00:00");
    dateFormatted = d.toLocaleDateString("en-US", {
      weekday: "long", year: "numeric", month: "long", day: "numeric",
    });
  } catch { /* keep raw */ }

  const html = `
<!DOCTYPE html>
<html>
<head><meta charset="utf-8" /><meta name="viewport" content="width=device-width" /></head>
<body style="margin:0; padding:0; background:#f8f5f0; font-family: Georgia, 'Times New Roman', serif;">
  <div style="max-width:560px; margin:0 auto; padding:40px 24px;">

    <!-- Header -->
    <div style="text-align:center; margin-bottom:32px;">
      <h1 style="font-size:14px; font-weight:bold; letter-spacing:3px; text-transform:uppercase; color:#8b7355; margin:0;">
        THE VIDESHI
      </h1>
    </div>

    <!-- Main Card -->
    <div style="background:#ffffff; border-radius:12px; padding:40px 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">

      <!-- Celebration -->
      <div style="text-align:center; margin-bottom:24px;">
        <span style="font-size:48px;">🎉</span>
      </div>

      <h2 style="font-family: Georgia, serif; font-size:26px; color:#1a1a1a; text-align:center; margin:0 0 8px; line-height:1.3;">
        Your Event Is Live!
      </h2>
      <p style="text-align:center; color:#888; font-size:14px; margin:0 0 28px;">
        Thank you for sharing with the desi community
      </p>

      <!-- Event Details Box -->
      <div style="background:#faf8f5; border:1px solid #e8e2d9; border-radius:10px; padding:24px; margin-bottom:28px;">
        <h3 style="font-family: Georgia, serif; font-size:18px; color:#1a1a1a; margin:0 0 16px; line-height:1.3;">
          ${safeTitle}
        </h3>
        <table style="width:100%; border-collapse:collapse;">
          <tr>
            <td style="padding:6px 0; color:#999; font-size:13px; width:28px; vertical-align:top;">📅</td>
            <td style="padding:6px 0; color:#444; font-size:14px;">${escape(dateFormatted)}</td>
          </tr>
          ${safeVenue ? `<tr>
            <td style="padding:6px 0; color:#999; font-size:13px; vertical-align:top;">📍</td>
            <td style="padding:6px 0; color:#444; font-size:14px;">${safeVenue}</td>
          </tr>` : ""}
          ${safeCity ? `<tr>
            <td style="padding:6px 0; color:#999; font-size:13px; vertical-align:top;">🏙️</td>
            <td style="padding:6px 0; color:#444; font-size:14px;">${safeCity}</td>
          </tr>` : ""}
        </table>
      </div>

      <!-- CTA Button -->
      <div style="text-align:center; margin-bottom:32px;">
        <a href="${eventUrl}" style="display:inline-block; padding:14px 36px; background:#8b7355; color:#ffffff; text-decoration:none; font-family:Georgia, serif; font-size:16px; font-weight:bold; border-radius:8px; letter-spacing:0.5px;">
          View Your Event →
        </a>
      </div>

      <!-- Divider -->
      <div style="height:1px; background:#e8e2d9; margin:28px 0;"></div>

      <!-- Edit Section -->
      <h4 style="font-size:14px; color:#1a1a1a; margin:0 0 8px; font-family:Georgia, serif;">
        Need to make changes?
      </h4>
      <p style="font-size:13px; color:#666; line-height:1.6; margin:0 0 12px;">
        You can edit or update your event anytime. Just visit your event's edit page and verify with the email you used to submit.
      </p>
      <a href="${editUrl}" style="font-size:13px; color:#8b7355; text-decoration:underline;">
        Edit your event →
      </a>

      <!-- Divider -->
      <div style="height:1px; background:#e8e2d9; margin:28px 0;"></div>

      <!-- How people find your event -->
      <h4 style="font-size:14px; color:#1a1a1a; margin:0 0 8px; font-family:Georgia, serif;">
        How people will find your event
      </h4>
      <p style="font-size:13px; color:#666; line-height:1.7; margin:0;">
        Your event is listed at <a href="https://thevideshi.com/events" style="color:#8b7355; text-decoration:underline;">thevideshi.com/events</a>. Visitors can discover it by browsing the Events page, searching by name or city, or using the <strong>Near Me</strong> feature to find events in their area. Share your event link with friends and community groups to spread the word!
      </p>
    </div>

    <!-- Footer -->
    <div style="text-align:center; margin-top:32px; padding:0 16px;">
      <p style="font-size:12px; color:#bbb; margin:0 0 8px; line-height:1.5;">
        You're receiving this because you submitted an event on The Videshi.
      </p>
      <p style="font-size:11px; color:#ccc; margin:0;">
        News &amp; events for the global Indian diaspora · <a href="https://thevideshi.com" style="color:#bbb;">thevideshi.com</a>
      </p>
    </div>

  </div>
</body>
</html>`;

  const text = `🎉 Your Event Is Live!\n\n${title}\n\n📅 ${dateFormatted}${venue ? `\n📍 ${venue}` : ""}${city ? `\n🏙️ ${city}` : ""}\n\nView your event: ${eventUrl}\n\nNeed to make changes? Edit anytime at:\n${editUrl}\n\nJust verify with the email you used to submit.\n\nHow people will find your event:\nYour event is listed at thevideshi.com/events. Visitors can discover it by browsing the Events page, searching by name or city, or using the "Near Me" feature to find events in their area. Share your event link with friends and community groups to spread the word!\n\nThank you for sharing with the desi community!\n— The Videshi\nhttps://thevideshi.com`;

  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "The Videshi Events <noreply@thevideshi.com>",
        to: [email],
        subject: `🎉 Your Event Is Live — ${title}`,
        html,
        text,
      }),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      console.error("Resend error:", res.status, data);
      return jsonResp({ error: "Failed to send confirmation email", details: data }, 502);
    }

    return jsonResp({ ok: true, id: data?.id ?? null });
  } catch (e) {
    console.error("send-event-confirmation exception:", e);
    return jsonResp({ error: "Failed to send email" }, 500);
  }
});
