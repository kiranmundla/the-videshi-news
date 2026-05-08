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
type Credibility = "official" | "tier1" | "tier2" | "tier3" | "nri" | "entertainment";
type Parser = "rss" | "html-mea";
const RSS_SOURCES: { name: string; url: string; category?: string; region?: string; credibility: Credibility; parser?: Parser }[] = [
  { name: "Times of India",  url: "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", credibility: "tier3", category: "news" },
  { name: "NDTV",            url: "https://feeds.feedburner.com/ndtvnews-top-stories", credibility: "tier3", category: "news" },
  { name: "The Hindu",       url: "https://www.thehindu.com/news/national/feeder/default.rss", credibility: "tier3", category: "news" },
  { name: "Hindustan Times", url: "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml", credibility: "tier3", category: "news" },
  { name: "India Today",     url: "https://www.indiatoday.in/rss/1206578", credibility: "tier3", category: "news" },
  { name: "Indian Express",  url: "https://indianexpress.com/feed", credibility: "tier3", category: "news" }, // verified 2026-05: returned 403 (Akamai). Re-test later.
  { name: "Deccan Herald",   url: "https://www.deccanherald.com/feed", credibility: "tier3", category: "news" },

  // ── Tier 1 — Official sources ─────────────────────────────
  // PIB English-language feed (verified 2026-05 — old ModId=6&Regid=1 was returning Hindi).
  { name: "PIB English",        url: "https://pib.gov.in/RssMain.aspx?ModId=6&lang=1", credibility: "official", category: "news" },
  // PIB PMO (ModId=2) returns HTML, not RSS — disabled.
  // { name: "PIB PMO",          url: "https://pib.gov.in/RssMain.aspx?ModId=2&lang=1", credibility: "official" },
  // MEA's RSS endpoint is Akamai-blocked, but the public HTML listing is fetchable. Scrape it.
  { name: "MEA Press Releases", url: "https://www.mea.gov.in/press-releases.htm?51/Press_Releases", credibility: "official", parser: "html-mea" },
  { name: "USCIS",        url: "https://www.uscis.gov/news/rss-feed/59144",      credibility: "official", category: "nri-world", region: "us" },
  { name: "USCIS Alerts", url: "https://www.uscis.gov/news/rss-feed/22984",      credibility: "official", category: "nri-world", region: "us" },
  { name: "RBI",         url: "https://rbi.org.in/pressreleases_rss.xml",        credibility: "official" },
  { name: "RBI Notifications", url: "https://rbi.org.in/notifications_rss.xml",  credibility: "official" },

  // ── Tier 3 — NRI / diaspora sources ───────────────────────
  { name: "NRI Pulse",             url: "https://nripulse.com/feed",                  credibility: "nri", category: "nri-world", region: "us" },
  { name: "Indian Link Australia", url: "https://www.indianlink.com.au/feed",         credibility: "nri", category: "nri-world", region: "australia" },
  { name: "SBS Hindi",             url: "https://www.sbs.com.au/language/hindi/rss",  credibility: "nri", category: "nri-world", region: "australia" },
  { name: "BBC India",             url: "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml", credibility: "nri", category: "nri-world", region: "uk" },

  // ── Entertainment ─────────────────────────────────────────
  { name: "Bollywood Hungama", url: "https://www.bollywoodhungama.com/rss/news.xml", credibility: "entertainment", category: "entertainment" },
  { name: "Filmfare",          url: "https://www.filmfare.com/feeds/feeds.xml",      credibility: "entertainment", category: "entertainment" },
  // Bollywood Life (bollywoodlife.com/feed) returns 403 (Akamai). Disabled.

  // ── Sports ────────────────────────────────────────────────
  { name: "CricketTimes", url: "https://crickettimes.com/feed", credibility: "tier3", category: "sports" },
  { name: "InsideSport",  url: "https://insidesport.in/feed",   credibility: "tier3", category: "sports" },
  // NDTV Sports / NDTV Cricket / Business Standard / Moneycontrol all 403/404 from server-side fetchers. Disabled.

  // ── Business ──────────────────────────────────────────────
  { name: "Economic Times", url: "https://economictimes.indiatimes.com/rssfeedstopstories.cms", credibility: "tier3", category: "markets-finance" },
];

