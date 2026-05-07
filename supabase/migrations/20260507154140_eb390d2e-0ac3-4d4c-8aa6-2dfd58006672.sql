SELECT cron.unschedule('process-stories-every-30-min');

SELECT cron.schedule(
  'agent-scout-every-15-min',
  '*/15 * * * *',
  $$
  select net.http_post(
    url := 'https://lboecaekpynbpyijrbfz.supabase.co/functions/v1/agent-scout',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || current_setting('app.settings.service_role_key', true)
    ),
    body := jsonb_build_object('triggered_at', now())
  );
  $$
);