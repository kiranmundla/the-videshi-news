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

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${Deno.env.get('GEMINI_API_KEY')}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: `You are a news editor for The Videshi, a news platform for Indian diaspora (US, UK, Australia, UAE, Canada).

Analyze these 10 headlines and for each one return:
- canonical_title: clearest version of the headline
- category: news|entertainment|sports|markets-finance|technology|nri-world|lifestyle-health|travel|food
- score_diaspora: 0-100 how relevant to Indians abroad
- score_significance: 0-100 how important overall
- event_type: election-result|swearing-in|birthday|match-result|policy-announcement|other
- entities: array of {name, type, entity_id} objects where entity_id disambiguates (e.g. vijay-politician-tamil-nadu vs vijay-deverakonda-actor-telugu)
- location_relevance: {bay_area, london, dubai, toronto, sydney} scores 0-100
- free_sources: 2-3 URLs of copyright-free sources (Wikipedia, PIB, official govt sites)
- synthesis_angle: one sentence on diaspora angle to take when writing the article

Headlines:
${signals.map((s, i) => `[${i}] ${s.title}`).join('\n')}

Return ONLY a valid JSON array. No markdown.`
            }]
          }],
          generationConfig: {
            temperature: 0.1,
            responseMimeType: "application/json"
          }
        })
      }
    );

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
