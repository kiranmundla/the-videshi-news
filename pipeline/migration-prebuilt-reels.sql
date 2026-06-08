-- Migration: prebuilt_reels table for HeyGen/manual reel pipeline
-- Created: 2026-06-08
-- Run in Supabase Dashboard > SQL Editor

CREATE TABLE IF NOT EXISTS public.prebuilt_reels (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  article_id UUID REFERENCES public.p2_articles(id),
  article_slug TEXT,
  headline TEXT,
  video_path TEXT NOT NULL,
  video_url TEXT,
  caption TEXT,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'uploading', 'ig_posted', 'yt_posted', 'posted', 'failed')),
  ig_media_id TEXT,
  yt_video_id TEXT,
  ig_posted_at TIMESTAMPTZ,
  yt_posted_at TIMESTAMPTZ,
  source TEXT DEFAULT 'manual'
    CHECK (source IN ('manual', 'heygen', 'ffmpeg')),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_prebuilt_reels_status ON public.prebuilt_reels(status);
CREATE INDEX IF NOT EXISTS idx_prebuilt_reels_article ON public.prebuilt_reels(article_id);

-- Status lifecycle:
--   pending → uploading → ig_posted → posted (after YT too)
--   pending → uploading → yt_posted → posted (after IG too)
--   any → failed

NOTIFY pgrst, 'reload schema';
