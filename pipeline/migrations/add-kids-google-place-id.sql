-- The Videshi: Persist Google place IDs on kids_local_places
-- Run this in Supabase Dashboard → SQL Editor (batch with
-- add-is-visual-story.sql and add-superseded-status.sql)
--
-- Why: expand-kids-places.py receives each place's Google ID
-- (normalize_place -> "place_id") but process() uses it only to hash
-- the slug — the row it inserts carries no place ID, and this table
-- has no column for one. Directory listings store google_place_id,
-- which is exactly what lets the Sunday photo refresh restore a
-- cover when image_url is null. Kids rows can never restore: 395
-- imageless kids rows exist today, and only the 312 cross-referenced
-- from directory listings can heal indirectly.
--
-- Timing: the first full split-budget production run of
-- videshi-directory-expansion (kids first, 20 guaranteed Places
-- calls) is Thu 2026-10-15 02:00 PDT. Every kids listing inserted
-- before this column exists loses its place ID permanently.
--
-- After running this, land the one-line companion change in
-- pipeline/expand-kids-places.py process(): add
--   "google_place_id": pid,
-- to the inserted row dict (pid is already in scope). Do NOT land
-- the code change first — PostgREST rejects inserts naming a
-- column that does not exist, which would fail whole batches.

ALTER TABLE kids_local_places
ADD COLUMN IF NOT EXISTS google_place_id TEXT;

CREATE INDEX IF NOT EXISTS idx_kids_local_places_google_place_id
ON kids_local_places (google_place_id)
WHERE google_place_id IS NOT NULL;
