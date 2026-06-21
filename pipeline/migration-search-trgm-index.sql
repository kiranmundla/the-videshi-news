-- ============================================================================
-- The Videshi — trigram search indexes for p2_articles
-- Fixes intermittent statement-timeouts on site search. The search box runs
-- leading-wildcard ILIKE ('%term%') over headline/subheadline/body. With ~4,900
-- published articles, the body scan is unindexed and times out ~1 in 4 on
-- common terms (e.g. "h1b"). pg_trgm GIN indexes make these ILIKE scans use an
-- index instead of a full sequential scan. No frontend change required.
-- ============================================================================

-- NOTE (2026-06-21): The body GIN build was repeatedly cancelled by the server-side
-- statement_timeout when run via the Management API, leaving NOTHING persisted (rolled back).
-- Fix: prepend `SET statement_timeout = 0;` in the SAME query call as the body index.
-- With that, the body GIN index built in ~10s. All three indexes are now live in prod.
--   SET statement_timeout = 0; CREATE INDEX IF NOT EXISTS idx_p2_articles_body_trgm ON p2_articles USING gin (body gin_trgm_ops);

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS idx_p2_articles_headline_trgm
    ON p2_articles USING gin (headline gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_p2_articles_subheadline_trgm
    ON p2_articles USING gin (subheadline gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_p2_articles_body_trgm
    ON p2_articles USING gin (body gin_trgm_ops);
