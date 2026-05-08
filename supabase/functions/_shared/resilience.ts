// Shared resilience layer for agent edge functions:
// - Error classification (transient/recoverable/fatal)
// - Resilient Anthropic API wrapper with backoff retries
// - Circuit breaker (5+ overloaded errors per agent in 10 min)
// - Alert logging to pipeline_alerts table
// - Critical alert email via Resend
// - Dead-letter queue helper

import { createClient, type SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

export type ErrorClass = "transient" | "recoverable" | "fatal" | "unknown";

export interface ClaudeError extends Error {
  status?: number;
  errorType?: string;
  classification?: ErrorClass;
}

const TRANSIENT_STATUSES = new Set([408, 502, 503, 504, 522, 524, 529]);
const RECOVERABLE_STATUSES = new Set([429]);
const FATAL_STATUSES = new Set([401, 403]);

export function classifyError(
  status: number | undefined,
  errType?: string,
  errMsg?: string,
): ErrorClass {
  if (errType === "overloaded_error") return "transient";
  if (errType === "rate_limit_error") return "recoverable";
  if (errType === "authentication_error" || errType === "permission_error") return "fatal";
  if (status != null) {
    if (FATAL_STATUSES.has(status)) return "fatal";
    if (TRANSIENT_STATUSES.has(status)) return "transient";
    if (RECOVERABLE_STATUSES.has(status)) return "recoverable";
    if (status >= 500) return "transient";
  }
  if (errMsg) {
    const m = errMsg.toLowerCase();
    if (m.includes("timeout") || m.includes("timed out") || m.includes("network")) return "transient";
    if (m.includes("json") || m.includes("parse")) return "recoverable";
  }
  return "unknown";
}

const TRANSIENT_BACKOFF_MS = [2000, 5000, 15000, 30000];
const RECOVERABLE_DELAY_MS = 10000;
const RECOVERABLE_MAX_RETRIES = 2;

export interface ResilientCallOpts {
  apiKey: string;
  body: any;
  agent: string;
  jobId?: string;
  supabase: SupabaseClient;
}

/**
 * Check if circuit breaker for this agent is tripped:
 * 5+ overloaded/transient alerts in the last 10 minutes.
 */
export async function isCircuitTripped(
  supabase: SupabaseClient,
  agent: string,
): Promise<boolean> {
  const since = new Date(Date.now() - 10 * 60 * 1000).toISOString();
  const { count } = await supabase
    .from("pipeline_alerts")
    .select("id", { count: "exact", head: true })
    .eq("agent", agent)
    .eq("error_type", "overloaded")
    .gte("created_at", since);
  return (count ?? 0) >= 5;
}

export async function logAlert(
  supabase: SupabaseClient,
  args: {
    severity: "info" | "warning" | "critical" | "fatal";
    agent: string;
    errorType?: string;
    message: string;
    jobId?: string;
  },
): Promise<void> {
  try {
    await supabase.from("pipeline_alerts").insert({
      severity: args.severity,
      agent: args.agent,
      error_type: args.errorType ?? null,
      message: args.message.slice(0, 4000),
      job_id: args.jobId ?? null,
    });
  } catch (e) {
    console.error(`[alert] failed to log alert:`, e);
  }
  console.error(
    `[alert:${args.severity}] agent=${args.agent} type=${args.errorType ?? "n/a"} job=${args.jobId ?? "-"}: ${args.message}`,
  );
}

const ALERT_EMAIL_TO = "editor@thevideshi.com";
const ALERT_EMAIL_FROM = "Pipeline Alerts <onboarding@resend.dev>";

/**
 * Send critical alert email via Resend.
 * Silently no-ops if RESEND_API_KEY isn't configured.
 */
export async function sendAlertEmail(args: {
  severity: string;
  agent: string;
  errorType?: string;
  jobId?: string;
  message: string;
}): Promise<void> {
  const key = Deno.env.get("RESEND_API_KEY");
  if (!key) {
    console.warn("[alert-email] RESEND_API_KEY not set; skipping email");
    return;
  }
  const ts = new Date().toISOString();
  const subject = `[${args.severity.toUpperCase()}] ${args.agent}: ${args.errorType ?? "error"}`;
  const html = `
    <h2>Pipeline alert (${args.severity})</h2>
    <ul>
      <li><b>Agent:</b> ${escapeHtml(args.agent)}</li>
      <li><b>Error type:</b> ${escapeHtml(args.errorType ?? "unknown")}</li>
      <li><b>Job ID:</b> ${escapeHtml(args.jobId ?? "n/a")}</li>
      <li><b>Timestamp (UTC):</b> ${ts}</li>
    </ul>
    <h3>Message</h3>
    <pre style="white-space:pre-wrap;background:#f6f6f6;padding:12px;border-radius:6px;">${escapeHtml(args.message)}</pre>
  `;
  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${key}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: ALERT_EMAIL_FROM,
        to: [ALERT_EMAIL_TO],
        subject,
        html,
      }),
    });
    if (!res.ok) {
      console.error(`[alert-email] Resend error ${res.status}: ${await res.text()}`);
    }
  } catch (e) {
    console.error(`[alert-email] send failed:`, e);
  }
}

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]!));
}

/**
 * Move a story_queue job to dead_letter_queue and remove the original
 * (or mark it failed if delete is undesirable). We keep story_queue row
 * marked failed for traceability and ALSO insert into DLQ.
 */
