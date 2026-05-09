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
  if (!text) return text
  return text
    // Remove <cite index="...">text</cite> — keep inner text
    .replace(/<cite[^>]*>([\s\S]*?)<\/cite>/gi, '$1')
    // Remove standalone [N] or [N-N] citation markers
    .replace(/\s*\[\d+(?:[–\-]\d+)?\]/g, '')
    // Remove leftover empty cite tags
    .replace(/<\/?cite[^>]*>/gi, '')
    // Clean up double spaces
    .replace(/  +/g, ' ')
    .trim()
}

function extractArticle(text: string): any {
  const clean = text
    .replace(/^```json\s*/i, '')
    .replace(/^```\s*/i, '')
    .replace(/```\s*$/i, '')
    .trim()

  let article = null

  try {
    article = JSON.parse(clean)
  } catch {
    const start = clean.indexOf('{')
    const end = clean.lastIndexOf('}')
    if (start !== -1 && end !== -1) {
      try {
        article = JSON.parse(clean.slice(start, end + 1))
      } catch {
        article = null
      }
    }
  }

  return article
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
  const start = Date.now();

  // 1. Top-scored pending topics
  const { data: topics, error: topicErr } = await supabase
    .from("p2_topics")
    .select("*")
    .eq("status", "pending")
    .gte("score_total", 60)
    .order("score_total", { ascending: false })
    .limit(2);

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
  console.log(`[timing] topics fetched: ${Date.now() - start}ms`)

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
      console.log(`[timing] source hunts fetched: ${Date.now() - start}ms`)

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

ARTICLE STRUCTURE (mandatory for every article):
Every article body MUST have this structure:

[Opening paragraph — 2-3 sentences, the core news]

**[Section header — what happened]:**
[2-3 sentences of detail]

**[Section header — context or implications]:**
[2-3 sentences of context]

**[Section header — what to watch]:**
[1-2 sentences on what comes next]

Section headers MUST use **bold:** format.
Every article must have at least 2 bold section headers — never write a wall of plain paragraphs.
Do not use ## markdown headers — use **bold:** only.
Do not use bullet points or numbered lists.
Write in the style of The Economist — precise, authoritative, one idea per sentence.

Return ONLY valid JSON. No markdown, no code fences, raw JSON only.

CRITICAL JSON RULES — never break these:
- Never use straight double quotes " inside any string value in your JSON response
- For dialogue or attribution use single quotes: He said 'this is important'
- For emphasis use asterisks: *important point*
- Your entire response must be parseable by JSON.parse() with no pre-processing
- Test mentally: would JSON.parse(yourResponse) throw an error? If yes, fix it before responding
OUTPUT FORMAT: Respond with valid JSON only.
The body field will contain article text.
Any quotation marks within the body text MUST use single quotes instead of double quotes.
Example: He said 'this matters' not He said 'this matters'.
Never use \" escape sequences.
Write body text as if double quotes do not exist.`;

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

      console.log(`[timing] calling Claude for: ${topic.canonical_title}`)
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
      console.log(`[timing] Claude responded: ${Date.now() - start}ms`)

      const article = extractArticle(textContent);
      console.log(`[timing] parsed response: ${Date.now() - start}ms`)
      if (!article) {
        console.error("Failed to parse Claude JSON response", {
          topicId: topic.id,
          topic: topic.canonical_title,
          responsePreview: textContent.slice(0, 2000),
        });
        await supabase.from("pipeline_alerts").insert({
          agent: 'p2-synthesize',
          severity: 'warning',
          message: 'Skipped topic — unparseable JSON response'
        });
        results.push({
          topic: topic.canonical_title,
          status: "error",
          error: "Skipped topic — unparseable JSON response",
        });
        continue;
      }

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
        tags: Array.isArray(article.tags) ? article.tags.map((t: any) => stripCitations(String(t))) : [],
        urgency: topic.urgency,
        sources: Array.isArray(article.sources) ? article.sources : [],
        slug,
        word_count: wordCount,
        status,
        is_featured: topic.score_total >= 82,
        published_at: publishedAt,
      });

      if (insertErr) throw new Error(`Insert failed: ${insertErr.message}`);
      console.log(`[timing] saved to db: ${Date.now() - start}ms`)

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
