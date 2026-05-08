// Homepage carousel — refreshed every 6 hours.
// Primary: The News API (top world headlines with images).
// Fallback: Unsplash, only when News API returns fewer than 5 usable images.

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const NEWS_API_KEY = Deno.env.get("NEWS_API_KEY") ?? "";
const UNSPLASH_ACCESS_KEY = Deno.env.get("UNSPLASH_ACCESS_KEY") ?? "";
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY") ?? "";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE_ROLE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

const TARGET = 10;
const NEWS_FALLBACK_THRESHOLD = 5;

type HeroImage = {
  url: string;
  alt: string;
  credit: string;
  caption: string;
  location: string;
  search_term: string;
};

function truncateWords(s: string, n: number) {
  const parts = (s ?? "").trim().split(/\s+/).filter(Boolean);
  return parts.slice(0, n).join(" ") + (parts.length > n ? "…" : "");
}

async function fetchTheNewsAPI(): Promise<HeroImage[]> {
  if (!NEWS_API_KEY) return [];
  const url =
    `https://api.thenewsapi.com/v1/news/top?api_token=${NEWS_API_KEY}` +
    `&language=en&limit=10&image=required` +
    `&categories=${encodeURIComponent("general,politics,business,sports,tech")}`;
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(20000) });
    if (!res.ok) {
      console.error("thenewsapi error", res.status, await res.text().catch(() => ""));
      return [];
    }
    const json = await res.json();
    const items = (json.data ?? []) as any[];
    const out: HeroImage[] = [];
    for (const it of items) {
      const u = it.image_url;
      if (!u || typeof u !== "string" || u.trim() === "") continue;
      const headline = (it.title ?? "").trim();
      out.push({
        url: u,
        alt: headline,
        credit: it.source ?? "News",
        caption: truncateWords(headline, 8),
        location: "",
        search_term: it.categories?.[0] ?? "news",
      });
    }
    return out;
  } catch (e) {
    console.error("thenewsapi exception", e);
    return [];
  }
}

async function fetchUnsplashFallback(needed: number): Promise<HeroImage[]> {
  if (!UNSPLASH_ACCESS_KEY || needed <= 0) return [];
  const queries = ["world news", "city skyline", "global politics", "stock market", "sports action", "technology"];
  const out: HeroImage[] = [];
  try {
    for (const q of queries) {
      if (out.length >= needed) break;
      const r = await fetch(
        `https://api.unsplash.com/search/photos?query=${encodeURIComponent(q)}&per_page=5&orientation=landscape&content_filter=high`,
        { headers: { Authorization: `Client-ID ${UNSPLASH_ACCESS_KEY}` }, signal: AbortSignal.timeout(15000) },
      );
      if (!r.ok) continue;
      const j = await r.json();
      for (const p of (j?.results ?? [])) {
        const url = p?.urls?.regular || p?.urls?.full;
        if (!url) continue;
        const desc = (p?.description || p?.alt_description || q).trim();
        out.push({
          url,
          alt: desc,
          credit: p?.user?.name ? `${p.user.name} / Unsplash` : "Unsplash",
          caption: truncateWords(desc, 8),
          location: "",
          search_term: q,
        });
        if (out.length >= needed) break;
      }
    }
  } catch (e) {
    console.error("unsplash fallback exception", e);
  }
  return out;
}

async function claudeVerify(img: HeroImage): Promise<boolean> {
  if (!ANTHROPIC_API_KEY) return true;
  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-3-5-haiku-20241022",
        max_tokens: 100,
        messages: [{
          role: "user",
          content: [
            { type: "image", source: { type: "url", url: img.url } },
            {
              type: "text",
              text:
                `Headline: "${img.alt}".\n` +
                `Score 0-10 for news-carousel quality.\n` +
                `REJECT (<7): celebrity award close-ups, pure logos/text, blurry, watermarked stock thumbs.\n` +
                `ACCEPT (>=7): crowds, landscapes with context, people in action, world leaders, events, sports moments.\n` +
                `Reply ONLY as JSON: {"score": <number>}`,
            },
          ],
        }],
      }),
      signal: AbortSignal.timeout(25000),
    });
    if (!res.ok) return true;
    const data = await res.json();
    const text = data?.content?.[0]?.text ?? "";
    const m = text.match(/\{[\s\S]*\}/);
    if (!m) return true;
    const score = Number(JSON.parse(m[0]).score ?? 0);
    return score >= 7;
  } catch {
    return true;
  }
}

async function buildSet(): Promise<HeroImage[]> {
  const news = await fetchTheNewsAPI();

  // Vision filter (parallel)
  const checks = await Promise.all(news.map(async (img) => ({ img, ok: await claudeVerify(img) })));
  const verified: HeroImage[] = [];
  for (const { img, ok } of checks) {
    if (ok) verified.push(img);
  }

  // Use Unsplash only if News produced fewer than threshold
  let combined = [...verified];
  if (verified.length < NEWS_FALLBACK_THRESHOLD) {
    const fb = await fetchUnsplashFallback(TARGET - verified.length);
    combined = [...combined, ...fb];
  }

  const seen = new Set<string>();
  const final: HeroImage[] = [];
  for (const i of combined) {
    if (seen.has(i.url)) continue;
    seen.add(i.url);
    final.push(i);
    if (final.length >= TARGET) break;
  }
  return final;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const url = new URL(req.url);
  const force = url.searchParams.get("force") === "1";
  const day = new Date().toISOString().slice(0, 10);
  const supabase = SUPABASE_URL && SERVICE_ROLE ? createClient(SUPABASE_URL, SERVICE_ROLE) : null;

  try {
    const images = await buildSet();

    if (supabase && images.length > 0) {
      // Replace today's set entirely on every refresh (cron runs every 6h).
      await supabase.from("carousel_images").delete().eq("date", day);
      const rows = images.map((img, i) => ({
        date: day,
        position: i,
        image_url: img.url,
        caption: img.caption,
        credit: img.credit,
        location: img.location,
        search_term: img.search_term,
      }));
      const { error } = await supabase
        .from("carousel_images")
        .insert(rows);
      if (error) console.error("carousel insert error", error);
    }

    return new Response(JSON.stringify({ images, refreshed: true, date: day, force }), {
      headers: { ...corsHeaders, "Content-Type": "application/json", "Cache-Control": "no-store" },
    });
  } catch (e) {
    console.error("carousel build exception", e);
    return new Response(JSON.stringify({ images: [], error: String(e) }), {
      status: 200,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
