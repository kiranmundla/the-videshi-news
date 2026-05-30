-- Migration: Diaspora Voices (community stories)
-- Run in Supabase SQL editor

CREATE TABLE IF NOT EXISTS stories (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,

  -- Author info
  author_name text NOT NULL,
  author_email text NOT NULL,
  author_photo_url text,
  author_city text,
  author_linkedin text,

  -- Story content
  category text NOT NULL DEFAULT 'general',
  headline text,
  subheadline text,
  body text,
  raw_story text NOT NULL,

  -- Structured prompts
  prompt_what_happened text,
  prompt_how_affected text,
  prompt_advice text,
  prompt_years_in_us text,
  prompt_origin_city text,

  -- Status & moderation
  status text NOT NULL DEFAULT 'draft',
  featured boolean DEFAULT false,
  rejection_reason text,
  suspicion_score integer DEFAULT 0,

  -- Verification
  email_verified boolean DEFAULT false,
  otp_code text,
  otp_expires_at timestamptz,
  edit_token text,

  -- Engagement
  reaction_count integer DEFAULT 0,
  view_count integer DEFAULT 0,

  -- Metadata
  slug text UNIQUE,
  image_url text,
  published_at timestamptz,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_stories_status ON stories(status);
CREATE INDEX IF NOT EXISTS idx_stories_category ON stories(category);
CREATE INDEX IF NOT EXISTS idx_stories_slug ON stories(slug);
CREATE INDEX IF NOT EXISTS idx_stories_published ON stories(published_at DESC) WHERE status = 'published';

-- RLS policies
ALTER TABLE stories ENABLE ROW LEVEL SECURITY;

-- Public can read published stories
CREATE POLICY "Published stories are public" ON stories
  FOR SELECT USING (status = 'published');

-- Service role has full access (edge functions use service role key)
CREATE POLICY "Service role full access" ON stories
  FOR ALL USING (true) WITH CHECK (true);
