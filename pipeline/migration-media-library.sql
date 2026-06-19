-- ============================================================================
-- The Videshi — media_library table
-- A deliberate, growing, quality-gated, attribution-clean pool of HIGH-QUALITY
-- images AND videos that articles and reels fall back to when X/Threads/
-- Instagram or dynamic search yields nothing better.
--
-- Run this once in the Supabase SQL editor (or psql). The pipeline also keeps a
-- JSON mirror at pipeline/media-library.json, so sourcing/lookup work even
-- before this table exists.
-- ============================================================================

CREATE TABLE IF NOT EXISTS media_library (
    id            text PRIMARY KEY,                  -- stable slug-based id, e.g. "person--narendra-modi--a1b2c3"
    media_type    text NOT NULL CHECK (media_type IN ('image','video')),
    url           text NOT NULL,                     -- Supabase-bucket-hosted public URL (never rots)
    thumb_url     text,                              -- poster/thumbnail (videos) or smaller variant (images)
    subject       text NOT NULL,                     -- canonical subject, e.g. "Narendra Modi", "Mumbai"
    subject_type  text NOT NULL CHECK (subject_type IN ('person','place','thing','event','concept')),
    caption       text,                              -- directly usable as an article image caption
    attribution   text,                              -- e.g. "Wikimedia Commons / Prime Minister's Office, GODL-India"
    license       text,                              -- e.g. "CC BY 2.0", "GODL-India", "PIB / GODL-India", "Pexels License"
    source_url    text,                              -- the original source page (Commons file page, PIB gallery, Pexels page)
    tags          jsonb DEFAULT '[]'::jsonb,         -- free-text tags for matching
    width         integer,
    height        integer,
    duration      numeric,                           -- seconds; NULL for images
    quality_score numeric DEFAULT 0,                 -- resolution + source-trust weighting (see media-library-source.py)
    added_date    timestamptz DEFAULT now(),
    last_used     timestamptz,                       -- bumped by find_media() when chosen
    times_used    integer DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_media_library_subject      ON media_library (lower(subject));
CREATE INDEX IF NOT EXISTS idx_media_library_subject_type ON media_library (subject_type);
CREATE INDEX IF NOT EXISTS idx_media_library_media_type   ON media_library (media_type);
CREATE INDEX IF NOT EXISTS idx_media_library_quality      ON media_library (quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_media_library_tags         ON media_library USING gin (tags);

-- Optional: keep RLS off (service-role only access from the pipeline), matching
-- how the rest of the Videshi pipeline tables are accessed.
