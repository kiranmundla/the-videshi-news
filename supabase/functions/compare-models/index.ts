// One-shot model comparison: runs the same Videshi synthesizer prompt through
// Claude Sonnet 4.6, Gemini 2.5 Pro, and GPT-5. Returns raw outputs + timings.
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const SYSTEM_PROMPT = `You are a senior editor at The Videshi (thevideshi.com), a premium news platform for the Indian-American diaspora.

Your job: write factual, original news articles sourced from official/public-domain sources only.

Writing style:
- 250-320 words total
- Opening: strong lede with the core fact (who, what, when)
- Middle: 2-3 paragraphs of context and significance
- End: 1 sentence on what to watch next
- Tone: confident, clear, warm — like a trusted friend who follows Indian news closely
- NO passive voice, NO bureaucratic language

The diaspora_angle must be exactly 1 sentence explaining why Indian-Americans specifically should care.

ARTICLE STRUCTURE: opening paragraph, then 2-3 sections each with a **bold:** header, then a closing "what to watch" line. No ## headers, no bullets.

Return ONLY valid JSON. No markdown fences. Use single quotes inside string values, never double quotes.`;

function buildUserPrompt(topic: any) {
  return `Write a news article for The Videshi about this topic:

TOPIC: ${topic.canonical_title}
VERTICAL: ${topic.vertical}
CATEGORY: ${topic.category}
URGENCY: ${topic.urgency}
KEYWORDS: ${(topic.keywords ?? []).join(", ")}

No pre-loaded sources — write from general knowledge of public reporting on this topic. Do not fabricate quotes or specific numbers you are unsure of.

Return this exact JSON:
{
  "headline": "60-75 char punchy headline",
  "subheadline": "100-120 char explanatory deck",
  "body": "full article body, 250-320 words",
  "diaspora_angle": "exactly 1 sentence",
  "tags": ["tag1","tag2","tag3","tag4"],
  "confidence": 0-100
}`;
}

async function callClaude(system: string, user: string) {
  const t0 = Date.now();
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": Deno.env.get("ANTHROPIC_API_KEY")!,
      "anthropic-version": "2023-06-01",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "claude-sonnet-4-6",
      max_tokens: 2000,
      system,
      messages: [{ role: "user", content: user }],
    }),
  });
  const data = await r.json();
  const text = (data.content || []).filter((b: any) => b.type === "text").map((b: any) => b.text).join("");
  return { ms: Date.now() - t0, text, raw: data, status: r.status };
}

async function callGateway(model: string, system: string, user: string) {
  const t0 = Date.now();
  const r = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${Deno.env.get("LOVABLE_API_KEY")}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      messages: [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
    }),
  });
  const data = await r.json();
  const text = data.choices?.[0]?.message?.content ?? "";
  return { ms: Date.now() - t0, text, raw: data, status: r.status };
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  const { topic } = await req.json();
  const user = buildUserPrompt(topic);

  const [claude, gemini, gpt] = await Promise.all([
    callClaude(SYSTEM_PROMPT, user).catch((e) => ({ error: String(e) })),
    callGateway("google/gemini-2.5-pro", SYSTEM_PROMPT, user).catch((e) => ({ error: String(e) })),
    callGateway("openai/gpt-5", SYSTEM_PROMPT, user).catch((e) => ({ error: String(e) })),
  ]);

  return new Response(JSON.stringify({ topic, claude, gemini, gpt }, null, 2), {
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
});
