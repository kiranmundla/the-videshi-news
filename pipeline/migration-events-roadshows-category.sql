-- Exhibitions & Roadshows category for the events table (2026-10-18)
-- Kiran's one-stop-shop directive: touring merchants (Dubai/India
-- property roadshows & expos, Indian jewelry exhibition tours, Indian
-- bridal expos) are covered as events under their own category.
--
-- The live events_category_check currently allows the original 12
-- values from create-events-table.sql PLUS Entertainment, Shopping,
-- Spiritual, Technology (added by later dashboard migrations — the
-- distinct category values present in the table on 2026-10-18).
-- This migration re-states the full live list + the new value so the
-- constraint stays exactly as permissive as it is today, plus one.
--
-- Apply via Supabase SQL editor or Management API
-- (POST /v1/projects/lboecaekpynbpyijrbfz/database/query).
-- After applying, flip the seeded rows to the real category:
--   python3 pipeline/seed-roadshow-events.py "Exhibitions & Roadshows"
-- (the seed script patches category on existing source_ids).

ALTER TABLE public.events DROP CONSTRAINT events_category_check;

ALTER TABLE public.events ADD CONSTRAINT events_category_check
  CHECK (category IN ('Cultural', 'Music', 'Food', 'Sports', 'Community',
                      'Festival', 'Comedy', 'Dance', 'Religious', 'Education',
                      'Competition', 'Entertainment', 'Shopping', 'Spiritual',
                      'Technology', 'Exhibitions & Roadshows', 'Other'));
