// Admin: pin/unpin a featured article. Auth via shared VIDESHI_API_KEY header.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-admin-key",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

  const adminKey = Deno.env.get("VIDESHI_API_KEY");
  if (!adminKey) {
    return new Response(JSON.stringify({ error: "admin key not configured" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
  if (req.headers.get("x-admin-key") !== adminKey) {
    return new Response(JSON.stringify({ error: "unauthorized" }), {
      status: 401,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  let body: { id?: string; pin?: boolean; hours?: number } = {};
  try { body = await req.json(); } catch { /* empty */ }

  const { id, pin, hours } = body;
  if (!id || typeof pin !== "boolean") {
    return new Response(JSON.stringify({ error: "id and pin required" }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  );

  const update: Record<string, unknown> = {
    is_pinned_featured: pin,
    pinned_until: pin
      ? new Date(Date.now() + (hours ?? 24) * 3600 * 1000).toISOString()
      : null,
  };

  const { data, error } = await supabase
    .from("articles")
    .update(update)
    .eq("id", id)
    .select("id, is_pinned_featured, pinned_until, featured_score")
    .single();

  if (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  return new Response(JSON.stringify({ ok: true, article: data }), {
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
});
