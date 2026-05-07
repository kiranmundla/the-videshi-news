SELECT cron.alter_job(job_id := (SELECT jobid FROM cron.job WHERE jobname = 'agent-writer-every-2-min'), schedule := '*/3 * * * *');
SELECT cron.alter_job(job_id := (SELECT jobid FROM cron.job WHERE jobname = 'agent-enricher-every-2-min'), schedule := '*/3 * * * *');
SELECT cron.alter_job(job_id := (SELECT jobid FROM cron.job WHERE jobname = 'agent-editor-every-2-min'), schedule := '*/3 * * * *');