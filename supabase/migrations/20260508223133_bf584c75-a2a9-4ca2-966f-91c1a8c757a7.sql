SELECT cron.unschedule('p2-images-cron') WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'p2-images-cron');

SELECT cron.schedule(
  'p2-images-cron',
  '*/10 * * * *',
  $$
  SELECT net.http_post(
    url := 'https://lboecaekpynbpyijrbfz.supabase.co/functions/v1/p2-images',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxib2VjYWVrcHluYnB5aWpyYmZ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc5NDc2NzQsImV4cCI6MjA5MzUyMzY3NH0.i2_CzXJEnIT2SZ9mx0j5OHh4rqewPwiLUogSrdM4HXY'
    ),
    body := '{}'::jsonb,
    timeout_milliseconds := 180000
  );
  $$
);