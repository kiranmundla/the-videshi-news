import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

function jsonResp(body: Record<string, unknown>, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return jsonResp({ error: "method not allowed" }, 405);

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const db = createClient(supabaseUrl, supabaseKey);

  let body: { story_id?: unknown; email?: unknown; code?: unknown };
  try {
    body = await req.json();
  } catch {
    return jsonResp({ error: "invalid JSON" }, 400);
  }

  const storyId = String(body.story_id ?? "").trim();
  const email = String(body.email ?? "").trim().toLowerCase();
  const code = String(body.code ?? "").trim();

  if (!storyId) return jsonResp({ error: "story_id required" }, 400);
  if (!email) return jsonResp({ error: "email required" }, 400);
  if (!code || code.length !== 6) return jsonResp({ error: "6-digit code required" }, 400);

  /* Find story and check OTP */
  const { data: story, error: storyErr } = await db
    .from("stories")
    .select("id, otp_code, otp_expires_at, author_email, status")
    .eq("id", storyId)
    .single();

  if (storyErr || !story) {
    return jsonResp({ error: "Story not found" }, 404);
  }

  if ((story.author_email || "").trim().toLowerCase() !== email) {
    return jsonResp({ error: "Email doesn't match" }, 403);
  }

  if (!story.otp_code || story.otp_code !== code) {
    return jsonResp({ error: "Invalid code" }, 403);
  }

  if (story.otp_expires_at && new Date(story.otp_expires_at) < new Date()) {
    return jsonResp({ error: "Code has expired. Please request a new one." }, 403);
  }

  /* Mark verified, move to pending_review, clear OTP */
  const { error: updateErr } = await db
    .from("stories")
    .update({
      email_verified: true,
      status: "pending_review",
      otp_code: null,
      otp_expires_at: null,
      updated_at: new Date().toISOString(),
    })
    .eq("id", storyId);

  if (updateErr) {
    console.error("Failed to verify story:", updateErr);
    return jsonResp({ error: "Verification failed" }, 500);
  }

  return jsonResp({ ok: true, verified: true });
});
