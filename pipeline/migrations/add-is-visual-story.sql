-- The Videshi: Add is_visual_story flag to p2_articles
-- Run this in Supabase Dashboard → SQL Editor
-- Purpose: Writers flag highly visual stories (natural phenomena, products,
-- architecture, fashion, food, places) so the image enricher prioritizes them.
-- A visual story without a picture is an incomplete article.

ALTER TABLE p2_articles
ADD COLUMN IF NOT EXISTS is_visual_story BOOLEAN DEFAULT FALSE;

-- Index for the enricher's priority ordering
CREATE INDEX IF NOT EXISTS idx_p2_articles_visual_story
ON p2_articles (is_visual_story, published_at DESC)
WHERE status = 'published';
