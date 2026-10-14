-- Add 'superseded' to the prebuilt_reels status CHECK.
--
-- Why: when the channel owner deletes a Phase 2 upload in YouTube
-- Studio (e.g. to redo a reel with a different music bed),
-- reel_publish.py --supersede marks the prebuilt_reels row as
-- superseded. The live status CHECK (which already allows 'ready'
-- beyond the original migration-prebuilt-reels.sql list) rejects
-- 'superseded', so until this migration runs, supersede falls back
-- to a `superseded=` marker in qa_notes (recognised by
-- reel_publish.is_superseded_row and reel_reconcile.py). Running
-- this makes the status itself express the state; the marker stays
-- as the audit trail.
--
-- Run in the Supabase SQL editor. Verify the current constraint
-- definition first (pg_constraint 'prebuilt_reels_status_check') —
-- the value list below is the union of the original migration, the
-- values observed live on 2026-10-14 ('pending', 'ready',
-- 'ig_posted', 'yt_posted'), and 'superseded'.

ALTER TABLE prebuilt_reels
  DROP CONSTRAINT IF EXISTS prebuilt_reels_status_check;

ALTER TABLE prebuilt_reels
  ADD CONSTRAINT prebuilt_reels_status_check
  CHECK (status IN ('pending', 'uploading', 'ig_posted', 'yt_posted',
                    'posted', 'failed', 'ready', 'superseded'));
