-- Add is_editorial flag for Editor's Desk hero banner
ALTER TABLE p2_articles ADD COLUMN IF NOT EXISTS is_editorial boolean DEFAULT false;

-- Index for quick lookups of published editorials
CREATE INDEX IF NOT EXISTS idx_p2_articles_editorial
  ON p2_articles (is_editorial, status, published_at DESC)
  WHERE is_editorial = true AND status = 'published';
