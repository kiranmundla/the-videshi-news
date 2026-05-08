CREATE TABLE public.carousel_images (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  date date NOT NULL,
  position integer NOT NULL,
  image_url text NOT NULL,
  caption text,
  credit text,
  search_term text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (date, position)
);

CREATE INDEX idx_carousel_images_date ON public.carousel_images(date DESC);

ALTER TABLE public.carousel_images ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read carousel"
  ON public.carousel_images
  FOR SELECT
  USING (true);

CREATE POLICY "Service role full access carousel"
  ON public.carousel_images
  FOR ALL
  USING (auth.role() = 'service_role');