-- ============================================================================
-- The Videshi — trigram search indexes for p2_articles
-- Fixes intermittent statement-timeouts on site search. The search box runs
-- leading-wildcard ILIKE ('%term%') over headline/subheadline/body. With ~4,900
-- published articles, the body scan is unindexed and times out ~1 in 4 on
-- common terms (e.g. "h1b"). pg_trgm GIN indexes make these ILIKE scans use an
-- index instead of a full sequential scan. No frontend change required.
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS idx_p2_articles_headline_trgm
    ON p2_articles USING gin (headline gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_p2_articles_subheadline_trgm
    ON p2_articles USING gin (subheadline gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_p2_articles_body_trgm
    ON p2_articles USING gin (body gin_trgm_ops);
