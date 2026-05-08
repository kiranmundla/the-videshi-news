// Returns 5 daily-rotating world-news landscape images for the homepage carousel.
// Picks 5 random search terms each day, fetches top landscape result from Unsplash,
// optionally verifies relevance with Claude Vision, and caches per-day in
// public.carousel_images. Subsequent same-day calls return the cached set.

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const UNSPLASH_ACCESS_KEY = Deno.env.get("UNSPLASH_ACCESS_KEY") ?? "";
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY") ?? "";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE_ROLE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

const SEARCH_TERMS = [
  "world leaders summit",
  "United Nations assembly",
  "protest demonstration",
  "award ceremony winners",
  "election voting",
  "world news event",
  "climate conference",
  "sports champion trophy",
  "India parliament",
  "diaspora community",
  "humanitarian crisis",
  "technology conference",
  "peace agreement signing",
  "natural disaster response",
  "cultural festival celebration",
  "stock market trading floor",
  "space exploration launch",
  "Olympic athletes",
  "geopolitical meeting",
  "refugee crisis",
];

type HeroImage = {
  url: string;
  alt: string;
  credit: string;
  caption: string;
  location: string;
  search_term: string;
};

function pickN<T>(arr: T[], n: number, seed: string): T[] {
  // Deterministic shuffle by seed so retries within a day are stable.
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    h = (h * 1103515245 + 12345) >>> 0;
    const j = h % (i + 1);
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy.slice(0, n);
}

async function unsplashSearch(query: string) {
  const url =
    `https://api.unsplash.com/search/photos?query=${encodeURIComponent(query)}` +
    `&orientation=landscape&per_page=5&content_filter=high`;
  const res = await fetch(url, {
    headers: { Authorization: `Client-ID ${UNSPLASH_ACCESS_KEY}` },
  });
  if (!res.ok) return null;
  const json = await res.json();
  const results = (json.results ?? []) as any[];
  return results;
}

async function claudeVerify(
  imageUrl: string,
  term: string,
  hint: string,
): Promise<{ ok: boolean; caption: string; location: string }> {
  if (!ANTHROPIC_API_KEY) return { ok: true, caption: term, location: hint };
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
        max_tokens: 300,
        messages: [
          {
            role: "user",
            content: [
              { type: "image", source: { type: "url", url: imageUrl } },
              {
                type: "text",
                text:
                  `Search term: "${term}". Photographer hint (may include location): "${hint}".\n` +
                  `1) Score 0-10 for "news/event relevance" (people, events, journalism scenes — NOT pure nature, food, abstract, or stock-y).\n` +
                  `2) Write an accurate factual caption (max 14 words) describing what is actually visible. Do NOT invent names of people or events. If unsure, describe the scene generically.\n` +
                  `3) Extract the location if it is explicitly stated in the hint or clearly visible (e.g., signage). Format "City, Country" or "Country". If unknown, return "".\n` +
                  `Reply ONLY as JSON: {"score": <number>, "caption": "<string>", "location": "<string>"}`,
              },
            ],
          },
        ],
      }),
    });
    if (!res.ok) return { ok: true, caption: term, location: hint };
    const data = await res.json();
    const text = data?.content?.[0]?.text ?? "";
    const m = text.match(/\{[\s\S]*\}/);
    if (!m) return { ok: true, caption: term, location: hint };
    const parsed = JSON.parse(m[0]);
    const score = Number(parsed.score ?? 0);
    const caption = String(parsed.caption ?? term).split(/\s+/).slice(0, 14).join(" ");
    const location = String(parsed.location ?? "").trim();
    return { ok: score >= 7, caption, location };
  } catch (_e) {
    return { ok: true, caption: term, location: hint };
  }
}

async function buildDailySet(day: string): Promise<HeroImage[]> {
  const terms = pickN(SEARCH_TERMS, 5, day);
  const out: HeroImage[] = [];
  for (const term of terms) {
    const results = await unsplashSearch(term);
    if (!results || results.length === 0) continue;
    let chosen: any = null;
    let chosenCaption = term;
    let chosenLocation = "";
    for (const p of results) {
      const url = p.urls?.regular ?? p.urls?.full;
      if (!url) continue;
      const hint = [
        p.location?.name,
        p.location?.city,
        p.location?.country,
        p.alt_description,
        p.description,
      ].filter(Boolean).join(" · ");
      const v = await claudeVerify(url, term, hint);
      if (v.ok) {
        chosen = p;
        chosenCaption = v.caption;
        chosenLocation =
          v.location ||
          [p.location?.city, p.location?.country].filter(Boolean).join(", ") ||
          p.location?.name ||
          "";
        break;
      }
    }
    if (!chosen) continue;
    out.push({
      url: chosen.urls?.regular ?? chosen.urls?.full,
      alt: chosen.alt_description ?? term,
      credit: chosen.user?.name ?? "",
      caption: chosenCaption,
      location: chosenLocation,
      search_term: term,
    });
  }
  return out;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const day = new Date().toISOString().slice(0, 10);
  const supabase = SUPABASE_URL && SERVICE_ROLE ? createClient(SUPABASE_URL, SERVICE_ROLE) : null;

  // 1. Try cache
  if (supabase) {
    const { data: cached } = await supabase
      .from("carousel_images")
      .select("image_url,caption,credit,search_term,position")
      .eq("date", day)
      .order("position", { ascending: true });
    if (cached && cached.length > 0) {
      const images = cached.map((r) => ({
        url: r.image_url,
        alt: r.caption ?? "",
        credit: r.credit ?? "",
        caption: r.caption ?? "",
        search_term: r.search_term ?? "",
      }));
      return new Response(JSON.stringify({ images, cached: true, date: day }), {
        headers: { ...corsHeaders, "Content-Type": "application/json", "Cache-Control": "public, max-age=3600" },
      });
    }
  }

  if (!UNSPLASH_ACCESS_KEY) {
    return new Response(JSON.stringify({ images: [] }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  try {
    const images = await buildDailySet(day);

    // 2. Persist
    if (supabase && images.length > 0) {
      const rows = images.map((img, i) => ({
        date: day,
        position: i,
        image_url: img.url,
        caption: img.caption,
        credit: img.credit,
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
    console.error("unsplash-hero exception", e);
    return new Response(JSON.stringify({ images: [] }), {
      status: 200,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
