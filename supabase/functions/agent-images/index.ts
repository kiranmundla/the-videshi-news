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
const PEXELS_API_KEY = Deno.env.get("PEXELS_API_KEY") ?? "";
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY") ?? "";

const MAX_PER_RUN = 10;
const HAIKU_MODEL = "claude-haiku-4-5";
const ACCEPT_VERIFIED_MIN = 8;
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
      signal: AbortSignal.timeout(50000),
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
type SubjectType = "PERSON" | "PLACE" | "EVENT" | "TOPIC";
type Classification = { type: SubjectType; subject: string; keyword: string };

type VisionVerdict = {
  description: string;
  shows_subject: boolean;
  is_real_photo: boolean;
  score: number;
};

async function classifySubject(title: string, firstPara: string, category: string): Promise<Classification> {
  const prompt = `Classify this article's primary subject.

Title: "${title}"
First paragraph: "${(firstPara || "").slice(0, 600)}"
Category: ${category}

Return JSON only:
{"type":"PERSON|PLACE|EVENT|TOPIC","subject":"specific name","keyword":"1-2 word general topic for stock fallback"}

Rules:
- PERSON if mainly about a named individual — full common name.
- PLACE if mainly about a specific city/state/landmark — that place name.
- EVENT if mainly about a specific event/incident.
- TOPIC if it's a general topic/issue.
- Never return generic words like "election", "policy", "news".`;
  const out = await callHaikuText(prompt, 200);
  try {
    const cleaned = out.replace(/^```(?:json)?\s*|\s*```$/g, "").trim();
    const m = cleaned.match(/\{[\s\S]*\}/);
    const j = JSON.parse(m ? m[0] : cleaned);
    const rawType = String(j.type || "TOPIC").toUpperCase();
    const type: SubjectType = (["PERSON", "PLACE", "EVENT", "TOPIC"].includes(rawType) ? rawType : "TOPIC") as SubjectType;
    return {
      type,
      subject: String(j.subject || title.split(/[:|—-]/)[0]).trim(),
      keyword: String(j.keyword || category).trim(),
    };
  } catch {
    return { type: "TOPIC", subject: title, keyword: category };
  }
}

async function verifyImage(imageUrl: string, c: Classification): Promise<VisionVerdict | null> {
  if (!ANTHROPIC_API_KEY) return null;
  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json" },
      body: JSON.stringify({
        model: HAIKU_MODEL,
        max_tokens: 200,
        messages: [{
          role: "user",
          content: [
            { type: "image", source: { type: "url", url: imageUrl } },
            { type: "text", text:
`Article subject: ${c.type} = "${c.subject}".

Does this image show ${c.subject}? Score 1-10 where 10 = clearly shows the exact ${c.type === "PERSON" ? "person" : c.type === "PLACE" ? "place" : "subject"}, 1 = unrelated.

Reply JSON only: {"score": N, "shows_subject": true|false, "is_real_photo": true|false, "description": "5 words or fewer — subject and location only, no verbs"}` },
          ],
        }],
      }),
      signal: AbortSignal.timeout(50000),
    });
    if (!res.ok) { console.error("vision error", res.status, await res.text()); return null; }
    const data = await res.json();
    const text = (data?.content?.[0]?.text ?? "").trim().replace(/^```(?:json)?\s*|\s*```$/g, "");
    const match = text.match(/\{[\s\S]*\}/);
    const parsed = JSON.parse(match ? match[0] : text);
    return {
      description: String(parsed.description ?? "").trim(),
      shows_subject: !!parsed.shows_subject,
      is_real_photo: parsed.is_real_photo !== false,
      score: Number(parsed.score) || 0,
    };
  } catch (e) {
    console.error(`verify failed for ${imageUrl}`, e);
    return null;
  }
}

// ---------- Image source candidates ----------

type Candidate = { url: string; credit: string; source: string };

function isLandscape(w?: number, h?: number, minW = 800): boolean {
  return !!(w && h && w > h && w >= minW);
}

function isAcceptablePortrait(w?: number, h?: number): boolean {
  return !!(w && h && w >= 400 && h >= 400);
}

