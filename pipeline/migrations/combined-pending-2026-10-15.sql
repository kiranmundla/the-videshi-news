-- The Videshi: combined pending migrations — ONE paste in Supabase SQL Editor
-- Built 2026-10-14 evening, combining:
--   1. add-kids-google-place-id.sql  (kids_local_places.google_place_id)
--   2. add-is-visual-story.sql       (p2_articles.is_visual_story)
--   3. add-superseded-status.sql     (prebuilt_reels status CHECK += 'superseded')
-- Every statement is idempotent (IF [NOT] EXISTS guards), so re-running
-- this file is safe. Order does not matter.
--
-- TIME-SENSITIVE PART: #1. The first split-budget directory run
-- (videshi-directory-expansion, daily 02:00 PDT) fires Thu 2026-10-15
-- 02:00 PDT. Kids listings inserted before this column exists lose
-- their Google place ID permanently (that is how 395 current kids
-- rows ended up imageless — the Sunday photo refresh cannot restore
-- a cover without the ID).
--
-- AFTER this runs and is confirmed: land the one-line companion
-- change in pipeline/expand-kids-places.py process() — add
--   "google_place_id": pid,
-- to the row dict (pid is already in scope at the top of process()).
-- Do NOT land that code change before this SQL: PostgREST rejects
-- inserts naming a column that does not exist.

-- 1. kids_local_places: persist Google place IDs
ALTER TABLE kids_local_places
ADD COLUMN IF NOT EXISTS google_place_id TEXT;

CREATE INDEX IF NOT EXISTS idx_kids_local_places_google_place_id
ON kids_local_places (google_place_id)
WHERE google_place_id IS NOT NULL;

-- 2. p2_articles: is_visual_story flag for the image enricher
ALTER TABLE p2_articles
ADD COLUMN IF NOT EXISTS is_visual_story BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_p2_articles_visual_story
ON p2_articles (is_visual_story, published_at DESC)
WHERE status = 'published';

-- 3. prebuilt_reels: allow 'superseded' status
-- (value list = original migration + live-observed 'pending', 'ready',
--  'ig_posted', 'yt_posted' as of 2026-10-14 + 'superseded')
ALTER TABLE prebuilt_reels
  DROP CONSTRAINT IF EXISTS prebuilt_reels_status_check;

ALTER TABLE prebuilt_reels
  ADD CONSTRAINT prebuilt_reels_status_check
  CHECK (status IN ('pending', 'uploading', 'ig_posted', 'yt_posted',
                    'posted', 'failed', 'ready', 'superseded'));

-- Verification (read-back after running — all three should return a row):
-- SELECT column_name FROM information_schema.columns
--   WHERE table_name='kids_local_places' AND column_name='google_place_id';
-- SELECT column_name FROM information_schema.columns
--   WHERE table_name='p2_articles' AND column_name='is_visual_story';
-- SELECT pg_get_constraintdef(oid) FROM pg_constraint
--   WHERE conname='prebuilt_reels_status_check';
