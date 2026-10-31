#!/usr/bin/env python3
"""backfill_image_provenance.py — replay the Rung 0 JSONL ledger
into p2_articles.image_provenance once the column exists (see
image_provenance_migration.sql).

For each article in the ledger: the latest event becomes the
current placement and every earlier event is preserved in its
`history` array (oldest first) — removals included; nothing is
erased. Articles whose DB value already matches the folded ledger
are skipped, so the script is idempotent and safe to re-run.

Usage:
  set -a; source ~/workspace/.env.supabase; set +a
  python3 backfill_image_provenance.py [--dry-run] [--limit N]

Exits 0 with a clear message when the column does not exist yet —
that is the expected state until the migration is run.
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import image_ledger as L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    url, key = L._sb_env()
    if not url:
        print("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set — "
              "source ~/workspace/.env.supabase first.")
        return 1
    if not L._db_column_exists(url, key):
        print("p2_articles.image_provenance does not exist yet. "
              "Run image_provenance_migration.sql in the Supabase "
              "SQL editor, then re-run this backfill. The JSONL "
              f"ledger at {L.ledger_path()} remains the record "
              "until then.")
        return 0

    records = L.read_ledger()
    by_article = {}
    for rec in records:
        aid = rec.get("article_id")
        if aid:
            by_article.setdefault(aid, []).append(rec)
    print(f"Ledger: {len(records)} events across "
          f"{len(by_article)} articles.")
    done = skipped = failed = 0
    for aid, recs in by_article.items():
        if args.limit and done >= args.limit:
            break
        prov = L.current_with_history(recs)
        try:
            rows = L._curl_json(
                "GET",
                f"{url}/rest/v1/p2_articles?id=eq.{aid}"
                "&select=image_provenance", key)
            current = rows[0].get("image_provenance") \
                if isinstance(rows, list) and rows else None
            if current == prov:
                skipped += 1
                continue
            if args.dry_run:
                print(f"  would PATCH {aid} "
                      f"({len(recs)} events, current action="
                      f"{prov.get('action')})")
                done += 1
                continue
            L._curl_json("PATCH",
                         f"{url}/rest/v1/p2_articles?id=eq.{aid}",
                         key, {"image_provenance": prov})
            done += 1
        except Exception as e:
            failed += 1
            print(f"  ⚠ {aid}: {e}")
    print(f"Backfill {'(dry run) ' if args.dry_run else ''}done: "
          f"{done} written, {skipped} already current, "
          f"{failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
