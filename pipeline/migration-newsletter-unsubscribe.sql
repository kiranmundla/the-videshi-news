-- Migration: make newsletter unsubscribe actually work
-- Date: 2026-09-10
--
-- Background: newsletter emails contain /unsubscribe?email=..&token=.. links plus
-- List-Unsubscribe one-click headers, but no handler ever existed — clicks landed
-- on the CategoryPage for "unsubscribe" and nobody was ever unsubscribed.
--
-- This adds:
--   1. unsubscribed_at column on newsletter_subscribers (NULL = subscribed)
--   2. unsubscribe_newsletter(email, token) SECURITY DEFINER function that verifies
--      the HMAC token and marks the subscriber unsubscribed. Token format must match
--      make_unsub_token() in pipeline/send-newsletter.py:
--        hmac.new(secret, email.lower(), sha256).hexdigest()[:16]
--      IMPORTANT: keep v_secret in sync with UNSUB_SECRET used by the pipeline
--      (currently the pipeline falls back to 'thevideshi-unsub' when the env var
--      is unset — all tokens sent to date use that value).

CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE newsletter_subscribers
  ADD COLUMN IF NOT EXISTS unsubscribed_at timestamptz;

CREATE OR REPLACE FUNCTION unsubscribe_newsletter(p_email text, p_token text)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  -- Must match UNSUB_SECRET in pipeline/send-newsletter.py / send-newsletter-daily.py
  v_secret text := 'thevideshi-unsub';
  v_expected text;
  v_rows int := 0;
BEGIN
  IF p_email IS NULL OR p_token IS NULL OR p_email = '' OR p_token = '' THEN
    RETURN false;
  END IF;

  v_expected := substr(encode(extensions.hmac(convert_to(lower(p_email), 'UTF8'), convert_to(v_secret, 'UTF8'), 'sha256'::text), 'hex'), 1, 16);

  IF v_expected IS DISTINCT FROM lower(p_token) THEN
    RETURN false;
  END IF;

  UPDATE newsletter_subscribers
  SET unsubscribed_at = now()
  WHERE lower(email) = lower(p_email)
    AND unsubscribed_at IS NULL;

  GET DIAGNOSTICS v_rows = ROW_COUNT;
  RETURN v_rows > 0;
END;
$$;

-- Allow the public API (anon key) to call it; token verification happens inside.
GRANT EXECUTE ON FUNCTION unsubscribe_newsletter(text, text) TO anon;
