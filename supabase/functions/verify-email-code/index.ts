import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

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

  if (!email || !isEmail(email)) return jsonResp({ error: "valid email required" }, 400);
  if (!code || code.length !== 6) return jsonResp({ error: "6-digit code required" }, 400);

  /* Look up matching, unexpired, unused OTP with null event_id (email verification) */
  const { data: otp, error: otpErr } = await db
    .from("event_otps")
    .select("id")
    .is("event_id", null)
    .eq("email", email)
    .eq("code", code)
    .eq("used", false)
    .gt("expires_at", new Date().toISOString())
    .limit(1)
    .single();

  if (otpErr || !otp) {
    return jsonResp({ error: "Invalid or expired code" }, 403);
  }

  /* Mark as used */
  await db
    .from("event_otps")
    .update({ used: true })
    .eq("id", otp.id);

  return jsonResp({ ok: true, verified: true });
});
