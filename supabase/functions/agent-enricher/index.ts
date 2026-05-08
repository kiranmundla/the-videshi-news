// agent-enricher: claims an 'enriching' job and produces a rich, diaspora-focused article structure.
import { createClient, type SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";
import {
  callClaudeResilient,
  logAlert,
  sendAlertEmail,
  moveToDLQ,
} from "../_shared/resilience.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const AGENT = "agent-enricher";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY")!;
const UNSPLASH_ACCESS_KEY = Deno.env.get("UNSPLASH_ACCESS_KEY") ?? "";
const MODEL = "claude-haiku-4-5-20251001";
const VISION_MODEL = "claude-haiku-4-5";

let _sb: SupabaseClient;
let _jobId: string | undefined;

// ---------------- Google News URL unwrap ----------------
// Google News RSS items use opaque news.google.com/rss/articles/... redirect URLs.
// Try to follow them to the real publisher URL. HEAD is faster than GET.
// Google now serves a JS interstitial in many cases, so unwrapping often no-ops;
// per spec we keep the original URL on any failure.
async function unwrapGoogleNewsUrl(url: string): Promise<{ url: string; domain: string | null }> {
  try {
    const u = new URL(url);
    if (!u.hostname.includes("news.google.com")) {
      return { url, domain: u.hostname.replace(/^www\./, "") };
    }
    const res = await fetch(url, {
      method: "HEAD",
      redirect: "follow",
      signal: AbortSignal.timeout(5000),
      headers: { "User-Agent": "Mozilla/5.0 TheVideshi/1.0" },
    });
    const finalUrl = res.url;
    const finalHost = new URL(finalUrl).hostname;
    if (finalUrl !== url && !finalHost.includes("news.google.com")) {
      return { url: finalUrl, domain: finalHost.replace(/^www\./, "") };
    }
  } catch (e) {
    console.warn(`[enricher] gnews unwrap failed for ${url}: ${(e as Error).message}`);
  }
  return { url, domain: null };
}

async function unwrapDraftSources(draft: any): Promise<void> {
  if (!draft || !Array.isArray(draft.sources_used)) return;
  let unwrapped = 0;
  for (const s of draft.sources_used) {
    if (typeof s?.url !== "string" || !s.url.includes("news.google.com")) continue;
    const { url: realUrl, domain } = await unwrapGoogleNewsUrl(s.url);
    if (realUrl !== s.url) {
      s.url = realUrl;
      if (domain && (!s.name || /^google news/i.test(s.name))) s.name = domain;
      unwrapped++;
    }
  }
  if (unwrapped > 0) console.log(`[enricher] unwrapped ${unwrapped} google-news source URL(s)`);
}

// ---------------- Image fetching helpers ----------------

type ImageResult = {
  image_url: string;
  image_caption: string;
  image_credit: string;
  image_verified: boolean;
  image_score: number;
};

async function anthropicFetch(body: any): Promise<any> {
  return await callClaudeResilient({
    apiKey: ANTHROPIC_API_KEY,
    body,
    agent: AGENT,
    jobId: _jobId,
    supabase: _sb,
  });
}

async function haikuJson(prompt: string, maxTokens = 200): Promise<any | null> {
  try {
    const data = await anthropicFetch({
      model: VISION_MODEL,
      max_tokens: maxTokens,
      messages: [{ role: "user", content: prompt }],
    });
    const text = (data?.content?.[0]?.text ?? "").trim();
    const cleaned = text.replace(/^```(?:json)?\s*|\s*```$/g, "").trim();
    const m = cleaned.match(/\{[\s\S]*\}/);
    return JSON.parse(m ? m[0] : cleaned);
  } catch (e) {
    console.error("haikuJson error", e);
    return null;
  }
}

type SubjectType = "PERSON" | "PLACE" | "EVENT" | "TOPIC";
type Classification = { type: SubjectType; subject: string; keyword: string };

