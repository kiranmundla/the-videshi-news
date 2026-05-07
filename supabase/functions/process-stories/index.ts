// supabase/functions/process-stories/index.ts
// ============================================================
// Runs every 30 minutes via Supabase cron scheduler.
//
// Pipeline:
//   1. Pull unprocessed raw_articles from last 3 hours
//   2. Claude groups + ranks them by source coverage
//   3. For each top story, Claude searches web + writes full article
//   4. Auto-categorizes and stores in articles table
// ============================================================

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
);

const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY")!;

const MAX_ARTICLES_PER_RUN = 5;

async function callClaude(
  prompt: string,
  useWebSearch = false,
  systemPrompt?: string
): Promise<string> {
  const body: Record<string, unknown> = {
    model: "claude-sonnet-4-20250514",
    max_tokens: 2000,
    messages: [{ role: "user", content: prompt }],
  };
  if (systemPrompt) body.system = systemPrompt;
  if (useWebSearch) {
    body.tools = [{ type: "web_search_20250305", name: "web_search" }];
  }

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
      ...(useWebSearch ? { "anthropic-beta": "web-search-2025-03-05" } : {}),
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();
  return (data.content || [])
    .filter((b: { type: string }) => b.type === "text")
    .map((b: { text: string }) => b.text)
    .join("\n");
}

interface RawArticle {
  id: string;
  title: string;
  description: string;
  source_name: string;
  url: string;
  image_url: string;
  published_at: string;
}

interface StoryGroup {
  priority: number;
  storyHeadline: string;
  category: string;
  sourceCount: number;
  sources: string[];
  articleIds: string[];
  bestArticleId: string;
  diasporaRelevant: boolean;
}

async function rankStories(articles: RawArticle[]): Promise<StoryGroup[]> {
  const prompt = `You are the news editor for an Indian-American diaspora news platform.

Below are ${articles.length} articles scraped from Indian news RSS feeds in the last 3 hours.

YOUR TASKS:
1. GROUP articles covering the same story/event (same news within 24hrs). Use semantic understanding — same event even if headlines differ.
2. RANK groups by priority: more sources = bigger story = higher priority.
3. CATEGORIZE each group using exactly one of: breaking | politics | business | us-india | technology | entertainment | sports | health | crime | world
   - "us-india": specifically US-India relations, NRI/diaspora affairs, visa/immigration
   - "breaking": major urgent news (violence, disasters, major political events)
4. Mark diasporaRelevant=true if Indian-Americans would especially care.
5. Return top 8 groups maximum.

ARTICLES:
${JSON.stringify(articles.map(a => ({
  id: a.id,
  title: a.title,
  source: a.source_name,
  desc: a.description?.slice(0, 120),
})))}

Respond ONLY with valid JSON, no markdown:
{
  "groups": [
    {
      "priority": 1,
      "storyHeadline": "Short punchy editorial headline",
      "category": "breaking",
      "sourceCount": 3,
      "sources": ["NDTV", "TOI", "The Hindu"],
      "articleIds": ["uuid1", "uuid2", "uuid3"],
      "bestArticleId": "uuid2",
      "diasporaRelevant": true
    }
  ]
}`;

  const response = await callClaude(prompt);
  try {
    const cleaned = response.replace(/```json|```/g, "").trim();
    const parsed = JSON.parse(cleaned);
    return parsed.groups || [];
  } catch {
    console.error("Failed to parse ranking response:", response.slice(0, 200));
    return [];
  }
}

interface GeneratedArticle {
  title: string;
  slug: string;
  summary: string;
  body: string;
  nriAngle: string | null;
  sourcesUsed: { name: string; url: string; type: string }[];
  tags: string[];
  wordCount: number;
}

function slugify(text: string): string {
  const date = new Date().toISOString().slice(0, 10);
  return (
    text
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .slice(0, 60) + `-${date}`
  );
}

