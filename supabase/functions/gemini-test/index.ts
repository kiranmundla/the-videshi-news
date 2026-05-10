// v2 - updated API key
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  try {
    const { data: signals, error } = await supabase
      .from("p2_signals")
      .select("id, title, published_at")
      .gte("published_at", new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())
      .order("published_at", { ascending: false })
      .limit(10);

    if (error) throw error;
    if (!signals || signals.length === 0) {
      return new Response(JSON.stringify({ ok: false, message: "No signals" }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const geminiKey = Deno.env.get('GEMINI_API_KEY');

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models?key=${geminiKey}`,
      { method: 'GET' }
    );

    const data = await response.json();

    const data = await response.json();

    return new Response(JSON.stringify({ ok: true, signalCount: signals.length, signals, gemini: data }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (err: any) {
    return new Response(JSON.stringify({ ok: false, error: err?.message ?? String(err) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
