// p2-rank — clusters unprocessed p2_signals into p2_topics using Claude Haiku.
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
    .select("id, title, feed_source_id, published_at, p2_feed_sources(name, layer, verticals)")
    .eq("is_processed", false)
    .order("published_at", { ascending: false, nullsFirst: false })
    .limit(120);

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
    .map((s: any, i: number) =>
      `[${i}] "${s.title}" — ${s.p2_feed_sources?.name ?? "unknown"}`
    )
    .join("\n");

  // 3. Claude clustering
  const systemPrompt =
    `You are a news editor for The Videshi, a premium news platform for Indian-Americans. Your job is to analyze news headlines from Indian sources and identify unique, publishable story topics.

Return ONLY a valid JSON array. No markdown, no explanation, no code fences. Raw JSON array only.`;

  const userPrompt =
    `Analyze these ${signals.length} news headlines from Indian sources.
Group headlines covering the SAME story. For each unique topic:

1. Pick the clearest canonical_title (max 100 chars)
2. Assign vertical (one of): politics|economy|tech|immigration|diaspora|science|culture|sports|entertainment
3. Score 0-100:
   - score_diaspora: Does this directly affect Indian-Americans? (visa/immigration/US-India = 90+, major India news = 60-75, local India = 30-50)
   - score_significance: How important is this for India overall?
   - score_recency: breaking news=90, today=70, this week=50, older=30
   - score_source_avail: Likely covered by PIB/RBI/USCIS press releases? yes=85, maybe=50, no=15
4. score_total: weighted average (diaspora×0.35 + significance×0.25 + recency×0.20 + source_avail×0.20)
5. urgency: breaking|daily|evergreen
6. keywords: 3-5 search terms for finding govt press releases on this topic
7. signal_indices: array of the [N] indices from the input that belong to this topic

Only include topics with score_total >= 45. Max 20 topics.

Headlines:
${headlineList}

Return JSON array of objects with these exact keys:
canonical_title, vertical, score_diaspora, score_significance, score_recency, score_source_avail, score_total, urgency, keywords, signal_indices`;

  let topics: any[] = [];
  try {
    const response = await anthropic.messages.create({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 4000,
      messages: [{ role: "user", content: userPrompt }],
      system: systemPrompt,
    });
    const raw = (response.content[0] as any).text.trim();
    const cleaned = raw.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "").trim();
    topics = JSON.parse(cleaned);
    if (!Array.isArray(topics)) throw new Error("Claude did not return an array");
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

  const sinceIso = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  let insertedTopics = 0;
  let skippedDupes = 0;

  for (const topic of topics) {
    if (!topic?.canonical_title || !topic?.vertical) continue;

    const vertical = String(topic.vertical);
    const category = VERTICAL_TO_CATEGORY[vertical] ?? "news";
    const titleSnippet = String(topic.canonical_title).slice(0, 40).replace(/[%_]/g, " ");

    // 24h dedup by partial title match
    const { data: existing } = await supabase
      .from("p2_topics")
      .select("id")
      .ilike("canonical_title", `%${titleSnippet}%`)
      .gte("created_at", sinceIso)
      .limit(1);

    if (existing && existing.length > 0) {
      skippedDupes++;
      continue;
    }

    const clamp = (v: any) => Math.min(100, Math.max(0, Math.round(Number(v) || 50)));
    const indices: number[] = Array.isArray(topic.signal_indices) ? topic.signal_indices : [];

    const { data: newTopic, error: topicErr } = await supabase
      .from("p2_topics")
      .insert({
        canonical_title: String(topic.canonical_title).slice(0, 200),
        vertical,
        category,
        urgency: topic.urgency ?? "daily",
        score_diaspora: clamp(topic.score_diaspora),
        score_significance: clamp(topic.score_significance),
        score_recency: clamp(topic.score_recency),
        score_source_avail: clamp(topic.score_source_avail),
        score_total: clamp(topic.score_total),
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
