// agent-images: Vision-verified image fetcher.
//
// For each article without a verified image, gather up to 3 candidates
// (Wikipedia summary, Wikimedia Commons search, Unsplash), then ask
// Claude Haiku Vision to look at each and score 1-10 for relevance.
// Pick the highest scorer; require ≥7 to mark verified, accept 5-6 unverified,
// reject <5. Use the AI-generated description as the caption.

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const UNSPLASH_ACCESS_KEY = Deno.env.get("UNSPLASH_ACCESS_KEY") ?? "";
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY") ?? "";

const MAX_PER_RUN = 5;
const HAIKU_MODEL = "claude-haiku-4-5";
const ACCEPT_VERIFIED_MIN = 7;
const ACCEPT_UNVERIFIED_MIN = 3;

// ---------- Anthropic helpers ----------

async function callHaikuText(prompt: string, maxTokens = 200): Promise<string> {
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
      console.error("haiku text error", res.status, await res.text());
      return "";
    }
    const data = await res.json();
    return data?.content?.[0]?.text?.trim() ?? "";
  } catch (e) {
    console.error("haiku text exception", e);
    return "";
  }
}

type VisionVerdict = {
  description: string;
  relevant: boolean;
  is_real_photo: boolean;
  score: number;
};

async function verifyImage(
  imageUrl: string,
  articleTitle: string,
  category: string,
): Promise<VisionVerdict | null> {
  if (!ANTHROPIC_API_KEY) return null;
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
        max_tokens: 200,
        messages: [{
          role: "user",
          content: [
            { type: "image", source: { type: "url", url: imageUrl } },
            {
              type: "text",
              text:
`Article title: "${articleTitle}"
Category: ${category}

Look at this image and respond in JSON only (no prose, no code fences):
{"description": "8 words or fewer describing only what you see — no analysis, no relevance. e.g. 'Kolkata Victoria Memorial at dusk', 'Indian Air Force fighter jet'", "relevant": true|false, "is_real_photo": true|false, "score": 1-10}

Score criteria:
- 9-10: Perfect match — shows the exact person, place, or event named in the article.
- 7-8: Good match — clearly related to the article topic.
- 5-6: Loosely related, generic stock.
- 1-4: Wrong topic, misleading, or a flag/logo/diagram/chart/map/graphic.`,
            },
          ],
        }],
      }),
    });
    if (!res.ok) {
      console.error("vision error", res.status, await res.text());
      return null;
    }
    const data = await res.json();
    const text = (data?.content?.[0]?.text ?? "").trim();
    // Strip code fences if model added them
    const cleaned = text.replace(/^```(?:json)?\s*|\s*```$/g, "").trim();
    const match = cleaned.match(/\{[\s\S]*\}/);
    const json = match ? match[0] : cleaned;
    const parsed = JSON.parse(json);
    return {
      description: String(parsed.description ?? "").trim(),
      relevant: !!parsed.relevant,
      is_real_photo: !!parsed.is_real_photo,
      score: Number(parsed.score) || 0,
    };
  } catch (e) {
    console.error(`verify failed for ${imageUrl}`, e);
    return null;
  }
}

