// agent-images: Find and attach images to articles missing image_url.
// Strategy: Wikimedia Commons first (free, great for politicians/landmarks),
// then Unsplash fallback (lifestyle/travel/generic).
// Stores source URL directly in articles.image_url + image_credit.

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const UNSPLASH_ACCESS_KEY = Deno.env.get("UNSPLASH_ACCESS_KEY") ?? "";

const MAX_PER_RUN = 10;

const STOPWORDS = new Set([
  "the","a","an","and","or","but","of","in","on","at","to","for","with","by",
  "from","as","is","are","was","were","be","been","being","this","that","these",
  "those","it","its","into","over","after","before","amid","amidst","says","said",
  "new","amid","up","down","out","off","near","vs","vs.","over","under","about"
]);

function pickKeywords(title: string, tags: string[] | null, limit = 4): string[] {
  const fromTags = (tags ?? [])
    .map(t => t.trim())
    .filter(t => t.length > 1)
    .slice(0, 3);
  const titleWords = title
    .replace(/[^A-Za-z0-9 \-]/g, " ")
    .split(/\s+/)
    .filter(w => w.length > 2 && !STOPWORDS.has(w.toLowerCase()))
    .slice(0, 6);
  const merged = [...fromTags, ...titleWords];
  // dedupe (case-insensitive)
  const seen = new Set<string>();
  const out: string[] = [];
  for (const w of merged) {
    const k = w.toLowerCase();
    if (!seen.has(k)) {
      seen.add(k);
      out.push(w);
    }
    if (out.length >= limit) break;
  }
  return out;
}

async function searchWikimedia(query: string): Promise<{ url: string; credit: string } | null> {
  try {
    // Step 1: search for files matching query
    const searchUrl =
      `https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*` +
      `&generator=search&gsrnamespace=6&gsrlimit=5&gsrsearch=${encodeURIComponent(query)}` +
      `&prop=imageinfo&iiprop=url|extmetadata|mime&iiurlwidth=1200`;
    const res = await fetch(searchUrl, {
      headers: { "User-Agent": "TheVideshi/1.0 (https://thevideshi.com)" },
    });
    if (!res.ok) return null;
    const data = await res.json();
    const pages = data?.query?.pages;
    if (!pages) return null;
    for (const k of Object.keys(pages)) {
      const p = pages[k];
      const info = p?.imageinfo?.[0];
      if (!info) continue;
      const mime: string = info.mime ?? "";
      if (!mime.startsWith("image/")) continue;
      if (mime.includes("svg")) continue;
      const url = info.thumburl || info.url;
      if (!url) continue;
      const artist = info.extmetadata?.Artist?.value
        ?.replace(/<[^>]+>/g, "")
        ?.trim();
      const credit = artist
        ? `Photo: ${artist} / Wikimedia Commons`
        : "Photo: Wikimedia Commons";
      return { url, credit };
    }
    return null;
  } catch (e) {
    console.error("wikimedia error", e);
    return null;
  }
}

async function searchUnsplash(query: string): Promise<{ url: string; credit: string } | null> {
  if (!UNSPLASH_ACCESS_KEY) return null;
  try {
    const url =
      `https://api.unsplash.com/search/photos?query=${encodeURIComponent(query)}` +
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
    const credit = `Photo: ${name} / Unsplash`;
    return { url: imgUrl, credit };
  } catch (e) {
    console.error("unsplash error", e);
    return null;
  }
}

async function findImage(title: string, tags: string[] | null, category: string): Promise<{ url: string; credit: string } | null> {
  const keywords = pickKeywords(title, tags);

  // Try multi-keyword Wikimedia query (good for "Mamata Banerjee", "BJP", landmarks)
  const wikiQueries = [
    keywords.slice(0, 2).join(" "),
    keywords[0],
  ].filter(q => q && q.length > 1);

  for (const q of wikiQueries) {
    const hit = await searchWikimedia(q);
    if (hit) return hit;
  }

  // Unsplash fallback — better for travel/lifestyle/generic
  const unsplashQueries = [
    keywords.slice(0, 2).join(" "),
    keywords[0],
    category,
  ].filter(q => q && q.length > 1);

  for (const q of unsplashQueries) {
    const hit = await searchUnsplash(q);
    if (hit) return hit;
  }

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
  if (runErr) {
    console.error("failed to create pipeline_runs row", runErr);
  }
  const runId = run?.id;

  let processed = 0;
  let updated = 0;
  let errorMessage: string | null = null;

  try {
    const { data: articles, error } = await supabase
      .from("articles")
      .select("id, title, tags, category, image_url")
      .eq("is_published", true)
      .or("image_url.is.null,image_url.eq.")
      .order("published_at", { ascending: false })
      .limit(MAX_PER_RUN);

    if (error) throw error;

    for (const a of articles ?? []) {
      processed++;
      const hit = await findImage(a.title, a.tags as string[] | null, a.category);
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
