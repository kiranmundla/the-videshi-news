// get-article: returns a single published article by slug, gated by x-videshi-key.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-videshi-key",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
};

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const VIDESHI_API_KEY = Deno.env.get("VIDESHI_API_KEY")!;

// Best-effort in-memory rate limiter: 60 req/min per IP.
// NOTE: per-instance only — resets on cold start, not shared across instances.
const RATE_LIMIT = 60;
const WINDOW_MS = 60_000;
const ipHits = new Map<string, number[]>();

function rateLimited(ip: string): boolean {
  const now = Date.now();
  const arr = (ipHits.get(ip) || []).filter((t) => now - t < WINDOW_MS);
  arr.push(now);
  ipHits.set(ip, arr);
  // occasional cleanup
  if (ipHits.size > 5000) {
    for (const [k, v] of ipHits) {
      if (!v.length || now - v[v.length - 1] > WINDOW_MS) ipHits.delete(k);
    }
  }
  return arr.length > RATE_LIMIT;
}

const json = (status: number, body: unknown, extra: Record<string, string> = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json", ...extra },
  });

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "GET") return json(405, { error: "Method not allowed" });

  // API key check (constant-time-ish)
  const provided = req.headers.get("x-videshi-key") || "";
  if (!VIDESHI_API_KEY || provided !== VIDESHI_API_KEY) {
    return json(401, { error: "Unauthorized" });
  }

  // Rate limit per IP
  const ip =
    req.headers.get("x-forwarded-for")?.split(",")[0].trim() ||
    req.headers.get("cf-connecting-ip") ||
    "unknown";
  if (rateLimited(ip)) {
    return json(429, { error: "Rate limit exceeded (60/min)" }, { "Retry-After": "60" });
  }

  const url = new URL(req.url);
  const slug = url.searchParams.get("slug")?.trim();
  if (!slug) return json(400, { error: "Missing 'slug' query parameter" });

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  const { data, error } = await supabase
    .from("articles")
    .select(
      "id, slug, title, summary, body, category, article_type, nri_angle, sources_used, image_url, tags, word_count, read_time_min, published_at, created_at, updated_at, is_published",
    )
    .eq("slug", slug)
    .eq("is_published", true)
    .maybeSingle();

  if (error) {
    console.error("get-article db error", error);
    return json(500, { error: "Database error" });
  }
  if (!data) return json(404, { error: "Article not found" });

  return json(200, { article: data });
});
