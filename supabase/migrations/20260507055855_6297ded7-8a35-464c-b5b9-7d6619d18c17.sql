-- Enable required extensions
create extension if not exists pg_cron with schema extensions;
create extension if not exists pg_net  with schema extensions;

-- Remove any prior versions of these jobs (idempotent)
do $$
begin
  perform cron.unschedule('ingest-rss-every-15-min');
exception when others then null;
end $$;

do $$
begin
  perform cron.unschedule('process-stories-every-30-min');
exception when others then null;
end $$;

-- Schedule ingest-rss every 15 minutes
select cron.schedule(
  'ingest-rss-every-15-min',
  '*/15 * * * *',
  $$
  select net.http_post(
    url := 'https://lboecaekpynbpyijrbfz.supabase.co/functions/v1/ingest-rss',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || current_setting('app.settings.service_role_key', true)
    ),
    body := jsonb_build_object('triggered_at', now())
  );
  $$
);

-- Schedule process-stories every 30 minutes
select cron.schedule(
  'process-stories-every-30-min',
  '*/30 * * * *',
  $$
  select net.http_post(
    url := 'https://lboecaekpynbpyijrbfz.supabase.co/functions/v1/process-stories',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || current_setting('app.settings.service_role_key', true)
    ),
    body := jsonb_build_object('triggered_at', now())
  );
  $$
);