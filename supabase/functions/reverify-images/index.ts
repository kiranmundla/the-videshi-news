// One-time: re-verify and possibly replace images for all published articles.
// Uses Claude Haiku to generate queries, Unsplash for candidates, Claude Vision to score.

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY")!;
const UNSPLASH_ACCESS_KEY = Deno.env.get("UNSPLASH_ACCESS_KEY")!;
const HAIKU = "claude-haiku-4-5";
const MIN_ACCEPT = 6;

async function haikuText(prompt: string, maxTokens = 200): Promise<string> {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model: HAIKU,
      max_tokens: maxTokens,
      messages: [{ role: "user", content: prompt }],
    }),
  });
  if (!res.ok) {
    console.error("haiku err", res.status, await res.text());
    return "";
  }
  const d = await res.json();
  return (d?.content?.[0]?.text ?? "").trim();
}

async function genQueries(title: string, category: string): Promise<string[]> {
  const out = await haikuText(
    `Generate 3 image-search queries for this Indian-diaspora news article. Prefer NAMED people and SPECIFIC Indian cities/states over generic terms like "election" or "politics". One query per line, no numbering, no quotes.

Category: ${category}
Title: ${title}`,
    150,
  );
  const lines = out.split("\n").map((l) => l.replace(/^[-*\d.\s"']+|["']+$/g, "").trim()).filter((l) => l.length > 1 && l.length < 80);
  return lines.slice(0, 3);
}

type Cand = { url: string; credit: string };

async function unsplash(query: string): Promise<Cand | null> {
  try {
    const r = await fetch(
      `https://api.unsplash.com/search/photos?query=${encodeURIComponent(query)}&per_page=1&orientation=landscape&content_filter=high`,
      { headers: { Authorization: `Client-ID ${UNSPLASH_ACCESS_KEY}` } },
    );
    if (!r.ok) return null;
    const d = await r.json();
    const p = d?.results?.[0];
    if (!p) return null;
    const url = p.urls?.regular || p.urls?.full;
    if (!url) return null;
    const name = p.user?.name ?? "Unsplash";
    return { url, credit: `Photo: ${name} / Unsplash` };
  } catch (e) {
    console.error("unsplash err", e);
    return null;
  }
}

async function score(imageUrl: string, title: string): Promise<{ score: number; description: string } | null> {
  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: HAIKU,
        max_tokens: 200,
        messages: [{
          role: "user",
          content: [
            { type: "image", source: { type: "url", url: imageUrl } },
            {
              type: "text",
              text: `Article: ${title}. Does this image show something directly relevant to this story? Score 1-10. If you see a famous Indian landmark unrelated to the article topic, score it 1. Reply JSON only: {"score": N, "description": "what you see"}`,
            },
          ],
        }],
      }),
    });
    if (!res.ok) {
      console.error("score err", res.status, await res.text());
      return null;
    }
    const d = await res.json();
    const text = (d?.content?.[0]?.text ?? "").trim().replace(/^```(?:json)?\s*|\s*```$/g, "");
    const m = text.match(/\{[\s\S]*\}/);
    const j = JSON.parse(m ? m[0] : text);
    return { score: Number(j.score) || 0, description: String(j.description ?? "").trim() };
  } catch (e) {
    console.error("score parse err", e);
    return null;
  }
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  const { data: run } = await supabase.from("pipeline_runs").insert({ run_type: "reverify-images", status: "running" }).select().single();
  const runId = run?.id;

  let processed = 0, replaced = 0, kept = 0;
  const results: any[] = [];
  let errorMessage: string | null = null;

  try {
    const { data: articles, error } = await supabase
      .from("articles")
      .select("id, title, category, image_url, image_score, image_caption")
      .eq("is_published", true)
      .not("image_url", "is", null);
    if (error) throw error;

    for (const a of articles ?? []) {
      processed++;
      console.log(`→ ${a.title}`);
      const queries = await genQueries(a.title, a.category);
      console.log(`  queries:`, queries);
      const cands: Cand[] = [];
      for (const q of queries) {
        const c = await unsplash(q);
        if (c && !cands.find((x) => x.url === c.url)) cands.push(c);
      }
      let best: { c: Cand; s: number; desc: string } | null = null;
      for (const c of cands) {
        const v = await score(c.url, a.title);
        if (!v) continue;
        console.log(`  · score=${v.score} — ${v.desc}`);
        if (!best || v.score > best.s) best = { c, s: v.score, desc: v.description };
      }
      if (!best || best.s < MIN_ACCEPT) {
        kept++;
        results.push({ id: a.id, title: a.title, action: "kept", best_score: best?.s ?? null });
        console.log(`  ✗ kept current (best ${best?.s ?? "n/a"})`);
        continue;
      }
      const { error: uErr } = await supabase.from("articles").update({
        image_url: best.c.url,
        image_caption: best.desc,
        image_credit: best.c.credit,
        image_score: best.s,
        image_verified: best.s >= 7,
      }).eq("id", a.id);
      if (uErr) {
        results.push({ id: a.id, title: a.title, action: "error", error: uErr.message });
      } else {
        replaced++;
        results.push({ id: a.id, title: a.title, action: "replaced", score: best.s, caption: best.desc });
        console.log(`  ✓ replaced (score ${best.s})`);
      }
    }
  } catch (e) {
    errorMessage = e instanceof Error ? e.message : String(e);
    console.error(e);
  }

  if (runId) {
    await supabase.from("pipeline_runs").update({
      status: errorMessage ? "error" : "success",
      finished_at: new Date().toISOString(),
      raw_fetched: processed,
      articles_created: replaced,
      error_message: errorMessage,
    }).eq("id", runId);
  }

  return new Response(JSON.stringify({ processed, replaced, kept, results }, null, 2), {
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
});