async function classifySubject(title: string, firstPara: string, category: string): Promise<Classification> {
  const out = await haikuJson(
    `Classify this article's primary subject.

Title: "${title}"
First paragraph: "${(firstPara || "").slice(0, 600)}"
Category: ${category}

Return JSON only:
{"type":"PERSON|PLACE|EVENT|TOPIC","subject":"specific name","keyword":"1-2 word general topic for stock fallback"}

Rules:
- PERSON if mainly about a named individual — set subject to their full common name.
- PLACE if mainly about a specific city/state/landmark — set subject to that place name.
- EVENT if mainly about a specific event/incident — set subject to its main keyword/name.
- TOPIC if it's a general topic/issue — set subject to the main keyword.
- Never return generic words like "election", "policy", "news".`,
    200,
  );
  const rawType = String(out?.type || "TOPIC").toUpperCase();
  const type: SubjectType = (["PERSON", "PLACE", "EVENT", "TOPIC"].includes(rawType) ? rawType : "TOPIC") as SubjectType;
  const subject = String(out?.subject || title.split(/[:|—-]/)[0].trim()).trim();
  const keyword = String(out?.keyword || category).trim();
  return { type, subject, keyword };
}

function isLandscape(w?: number, h?: number, minW = 800): boolean {
  return !!(w && h && w > h && w >= minW);
}

const BAD_PATTERNS = /flag|banner|logo|diagram|chart|map|sankey|poll|report|icon|symbol|svg/i;

async function tryWikipedia(subject: string, allowPortrait: boolean): Promise<{ url: string; credit: string; source: string } | null> {
  try {
    const slug = encodeURIComponent(subject.trim().replace(/\s+/g, "_"));
    const res = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${slug}`, {
      headers: { "User-Agent": "TheVideshi/1.0" },
    });
    if (!res.ok) return null;
    const d = await res.json();
    const orig = d?.originalimage;
    const thumb = d?.thumbnail;
    const acceptable = (img: any) => {
      if (!img?.source) return false;
      const w = img.width, h = img.height;
      if (!w || !h) return false;
      if (allowPortrait) return w >= 400 && h >= 400;
      return w > h && w >= 800;
    };
    const pick = acceptable(orig) ? orig : acceptable(thumb) ? thumb : null;
    if (!pick?.source) return null;
    return { url: pick.source, credit: "Wikipedia", source: "Wikipedia" };
  } catch { return null; }
}

async function tryCommons(subject: string, allowPortrait: boolean): Promise<{ url: string; credit: string; source: string } | null> {
  try {
    const u = `https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&generator=search&gsrnamespace=6&gsrlimit=8&gsrsearch=${encodeURIComponent(subject)}&prop=imageinfo&iiprop=url|mime|size&iiurlwidth=1200`;
    const res = await fetch(u, { headers: { "User-Agent": "TheVideshi/1.0" } });
    if (!res.ok) return null;
    const d = await res.json();
    const pages = d?.query?.pages;
    if (!pages) return null;
    for (const k of Object.keys(pages)) {
      const info = pages[k]?.imageinfo?.[0];
      const mime: string = info?.mime ?? "";
      if (mime !== "image/jpeg") continue;
      const w = info.thumbwidth || info.width;
      const h = info.thumbheight || info.height;
      if (!w || !h) continue;
      if (!allowPortrait && !isLandscape(w, h)) continue;
      if (allowPortrait && (w < 400 || h < 400)) continue;
      const url = info.thumburl || info.url;
      if (!url || BAD_PATTERNS.test(url)) continue;
      return { url, credit: "Wikimedia Commons", source: "Wikimedia Commons" };
    }
    return null;
  } catch { return null; }
}

async function tryUnsplash(keyword: string): Promise<{ url: string; credit: string; source: string } | null> {
  if (!UNSPLASH_ACCESS_KEY) return null;
  try {
    const u = `https://api.unsplash.com/search/photos?query=${encodeURIComponent(keyword + " India")}&per_page=3&orientation=landscape&content_filter=high`;
    const res = await fetch(u, { headers: { Authorization: `Client-ID ${UNSPLASH_ACCESS_KEY}` } });
    if (!res.ok) return null;
    const d = await res.json();
    for (const p of (d?.results ?? [])) {
      const w = p?.width ?? 0;
      if (w < 1200) continue;
      const url = p?.urls?.regular || p?.urls?.full;
      if (url) return { url, credit: "Unsplash", source: "Unsplash" };
    }
    const p = d?.results?.[0];
    const url = p?.urls?.regular || p?.urls?.full;
    return url ? { url, credit: "Unsplash", source: "Unsplash" } : null;
  } catch { return null; }
}

