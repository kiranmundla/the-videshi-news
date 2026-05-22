import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
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

const escape = (s: string) =>
  s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

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

  let body: {
    classified_id?: unknown;
    sender_name?: unknown;
    sender_email?: unknown;
    message?: unknown;
  };
  try {
    body = await req.json();
  } catch {
    return jsonResp({ error: "invalid JSON" }, 400);
  }

  const classifiedId = String(body.classified_id ?? "").trim();
  const senderName = String(body.sender_name ?? "").trim();
  const senderEmail = String(body.sender_email ?? "").trim().toLowerCase();
  const message = String(body.message ?? "").trim();

  if (!classifiedId)
    return jsonResp({ error: "classified_id required" }, 400);
  if (!senderName) return jsonResp({ error: "sender_name required" }, 400);
  if (!senderEmail || !isEmail(senderEmail))
    return jsonResp({ error: "valid sender_email required" }, 400);
  if (!message) return jsonResp({ error: "message required" }, 400);
  if (message.length > 2000)
    return jsonResp({ error: "message too long (max 2000 chars)" }, 400);

  /* Look up the classified listing */
  const { data: listing, error: listingErr } = await db
    .from("classifieds")
    .select("id, title, contact_email, status")
    .eq("id", classifiedId)
    .single();

  if (listingErr || !listing) {
    return jsonResp({ error: "Listing not found" }, 404);
  }
  if (listing.status !== "active") {
    return jsonResp({ error: "This listing is no longer active" }, 403);
  }
  if (!listing.contact_email) {
    return jsonResp(
      { error: "This listing has no contact email configured" },
      400,
    );
  }

  const listingTitle = escape(listing.title || "your listing");
  const safeSenderName = escape(senderName);
  const safeSenderEmail = escape(senderEmail);
  const safeMessage = escape(message).replace(/\n/g, "<br />");

  const html = `
    <div style="font-family: Georgia, serif; max-width: 560px; margin: 0 auto; padding: 32px 24px;">
      <h2 style="font-size: 20px; color: #1a1a1a; margin: 0 0 8px;">New Inquiry for Your Listing</h2>
      <p style="color: #666; font-size: 14px; margin: 0 0 24px;">
        Someone is interested in your listing: <strong>"${listingTitle}"</strong>
      </p>

      <div style="background: #f8f5f0; border: 1px solid #e5ddd3; border-radius: 12px; padding: 20px; margin: 0 0 24px;">
        <p style="font-size: 14px; color: #333; margin: 0 0 12px;">
          <strong>From:</strong> ${safeSenderName}
        </p>
        <p style="font-size: 14px; color: #333; margin: 0 0 16px;">
          <strong>Email:</strong> <a href="mailto:${safeSenderEmail}" style="color: #7c3aed;">${safeSenderEmail}</a>
        </p>
        <hr style="border: none; border-top: 1px solid #e5ddd3; margin: 0 0 16px;" />
        <p style="font-size: 14px; color: #444; margin: 0; line-height: 1.6;">
          ${safeMessage}
        </p>
      </div>

      <p style="font-size: 14px; color: #333; margin: 0 0 16px;">
        <strong>Reply directly</strong> to this person at
        <a href="mailto:${safeSenderEmail}" style="color: #7c3aed;">${safeSenderEmail}</a>
      </p>

      <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px 16px; margin: 0 0 24px;">
        <p style="font-size: 13px; color: #166534; margin: 0;">
          🔒 Your email address was <strong>not</strong> shared with the sender.
        </p>
      </div>

      <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;" />
      <p style="color: #bbb; font-size: 11px; margin: 0;">
        The Videshi Classifieds — News &amp; Community for the Indian Diaspora
      </p>
    </div>
  `;

  const text = `New inquiry for your listing "${listing.title}"

From: ${senderName} (${senderEmail})

Message:
${message}

Reply directly to this person at ${senderEmail}.

Your email address was not shared with the sender.

— The Videshi Classifieds`;

  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "The Videshi Classifieds <noreply@thevideshi.com>",
        to: [listing.contact_email],
        reply_to: senderEmail,
        subject: `New Inquiry: ${listing.title} — The Videshi Classifieds`,
        html,
        text,
      }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      console.error("Resend error:", res.status, data);
      return jsonResp({ error: "Failed to send inquiry" }, 502);
    }
    return jsonResp({ ok: true });
  } catch (e) {
    console.error("send-classified-inquiry exception:", e);
    return jsonResp({ error: "Failed to send inquiry" }, 500);
  }
});
