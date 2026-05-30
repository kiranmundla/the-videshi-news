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

  const raw_story = String(body.raw_story ?? "").trim();
  const author_name = String(body.author_name ?? "").trim();
  const category = String(body.category ?? "general").trim();
  const prompt_what_happened = String(body.prompt_what_happened ?? "").trim();
  const prompt_how_affected = String(body.prompt_how_affected ?? "").trim();
  const prompt_advice = String(body.prompt_advice ?? "").trim();
  const prompt_years_in_us = String(body.prompt_years_in_us ?? "").trim();
  const prompt_origin_city = String(body.prompt_origin_city ?? "").trim();
  const author_city = String(body.author_city ?? "").trim();

  if (!raw_story) {
    return jsonResp({ error: "raw_story is required" }, 400);
  }

  const OPENAI_API_KEY = Deno.env.get("OPENAI_API_KEY");

  if (!OPENAI_API_KEY) {
    console.warn("OPENAI_API_KEY not configured — returning raw content");
    return jsonResp({
      ok: true,
      headline: "My Story",
      subheadline: null,
      body: raw_story,
      suspicion_score: 0,
      fallback: true,
    });
  }

  const categoryLabel: Record<string, string> = {
    immigration: "Immigration & Visa",
    career: "Career & Work",
    family: "Family & Identity",
    culture: "Culture & Belonging",
    food: "Food & Home",
    "return-home": "Return to India",
    "raising-kids": "Raising Kids Abroad",
    "starting-over": "Starting Over",
    general: "Diaspora Life",
  };

  const promptParts = [
    prompt_what_happened && `What happened: ${prompt_what_happened}`,
    prompt_how_affected && `How it affected me: ${prompt_how_affected}`,
    prompt_advice && `Advice for others: ${prompt_advice}`,
    prompt_years_in_us && `Years in the US: ${prompt_years_in_us}`,
    prompt_origin_city && `Originally from: ${prompt_origin_city}`,
    author_city && `Currently lives in: ${author_city}`,
  ].filter(Boolean).join("\n");

  const systemPrompt = `You are a compassionate editorial writer for The Videshi, a platform for the Indian diaspora. Your job is to take a community member's raw, unpolished personal story and craft it into a compelling first-person essay — like a Business Insider "as told to" piece, but warmer and more personal.

IMPORTANT RULES:
- Write in first person from the author's perspective (use "I", "my", "we")
- Keep it warm, genuine, and human — NOT corporate or journalistic
- Preserve ALL specific details from their input — names, dates, places, visa types, companies
- Do NOT invent facts, add fictional details, or embellish beyond what was shared
- Structure: hook opening (1-2 sentences that grab attention) → context/background → the story itself → reflection/what I learned or what I'd tell others
- Length: 600-900 words in markdown format
- Use paragraph breaks, no headers within the body

FORMATTING — this is critical for the reading experience:
- Use **bold** for key emotional moments, pivotal facts, or turning points (2-4 times per essay, not more). Example: "The portal said **not selected**. For the third time."
- Use *italic* for internal thoughts, realizations, or things left unsaid. Example: "*Why would anyone live here?* my son asked."
- Write at least 2-3 short standalone sentences (under 80 chars) that could work as pull quotes — poignant, quotable lines that capture the essence. Place them as their own paragraph.
- The first paragraph should open with a vivid, specific image or moment — not a summary
- Vary paragraph length: mix short punchy paragraphs (1-2 sentences) with longer narrative ones (4-5 sentences)
- End with something that lingers — an observation, an unresolved feeling, a piece of hard-won wisdom

The tone should feel like someone sharing over chai — honest, sometimes vulnerable, always real.

Also evaluate the submission for authenticity:
- suspicion_score (0-100): 0 = clearly genuine personal story, 100 = clearly fake/spam/AI-generated
- Flags: no specific details, generic platitudes, promotional content, impossible timelines, reads like ChatGPT output

Return ONLY valid JSON with these keys:
- "headline": A compelling, specific headline (not generic — reference a real detail from the story). Max 15 words. Should feel like a personal confession, not a news headline.
- "subheadline": A one-sentence teaser that makes you want to read more. Max 25 words. Italic tone — like an editor's note.
- "body": The polished first-person essay in markdown with **bold** and *italic* formatting.
- "suspicion_score": integer 0-100`;

  const userMessage = `AUTHOR: ${author_name || "Anonymous"}
CATEGORY: ${categoryLabel[category] || category}

GUIDED PROMPT ANSWERS:
${promptParts || "(none provided)"}

RAW STORY IN THEIR OWN WORDS:
${raw_story}

Please craft this into a polished first-person essay.`;

  try {
    const res = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${OPENAI_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userMessage },
        ],
        temperature: 0.7,
        max_tokens: 2000,
        response_format: { type: "json_object" },
      }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      console.error("OpenAI error:", res.status, errData);
      return jsonResp({
        ok: true,
        headline: "My Story",
        subheadline: null,
        body: raw_story,
        suspicion_score: 0,
        fallback: true,
      });
    }

    const data = await res.json();
    const content = data.choices?.[0]?.message?.content || "";

    let parsed: { headline?: string; subheadline?: string; body?: string; suspicion_score?: number };
    try {
      const cleaned = content.replace(/^```json?\s*\n?/i, "").replace(/\n?```\s*$/i, "").trim();
      parsed = JSON.parse(cleaned);
    } catch {
      console.error("Failed to parse OpenAI response:", content);
      return jsonResp({
        ok: true,
        headline: "My Story",
        subheadline: null,
        body: raw_story,
        suspicion_score: 0,
        fallback: true,
      });
    }

    return jsonResp({
      ok: true,
      headline: parsed.headline || "My Story",
      subheadline: parsed.subheadline || null,
      body: parsed.body || raw_story,
      suspicion_score: typeof parsed.suspicion_score === "number" ? parsed.suspicion_score : 0,
    });
  } catch (e) {
    console.error("synthesize-story exception:", e);
    return jsonResp({
      ok: true,
      headline: "My Story",
      subheadline: null,
      body: raw_story,
      suspicion_score: 0,
      fallback: true,
    });
  }
});
