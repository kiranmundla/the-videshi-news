
ALTER TABLE public.feed_sources RENAME TO p2_feed_sources;
ALTER TABLE public.raw_signals RENAME TO p2_signals;
ALTER TABLE public.topics RENAME TO p2_topics;
ALTER TABLE public.source_hunts RENAME TO p2_source_hunts;
ALTER TABLE public.articles_pipeline RENAME TO p2_articles;

DROP TABLE IF EXISTS public.pipeline_run_log;

ALTER TABLE public.p2_topics ADD COLUMN IF NOT EXISTS category text;
ALTER TABLE public.p2_feed_sources ADD COLUMN IF NOT EXISTS notes text;

ALTER INDEX IF EXISTS idx_raw_signals_processed RENAME TO idx_p2_signals_processed;
ALTER INDEX IF EXISTS idx_topics_score RENAME TO idx_p2_topics_score;
ALTER INDEX IF EXISTS idx_topics_status RENAME TO idx_p2_topics_status;
ALTER INDEX IF EXISTS idx_source_hunts_topic RENAME TO idx_p2_source_hunts_topic;
ALTER INDEX IF EXISTS idx_articles_pipeline_status RENAME TO idx_p2_articles_status;
