ALTER TABLE public.story_queue ALTER COLUMN max_attempts SET DEFAULT 5;
UPDATE public.story_queue SET max_attempts = 5 WHERE status = 'pending' AND max_attempts < 5;