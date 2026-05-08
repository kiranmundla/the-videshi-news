
CREATE TABLE IF NOT EXISTS public.p2_topic_signals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id uuid NOT NULL REFERENCES public.p2_topics(id) ON DELETE CASCADE,
  signal_id uuid NOT NULL REFERENCES public.p2_signals(id) ON DELETE CASCADE,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT p2_topic_signals_unique UNIQUE (topic_id, signal_id)
);

CREATE INDEX IF NOT EXISTS p2_topic_signals_topic_idx ON public.p2_topic_signals(topic_id);
CREATE INDEX IF NOT EXISTS p2_topic_signals_signal_idx ON public.p2_topic_signals(signal_id);

ALTER TABLE public.p2_topic_signals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read topic_signals" ON public.p2_topic_signals
  FOR SELECT USING (true);

CREATE POLICY "Service role full access topic_signals" ON public.p2_topic_signals
  FOR ALL USING (auth.role() = 'service_role');
