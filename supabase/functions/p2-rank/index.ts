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
    .select("headline, category")
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

═══════════════════════════════════════
PART A: ALREADY PUBLISHED — DO NOT REPUBLISH
═══════════════════════════════════════
${publishedHeadlines}

═══════════════════════════════════════
PART B: RSS SIGNALS TO RANK
═══════════════════════════════════════
${headlineList}

═══════════════════════════════════════
YOUR JOB: TWO TASKS
═══════════════════════════════════════

──────────────────────────────────────
TASK 1: RANK AND CLUSTER RSS SIGNALS
──────────────────────────────────────
Group signals into unique story topics.
Skip stories already in PART A.

For each topic return:
- canonical_title: clear headline, full names always
- vertical: politics|economy|tech|immigration|diaspora|science|culture|sports|entertainment|education
- category: news|entertainment|sports|markets-finance|technology|nri-world|lifestyle-health|travel|food
- event_type: election-result|swearing-in|policy-announcement|policy-update|match-result|match-preview|birthday|film-release|arrest-raid|court-ruling|market-move|diplomatic-meeting|natural-disaster|obituary|protest|accident|appointment|resignation|award|statement|report-release|other
- event_date: YYYY-MM-DD
- score_diaspora: 0-100
    90-100: H-1B/visa/immigration, Indian-Americans in news, India-US policy
    75-89: National elections, India-Pakistan/China, Bollywood A-list, cricket World Cup/IPL finals
    65-74: Tamil Nadu, Kerala, Punjab, Andhra/Telangana, Karnataka, Gujarat, Maharashtra, West Bengal
    50-64: National India politics, economy, IPL
    30-49: India-domestic, minimal diaspora relevance
    5-25:  Non-Indian celebrities, unrelated global news
    RULES:
    - Indian state board exams (HPBOSE, CBSE) = max 35
    - Non-Indian celebrities = max 20
    - Celebrity birthdays = max 55
    - Local India crime = max 30
- score_significance: 0-100
- urgency: breaking|daily|evergreen
- keywords: 3-5 search terms
- signal_indices: [N] indices from PART B
- key_entities: typed entity objects:
  {
    name: "full canonical name",
    type: "politician|actor|athlete|businessman|organization|place|event|policy",
    entity_id: "disambiguated-slug"
  }
  DISAMBIGUATION:
  - Vijay (TVK/Tamil Nadu/CM) = vijay-politician-tamil-nadu
  - Vijay Deverakonda (actor) = vijay-deverakonda-actor-telugu
  - Rahul Gandhi = rahul-gandhi-politician-congress
  - Congress India = inc-organization-india
  - Congress USA = us-congress-organization-usa
  - Supreme Court India = supreme-court-india
  - Supreme Court USA = supreme-court-usa
  - Delhi Capitals (IPL) = delhi-capitals-ipl-team
  - Delhi (city) = delhi-place-capital
- free_sources: 2-3 copyright-free URLs:
    PIB (pib.gov.in) → Wikipedia → official govt sites
    NEVER link to NDTV, TOI, Hindu, IE, BBC
- synthesis_angle: one sentence diaspora angle
- image: Find the best available image for this story. Return ONE image object:
  {
    url: direct accessible image URL — use this format for Wikimedia:
      https://commons.wikimedia.org/wiki/Special:FilePath/FILENAME.jpg
      This format works for download (NOT the /thumb/ hotlink format).
      Leave null for Unsplash/Pexels — provide search_query instead,
    search_query: 4-6 word specific image search query always required
      e.g. 'Kerala Congress Chief Minister assembly 2026'
      NOT generic like 'India politics news',
    source: "wikimedia-commons|pib|unsplash|pexels|pixabay",
    attribution: exact credit line e.g.
      Photo: Wikimedia Commons / CC BY-SA 4.0
      Image: Press Information Bureau, Govt of India
      Photo: Unsplash,
    alt_text: describe what ideal image shows,
    license: "cc-by-sa|cc-by|public-domain|free-to-use"
  }
  RULES:
  - Wikimedia Special:FilePath format only — never /thumb/ URLs
  - For politicians: search their Wikipedia/Commons page name
  - For cricket/IPL: Commons has extensive cricket images
  - For Bollywood actors: Commons has actor pages
  - For places: Commons or Unsplash landmark photos
  - For PIB: use pib.gov.in for Indian government stories
  - NEVER suggest Getty/AP/Reuters/news site images

──────────────────────────────────────
TASK 2: CAROUSEL PHOTOS
──────────────────────────────────────
Suggest 5 high-quality images for our homepage photo carousel — major events, cultural moments, sports from the last 48 hours relevant to diaspora.

Return as "carousel_photos" array:
{
  title: short carousel caption,
  description: 2-3 sentence context,
  image: {
    url: direct image URL,
    source: "Wikimedia Commons|PIB|Unsplash|Pexels",
    attribution: credit text,
    license: "public-domain|cc-by|cc-by-sa|free-to-use"
  },
  related_topic: topic this relates to if any
}

═══════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════
Return a single valid JSON object:
{
  "ranked_topics": [...],
  "carousel_photos": [...]
}
No markdown. Raw JSON only.
Exclude topics with score_diaspora < 40.
Maximum 20 ranked_topics.
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
    topics = Array.isArray(data) ? data : (data?.ranked_topics ?? []);
    carouselPhotos = data?.carousel_photos ?? [];
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

    const scoreDiaspora = clamp(topic.score_diaspora);
    const scoreSignificance = clamp(topic.score_significance);

    // Option B: Trust Gemini's diaspora scoring
    // Only add what Gemini can't know: recency + signal count
    const signalBoost = Math.min((indices.length - 1) * 7, 21);

    const computedTotal = Math.min(100, Math.max(0, Math.round(
      scoreDiaspora    * 0.60 +
      scoreSignificance * 0.30 +
      avgRecency        * 0.10 +
      signalBoost
      + (scoreDiaspora < 50 ? -10 : 0)
    )));

    // Hard reject: not diaspora relevant
    if (computedTotal < 45 || scoreDiaspora < 35) continue;

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