export async function moveToDLQ(
  supabase: SupabaseClient,
  args: {
    jobId: string;
    agent: string;
    storyBrief: any;
    errorHistory: string[];
    failureReason: string;
  },
): Promise<void> {
  try {
    const { error } = await supabase.from("dead_letter_queue").insert({
      original_job_id: args.jobId,
      agent: args.agent,
      story_brief: args.storyBrief ?? null,
      error_history: args.errorHistory.map((s) => s.slice(0, 2000)),
      failure_reason: args.failureReason.slice(0, 4000),
      can_retry: true,
    });
    if (error) console.error(`[dlq] insert failed:`, error);
  } catch (e) {
    console.error(`[dlq] exception:`, e);
  }
}

/**
 * Resilient Anthropic API call with classification, retries, and circuit breaker.
 *
 * - TRANSIENT (529, 503, 504, overloaded_error): up to 4 retries, backoff 2s, 5s, 15s, 30s
 * - RECOVERABLE (429 rate limit, JSON/parse): up to 2 retries, 10s delay
 * - FATAL (401, 403): log critical alert + throw immediately, no retry
 *
 * Throws a ClaudeError with status/errorType/classification populated.
 */
export async function callClaudeResilient(opts: ResilientCallOpts): Promise<any> {
  const { apiKey, body, agent, jobId, supabase } = opts;

  // Circuit breaker check
  if (await isCircuitTripped(supabase, agent)) {
    const msg = `Circuit breaker tripped for ${agent} (5+ overloaded errors in 10 min) — skipping`;
    await logAlert(supabase, {
      severity: "critical",
      agent,
      errorType: "circuit_breaker",
      message: msg,
      jobId,
    });
    await sendAlertEmail({
      severity: "critical",
      agent,
      errorType: "circuit_breaker",
      jobId,
      message: msg,
    });
    const err: ClaudeError = Object.assign(new Error(msg), {
      classification: "transient" as ErrorClass,
      errorType: "circuit_breaker",
    });
    throw err;
  }

  let transientAttempts = 0;
  let recoverableAttempts = 0;
  let lastErr: ClaudeError | null = null;

  while (true) {
    let res: Response;
    let text = "";
    let data: any = null;
    try {
      res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "x-api-key": apiKey,
          "anthropic-version": "2023-06-01",
          "content-type": "application/json",
        },
        body: JSON.stringify(body),
        // Hard 50s ceiling so Supabase's 60s function timeout doesn't kill us mid-call.
        // AbortError name "TimeoutError" / message "timed out" -> classified TRANSIENT and retried.
        signal: AbortSignal.timeout(50000),
      });
      text = await res.text();
      try { data = text ? JSON.parse(text) : null; } catch { /* leave null */ }
    } catch (networkErr) {
      // Network exception — treat as transient
      const msg = networkErr instanceof Error ? networkErr.message : String(networkErr);
      const cls = classifyError(undefined, undefined, msg);
      lastErr = Object.assign(new Error(`Claude network error: ${msg}`), {
        classification: cls,
      }) as ClaudeError;
      if (cls === "transient" && transientAttempts < TRANSIENT_BACKOFF_MS.length) {
        const wait = TRANSIENT_BACKOFF_MS[transientAttempts++];
        console.log(`[claude:${agent}] network transient, retry ${transientAttempts}/${TRANSIENT_BACKOFF_MS.length} in ${wait}ms: ${msg}`);
        await new Promise((r) => setTimeout(r, wait));
        continue;
      }
      throw lastErr;
    }

    if (res.ok) return data;

    const errType = data?.error?.type as string | undefined;
    const errMsg = data?.error?.message as string | undefined;
    const cls = classifyError(res.status, errType, errMsg);
    const summary = `Claude ${res.status} ${errType ?? ""}: ${(errMsg ?? text).slice(0, 400)}`;

    lastErr = Object.assign(new Error(summary), {
      status: res.status,
      errorType: errType,
      classification: cls,
    }) as ClaudeError;

    if (cls === "fatal") {
      await logAlert(supabase, {
        severity: "fatal",
        agent,
        errorType: errType ?? `http_${res.status}`,
        message: summary,
        jobId,
      });
      await sendAlertEmail({
        severity: "fatal",
        agent,
        errorType: errType ?? `http_${res.status}`,
        jobId,
        message: summary,
      });
      throw lastErr;
    }

    if (cls === "transient") {
      // Log overloaded errors so circuit breaker can count them
      if (res.status === 529 || errType === "overloaded_error") {
        await logAlert(supabase, {
          severity: "warning",
          agent,
          errorType: "overloaded",
          message: summary,
          jobId,
        });
      }
      if (transientAttempts < TRANSIENT_BACKOFF_MS.length) {
        const wait = TRANSIENT_BACKOFF_MS[transientAttempts++];
        console.log(`[claude:${agent}] transient (${res.status} ${errType ?? ""}), retry ${transientAttempts}/${TRANSIENT_BACKOFF_MS.length} in ${wait}ms`);
        await new Promise((r) => setTimeout(r, wait));
        continue;
      }
      throw lastErr;
    }

    if (cls === "recoverable") {
      if (recoverableAttempts < RECOVERABLE_MAX_RETRIES) {
        recoverableAttempts++;
        console.log(`[claude:${agent}] recoverable (${res.status} ${errType ?? ""}), retry ${recoverableAttempts}/${RECOVERABLE_MAX_RETRIES} in ${RECOVERABLE_DELAY_MS}ms`);
        await new Promise((r) => setTimeout(r, RECOVERABLE_DELAY_MS));
        continue;
      }
      throw lastErr;
    }

    // unknown — single retry as transient then give up
    if (transientAttempts < 1) {
      transientAttempts++;
      await new Promise((r) => setTimeout(r, 2000));
      continue;
    }
    throw lastErr;
  }
}

export function makeServiceClient(): SupabaseClient {
  return createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  );
}
