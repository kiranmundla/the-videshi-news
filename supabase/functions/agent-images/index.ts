// agent-images: Find and attach images to articles missing image_url.
// Pipeline:
//   1. Claude Haiku extracts up to 3 ranked search keywords (always include "India" if relevant).
//   2. Try Wikipedia REST summary API for each keyword (most reliable, properly attributed).
//   3. Fallback to Unsplash, then Pexels.
//   4. Validate every candidate via Claude Haiku ("does this URL look relevant?") before saving.

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
const HAIKU_MODEL = "claude-haiku-4-5";

// ---------- Claude helpers ----------

async function callHaiku(prompt: string, maxTokens = 200): Promise<string> {
  if (!ANTHROPIC_API_KEY) return "";
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
        max_tokens: maxTokens,
        messages: [{ role: "user", content: prompt }],
      }),
    });
    if (!res.ok) {
      console.error("haiku error", res.status, await res.text());
      return "";
    }
    const data = await res.json();
    return data?.content?.[0]?.text?.trim() ?? "";
  } catch (e) {
    console.error("haiku exception", e);
    return "";
  }
}

async function extractKeywords(title: string, category: string): Promise<string[]> {
  const fallback = [title.replace(/[^A-Za-z0-9 ]/g, " ").split(/\s+/).slice(0, 4).join(" ").trim()];
  const prompt = `You generate image-search queries for an Indian-diaspora news site.

RULES:
- Identify the PRIMARY subject: a specific person, place, or named event.
- ALWAYS append "India" if the article is about India (it almost always is).
- NEVER return generic terms alone like "election", "democracy", "politics", "government".
- Return 3 ranked queries, most specific first, one per line, no numbering, no quotes.

EXAMPLES:
Title: "Mamata Banerjee refuses to resign after BJP victory in West Bengal"
Mamata Banerjee
West Bengal Chief Minister India
Bharatiya Janata Party West Bengal

Title: "Ernakulam Junction redevelopment to ease traffic"
Ernakulam Junction railway station India
Ernakulam railway station Kerala
Kochi railway India

Title: "Supreme Court questions CEC appointment law"
Supreme Court of India
Chief Election Commissioner India
Election Commission of India

Title: "Operation Sindoor one year on"
Operation Sindoor India Pakistan
Indian Army Operation Sindoor
India Pakistan border 2025

Title: "Vijay's TVK gains ground in Tamil Nadu"
Thalapathy Vijay actor
Tamilaga Vettri Kazhagam Tamil Nadu
Vijay TVK rally India

Now do this one.
Category: ${category}
Title: ${title}`;

  const out = await callHaiku(prompt, 150);
  if (!out) return fallback;
  const lines = out
    .split("\n")
    .map((l) => l.replace(/^[-*\d.\s"']+|["']+$/g, "").trim())
    .filter((l) => l.length > 1 && l.length < 80)
    .slice(0, 3);
  return lines.length ? lines : fallback;
}

async function isImageRelevant(imageUrl: string, title: string): Promise<boolean> {
  if (!ANTHROPIC_API_KEY) return true; // can't validate, accept
  // Pull filename + last path segments — that's all the signal we have without downloading.
  let signal = imageUrl;
  try {
    const u = new URL(imageUrl);
    signal = decodeURIComponent(u.pathname.split("/").slice(-2).join("/"));
  } catch (_e) { /* ignore */ }
  const prompt =
    `Article title: "${title}"\n` +
    `Image URL filename/path: "${signal}"\n\n` +
    `Could this image plausibly illustrate the article? ` +
    `Be lenient — accept anything topically related (person, place, institution, event). ` +
    `Reject only if clearly unrelated (e.g. wrong country, wrong person, generic stock unrelated to topic).\n` +
    `Answer with one word: yes or no.`;
  const ans = (await callHaiku(prompt, 5)).toLowerCase();
  if (!ans) return true;
  return ans.startsWith("y");
}

// ---------- Image sources ----------

type Hit = { url: string; credit: string };

async function searchWikipedia(keyword: string): Promise<Hit | null> {
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

async function searchUnsplash(keyword: string): Promise<Hit | null> {
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
    if (!imgUrl) return null;
    return { url: imgUrl, credit: "Photo: Unsplash" };
  } catch (e) {
    console.error("unsplash error", e);
    return null;
  }
}

async function searchPexels(keyword: string): Promise<Hit | null> {
  if (!PEXELS_API_KEY) return null;
  try {
    const url =
      `https://api.pexels.com/v1/search?query=${encodeURIComponent(keyword)}` +
      `&per_page=1&orientation=landscape`;
    const res = await fetch(url, { headers: { Authorization: PEXELS_API_KEY } });
    if (!res.ok) return null;
    const data = await res.json();
    const photo = data?.photos?.[0];
    if (!photo) return null;
    const imgUrl = photo.src?.large2x || photo.src?.large || photo.src?.original;
    if (!imgUrl) return null;
    return { url: imgUrl, credit: "Photo: Pexels" };
  } catch (e) {
    console.error("pexels error", e);
    return null;
  }
}

async function generateCaption(imageUrl: string, title: string): Promise<string> {
  let filename = "";
  try {
    const u = new URL(imageUrl);
    filename = decodeURIComponent(u.pathname.split("/").pop() ?? "");
  } catch (_e) { /* ignore */ }
  const prompt =
    `Image URL: ${imageUrl}\n` +
    `Filename: ${filename}\n` +
    `Article title: ${title}\n\n` +
    `Write a single short caption (max 10 words) describing what this specific image likely shows. ` +
    `Be specific — name the person, place, or object if identifiable from the filename. ` +
    `Do NOT repeat the article headline. No quotes, no trailing period.`;
  const out = await callHaiku(prompt, 40);
  return out.replace(/^["']|["'.]+$/g, "").trim();
}

async function findImage(title: string, category: string): Promise<Hit | null> {
  const keywords = await extractKeywords(title, category);
  console.log(`keywords for "${title}":`, keywords);

  // Pass 1: Wikipedia summary for each keyword (most likely to be on-topic).
  for (const kw of keywords) {
    const hit = await searchWikipedia(kw);
    if (hit && (await isImageRelevant(hit.url, title))) {
      console.log(`✓ wikipedia hit for "${kw}"`);
      return hit;
    }
  }

  // Pass 2: Unsplash.
  for (const kw of keywords) {
    const hit = await searchUnsplash(kw);
    if (hit && (await isImageRelevant(hit.url, title))) {
      console.log(`✓ unsplash hit for "${kw}"`);
      return hit;
    }
  }

  // Pass 3: Pexels.
  for (const kw of keywords) {
    const hit = await searchPexels(kw);
    if (hit && (await isImageRelevant(hit.url, title))) {
      console.log(`✓ pexels hit for "${kw}"`);
      return hit;
    }
  }

  return null;
}

// ---------- Main handler ----------

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
      .select("id, title, category, image_url, image_caption")
      .eq("is_published", true)
      .or("image_url.is.null,image_url.eq.,image_caption.is.null")
      .order("published_at", { ascending: false })
      .limit(MAX_PER_RUN);

    if (error) throw error;

    for (const a of articles ?? []) {
      processed++;
      const hit = await findImage(a.title, a.category);
      if (!hit) {
        console.log(`✗ no image found for: ${a.title}`);
        continue;
      }
      const caption = await generateCaption(hit.url, a.title);
      const { error: updErr } = await supabase
        .from("articles")
        .update({ image_url: hit.url, image_credit: hit.credit, image_caption: caption || null })
        .eq("id", a.id);
      if (updErr) {
        console.error(`update failed for ${a.id}`, updErr);
      } else {
        updated++;
        console.log(`✓ ${a.title} -> ${hit.url} | "${caption}"`);
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
