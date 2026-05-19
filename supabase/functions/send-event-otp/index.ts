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

  let body: { event_id?: unknown; email?: unknown };
  try {
    body = await req.json();
  } catch {
    return jsonResp({ error: "invalid JSON" }, 400);
  }

  const eventId = String(body.event_id ?? "").trim();
  const email = String(body.email ?? "").trim().toLowerCase();

  if (!eventId) return jsonResp({ error: "event_id required" }, 400);
  if (!email || !isEmail(email)) return jsonResp({ error: "valid email required" }, 400);

  /* Verify the event exists, is user-submitted, and email matches organizer */
  const { data: event, error: eventErr } = await db
    .from("events")
    .select("id, title, organizer, source")
    .eq("id", eventId)
    .single();

  if (eventErr || !event) {
    return jsonResp({ error: "Event not found" }, 404);
  }
  if (event.source !== "user_submitted") {
    return jsonResp({ error: "This event cannot be edited" }, 403);
  }
  if ((event.organizer || "").trim().toLowerCase() !== email) {
    return jsonResp({ error: "Email doesn't match our records" }, 403);
  }

  /* Generate 6-digit code */
  const code = String(Math.floor(100000 + Math.random() * 900000));

  /* Delete any existing unused OTPs for this event */
  await db
    .from("event_otps")
    .delete()
    .eq("event_id", eventId)
    .eq("used", false);

  /* Insert new OTP — expires in 10 minutes */
  const expiresAt = new Date(Date.now() + 10 * 60 * 1000).toISOString();
  const { error: insertErr } = await db
    .from("event_otps")
    .insert({ event_id: eventId, email, code, expires_at: expiresAt });

  if (insertErr) {
    console.error("OTP insert error:", insertErr);
    return jsonResp({ error: "Failed to generate code" }, 500);
  }

  /* Send email via Resend */
  const escape = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  const eventTitle = escape(event.title || "your event");

  const html = `
    <div style="font-family: Georgia, serif; max-width: 480px; margin: 0 auto; padding: 32px 24px;">
      <h2 style="font-size: 20px; color: #1a1a1a; margin: 0 0 8px;">Your Edit Code</h2>
      <p style="color: #666; font-size: 14px; margin: 0 0 24px;">
        You requested to edit <strong>${eventTitle}</strong> on The Videshi.
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

  const text = `Your edit code for "${event.title}" on The Videshi is: ${code}\n\nThis code expires in 10 minutes.\n\nIf you didn't request this, ignore this email.`;

  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "The Videshi <onboarding@resend.dev>",
        to: [email],
        subject: `Your Event Edit Code — The Videshi`,
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
    console.error("send-event-otp exception:", e);
    return jsonResp({ error: "Failed to send email" }, 500);
  }
});