async function tryPexels(keyword: string): Promise<{ url: string; credit: string; source: string } | null> {
  const key = Deno.env.get("PEXELS_API_KEY") ?? "";
  if (!key) return null;
  try {
    const u = `https://api.pexels.com/v1/search?query=${encodeURIComponent(keyword + " India")}&per_page=3&orientation=landscape`;
    const res = await fetch(u, { headers: { Authorization: key } });
    if (!res.ok) return null;
    const d = await res.json();
    const p = d?.photos?.[0];
    const url = p?.src?.large2x || p?.src?.large || p?.src?.original;
    return url ? { url, credit: "Pexels", source: "Pexels" } : null;
  } catch { return null; }
}

async function visionScore(imageUrl: string, classification: Classification): Promise<{ score: number; description: string; shows_subject: boolean }> {
  try {
    const data = await anthropicFetch({
      model: VISION_MODEL,
      max_tokens: 150,
      messages: [{
        role: "user",
        content: [
          { type: "image", source: { type: "url", url: imageUrl } },
          { type: "text", text: `Article subject: ${classification.type} = "${classification.subject}".

Does this image show ${classification.subject}? Score 1-10 where 10 = clearly shows the exact ${classification.type === "PERSON" ? "person" : classification.type === "PLACE" ? "place" : "subject"}, 1 = unrelated.

Reply JSON only: {"score": N, "shows_subject": true|false, "description": "5 words or fewer — subject and location only, no verbs, no analysis"}` },
        ],
      }],
    });
    const text = (data?.content?.[0]?.text ?? "").trim().replace(/^```(?:json)?\s*|\s*```$/g, "");
    const m = text.match(/\{[\s\S]*\}/);
    const j = JSON.parse(m ? m[0] : text);
    return {
      score: Number(j.score) || 0,
      description: String(j.description || "").trim(),
      shows_subject: !!j.shows_subject,
    };
  } catch { return { score: 0, description: "", shows_subject: false }; }
}

async function isImageUrlInUse(url: string): Promise<boolean> {
  if (!_sb) return false;
  const { count, error } = await _sb
    .from("articles")
    .select("id", { count: "exact", head: true })
    .eq("image_url", url)
    .eq("is_published", true);
  if (error) {
    console.error("[image] dedupe check failed", error);
    return false;
  }
  return (count ?? 0) > 0;
}

type ImageResultExt = ImageResult & { subject_type: SubjectType; subject_name: string };

function sourcesFor(c: Classification, category: string): Array<() => Promise<{ url: string; credit: string; source: string } | null>> {
  const allowPortrait = c.type === "PERSON";
  switch (c.type) {
    case "PERSON":
      return [
        () => tryWikipedia(c.subject, true),
        () => tryCommons(c.subject, true),
      ];
    case "PLACE":
      return [
        () => tryWikipedia(c.subject, false),
        () => tryCommons(`${c.subject} India`, false),
        () => tryUnsplash(c.subject),
      ];
    case "EVENT":
      return [
        () => tryCommons(c.subject, false),
        () => tryUnsplash(c.keyword || c.subject),
        () => tryPexels(c.keyword || c.subject),
      ];
    case "TOPIC":
    default:
      return [
        () => tryUnsplash(`${c.keyword || c.subject}`),
        () => tryPexels(`${c.keyword || c.subject}`),
        () => tryUnsplash(`India ${category || "news"}`),
      ];
  }
}

