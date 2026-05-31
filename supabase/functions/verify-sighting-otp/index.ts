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

  let body: {
    email?: unknown;
    code?: unknown;
    sighting_data?: {
      consulate?: string;
      visa_type?: string;
      slots_date_start?: string;
      slots_date_end?: string;
      description?: string;
      reporter_name?: string;
    };
  };
  try {
    body = await req.json();
  } catch {
    return jsonResp({ error: "invalid JSON" }, 400);
  }

  const email = String(body.email ?? "").trim().toLowerCase();
  const code = String(body.code ?? "").trim();
  const sighting = body.sighting_data;

  if (!email || !isEmail(email)) return jsonResp({ error: "valid email required" }, 400);
  if (!code || code.length !== 6) return jsonResp({ error: "6-digit code required" }, 400);
  if (!sighting) return jsonResp({ error: "sighting_data required" }, 400);
  if (!sighting.consulate || !sighting.visa_type || !sighting.description || !sighting.reporter_name) {
    return jsonResp({ error: "Missing required sighting fields" }, 400);
  }

  /* Find a valid, unused OTP that hasn't expired */
  const { data: otps, error: otpErr } = await db
    .from("sighting_otps")
    .select("id, expires_at")
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
    .from("sighting_otps")
    .update({ used: true })
    .eq("id", otps[0].id);

  /* Insert the sighting */
  const { error: insertErr } = await db.from("visa_sightings").insert([
    {
      consulate: sighting.consulate,
      visa_type: sighting.visa_type,
      slots_date_start: sighting.slots_date_start || null,
      slots_date_end: sighting.slots_date_end || null,
      description: sighting.description.trim(),
      reporter_name: sighting.reporter_name.trim(),
      reporter_email: email,
      status: "published",
      verified: false,
    },
  ]);

  if (insertErr) {
    console.error("Sighting insert error:", insertErr);
    return jsonResp({ error: "Failed to publish sighting" }, 500);
  }

  return jsonResp({ ok: true });
});
