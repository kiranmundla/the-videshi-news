// agent-scout: groups raw articles, ranks them, writes story briefs into story_queue.
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
  "You are a news scout for an Indian-American diaspora platform called The Videshi. Your job is to group similar stories, rank them by importance, and write a brief for each one.";

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
      max_tokens: 4096,
      system: SYSTEM_PROMPT,
      messages: [{ role: "user", content: userPrompt }],
    }),
    signal: AbortSignal.timeout(50000),
  });
  if (!res.ok) {
    throw new Error(`Claude error ${res.status}: ${await res.text()}`);
  }
  const data = await res.json();
  return data.content?.[0]?.text ?? "";
}

function extractJson(text: string): any {
  const fence = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  const raw = fence ? fence[1] : text;
  const start = raw.indexOf("{");
  const end = raw.lastIndexOf("}");
  if (start === -1 || end === -1) throw new Error("No JSON object found");
  return JSON.parse(raw.slice(start, end + 1));
}

function keywords(headline: string): string[] {
  const stop = new Set([
    "the","a","an","and","or","of","in","on","to","for","at","by","with",
    "is","are","was","were","be","as","from","that","this","it","its","after",
    "over","into","amid","says","said","new","up","down","out",
  ]);
  return headline
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length > 3 && !stop.has(w))
    .slice(0, 6);
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

  const { data: runRow } = await supabase
    .from("pipeline_runs")
    .insert({ run_type: "scout", status: "running" })
    .select()
    .single();
  const runId = runRow?.id;

  const respond = (status: number, body: unknown) =>
    new Response(JSON.stringify(body), {
      status,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });

  try {
    const threeHoursAgo = new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString();

    const { data: raws, error: rawErr } = await supabase
      .from("raw_articles")
      .select("id, title, description, source_name, url, published_at")
      .eq("processed", false)
      .gte("fetched_at", threeHoursAgo)
      .limit(100);

    if (rawErr) throw rawErr;

    if (!raws || raws.length === 0) {
      await supabase
        .from("pipeline_runs")
        .update({
          status: "ok",
          finished_at: new Date().toISOString(),
          raw_fetched: 0,
          groups_created: 0,
        })
        .eq("id", runId);
      return respond(200, { ok: true, message: "No new raw articles" });
    }

    const compact = raws.map((r) => ({
      id: r.id,
      title: r.title,
      source: r.source_name,
      desc: (r.description || "").slice(0, 300),
    }));

    const userPrompt = `Here are ${raws.length} raw news articles fetched in the last 3 hours.

Tasks:
1. Group articles covering the same story semantically.
2. Rank groups by source count (more sources = higher priority).
3. Score diaspora_relevance as: high | medium | low | none.
4. Assign a category from EXACTLY this list (no other values allowed): news | sports | markets-finance | technology | entertainment | lifestyle-health | travel | nri-world. ('news' covers breaking, politics, world, crime, and US-India coverage. 'nri-world' covers Indians abroad / global diaspora — see special instructions below. Events and Classifieds are user-generated and excluded.)

   Special instructions for nri-world: For nri-world category, prioritize stories mentioning these people: Vivek Ramaswamy, Usha Vance, Kamala Harris, Rishi Sunak, Jagmeet Singh, Sundar Pichai, Satya Nadella, Ajay Banga, Ro Khanna, Pramila Jayapal, Ami Bera, Raja Krishnamoorthi, Anita Anand, Ed Husic. Also prioritize: H-1B visa news, OCI card updates, Indian immigration policy in US/UK/Canada/Australia/UAE, Indian diaspora community events, and Indian-origin business leaders making news globally.
5. For the top 3 groups, write a story_brief.

Return ONLY valid JSON in this exact shape (no prose, no markdown):
{
  "stories": [
    {
      "headline": "string",
      "why_it_matters": "string",
      "key_facts": ["string"],
      "suggested_search_queries": ["string"],
      "diaspora_relevance": "high|medium|low|none",
      "category": "news|sports|markets-finance|technology|entertainment|lifestyle-health|travel|nri-world",
      "raw_article_ids": ["uuid"],
      "best_article_id": "uuid",
      "source_count": 0,
      "sources": ["string"]
    }
  ]
}

Articles:
${JSON.stringify(compact)}`;

    const text = await callClaude(userPrompt);
    const parsed = extractJson(text);
    const stories: any[] = Array.isArray(parsed.stories) ? parsed.stories : [];

    const fortyEightHoursAgo = new Date(
      Date.now() - 48 * 60 * 60 * 1000,
    ).toISOString();

    const { data: recentQueue } = await supabase
      .from("story_queue")
      .select("story_brief, status, created_at")
      .neq("status", "failed")
      .gte("created_at", fortyEightHoursAgo);

    const recentBriefs = (recentQueue || [])
      .map((row: any) => row.story_brief)
      .filter((b: any) => b && b.headline);

    const recentWithKw = recentBriefs.map((b: any) => ({
      brief: b,
      kw: new Set(keywords(b.headline || "")),
    }));

    // Ask Claude whether the new brief contains materially new facts vs. an existing one.
    async function hasNewFacts(existing: any, candidate: any): Promise<boolean> {
      try {
        const prompt = `Existing article brief:
Headline: ${existing.headline}
Key facts: ${JSON.stringify(existing.key_facts || [])}

New story brief:
Headline: ${candidate.headline}
Key facts: ${JSON.stringify(candidate.key_facts || [])}

Does the new story brief contain materially new facts not covered in the existing article? Answer "yes" or "no" only.`;
        const ans = (await callClaude(prompt)).trim().toLowerCase();
        return ans.startsWith("yes");
      } catch (e) {
        console.error("hasNewFacts error", e);
        // On failure, allow through rather than block real news.
        return true;
      }
    }

    let inserted = 0;
    const usedRawIds = new Set<string>();

    for (let i = 0; i < stories.length; i++) {
      const s = stories[i];
      if (!s?.headline) continue;
      const kw = keywords(s.headline);
      const kwSet = new Set(kw);

      // Find topically-similar existing briefs from last 48h.
      const similar = recentWithKw.filter(({ kw: existing }) => {
        let overlap = 0;
        for (const w of kwSet) if (existing.has(w)) overlap++;
        return overlap >= 3 || (kwSet.size > 0 && overlap / kwSet.size >= 0.6);
      });

      // If similar exist, only block when NONE of them lack the new facts
      // (i.e. every similar one already covers the new facts).
      let isDup = false;
      if (similar.length > 0) {
        isDup = true;
        for (const { brief } of similar) {
          const isNew = await hasNewFacts(brief, s);
          if (isNew) {
            isDup = false;
            break;
          }
        }
      }
      if (isDup) continue;

      const rawIds: string[] = Array.isArray(s.raw_article_ids)
        ? s.raw_article_ids.filter((x: any) => typeof x === "string")
        : [];

      const sourceCount =
        typeof s.source_count === "number"
          ? s.source_count
          : Array.isArray(s.sources)
          ? s.sources.length
          : rawIds.length;
      const articleType =
        s.diaspora_relevance === "high" && sourceCount >= 3
          ? "feature"
          : "news";
      s.article_type = articleType;

      const { error: insErr } = await supabase.from("story_queue").insert({
        status: "pending",
        story_brief: s,
        priority: stories.length - i,
        category: s.category,
        diaspora_relevance: s.diaspora_relevance,
        raw_article_ids: rawIds,
      });
      if (insErr) {
        console.error("insert story_queue error", insErr);
        continue;
      }
      inserted++;
      recentWithKw.push({ brief: s, kw: kwSet });
      rawIds.forEach((id) => usedRawIds.add(id));
    }

    // mark processed: all raw articles fed to the model
    const allRawIds = raws.map((r) => r.id);
    if (allRawIds.length > 0) {
      await supabase
        .from("raw_articles")
        .update({ processed: true })
        .in("id", allRawIds);
    }

    await supabase
      .from("pipeline_runs")
      .update({
        status: "ok",
        finished_at: new Date().toISOString(),
        raw_fetched: raws.length,
        raw_new: raws.length,
        groups_created: inserted,
      })
      .eq("id", runId);

    return respond(200, {
      ok: true,
      raw_fetched: raws.length,
      stories_proposed: stories.length,
      inserted,
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    console.error("agent-scout error", msg);
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
    return respond(500, { ok: false, error: msg });
  }
});
