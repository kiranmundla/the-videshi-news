import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

function jsonResp(body: Record<string, unknown>, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS")
    return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST")
    return jsonResp({ error: "method not allowed" }, 405);

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const db = createClient(supabaseUrl, supabaseKey);

  let body: { email?: unknown; code?: unknown };
  try {
    body = await req.json();
  } catch {
    return jsonResp({ error: "invalid JSON" }, 400);
  }

  const email = String(body.email ?? "").trim().toLowerCase();
  const code = String(body.code ?? "").trim();

  if (!email) return jsonResp({ error: "email required" }, 400);
  if (!code || code.length !== 6) return jsonResp({ error: "6-digit code required" }, 400);

  /* Find matching OTP: not used, created within last 10 minutes */
  const tenMinAgo = new Date(Date.now() - 10 * 60 * 1000).toISOString();
  const { data: otp, error: fetchErr } = await db
    .from("inquiry_otps")
    .select("id, code")
    .eq("email", email)
    .eq("code", code)
    .eq("used", false)
    .gte("created_at", tenMinAgo)
    .order("created_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  if (fetchErr) {
    console.error("verify-inquiry-otp fetch error:", fetchErr);
    return jsonResp({ error: "Verification failed" }, 500);
  }

  if (!otp) {
    return jsonResp({ success: false, error: "Invalid or expired code" }, 400);
  }

  /* Mark as used */
  await db
    .from("inquiry_otps")
    .update({ used: true })
    .eq("id", otp.id);

  return jsonResp({ success: true });
});
