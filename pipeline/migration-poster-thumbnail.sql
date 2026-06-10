-- Add poster and thumbnail columns to prebuilt_reels
-- Run this in Supabase SQL Editor
ALTER TABLE prebuilt_reels ADD COLUMN IF NOT EXISTS poster_url TEXT;
ALTER TABLE prebuilt_reels ADD COLUMN IF NOT EXISTS thumbnail_url TEXT;
