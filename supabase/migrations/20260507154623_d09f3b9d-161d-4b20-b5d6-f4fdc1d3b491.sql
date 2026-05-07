SELECT cron.schedule(
  'agent-enricher-every-2-min',
  '*/2 * * * *',
  $$
  select net.http_post(
    url := 'https://lboecaekpynbpyijrbfz.supabase.co/functions/v1/agent-enricher',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || current_setting('app.settings.service_role_key', true)
    ),
    body := jsonb_build_object('triggered_at', now())
  );
  $$
);