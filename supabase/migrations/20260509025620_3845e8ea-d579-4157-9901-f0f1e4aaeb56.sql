-- Null out orphan references that don't exist in videshi_sources
UPDATE public.p2_signals
SET feed_source_id = NULL
WHERE feed_source_id IS NOT NULL
  AND feed_source_id NOT IN (SELECT id FROM public.videshi_sources);

ALTER TABLE public.p2_signals DROP CONSTRAINT IF EXISTS raw_signals_feed_source_id_fkey;
ALTER TABLE public.p2_signals DROP CONSTRAINT IF EXISTS p2_signals_feed_source_id_fkey;
ALTER TABLE public.p2_signals
  ADD CONSTRAINT p2_signals_feed_source_id_fkey
  FOREIGN KEY (feed_source_id)
  REFERENCES public.videshi_sources(id)
  ON DELETE SET NULL;