
-- ── Drop overly permissive public write policies ──────────
DROP POLICY IF EXISTS "Public write articles_pipeline" ON public.p2_articles;
DROP POLICY IF EXISTS "Public write topics" ON public.p2_topics;
DROP POLICY IF EXISTS "Public write raw_signals" ON public.p2_signals;
DROP POLICY IF EXISTS "Public write source_hunts" ON public.p2_source_hunts;
DROP POLICY IF EXISTS "Public write feed_sources" ON public.p2_feed_sources;
DROP POLICY IF EXISTS "Public write image_source_log" ON public.p2_image_source_log;

-- ── Service-role-only write access for pipeline tables ────
CREATE POLICY "Service role full access p2_articles"
  ON public.p2_articles FOR ALL TO public
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access p2_topics"
  ON public.p2_topics FOR ALL TO public
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access p2_signals"
  ON public.p2_signals FOR ALL TO public
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access p2_source_hunts"
  ON public.p2_source_hunts FOR ALL TO public
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access p2_image_source_log"
  ON public.p2_image_source_log FOR ALL TO public
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

-- ── Tables with RLS but no policies — add service role access ──
CREATE POLICY "Service role full access gemini_test_results"
  ON public.gemini_test_results FOR ALL TO public
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access p2_image_sources"
  ON public.p2_image_sources FOR ALL TO public
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access videshi_carousel_photos"
  ON public.videshi_carousel_photos FOR ALL TO public
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Public read videshi_carousel_photos"
  ON public.videshi_carousel_photos FOR SELECT TO public USING (true);

CREATE POLICY "Service role full access videshi_entities"
  ON public.videshi_entities FOR ALL TO public
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access videshi_event_fingerprints"
  ON public.videshi_event_fingerprints FOR ALL TO public
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access videshi_source_logs"
  ON public.videshi_source_logs FOR ALL TO public
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Public read videshi_source_logs"
  ON public.videshi_source_logs FOR SELECT TO public USING (true);

CREATE POLICY "Service role full access videshi_sources"
  ON public.videshi_sources FOR ALL TO public
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Public read videshi_sources"
  ON public.videshi_sources FOR SELECT TO public USING (true);

CREATE POLICY "Service role full access videshi_topic_entities"
  ON public.videshi_topic_entities FOR ALL TO public
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');
