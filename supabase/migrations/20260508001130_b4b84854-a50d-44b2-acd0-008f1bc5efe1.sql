ALTER TABLE public.articles ADD COLUMN IF NOT EXISTS image_verified boolean DEFAULT false;
ALTER TABLE public.articles ADD COLUMN IF NOT EXISTS image_score integer;
UPDATE public.articles SET image_verified = false, image_score = NULL;