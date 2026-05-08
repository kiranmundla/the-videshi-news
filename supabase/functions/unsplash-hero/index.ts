// Daily homepage carousel sourced from real news photos.
// Primary: The News API (thenewsapi.com) — top world headlines with images.
// Secondary: Wikimedia Commons Picture of the Day — high-quality featured image.
// Optional: Claude Haiku Vision filter (score >= 7) for visual quality / news relevance.
// Caches the day's set in public.carousel_images.

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const NEWS_API_KEY = Deno.env.get("NEWS_API_KEY") ?? "";
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY") ?? "";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE_ROLE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

type HeroImage = {
  url: string;
  alt: string;
  credit: string;
  caption: string;
  location: string;
  search_term: string;
};

function truncateWords(s: string, n: number) {
  const parts = (s ?? "").trim().split(/\s+/);
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
      if (!u || typeof u !== "string") continue;
      out.push({
        url: u,
        alt: it.title ?? "",
        credit: it.source ?? "",
        caption: truncateWords(it.title ?? "", 10),
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

async function fetchWikimediaPOTD(): Promise<HeroImage | null> {
  try {
    const day = new Date().toISOString().slice(0, 10);
    const res = await fetch(
      `https://api.wikimedia.org/feed/v1/wikipedia/en/featured/${day.replace(/-/g, "/")}`,
      { signal: AbortSignal.timeout(15000) },
    );
    if (!res.ok) return null;
    const json = await res.json();
    const img = json?.image;
    const url = img?.image?.source ?? img?.thumbnail?.source;
    if (!url) return null;
    const caption = truncateWords(
      img?.description?.text ?? img?.title ?? "Wikimedia Picture of the Day",
      10,
    );
    return {
      url,
      alt: caption,
      credit: img?.artist?.text ? `Wikimedia · ${img.artist.text.replace(/<[^>]+>/g, "")}` : "Wikimedia Commons",
      caption,
      location: "",
      search_term: "wikimedia-potd",
    };
  } catch (e) {
    console.error("wikimedia POTD exception", e);
    return null;
  }
}

async function fetchNasaAPOD(): Promise<HeroImage | null> {
  try {
    const res = await fetch(
      "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY",
      { signal: AbortSignal.timeout(15000) },
    );
    if (!res.ok) return null;
    const j = await res.json();
    if (j.media_type !== "image" || !j.url) return null;
    return {
      url: j.hdurl ?? j.url,
      alt: j.title ?? "NASA Astronomy Picture of the Day",
      credit: j.copyright ? `NASA · ${j.copyright.trim()}` : "NASA APOD",
      caption: truncateWords(j.title ?? "NASA Picture of the Day", 10),
      location: "",
      search_term: "nasa-apod",
    };
  } catch (e) {
    console.error("nasa apod exception", e);
    return null;
  }
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
                `REJECT (score <7): celebrity award close-ups, pure logos/text, blurry, watermarked stock thumbs.\n` +
                `ACCEPT (score >=7): crowds, landscapes with context, people in action, world leaders, events, sports moments, science imagery.\n` +
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

async function buildDailySet(): Promise<HeroImage[]> {
  const news = await fetchTheNewsAPI();

  // Filter via Claude vision (parallel, capped)
  const verified: HeroImage[] = [];
  const checks = await Promise.all(news.map(async (img) => ({ img, ok: await claudeVerify(img) })));
  for (const { img, ok } of checks) {
    if (ok) verified.push(img);
    if (verified.length >= 8) break;
  }

  const [potd, apod] = await Promise.all([fetchWikimediaPOTD(), fetchNasaAPOD()]);
  const extras = [potd, apod].filter(Boolean) as HeroImage[];

  const combined = [...verified, ...extras];
  // Dedupe by url
  const seen = new Set<string>();
  const final: HeroImage[] = [];
  for (const i of combined) {
    if (seen.has(i.url)) continue;
    seen.add(i.url);
    final.push(i);
    if (final.length >= 10) break;
  }
  return final;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const url = new URL(req.url);
  const force = url.searchParams.get("force") === "1";
  const day = new Date().toISOString().slice(0, 10);
  const supabase = SUPABASE_URL && SERVICE_ROLE ? createClient(SUPABASE_URL, SERVICE_ROLE) : null;

  if (supabase && !force) {
    const { data: cached } = await supabase
      .from("carousel_images")
      .select("image_url,caption,credit,search_term,location,position")
      .eq("date", day)
      .order("position", { ascending: true });
    if (cached && cached.length > 0) {
      const images = cached.map((r: any) => ({
        url: r.image_url,
        alt: r.caption ?? "",
        credit: r.credit ?? "",
        caption: r.caption ?? "",
        location: r.location ?? "",
        search_term: r.search_term ?? "",
      }));
      return new Response(JSON.stringify({ images, cached: true, date: day }), {
        headers: { ...corsHeaders, "Content-Type": "application/json", "Cache-Control": "public, max-age=3600" },
      });
    }
  }

  try {
    const images = await buildDailySet();

    if (supabase && images.length > 0) {
      if (force) {
        await supabase.from("carousel_images").delete().eq("date", day);
      }
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
        .upsert(rows, { onConflict: "date,position" });
      if (error) console.error("carousel cache insert error", error);
    }

    return new Response(JSON.stringify({ images, cached: false, date: day }), {
      headers: {
        ...corsHeaders,
        "Content-Type": "application/json",
        "Cache-Control": "public, max-age=3600",
      },
    });
  } catch (e) {
    console.error("carousel build exception", e);
    return new Response(JSON.stringify({ images: [] }), {
      status: 200,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
