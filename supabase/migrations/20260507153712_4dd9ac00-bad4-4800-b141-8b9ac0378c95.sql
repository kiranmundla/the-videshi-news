CREATE TABLE public.story_queue (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  status text NOT NULL DEFAULT 'pending',
  story_brief jsonb,
  priority int,
  category text,
  diaspora_relevance text,
  article_draft jsonb,
  draft_version int NOT NULL DEFAULT 0,
  enriched_article jsonb,
  editor_decision text,
  editor_notes text,
  revision_count int NOT NULL DEFAULT 0,
  max_revisions int NOT NULL DEFAULT 2,
  raw_article_ids uuid[],
  sources_found jsonb,
  attempts int NOT NULL DEFAULT 0,
  max_attempts int NOT NULL DEFAULT 3,
  locked_by text,
  locked_until timestamptz,
  error_message text,
  published_article_id uuid REFERENCES public.articles(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_story_queue_status_priority ON public.story_queue (status, priority);
CREATE INDEX idx_story_queue_locked_until ON public.story_queue (locked_until);

ALTER TABLE public.story_queue ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access story_queue"
ON public.story_queue
FOR ALL
USING (auth.role() = 'service_role');

CREATE OR REPLACE FUNCTION public.claim_queue_job(
  p_status text,
  p_worker_id text,
  p_lock_secs int DEFAULT 300
)
RETURNS public.story_queue
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_row public.story_queue;
BEGIN
  WITH cte AS (
    SELECT id
    FROM public.story_queue
    WHERE status = p_status
      AND (locked_until IS NULL OR locked_until < now())
      AND attempts < max_attempts
    ORDER BY priority DESC NULLS LAST, created_at ASC
    LIMIT 1
    FOR UPDATE SKIP LOCKED
  )
  UPDATE public.story_queue q
  SET locked_by = p_worker_id,
      locked_until = now() + make_interval(secs => p_lock_secs),
      attempts = q.attempts + 1,
      updated_at = now()
  FROM cte
  WHERE q.id = cte.id
  RETURNING q.* INTO v_row;

  RETURN v_row;
END;
$$;