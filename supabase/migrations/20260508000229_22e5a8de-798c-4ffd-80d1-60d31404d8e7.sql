UPDATE public.articles SET image_caption = NULL
WHERE image_caption ~* '^(i |i''|sorry|unable|as an ai)';