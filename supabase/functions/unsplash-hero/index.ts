// Returns 5 landscape images from Unsplash collections for the homepage carousel.
// Cached for 24h via Cache-Control headers (Unsplash API is rate limited).

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const UNSPLASH_ACCESS_KEY = Deno.env.get("UNSPLASH_ACCESS_KEY") ?? "";
const COLLECTIONS = "317099,9432971";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  if (!UNSPLASH_ACCESS_KEY) {
    return new Response(JSON.stringify({ images: [] }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  try {
    // Daily-rotating seed so results refresh once per day.
    const day = new Date().toISOString().slice(0, 10);
    const url =
      `https://api.unsplash.com/photos/random?count=5&orientation=landscape` +
      `&collections=${COLLECTIONS}&seed=${encodeURIComponent(day)}`;
    const res = await fetch(url, {
      headers: { Authorization: `Client-ID ${UNSPLASH_ACCESS_KEY}` },
    });
    if (!res.ok) {
      console.error("unsplash error", res.status, await res.text());
      return new Response(JSON.stringify({ images: [] }), {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }
    const data = await res.json();
    const images = (Array.isArray(data) ? data : []).map((p: any) => ({
      url: p.urls?.regular ?? p.urls?.full,
      alt: p.alt_description ?? "",
      credit: p.user?.name ?? "",
    })).filter((i: any) => i.url);

    return new Response(JSON.stringify({ images }), {
      headers: {
        ...corsHeaders,
        "Content-Type": "application/json",
        "Cache-Control": "public, max-age=86400",
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
