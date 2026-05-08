ALTER TABLE public.p2_articles ADD COLUMN IF NOT EXISTS image_url text;
CREATE INDEX IF NOT EXISTS idx_p2_articles_image_url ON public.p2_articles(image_url) WHERE image_url IS NULL;