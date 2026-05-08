CREATE TABLE IF NOT EXISTS public.pipeline_alerts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  severity text NOT NULL,
  agent text NOT NULL,
  error_type text,
  message text NOT NULL,
  job_id uuid,
  resolved boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS pipeline_alerts_created_at_idx ON public.pipeline_alerts (created_at DESC);
CREATE INDEX IF NOT EXISTS pipeline_alerts_agent_idx ON public.pipeline_alerts (agent, created_at DESC);
CREATE INDEX IF NOT EXISTS pipeline_alerts_unresolved_idx ON public.pipeline_alerts (resolved, created_at DESC) WHERE resolved = false;

ALTER TABLE public.pipeline_alerts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access pipeline_alerts"
ON public.pipeline_alerts
FOR ALL
USING (auth.role() = 'service_role');

CREATE TABLE IF NOT EXISTS public.dead_letter_queue (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  original_job_id uuid,
  agent text,
  story_brief jsonb,
  error_history text[],
  failure_reason text,
  can_retry boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS dlq_created_at_idx ON public.dead_letter_queue (created_at DESC);

ALTER TABLE public.dead_letter_queue ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access dead_letter_queue"
ON public.dead_letter_queue
FOR ALL
USING (auth.role() = 'service_role');

ALTER TABLE public.story_queue ALTER COLUMN max_attempts SET DEFAULT 5;
UPDATE public.story_queue SET max_attempts = 5 WHERE max_attempts < 5;