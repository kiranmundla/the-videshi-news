#!/usr/bin/env python3
"""Create all immigration tables via Supabase Management API."""
import json, requests, sys

MGMT_TOKEN = os.environ.get("SUPABASE_MGMT_TOKEN", "")
if not MGMT_TOKEN:
    print("Set SUPABASE_MGMT_TOKEN env var")
    sys.exit(1)
PROJECT_REF = "lboecaekpynbpyijrbfz"
URL = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
HEADERS = {
    "Authorization": f"Bearer {MGMT_TOKEN}",
    "Content-Type": "application/json",
}

SQL = """
-- Table 1: visa_bulletin
CREATE TABLE IF NOT EXISTS visa_bulletin (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  bulletin_month INT NOT NULL,
  bulletin_year INT NOT NULL,
  preference_type TEXT NOT NULL,
  category TEXT NOT NULL,
  chart_type TEXT NOT NULL,
  country TEXT NOT NULL,
  priority_date DATE,
  status TEXT DEFAULT 'dated',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(bulletin_month, bulletin_year, category, chart_type, country)
);
CREATE INDEX IF NOT EXISTS idx_visa_bulletin_india ON visa_bulletin(country, category, chart_type) WHERE country = 'india';
CREATE INDEX IF NOT EXISTS idx_visa_bulletin_month ON visa_bulletin(bulletin_year DESC, bulletin_month DESC);

-- Table 2: consulate_wait_times
CREATE TABLE IF NOT EXISTS consulate_wait_times (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  consulate TEXT NOT NULL,
  consulate_display TEXT NOT NULL,
  visa_type TEXT NOT NULL,
  visa_type_display TEXT NOT NULL,
  avg_wait_months NUMERIC(4,1),
  next_available_months NUMERIC(4,1),
  scraped_at TIMESTAMPTZ DEFAULT NOW(),
  source_updated TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_consulate_wait ON consulate_wait_times(consulate, scraped_at DESC);

-- Table 3: uscis_processing_times
CREATE TABLE IF NOT EXISTS uscis_processing_times (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  form_number TEXT NOT NULL,
  form_name TEXT NOT NULL,
  form_category TEXT,
  office TEXT NOT NULL,
  office_code TEXT NOT NULL,
  processing_time_months NUMERIC(4,1),
  estimated_range_low NUMERIC(4,1),
  estimated_range_high NUMERIC(4,1),
  scraped_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_processing_form ON uscis_processing_times(form_number, office_code, scraped_at DESC);

-- Table 4: immigration_guides
CREATE TABLE IF NOT EXISTS immigration_guides (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  subtitle TEXT,
  category TEXT NOT NULL,
  content TEXT NOT NULL,
  meta_description TEXT,
  featured_image TEXT,
  reading_time_min INT,
  last_updated TIMESTAMPTZ DEFAULT NOW(),
  published BOOLEAN DEFAULT true,
  sort_order INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table 5: h1b_data
CREATE TABLE IF NOT EXISTS h1b_data (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  fiscal_year INT NOT NULL,
  metric TEXT NOT NULL,
  value TEXT NOT NULL,
  source_url TEXT,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(fiscal_year, metric)
);

-- Enable RLS but allow public read
ALTER TABLE visa_bulletin ENABLE ROW LEVEL SECURITY;
ALTER TABLE consulate_wait_times ENABLE ROW LEVEL SECURITY;
ALTER TABLE uscis_processing_times ENABLE ROW LEVEL SECURITY;
ALTER TABLE immigration_guides ENABLE ROW LEVEL SECURITY;
ALTER TABLE h1b_data ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='visa_bulletin' AND policyname='public_read_visa_bulletin') THEN
    CREATE POLICY public_read_visa_bulletin ON visa_bulletin FOR SELECT TO anon USING (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='consulate_wait_times' AND policyname='public_read_consulate_wait_times') THEN
    CREATE POLICY public_read_consulate_wait_times ON consulate_wait_times FOR SELECT TO anon USING (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='uscis_processing_times' AND policyname='public_read_uscis_processing_times') THEN
    CREATE POLICY public_read_uscis_processing_times ON uscis_processing_times FOR SELECT TO anon USING (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='immigration_guides' AND policyname='public_read_immigration_guides') THEN
    CREATE POLICY public_read_immigration_guides ON immigration_guides FOR SELECT TO anon USING (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='h1b_data' AND policyname='public_read_h1b_data') THEN
    CREATE POLICY public_read_h1b_data ON h1b_data FOR SELECT TO anon USING (true);
  END IF;
END $$;
"""

resp = requests.post(URL, headers=HEADERS, json={"query": SQL})
print(f"Status: {resp.status_code}")
print(resp.text[:2000])
if resp.status_code not in (200, 201):
    sys.exit(1)
print("\n✅ All 5 immigration tables created successfully!")
