DO $$
BEGIN
  PERFORM cron.unschedule('refresh-carousel-images-6h');
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

SELECT cron.schedule(
  'refresh-carousel-images-6h',
  '0 0,6,12,18 * * *',
  $cron$
  SELECT net.http_post(
    url := 'https://lboecaekpynbpyijrbfz.supabase.co/functions/v1/unsplash-hero?force=1',
    headers := '{"Content-Type":"application/json","apikey":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxib2VjYWVrcHluYnB5aWpyYmZ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc5NDc2NzQsImV4cCI6MjA5MzUyMzY3NH0.i2_CzXJEnIT2SZ9mx0j5OHh4rqewPwiLUogSrdM4HXY"}'::jsonb,
    body := '{}'::jsonb
  );
  $cron$
);