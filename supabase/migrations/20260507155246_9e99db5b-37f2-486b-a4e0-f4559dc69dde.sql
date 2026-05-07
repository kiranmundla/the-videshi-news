CREATE SCHEMA IF NOT EXISTS extensions;
DROP INDEX IF EXISTS public.articles_title_trgm_idx;
ALTER EXTENSION pg_trgm SET SCHEMA extensions;

CREATE INDEX IF NOT EXISTS articles_title_trgm_idx
ON public.articles USING gin (title extensions.gin_trgm_ops);

CREATE OR REPLACE FUNCTION public.find_similar_articles(
  p_title text,
  p_hours int DEFAULT 48,
  p_threshold real DEFAULT 0.6
)
RETURNS TABLE (id uuid, title text, slug text, similarity real)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, extensions
AS $$
  SELECT a.id, a.title, a.slug, extensions.similarity(a.title, p_title) AS similarity
  FROM public.articles a
  WHERE a.is_published = true
    AND a.published_at >= now() - make_interval(hours => p_hours)
    AND extensions.similarity(a.title, p_title) > p_threshold
  ORDER BY similarity DESC
  LIMIT 5;
$$;

REVOKE EXECUTE ON FUNCTION public.find_similar_articles(text, int, real) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.find_similar_articles(text, int, real) TO service_role;