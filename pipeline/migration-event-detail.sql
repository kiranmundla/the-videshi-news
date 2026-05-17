-- Migration: Add event detail page columns
-- Run this in Supabase Dashboard > SQL Editor
-- After running, do NOTIFY pgrst, 'reload schema';

ALTER TABLE public.events ADD COLUMN IF NOT EXISTS long_description TEXT;
ALTER TABLE public.events ADD COLUMN IF NOT EXISTS artist_info TEXT;
ALTER TABLE public.events ADD COLUMN IF NOT EXISTS venue_info TEXT;
ALTER TABLE public.events ADD COLUMN IF NOT EXISTS slug TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS events_slug_idx ON public.events(slug);

-- Generate slugs for existing events
UPDATE public.events
SET slug = LOWER(
  REGEXP_REPLACE(
    REGEXP_REPLACE(
      LEFT(REGEXP_REPLACE(title, '[^a-zA-Z0-9\s-]', '', 'g'), 60),
      '\s+', '-', 'g'
    ),
    '-+$', ''
  )
) || '-' || date::text
WHERE slug IS NULL;

-- Reload PostgREST schema cache
NOTIFY pgrst, 'reload schema';