async function fetchImageForArticle(title: string, firstPara: string, category: string): Promise<ImageResultExt | null> {
  const classification = await classifySubject(title, firstPara, category);
  console.log(`[image] classified type=${classification.type} subject="${classification.subject}" keyword="${classification.keyword}"`);

  const sources = sourcesFor(classification, category);
  let best: { url: string; credit: string; source: string; description: string; score: number } | null = null;

  for (const src of sources) {
    const cand = await src();
    if (!cand) continue;
    if (await isImageUrlInUse(cand.url)) {
      console.log(`[image] skip ${cand.source} — url already used`);
      continue;
    }
    const v = await visionScore(cand.url, classification);
    console.log(`[image] ${cand.source} score=${v.score} shows=${v.shows_subject} — ${v.description}`);
    if (v.score >= 7) {
      return {
        image_url: cand.url,
        image_caption: `${v.description || classification.subject} · Photo: ${cand.source}`,
        image_credit: `Photo: ${cand.credit}`,
        image_verified: true,
        image_score: v.score,
        subject_type: classification.type,
        subject_name: classification.subject,
      };
    }
    if (!best || v.score > best.score) {
      best = { ...cand, description: v.description, score: v.score };
    }
  }

  if (best) {
    return {
      image_url: best.url,
      image_caption: `${best.description || classification.subject} · Photo: ${best.source}`,
      image_credit: `Photo: ${best.credit}`,
      image_verified: false,
      image_score: best.score,
      subject_type: classification.type,
      subject_name: classification.subject,
    };
  }
  // Generic India + category fallback.
  console.warn(`[image] all sources exhausted for "${title}" — trying generic India fallback`);
  const fb = (await tryUnsplash(`India ${category || "news"}`)) ?? (await tryPexels(`India ${category || "news"}`));
  if (fb && !(await isImageUrlInUse(fb.url))) {
    return {
      image_url: fb.url,
      image_caption: `${classification.subject} · Photo: ${fb.source}`,
      image_credit: `Photo: ${fb.credit}`,
      image_verified: false,
      image_score: 0,
      subject_type: classification.type,
      subject_name: classification.subject,
    };
  }
  console.error(`[image] no unique image available for "${title}"`);
  return null;
}

const SYSTEM_PROMPT =
  "You are a senior features editor at The Videshi, a news platform for Indian-Americans. Your job is to take a factual draft and transform it into a rich, beautiful, deeply contextual article that resonates specifically with the Indian-American diaspora.\n\n" +
  "CRITICAL: Never include HTML tags, citation tags, reference tags, or any markup like <cite>, <ref>, <a>, <span>, <div>, or similar in your output. Plain markdown only. No HTML whatsoever.";

// ---------------- NRI signal detection ----------------
const VISA_SIGNALS = ["H-1B", "H1B", "OCI", "green card", "visa", "immigration", "USCIS", "work permit"];
const REMITTANCE_SIGNALS = ["remittance", "wire transfer", "NRE account", "NRO", "FEMA", "foreign exchange"];
const PROPERTY_SIGNALS = ["NRI investment", "real estate", "property", "realty"];
const PERSON_SIGNALS = [
  "Sundar Pichai", "Satya Nadella", "Vivek Ramaswamy", "Kamala Harris",
  "Usha Vance", "Ajay Banga", "Rishi Sunak", "Jagmeet Singh",
  "Indra Nooyi", "Pramila Jayapal", "Ro Khanna", "Ami Bera",
];
const COMMUNITY_SIGNALS = ["Indian-American", "diaspora", "NRI", "Indian origin", "South Asian"];

type NriSignals = {
  visa: string[];
  remittance: string[];
  property: string[];
  persons: string[];
  community: string[];
  all: string[];
};

function detectNriSignals(haystack: string): NriSignals {
  const lower = haystack.toLowerCase();
  const match = (sigs: string[]) => sigs.filter((s) => lower.includes(s.toLowerCase()));
  const visa = match(VISA_SIGNALS);
  const remittance = match(REMITTANCE_SIGNALS);
  const property = match(PROPERTY_SIGNALS);
  const persons = match(PERSON_SIGNALS);
  const community = match(COMMUNITY_SIGNALS);
  const all = Array.from(new Set([...visa, ...remittance, ...property, ...persons, ...community]));
  return { visa, remittance, property, persons, community, all };
}

function nriAngleFocus(sig: NriSignals): string {
  const parts: string[] = [];
  if (sig.visa.length)
    parts.push(`VISA focus — center the NRI angle on direct policy impact for H-1B / OCI / green card / visa holders. Detected: ${sig.visa.join(", ")}.`);
  if (sig.remittance.length)
    parts.push(`REMITTANCE focus — center the NRI angle on impact to the ~$125B annual India-US remittance corridor and NRE/NRO account holders. Detected: ${sig.remittance.join(", ")}.`);
  if (sig.property.length)
    parts.push(`PROPERTY focus — center the NRI angle on NRI real-estate / realty investment implications. Detected: ${sig.property.join(", ")}.`);
  if (sig.persons.length)
    parts.push(`PERSON focus — center the NRI angle on the diaspora significance of: ${sig.persons.join(", ")}.`);
  if (sig.community.length)
    parts.push(`COMMUNITY focus — center the NRI angle on Indian-American community organization response. Detected: ${sig.community.join(", ")}.`);
  if (parts.length === 0)
    parts.push(`GENERIC focus — no specific NRI signals matched. Use a generic "why Indians abroad should care" angle, kept short.`);
  return parts.join("\n  * ");
}

