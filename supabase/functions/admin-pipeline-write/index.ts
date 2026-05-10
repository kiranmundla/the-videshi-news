// Admin write proxy for pipeline tables. Auth via shared VIDESHI_API_KEY header.
// Used by the admin/pipeline UI in the frontend so we can keep table writes
// restricted to the service role.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-admin-key",
};

const ALLOWED_TABLES = new Set([
  "p2_feed_sources",
  "p2_topics",
  "p2_articles",
  "videshi_sources",
]);

const ALLOWED_OPS = new Set(["insert", "update", "delete"]);

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

  const adminKey = Deno.env.get("VIDESHI_API_KEY");
  if (!adminKey) return json({ error: "admin key not configured" }, 500);
  if (req.headers.get("x-admin-key") !== adminKey) {
    return json({ error: "unauthorized" }, 401);
  }

  let body: {
    table?: string;
    op?: string;
    payload?: Record<string, unknown>;
    id?: string;
  } = {};
  try { body = await req.json(); } catch { /* empty */ }

  const { table, op, payload, id } = body;
  if (!table || !op || !ALLOWED_TABLES.has(table) || !ALLOWED_OPS.has(op)) {
    return json({ error: "invalid table or op" }, 400);
  }

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  );

  try {
    if (op === "insert") {
      if (!payload || typeof payload !== "object") return json({ error: "payload required" }, 400);
      const { data, error } = await supabase.from(table).insert(payload).select().single();
      if (error) return json({ error: error.message }, 500);
      return json({ ok: true, data });
    }
    if (op === "update") {
      if (!id) return json({ error: "id required" }, 400);
      if (!payload || typeof payload !== "object") return json({ error: "payload required" }, 400);
      const { data, error } = await supabase.from(table).update(payload).eq("id", id).select().single();
      if (error) return json({ error: error.message }, 500);
      return json({ ok: true, data });
    }
    if (op === "delete") {
      if (!id) return json({ error: "id required" }, 400);
      const { error } = await supabase.from(table).delete().eq("id", id);
      if (error) return json({ error: error.message }, 500);
      return json({ ok: true });
    }
  } catch (e) {
    return json({ error: e instanceof Error ? e.message : String(e) }, 500);
  }
  return json({ error: "unhandled" }, 500);
});
