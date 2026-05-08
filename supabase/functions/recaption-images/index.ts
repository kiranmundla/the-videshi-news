// One-time: regenerate image_caption for all published articles via Claude Haiku Vision.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY")!;
const HAIKU_MODEL = "claude-haiku-4-5";

const PROMPT =
  "Look at this image carefully. In one short sentence (max 12 words), describe exactly what you see — the specific building, place, person, or scene. Be precise, not generic.";

async function captionImage(imageUrl: string): Promise<string | null> {
  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: HAIKU_MODEL,
        max_tokens: 100,
        messages: [{
          role: "user",
          content: [
            { type: "image", source: { type: "url", url: imageUrl } },
            { type: "text", text: PROMPT },
          ],
        }],
      }),
    });
    if (!res.ok) {
      console.error("vision error", res.status, await res.text());
      return null;
    }
    const data = await res.json();
    return (data?.content?.[0]?.text ?? "").trim() || null;
  } catch (e) {
    console.error("caption error", e);
    return null;
  }
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  const { data: articles, error } = await supabase
    .from("articles")
    .select("id, title, image_url")
    .eq("is_published", true)
    .not("image_url", "is", null);

  if (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const results: Array<{ id: string; title: string; caption: string | null; ok: boolean }> = [];
  for (const a of articles ?? []) {
    const caption = await captionImage(a.image_url!);
    if (!caption) {
      results.push({ id: a.id, title: a.title, caption: null, ok: false });
      console.log(`✗ ${a.title}`);
      continue;
    }
    const { error: updErr } = await supabase
      .from("articles")
      .update({ image_caption: caption })
      .eq("id", a.id);
    results.push({ id: a.id, title: a.title, caption, ok: !updErr });
    console.log(`✓ ${a.title} → ${caption}`);
  }

  return new Response(
    JSON.stringify({ processed: results.length, results }, null, 2),
    { headers: { ...corsHeaders, "Content-Type": "application/json" } },
  );
});