function stripFences(text: string): string {
  const fence = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  const raw = fence ? fence[1] : text;
  const start = raw.indexOf("{");
  const end = raw.lastIndexOf("}");
  if (start === -1 || end === -1) return raw.trim();
  return raw.slice(start, end + 1);
}

async function repairJsonWithHaiku(malformed: string): Promise<string> {
  const data = await anthropicFetch({
    model: "claude-haiku-4-5-20251001",
    max_tokens: 8192,
    messages: [{
      role: "user",
      content: `The following is malformed JSON. Fix it and return only valid JSON, nothing else: ${malformed}`,
    }],
  });
  return (data.content || [])
    .filter((b: any) => b.type === "text")
    .map((b: any) => b.text)
    .join("\n");
}

async function extractJsonWithRepair(text: string): Promise<any> {
  const candidate = stripFences(text);
  try {
    return JSON.parse(candidate);
  } catch (_e) {
    console.warn("Initial JSON parse failed, attempting repair via Haiku");
    const repaired = await repairJsonWithHaiku(candidate);
    const repairedCandidate = stripFences(repaired);
    return JSON.parse(repairedCandidate);
  }
}

async function callClaudeWithSearch(userPrompt: string, useWebSearch: boolean): Promise<string> {
  const body: any = {
    model: MODEL,
    max_tokens: 6144,
    system: SYSTEM_PROMPT,
    messages: [{ role: "user", content: userPrompt }],
  };
  if (useWebSearch) {
    body.tools = [{ type: "web_search_20250305", name: "web_search", max_uses: 6 }];
  }
  const data = await anthropicFetch(body);
  return (data.content || [])
    .filter((b: any) => b.type === "text")
    .map((b: any) => b.text)
    .join("\n");
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  _sb = supabase;
  const workerId = `enricher-${crypto.randomUUID()}`;

  const respond = (status: number, body: unknown) =>
    new Response(JSON.stringify(body), {
      status,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });

  // Daily article cap (configurable via DAILY_ARTICLE_CAP secret, default 10)
  const dailyCap = parseInt(Deno.env.get("DAILY_ARTICLE_CAP") ?? "10", 10);
  const startOfDay = new Date();
  startOfDay.setUTCHours(0, 0, 0, 0);
  const { count: todayCount } = await supabase
    .from("articles")
    .select("id", { count: "exact", head: true })
    .eq("is_published", true)
    .gte("published_at", startOfDay.toISOString());
  if ((todayCount ?? 0) >= dailyCap) {
    return respond(200, { ok: true, message: `Daily cap reached (${todayCount}/${dailyCap} articles today)` });
  }

  const { data: claimed, error: claimErr } = await supabase.rpc("claim_queue_job", {
    p_status: "enriching",
    p_worker_id: workerId,
    p_lock_secs: 300,
  });
  if (claimErr) {
    console.error("claim error", claimErr);
    return respond(500, { ok: false, error: claimErr.message });
  }
  if (!claimed || !claimed.id) {
    return respond(200, { ok: true, message: "No enriching jobs" });
  }

  const job = claimed;
  _jobId = job.id;
  const { data: runRow } = await supabase
    .from("pipeline_runs")
    .insert({ run_type: "enricher", status: "running" })
    .select()
    .single();
  const runId = runRow?.id;

  try {
    const draft = job.article_draft || {};
    const brief = job.story_brief || {};

    const articleType = brief.article_type === "feature" ? "feature" : "news";
    const totalLen =
      articleType === "feature"
        ? "1,000–1,500 words MAXIMUM including all sections combined (in-depth analysis/feature)"
        : "300–400 words MAXIMUM including all sections combined (concise news brief)";

    // Detect NRI signals from brief + draft text so we can tailor the angle.
    const signalHaystack = [
      brief.headline, brief.why_it_matters,
      ...(Array.isArray(brief.key_facts) ? brief.key_facts : []),
      draft.title, draft.summary,
      typeof draft.body === "string" ? draft.body : JSON.stringify(draft.body ?? ""),
    ].filter(Boolean).join(" \n ");
    const nriSignals = detectNriSignals(signalHaystack);
    const nriFocusBlock = nriAngleFocus(nriSignals);
    console.log(`[enricher] nri signals job=${job.id}`, nriSignals.all);
    const userPrompt = `Take this factual draft and turn it into a rich, deeply contextual article for the Indian-American diaspora.

STORY BRIEF:
${JSON.stringify(brief, null, 2)}

FACTUAL DRAFT:
${JSON.stringify(draft, null, 2)}

ARTICLE TYPE: ${articleType.toUpperCase()}

DO ALL OF THE FOLLOWING (with strict constraints):
- NRI/Diaspora Angle — STRICT RULES:
  * SIGNAL-BASED FOCUS — tailor the angle using these detected signals (highest priority instructions):
  * ${nriFocusBlock}
  * Format the nri_angle block content as a markdown bulleted list using "- " (dash + space) bullets — NEVER use the • character.
  * Exactly 2-3 bullets, each on its own line, in this order:
    - **Why It Matters:** one sentence on why Indian-Americans should care
    - **What To Watch:** one sentence on what comes next
    - **Action If Any:** (optional) one sentence on resources or steps
  * Each bullet bold label must be wrapped in markdown bold (**Label:**), followed by a space and the sentence.
  * Do NOT include organizational history. Do NOT include demographic statistics unless directly sourced in sources_used.
  * Example content value:\n    "- **Why It Matters:** For the ~2.5 million Bengali-Americans, this shift ends a culturally protective regional government.\n- **What To Watch:** How the new BJP administration handles Bengali-language policy and diaspora investment channels.\n- **Action If Any:** Diaspora groups can lobby through FIA-NY for cultural funding continuity."
- Wikipedia / Background Context: keep historical context sections — they are valuable. Paraphrasing Wikipedia is encouraged but MUST be clearly attributed (e.g. "According to Wikipedia").
- Geographic Context boxes: keep them — they are valuable for diaspora readers.
- "Understanding the Players" explainer boxes: keep them.
- Pull Quotes: only use quotes that appear VERBATIM in sources_used AND are attributed to a NAMED individual with a specific source. NEVER use vague attributions like "— Political analysts" or "— Observers". If you cannot verify the exact wording or named source, paraphrase inside a normal paragraph and do NOT format as a pull_quote.
- Total article length: ${totalLen}.
- Seat counts and numbers: when sources conflict, always use the most CONSERVATIVE figure and append "(preliminary)".
- Key Facts Box: 4–6 bullets at the top.
- Subheadings every 2–3 paragraphs.

IMPORTANT: Your entire response must be a single valid JSON object. Do not use unescaped double quotes inside string values. Use single quotes for dialogue and apostrophes only. Do not include any text outside the JSON object.

Return ONLY valid JSON (no prose, no fences) in this exact shape:
{
  "title": "string",
  "slug": "string",
  "summary": "2-3 sentence card summary",
  "key_facts": ["string"],
  "body": [
    {"type": "paragraph", "content": "string"},
    {"type": "pull_quote", "quote": "string", "attribution": "string"},
    {"type": "subheading", "content": "string"},
    {"type": "context_box", "heading": "string", "content": "string"},
    {"type": "nri_angle", "heading": "What This Means For Indian-Americans", "content": "string"},
    {"type": "key_facts", "facts": ["string"]},
    {"type": "map_reference", "region": "string", "note": "string"}
  ],
  "wikipedia_context": {"topic": "string", "summary": "string", "url": "string"},
  "nri_relevance": "high|medium|low",
  "nri_communities": ["string"],
  "tags": ["string"],
  "word_count": 0,
  "read_time_min": 0
}`;

    const useWebSearch = brief?.diaspora_relevance === "high";
    const text = await callClaudeWithSearch(userPrompt, useWebSearch);
    const enriched = await extractJsonWithRepair(text);

    if (!enriched.title || !Array.isArray(enriched.body)) {
      throw new Error("Enriched article missing required fields");
    }

    // Fetch hero image inline so no article is published without one.
    try {
      const firstPara = (() => {
        if (Array.isArray(enriched.body)) {
          const p = enriched.body.find((b: any) => b?.type === "paragraph" && typeof b.content === "string");
          if (p) return p.content as string;
        }
        return enriched.summary || "";
      })();
      const img = await fetchImageForArticle(enriched.title, firstPara, job.category || "world");
      if (img) {
        enriched.image_url = img.image_url;
        enriched.image_caption = img.image_caption;
        enriched.image_credit = img.image_credit;
        enriched.image_verified = img.image_verified;
        enriched.image_score = img.image_score;
        enriched.subject_type = img.subject_type;
        enriched.subject_name = img.subject_name;
      } else {
        console.warn(`[image] no image found for "${enriched.title}"`);
      }
    } catch (e) {
      console.error("[image] fetch failed", e);
    }

    // Merge detected NRI signals into tags for future filtering.
    const existingTags = Array.isArray(enriched.tags) ? enriched.tags.map((t: any) => String(t)) : [];
    const signalTags = nriSignals.all.map((s) => `nri:${s.toLowerCase().replace(/\s+/g, "-")}`);
    enriched.tags = Array.from(new Set([...existingTags, ...signalTags]));
    enriched.nri_signals = nriSignals.all;

    await supabase
      .from("story_queue")
      .update({
        status: "editing",
        enriched_article: enriched,
        locked_by: null,
        locked_until: null,
        error_message: null,
        updated_at: new Date().toISOString(),
      })
      .eq("id", job.id);

    if (runId) {
      await supabase
        .from("pipeline_runs")
        .update({
          status: "ok",
          finished_at: new Date().toISOString(),
          articles_created: 1,
        })
        .eq("id", runId);
    }

    return respond(200, { ok: true, job_id: job.id, status: "editing" });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    const stack = e instanceof Error && e.stack ? e.stack : "";
    const fullErr = stack ? `${msg}\n${stack}` : msg;
    console.error(`[agent-enricher] job=${job.id} attempt=${job.attempts}/${job.max_attempts} FAILED:`, msg);
    if (stack) console.error(`[agent-enricher] stack:`, stack);

    const attempts = job.attempts || 0;
    const maxAttempts = job.max_attempts || 5;
    const exhausted = attempts >= maxAttempts;
    const nextStatus = exhausted ? "failed" : "enriching";
    const prevErr = job.error_message || "";
    const appended = `${prevErr}${prevErr ? " | " : ""}attempt ${attempts}: ${fullErr}`.slice(0, 4000);

    await supabase
      .from("story_queue")
      .update({
        status: nextStatus,
        error_message: appended,
        locked_by: null,
        locked_until: null,
        updated_at: new Date().toISOString(),
      })
      .eq("id", job.id);

    if (runId) {
      await supabase
        .from("pipeline_runs")
        .update({
          status: "error",
          finished_at: new Date().toISOString(),
          error_message: fullErr.slice(0, 4000),
        })
        .eq("id", runId);
    } else {
      await supabase.from("pipeline_runs").insert({
        run_type: "agent-enricher",
        status: "error",
        started_at: new Date().toISOString(),
        finished_at: new Date().toISOString(),
        error_message: `job=${job.id} attempt=${attempts}: ${fullErr}`.slice(0, 4000),
      });
    }

    await logAlert(supabase, {
      severity: exhausted ? "critical" : "warning",
      agent: AGENT,
      errorType: (e as any)?.errorType ?? "exception",
      message: msg,
      jobId: job.id,
    });

    if (exhausted) {
      const history = appended.split(" | ");
      await moveToDLQ(supabase, {
        jobId: job.id,
        agent: AGENT,
        storyBrief: job.story_brief,
        errorHistory: history,
        failureReason: msg,
      });
      await sendAlertEmail({
        severity: "critical",
        agent: AGENT,
        errorType: (e as any)?.errorType ?? "max_attempts",
        jobId: job.id,
        message: `Job exhausted ${maxAttempts} attempts. Last error: ${msg}`,
      });
    }

    return respond(500, { ok: false, job_id: job.id, status: nextStatus, error: msg });
  }
});
