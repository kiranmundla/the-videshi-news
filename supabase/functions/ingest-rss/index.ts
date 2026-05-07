// supabase/functions/ingest-rss/index.ts
// ============================================================
// Runs every 15 minutes via Supabase cron scheduler.
// Fetches RSS from all India news sources, parses, deduplicates,
// and stores new items in raw_articles.
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

// ── RSS Sources ──────────────────────────────────────────────
const RSS_SOURCES = [
  { name: "Times of India",  url: "https://timesofindia.indiatimes.com/rssfeedstopstories.cms" },
  { name: "NDTV",            url: "https://feeds.feedburner.com/ndtvnews-top-stories" },
  { name: "The Hindu",       url: "https://www.thehindu.com/news/national/feeder/default.rss" },
  { name: "Hindustan Times", url: "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml" },
  { name: "India Today",     url: "https://www.indiatoday.in/rss/1206578" },
  // Public domain — All India Radio (full text publishable)
  { name: "Newsonair",       url: "https://www.newsonair.gov.in/feed/" },
];

interface RawArticle {
  title: string;
  url: string;
  description: string;
  image_url: string;
  source_name: string;
  source_url: string;
  published_at: string;
}

// ── Simple RSS/XML Parser ────────────────────────────────────
function parseRSS(xml: string, sourceName: string, sourceUrl: string): RawArticle[] {
  const items: RawArticle[] = [];
  const itemMatches = xml.match(/<item[\s\S]*?<\/item>/g) || [];

  for (const item of itemMatches) {
    const get = (tag: string) => {
      const match = item.match(
        new RegExp(
          `<${tag}[^>]*><!\\[CDATA\\[([\\s\\S]*?)\\]\\]><\\/${tag}>|<${tag}[^>]*>([^<]*)<\\/${tag}>`
        )
      );
      return (match?.[1] || match?.[2] || "").trim();
    };

    const title = get("title");
    const link = get("link") || item.match(/<link>([^<]*)<\/link>/)?.[1]?.trim() || "";
    if (!title || !link) continue;

    const rawDescription = get("description");
    const description = rawDescription
      .replace(/<[^>]*>/g, "")
      .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
      .replace(/&quot;/g, '"').replace(/&#39;/g, "'")
      .slice(0, 500);

    // Image extraction — try patterns in order until one returns a value
    const attr = (re: RegExp) => item.match(re)?.[1]?.trim();
    const image =
      // 1. <media:content url="..." medium="image" .../>  (or no medium attr)
      attr(/<media:content\b[^>]*\burl=["']([^"']+)["'][^>]*>/i) ||
      // 2. <media:thumbnail url="..."/>
      attr(/<media:thumbnail\b[^>]*\burl=["']([^"']+)["'][^>]*>/i) ||
      // 3. <enclosure url="..." type="image/..."/>  (either attr order)
      attr(/<enclosure\b[^>]*\burl=["']([^"']+)["'][^>]*\btype=["']image\/[^"']+["'][^>]*>/i) ||
      attr(/<enclosure\b[^>]*\btype=["']image\/[^"']+["'][^>]*\burl=["']([^"']+)["'][^>]*>/i) ||
      // 4. First <img src="..."> inside <description> (CDATA-wrapped HTML)
      attr(new RegExp(`<img\\b[^>]*\\bsrc=["']([^"']+)["']`, "i").exec(rawDescription) ? new RegExp(`<img\\b[^>]*\\bsrc=["']([^"']+)["']`, "i") : /^$/) ||
      // 5. og:image (some feeds embed it inline)
      attr(/<meta\b[^>]*\bproperty=["']og:image["'][^>]*\bcontent=["']([^"']+)["']/i) ||
      attr(/<meta\b[^>]*\bcontent=["']([^"']+)["'][^>]*\bproperty=["']og:image["']/i) ||
      null;

    const pubDateStr = get("pubDate");
    const publishedAt = pubDateStr
      ? new Date(pubDateStr).toISOString()
      : new Date().toISOString();

    items.push({
      title,
      url: link,
      description,
      image_url: image,
      source_name: sourceName,
      source_url: sourceUrl,
      published_at: publishedAt,
    });
  }

  return items;
}

async function fetchFeed(source: typeof RSS_SOURCES[0]): Promise<RawArticle[]> {
  try {
    const res = await fetch(source.url, {
      headers: { "User-Agent": "DiasporaNewsBot/1.0" },
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) return [];
    const xml = await res.text();
    return parseRSS(xml, source.name, source.url);
  } catch (err) {
    console.error(`Failed to fetch ${source.name}:`, (err as Error).message);
    return [];
  }
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  const runId = crypto.randomUUID();
  let rawFetched = 0;
  let rawNew = 0;

  await supabase.from("pipeline_runs").insert({
    id: runId,
    run_type: "ingest",
    status: "running",
  });

  try {
    const results = await Promise.all(RSS_SOURCES.map(fetchFeed));
    const allArticles = results.flat();
    rawFetched = allArticles.length;

    if (allArticles.length === 0) {
      throw new Error("No articles fetched from any source");
    }

    for (let i = 0; i < allArticles.length; i += 50) {
      const batch = allArticles.slice(i, i + 50);
      const { data, error } = await supabase
        .from("raw_articles")
        .upsert(batch, { onConflict: "url", ignoreDuplicates: true })
        .select("id");

      if (error) {
        console.error("Upsert error:", error.message);
      } else {
        rawNew += data?.length || 0;
      }
    }

    await supabase
      .from("pipeline_runs")
      .update({
        status: "done",
        raw_fetched: rawFetched,
        raw_new: rawNew,
        finished_at: new Date().toISOString(),
      })
      .eq("id", runId);

    console.log(`Ingest done — fetched: ${rawFetched}, new: ${rawNew}`);

    return new Response(
      JSON.stringify({ success: true, rawFetched, rawNew }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (err) {
    const message = (err as Error).message;
    await supabase
      .from("pipeline_runs")
      .update({
        status: "error",
        error_message: message,
        finished_at: new Date().toISOString(),
      })
      .eq("id", runId);

    return new Response(
      JSON.stringify({ success: false, error: message }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
