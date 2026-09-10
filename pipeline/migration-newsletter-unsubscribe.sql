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
--
-- Return values: 'unsubscribed' | 'already' | 'not_found' | 'invalid'

CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE newsletter_subscribers
  ADD COLUMN IF NOT EXISTS unsubscribed_at timestamptz;

-- DROP first: Postgres won't change a function's return type via CREATE OR REPLACE
DROP FUNCTION IF EXISTS unsubscribe_newsletter(text, text);

CREATE OR REPLACE FUNCTION unsubscribe_newsletter(p_email text, p_token text)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  -- Must match UNSUB_SECRET in pipeline/send-newsletter.py / send-newsletter-daily.py
  v_secret text := 'thevideshi-unsub';
  v_expected text;
  v_exists boolean;
  v_already boolean;
BEGIN
  -- 'invalid': missing params or token mismatch (forged/tampered link)
  IF p_email IS NULL OR p_token IS NULL OR p_email = '' OR p_token = '' THEN
    RETURN 'invalid';
  END IF;

  v_expected := substr(encode(extensions.hmac(convert_to(lower(p_email), 'UTF8'), convert_to(v_secret, 'UTF8'), 'sha256'::text), 'hex'), 1, 16);

  IF v_expected IS DISTINCT FROM lower(p_token) THEN
    RETURN 'invalid';
  END IF;

  -- Token is valid: is this email on the list?
  SELECT EXISTS (
    SELECT 1 FROM newsletter_subscribers WHERE lower(email) = lower(p_email)
  ) INTO v_exists;
  IF NOT v_exists THEN
    -- Valid token but unknown address. End state is what the user wants: no mail.
    RETURN 'not_found';
  END IF;

  SELECT unsubscribed_at IS NOT NULL FROM newsletter_subscribers
  WHERE lower(email) = lower(p_email) INTO v_already;
  IF v_already THEN
    RETURN 'already';
  END IF;

  UPDATE newsletter_subscribers
  SET unsubscribed_at = now()
  WHERE lower(email) = lower(p_email);

  RETURN 'unsubscribed';
END;
$$;

-- Allow the public API (anon key) to call it; token verification happens inside.
GRANT EXECUTE ON FUNCTION unsubscribe_newsletter(text, text) TO anon;
