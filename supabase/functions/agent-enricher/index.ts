// agent-enricher: claims an 'enriching' job and produces a rich, diaspora-focused article structure.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY")!;
const MODEL = "claude-haiku-4-5-20251001";

const SYSTEM_PROMPT =
  "You are a senior features editor at The Videshi, a news platform for Indian-Americans. Your job is to take a factual draft and transform it into a rich, beautiful, deeply contextual article that resonates specifically with the Indian-American diaspora.";

function stripFences(text: string): string {
  const fence = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  const raw = fence ? fence[1] : text;
  const start = raw.indexOf("{");
  const end = raw.lastIndexOf("}");
  if (start === -1 || end === -1) return raw.trim();
  return raw.slice(start, end + 1);
}

async function repairJsonWithHaiku(malformed: string): Promise<string> {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 8192,
      messages: [{
        role: "user",
        content: `The following is malformed JSON. Fix it and return only valid JSON, nothing else: ${malformed}`,
      }],
    }),
  });
  if (!res.ok) throw new Error(`Repair failed ${res.status}: ${await res.text()}`);
  const data = await res.json();
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
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`Claude error ${res.status}: ${await res.text()}`);
  }
  const data = await res.json();
  return (data.content || [])
    .filter((b: any) => b.type === "text")
    .map((b: any) => b.text)
    .join("\n");
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
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
    const userPrompt = `Take this factual draft and turn it into a rich, deeply contextual article for the Indian-American diaspora.

STORY BRIEF:
${JSON.stringify(brief, null, 2)}

FACTUAL DRAFT:
${JSON.stringify(draft, null, 2)}

ARTICLE TYPE: ${articleType.toUpperCase()}

DO ALL OF THE FOLLOWING (with strict constraints):
- NRI/Diaspora Angle — STRICT RULES:
  * Maximum 3 sentences total. No bullets, no numbered lists, no subheadings inside this section.
  * Sentence 1: WHY this matters to Indian-Americans. Sentence 2: WHAT to watch next. Sentence 3 (optional): action or resources.
  * Do NOT include organizational history. Do NOT include demographic statistics unless directly sourced in sources_used.
  * Example of correct length and tone: "For the ~2.5 million Bengali-Americans, this shift marks the end of a regional government many saw as culturally protective. Watch how the new BJP administration handles Bengali-language policy and diaspora investment channels in the coming months."
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
    console.error("agent-enricher error", msg);

    const attempts = job.attempts || 0;
    const maxAttempts = job.max_attempts || 3;
    const nextStatus = attempts >= maxAttempts ? "failed" : "enriching";
    const prevErr = job.error_message || "";
    const appended = `${prevErr}${prevErr ? " | " : ""}attempt ${attempts}: ${msg}`.slice(0, 2000);

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
          error_message: msg,
        })
        .eq("id", runId);
    }

    return respond(500, { ok: false, job_id: job.id, status: nextStatus, error: msg });
  }
});
