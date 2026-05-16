-- Newsletter subscribers table
-- Run this in Supabase SQL editor (Dashboard > SQL Editor)
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  email text NOT NULL UNIQUE,
  subscribed_at timestamptz DEFAULT now()
);

ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (for the subscribe API)
CREATE POLICY "allow_anon_insert" ON newsletter_subscribers
  FOR INSERT TO anon WITH CHECK (true);

-- Allow service role to read all
CREATE POLICY "allow_service_select" ON newsletter_subscribers
  FOR SELECT TO service_role USING (true);
