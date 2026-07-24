#!/usr/bin/env python3
"""
Deduplicate events in the Videshi events table.

Groups future events by (date, normalized_venue, city, state) and uses fuzzy title
matching to identify duplicates within each group. Keeps the event with
the most complete data and deletes the rest.

Usage:
    python3 -u pipeline/dedup-events.py              # live run
    python3 -u pipeline/dedup-events.py --dry-run    # preview only
"""

import json, os, re, subprocess, sys, unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher

# ── Config ───────────────────────────────────────────────────────────────
DRY_RUN = "--dry-run" in sys.argv
TITLE_SIMILARITY_THRESHOLD = 0.70
SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Venues that are placeholders, not real locations — skip grouping on these
GENERIC_VENUES = frozenset([
    "location provided after booking",
    "refer eventbrite ticket link",
    "regus center",
    "online",
    "virtual",
    "tbd",
    "to be announced",
])

# ── Supabase helpers ─────────────────────────────────────────────────────
def sb_get(endpoint, params, range_header=None):
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
        print(f"  WARNING: Failed to parse response: {r.stdout[:200]}")
        return []


def sb_delete(ids):
    if not ids:
        return 0
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
        print(f"  WARNING: Delete failed (HTTP {code}) for {len(ids)} events")
        return 0


# ── Normalization ────────────────────────────────────────────────────────
def normalize_venue(name):
    if not name:
        return ""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r",\s*(usa|u\.s\.a\.?)\s*$", "", s)
    s = s.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
    s = re.sub(r"\s+", " ", s).strip()
    return s


