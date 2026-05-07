// agent-images: Find and attach images to articles missing image_url.
// Strategy: Claude Haiku extracts best keyword -> Wikipedia REST summary
// -> Unsplash -> Pexels. Stores source URL in articles.image_url + image_credit.

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const UNSPLASH_ACCESS_KEY = Deno.env.get("UNSPLASH_ACCESS_KEY") ?? "";
const PEXELS_API_KEY = Deno.env.get("PEXELS_API_KEY") ?? "";
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY") ?? "";

const MAX_PER_RUN = 10;

async function extractKeyword(title: string, category: string): Promise<string> {
  if (!ANTHROPIC_API_KEY) {
    // Fallback: strip punctuation, take first 3 words
    return title.replace(/[^A-Za-z0-9 ]/g, " ").split(/\s+/).slice(0, 3).join(" ").trim();
  }
  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5",
        max_tokens: 50,
        messages: [
          {
            role: "user",
            content:
              `Extract the single best image-search keyword from this news headline. ` +
              `For news (politics/business/world) prefer the main person or place name. ` +
              `For lifestyle/travel/sports/food/culture use the main topic. ` +
              `Return ONLY the keyword, no quotes, no punctuation, max 4 words.\n\n` +
              `Category: ${category}\nHeadline: ${title}`,
          },
        ],
      }),
    });
    if (!res.ok) throw new Error(`anthropic ${res.status}`);
    const data = await res.json();
    const text = data?.content?.[0]?.text?.trim() ?? "";
    return text.replace(/^["']|["']$/g, "").slice(0, 80) || title;
  } catch (e) {
    console.error("extractKeyword error", e);
    return title.split(/\s+/).slice(0, 3).join(" ");
  }
}

async function searchWikipedia(keyword: string): Promise<{ url: string; credit: string } | null> {
  try {
    const slug = encodeURIComponent(keyword.trim().replace(/\s+/g, "_"));
    const res = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${slug}`, {
      headers: { "User-Agent": "TheVideshi/1.0 (https://thevideshi.com)" },
    });
    if (!res.ok) return null;
    const data = await res.json();
    const url = data?.originalimage?.source || data?.thumbnail?.source;
    if (!url) return null;
    return { url, credit: "Photo: Wikimedia Commons" };
  } catch (e) {
    console.error("wikipedia error", e);
    return null;
  }
}

async function searchUnsplash(keyword: string): Promise<{ url: string; credit: string } | null> {
  if (!UNSPLASH_ACCESS_KEY) return null;
  try {
    const url =
      `https://api.unsplash.com/search/photos?query=${encodeURIComponent(keyword)}` +
      `&per_page=1&orientation=landscape&content_filter=high`;
    const res = await fetch(url, {
      headers: { Authorization: `Client-ID ${UNSPLASH_ACCESS_KEY}` },
    });
    if (!res.ok) return null;
    const data = await res.json();
    const photo = data?.results?.[0];
    if (!photo) return null;
    const imgUrl = photo.urls?.regular || photo.urls?.full;
    const name = photo.user?.name ?? "Unknown";
    return { url: imgUrl, credit: `Photo: ${name} / Unsplash` };
  } catch (e) {
    console.error("unsplash error", e);
    return null;
  }
}

async function searchPexels(keyword: string): Promise<{ url: string; credit: string } | null> {
  if (!PEXELS_API_KEY) return null;
  try {
    const url =
      `https://api.pexels.com/v1/search?query=${encodeURIComponent(keyword)}` +
      `&per_page=1&orientation=landscape`;
    const res = await fetch(url, {
      headers: { Authorization: PEXELS_API_KEY },
    });
    if (!res.ok) return null;
    const data = await res.json();
    const photo = data?.photos?.[0];
    if (!photo) return null;
    const imgUrl = photo.src?.large2x || photo.src?.large || photo.src?.original;
    const name = photo.photographer ?? "Unknown";
    return { url: imgUrl, credit: `Photo: ${name} / Pexels` };
  } catch (e) {
    console.error("pexels error", e);
    return null;
  }
}

async function findImage(title: string, category: string): Promise<{ url: string; credit: string } | null> {
  const keyword = await extractKeyword(title, category);
  console.log(`keyword for "${title}" -> "${keyword}"`);

  const wiki = await searchWikipedia(keyword);
  if (wiki) return wiki;

  const uns = await searchUnsplash(keyword);
  if (uns) return uns;

  const px = await searchPexels(keyword);
  if (px) return px;

  return null;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

  const { data: run, error: runErr } = await supabase
    .from("pipeline_runs")
    .insert({ run_type: "images", status: "running" })
    .select()
    .single();
  if (runErr) console.error("failed to create pipeline_runs row", runErr);
  const runId = run?.id;

  let processed = 0;
  let updated = 0;
  let errorMessage: string | null = null;

  try {
    const { data: articles, error } = await supabase
      .from("articles")
      .select("id, title, category, image_url")
      .eq("is_published", true)
      .or("image_url.is.null,image_url.eq.")
      .order("published_at", { ascending: false })
      .limit(MAX_PER_RUN);

    if (error) throw error;

    for (const a of articles ?? []) {
      processed++;
      const hit = await findImage(a.title, a.category);
      if (!hit) {
        console.log(`no image found for: ${a.title}`);
        continue;
      }
      const { error: updErr } = await supabase
        .from("articles")
        .update({ image_url: hit.url, image_credit: hit.credit })
        .eq("id", a.id);
      if (updErr) {
        console.error(`update failed for ${a.id}`, updErr);
      } else {
        updated++;
        console.log(`✓ ${a.title} -> ${hit.url}`);
      }
    }
  } catch (e) {
    errorMessage = e instanceof Error ? e.message : String(e);
    console.error("agent-images error", e);
  }

  if (runId) {
    await supabase
      .from("pipeline_runs")
      .update({
        status: errorMessage ? "error" : "success",
        finished_at: new Date().toISOString(),
        raw_fetched: processed,
        articles_created: updated,
        error_message: errorMessage,
      })
      .eq("id", runId);
  }

  return new Response(
    JSON.stringify({ processed, updated, error: errorMessage }),
    { headers: { ...corsHeaders, "Content-Type": "application/json" } },
  );
});
