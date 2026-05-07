create extension if not exists pg_cron with schema extensions;
create extension if not exists pg_net with schema extensions;

select cron.schedule(
  'agent-images-every-5-min',
  '*/5 * * * *',
  $$
  select net.http_post(
    url:='https://lboecaekpynbpyijrbfz.supabase.co/functions/v1/agent-images',
    headers:='{"Content-Type": "application/json", "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxib2VjYWVrcHluYnB5aWpyYmZ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc5NDc2NzQsImV4cCI6MjA5MzUyMzY3NH0.i2_CzXJEnIT2SZ9mx0j5OHh4rqewPwiLUogSrdM4HXY"}'::jsonb,
    body:='{}'::jsonb
  );
  $$
);