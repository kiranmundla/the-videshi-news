ALTER TABLE public.articles
  ADD COLUMN IF NOT EXISTS featured_score numeric NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS is_pinned_featured boolean NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS pinned_until timestamptz;

CREATE INDEX IF NOT EXISTS articles_featured_idx
  ON public.articles (is_pinned_featured DESC, featured_score DESC, published_at DESC)
  WHERE is_published = true;

CREATE OR REPLACE FUNCTION public.calculate_featured_score(article_id uuid)
RETURNS numeric
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  rec record;
  score numeric := 0;
  hours_old numeric;
BEGIN
  SELECT
    a.image_score,
    a.published_at,
    a.article_type,
    sg.source_count,
    sq.diaspora_relevance,
    sg.diaspora_relevant
  INTO rec
  FROM public.articles a
  LEFT JOIN public.story_groups sg ON sg.best_article_id = a.id
  LEFT JOIN public.story_queue  sq ON sq.published_article_id = a.id
  WHERE a.id = article_id;

  IF NOT FOUND THEN
    RETURN 0;
  END IF;

  score := score + COALESCE(rec.source_count, 1) * 3;

  score := score + CASE
    WHEN rec.diaspora_relevance = 'high' THEN 5
    WHEN rec.diaspora_relevance = 'medium' THEN 3
    WHEN rec.diaspora_relevance IS NULL AND rec.diaspora_relevant = true THEN 3
    ELSE 1
  END;

  score := score + COALESCE(rec.image_score, 5);
  score := score + CASE rec.article_type WHEN 'feature' THEN 5 ELSE 0 END;

  hours_old := EXTRACT(EPOCH FROM (now() - COALESCE(rec.published_at, now()))) / 3600;
  score := score + CASE WHEN hours_old < 6 THEN 5 ELSE 0 END;
  score := score - (hours_old * 0.5);

  RETURN GREATEST(score, 0);
END;
$$;

UPDATE public.articles
SET featured_score = public.calculate_featured_score(id)
WHERE is_published = true;