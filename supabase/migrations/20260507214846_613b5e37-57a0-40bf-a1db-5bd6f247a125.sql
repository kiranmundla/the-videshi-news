UPDATE public.story_queue
SET editor_decision = NULL,
    attempts = 0,
    locked_by = NULL,
    locked_until = NULL,
    updated_at = now()
WHERE status = 'editing'
  AND attempts >= 3;