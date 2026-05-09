CREATE TABLE IF NOT EXISTS public.videshi_image_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id uuid REFERENCES public.p2_articles(id) ON DELETE CASCADE,
  headline text,
  source_used text,
  candidates_count smallint,
  vision_pick smallint,
  vision_score smallint,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.videshi_image_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read videshi_image_log"
  ON public.videshi_image_log FOR SELECT
  USING (true);

CREATE POLICY "Service role full access videshi_image_log"
  ON public.videshi_image_log FOR ALL
  USING (auth.role() = 'service_role');

CREATE INDEX IF NOT EXISTS idx_videshi_image_log_created_at
  ON public.videshi_image_log (created_at DESC);