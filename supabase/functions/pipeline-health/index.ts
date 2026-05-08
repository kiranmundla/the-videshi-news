// pipeline-health: returns a snapshot of agent health, queue depth, stuck jobs, and recent alerts.
// No auth required (verify_jwt = false in config.toml).
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

const AGENTS = ["agent-scout", "agent-writer", "agent-enricher", "agent-editor"];

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  const now = new Date();
  const tenMinAgo = new Date(now.getTime() - 10 * 60 * 1000).toISOString();
  const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000).toISOString();
  const stuckCutoff = new Date(now.getTime() - 30 * 60 * 1000).toISOString();

  // Queue depth by status
  const { data: byStatus } = await supabase
    .from("story_queue")
    .select("status");
  const queueDepth: Record<string, number> = {};
  for (const r of byStatus ?? []) {
    queueDepth[r.status] = (queueDepth[r.status] ?? 0) + 1;
  }

  // Stuck jobs: locked but lock expired, or updated_at older than 30 min in non-terminal status
  const { data: stuckLocks } = await supabase
    .from("story_queue")
    .select("id, status, locked_by, locked_until, updated_at")
    .not("locked_until", "is", null)
    .lt("locked_until", now.toISOString())
    .limit(50);

  const { data: stuckProgress } = await supabase
    .from("story_queue")
    .select("id, status, updated_at")
    .in("status", ["writing", "enriching", "editing"])
    .lt("updated_at", stuckCutoff)
    .limit(50);

  // Per-agent alert counts
  const agentHealth: Record<string, any> = {};
  for (const agent of AGENTS) {
    const { count: critical } = await supabase
      .from("pipeline_alerts")
      .select("id", { count: "exact", head: true })
      .eq("agent", agent)
      .in("severity", ["critical", "fatal"])
      .gte("created_at", oneHourAgo);
    const { count: overloaded } = await supabase
      .from("pipeline_alerts")
      .select("id", { count: "exact", head: true })
      .eq("agent", agent)
      .eq("error_type", "overloaded")
      .gte("created_at", tenMinAgo);
    const circuitTripped = (overloaded ?? 0) >= 5;
    agentHealth[agent] = {
      critical_alerts_last_hour: critical ?? 0,
      overloaded_last_10min: overloaded ?? 0,
      circuit_breaker_tripped: circuitTripped,
      status: circuitTripped ? "degraded" : (critical ?? 0) > 0 ? "warning" : "healthy",
    };
  }

  // Recent alerts (last hour, top 20)
  const { data: recentAlerts } = await supabase
    .from("pipeline_alerts")
    .select("id, severity, agent, error_type, message, job_id, resolved, created_at")
    .gte("created_at", oneHourAgo)
    .order("created_at", { ascending: false })
    .limit(20);

  // DLQ count
  const { count: dlqCount } = await supabase
    .from("dead_letter_queue")
    .select("id", { count: "exact", head: true });
  const { count: dlqLastDay } = await supabase
    .from("dead_letter_queue")
    .select("id", { count: "exact", head: true })
    .gte("created_at", new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString());

  // Last successful pipeline run per type
  const { data: recentRuns } = await supabase
    .from("pipeline_runs")
    .select("run_type, status, started_at, finished_at, error_message")
    .order("started_at", { ascending: false })
    .limit(20);

  const overallStatus = Object.values(agentHealth).some((a: any) => a.status === "degraded")
    ? "degraded"
    : Object.values(agentHealth).some((a: any) => a.status === "warning")
    ? "warning"
    : "healthy";

  const body = {
    status: overallStatus,
    timestamp: now.toISOString(),
    agents: agentHealth,
    queue: {
      depth_by_status: queueDepth,
      stuck_locks: stuckLocks ?? [],
      stuck_in_progress: stuckProgress ?? [],
    },
    dead_letter_queue: {
      total: dlqCount ?? 0,
      last_24h: dlqLastDay ?? 0,
    },
    recent_alerts: recentAlerts ?? [],
    recent_runs: recentRuns ?? [],
  };

  return new Response(JSON.stringify(body, null, 2), {
    status: 200,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
});
