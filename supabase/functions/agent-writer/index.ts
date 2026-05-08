// agent-writer: claims a pending story_queue job and writes a first draft using Claude Sonnet + web search.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY")!;
const MODEL = "claude-sonnet-4-6";

const SYSTEM_PROMPT =
  "You are an experienced journalist writing for The Videshi, a news platform for Indian-Americans. Write factually, neutrally, and with depth. Always search for official sources first — PIB, Newsonair, ANI, ECI, NIA, RBI. Then wire services — PTI, IANS. Then reputable news outlets.\n\n" +
  "CRITICAL: Never include HTML tags, citation tags, reference tags, or any markup like <cite>, <ref>, <a>, <span>, <div>, or similar in your output. Plain markdown only. No HTML whatsoever.";

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
    return JSON.parse(stripFences(repaired));
  }
}

async function callClaude(userPrompt: string): Promise<string> {
  const body: any = {
    model: MODEL,
    max_tokens: 4096,
    system: SYSTEM_PROMPT,
    messages: [{ role: "user", content: userPrompt }],
  };
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
  // concatenate all text blocks (web_search produces interleaved tool_use/result blocks)
  const parts = (data.content || [])
    .filter((b: any) => b.type === "text")
    .map((b: any) => b.text);
  return parts.join("\n");
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

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

  const MAX_JOBS_PER_INVOCATION = 3;
  const results: any[] = [];

  for (let i = 0; i < MAX_JOBS_PER_INVOCATION; i++) {
    const workerId = `writer-${crypto.randomUUID()}`;

    // Claim a job atomically
    const { data: claimed, error: claimErr } = await supabase.rpc(
      "claim_queue_job",
      { p_status: "pending", p_worker_id: workerId, p_lock_secs: 300 },
    );
    console.log(
      `[writer iter ${i}] worker=${workerId} claim result:`,
      JSON.stringify(claimed),
      "error:",
      JSON.stringify(claimErr),
    );
    if (claimErr) {
      console.error("claim error", claimErr);
      results.push({ ok: false, error: claimErr.message });
      break;
    }
    if (!claimed || !claimed.id) {
      console.log(`[writer iter ${i}] No jobs claimed — exiting loop`);
      if (results.length === 0) {
        return respond(200, { ok: true, message: "No pending jobs" });
      }
      break;
    }
    console.log(`[writer iter ${i}] Claimed job id=${claimed.id} attempts=${claimed.attempts}`);

    const job = claimed;
    const { data: runRow } = await supabase
      .from("pipeline_runs")
      .insert({ run_type: "writer", status: "running" })
      .select()
      .single();
    const runId = runRow?.id;

    // Mark as writing
    await supabase
      .from("story_queue")
      .update({ status: "writing", updated_at: new Date().toISOString() })
      .eq("id", job.id);

    try {
    const brief = job.story_brief || {};
    const articleType = brief.article_type === "feature" ? "feature" : "news";
    const targetLen =
      articleType === "feature"
        ? "1,000–1,500 word in-depth feature/analysis draft"
        : "300–400 word factual news brief";
    const userPrompt = `You have a story brief. Write a factual first draft.

STORY BRIEF:
${JSON.stringify(brief, null, 2)}

ARTICLE TYPE: ${articleType.toUpperCase()}

INSTRUCTIONS:
- Work ONLY from the story brief above. Do NOT call any external tools or perform web searches.
- Use the sources already provided in the brief; cite them by name/url in sources_used.
- Write a ${targetLen} in markdown with: lead paragraph, key facts, official reactions, background context${articleType === "feature" ? ", deeper analysis, multiple perspectives, and historical context" : ""}.
- Do NOT add NRI/diaspora angle (that's a separate step).
- Do NOT editorialize or add opinion.


IMPORTANT: Your entire response must be a single valid JSON object. Do not use unescaped double quotes inside string values. Use single quotes for dialogue and apostrophes only. Do not include any text outside the JSON object.

Return ONLY valid JSON (no prose, no markdown fences) in this exact shape:
{
  "title": "string",
  "slug": "url-slug-with-date",
  "body_markdown": "string",
  "sources_used": [{"name": "string", "url": "string", "type": "official|wire|news"}],
  "word_count": 0,
  "missing_info": ["string"],
  "confidence": "high|medium|low"
}`;

    const text = await callClaude(userPrompt);
    const draft = await extractJsonWithRepair(text);

    if (!draft.title || !draft.body_markdown) {
      throw new Error("Draft missing required fields");
    }

    await supabase
      .from("story_queue")
      .update({
        status: "enriching",
        article_draft: draft,
        draft_version: (job.draft_version || 0) + 1,
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

      results.push({ ok: true, job_id: job.id, status: "enriching" });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      console.error("agent-writer error", msg);

      const attempts = job.attempts || 0;
      const maxAttempts = job.max_attempts || 3;
      const nextStatus = attempts >= maxAttempts ? "failed" : "pending";
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

      results.push({ ok: false, job_id: job.id, status: nextStatus, error: msg });
    }
  }

  return respond(200, { ok: true, processed: results.length, results });
});
