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

function isEmail(s: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return jsonResp({ error: "method not allowed" }, 405);

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const db = createClient(supabaseUrl, supabaseKey);

  let body: { event_id?: unknown; email?: unknown; code?: unknown };
  try {
    body = await req.json();
  } catch {
    return jsonResp({ error: "invalid JSON" }, 400);
  }

  const eventId = String(body.event_id ?? "").trim();
  const email = String(body.email ?? "").trim().toLowerCase();
  const code = String(body.code ?? "").trim();

  if (!eventId) return jsonResp({ error: "event_id required" }, 400);
  if (!email || !isEmail(email)) return jsonResp({ error: "valid email required" }, 400);
  if (!code || code.length !== 6) return jsonResp({ error: "6-digit code required" }, 400);

  /* Find a valid, unused OTP that hasn't expired */
  const { data: otps, error: otpErr } = await db
    .from("event_otps")
    .select("id, expires_at")
    .eq("event_id", eventId)
    .eq("email", email)
    .eq("code", code)
    .eq("used", false)
    .gte("expires_at", new Date().toISOString())
    .limit(1);

  if (otpErr || !otps || otps.length === 0) {
    return jsonResp({ error: "Invalid or expired code" }, 403);
  }

  /* Mark OTP as used */
  await db
    .from("event_otps")
    .update({ used: true })
    .eq("id", otps[0].id);

  return jsonResp({ ok: true, verified: true });
});