async function extractKeywords(title: string, category: string): Promise<string[]> {
  const fallback = [title.replace(/[^A-Za-z0-9 ]/g, " ").split(/\s+/).slice(0, 4).join(" ").trim()];
  const prompt = `You generate image-search queries for an Indian-diaspora news site.

RULES:
- Identify the PRIMARY subject: a specific person, place, or named event.
- ALWAYS append "India" if the article is about India.
- NEVER return generic terms alone like "election", "democracy", "politics", "government".
- Return 3 ranked queries, most specific first, one per line. No numbering, no quotes.

Category: ${category}
Title: ${title}`;
  const out = await callHaikuText(prompt, 150);
  if (!out) return fallback;
  const lines = out
    .split("\n")
    .map((l) => l.replace(/^[-*\d.\s"']+|["']+$/g, "").trim())
    .filter((l) => l.length > 1 && l.length < 80)
    .slice(0, 3);
  return lines.length ? lines : fallback;
}

// ---------- Image source candidates ----------

type Candidate = { url: string; credit: string; source: string };

function isAcceptableSize(w?: number, h?: number): boolean {
  if (!w || !h) return false;
  if (w <= h) return false; // landscape only
  if (w < 800) return false;
  return true;
}

async function wikipediaSummary(keyword: string): Promise<Candidate | null> {
  try {
    const slug = encodeURIComponent(keyword.trim().replace(/\s+/g, "_"));
    const res = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${slug}`, {
      headers: { "User-Agent": "TheVideshi/1.0 (https://thevideshi.com)" },
    });
    if (!res.ok) return null;
    const data = await res.json();
    const orig = data?.originalimage;
    const thumb = data?.thumbnail;
    // Prefer original if landscape & big enough, else thumbnail.
    let pick: { source?: string; width?: number; height?: number } | null = null;
    if (orig && isAcceptableSize(orig.width, orig.height)) pick = orig;
    else if (thumb && isAcceptableSize(thumb.width, thumb.height)) pick = thumb;
    if (!pick?.source) return null;
    return { url: pick.source, credit: "Photo: Wikimedia Commons", source: "wikipedia" };
  } catch (e) {
    console.error("wikipedia error", e);
    return null;
  }
}

async function commonsSearch(keyword: string): Promise<Candidate | null> {
  try {
    const u =
      `https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*` +
      `&generator=search&gsrnamespace=6&gsrlimit=8&gsrsearch=${encodeURIComponent(keyword)}` +
      `&prop=imageinfo&iiprop=url|mime|size&iiurlwidth=1200`;
    const res = await fetch(u, {
      headers: { "User-Agent": "TheVideshi/1.0 (https://thevideshi.com)" },
    });
    if (!res.ok) return null;
    const data = await res.json();
    const pages = data?.query?.pages;
    if (!pages) return null;
    for (const k of Object.keys(pages)) {
      const info = pages[k]?.imageinfo?.[0];
      const mime: string = info?.mime ?? "";
      if (!mime.startsWith("image/") || mime.includes("svg")) continue;
      const w = info.thumbwidth || info.width;
      const h = info.thumbheight || info.height;
      if (!isAcceptableSize(w, h)) continue;
      const url = info.thumburl || info.url;
      if (!url) continue;
      return { url, credit: "Photo: Wikimedia Commons", source: "commons" };
    }
    return null;
  } catch (e) {
    console.error("commons error", e);
    return null;
  }
}

async function unsplashSearch(keyword: string): Promise<Candidate | null> {
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
    return { url: imgUrl, credit: "Photo: Unsplash", source: "unsplash" };
  } catch (e) {
    console.error("unsplash error", e);
    return null;
  }
}

async function gatherCandidates(
  title: string,
  category: string,
): Promise<Candidate[]> {
  const keywords = await extractKeywords(title, category);
  console.log(`keywords for "${title}":`, keywords);
  const primary = keywords[0] ?? title;
  const list: (Candidate | null)[] = await Promise.all([
    wikipediaSummary(primary),
    commonsSearch(primary),
    unsplashSearch(keywords[1] ?? primary),
  ]);
  // dedupe by url
  const seen = new Set<string>();
  return list.filter((c): c is Candidate => {
    if (!c) return false;
    if (seen.has(c.url)) return false;
    seen.add(c.url);
    return true;
  });
}

// ---------- Main handler ----------

type ChosenImage = {
  url: string;
  credit: string;
  caption: string;
  score: number;
  verified: boolean;
};

async function pickBestImage(
  title: string,
  category: string,
): Promise<ChosenImage | null> {
  const candidates = await gatherCandidates(title, category);
  if (candidates.length === 0) return null;

  let best: { c: Candidate; v: VisionVerdict } | null = null;
  for (const c of candidates) {
    const v = await verifyImage(c.url, title, category);
    if (!v) continue;
    console.log(`  · ${c.source} score=${v.score} photo=${v.is_real_photo} — ${v.description}`);
    if (!v.is_real_photo) continue;
    if (!best || v.score > best.v.score) best = { c, v };
  }
  if (!best) return null;
  if (best.v.score < ACCEPT_UNVERIFIED_MIN) return null;
  return {
    url: best.c.url,
    credit: best.c.credit,
    caption: best.v.description,
    score: best.v.score,
    verified: best.v.score >= ACCEPT_VERIFIED_MIN,
  };
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
    // Upgrade-only mode: re-evaluate articles whose existing image is unverified
    // or scored below 8, and replace ONLY if we find something strictly better.
    // Never delete an existing image.
    const { data: articles, error } = await supabase
      .from("articles")
      .select("id, title, category, image_url, image_verified, image_score")
      .eq("is_published", true)
      .not("image_url", "is", null)
      .or("image_verified.eq.false,image_score.is.null,image_score.lt.8")
      .order("published_at", { ascending: false })
      .limit(MAX_PER_RUN);

    if (error) throw error;

    for (const a of articles ?? []) {
      processed++;
      console.log(`→ ${a.title} (current score=${a.image_score ?? "?"})`);
      const chosen = await pickBestImage(a.title, a.category);
      if (!chosen) {
        console.log(`· no candidate beat current — keeping existing image`);
        continue;
      }
      const currentScore = a.image_score ?? 0;
      if (chosen.score <= currentScore) {
        console.log(`· candidate score=${chosen.score} ≤ current ${currentScore} — keeping`);
        continue;
      }
      const { error: updErr } = await supabase
        .from("articles")
        .update({
          image_url: chosen.url,
          image_caption: chosen.caption,
          image_credit: chosen.credit,
          image_verified: chosen.verified,
          image_score: chosen.score,
        })
        .eq("id", a.id);
      if (updErr) {
        console.error(`update failed for ${a.id}`, updErr);
      } else {
        updated++;
        console.log(`✓ upgraded ${a.title} ${currentScore} → ${chosen.score}`);
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
