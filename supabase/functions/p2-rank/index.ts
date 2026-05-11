// p2-rank — clusters unprocessed p2_signals into p2_topics using Claude Haiku.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const GEMINI_KEY = Deno.env.get("GEMINI_API_KEY")!;

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);
const VERTICAL_TO_CATEGORY: Record<string, string> = {
  politics: "news",
  economy: "markets-finance",
  tech: "technology",
  immigration: "nri-world",
  diaspora: "nri-world",
  science: "technology",
  culture: "lifestyle-health",
  sports: "sports",
  entertainment: "entertainment",
  education: "news",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  const startTime = Date.now();

  // 1. Fetch unprocessed signals
  const { data: signals, error: sigErr } = await supabase
    .from("p2_signals")
    .select("id, title, feed_source_id, published_at")
    .eq("is_processed", false)
    .gte("published_at", new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString())
    .order("published_at", { ascending: false, nullsFirst: false })
    .limit(80);

  // 1b. Fetch source metadata from videshi_sources
  const sourceIds = [...new Set((signals ?? []).map((s: any) => s.feed_source_id).filter(Boolean))];
  const { data: sourcesData } = await supabase
    .from("videshi_sources")
    .select("id, name, slug, categories, priority")
    .in("id", sourceIds);
  const sourceMap: Record<string, any> = Object.fromEntries(
    (sourcesData ?? []).map((s: any) => [s.id, s])
  );

  if (sigErr) {
    return new Response(JSON.stringify({ ok: false, error: sigErr.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
  if (!signals || signals.length === 0) {
    return new Response(
      JSON.stringify({ ok: true, message: "No unprocessed signals", elapsed: Date.now() - startTime }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }

  // 2. Build headline list
  const headlineList = signals
    .map((s: any, i: number) => {
      const src = sourceMap[s.feed_source_id];
      const hoursAgo = s.published_at
        ? Math.round((Date.now() - new Date(s.published_at).getTime()) / 3_600_000)
        : 24;
      const tier = (src?.priority ?? 50) >= 80
        ? "TOP-STORY"
        : (src?.priority ?? 50) >= 60
        ? "SECTION"
        : "SPECIALIST";
      return `[${i}] "${s.title}" — ${src?.name ?? "unknown"} [${tier}, ${hoursAgo}h ago]`;
    })
    .join("\n");

  // 2b. Fetch recently published articles (for re-ranking)
  const { data: recentArticles } = await supabase
    .from("p2_articles")
    .select("id, headline, category, score_total, published_at")
    .eq("status", "published")
    .gte("published_at", new Date(Date.now() - 96 * 60 * 60 * 1000).toISOString())
    .order("published_at", { ascending: false })
    .limit(40);

  const publishedHeadlines = (recentArticles ?? [])
    .map((a: any) => {
      const hoursAgo = a.published_at
        ? Math.round((Date.now() - new Date(a.published_at).getTime()) / 3_600_000)
        : 0;
      return `- ${a.id} | "${a.headline}" [${a.category}, ${hoursAgo}h ago]`;
    })
    .join("\n");

  // 3. Three independent Gemini prompts (split to avoid 503/MAX_TOKENS on one giant call)

  // ---- Prompt A: Re-rank existing published articles ----
  const promptRerank = `
You are the chief editor of The Videshi (Indian diaspora news platform).
Today's date and time: ${new Date().toISOString()}

EXISTING PUBLISHED ARTICLES (re-rank these):
${publishedHeadlines}

For each article return a single final score 0-100 considering:
- Diaspora relevance, story significance
- Age relative to NOW
- Whether story is developing/resolved/evergreen/stale

Decay guidance:
  Breaking (<6h): full value
  Fresh (6-24h): slight decay if resolved
  Yesterday (24-48h): significant decay unless developing
  Old (48-72h): heavy decay unless evergreen
  Archive (72h+): minimal unless truly evergreen

Return ONLY raw JSON, no markdown:
{ "re_ranked": [ { "id": "uuid", "score_final": 0-100, "freshness_note": "breaking|developing|resolved|evergreen|stale" } ] }
`;

  // ---- Prompt B: Cluster + rank new RSS signals ----
  const promptCluster = `
You are the chief editor of The Videshi, a premium news platform for the Indian diaspora globally (US, UK, Australia, UAE, Canada, Singapore).
Today's date: ${new Date().toISOString()}

ALREADY PUBLISHED (do NOT recreate topics already covering these events):
${publishedHeadlines}

NEW RSS SIGNALS TO CLUSTER:
${headlineList}

Group signals into unique story topics. Skip events already covered above.
Same event examples:
- 'Vijay sworn in' + 'Vijay takes oath' = SAME EVENT (skip)
- 'Vijay cabinet announced' = DIFFERENT EVENT (include)
Only create new topics for genuinely new events.

For each topic return:
- canonical_title: clear headline, full names
- vertical: politics|economy|tech|immigration|diaspora|science|culture|sports|entertainment|education
- category: news|entertainment|sports|markets-finance|technology|nri-world|lifestyle-health|travel|food
  CATEGORY RULES:
  Use 'news' ONLY for India-domestic stories (events INSIDE India).
  Use 'nri-world' for Indian-origin people OUTSIDE India (Pramila Jayapal, Sundar Pichai, Satya Nadella, etc.).
- event_type: election-result|swearing-in|policy-announcement|policy-update|match-result|match-preview|birthday|film-release|arrest-raid|court-ruling|market-move|diplomatic-meeting|natural-disaster|obituary|protest|accident|appointment|resignation|award|statement|report-release|other
- event_date: YYYY-MM-DD
- score_diaspora: 0-100
    90-100: H-1B/visa/immigration, Indian-Americans, India-US policy
    75-89: National elections, India-Pakistan/China, Bollywood A-list, cricket WC/IPL finals
    65-74: Major Indian state politics
    50-64: National India politics, economy, IPL
    30-49: India-domestic, minimal diaspora relevance
    5-25: Non-Indian celebs, unrelated global news
    Indian state board exams = max 35; non-Indian celebs = max 20;
    celebrity birthdays = max 55; local India crime = max 30
- score_significance: 0-100
- urgency: breaking|daily|evergreen
- keywords: 3-5 search terms
- signal_indices: [N] indices from RSS list above
- key_entities: [{ name, type: politician|actor|athlete|businessman|organization|place|event|policy, entity_id: "disambiguated-slug" }]
  DISAMBIGUATION examples:
  - Vijay (TVK Tamil Nadu CM) = vijay-politician-tamil-nadu
  - Vijay Deverakonda (actor) = vijay-deverakonda-actor-telugu
  - Congress India = inc-organization-india vs Congress USA = us-congress-organization-usa
- free_sources: 2-3 copyright-free URLs (PIB → Wikipedia → official govt). NEVER NDTV/TOI/Hindu/IE/BBC.
- synthesis_angle: one sentence diaspora angle
- image: ONE object {
    url: direct image URL — for Wikimedia use https://commons.wikimedia.org/wiki/Special:FilePath/FILENAME.jpg (NOT /thumb/), null for Unsplash/Pexels,
    search_query: 4-6 word specific query (always required),
    source: "wikimedia-commons|pib|unsplash|pexels|pixabay",
    attribution: e.g. "Photo: Wikimedia Commons / CC BY-SA 4.0",
    alt_text: describe ideal image,
    license: "cc-by-sa|cc-by|public-domain|free-to-use"
  }
  NEVER suggest Getty/AP/Reuters/news site images.

Return ONLY raw JSON, no markdown:
{ "ranked_topics": [...] }
Exclude topics with score_diaspora < 40. Maximum 12 topics.
`;

  // ---- Prompt C: Carousel photos ----
  const promptCarousel = `
You are the photo editor of The Videshi (Indian diaspora news platform).
Today: ${new Date().toISOString()}

Suggest 5 high-quality images for the homepage carousel — major events, cultural moments, sports from the last 48 hours relevant to the Indian diaspora.

Return ONLY raw JSON, no markdown:
{
  "carousel_photos": [
    {
      "title": "short caption",
      "description": "2-3 sentence context",
      "image": {
        "url": "direct image URL",
        "source": "Wikimedia Commons|PIB|Unsplash|Pexels",
        "attribution": "credit text",
        "license": "public-domain|cc-by|cc-by-sa|free-to-use"
      },
      "related_topic": "topic name or null"
    }
  ]
}
Use only copyright-free sources. NEVER Getty/AP/Reuters.
`;
  let topics: any[] = [];
  let discoveredTopics: any[] = [];
  let carouselPhotos: any[] = [];
  let reRanked: any[] = [];

  // Helper: call Gemini once with retry + 2.0-flash fallback on overload
  const runGemini = async (prompt: string, useGrounding: boolean, label: string): Promise<any> => {
    const callOnce = (model: string) => fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${GEMINI_KEY}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          ...(useGrounding ? { tools: [{ googleSearch: {} }] } : {}),
          generationConfig: {
            temperature: 0.1,
            thinkingConfig: { thinkingBudget: 0 },
            maxOutputTokens: 16384,
          },
        }),
      },
    );

    const models = ["gemini-2.5-flash", "gemini-2.5-flash", "gemini-2.0-flash"];
    let geminiData: any = null;
    let lastStatus = 0;
    for (let i = 0; i < models.length; i++) {
      if (i > 0) await new Promise((r) => setTimeout(r, 2000 * i));
      const response = await callOnce(models[i]);
      lastStatus = response.status;
      geminiData = await response.json().catch(() => null);
      const overloaded = response.status === 503 || geminiData?.error?.code === 503;
      const hasText = geminiData?.candidates?.[0]?.content?.parts?.some?.((p: any) => p?.text);
      if (response.ok && hasText) break;
      if (!overloaded && i === 0) break;
      console.warn(`[p2-rank:${label}] model=${models[i]} status=${response.status} overloaded=${overloaded} retry…`);
    }
    if (!geminiData) throw new Error(`[${label}] Gemini fetch failed (status=${lastStatus})`);

    const candidate = geminiData?.candidates?.[0];
    const finishReason = candidate?.finishReason;
    const parts = candidate?.content?.parts ?? [];
    const raw = parts.map((p: any) => p?.text ?? "").join("").trim();
    if (!raw) {
      await supabase.from("pipeline_alerts").insert({
        agent: "p2-rank",
        severity: "error",
        error_type: "empty_response",
        message: `[${label}] empty. finishReason=${finishReason} err=${JSON.stringify(geminiData?.error ?? geminiData?.promptFeedback ?? {}).slice(0, 400)}`,
      });
      throw new Error(`[${label}] Gemini empty (finishReason=${finishReason})`);
    }

    let cleaned = raw.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "").trim();
    cleaned = cleaned.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "");
    try {
      return JSON.parse(cleaned);
    } catch (parseErr) {
      const lastBrace = Math.max(cleaned.lastIndexOf("}"), cleaned.lastIndexOf("]"));
      if (lastBrace > 0) {
        let repaired = cleaned.slice(0, lastBrace + 1);
        for (let attempt = 0; attempt < 5; attempt++) {
          try {
            const data = JSON.parse(repaired);
            await supabase.from("pipeline_alerts").insert({
              agent: "p2-rank",
              severity: "warning",
              error_type: "json_repair",
              message: `[${label}] repaired truncated JSON (len ${raw.length})`,
            });
            return data;
          } catch {
            repaired = repaired.replace(/,\s*$/, "");
            repaired += attempt % 2 === 0 ? "]" : "}";
          }
        }
      }
      throw parseErr;
    }
  };

  // Run all three calls in parallel — independent, can fail individually
  const [rerankRes, clusterRes, carouselRes] = await Promise.allSettled([
    runGemini(promptRerank, false, "rerank"),
    runGemini(promptCluster, true, "cluster"),
    runGemini(promptCarousel, true, "carousel"),
  ]);

  if (rerankRes.status === "fulfilled") {
    reRanked = rerankRes.value?.re_ranked ?? [];
  } else {
    await supabase.from("pipeline_alerts").insert({
      agent: "p2-rank", severity: "warning", error_type: "rerank_failed",
      message: `rerank: ${(rerankRes.reason?.message ?? String(rerankRes.reason)).slice(0, 500)}`,
    });
  }

  if (clusterRes.status === "fulfilled") {
    const data = clusterRes.value;
    topics = Array.isArray(data) ? data : (data?.ranked_topics ?? []);
  } else {
    await supabase.from("pipeline_alerts").insert({
      agent: "p2-rank", severity: "error", error_type: "cluster_failed",
      message: `cluster: ${(clusterRes.reason?.message ?? String(clusterRes.reason)).slice(0, 500)}`,
    });
  }

  if (carouselRes.status === "fulfilled") {
    carouselPhotos = carouselRes.value?.carousel_photos ?? [];
  } else {
    await supabase.from("pipeline_alerts").insert({
      agent: "p2-rank", severity: "warning", error_type: "carousel_failed",
      message: `carousel: ${(carouselRes.reason?.message ?? String(carouselRes.reason)).slice(0, 500)}`,
    });
  }

  await supabase.from("pipeline_alerts").insert({
    agent: "p2-rank",
    severity: "info",
    error_type: "debug",
    message: `split-call done: rerank=${reRanked.length} topics=${topics.length} carousel=${carouselPhotos.length}`,
  });


  // Apply re-ranking to existing articles
  for (const item of reRanked) {
    if (!item?.id || item?.score_final === undefined) continue;
    await supabase
      .from('p2_articles')
      .update({ score_total: Math.round(item.score_final) })
      .eq('id', item.id);
  }

  // Fallback decay for articles not returned by re-ranking
  const reRankedIds = new Set(reRanked.map((r: any) => r.id));
  for (const article of recentArticles ?? []) {
    if (reRankedIds.has(article.id)) continue;

    const hoursAgo = (Date.now() - new Date(article.published_at).getTime()) / 3_600_000;

    const freshness =
      hoursAgo <= 6  ? 1.00 :
      hoursAgo <= 12 ? 0.90 :
      hoursAgo <= 24 ? 0.75 :
      hoursAgo <= 48 ? 0.55 :
      hoursAgo <= 72 ? 0.35 : 0.20;

    const currentScore = article.score_total ?? 50;
    const decayedScore = Math.round(currentScore * freshness);

    if (decayedScore !== currentScore) {
      await supabase
        .from('p2_articles')
        .update({ score_total: decayedScore })
        .eq('id', article.id);
    }
  }

  // 48h dedup window with entity-aware comparison
  const sinceIso = new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString();
  let insertedTopics = 0;
  let skippedDupes = 0;

  const { data: recentTopics } = await supabase
    .from("p2_topics")
    .select("id, canonical_title, keywords")
    .gte("created_at", sinceIso);

  // Lightweight extractor: capitalized 1-3 word proper-noun phrases
  const PROPER_NOUN_RE = /\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})\b/g;
  const STOPWORDS = new Set([
    "The", "A", "An", "In", "On", "At", "Of", "And", "Or", "But", "For", "To",
    "From", "By", "With", "After", "Before", "India", "Indian",
  ]);
  const extractEntities = (title: string): string[] => {
    const out = new Set<string>();
    const matches = title.match(PROPER_NOUN_RE) ?? [];
    for (const m of matches) {
      if (STOPWORDS.has(m)) continue;
      out.add(m.toLowerCase());
    }
    return [...out];
  };

  const recentEntitySets = (recentTopics ?? []).map((t: any) => {
    const fromTitle = extractEntities(String(t.canonical_title ?? ""));
    const fromKeywords = (Array.isArray(t.keywords) ? t.keywords : []).map((k: any) =>
      String(k).toLowerCase()
    );
    return { entities: new Set<string>([...fromTitle, ...fromKeywords]) };
  });

  const publishedEntitySets = (recentArticles ?? []).map((a: any) => ({
    entities: new Set<string>(extractEntities(String(a.headline)))
  }));

  // Duplicate if 2+ shared entities with any recent topic
  // Politics/news verticals need a higher threshold because celebrity names
  // (e.g. "Vijay") collide across entertainment and politics contexts.
  const HIGH_THRESHOLD_VERTICALS = new Set(["politics", "news"]);
  const isDuplicate = (candidateEntities: string[], vertical: string): boolean => {
    if (candidateEntities.length === 0) return false;
    const threshold = HIGH_THRESHOLD_VERTICALS.has(vertical) ? 3 : 2;
    // Check recent topics
    for (const r of recentEntitySets) {
      let shared = 0;
      for (const e of candidateEntities) if (r.entities.has(e)) shared++;
      if (shared >= threshold) return true;
    }
    // Check published articles (threshold always 2)
    for (const r of publishedEntitySets) {
      let shared = 0;
      for (const e of candidateEntities) if (r.entities.has(e)) shared++;
      if (shared >= 2) return true;
    }
    return false;
  };

  for (const topic of topics) {
    if (!topic?.canonical_title || !topic?.vertical) continue;

    const vertical = String(topic.vertical);
    const category = VERTICAL_TO_CATEGORY[vertical] ?? "news";

    const claudeEntities: string[] = Array.isArray(topic.key_entities)
      ? topic.key_entities.map((e: any) => String(e))
      : [];
    const titleEntities = extractEntities(String(topic.canonical_title));
    const candidateEntities = [
      ...new Set([...claudeEntities, ...titleEntities].map((e) => e.toLowerCase())),
    ];

    const urgency = topic.urgency ?? "daily";
    if (urgency !== "breaking" && isDuplicate(candidateEntities, vertical)) {
      skippedDupes++;
      continue;
    }

    // Track this topic so subsequent topics in the same run also dedup against it
    recentEntitySets.push({ entities: new Set<string>(candidateEntities) });

    const clamp = (v: any) => Math.min(100, Math.max(0, Math.round(Number(v) || 50)));
    const indices: number[] = Array.isArray(topic.signal_indices) ? topic.signal_indices : [];

    // Source prominence: max priority among contributing sources
    const validIdx = indices.filter((i) => i >= 0 && i < signals.length);
    const maxPriority = validIdx.length > 0
      ? Math.max(...validIdx.map((i) => sourceMap[signals[i].feed_source_id]?.priority ?? 50))
      : 50;

    const scoreDiaspora = clamp(topic.score_diaspora);
    const scoreSignificance = clamp(topic.score_significance);

    const computedTotal = Math.min(100, Math.round(
      scoreDiaspora    * 0.60 +
      scoreSignificance * 0.30
    ));

    if (scoreDiaspora < 45) continue;

    const { data: newTopic, error: topicErr } = await supabase
      .from("p2_topics")
      .insert({
        canonical_title: String(topic.canonical_title).slice(0, 200),
        vertical,
        category,
        urgency,
        score_diaspora: scoreDiaspora,
        score_significance: scoreSignificance,
        score_recency: 50,
        score_source_avail: clamp(topic.score_source_avail),
        score_total: computedTotal,
        signal_count: indices.length || 1,
        status: "pending",
        keywords: Array.isArray(topic.keywords) ? topic.keywords : [],
        image_url: topic.image?.url ?? null,
        image_attribution: topic.image?.attribution ?? null,
        image_license: topic.image?.license ?? null,
        image_search_query: topic.image?.search_query ?? null,
      })
      .select("id")
      .single();

    if (topicErr || !newTopic) continue;
    insertedTopics++;

    const signalLinks = indices
      .filter((i) => Number.isInteger(i) && i >= 0 && i < signals.length)
      .map((i) => ({ topic_id: newTopic.id, signal_id: signals[i].id }));

    if (signalLinks.length > 0) {
      await supabase
        .from("p2_topic_signals")
        .upsert(signalLinks, { onConflict: "topic_id,signal_id", ignoreDuplicates: true });
    }
  }

  // Insert discovered topics (from Google Search, no RSS signals attached)
  let insertedDiscovered = 0;
  for (const topic of discoveredTopics) {
    if (!topic?.canonical_title || !topic?.vertical) continue;
    const vertical = String(topic.vertical);
    const category = VERTICAL_TO_CATEGORY[vertical] ?? "news";
    const clamp = (v: any) => Math.min(100, Math.max(0, Math.round(Number(v) || 50)));
    const scoreDiaspora = clamp(topic.score_diaspora);
    if (scoreDiaspora < 40) continue;
    const scoreSignificance = clamp(topic.score_significance);
    const scoreTotal = Math.round(scoreDiaspora * 0.6 + scoreSignificance * 0.4);

    const { error: discErr } = await supabase
      .from("p2_topics")
      .insert({
        canonical_title: String(topic.canonical_title).slice(0, 200),
        vertical,
        category,
        urgency: topic.urgency ?? "daily",
        score_diaspora: scoreDiaspora,
        score_significance: scoreSignificance,
        score_recency: 80,
        score_source_avail: 50,
        score_total: scoreTotal,
        signal_count: 0,
        status: "pending",
        keywords: Array.isArray(topic.keywords) ? topic.keywords : [],
      });
    if (!discErr) insertedDiscovered++;
  }

  // Store carousel photos
  if (carouselPhotos.length > 0) {
    await supabase
      .from("videshi_carousel_photos")
      .upsert(
        carouselPhotos
          .filter((p: any) => p?.image?.url)
          .map((p: any) => ({
            title: p.title,
            description: p.description,
            image_url: p.image?.url,
            image_source: p.image?.source,
            image_attribution: p.image?.attribution,
            image_license: p.image?.license,
            related_topic: p.related_topic,
            fetched_at: new Date().toISOString(),
          })),
        { onConflict: "image_url", ignoreDuplicates: true }
      );
  }

  // Mark all processed signals
  const signalIds = signals.map((s: any) => s.id);
  await supabase.from("p2_signals").update({ is_processed: true }).in("id", signalIds);

  const elapsed = Date.now() - startTime;
  const summary =
    `p2-rank: ${signals.length} signals → ${insertedTopics} topics inserted, ${skippedDupes} dupes skipped in ${elapsed}ms`;

  await supabase.from("pipeline_alerts").insert({
    agent: "p2-rank",
    severity: "info",
    error_type: null,
    message: summary,
  });

  return new Response(
    JSON.stringify({ ok: true, signalsProcessed: signals.length, insertedTopics, skippedDupes, elapsed }),
    { headers: { ...corsHeaders, "Content-Type": "application/json" } },
  );
});
