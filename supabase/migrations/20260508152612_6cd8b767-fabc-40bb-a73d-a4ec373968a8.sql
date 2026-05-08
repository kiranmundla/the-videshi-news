REVOKE EXECUTE ON FUNCTION public.calculate_featured_score(uuid) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.calculate_featured_score(uuid) TO service_role;