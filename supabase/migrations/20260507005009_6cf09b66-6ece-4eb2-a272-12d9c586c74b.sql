UPDATE public.articles
SET hero_image_url = sub.url
FROM (
  SELECT a.id,
         (regexp_match(a.body, '!\[[^\]]*\]\((https?://(?!counter\.theconversation)[^)]+)\)'))[1] AS url
  FROM public.articles a
  WHERE a.category = 'india'
    AND (a.hero_image_url IS NULL OR a.hero_image_url LIKE '%counter.theconversation%')
) AS sub
WHERE public.articles.id = sub.id AND sub.url IS NOT NULL;