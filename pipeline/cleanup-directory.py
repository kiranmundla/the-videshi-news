#!/usr/bin/env python3
"""
Cleanup existing directory_listings: remove non-Indian businesses
and enforce quality gates on the remainder.

Uses indian_relevance.is_indian_business() for relevance + quality rules.
"""
import json
import os
import subprocess
import sys
import collections

sys.path.insert(0, os.path.dirname(__file__))
from indian_relevance import is_indian_business

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SRK = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_AT = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
PROJECT_REF = "lboecaekpynbpyijrbfz"


def mgmt_query(sql):
    """Run SQL via Supabase Management API (read-only)."""
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    payload = json.dumps({"query": sql})
    cmd = [
        "curl", "-sS", "--max-time", "30",
        "-X", "POST", url,
        "-H", f"Authorization: Bearer {SUPABASE_AT}",
        "-H", "Content-Type: application/json",
        "-d", payload,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
    if r.returncode != 0:
        print(f"ERROR: mgmt_query failed: {r.stderr}", file=sys.stderr)
        return []
    try:
        return json.loads(r.stdout)
    except Exception as e:
        print(f"ERROR: parse mgmt_query: {e}\n{r.stdout[:500]}", file=sys.stderr)
        return []


def delete_ids(ids):
    """Delete listings by ID via REST API."""
    if not ids:
        return 0
    deleted = 0
    # Batch delete in chunks of 100
    for i in range(0, len(ids), 100):
        batch = ids[i:i+100]
        id_csv = ",".join(str(x) for x in batch)
        url = f"{SUPABASE_URL}/rest/v1/directory_listings?id=in.({id_csv})"
        cmd = [
            "curl", "-sS", "--max-time", "30",
            "-X", "DELETE", url,
            "-H", f"apikey: {SUPABASE_SRK}",
            "-H", f"Authorization: Bearer {SUPABASE_SRK}",
            "-H", "Prefer: count=exact",
            "-o", "/dev/null", "-w", "%{http_code}",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        code = r.stdout.strip()
        if code in ("200", "204"):
            deleted += len(batch)
        else:
            print(f"  WARNING: delete batch returned {code}", file=sys.stderr)
    return deleted


def main():
    print("=" * 60)
    print("Directory Cleanup — Indian Relevance Filter")
    print("=" * 60)

    # Fetch all listings
    rows = mgmt_query(
        "SELECT id, name, category, rating, review_count FROM directory_listings ORDER BY id"
    )
    print(f"Total listings in DB: {len(rows)}")

    keep_ids = []
    delete_ids_list = []
    stats_keep = collections.Counter()
    stats_del = collections.Counter()
    stats_reason = collections.Counter()

    for row in rows:
        name = row.get("name", "")
        cat = row.get("category", "")
        rid = row["id"]
        rating = float(row.get("rating") or 0)
        reviews = int(row.get("review_count") or 0)

        is_relevant, skip_quality = is_indian_business(name, cat)

        if not is_relevant:
            delete_ids_list.append(rid)
            stats_del[cat] += 1
            stats_reason["not_indian"] += 1
            continue

        if not skip_quality:
            if rating < 4.0 or reviews < 10:
                delete_ids_list.append(rid)
                stats_del[cat] += 1
                stats_reason["low_quality"] += 1
                continue

        keep_ids.append(rid)
        stats_keep[cat] += 1

    print(f"\nKeep: {len(keep_ids)}")
    print(f"Delete: {len(delete_ids_list)}")
    print(f"  - Not Indian: {stats_reason['not_indian']}")
    print(f"  - Low quality: {stats_reason['low_quality']}")

    print("\n── Kept by category ──")
    for cat, n in sorted(stats_keep.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {n}")

    print("\n── Deleted by category ──")
    for cat, n in sorted(stats_del.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {n}")

    # Perform the deletes
    if delete_ids_list:
        print(f"\nDeleting {len(delete_ids_list)} records...")
        deleted = delete_ids(delete_ids_list)
        print(f"Deleted: {deleted}")
    else:
        print("\nNothing to delete.")

    # Verify final count
    final = mgmt_query("SELECT COUNT(*) as total FROM directory_listings")
    if final:
        print(f"\nFinal count: {final[0]['total']}")

    print("=" * 60)


if __name__ == "__main__":
    main()
