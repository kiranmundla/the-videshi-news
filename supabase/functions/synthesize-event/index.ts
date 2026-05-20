import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

function jsonResp(body: Record<string, unknown>, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return jsonResp({ error: "method not allowed" }, 405);

  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return jsonResp({ error: "invalid JSON" }, 400);
  }

  const title = String(body.title ?? "").trim();
  const date = String(body.date ?? "").trim();
  const end_date = body.end_date ? String(body.end_date).trim() : null;
  const time = body.time ? String(body.time).trim() : null;
  const city = String(body.city ?? "").trim();
  const state = String(body.state ?? "").trim();
  const venue_name = String(body.venue_name ?? "").trim();
  const category = String(body.category ?? "").trim();
  const description = String(body.description ?? "").trim();
  const ticket_url = body.ticket_url ? String(body.ticket_url).trim() : null;

  if (!title || !date) {
    return jsonResp({ error: "title and date are required" }, 400);
  }

  const OPENAI_API_KEY = Deno.env.get("OPENAI_API_KEY");

  /* If no API key, return original description as fallback */
  if (!OPENAI_API_KEY) {
    console.warn("OPENAI_API_KEY not configured — returning unsynthesized content");
    return jsonResp({
      ok: true,
      long_description: description || null,
      artist_info: null,
      venue_info: null,
    });
  }

  /* Format a nice date string for the prompt */
  const dateObj = new Date(date + "T00:00:00");
  const dateFormatted = dateObj.toLocaleDateString("en-US", {
    weekday: "long", year: "numeric", month: "long", day: "numeric",
  });
  const endDateFormatted = end_date
    ? new Date(end_date + "T00:00:00").toLocaleDateString("en-US", {
        weekday: "long", year: "numeric", month: "long", day: "numeric",
      })
    : null;

  const prompt = `You are an editorial assistant for The Videshi, a news platform for the Indian diaspora in the United States. Given the following event details submitted by a community member, produce polished content.

EVENT DETAILS:
- Title: ${title}
- Date: ${dateFormatted}${endDateFormatted ? ` to ${endDateFormatted}` : ""}${time ? ` at ${time}` : ""}
- Venue: ${venue_name}, ${city}, ${state}
- Category: ${category}
- Ticket/Event URL: ${ticket_url || "N/A"}
- Submitter's description: ${description || "No description provided"}

PRODUCE (as JSON):
1. "long_description": A polished 2-3 paragraph editorial event description (150-250 words). Written in third person, informative, engaging. Describe what the event is about, who it's for, and what attendees can expect. If the submitter gave little detail, write a warm, general description based on the event type, venue, and category. Do NOT invent specific performers, speakers, or activities that weren't mentioned. Use a warm, editorial tone suitable for a diaspora news site.

2. "artist_info": If this is a music, entertainment, comedy, or dance event AND the title mentions a specific performer/artist, write a brief 2-3 sentence bio. Otherwise, set to null.

3. "venue_info": If the venue is a well-known temple, cultural center, stadium, or concert hall, write ONE sentence about it. Otherwise, set to null.

Return ONLY valid JSON with these three keys. No markdown, no code fences.`;

  try {
    const res = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${OPENAI_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [{ role: "user", content: prompt }],
        temperature: 0.7,
        max_tokens: 800,
      }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      console.error("OpenAI error:", res.status, errData);
      // Graceful fallback
      return jsonResp({
        ok: true,
        long_description: description || null,
        artist_info: null,
        venue_info: null,
        fallback: true,
      });
    }

    const data = await res.json();
    const content = data.choices?.[0]?.message?.content || "";

    /* Parse the JSON response */
    let parsed: { long_description?: string; artist_info?: string | null; venue_info?: string | null };
    try {
      // Strip potential markdown fences
      const cleaned = content.replace(/^```json?\s*\n?/i, "").replace(/\n?```\s*$/i, "").trim();
      parsed = JSON.parse(cleaned);
    } catch {
      console.error("Failed to parse OpenAI response:", content);
      return jsonResp({
        ok: true,
        long_description: description || null,
        artist_info: null,
        venue_info: null,
        fallback: true,
      });
    }

    return jsonResp({
      ok: true,
      long_description: parsed.long_description || description || null,
      artist_info: parsed.artist_info || null,
      venue_info: parsed.venue_info || null,
    });
  } catch (e) {
    console.error("synthesize-event exception:", e);
    return jsonResp({
      ok: true,
      long_description: description || null,
      artist_info: null,
      venue_info: null,
      fallback: true,
    });
  }
});
