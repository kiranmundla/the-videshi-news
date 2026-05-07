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

const MAX_ARTICLES_PER_RUN = 3;

async function callClaude(
  prompt: string,
  useWebSearch = false,
  systemPrompt?: string
): Promise<string> {
  const body: Record<string, unknown> = {
    model: "claude-sonnet-4-5",
    max_tokens: 8000,
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
  if (!res.ok || !data.content) {
    console.error("Claude API error:", res.status, JSON.stringify(data).slice(0, 500));
    return "";
  }
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
    // Tolerate truncated responses: extract the largest balanced JSON object we can
    const start = cleaned.indexOf("{");
    if (start === -1) throw new Error("no JSON object in response");
    let depth = 0;
    let end = -1;
    let inStr = false;
    let esc = false;
    for (let i = start; i < cleaned.length; i++) {
      const ch = cleaned[i];
      if (inStr) {
        if (esc) { esc = false; continue; }
        if (ch === "\\") { esc = true; continue; }
        if (ch === '"') inStr = false;
        continue;
      }
      if (ch === '"') { inStr = true; continue; }
      if (ch === "{") depth++;
      else if (ch === "}") { depth--; if (depth === 0) { end = i; break; } }
    }
    const slice = end !== -1 ? cleaned.slice(start, end + 1) : cleaned.slice(start);
    const parsed = JSON.parse(slice);
    return parsed.groups || [];
  } catch (err) {
    console.error("Failed to parse ranking response. len=" + response.length + " err=" + (err as Error).message);
    console.error("First 500 chars:", response.slice(0, 500));
    console.error("Last 300 chars:", response.slice(-300));
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
    const stripCitations = (s: string) =>
      typeof s === "string"
        ? s.replace(/<\/?cite\b[^>]*>/gi, "").replace(/\[\d+(?:[-,\s]\d+)*\]/g, "")
        : s;
    const cleanedBody = stripCitations(parsed.body || "");
    const cleanedSummary = stripCitations(parsed.summary || "");
    const cleanedNri = parsed.nriAngle ? stripCitations(parsed.nriAngle) : null;
    const wordCount = cleanedBody.split(/\s+/).filter(Boolean).length;

    return {
      title: parsed.title || group.storyHeadline,
      slug: parsed.slug || slugify(group.storyHeadline),
      summary: cleanedSummary,
      body: cleanedBody,
      nriAngle: cleanedNri,
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

    // Fetch recent published articles (last 48h) for duplicate detection / update
    const recentSince = new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString();
    const { data: recentArticles } = await supabase
      .from("articles")
      .select("id, slug, title, summary, body, sources_used, category, tags, nri_angle, image_url")
      .eq("is_published", true)
      .gte("published_at", recentSince)
      .order("published_at", { ascending: false })
      .limit(50);

    const successfullyProcessedRawIds = new Set<string>();

    for (const group of topGroups) {
      const bestArticle = (rawArticles as RawArticle[]).find(
        (a) => a.id === group.bestArticleId
      );
      if (!bestArticle) continue;

      // Option B: ask Claude if this story matches a recent article, and if so
      // whether the new raw articles add a materially new development.
      if (recentArticles && recentArticles.length > 0) {
        const dupPrompt = `You are checking whether a candidate news story matches a recently-published article, and if so whether it adds a materially new development.

CANDIDATE NEW STORY:
Headline: ${group.storyHeadline}
Best excerpt: ${bestArticle.title} — ${bestArticle.description?.slice(0, 300)}
Other raw items in this group:
${(rawArticles as RawArticle[])
  .filter((a) => group.articleIds.includes(a.id) && a.id !== group.bestArticleId)
  .slice(0, 5)
  .map((a, i) => `${i + 1}. ${a.title} — ${a.description?.slice(0, 200)}`)
  .join("\n") || "(none)"}

ALREADY-PUBLISHED ARTICLES (last 48h):
${recentArticles.map((a, i) => `[${i}] id=${a.id}\n  Title: ${a.title}\n  Summary: ${a.summary?.slice(0, 200)}`).join("\n\n")}

Decide:
1. Does the candidate cover the SAME underlying news event/incident/announcement as one of the published articles? (match)
2. If matched, does the candidate add a MATERIALLY NEW development? (e.g., new casualty figures, new official statement, arrest, court ruling, escalation, retraction). Minor rephrasing or the same facts = NOT material.

Respond ONLY with valid JSON:
{"match": true|false, "matchedIndex": <number or null>, "materialUpdate": true|false, "reason": "short reason"}`;

        try {
          const dupRes = await callClaude(dupPrompt);
          const m = dupRes.match(/\{[\s\S]*\}/);
          if (m) {
            const parsed = JSON.parse(m[0]);
            if (parsed.match === true && typeof parsed.matchedIndex === "number") {
              const matched = recentArticles[parsed.matchedIndex];
              if (matched && parsed.materialUpdate !== true) {
                console.log(`Skipping duplicate: "${group.storyHeadline}" — ${parsed.reason}`);
                for (const rid of group.articleIds) successfullyProcessedRawIds.add(rid);
                continue;
              }
              if (matched && parsed.materialUpdate === true) {
                console.log(`Updating existing article ${matched.id}: "${group.storyHeadline}" — ${parsed.reason}`);
                const updated = await regenerateArticleUpdate(group, bestArticle, matched, rawArticles as RawArticle[]);
                if (updated) {
                  const nowIso = new Date().toISOString();
                  const updateLine = `_Updated: ${nowIso}_\n\n`;
                  const newBody = updateLine + updated.body;
                  const existingSources = Array.isArray(matched.sources_used) ? matched.sources_used : [];
                  const seen = new Set(existingSources.map((s: { url?: string }) => s?.url).filter(Boolean));
                  const mergedSources = [
                    ...existingSources,
                    ...updated.sourcesUsed.filter((s) => s?.url && !seen.has(s.url)),
                  ];
                  const wordCount = newBody.split(/\s+/).filter(Boolean).length;
                  const { error: updErr } = await supabase
                    .from("articles")
                    .update({
                      summary: updated.summary || matched.summary,
                      body: newBody,
                      nri_angle: updated.nriAngle ?? matched.nri_angle,
                      sources_used: mergedSources,
                      tags: updated.tags?.length ? updated.tags : matched.tags,
                      word_count: wordCount,
                      read_time_min: Math.ceil(wordCount / 200),
                      image_url: matched.image_url || bestArticle.image_url || null,
                      updated_at: nowIso,
                    })
                    .eq("id", matched.id);
                  if (!updErr) {
                    articlesCreated++;
                    for (const rid of group.articleIds) successfullyProcessedRawIds.add(rid);
                    await supabase
                      .from("story_groups")
                      .update({ enriched: true })
                      .eq("priority", group.priority)
                      .eq("run_id", runId);
                  } else {
                    console.error("Article update error:", updErr.message);
                  }
                } else {
                  console.warn("Regeneration failed; leaving existing article unchanged");
                  for (const rid of group.articleIds) successfullyProcessedRawIds.add(rid);
                }
                await new Promise((r) => setTimeout(r, 2000));
                continue;
              }
            }
          }
        } catch (err) {
          console.warn("Duplicate check failed, proceeding to generate:", (err as Error).message);
        }
      }

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
        // Mark only the raw articles in this successfully-published group as processed
        for (const rid of group.articleIds) successfullyProcessedRawIds.add(rid);
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

    // Only mark raw articles processed if their group produced a published article.
    // Unprocessed raw articles will be retried on the next run.
    if (successfullyProcessedRawIds.size > 0) {
      await supabase
        .from("raw_articles")
        .update({ processed: true })
        .in("id", Array.from(successfullyProcessedRawIds));
    }

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