async function wikipediaSummary(keyword: string, allowPortrait: boolean): Promise<Candidate | null> {
  try {
    const slug = encodeURIComponent(keyword.trim().replace(/\s+/g, "_"));
    const res = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${slug}`, {
      headers: { "User-Agent": "TheVideshi/1.0 (https://thevideshi.com)" },
    });
    if (!res.ok) return null;
    const data = await res.json();
    const orig = data?.originalimage;
    const thumb = data?.thumbnail;
    const ok = (img: any) => img?.source && (allowPortrait ? isAcceptablePortrait(img.width, img.height) : isLandscape(img.width, img.height));
    const pick = ok(orig) ? orig : ok(thumb) ? thumb : null;
    if (!pick?.source) return null;
    return { url: pick.source, credit: "Photo: Wikipedia", source: "Wikipedia" };
  } catch (e) { console.error("wikipedia error", e); return null; }
}

async function commonsSearch(keyword: string, allowPortrait: boolean): Promise<Candidate | null> {
  try {
    const u =
      `https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*` +
      `&generator=search&gsrnamespace=6&gsrlimit=8&gsrsearch=${encodeURIComponent(keyword)}` +
      `&prop=imageinfo&iiprop=url|mime|size&iiurlwidth=1200`;
    const res = await fetch(u, { headers: { "User-Agent": "TheVideshi/1.0 (https://thevideshi.com)" } });
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
      if (allowPortrait ? !isAcceptablePortrait(w, h) : !isLandscape(w, h)) continue;
      const url = info.thumburl || info.url;
      if (!url) continue;
      return { url, credit: "Photo: Wikimedia Commons", source: "Wikimedia Commons" };
    }
    return null;
  } catch (e) { console.error("commons error", e); return null; }
}

async function unsplashSearch(keyword: string): Promise<Candidate | null> {
  if (!UNSPLASH_ACCESS_KEY) return null;
  try {
    const url = `https://api.unsplash.com/search/photos?query=${encodeURIComponent(keyword)}&per_page=3&orientation=landscape&content_filter=high`;
    const res = await fetch(url, { headers: { Authorization: `Client-ID ${UNSPLASH_ACCESS_KEY}` } });
    if (!res.ok) return null;
    const data = await res.json();
    const photo = data?.results?.[0];
    if (!photo) return null;
    const imgUrl = photo.urls?.regular || photo.urls?.full;
    if (!imgUrl) return null;
    return { url: imgUrl, credit: "Photo: Unsplash", source: "Unsplash" };
  } catch (e) { console.error("unsplash error", e); return null; }
}

async function pexelsSearch(keyword: string): Promise<Candidate | null> {
  if (!PEXELS_API_KEY) return null;
  try {
    const u = `https://api.pexels.com/v1/search?query=${encodeURIComponent(keyword)}&per_page=3&orientation=landscape`;
    const res = await fetch(u, { headers: { Authorization: PEXELS_API_KEY } });
    if (!res.ok) return null;
    const data = await res.json();
    const p = data?.photos?.[0];
    const url = p?.src?.large2x || p?.src?.large || p?.src?.original;
    return url ? { url, credit: "Photo: Pexels", source: "Pexels" } : null;
  } catch (e) { console.error("pexels error", e); return null; }
}

