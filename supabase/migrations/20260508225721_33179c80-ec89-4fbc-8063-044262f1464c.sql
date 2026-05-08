UPDATE public.p2_articles SET image_url = NULL
WHERE vertical IN ('politics','economy','immigration','tech')
AND image_url IS NOT NULL;