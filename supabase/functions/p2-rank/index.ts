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

  // 3. Claude clustering
  const systemPrompt =
    `You are a news editor for The Videshi, a premium news platform for Indian-Americans and Indian diaspora globally (US, UK, Australia, UAE, Canada).

Analyze headlines and identify unique publishable story topics with precise entity disambiguation.

Return ONLY a valid JSON array. No markdown, no explanation, no code fences.`;

  const userPrompt =
    `Analyze these ${signals.length} news headlines from Indian sources.
Group headlines covering the SAME story. For each unique topic:

1. Pick the clearest canonical_title (max 100 chars)
2. Assign vertical (one of): politics|economy|tech|immigration|diaspora|science|culture|sports|entertainment
3. Score each topic 0-100 on these THREE dimensions only (do NOT score recency or source_avail — these are calculated in code):

score_diaspora: How relevant is this to Indians living abroad (US, UK, Australia, UAE, Canada)?
  90-100: Directly affects diaspora lives
    - H-1B, visa, immigration, work permits
    - Indian American discrimination or achievement
    - USCIS/DHS policy changes
    - India-US bilateral relations, trade deals
  75-89: Major India event diaspora follows closely
    - National elections or major political shifts
    - India-Pakistan/China conflict or diplomacy
    - Big Indian company IPO or market move (Zepto, etc)
    - Bollywood A-list news, cricket World Cup/IPL finals
  65-74: Diaspora-heavy STATE events — ALWAYS score 65+:
    - Tamil Nadu (large Tamil diaspora: US, UK, Singapore)
    - Kerala (large Malayali diaspora: Gulf, US, UK)
    - Punjab (large Sikh diaspora: UK, Canada, US)
    - Andhra/Telangana (Telugu diaspora: US tech hubs)
    - Karnataka (Kannada diaspora: Silicon Valley)
    - Gujarat (Gujarati diaspora: US, UK, East Africa)
    - Maharashtra (Marathi diaspora: US, UK)
    - West Bengal (Bengali diaspora: US, UK)
  50-64: India news diaspora is aware of but not directly affected
    - General national politics, Supreme Court rulings
    - India economy indicators, budget
    - Sports (non-cricket or non-major cricket)
  30-49: India-domestic, minimal diaspora relevance
    - Local state crime, local politics
    - Hyper-local city news
    - Routine government appointments

score_significance: How important is this story overall?
  80-100: National/global scale, affects millions
  60-79: Major regional or sectoral impact
  40-59: Moderate significance
  20-39: Minor or niche story

4. score_total: leave as 50 — recalculated in code.
5. urgency: breaking|daily|evergreen
6. keywords: 3-5 search terms for finding govt press releases on this topic
7. signal_indices: array of the [N] indices from the input that belong to this topic
8. key_entities: array of 2-5 typed entity objects:
{
  name: full canonical name (NEVER abbreviate),
  type: politician|actor|athlete|businessman|organization|place|event|policy,
  entity_id: disambiguated slug e.g.:
    vijay-politician-tamil-nadu
    vijay-deverakonda-actor-telugu
    rahul-gandhi-politician-congress
    us-congress-organization-usa
    supreme-court-india
    supreme-court-usa
    delhi-capitals-ipl-team
    delhi-place-capital
}

DISAMBIGUATION RULES:
- Same first name ≠ same person
- Vijay (TVK/Tamil Nadu/CM) → vijay-politician-tamil-nadu
- Vijay Deverakonda (actor/Telugu/film) → vijay-deverakonda-actor-telugu
- Rahul Gandhi (Congress) → rahul-gandhi-politician-congress
- Congress India → inc-organization-india
- Congress USA → us-congress-organization-usa
- Always use full names in canonical_title

Only include topics with score_total >= 45. Max 20 topics.

Headlines:
${headlineList}

Return JSON array of objects with these exact keys:
canonical_title, vertical, score_diaspora, score_significance, score_recency, score_source_avail, score_total, urgency, keywords, key_entities, signal_indices`;

  let topics: any[] = [];
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_KEY}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{
            parts: [{ text: systemPrompt + "\n\n" + userPrompt }]
          }],
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
    topics = JSON.parse(cleaned);
    if (!Array.isArray(topics)) throw new Error("Gemini did not return an array");
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
