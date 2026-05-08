// p2-ingest — Pipeline v2 RSS ingestion heartbeat.
// Fetches active feeds from p2_feed_sources, dedups by url_hash, writes to p2_signals.
// Primary-layer feeds also seed p2_source_hunts with full content.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);

const RSS2JSON_KEY = Deno.env.get("RSS2JSON_KEY") ?? "";

// ── Parsers ───────────────────────────────────────────────
function parseRSSXML(xml: string) {
  const items: { title: string; url: string; publishedAt: string | null; content: string | null }[] = [];
  const itemRegex = /<item[\s>][\s\S]*?<\/item>/g;
  const entryRegex = /<entry[\s>][\s\S]*?<\/entry>/g;
  const blocks = xml.match(itemRegex) ?? xml.match(entryRegex) ?? [];

  for (const block of blocks) {
    const title =
      block.match(/<title[^>]*><!\[CDATA\[([\s\S]*?)\]\]><\/title>/)?.[1]?.trim() ||
      block.match(/<title[^>]*>([\s\S]*?)<\/title>/)?.[1]?.trim() || "";

    const link =
      block.match(/<link[^>]*>([^<]+)<\/link>/)?.[1]?.trim() ||
      block.match(/<link[^>]*href="([^"]+)"/)?.[1]?.trim() ||
      block.match(/<guid[^>]*>([\s\S]*?)<\/guid>/)?.[1]?.trim() || "";

    const pubDate =
      block.match(/<pubDate>([\s\S]*?)<\/pubDate>/)?.[1]?.trim() ||
      block.match(/<published>([\s\S]*?)<\/published>/)?.[1]?.trim() ||
      block.match(/<dc:date>([\s\S]*?)<\/dc:date>/)?.[1]?.trim() || null;

    const content =
      block.match(/<content:encoded><!\[CDATA\[([\s\S]*?)\]\]><\/content:encoded>/)?.[1] ||
      block.match(/<description><!\[CDATA\[([\s\S]*?)\]\]><\/description>/)?.[1] ||
      block.match(/<description>([\s\S]*?)<\/description>/)?.[1] || null;

    if (title && link) items.push({ title, url: link, publishedAt: pubDate, content });
  }
  return items;
}

function parseRSS2JSON(data: any) {
  if (data?.status !== "ok" || !Array.isArray(data.items)) return [];
  return data.items
    .map((i: any) => ({
      title: (i.title ?? "").trim(),
      url: (i.link ?? "").trim(),
      publishedAt: i.pubDate ?? null,
      content: i.content ?? i.description ?? null,
    }))
    .filter((i: any) => i.title && i.url);
}

// ── Hash ─────────────────────────────────────────────────
async function hashUrl(url: string): Promise<string> {
  const buf = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(url.toLowerCase().trim()),
  );
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")
    .slice(0, 32);
}

