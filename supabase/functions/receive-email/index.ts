// Resend Inbound Webhook — receives email.received events
// and stores them in the email_signals table for pipeline ingestion.

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? "";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SUPABASE_SERVICE_ROLE_KEY =
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

// Map sender domains to company names for easier pipeline filtering
const SENDER_MAP: Record<string, string> = {
  "blog.google": "Google",
  "google.com": "Google",
  "apple.com": "Apple",
  "microsoft.com": "Microsoft",
  "meta.com": "Meta",
  "fb.com": "Meta",
  "nvidia.com": "Nvidia",
  "openai.com": "OpenAI",
  "amazon.com": "Amazon",
  "aws.amazon.com": "AWS",
  "intel.com": "Intel",
  "salesforce.com": "Salesforce",
  "spacex.com": "SpaceX",
  "anthropic.com": "Anthropic",
  "qualcomm.com": "Qualcomm",
  "broadcom.com": "Broadcom",
  "tesla.com": "Tesla",
};

function identifyCompany(from: string): string | null {
  const domain = from.split("@")[1]?.toLowerCase() ?? "";
  for (const [key, company] of Object.entries(SENDER_MAP)) {
    if (domain === key || domain.endsWith("." + key)) {
      return company;
    }
  }
  return null;
}

Deno.serve(async (req: Request) => {
  // Only accept POST
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  try {
    const payload = await req.json();

    // Only process email.received events
    if (payload.type !== "email.received") {
      return new Response(JSON.stringify({ ok: true, skipped: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }

    const data = payload.data;
    const emailId = data.email_id;
    const from = data.from ?? "";
    const to = Array.isArray(data.to) ? data.to.join(", ") : (data.to ?? "");
    const subject = data.subject ?? "";

    // Fetch the full email content from Resend API
    let bodyText = "";
    let bodyHtml = "";

    if (RESEND_API_KEY && emailId) {
      try {
        const emailRes = await fetch(
          `https://api.resend.com/emails/receiving/${emailId}`,
          {
            headers: { Authorization: `Bearer ${RESEND_API_KEY}` },
          }
        );
        if (emailRes.ok) {
          const emailData = await emailRes.json();
          bodyText = emailData.text ?? "";
          bodyHtml = emailData.html ?? "";
        }
      } catch {
        // If we can't fetch the full content, store what we have from the webhook
      }
    }

    const sourceCompany = identifyCompany(from);

    // Store in Supabase
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
    const { error } = await supabase.from("email_signals").upsert(
      {
        email_id: emailId,
        from_address: from,
        to_address: to,
        subject,
        body_text: bodyText,
        body_html: bodyHtml,
        received_at: data.created_at ?? new Date().toISOString(),
        source_company: sourceCompany,
        processed: false,
      },
      { onConflict: "email_id" }
    );

    if (error) {
      console.error("Supabase insert error:", error);
      return new Response(JSON.stringify({ ok: false, error: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }

    return new Response(
      JSON.stringify({ ok: true, email_id: emailId, company: sourceCompany }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  } catch (err) {
    console.error("Webhook error:", err);
    return new Response(
      JSON.stringify({ ok: false, error: String(err) }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});