def strip_title_suffix(title):
    """Strip location, platform, and date suffixes for comparison."""
    if not title:
        return ""
    s = title.lower().strip()
    s = s.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
    # Strip trailing platform/org markers
    s = re.sub(r"\s*[|–]\s*(cozymeal|eventbrite|meetup|sulekha).*$", "", s, flags=re.I)
    # Strip trailing "in City, ST" patterns
    s = re.sub(r"\s+in\s+[A-Za-z\s,\.]+,\s*[A-Z]{2}\b.*$", "", s, flags=re.I)
    # Strip trailing "@ Venue"
    s = re.sub(r"\s*@\s*\S.*$", "", s)
    # Strip trailing " | City | Date" chains
    s = re.sub(r"\s*\|\s*[A-Za-z]+\s*\|.*$", "", s)
    # Strip date patterns
    s = re.sub(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}(st|nd|rd|th)?\b", "", s, flags=re.I)
    # Strip day-of-week prefixes
    s = re.sub(r"^(monday|tuesday|wednesday|thursday|friday|saturday|sunday),?\s*", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def titles_differ_only_in_time(t1, t2):
    """True if titles are identical except for time patterns (different showtimes)."""
    time_pat = re.compile(r'\b\d{1,2}:\d{2}\s*(am|pm)?\b', re.I)
    s1 = time_pat.sub("TIME", t1.lower().strip())
    s2 = time_pat.sub("TIME", t2.lower().strip())
    # Both must have had times, and replacing times makes them equal
    return s1 == s2 and time_pat.search(t1.lower()) and time_pat.search(t2.lower())


def title_similarity(t1, t2):
    n1 = strip_title_suffix(t1)
    n2 = strip_title_suffix(t2)
    if not n1 or not n2:
        return 0.0
    return SequenceMatcher(None, n1, n2).ratio()


# ── Scoring ──────────────────────────────────────────────────────────────
def completeness_score(event):
    score = 0
    if event.get("image_url"):
        score += 3
    if event.get("organizer"):
        score += 2
    desc = event.get("description") or ""
    score += min(len(desc) / 100, 3)
    long_desc = event.get("long_description") or ""
    score += min(len(long_desc) / 200, 2)
    if event.get("ticket_url"):
        score += 1
    if event.get("price_range"):
        score += 1
    if event.get("latitude") and event.get("longitude"):
        score += 1
    source_pref = {"eventbrite": 2, "sulekha": 1.5, "web": 1.5, "meetup": 1, "allevents": 0.5, "ticketmaster": 0.5}
    score += source_pref.get(event.get("source", ""), 0)
    return score


# ── Main ─────────────────────────────────────────────────────────────────
def main():
    print(f"{'='*60}")
    print(f"Event Deduplication — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print(f"  Date filter: >= {TODAY}")
    print(f"  Title similarity threshold: {TITLE_SIMILARITY_THRESHOLD}")
    print(f"{'='*60}\n")

    # 1) Load all future events
    print("── Loading future events ──")
    all_events = []
    offset = 0
    while True:
        page = sb_get("events", {
            "select": "id,title,date,venue_name,city,state,source,organizer,description,"
                      "long_description,image_url,ticket_url,price_range,latitude,longitude,"
                      "content_fingerprint",
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

    # 2) Group by (date, normalized venue, city, state)
    print("\n── Grouping by date + venue + city ──")
    groups = defaultdict(list)
    skipped_empty = 0
    skipped_generic = 0
    for e in all_events:
        vn = normalize_venue(e.get("venue_name"))
        if not vn:
            skipped_empty += 1
            continue
        if vn in GENERIC_VENUES:
            skipped_generic += 1
            continue
        city = (e.get("city") or "").strip().lower()
        state = (e.get("state") or "").strip().lower()
        key = (e["date"], vn, city, state)
        groups[key].append(e)

    multi_groups = {k: v for k, v in groups.items() if len(v) > 1}
    print(f"  Unique groups: {len(groups)}")
    print(f"  Groups with >1 event: {len(multi_groups)}")
    print(f"  Skipped (empty venue): {skipped_empty}")
    print(f"  Skipped (generic venue): {skipped_generic}")

    # 3) Find duplicates within each group
    print("\n── Finding duplicates ──")
    to_delete = []
    dup_groups_found = 0

    for (date, venue, city, state), events in sorted(multi_groups.items()):
        clusters = []
        used = set()

        for i, e1 in enumerate(events):
            if i in used:
                continue
            cluster = [e1]
            used.add(i)
            for j, e2 in enumerate(events):
                if j in used:
                    continue
                # Exact fingerprint match = definite duplicate
                if (e1.get("content_fingerprint") and
                        e1["content_fingerprint"] == e2.get("content_fingerprint")):
                    cluster.append(e2)
                    used.add(j)
                    continue
                # Skip if titles only differ by showtime
                if titles_differ_only_in_time(e1["title"], e2["title"]):
                    continue
                # Fuzzy title match on stripped titles
                sim = title_similarity(e1["title"], e2["title"])
                if sim >= TITLE_SIMILARITY_THRESHOLD:
                    cluster.append(e2)
                    used.add(j)

            if len(cluster) > 1:
                clusters.append(cluster)

        for cluster in clusters:
            dup_groups_found += 1
            scored = [(completeness_score(e), e) for e in cluster]
            scored.sort(key=lambda x: x[0], reverse=True)
            keeper = scored[0][1]
            loc = f" ({city}, {state})" if city else ""

            print(f"  {date} | {venue}{loc}:")
            print(f"    KEEP: [{keeper['source']}] {keeper['title'][:70]} (score={scored[0][0]:.1f})")
            for sc, e in scored[1:]:
                print(f"    DEL:  [{e['source']}] {e['title'][:70]} (score={sc:.1f})")
                to_delete.append(e["id"])

    # 4) Fingerprint duplicates across ALL events
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

    # 5) Summary and delete
    to_delete = list(set(to_delete))
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

    print(f"\n── Deleting {len(to_delete)} duplicates ──")
    deleted = 0
    BATCH = 50
    for i in range(0, len(to_delete), BATCH):
        batch = to_delete[i:i+BATCH]
        n = sb_delete(batch)
        deleted += n
        print(f"  Batch {i//BATCH + 1}: deleted {n}")

    print(f"\n  Done. Deleted {deleted} duplicate events.")


if __name__ == "__main__":
    main()
