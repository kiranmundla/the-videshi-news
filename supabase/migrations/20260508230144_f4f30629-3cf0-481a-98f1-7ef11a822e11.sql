UPDATE public.p2_articles SET image_url = NULL
WHERE image_url IS NOT NULL;