async function generateArticle(
  group: StoryGroup,
  bestArticle: RawArticle
): Promise<GeneratedArticle | null> {
  const prompt = `You are a journalist writing for an Indian-American diaspora news platform. 
Your readers are educated Indian-Americans who want substantive news about India — not clickbait.

STORY TO COVER:
Headline: ${group.storyHeadline}
Category: ${group.category}
Sources that covered it: ${group.sources.join(", ")}
Best RSS excerpt available:
  Title: ${bestArticle.title}
  Description: ${bestArticle.description}
  Source: ${bestArticle.source_name}
  URL: ${bestArticle.url}

YOUR TASKS:
1. Use web_search to find 3-5 additional sources on this story. Prioritize:
   - Official sources: PIB (pib.gov.in), Newsonair (newsonair.gov.in), ECI, NIA, RBI statements
   - Wire services: ANI (aninews.in), PTI, IANS
   - Reputable news: NDTV, The Hindu, Al Jazeera, BBC India
2. Write a complete, publish-ready article (300-500 words) in markdown format.
   - Lead paragraph: who/what/where/when/why
   - Key facts with specific numbers and named officials
   - Political/official reactions
   - Context/background (1 paragraph)
   - ${group.diasporaRelevant ? "NRI Angle paragraph: why Indian-Americans specifically should care" : "Skip NRI angle — not strongly relevant"}
3. Respond ONLY with valid JSON (no markdown wrapper):

{
  "title": "Final editorial headline (compelling, not clickbait)",
  "slug": "url-friendly-slug-with-date",
  "summary": "2-3 sentence summary for the article card",
  "body": "Full article in markdown (300-500 words)",
  "nriAngle": "1-2 sentence NRI/diaspora angle, or null if not relevant",
  "sourcesUsed": [
    {"name": "Newsonair", "url": "https://...", "type": "official"},
    {"name": "ANI", "url": "https://...", "type": "wire"},
    {"name": "NDTV", "url": "https://...", "type": "news"}
  ],
  "tags": ["West Bengal", "BJP", "post-poll violence", "election"]
}`;

  try {
    const response = await callClaude(
      prompt,
      true,
      "You are a professional journalist. Always search for official and wire sources first. Write factually and neutrally."
    );

    const cleaned = response.replace(/```json|```/g, "").trim();
    const jsonMatch = cleaned.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("No JSON found in response");

    const parsed = JSON.parse(jsonMatch[0]);
    const wordCount = parsed.body?.split(/\s+/).length || 0;

    return {
      title: parsed.title || group.storyHeadline,
      slug: parsed.slug || slugify(group.storyHeadline),
      summary: parsed.summary || "",
      body: parsed.body || "",
      nriAngle: parsed.nriAngle || null,
      sourcesUsed: parsed.sourcesUsed || [],
      tags: parsed.tags || [],
      wordCount,
    };
  } catch (err) {
    console.error(
      `Article generation failed for "${group.storyHeadline}":`,
      (err as Error).message
    );
    return null;
  }
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  const runId = crypto.randomUUID();
  let groupsCreated = 0;
  let articlesCreated = 0;

  await supabase.from("pipeline_runs").insert({
    id: runId,
    run_type: "process",
    status: "running",
  });

  try {
    const since = new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString();
    const { data: rawArticles, error: fetchErr } = await supabase
      .from("raw_articles")
      .select("*")
      .eq("processed", false)
      .gte("fetched_at", since)
      .order("fetched_at", { ascending: false })
      .limit(100);

    if (fetchErr) throw fetchErr;
    if (!rawArticles || rawArticles.length === 0) {
      console.log("No unprocessed articles found");
      await supabase
        .from("pipeline_runs")
        .update({ status: "done", finished_at: new Date().toISOString() })
        .eq("id", runId);
      return new Response(
        JSON.stringify({ success: true, message: "Nothing to process" }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    console.log(`Processing ${rawArticles.length} raw articles`);

    const groups = await rankStories(rawArticles as RawArticle[]);
    console.log(`Got ${groups.length} story groups`);

    for (const group of groups) {
      const { error } = await supabase.from("story_groups").insert({
        priority: group.priority,
        story_headline: group.storyHeadline,
        category: group.category,
        source_count: group.sourceCount,
        sources: group.sources,
        raw_article_ids: group.articleIds,
        best_article_id: group.bestArticleId,
        diaspora_relevant: group.diasporaRelevant,
        enriched: false,
        run_id: runId,
      });
      if (!error) groupsCreated++;
    }

    const topGroups = groups
      .filter((g) => g.sourceCount >= 1)
      .sort((a, b) => a.priority - b.priority)
      .slice(0, MAX_ARTICLES_PER_RUN);

    for (const group of topGroups) {
      const bestArticle = (rawArticles as RawArticle[]).find(
        (a) => a.id === group.bestArticleId
      );
      if (!bestArticle) continue;

      console.log(`Generating article: "${group.storyHeadline}"`);
      const generated = await generateArticle(group, bestArticle);
      if (!generated) continue;

      const { error: articleErr } = await supabase.from("articles").insert({
        story_group_id: null,
        title: generated.title,
        slug: generated.slug,
        category: group.category,
        summary: generated.summary,
        body: generated.body,
        nri_angle: generated.nriAngle,
        sources_used: generated.sourcesUsed,
        image_url: bestArticle.image_url || null,
        word_count: generated.wordCount,
        read_time_min: Math.ceil(generated.wordCount / 200),
        tags: generated.tags,
        is_published: true,
        published_at: new Date().toISOString(),
      });

      if (!articleErr) {
        articlesCreated++;
        await supabase
          .from("story_groups")
          .update({ enriched: true })
          .eq("priority", group.priority)
          .eq("run_id", runId);
      } else {
        console.error("Article insert error:", articleErr.message);
      }

      await new Promise((r) => setTimeout(r, 2000));
    }

    const processedIds = (rawArticles as RawArticle[]).map((a) => a.id);
    await supabase
      .from("raw_articles")
      .update({ processed: true })
      .in("id", processedIds);

    await supabase
      .from("pipeline_runs")
      .update({
        status: "done",
        groups_created: groupsCreated,
        articles_created: articlesCreated,
        finished_at: new Date().toISOString(),
      })
      .eq("id", runId);

    console.log(
      `Done — groups: ${groupsCreated}, articles: ${articlesCreated}`
    );

    return new Response(
      JSON.stringify({ success: true, groupsCreated, articlesCreated }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (err) {
    console.error("Process run failed:", err);
    await supabase
      .from("pipeline_runs")
      .update({
        status: "error",
        error_message: (err as Error).message,
        finished_at: new Date().toISOString(),
      })
      .eq("id", runId);

    return new Response(
      JSON.stringify({ success: false, error: (err as Error).message }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});
