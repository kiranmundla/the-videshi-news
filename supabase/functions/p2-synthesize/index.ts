// p2-synthesize — writes original diaspora-focused articles for top-ranked topics.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import Anthropic from "https://esm.sh/@anthropic-ai/sdk@0.27.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);

const anthropic = new Anthropic({ apiKey: Deno.env.get("ANTHROPIC_API_KEY")! });

const VERTICAL_TO_CATEGORY: Record<string, string> = {
  politics: 'news',
  economy: 'markets-finance',
  tech: 'technology',
  immigration: 'nri-world',
  diaspora: 'nri-world',
  science: 'technology',
  culture: 'lifestyle-health',
  sports: 'sports',
  entertainment: 'entertainment',
};

function stripCitations(text: string): string {
  return text
    // Remove <cite index="...">text</cite> tags, keep inner text
    .replace(/<cite[^>]*>([\s\S]*?)<\/cite>/g, '$1')
    // Remove bare [0], [1], [2] reference markers
    .replace(/\[\d+\]/g, '')
    // Remove (Source: ...) inline citations
    .replace(/\(Source:[^)]+\)/gi, '')
    // Clean up any double spaces left behind
    .replace(/  +/g, ' ')
    .trim();
}

function safeParseArticle(text: string) {
  let cleaned = text
    .replace(/^```json\s*/i, '')
    .replace(/^```\s*/i, '')
    .replace(/```\s*$/i, '')
    .trim()

  try { return JSON.parse(cleaned) } catch {}

  const match = cleaned.match(/\{[\s\S]*\}/)
  if (match) {
    try { return JSON.parse(match[0]) } catch {}
  }

  try {
    const fixed = cleaned.replace(/:\s*"([\s\S]*?)"/g, (_m, val) =>
      ': "' + val
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r')
        .replace(/\t/g, '\\t')
        .replace(/"/g, '\\"') + '"'
    )
    return JSON.parse(fixed)
  } catch {}

  return null
}

function slugify(text: string): string {
  return (
    text
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "")
      .slice(0, 80) +
    "-" +
    Date.now().toString(36)
  );
}

async function findSourceHunts(_topicId: string, keywords: string[]) {
  const { data } = await supabase
    .from("p2_source_hunts")
    .select("*")
    .is("topic_id", null)
    .not("content", "is", null)
    .order("fetched_at", { ascending: false })
    .limit(50);

  if (!data || data.length === 0) return [];
  const kws = (keywords ?? []).map((k) => String(k).toLowerCase()).filter(Boolean);
  if (kws.length === 0) return [];
  const matched = data.filter((hunt: any) => {
    const t = (hunt.title ?? "").toLowerCase();
    return kws.some((kw) => t.includes(kw));
  });
  return matched.slice(0, 3);
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  const startTime = Date.now();

  // 1. Top-scored pending topics
  const { data: topics, error: topicErr } = await supabase
    .from("p2_topics")
    .select("*")
    .eq("status", "pending")
    .gte("score_total", 60)
    .order("score_total", { ascending: false })
    .limit(6);

  if (topicErr) {
    return new Response(JSON.stringify({ ok: false, error: topicErr.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
  if (!topics || topics.length === 0) {
    return new Response(
      JSON.stringify({ ok: true, message: "No topics ready for synthesis" }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }

  // Skip topics that already have an article
  const topicIds = topics.map((t: any) => t.id);
  const { data: existing } = await supabase
    .from("p2_articles")
    .select("topic_id")
    .in("topic_id", topicIds);
  const existingIds = new Set((existing ?? []).map((e: any) => e.topic_id));
  const toProcess = topics.filter((t: any) => !existingIds.has(t.id));

  if (toProcess.length === 0) {
    return new Response(
      JSON.stringify({ ok: true, message: "All pending topics already synthesized" }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }

  const results: any[] = [];

  for (const topic of toProcess) {
    try {
      await supabase.from("p2_topics").update({ status: "synthesizing" }).eq("id", topic.id);

      const sourceHunts = await findSourceHunts(topic.id, topic.keywords ?? []);
      const hasPreloadedSources = sourceHunts.length > 0;

      const sourceContext = hasPreloadedSources
        ? sourceHunts
            .map((h: any) =>
              `SOURCE: ${h.title}\nURL: ${h.url}\nCONTENT: ${(h.content ?? "").slice(0, 2000)}`
            )
            .join("\n\n---\n\n")
        : "";

      const systemPrompt =
        `You are a senior editor at The Videshi (thevideshi.com), a premium news platform for the Indian-American diaspora.

Your job: write factual, original news articles sourced from official/public-domain sources only (government press releases, regulatory announcements, official statements).

Writing style:
- 250-320 words total
- Opening: strong lede with the core fact (who, what, when)
- Middle: 2-3 paragraphs of context and significance
- End: 1 sentence on what to watch next
- Tone: confident, clear, warm — like a trusted friend who follows Indian news closely
- NO passive voice, NO bureaucratic language
- DO NOT start with "The government today..." or "In a statement..."

The diaspora_angle must be exactly 1 sentence explaining why Indian-Americans specifically should care.

Return ONLY valid JSON. No markdown, no code fences, raw JSON only.

CRITICAL: Your response must be valid JSON. Never use unescaped double quotes inside string values. Use single quotes or escaped \\" instead. Never include raw newlines inside JSON string values — use \\n instead. Wrap all string values carefully.`;

      const userPrompt = `Write a news article for The Videshi about this topic:

TOPIC: ${topic.canonical_title}
VERTICAL: ${topic.vertical}
CATEGORY: ${topic.category ?? "news"}
URGENCY: ${topic.urgency}
KEYWORDS: ${(topic.keywords ?? []).join(", ")}
${
        hasPreloadedSources
          ? `\nPRE-LOADED SOURCE MATERIAL:\n${sourceContext}`
          : "\nNo pre-loaded sources — use web search to find the official press release, government announcement, or authoritative source for this story. Cite only public-domain or freely available sources."
      }

Return this exact JSON structure:
{
  "headline": "60-75 char punchy headline",
  "subheadline": "100-120 char explanatory deck",
  "body": "full article body, 250-320 words, markdown allowed for emphasis only",
  "diaspora_angle": "exactly 1 sentence: why Indian-Americans should care",
  "tags": ["tag1", "tag2", "tag3", "tag4"],
  "sources": [{"name": "Source Name", "url": "https://..."}],
  "confidence": 0-100
}`;

      const tools = !hasPreloadedSources
        ? [{ type: "web_search_20250305" as const, name: "web_search" }]
        : undefined;

      const response = await anthropic.messages.create({
        model: "claude-sonnet-4-6",
        max_tokens: 2000,
        system: systemPrompt,
        tools,
        messages: [{ role: "user", content: userPrompt }],
      });

      const textContent = response.content
        .filter((b: any) => b.type === "text")
        .map((b: any) => b.text)
        .join("");

      if (!textContent.trim()) throw new Error("No text content in Claude response");

      // Extract JSON from response (Claude sometimes adds prose around it)
      let jsonText = textContent.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "").trim();
      const firstBrace = jsonText.indexOf("{");
      const lastBrace = jsonText.lastIndexOf("}");
      if (firstBrace > 0 || lastBrace < jsonText.length - 1) {
        jsonText = jsonText.slice(firstBrace, lastBrace + 1);
      }
      const article = safeParseArticle(jsonText);
      if (!article) throw new Error("Failed to parse Claude JSON response");

      if (!article.headline || !article.body) {
        throw new Error("Missing required fields in Claude response");
      }

      const slug = slugify(article.headline);
      const wordCount = String(article.body).split(/\s+/).filter(Boolean).length;

      const autoPublish = topic.score_total >= 72 && (article.confidence ?? 0) >= 72;
      const status = autoPublish ? "published" : "review";
      const publishedAt = autoPublish ? new Date().toISOString() : null;

      const { error: insertErr } = await supabase.from("p2_articles").insert({
        topic_id: topic.id,
        headline: stripCitations(String(article.headline)).slice(0, 200),
        subheadline: article.subheadline ? stripCitations(String(article.subheadline)).slice(0, 300) : null,
        body: stripCitations(String(article.body)),
        diaspora_angle: article.diaspora_angle
          ? stripCitations(String(article.diaspora_angle)).slice(0, 500)
          : null,
        vertical: topic.vertical,
        category: VERTICAL_TO_CATEGORY[topic.vertical] ?? 'news',
        tags: Array.isArray(article.tags) ? article.tags : [],
        urgency: topic.urgency,
        sources: Array.isArray(article.sources) ? article.sources : [],
        slug,
        word_count: wordCount,
        status,
        is_featured: topic.score_total >= 82,
        published_at: publishedAt,
      });

      if (insertErr) throw new Error(`Insert failed: ${insertErr.message}`);

      if (hasPreloadedSources) {
        await supabase
          .from("p2_source_hunts")
          .update({ topic_id: topic.id, is_used: true })
          .in("id", sourceHunts.map((h: any) => h.id));
      }

      await supabase
        .from("p2_topics")
        .update({ status: autoPublish ? "published" : "review" })
        .eq("id", topic.id);

      results.push({
        topic: topic.canonical_title,
        status,
        headline: article.headline,
        wordCount,
        autoPublish,
      });
    } catch (err: any) {
      await supabase.from("p2_topics").update({ status: "pending" }).eq("id", topic.id);
      await supabase.from("pipeline_alerts").insert({
        agent: "p2-synthesize",
        severity: "error",
        error_type: "synthesis_failed",
        message: `Failed: ${topic.canonical_title} — ${err?.message ?? String(err)}`,
      });
      results.push({
        topic: topic.canonical_title,
        status: "error",
        error: err?.message ?? String(err),
      });
    }
  }

  const published = results.filter((r) => r.status === "published").length;
  const inReview = results.filter((r) => r.status === "review").length;
  const failed = results.filter((r) => r.status === "error").length;
  const elapsed = Date.now() - startTime;

  await supabase.from("pipeline_alerts").insert({
    agent: "p2-synthesize",
    severity: "info",
    error_type: null,
    message:
      `p2-synthesize: ${published} auto-published, ${inReview} in review, ${failed} failed in ${elapsed}ms`,
  });

  return new Response(
    JSON.stringify({ ok: true, published, inReview, failed, elapsed, results }),
    { headers: { ...corsHeaders, "Content-Type": "application/json" } },
  );
});
