-- image_provenance_migration.sql — Rung 0 of the image-sourcing
-- rebuild (2026-10-30, design §2). Run ONCE in the Supabase SQL
-- editor (or via the Management API when a token is provisioned).
--
-- As of 2026-10-30 this has NOT been run: the build environment
-- holds no SUPABASE_ACCESS_TOKEN (sbp_) and DDL cannot be issued
-- through PostgREST with the service-role key. Until it runs, the
-- provenance ledger of record is the append-only JSONL at
-- pipeline/.state/image-provenance.jsonl (see image_ledger.py);
-- afterwards, run backfill_image_provenance.py to replay it.
-- image_ledger.record_provenance() already best-effort syncs this
-- column on every write once it exists — no code change needed.

alter table public.p2_articles
  add column if not exists image_provenance jsonb;

comment on column public.p2_articles.image_provenance is
  'Rung 0 provenance ledger (current placement; prior events in '
  'history[]): {article_id, slug, surface, action, producer, '
  'source_route, image_url, source_page_url, original_file_url, '
  'file_key, rights_status, license, attribution, capture_year, '
  'entity, reason, placed_at, history[]}';
