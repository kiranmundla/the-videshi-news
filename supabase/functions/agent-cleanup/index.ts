// agent-cleanup: resets jobs stuck in writing/enriching/editing for >15 min back to pending.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  const cutoff = new Date(Date.now() - 15 * 60 * 1000).toISOString();

  const { data: stuck, error: selErr } = await supabase
    .from("story_queue")
    .select("id, status, error_message")
    .in("status", ["writing", "enriching", "editing"])
    .lt("updated_at", cutoff);

  if (selErr) {
    return new Response(JSON.stringify({ ok: false, error: selErr.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const reset: string[] = [];
  for (const row of stuck || []) {
    const note = `${row.error_message ?? ""} | reset from stuck ${row.status}`.slice(0, 2000);
    const { error: updErr } = await supabase
      .from("story_queue")
      .update({
        status: "pending",
        locked_by: null,
        locked_until: null,
        error_message: note,
        updated_at: new Date().toISOString(),
      })
      .eq("id", row.id);
    if (!updErr) reset.push(row.id);
  }

  return new Response(JSON.stringify({ ok: true, reset_count: reset.length, ids: reset }), {
    status: 200,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
});
