UPDATE public.articles
SET image_score = NULL, image_verified = false
WHERE is_published = true
  AND image_url IS NOT NULL
  AND image_url NOT LIKE '%supabase.co/storage%';