CREATE EXTENSION IF NOT EXISTS pg_cron;

DO $$
DECLARE jid bigint;
BEGIN
  SELECT jobid INTO jid FROM cron.job WHERE jobname = 'update-featured-scores';
  IF jid IS NOT NULL THEN
    PERFORM cron.unschedule(jid);
  END IF;
END$$;

SELECT cron.schedule(
  'update-featured-scores',
  '*/30 * * * *',
  $$UPDATE public.articles
    SET featured_score = public.calculate_featured_score(id)
    WHERE is_published = true
      AND published_at > now() - interval '48 hours'$$
);