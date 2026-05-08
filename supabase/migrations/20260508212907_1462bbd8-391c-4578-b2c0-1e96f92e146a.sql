
CREATE TABLE public.feed_sources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  url text NOT NULL UNIQUE,
  type text NOT NULL,
  layer text NOT NULL,
  verticals text[] NOT NULL DEFAULT '{}',
  tier text NOT NULL DEFAULT 'B',
  is_active boolean NOT NULL DEFAULT true,
  fetch_interval_min int NOT NULL DEFAULT 60,
  last_fetched_at timestamptz,
  avg_items_per_day real,
  created_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.feed_sources ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role full access feed_sources" ON public.feed_sources
  FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Public read feed_sources" ON public.feed_sources
  FOR SELECT USING (true);
CREATE POLICY "Public write feed_sources" ON public.feed_sources
  FOR ALL USING (true) WITH CHECK (true);

CREATE TABLE public.raw_signals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  feed_source_id uuid REFERENCES public.feed_sources(id) ON DELETE SET NULL,
  title text NOT NULL,
  original_url text NOT NULL,
  url_hash text NOT NULL UNIQUE,
  published_at timestamptz,
  fetched_at timestamptz NOT NULL DEFAULT now(),
  is_processed boolean NOT NULL DEFAULT false,
  topic_id uuid
);
ALTER TABLE public.raw_signals ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read raw_signals" ON public.raw_signals FOR SELECT USING (true);
CREATE POLICY "Public write raw_signals" ON public.raw_signals FOR ALL USING (true) WITH CHECK (true);

CREATE TABLE public.topics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  canonical_title text NOT NULL,
  vertical text NOT NULL,
  urgency text NOT NULL DEFAULT 'daily',
  score_diaspora smallint,
  score_significance smallint,
  score_recency smallint,
  score_source_avail smallint,
  score_total smallint,
  signal_count smallint NOT NULL DEFAULT 1,
  status text NOT NULL DEFAULT 'pending',
  keywords text[] NOT NULL DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.topics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read topics" ON public.topics FOR SELECT USING (true);
CREATE POLICY "Public write topics" ON public.topics FOR ALL USING (true) WITH CHECK (true);

CREATE TABLE public.source_hunts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id uuid REFERENCES public.topics(id) ON DELETE CASCADE,
  feed_source_id uuid REFERENCES public.feed_sources(id) ON DELETE SET NULL,
  url text NOT NULL,
  title text NOT NULL,
  content text,
  published_at timestamptz,
  relevance_score real,
  is_used boolean NOT NULL DEFAULT false,
  fetched_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.source_hunts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read source_hunts" ON public.source_hunts FOR SELECT USING (true);
CREATE POLICY "Public write source_hunts" ON public.source_hunts FOR ALL USING (true) WITH CHECK (true);

CREATE TABLE public.articles_pipeline (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id uuid UNIQUE REFERENCES public.topics(id) ON DELETE CASCADE,
  headline text NOT NULL,
  subheadline text,
  body text NOT NULL,
  diaspora_angle text,
  vertical text NOT NULL,
  tags text[] NOT NULL DEFAULT '{}',
  urgency text,
  sources jsonb NOT NULL DEFAULT '[]'::jsonb,
  slug text UNIQUE,
  word_count smallint,
  status text NOT NULL DEFAULT 'draft',
  is_featured boolean NOT NULL DEFAULT false,
  reviewed_at timestamptz,
  published_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.articles_pipeline ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read articles_pipeline" ON public.articles_pipeline FOR SELECT USING (true);
CREATE POLICY "Public write articles_pipeline" ON public.articles_pipeline FOR ALL USING (true) WITH CHECK (true);

CREATE TABLE public.pipeline_run_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  stage text NOT NULL,
  items_processed int NOT NULL DEFAULT 0,
  status text NOT NULL DEFAULT 'success',
  notes text,
  created_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.pipeline_run_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read pipeline_run_log" ON public.pipeline_run_log FOR SELECT USING (true);
CREATE POLICY "Public write pipeline_run_log" ON public.pipeline_run_log FOR ALL USING (true) WITH CHECK (true);

CREATE INDEX idx_raw_signals_processed ON public.raw_signals(is_processed, fetched_at DESC);
CREATE INDEX idx_topics_score ON public.topics(score_total DESC NULLS LAST, created_at DESC);
CREATE INDEX idx_topics_status ON public.topics(status);
CREATE INDEX idx_source_hunts_topic ON public.source_hunts(topic_id);
CREATE INDEX idx_articles_pipeline_status ON public.articles_pipeline(status, created_at DESC);
