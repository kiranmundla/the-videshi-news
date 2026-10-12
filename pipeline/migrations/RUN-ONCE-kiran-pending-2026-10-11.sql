-- The Videshi — ONE-PASTE pending migrations (2026-10-11)
-- =====================================================================
-- HOW TO RUN (takes ~10 seconds):
--   1. Open Supabase Dashboard → SQL Editor → New query
--   2. Paste this whole file, press Run
--   3. Scroll to the bottom: the verification queries print one row each.
--      You should see: is_visual_story | YES, and three rows flight_prices /
--      flight_price_monthly / flight_alerts all | YES.
-- Everything here is idempotent (IF NOT EXISTS everywhere) — safe to run twice.
--
-- This file is a concatenation of two already-reviewed migrations, so you only
-- have to paste once:
--   A. pipeline/migrations/add-is-visual-story.sql        (visual-story image priority)
--   B. pipeline/flight-deals-schema.sql                   (flight deals price calendar)

-- ══════════════════════════════════════════════════════════════════════
-- A. Visual-story flag on p2_articles
-- Lets writers flag highly visual stories (phenomena, products, architecture,
-- fashion, food, places) so the image enricher prioritizes them — a visual
-- story without a picture is an incomplete article.
-- ══════════════════════════════════════════════════════════════════════
ALTER TABLE p2_articles
ADD COLUMN IF NOT EXISTS is_visual_story BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_p2_articles_visual_story
ON p2_articles (is_visual_story, published_at DESC)
WHERE status = 'published';

-- ══════════════════════════════════════════════════════════════════════
-- B. Flight deals price-calendar schema (Travel page, Phase 1)
-- Tables: flight_prices (raw observations), flight_price_monthly (calendar
-- aggregates the page reads), flight_alerts (Phase 2 price alerts).
-- ══════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS flight_prices (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  origin        TEXT NOT NULL,          -- IATA, e.g. 'SFO'
  destination   TEXT NOT NULL,          -- IATA, e.g. 'DEL'
  dep_date      DATE NOT NULL,          -- outbound date
  ret_date      DATE NOT NULL,          -- return date
  weeks         INT  NOT NULL,          -- trip duration in weeks (2/3/4)
  price_min     NUMERIC NOT NULL,       -- cheapest qualifying fare (USD)
  price_max     NUMERIC NOT NULL,       -- 25th pct fare (USD), upper bound of "good" range
  currency      TEXT NOT NULL DEFAULT 'USD',
  airline       TEXT,                   -- cheapest airline name
  num_offers    INT,                    -- qualifying offers found
  max_stops     INT  NOT NULL DEFAULT 1,
  min_bags      INT  NOT NULL DEFAULT 2,
  searched_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (origin, destination, dep_date, ret_date, weeks, (searched_at::date))
);

CREATE INDEX IF NOT EXISTS idx_flight_prices_route
  ON flight_prices (origin, destination, weeks, searched_at DESC);
CREATE INDEX IF NOT EXISTS idx_flight_prices_dep
  ON flight_prices (dep_date);

CREATE TABLE IF NOT EXISTS flight_price_monthly (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  origin        TEXT NOT NULL,
  destination   TEXT NOT NULL,
  year          INT  NOT NULL,
  month         INT  NOT NULL CHECK (month BETWEEN 1 AND 12),
  weeks         INT  NOT NULL,
  dep_date      DATE NOT NULL,          -- best departure date found
  ret_date      DATE NOT NULL,          -- best return date found
  price_min     NUMERIC NOT NULL,
  price_max     NUMERIC NOT NULL,
  airline       TEXT,
  num_samples   INT,
  as_of         DATE NOT NULL,          -- when prices were observed
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (origin, destination, year, month, weeks)
);

CREATE INDEX IF NOT EXISTS idx_flight_price_monthly_route
  ON flight_price_monthly (origin, destination, weeks, year, month);

CREATE TABLE IF NOT EXISTS flight_alerts (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  origin        TEXT NOT NULL,
  destination   TEXT NOT NULL,
  weeks         INT  NOT NULL,
  target_price  NUMERIC,                -- alert when price_min <= target
  channel       TEXT NOT NULL DEFAULT 'whatsapp',  -- whatsapp | email
  contact       TEXT NOT NULL,          -- phone or email
  active        BOOLEAN NOT NULL DEFAULT true,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_notified TIMESTAMPTZ
);

ALTER TABLE flight_prices        ENABLE ROW LEVEL SECURITY;
ALTER TABLE flight_price_monthly ENABLE ROW LEVEL SECURITY;
ALTER TABLE flight_alerts        ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "public read flight_prices" ON flight_prices;
CREATE POLICY "public read flight_prices"
  ON flight_prices FOR SELECT USING (true);

DROP POLICY IF EXISTS "public read flight_price_monthly" ON flight_price_monthly;
CREATE POLICY "public read flight_price_monthly"
  ON flight_price_monthly FOR SELECT USING (true);

-- flight_alerts: no public access (service role only)

-- ══════════════════════════════════════════════════════════════════════
-- VERIFICATION — expect: is_visual_story | YES, plus three YES rows
-- ══════════════════════════════════════════════════════════════════════
SELECT 'is_visual_story' AS check,
       CASE WHEN EXISTS (
         SELECT 1 FROM information_schema.columns
         WHERE table_name = 'p2_articles' AND column_name = 'is_visual_story'
       ) THEN 'YES' ELSE 'MISSING' END AS status;

SELECT tablename AS flight_table,
       CASE WHEN rowsecurity THEN 'YES (RLS on)' ELSE 'NO RLS' END AS status
FROM pg_tables
WHERE tablename IN ('flight_prices', 'flight_price_monthly', 'flight_alerts')
ORDER BY tablename;
