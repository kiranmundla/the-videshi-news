-- Migration: OTP tables for visa sighting reports and alert signups
-- Run against the Supabase SQL editor

CREATE TABLE IF NOT EXISTS sighting_otps (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  email text NOT NULL,
  code text NOT NULL,
  expires_at timestamptz NOT NULL,
  used boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alert_otps (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  email text NOT NULL,
  code text NOT NULL,
  expires_at timestamptz NOT NULL,
  used boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Indexes for lookups
CREATE INDEX IF NOT EXISTS idx_sighting_otps_email ON sighting_otps(email);
CREATE INDEX IF NOT EXISTS idx_sighting_otps_lookup ON sighting_otps(email, code, used);
CREATE INDEX IF NOT EXISTS idx_alert_otps_email ON alert_otps(email);
CREATE INDEX IF NOT EXISTS idx_alert_otps_lookup ON alert_otps(email, code, used);

-- Cleanup: auto-delete expired OTPs older than 1 hour (run via pg_cron or manual)
-- DELETE FROM sighting_otps WHERE expires_at < now() - interval '1 hour';
-- DELETE FROM alert_otps WHERE expires_at < now() - interval '1 hour';