async function gatherCandidates(c: Classification, category: string): Promise<Candidate[]> {
  console.log(`classification: type=${c.type} subject="${c.subject}" keyword="${c.keyword}"`);
  let raw: (Candidate | null)[] = [];
  switch (c.type) {
    case "PERSON":
      raw = await Promise.all([
        wikipediaSummary(c.subject, true),
        commonsSearch(c.subject, true),
      ]);
      break;
    case "PLACE":
      raw = await Promise.all([
        wikipediaSummary(c.subject, false),
        commonsSearch(`${c.subject} India`, false),
        unsplashSearch(`${c.subject} India`),
      ]);
      break;
    case "EVENT":
      raw = await Promise.all([
        commonsSearch(c.subject, false),
        unsplashSearch(`${c.keyword || c.subject} India`),
        pexelsSearch(`${c.keyword || c.subject} India`),
      ]);
      break;
    case "TOPIC":
    default:
      raw = await Promise.all([
        unsplashSearch(`${c.keyword || c.subject} India`),
        pexelsSearch(`${c.keyword || c.subject} India`),
        unsplashSearch(`India ${category || "news"}`),
      ]);
  }
  const seen = new Set<string>();
  return raw.filter((x): x is Candidate => {
    if (!x || seen.has(x.url)) return false;
    seen.add(x.url);
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
  subject_type: SubjectType;
  subject_name: string;
};

async function uploadToStorage(
  supabase: ReturnType<typeof createClient>,
  sourceUrl: string,
  articleId: string,
): Promise<string | null> {
  try {
    const r = await fetch(sourceUrl, {
      headers: { "User-Agent": "TheVideshi/1.0 (https://thevideshi.com)" },
    });
    if (!r.ok) {
      console.error(`download failed ${r.status} for ${sourceUrl}`);
      return null;
    }
    const buf = await r.arrayBuffer();
    const contentType = r.headers.get("content-type") || "image/jpeg";
    const ext = contentType.includes("png") ? "png" : contentType.includes("webp") ? "webp" : "jpg";
    const filename = `${articleId}-${Date.now()}.${ext}`;
    const { error } = await supabase.storage
      .from("article-images")
      .upload(filename, buf, { contentType, cacheControl: "31536000", upsert: false });
    if (error) { console.error("storage upload error", error); return null; }
    const { data: { publicUrl } } = supabase.storage.from("article-images").getPublicUrl(filename);
    return publicUrl;
  } catch (e) { console.error("uploadToStorage exception", e); return null; }
}

async function isImageUrlInUse(
  supabase: ReturnType<typeof createClient>,
  url: string,
  excludeArticleId?: string,
): Promise<boolean> {
  let q = supabase.from("articles").select("id", { count: "exact", head: true }).eq("image_url", url).eq("is_published", true);
  if (excludeArticleId) q = q.neq("id", excludeArticleId);
  const { count, error } = await q;
  if (error) { console.error("dedupe check failed", error); return false; }
  return (count ?? 0) > 0;
}

function firstParagraphFromBody(body: unknown): string {
  if (typeof body === "string") {
    const m = body.match(/[^\n]{40,}/);
    return m ? m[0] : body.slice(0, 400);
  }
  if (Array.isArray(body)) {
    const p = body.find((b: any) => b?.type === "paragraph" && typeof b.content === "string");
    if (p) return p.content as string;
  }
  return "";
}

async function pickBestImage(
  title: string,
  body: unknown,
  category: string,
  supabase: ReturnType<typeof createClient>,
  articleId: string,
  existingClass?: { type: SubjectType; subject: string } | null,
): Promise<ChosenImage | null> {
  const classification: Classification = existingClass
    ? { type: existingClass.type, subject: existingClass.subject, keyword: category }
    : await classifySubject(title, firstParagraphFromBody(body), category);

  const candidates = await gatherCandidates(classification, category);
  if (candidates.length === 0) return null;

  let best: { c: Candidate; v: VisionVerdict } | null = null;
  for (const c of candidates) {
    if (await isImageUrlInUse(supabase, c.url, articleId)) {
      console.log(`  · skip ${c.source} — url already used`);
      continue;
    }
    const v = await verifyImage(c.url, classification);
    if (!v) continue;
    console.log(`  · ${c.source} score=${v.score} shows=${v.shows_subject} — ${v.description}`);
    if (!v.is_real_photo) continue;
    if (v.score >= 7) {
      return {
        url: c.url,
        credit: c.credit,
        caption: `${v.description || classification.subject} · Photo: ${c.source}`,
        score: v.score,
        verified: true,
        subject_type: classification.type,
        subject_name: classification.subject,
      };
    }
    if (!best || v.score > best.v.score) best = { c, v };
  }
  if (!best) return null;
  if (best.v.score < ACCEPT_UNVERIFIED_MIN) return null;
  return {
    url: best.c.url,
    credit: best.c.credit,
    caption: `${best.v.description || classification.subject} · Photo: ${best.c.source}`,
    score: best.v.score,
    verified: false,
    subject_type: classification.type,
    subject_name: classification.subject,
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
    // Process only articles that aren't "good enough":
    //   - no image yet, OR
    //   - image_score < 8 (always retry to try to beat it), OR
    //   - image_url is still an external (non-supabase) URL.
    // Once score >= 8 AND self-hosted, mark verified and never touch again.
    const { data: articles, error } = await supabase
      .from("articles")
      .select("id, title, body, category, image_url, image_verified, image_score, subject_type, subject_name")
      .eq("is_published", true)
      .or("image_url.is.null,image_score.is.null,image_score.lt.8,image_url.not.ilike.%supabase%")
      .order("published_at", { ascending: false })
      .limit(MAX_PER_RUN);

    if (error) throw error;

    for (const a of articles ?? []) {
      processed++;
      console.log(`→ ${a.title} (current score=${a.image_score ?? "?"})`);
      const existingClass = a.subject_type && a.subject_name
        ? { type: a.subject_type as SubjectType, subject: a.subject_name }
        : null;
      const chosen = await pickBestImage(a.title, a.body, a.category, supabase, a.id, existingClass);
      if (!chosen) {
        console.log(`· no candidate beat current — keeping existing image`);
        continue;
      }
      const currentScore = a.image_score ?? 0;
      if (chosen.score <= currentScore) {
        console.log(`· candidate score=${chosen.score} ≤ current ${currentScore} — keeping`);
        continue;
      }
      const hostedUrl = await uploadToStorage(supabase, chosen.url, a.id);
      if (!hostedUrl) {
        console.error(`· upload to storage failed — keeping existing`);
        continue;
      }
      const { error: updErr } = await supabase
        .from("articles")
        .update({
          image_url: hostedUrl,
          image_caption: chosen.caption,
          image_credit: chosen.credit,
          image_verified: chosen.verified,
          image_score: chosen.score,
          subject_type: chosen.subject_type,
          subject_name: chosen.subject_name,
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
