UPDATE public.articles
SET hero_image_url = NULL
WHERE hero_image_url ~* 'counter\.theconversation\.com|/count\.gif|1x1\.gif|tracking-pixel';