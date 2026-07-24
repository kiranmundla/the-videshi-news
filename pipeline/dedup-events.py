#!/usr/bin/env python3
"""
Deduplicate events in the Videshi events table.

Groups future events by (date, normalized_venue) and uses fuzzy title
matching to identify duplicates within each group. Keeps the event with
the most complete data and deletes the rest.

Usage:
    python3 -u pipeline/dedup-events.py              # live run
    python3 -u pipeline/dedup-events.py --dry-run    # preview only
"""

import json, os, re, subprocess, sys, unicodedata
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher

# ── Config ───────────────────────────────────────────────────────────────
DRY_RUN = "--dry-run" in sys.argv
TITLE_SIMILARITY_THRESHOLD = 0.5
SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
TODAY = datetime.utcnow().strftime("%Y-%m-%d")

# ── Supabase helpers ─────────────────────────────────────────────────────
def sb_get(endpoint, params, range_header=None):
    """GET from Supabase REST API using curl."""
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{SB_URL}/rest/v1/{endpoint}?{qs}"
    cmd = [
        "curl", "-s", url,
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
    ]
    if range_header:
        cmd += ["-H", f"Range: {range_header}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"  ⚠ Failed to parse response: {r.stdout[:200]}")
        return []


def sb_delete(ids):
    """Delete events by ID list using curl."""
    if not ids:
        return 0
    # Supabase REST API accepts IN filter
    id_filter = ",".join(ids)
    url = f"{SB_URL}/rest/v1/events?id=in.({id_filter})"
    cmd = [
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-X", "DELETE", url,
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    code = r.stdout.strip()
    if code in ("200", "204"):
        return len(ids)
    else:
        print(f"  ⚠ Delete failed (HTTP {code}) for {len(ids)} events")
        return 0


# ── Normalization ────────────────────────────────────────────────────────
def normalize_venue(name):
    """Normalize venue name for grouping."""
    if not name:
        return ""
    # Remove accents/diacritics
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    # Remove trailing city/state suffixes like ", Chicago, IL, USA"
    # Pattern: strip everything after last comma-separated city/state chunk
    s = re.sub(r",\s*(usa|u\.s\.a\.?)\s*$", "", s)
    # Remove HTML entities
    s = s.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalize_title(title):
    """Normalize title for comparison."""
    if not title:
        return ""
    s = title.lower().strip()
    s = s.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
    # Remove common suffixes like "| Cozymeal™", "- Eventbrite"
    s = re.sub(r"\s*[|–-]\s*(cozymeal|eventbrite|meetup|sulekha).*$", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def title_similarity(t1, t2):
    """Fuzzy title match ratio."""
    n1 = normalize_title(t1)
    n2 = normalize_title(t2)
    if not n1 or not n2:
        return 0.0
    return SequenceMatcher(None, n1, n2).ratio()


# ── Scoring ──────────────────────────────────────────────────────────────
def completeness_score(event):
    """Score how complete an event record is. Higher = keep."""
    score = 0
    if event.get("image_url"):
        score += 3
    if event.get("organizer"):
        score += 2
    desc = event.get("description") or ""
    score += min(len(desc) / 100, 3)  # up to 3 points for description length
    long_desc = event.get("long_description") or ""
    score += min(len(long_desc) / 200, 2)
    if event.get("ticket_url"):
        score += 1
    if event.get("price_range"):
        score += 1
    if event.get("latitude") and event.get("longitude"):
        score += 1
    # Prefer eventbrite > sulekha > allevents > meetup
    source_pref = {"eventbrite": 2, "sulekha": 1.5, "meetup": 1, "allevents": 0.5}
    score += source_pref.get(event.get("source", ""), 0)
    return score


# ── Main ─────────────────────────────────────────────────────────────────
def main():
    print(f"{'='*60}")
    print(f"Event Deduplication — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print(f"  Date filter: >= {TODAY}")
    print(f"{'='*60}\n")

    # 1) Load all future events
    print("── Loading future events ──")
    all_events = []
    offset = 0
    while True:
        page = sb_get("events", {
            "select": "id,title,date,venue_name,source,organizer,description,long_description,"
                      "image_url,ticket_url,price_range,latitude,longitude,content_fingerprint",
            "date": f"gte.{TODAY}",
            "order": "date.asc,venue_name.asc",
        }, range_header=f"{offset}-{offset+999}")
        if not page or isinstance(page, dict):
            break
        all_events.extend(page)
        if len(page) < 1000:
            break
        offset += 1000

    print(f"  Total future events: {len(all_events)}")

    # 2) Group by (date, normalized venue)
    print("\n── Grouping by date + venue ──")
    groups = defaultdict(list)
    skipped_empty_venue = 0
    for e in all_events:
        vn = normalize_venue(e.get("venue_name"))
        if not vn:
            skipped_empty_venue += 1
            continue
        key = (e["date"], vn)
        groups[key].append(e)

    multi_groups = {k: v for k, v in groups.items() if len(v) > 1}
    print(f"  Unique (date, venue) groups: {len(groups)}")
    print(f"  Groups with >1 event: {len(multi_groups)}")
    print(f"  Skipped (empty venue): {skipped_empty_venue}")

    # 3) Within each group, find duplicates using fuzzy title matching
    print("\n── Finding duplicates ──")
    to_delete = []
    dup_groups_found = 0

    for (date, venue), events in sorted(multi_groups.items()):
        # Build clusters of similar titles within this group
        clusters = []  # list of lists of events
        used = set()

        for i, e1 in enumerate(events):
            if i in used:
                continue
            cluster = [e1]
            used.add(i)
            for j, e2 in enumerate(events):
                if j in used:
                    continue
                sim = title_similarity(e1["title"], e2["title"])
                if sim >= TITLE_SIMILARITY_THRESHOLD:
                    cluster.append(e2)
                    used.add(j)
                # Also catch exact fingerprint matches
                elif (e1.get("content_fingerprint") and
                      e1["content_fingerprint"] == e2.get("content_fingerprint")):
                    cluster.append(e2)
                    used.add(j)
            if len(cluster) > 1:
                clusters.append(cluster)

        # For each cluster, keep the best and mark rest for deletion
        for cluster in clusters:
            dup_groups_found += 1
            scored = [(completeness_score(e), e) for e in cluster]
            scored.sort(key=lambda x: x[0], reverse=True)
            keeper = scored[0][1]
            dupes = [e for _, e in scored[1:]]

            print(f"  {date} | {venue}:")
            print(f"    KEEP: [{keeper['source']}] {keeper['title'][:65]} (score={scored[0][0]:.1f})")
            for _, e in scored[1:]:
                s = completeness_score(e)
                print(f"    DEL:  [{e['source']}] {e['title'][:65]} (score={s:.1f})")
                to_delete.append(e["id"])

    # 4) Also catch exact content_fingerprint duplicates across ALL events
    # (same fingerprint = exact same content, regardless of venue normalization)
    print("\n── Checking fingerprint duplicates ──")
    fp_groups = defaultdict(list)
    for e in all_events:
        fp = e.get("content_fingerprint")
        if fp:
            fp_groups[fp].append(e)

    fp_dupes = 0
    already_deleting = set(to_delete)
    for fp, events in fp_groups.items():
        if len(events) <= 1:
            continue
        # Filter out ones already marked for deletion
        remaining = [e for e in events if e["id"] not in already_deleting]
        if len(remaining) <= 1:
            continue
        scored = [(completeness_score(e), e) for e in remaining]
        scored.sort(key=lambda x: x[0], reverse=True)
        for _, e in scored[1:]:
            fp_dupes += 1
            to_delete.append(e["id"])
            already_deleting.add(e["id"])
            print(f"  FP dup: [{e['source']}] {e['title'][:60]} (fp={fp[:16]})")

    print(f"  Fingerprint-only duplicates: {fp_dupes}")

    # 5) Delete
    to_delete = list(set(to_delete))  # dedupe the delete list itself
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total events checked: {len(all_events)}")
    print(f"  Duplicate groups found: {dup_groups_found}")
    print(f"  Events to delete: {len(to_delete)}")
    print(f"{'='*60}")

    if not to_delete:
        print("\nNo duplicates found. Done.")
        return

    if DRY_RUN:
        print(f"\n  DRY RUN — would delete {len(to_delete)} events. Rerun without --dry-run to execute.")
        return

    # Delete in batches (URL length limit)
    print(f"\n── Deleting {len(to_delete)} duplicates ──")
    deleted = 0
    BATCH = 50
    for i in range(0, len(to_delete), BATCH):
        batch = to_delete[i:i+BATCH]
        n = sb_delete(batch)
        deleted += n
        print(f"  Batch {i//BATCH + 1}: deleted {n}")

    print(f"\n✅ Done. Deleted {deleted} duplicate events.")


if __name__ == "__main__":
    main()
