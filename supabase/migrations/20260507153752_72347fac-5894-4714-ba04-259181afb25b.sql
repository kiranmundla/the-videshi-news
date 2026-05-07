REVOKE EXECUTE ON FUNCTION public.claim_queue_job(text, text, int) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.claim_queue_job(text, text, int) TO service_role;