interface RawArticle {
  credibility?: string;
  title: string;
  url: string;
  description: string;
  image_url: string | null;
  source_name: string;
  source_url: string;
  published_at: string;
}

// ── Simple RSS/XML Parser ────────────────────────────────────
function parseRSS(xml: string, sourceName: string, sourceUrl: string, credibility: string): RawArticle[] {
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
      rawDescription.match(/<img\b[^>]*\bsrc=["']([^"']+)["']/i)?.[1]?.trim() ||
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
      credibility,
    });
  }

  return items;
}

// ── MEA HTML listing parser ──────────────────────────────────
// Each press release is an <li> containing an <a class="searchContent" href="press-releases.htm?dtl/...">
// followed by a <p> with a fa-calendar span and a date like "May 08, 2026".
function parseMeaHtml(
  html: string,
  sourceName: string,
  sourceUrl: string,
  credibility: string
): RawArticle[] {
  const items: RawArticle[] = [];
  const base = "https://www.mea.gov.in/";
  const liRe = /<li\b[\s\S]*?<\/li>/g;
  const linkRe = /<a\b[^>]*class="[^"]*searchContent[^"]*"[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/i;
  const dateRe = /fa-calendar[^>]*><\/span>\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})/i;

  for (const li of html.match(liRe) || []) {
    const linkMatch = li.match(linkRe);
    if (!linkMatch) continue;
    const href = linkMatch[1].trim();
    const title = linkMatch[2].replace(/<[^>]*>/g, "").replace(/\s+/g, " ").trim();
    if (!title || !href) continue;
    const url = href.startsWith("http") ? href : base + href.replace(/^\/+/, "");

    const dateMatch = li.match(dateRe);
    const publishedAt = dateMatch
      ? new Date(dateMatch[1]).toISOString()
      : new Date().toISOString();

    items.push({
      title,
      url,
      description: "",
      image_url: null,
      source_name: sourceName,
      source_url: sourceUrl,
      published_at: publishedAt,
      credibility,
    });
  }
  return items;
}

async function fetchFeed(source: typeof RSS_SOURCES[0]): Promise<RawArticle[]> {
  try {
    const res = await fetch(source.url, {
      headers: {
        // Some publishers (Akamai-fronted .gov.in / moneycontrol / siliconindia)
        // 403 / serve a JS challenge to non-browser User-Agents.
        "User-Agent":
          "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36 DiasporaNewsBot/1.0",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
      },
      redirect: "follow",
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) {
      const body = (await res.text()).slice(0, 200).replace(/\s+/g, " ");
      console.error(
        `[ingest-rss] ${source.name} HTTP ${res.status} ${res.statusText} — ${source.url} :: ${body}`
      );
      return [];
    }
    const body = await res.text();

    if (source.parser === "html-mea") {
      const items = parseMeaHtml(body, source.name, source.url, source.credibility);
      console.log(`[ingest-rss] ${source.name} → ${items.length} items (html-mea)`);
      return items;
    }

    const trimmed = body.trimStart().slice(0, 200);
    // Detect HTML / bot-challenge pages returned with 200
    if (!/^<\?xml|^<rss|^<feed/i.test(trimmed)) {
      console.error(
        `[ingest-rss] ${source.name} returned non-RSS content (${body.length} bytes) — ${source.url} :: ${trimmed.replace(/\s+/g, " ")}`
      );
      return [];
    }
    const items = parseRSS(body, source.name, source.url, source.credibility);
    console.log(`[ingest-rss] ${source.name} → ${items.length} items`);
    return items;
  } catch (err) {
    console.error(
      `[ingest-rss] ${source.name} fetch failed — ${source.url} :: ${(err as Error).message}`
    );
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
