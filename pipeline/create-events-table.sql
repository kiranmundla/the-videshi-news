-- Events table for The Videshi events feature
-- Run this in Supabase Dashboard > SQL Editor

CREATE TABLE IF NOT EXISTS events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  date DATE NOT NULL,
  time TEXT,
  end_date DATE,
  venue_name TEXT,
  city TEXT NOT NULL,
  state TEXT,
  category TEXT CHECK (category IN ('Cultural', 'Music', 'Food', 'Sports', 'Community', 'Festival', 'Comedy', 'Dance', 'Religious', 'Education', 'Competition', 'Other')),
  description TEXT,
  image_url TEXT,
  ticket_url TEXT,
  source TEXT,
  source_id TEXT,
  price_range TEXT,
  organizer TEXT,
  audience TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(source, source_id)
);

-- Enable RLS but allow public reads (anon key can query)
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access" ON events
  FOR SELECT USING (true);

CREATE POLICY "Allow service role full access" ON events
  FOR ALL USING (auth.role() = 'service_role');

-- Index for common queries
CREATE INDEX idx_events_date ON events(date);
CREATE INDEX idx_events_city ON events(city);
CREATE INDEX idx_events_category ON events(category);
CREATE INDEX idx_events_audience ON events(audience);
