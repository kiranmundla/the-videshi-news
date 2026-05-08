// agent-editor: claims an 'editing' job, runs an editorial QA pass, and publishes/revises/rejects.
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
  "You are a senior editor and legal checker at The Videshi. You are the last gate before publication. Be thorough but fair — only reject or revise if there is a real problem.";

function extractJson(text: string): any {
  const fence = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  const raw = fence ? fence[1] : text;
  const start = raw.indexOf("{");
  const end = raw.lastIndexOf("}");
  if (start === -1 || end === -1) throw new Error("No JSON object found");
  return JSON.parse(raw.slice(start, end + 1));
}

async function callClaude(userPrompt: string): Promise<string> {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: 2048,
      system: SYSTEM_PROMPT,
      messages: [{ role: "user", content: userPrompt }],
    }),
  });
  if (!res.ok) throw new Error(`Claude error ${res.status}: ${await res.text()}`);
  const data = await res.json();
  return (data.content || [])
    .filter((b: any) => b.type === "text")
    .map((b: any) => b.text)
    .join("\n");
}

function bodyToMarkdown(body: any[]): string {
  if (!Array.isArray(body)) return "";
  const out: string[] = [];
  for (const block of body) {
    if (!block || typeof block !== "object") continue;
    switch (block.type) {
      case "paragraph":
        if (block.content) out.push(block.content);
        break;
      case "subheading":
        if (block.content) out.push(`## ${block.content}`);
        break;
      case "pull_quote": {
        const q = block.quote ? `> ${block.quote}` : "";
        const a = block.attribution ? `\n> \n> — ${block.attribution}` : "";
        if (q) out.push(q + a);
        break;
      }
      case "context_box":
        out.push(
          `> **${block.heading || "Context"}**\n>\n> ${block.content || ""}`,
        );
        break;
      case "nri_angle":
        out.push(
          `## ${block.heading || "What This Means For Indian-Americans"}\n\n${block.content || ""}`,
        );
        break;
      case "key_facts": {
        const facts: string[] = Array.isArray(block.facts) ? block.facts : [];
        out.push(
          `**Key facts**\n\n${facts.map((f) => `- ${f}`).join("\n")}`,
        );
        break;
      }
      case "map_reference":
        out.push(
          `_📍 ${block.region || ""}${block.note ? " — " + block.note : ""}_`,
        );
        break;
      default:
        if (typeof block.content === "string") out.push(block.content);
    }
  }
  return out.join("\n\n");
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  const workerId = `editor-${crypto.randomUUID()}`;

  const respond = (status: number, body: unknown) =>
    new Response(JSON.stringify(body), {
      status,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });

  const { data: claimed, error: claimErr } = await supabase.rpc("claim_queue_job", {
    p_status: "editing",
    p_worker_id: workerId,
    p_lock_secs: 300,
  });
  if (claimErr) {
    console.error("claim error", claimErr);
    return respond(500, { ok: false, error: claimErr.message });
  }
  if (!claimed || !claimed.id) {
    return respond(200, { ok: true, message: "No editing jobs" });
  }

  const job = claimed;
  const { data: runRow } = await supabase
    .from("pipeline_runs")
    .insert({ run_type: "editor", status: "running" })
    .select()
    .single();
  const runId = runRow?.id;

  try {
    const enriched = job.enriched_article || {};
    const draft = job.article_draft || {};

    // 1. Duplicate article check via pg_trgm similarity
    let duplicateMatch: { title: string; slug: string; similarity: number } | null = null;
    if (enriched.title) {
      const { data: dupes, error: dupErr } = await supabase.rpc(
        "find_similar_articles",
        { p_title: enriched.title, p_hours: 48, p_threshold: 0.6 },
      );
      if (dupErr) console.error("dup check error", dupErr);
      if (dupes && dupes.length > 0) duplicateMatch = dupes[0];
    }

    if (duplicateMatch) {
      const reason = `duplicate: similar article already published at ${duplicateMatch.slug} (similarity ${duplicateMatch.similarity.toFixed(2)})`;
      await supabase
        .from("story_queue")
        .update({
          status: "rejected",
          editor_decision: "reject",
          editor_notes: reason,
          locked_by: null,
          locked_until: null,
          error_message: null,
          updated_at: new Date().toISOString(),
        })
        .eq("id", job.id);

      if (runId) {
        await supabase
          .from("pipeline_runs")
          .update({ status: "ok", finished_at: new Date().toISOString() })
          .eq("id", runId);
      }
      return respond(200, { ok: true, job_id: job.id, decision: "reject", reason });
    }

    const userPrompt = `You are reviewing an article before publication. Run this checklist:

1. Copyright: any verbatim quotes longer than 15 words copied from a source? Flag them.
2. Fact consistency: do numbers, names, and dates match throughout?
3. Bias: is the article politically neutral and showing multiple perspectives?
4. NRI angle: if nri_relevance is high/medium, is there a meaningful NRI section?
5. Headline quality: title specific, factual, compelling but not clickbait?
6. Structure: subheadings, pull quotes, key facts box?
7. Word count: between 400 and 800 words?
8. Overall quality: would an Indian-American reader find this genuinely valuable?
9. Content similarity: compare the article body against the sources_used URLs in the original draft. Flag any passage that appears verbatim or near-verbatim (>10 words in sequence) from a source. If found, decision MUST be "revise" with revision_notes telling the writer to paraphrase the flagged sections (quote the offending passage and name the source).

ENRICHED ARTICLE:
${JSON.stringify(enriched, null, 2)}

ORIGINAL FACTUAL DRAFT (for cross-checking sources/quotes):
${JSON.stringify(draft, null, 2)}

DECISION RULES (apply strictly):
- If quality_score >= 6/10, decision MUST be "publish" — no exceptions.
- Minor formatting issues (word count slightly off, NRI section length, citation formatting, missing subheading, etc.) → "publish" with notes in issues. NEVER "revise" for formatting.
- Only use "revise" for: clear copyright violation, fabricated/unverifiable quotes, or major factual error.
- Only use "reject" for: quality_score below 4, or complete plagiarism.

Return ONLY valid JSON (no prose, no fences) in this exact shape:
{
  "decision": "publish|revise|reject",
  "quality_score": 0,
  "issues": ["string"],
  "revision_notes": "string",
  "rejection_reason": "string"
}`;

    const text = await callClaude(userPrompt);
    const review = extractJson(text);
    const decision = review.decision;

    const revisionCount = job.revision_count || 0;
    const maxRevisions = job.max_revisions || 2;

    const exhaustedRevisions = revisionCount >= maxRevisions;
    const forcePublish = exhaustedRevisions && enriched && enriched.title;

    if (decision === "publish" || forcePublish || (decision === "revise" && exhaustedRevisions)) {
      // Publish
      const slug =
        enriched.slug ||
        (enriched.title || "story")
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/^-+|-+$/g, "")
          .slice(0, 80);

      const bodyMd = sanitizeMarkdown(bodyToMarkdown(enriched.body || []));
      const cleanSummary = sanitizeMarkdown(enriched.summary || "");
      const cleanTitle = sanitizeMarkdown(enriched.title || "").trim();
      const wordCount =
        enriched.word_count ||
        bodyMd.split(/\s+/).filter(Boolean).length;
      const readTime =
        enriched.read_time_min || Math.max(1, Math.round(wordCount / 220));

      const editorNote =
        decision !== "publish"
          ? `Auto-published after ${revisionCount} revision attempts (decision was ${decision}). Notes: ${review.revision_notes || review.rejection_reason || ""}`
          : null;

      const { data: inserted, error: insErr } = await supabase
        .from("articles")
        .insert({
          title: cleanTitle || enriched.title,
          slug,
          summary: cleanSummary,
          body: bodyMd,
          category: job.category || "world",
          tags: enriched.tags || [],
          word_count: wordCount,
          read_time_min: readTime,
          is_published: true,
          published_at: new Date().toISOString(),
          sources_used: draft.sources_used || null,
          nri_angle: enriched.nri_relevance || null,
          article_type:
            (job.story_brief as any)?.article_type === "feature"
              ? "feature"
              : "news",
        })
        .select()
        .single();

      if (insErr) throw insErr;

      await supabase
        .from("story_queue")
        .update({
          status: "published",
          editor_decision: "publish",
          editor_notes: editorNote,
          published_article_id: inserted.id,
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

      return respond(200, {
        ok: true,
        job_id: job.id,
        decision: "publish",
        article_id: inserted.id,
      });
    }

    if (decision === "revise") {
      await supabase
        .from("story_queue")
        .update({
          status: "writing",
          editor_decision: "revise",
          editor_notes: review.revision_notes || "",
          revision_count: revisionCount + 1,
          locked_by: null,
          locked_until: null,
          error_message: null,
          updated_at: new Date().toISOString(),
        })
        .eq("id", job.id);

      if (runId) {
        await supabase
          .from("pipeline_runs")
          .update({ status: "ok", finished_at: new Date().toISOString() })
          .eq("id", runId);
      }

      return respond(200, { ok: true, job_id: job.id, decision: "revise" });
    }

    // reject
    await supabase
      .from("story_queue")
      .update({
        status: "rejected",
        editor_decision: "reject",
        editor_notes: review.rejection_reason || "Rejected by editor",
        locked_by: null,
        locked_until: null,
        error_message: null,
        updated_at: new Date().toISOString(),
      })
      .eq("id", job.id);

    if (runId) {
      await supabase
        .from("pipeline_runs")
        .update({ status: "ok", finished_at: new Date().toISOString() })
        .eq("id", runId);
    }

    return respond(200, { ok: true, job_id: job.id, decision: "reject" });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    console.error("agent-editor error", msg);

    const attempts = job.attempts || 0;
    const maxAttempts = job.max_attempts || 3;
    const nextStatus = attempts >= maxAttempts ? "failed" : "editing";

    await supabase
      .from("story_queue")
      .update({
        status: nextStatus,
        error_message: msg.slice(0, 2000),
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
