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
    .limit(120);

  // 1b. Fetch source metadata from videshi_sources
  const sourceIds = [...new Set((signals ?? []).map((s: any) => s.feed_source_id).filter(Boolean))];
  const { data: sourcesData } = await supabase
    .from("videshi_sources")
    .select("id, name, slug, categories, priority")
    .in("id", sourceIds);
  const sourceMap: Record<string, any> = Object.fromEntries(
    (sourcesData ?? []).map((s: any) => [s.id, s])
  );

  const calcRecency = (publishedAt: string | null): number => {
    if (!publishedAt) return 50;
    const hoursAgo = (Date.now() - new Date(publishedAt).getTime()) / 3_600_000;
    if (hoursAgo <= 2) return 100;
    if (hoursAgo <= 6) return 90;
    if (hoursAgo <= 12) return 80;
    if (hoursAgo <= 24) return 65;
    if (hoursAgo <= 36) return 45;
    return 25;
  };

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

  // 2b. Fetch recently published headlines (to avoid republishing)
  const { data: recentArticles } = await supabase
    .from("p2_articles")
    .select("headline, category, published_at")
    .eq("status", "published")
    .gte("published_at", new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString())
    .order("published_at", { ascending: false })
    .limit(20);

  const publishedHeadlines = (recentArticles ?? [])
    .map((a: any) => `- ${a.headline} [${a.category}]`)
    .join("\n");

  // 3. Gemini clustering + discovery + carousel (with Google Search grounding)
  const userPrompt = `
You are the chief editor of The Videshi, a premium news platform for the Indian diaspora globally (US, UK, Australia, UAE, Canada, Singapore).

You have access to Google Search — use it actively.

═══════════════════════════════════════
PART A: ALREADY PUBLISHED (DO NOT REPUBLISH)
═══════════════════════════════════════
${publishedHeadlines}

═══════════════════════════════════════
PART B: RSS SIGNALS (what our feeds caught)
═══════════════════════════════════════
${headlineList}

═══════════════════════════════════════
PART C: YOUR JOB
═══════════════════════════════════════

Do THREE things:

──────────────────────────────────────
TASK 1: RANK AND CLUSTER RSS SIGNALS
──────────────────────────────────────
Group the RSS signals above into unique story topics.
Skip any story already in PART A (published).

For each topic return a JSON object with ALL these fields:
- canonical_title: clear headline (max 100 chars, full names)
- vertical: politics|economy|tech|immigration|diaspora|science|culture|sports|entertainment|education
- category: news|entertainment|sports|markets-finance|technology|nri-world|lifestyle-health|travel|food
- event_type: election-result|swearing-in|policy-announcement|policy-update|match-result|match-preview|birthday|film-release|arrest-raid|court-ruling|market-move|diplomatic-meeting|natural-disaster|obituary|protest|accident|appointment|resignation|award|interview|statement|report-release|other
- event_date: YYYY-MM-DD when event occurred
- score_diaspora: 0-100
    90-100: H-1B/visa/immigration, Indian-Americans in news, India-US policy directly affecting diaspora
    75-89: National India elections, India-Pakistan/China, Bollywood A-list, cricket World Cup/IPL finals
    65-74: Tamil Nadu, Kerala, Punjab, Andhra/Telangana, Karnataka, Gujarat, Maharashtra, West Bengal (always 65+ for these diaspora-heavy states)
    50-64: National India politics, economy, IPL regular season
    30-49: India-domestic, minimal diaspora relevance
    5-25:  Non-Indian celebrities, unrelated global news
    NEVER score Indian state board exams above 35
    NEVER score non-Indian celebrities above 20
- score_significance: 0-100
- urgency: breaking|daily|evergreen
- keywords: 3-5 search terms for govt press releases
- signal_indices: array of [N] indices from PART B
- key_entities: array of typed entity objects:
  {
    name: "full canonical name — never abbreviate",
    type: "politician|actor|athlete|businessman|organization|place|event|policy",
    entity_id: "disambiguated-slug e.g.
      vijay-politician-tamil-nadu (NOT vijay-deverakonda)
      vijay-deverakonda-actor-telugu (Telugu film actor)
      rahul-gandhi-politician-congress
      inc-organization-india (Indian National Congress)
      us-congress-organization-usa (US Congress)
      supreme-court-india vs supreme-court-usa
      delhi-capitals-ipl-team vs delhi-place-capital"
  }
- free_sources: 2-3 copyright-free URLs for synthesis:
    Priority: PIB (pib.gov.in) → Wikipedia → official govt sites → Wikimedia Commons
    NEVER link to NDTV, TOI, Hindu, IE, BBC (copyrighted)
- synthesis_angle: one sentence on diaspora relevance angle
- image: single best image object:
  {
    url: direct accessible image URL,
    source: "Wikimedia Commons|PIB|Unsplash|Pexels|Official Govt|AP Archive",
    attribution: exact credit text to display on site,
    alt_text: description of image,
    license: "public-domain|cc-by|cc-by-sa|free-to-use"
  }
  Sources by story type:
  - Politicians/officials → Wikimedia Commons or PIB
  - Cricket/IPL → Wikimedia Commons team pages
  - Places → Wikimedia Commons or Unsplash
  - Bollywood → Wikimedia Commons actor pages
  - Generic/concept → Unsplash or Pexels

──────────────────────────────────────
TASK 2: DISCOVER STORIES WE MISSED
──────────────────────────────────────
Search Google News right now for stories important to Indian diaspora that are NOT in our RSS signals and NOT already published (PART A).
Find 3-5 additional high-value stories.
Focus on:
- Breaking India-US news (visa, immigration, policy)
- Major India events in last 6 hours
- Stories trending in Indian diaspora communities
- Events our RSS feeds likely missed

For each discovered story return same JSON format as Task 1 but add:
- source: "google_discovery" (to distinguish from RSS)
- signal_indices: [] (empty — not from our RSS)
- discovered_url: the URL where you found this story

──────────────────────────────────────
TASK 3: EVENT PHOTOS FOR CAROUSEL
──────────────────────────────────────
Find 5 high-quality news event photos from the last 48 hours relevant to Indian diaspora. These are for our homepage photo carousel.
Search Google for recent event images. Return:
[
  {
    "carousel": true,
    "title": "short caption for carousel",
    "description": "2-3 sentence context",
    "image": {
      "url": direct image URL,
      "source": "AP Archive|Reuters|PIB|Wikimedia|Getty",
      "attribution": "credit text",
      "license": "public-domain|press-use|cc-by"
    },
    "related_article_topic": "topic this relates to if any"
  }
]
Prioritize: official govt events, sports moments, cultural events, landmark occasions.

═══════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════
Return a single valid JSON object:
{
  "ranked_topics": [...],     ← Task 1: RSS ranked clusters
  "discovered_topics": [...], ← Task 2: Google-found stories
  "carousel_photos": [...]    ← Task 3: Event photos
}
No markdown. No explanation. Raw JSON only.
Score topics with score_diaspora < 40 are excluded.
Maximum 20 ranked_topics + 5 discovered_topics.
`;

  let topics: any[] = [];
  let discoveredTopics: any[] = [];
  let carouselPhotos: any[] = [];
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_KEY}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: userPrompt }] }],
          tools: [{ googleSearch: {} }],
          generationConfig: {
            temperature: 0.1,
            thinkingConfig: { thinkingBudget: 0 }
          }
        })
      }
    );
    const geminiData = await response.json();
    const raw = geminiData?.candidates?.[0]?.content?.parts?.[0]?.text?.trim() ?? "";
    const cleaned = raw.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "").trim();
    const data = JSON.parse(cleaned);
    topics = Array.isArray(data?.ranked_topics) ? data.ranked_topics : [];
    discoveredTopics = Array.isArray(data?.discovered_topics) ? data.discovered_topics : [];
    carouselPhotos = Array.isArray(data?.carousel_photos) ? data.carousel_photos : [];
  } catch (err: any) {
    await supabase.from("pipeline_alerts").insert({
      agent: "p2-rank",
      severity: "error",
      error_type: "claude_error",
      message: `Claude ranking failed: ${err?.message ?? String(err)}`,
    });
    return new Response(JSON.stringify({ ok: false, error: err?.message ?? String(err) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
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

  // Duplicate if 2+ shared entities with any recent topic
  // Politics/news verticals need a higher threshold because celebrity names
  // (e.g. "Vijay") collide across entertainment and politics contexts.
  const HIGH_THRESHOLD_VERTICALS = new Set(["politics", "news"]);
  const isDuplicate = (candidateEntities: string[], vertical: string): boolean => {
    if (candidateEntities.length === 0) return false;
    const threshold = HIGH_THRESHOLD_VERTICALS.has(vertical) ? 3 : 2;
    for (const r of recentEntitySets) {
      let shared = 0;
      for (const e of candidateEntities) if (r.entities.has(e)) shared++;
      if (shared >= threshold) return true;
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

    // Recency: average of actual published_at scores
    const avgRecency = validIdx.length > 0
      ? validIdx.reduce((sum, i) => sum + calcRecency(signals[i].published_at), 0) / validIdx.length
      : 50;

    // Tier 1 top-story feeds (highest prominence)
    const TIER1_SLUGS = new Set([
      'ndtv-top-stories', 'ndtv-india-news', 'times-of-india',
      'toi-most-recent', 'the-hindu', 'bbc-india',
      'hindustan-times', 'indian-express',
    ]);

    // Diaspora-heavy state keywords
    const DIASPORA_STATES = [
      'tamil nadu', 'kerala', 'punjab', 'andhra', 'telangana',
      'karnataka', 'gujarat', 'maharashtra', 'west bengal', 'bengal',
      'vijay', 'tvk', 'dmk', 'aiadmk', 'bjp bengal',
    ];

    const topicSignals = indices
      .filter((i) => i >= 0 && i < signals.length)
      .map((i) => signals[i]);

    // Boost 1: Tier 1 top-story source
    const hasTier1Source = topicSignals.some((s: any) => {
      const src = sourceMap[s.feed_source_id];
      return src && TIER1_SLUGS.has(src.slug ?? '');
    });
    const tier1Boost = hasTier1Source ? 10 : 0;

    // Boost 2: Signal count (uncapped-ish)
    const signalCountBoost = Math.min((indices.length - 1) * 5, 20);

    // Boost 3: Diaspora state
    const titleLower = String(topic.canonical_title).toLowerCase();
    const isDiasporaState = DIASPORA_STATES.some((s) => titleLower.includes(s));
    const diasporaStateBoost = isDiasporaState ? 10 : 0;

    // Boost 4: India-US bilateral
    const isIndiUS = titleLower.includes('india-us') ||
      titleLower.includes('india us') ||
      titleLower.includes('white house') ||
      titleLower.includes('washington') ||
      titleLower.includes('pentagon') ||
      titleLower.includes('trump') ||
      titleLower.includes('biden') ||
      titleLower.includes('us-india');
    const indiUSBoost = isIndiUS ? 8 : 0;

    // Boost 5: Penalty for India-domestic only
    const scoreDiaspora = clamp(topic.score_diaspora);
    const isDomesticOnly = scoreDiaspora < 50;
    const domesticPenalty = isDomesticOnly ? -15 : 0;

    const scoreSignificance = clamp(topic.score_significance);

    // New weights — diaspora is the primary driver
    const baseScore = Math.round(
      scoreDiaspora     * 0.55 +
        scoreSignificance * 0.35 +
        avgRecency        * 0.10,
    );

    // Apply boosts
    const computedTotal = Math.min(100, Math.max(0,
      baseScore
        + tier1Boost
        + signalCountBoost
        + diasporaStateBoost
        + indiUSBoost
        + domesticPenalty,
    ));

    if (computedTotal < 45 || scoreDiaspora < 40) continue;

    const { data: newTopic, error: topicErr } = await supabase
      .from("p2_topics")
      .insert({
        canonical_title: String(topic.canonical_title).slice(0, 200),
        vertical,
        category,
        urgency,
        score_diaspora: scoreDiaspora,
        score_significance: scoreSignificance,
        score_recency: Math.round(avgRecency),
        score_source_avail: clamp(topic.score_source_avail),
        score_total: computedTotal,
        signal_count: indices.length || 1,
        status: "pending",
        keywords: Array.isArray(topic.keywords) ? topic.keywords : [],
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
