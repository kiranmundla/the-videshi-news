"""
Shared cross-source event dedup utilities.

All event scrapers import from here so fingerprint generation
and dedup checks are consistent across sources.
"""

import hashlib
import json
import os
import re
import subprocess


# ── Fingerprint generation ────────────────────────────────────────────────

def normalize_title(title: str) -> str:
    """Normalize a title for fingerprinting: lowercase, strip non-alphanum, first 60 chars."""
    t = re.sub(r'[^a-z0-9 ]', '', (title or '').lower())
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:60]


def normalize_city(city: str) -> str:
    """Normalize city for fingerprinting."""
    return re.sub(r'[^a-z0-9]', '', (city or '').lower())


def content_fingerprint(title: str, date_str: str, city: str) -> str:
    """
    Unified cross-source content fingerprint.

    Uses normalized title (first 60 alphanum chars) + date + normalized city.
    This works across all sources regardless of whether they have lat/lon,
    time, or venue names (which vary widely between platforms).

    Returns a 16-char hex digest.
    """
    norm_title = normalize_title(title)
    norm_date = (date_str or '')[:10]  # YYYY-MM-DD only
    norm_city = normalize_city(city)
    raw = f"{norm_title}|{norm_date}|{norm_city}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ── Cross-source dedup check ─────────────────────────────────────────────

def get_all_fingerprints() -> set:
    """
    Fetch ALL content_fingerprints from the events table (no source filter).
    Uses curl to avoid proxy issues with Python requests.
    """
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        print("  ⚠ SUPABASE env not set, skipping fingerprint fetch")
        return set()

    fps = set()
    offset = 0
    batch = 5000

    while True:
        url = f"{sb_url}/rest/v1/events?select=content_fingerprint&content_fingerprint=not.is.null&limit={batch}&offset={offset}"
        try:
            r = subprocess.run(
                ["curl", "-s", url,
                 "-H", f"apikey: {sb_key}",
                 "-H", f"Authorization: Bearer {sb_key}"],
                capture_output=True, text=True, timeout=30
            )
            rows = json.loads(r.stdout)
            if not rows:
                break
            for row in rows:
                fp = row.get("content_fingerprint")
                if fp:
                    fps.add(fp)
            if len(rows) < batch:
                break
            offset += batch
        except Exception as e:
            print(f"  ⚠ Error fetching fingerprints (offset {offset}): {e}")
            break

    return fps


# ── Duplicate cleanup ─────────────────────────────────────────────────────

def find_cross_source_duplicates(dry_run: bool = True) -> list:
    """
    Find events that are duplicates across sources.
    Groups by (normalized_title_prefix, date, normalized_city).
    Returns list of dicts: { 'keep': event_row, 'delete': [event_rows] }
    """
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        return []

    # Fetch upcoming events with enough fields to score
    url = (f"{sb_url}/rest/v1/events"
           f"?select=id,title,source,source_id,date,city,ticket_url,description,image_url,created_at,content_fingerprint"
           f"&date=gte.{_today()}"
           f"&order=date.asc"
           f"&limit=5000")
    try:
        r = subprocess.run(
            ["curl", "-s", url,
             "-H", f"apikey: {sb_key}",
             "-H", f"Authorization: Bearer {sb_key}"],
            capture_output=True, text=True, timeout=30
        )
        events = json.loads(r.stdout)
    except Exception as e:
        print(f"  ⚠ Error fetching events for dedup: {e}")
        return []

    # Group by our unified fingerprint
    from collections import defaultdict
    groups = defaultdict(list)
    for ev in events:
        fp = content_fingerprint(
            ev.get("title", ""),
            ev.get("date", ""),
            ev.get("city", "")
        )
        groups[fp].append(ev)

    # Find groups with multiple sources
    dupes = []
    for fp, evts in groups.items():
        sources = set(e.get("source") for e in evts)
        if len(sources) > 1:
            # Score each: ticket_url(3) + description(2) + image(1) + earlier created_at(0.5)
            scored = []
            for e in evts:
                score = 0
                if e.get("ticket_url"):
                    score += 3
                if e.get("description") and len(e["description"]) > 50:
                    score += 2
                if e.get("image_url"):
                    score += 1
                scored.append((score, e))

            # Sort: highest score first, then earliest created_at as tiebreaker
            scored.sort(key=lambda x: (-x[0], x[1].get("created_at", "")))
            keeper = scored[0][1]
            to_delete = [s[1] for s in scored[1:]]
            dupes.append({"keep": keeper, "delete": to_delete})

    return dupes


