-- Flight deals schema for The Videshi
-- Run this in the Supabase SQL editor (dashboard) — the REST API cannot do DDL.
--
-- Tables:
--   flight_prices          — raw price observations (one row per search)
--   flight_price_monthly   — aggregated calendar data per route/month/weeks
--   flight_alerts          — user price alerts (Phase 2)

-- ── Raw price observations ──────────────────────────────────────────
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
  -- One observation per route/date-pair/weeks per day
  UNIQUE (origin, destination, dep_date, ret_date, weeks, (searched_at::date))
);

CREATE INDEX IF NOT EXISTS idx_flight_prices_route
  ON flight_prices (origin, destination, weeks, searched_at DESC);
CREATE INDEX IF NOT EXISTS idx_flight_prices_dep
  ON flight_prices (dep_date);

-- ── Monthly aggregates (what the calendar reads) ────────────────────
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

-- ── User price alerts (Phase 2) ─────────────────────────────────────
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

-- ── RLS: public read, service-role write ────────────────────────────
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
