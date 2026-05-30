-- Visa Alert Subscribers
CREATE TABLE IF NOT EXISTS visa_alert_subscribers (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  email text NOT NULL UNIQUE,
  visa_type text NOT NULL DEFAULT 'all',
  consulate text,
  channel text DEFAULT 'email',
  phone text,
  subscribed_at timestamptz DEFAULT now(),
  unsubscribed_at timestamptz,
  active boolean DEFAULT true
);

-- RLS
ALTER TABLE visa_alert_subscribers ENABLE ROW LEVEL SECURITY;

-- Allow anon insert (signup)
CREATE POLICY "anon_insert_visa_alerts" ON visa_alert_subscribers
  FOR INSERT TO anon WITH CHECK (true);

-- Allow anon update own row (for unsubscribe via email link)
CREATE POLICY "anon_update_visa_alerts" ON visa_alert_subscribers
  FOR UPDATE TO anon USING (true) WITH CHECK (true);

-- Service role can read all (for sending alerts)
CREATE POLICY "service_read_visa_alerts" ON visa_alert_subscribers
  FOR SELECT TO service_role USING (true);

-- Index for lookups
CREATE INDEX IF NOT EXISTS idx_visa_alerts_active ON visa_alert_subscribers (active, visa_type);
CREATE INDEX IF NOT EXISTS idx_visa_alerts_email ON visa_alert_subscribers (email);
