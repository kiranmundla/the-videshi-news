-- Migration: reel_avatars table
-- Stores avatar looks for the reel orchestrator to pick from.
-- New avatars/looks can be added at any time via Supabase dashboard or REST API.

CREATE TABLE IF NOT EXISTS reel_avatars (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  platform TEXT NOT NULL DEFAULT 'heygen',        -- heygen, d-id, etc
  avatar_id TEXT NOT NULL,                         -- platform avatar ID
  avatar_name TEXT NOT NULL,                       -- display name
  look_name TEXT NOT NULL,                         -- look description
  voice_id TEXT,                                   -- platform voice ID
  voice_name TEXT,                                 -- voice description
  style TEXT NOT NULL,                             -- professional, casual, editorial, sporty
  tone TEXT NOT NULL,                              -- serious, conversational, energetic
  categories TEXT[] DEFAULT '{}',                  -- article categories this suits
  fit TEXT DEFAULT 'cover',                        -- cover vs contain
  aspect_ratio TEXT DEFAULT '9:16',
  preview_url TEXT,
  active BOOLEAN DEFAULT true,
  weight REAL DEFAULT 1.0,                         -- selection weight (higher = more likely)
  last_used_at TIMESTAMPTZ,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_reel_avatars_active ON reel_avatars(active) WHERE active = true;
