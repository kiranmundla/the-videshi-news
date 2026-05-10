// p2-orchestrate — Sequentially triggers the p2 pipeline functions with delays.
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const BASE = "https://lboecaekpynbpyijrbfz.supabase.co/functions/v1";
const ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxib2VjYWVrcHluYnB5aWpyYmZ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc5NDc2NzQsImV4cCI6MjA5MzUyMzY3NH0.i2_CzXJEnIT2SZ9mx0j5OHh4rqewPwiLUogSrdM4HXY";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function call(name: string) {
  const startedAt = new Date().toISOString();
  const t0 = Date.now();
  try {
    const res = await fetch(`${BASE}/${name}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${ANON}`,
        "apikey": ANON,
      },
      body: "{}",
    });
    const text = await res.text();
    let body: unknown = text;
    try { body = JSON.parse(text); } catch { /* keep text */ }
    return {
      function: name,
      status: res.status,
      ok: res.ok,
      startedAt,
      durationMs: Date.now() - t0,
      response: body,
    };
  } catch (err: any) {
    return {
      function: name,
      status: 0,
      ok: false,
      startedAt,
      durationMs: Date.now() - t0,
      error: err?.message ?? String(err),
    };
  }
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const overallStart = Date.now();
  const results: any[] = [];

  results.push(await call("p2-ingest"));
  await sleep(45_000);

  results.push(await call("p2-rank"));
  await sleep(90_000);

  results.push(await call("p2-synthesize"));
  await sleep(120_000);

  results.push(await call("p2-images"));

  return new Response(
    JSON.stringify({
      ok: results.every((r) => r.ok),
      totalDurationMs: Date.now() - overallStart,
      results,
    }, null, 2),
    { headers: { ...corsHeaders, "Content-Type": "application/json" } },
  );
});
