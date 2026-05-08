CREATE TABLE IF NOT EXISTS public.p2_image_source_log (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id    uuid REFERENCES public.p2_articles(id) ON DELETE CASCADE,
  image_source  text,
  source_type   text,
  candidates    smallint,
  winner_rank   smallint,
  created_at    timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.p2_image_source_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read image_source_log"
  ON public.p2_image_source_log FOR SELECT USING (true);

CREATE POLICY "Public write image_source_log"
  ON public.p2_image_source_log FOR ALL USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_p2_image_source_log_article
  ON public.p2_image_source_log(article_id);