def cleanup_duplicates(dry_run: bool = True) -> int:
    """
    Find and delete cross-source duplicate events.
    Returns count of deleted rows.
    """
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

    dupes = find_cross_source_duplicates(dry_run=dry_run)
    if not dupes:
        print("  ✅ No cross-source duplicates found")
        return 0

    deleted = 0
    for group in dupes:
        keeper = group["keep"]
        for victim in group["delete"]:
            label = f"[{victim['source']}] {victim['title'][:50]}"
            if dry_run:
                print(f"  🔍 WOULD DELETE: {label}")
                print(f"       keeping [{keeper['source']}] {keeper['title'][:50]}")
            else:
                # Delete by id
                url = f"{sb_url}/rest/v1/events?id=eq.{victim['id']}"
                try:
                    r = subprocess.run(
                        ["curl", "-s", "-X", "DELETE", url,
                         "-H", f"apikey: {sb_key}",
                         "-H", f"Authorization: Bearer {sb_key}",
                         "-H", "Prefer: return=minimal"],
                        capture_output=True, text=True, timeout=15
                    )
                    if r.returncode == 0:
                        print(f"  🗑️  DELETED: {label}")
                        deleted += 1
                    else:
                        print(f"  ⚠ Failed to delete {label}: {r.stderr}")
                except Exception as e:
                    print(f"  ⚠ Error deleting {label}: {e}")

    return deleted


def _today():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def recompute_all_fingerprints():
    """
    Recompute content_fingerprint for all events using the unified formula.
    This ensures old fingerprints (from different formulas) are updated.
    """
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        print("  ⚠ SUPABASE env not set")
        return

    # Fetch all events
    offset = 0
    batch = 1000
    updated = 0

    while True:
        url = (f"{sb_url}/rest/v1/events"
               f"?select=id,title,date,city"
               f"&order=id"
               f"&limit={batch}&offset={offset}")
        try:
            r = subprocess.run(
                ["curl", "-s", url,
                 "-H", f"apikey: {sb_key}",
                 "-H", f"Authorization: Bearer {sb_key}"],
                capture_output=True, text=True, timeout=30
            )
            rows = json.loads(r.stdout)
            if not rows:
                break

            for row in rows:
                new_fp = content_fingerprint(
                    row.get("title", ""),
                    row.get("date", ""),
                    row.get("city", "")
                )
                # Update the fingerprint
                upd_url = f"{sb_url}/rest/v1/events?id=eq.{row['id']}"
                subprocess.run(
                    ["curl", "-s", "-X", "PATCH", upd_url,
                     "-H", f"apikey: {sb_key}",
                     "-H", f"Authorization: Bearer {sb_key}",
                     "-H", "Content-Type: application/json",
                     "-H", "Prefer: return=minimal",
                     "-d", json.dumps({"content_fingerprint": new_fp})],
                    capture_output=True, text=True, timeout=15
                )
                updated += 1

            if updated % 500 == 0:
                print(f"  Updated {updated} events...")

            if len(rows) < batch:
                break
            offset += batch
        except Exception as e:
            print(f"  ⚠ Error at offset {offset}: {e}")
            break

    print(f"  ✅ Recomputed fingerprints for {updated} events")


# ── CLI ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "dry-run"

    if mode == "dry-run":
        print("🔍 DRY RUN — finding cross-source duplicates...")
        dupes = find_cross_source_duplicates(dry_run=True)
        total_extra = sum(len(g["delete"]) for g in dupes)
        print(f"\n  Found {len(dupes)} duplicate groups ({total_extra} extra events)")
        for g in dupes:
            print(f"\n  KEEP [{g['keep']['source']}] {g['keep']['title'][:60]}")
            for d in g['delete']:
                print(f"    DEL [{d['source']}] {d['title'][:60]}")

    elif mode == "clean":
        print("🧹 CLEANING cross-source duplicates...")
        deleted = cleanup_duplicates(dry_run=False)
        print(f"\n  Deleted {deleted} duplicate events")

    elif mode == "recompute":
        print("🔄 RECOMPUTING fingerprints for all events...")
        recompute_all_fingerprints()

    else:
        print(f"Usage: {sys.argv[0]} [dry-run|clean|recompute]")