// ── Fetch one feed ────────────────────────────────────────
async function fetchFeed(source: any) {
  if (source.type === "scrape") return { source, items: [], skipped: true };

  const isRSS2JSON = source.url.includes("rss2json.com");
  try {
    let items: any[] = [];

    if (isRSS2JSON) {
      const url = RSS2JSON_KEY
        ? source.url + (source.url.includes("?") ? "&" : "?") + `api_key=${RSS2JSON_KEY}`
        : source.url;
      const res = await fetch(url, {
        headers: { "User-Agent": "Videshi/1.0" },
        signal: AbortSignal.timeout(20000),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      items = parseRSS2JSON(await res.json());
    } else {
      const res = await fetch(source.url, {
        headers: {
          "User-Agent": "Mozilla/5.0 (compatible; Videshi/1.0; +https://thevideshi.com)",
          "Accept": "application/rss+xml, application/xml, text/xml, */*",
        },
        signal: AbortSignal.timeout(20000),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const text = await res.text();
      items = text.trim().startsWith("{")
        ? parseRSS2JSON(JSON.parse(text))
        : parseRSSXML(text);
    }

    return { source, items, skipped: false };
  } catch (err: any) {
    return { source, items: [], error: err?.message ?? String(err), skipped: false };
  }
}

// ── Main handler ──────────────────────────────────────────
Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  const startTime = Date.now();
  const results: any[] = [];

  const { data: sourcesRaw, error: srcErr } = await supabase
    .from("videshi_sources")
    .select("*")
    .eq("is_active", true)
    .in("pipeline_stage", ["discovery", "primary"]);

  // Normalize so the rest of the function (which expects {url, layer, type})
  // keeps working without further changes.
  const sources = (sourcesRaw ?? []).map((s: any) => ({
    ...s,
    url: s.endpoint_url,
    type: s.source_type,
    layer: s.pipeline_stage,
  }));

  if (srcErr || !sourcesRaw) {
    return new Response(JSON.stringify({ error: "Failed to load feed sources", detail: srcErr?.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  // Fetch with concurrency cap of 5
  const BATCH_SIZE = 5;
  const fetched: any[] = [];
  for (let i = 0; i < sources.length; i += BATCH_SIZE) {
    const batch = sources.slice(i, i + BATCH_SIZE);
    fetched.push(...await Promise.all(batch.map(fetchFeed)));
    if (i + BATCH_SIZE < sources.length) await new Promise((r) => setTimeout(r, 500));
  }

  for (const result of fetched) {
    const { source, items, error, skipped } = result;
    if (skipped) continue;
    const fetchStart = Date.now();

    if (error) {
      await supabase.from("pipeline_alerts").insert({
        agent: "p2-ingest",
        severity: "warning",
        error_type: "fetch_failed",
        message: `Failed to fetch ${source.name}: ${error}`,
      });
      await supabase.from("videshi_source_logs").insert({
        source_id: source.id,
        agent: "p2-ingest",
        status: "error",
        error_message: error,
        duration_ms: Date.now() - fetchStart,
      });
      await supabase
        .from("videshi_sources")
        .update({
          consecutive_errors: (source.consecutive_errors ?? 0) + 1,
          last_error: error,
          last_error_at: new Date().toISOString(),
        })
        .eq("id", source.id);
      results.push({ source: source.name, status: "error", error });
      continue;
    }

    if (items.length === 0) {
      await supabase.from("videshi_source_logs").insert({
        source_id: source.id,
        agent: "p2-ingest",
        status: "empty",
        items_fetched: 0,
        items_new: 0,
        duration_ms: Date.now() - fetchStart,
      });
      results.push({ source: source.name, status: "empty" });
      continue;
    }

    // Build signal rows (cap per feed)
    const cap = source.max_items ?? 50;
    const signalRows = await Promise.all(
      items.slice(0, cap).map(async (item: any) => ({
        feed_source_id: source.id,
        title: item.title.slice(0, 500),
        original_url: item.url.slice(0, 1000),
        url_hash: await hashUrl(item.url),
        published_at: item.publishedAt ? safeDate(item.publishedAt) : null,
      })),
    );

    // Upsert with dedup on url_hash
    const { data: insertedRows, error: insertErr } = await supabase
      .from("p2_signals")
      .upsert(signalRows, { onConflict: "url_hash", ignoreDuplicates: true })
      .select("id");

    const inserted = insertErr ? 0 : (insertedRows?.length ?? 0);

    if (insertErr) {
      await supabase.from("pipeline_alerts").insert({
        agent: "p2-ingest",
        severity: "error",
        error_type: "insert_failed",
        message: `Insert signals failed for ${source.name}: ${insertErr.message}`,
      });
    }

    // Primary feeds also feed p2_source_hunts (pre-content for matching)
    if (source.layer === "primary" && !insertErr) {
      const huntRows = items
        .slice(0, 30)
        .filter((i: any) => i.content && i.content.length > 100)
        .map((item: any) => ({
          topic_id: null,
          feed_source_id: source.id,
          url: item.url.slice(0, 1000),
          title: item.title.slice(0, 500),
          content: item.content?.slice(0, 10000) ?? null,
          published_at: item.publishedAt ? safeDate(item.publishedAt) : null,
          relevance_score: null,
          is_used: false,
        }));

      if (huntRows.length > 0) {
        await supabase
          .from("p2_source_hunts")
          .upsert(huntRows, { onConflict: "url", ignoreDuplicates: true });
      }
    }

    // Update last_fetched_at + rolling avg + reset error counter
    const prevAvg = source.avg_items_per_day ?? items.length;
    const newAvg = Math.round((prevAvg * 6 + items.length * 48) / 7);
    await supabase
      .from("videshi_sources")
      .update({
        last_fetched_at: new Date().toISOString(),
        avg_items_per_day: newAvg,
        consecutive_errors: 0,
        total_fetches: (source.total_fetches ?? 0) + 1,
        total_items: (source.total_items ?? 0) + items.length,
      })
      .eq("id", source.id);

    await supabase.from("videshi_source_logs").insert({
      source_id: source.id,
      agent: "p2-ingest",
      status: insertErr ? "partial" : "ok",
      items_fetched: items.length,
      items_new: inserted,
      items_accepted: inserted,
      duration_ms: Date.now() - fetchStart,
      error_message: insertErr?.message ?? null,
    });

    results.push({
      source: source.name,
      layer: source.layer,
      fetched: items.length,
      inserted,
      status: "ok",
    });
  }

  const totalFetched = results.reduce((s, r) => s + (r.fetched ?? 0), 0);
  const totalInserted = results.reduce((s, r) => s + (r.inserted ?? 0), 0);
  const elapsed = Date.now() - startTime;

  await supabase.from("pipeline_alerts").insert({
    agent: "p2-ingest",
    severity: "info",
    error_type: null,
    message: `p2-ingest complete: ${totalInserted} new signals from ${results.length} feeds in ${elapsed}ms`,
  });

  return new Response(
    JSON.stringify({ ok: true, totalFetched, totalInserted, elapsed, results }),
    { headers: { ...corsHeaders, "Content-Type": "application/json" } },
  );
});

function safeDate(s: string): string | null {
  const d = new Date(s);
  return isNaN(d.getTime()) ? null : d.toISOString();
}
