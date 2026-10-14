#!/usr/bin/env python3
"""
rehost-event-images.py — Sweep: re-host hotlinked event images into our own
Supabase storage and point the events table at the new URLs.

Uses pipeline/event_image_rehost.py (download via curl, magic-byte
validation, upload to article-images/events/). On any failure the event
keeps its original URL — nothing is ever blanked.

The original URL of every rewritten row is appended to
pipeline/reports/event-image-rehost-map.jsonl as
{"event_id", "source_url", "our_url"} so the change is reversible/auditable.

Resumable: rows already on our storage domain are skipped, and a local
URL cache dedupes posters shared by an event series.

Usage:
  python3 -u pipeline/rehost-event-images.py [--limit N] [--workers 4]
                                            [--upcoming-only] [--dry-run]

Stops early if storage uploads start failing consecutively (quota guard).
Env: source ~/workspace/.env.supabase first (script also self-loads it).
"""

import argparse
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import urlparse

sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from event_image_rehost import rehost_image, is_ours, SUPABASE_URL, SUPABASE_KEY  # noqa: E402

REST = f"{SUPABASE_URL}/rest/v1"
HEADERS = [
    "-H", f"apikey: {SUPABASE_KEY}",
    "-H", f"Authorization: Bearer {SUPABASE_KEY}",
]
MAP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "reports", "event-image-rehost-map.jsonl")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
MAX_CONSEC_UPLOAD_FAILURES = 8  # quota guard


def curl_json(args, timeout=60):
    r = subprocess.run(["curl", "-sS", "--max-time", str(timeout)] + args,
                       capture_output=True, text=True, timeout=timeout + 10)
    return r


def fetch_events():
    """All events with a non-null image_url, paged by id for stability."""
    rows, last_id = [], ""
    while True:
        url = (f"{REST}/events?select=id,title,date,image_url,source"
               f"&image_url=not.is.null&order=id.asc&limit=1000")
        if last_id:
            url += f"&id=gt.{last_id}"
        r = curl_json(["-g", url] + HEADERS)
        page = json.loads(r.stdout)
        if isinstance(page, dict):
            raise RuntimeError(f"events fetch failed: {r.stdout[:300]}")
        if not page:
            break
        rows.extend(page)
        last_id = page[-1]["id"]
        if len(page) < 1000:
            break
    return rows


def patch_rows(ids, new_url):
    """PATCH events id IN (ids) SET image_url=new_url. Chunks of 100.
    Returns True only if every chunk returned a 2xx."""
    ok_all = True
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        filt = "id=in.(" + ",".join(chunk) + ")"
        r = curl_json(["-g", "-X", "PATCH", f"{REST}/events?{filt}"] + HEADERS + [
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=minimal",
            "-d", json.dumps({"image_url": new_url}),
            "-o", "/dev/null", "-w", "%{http_code}"])
        code = (r.stdout or "").strip()
        if code not in ("200", "204"):
            print(f"  PATCH failed http-{code} for {len(chunk)} rows -> {new_url}")
            ok_all = False
    return ok_all


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0,
                    help="max unique image URLs to process (0 = no limit)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--upcoming-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="report counts only; no downloads/uploads/patches")
    args = ap.parse_args()

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing")
        return 1

    rows = fetch_events()
    todo = [r for r in rows if r.get("image_url") and not is_ours(r["image_url"])]
    print(f"events with image_url: {len(rows)}; not yet ours: {len(todo)}")

    # Group rows by unique image URL (series share posters -> one upload).
    groups = {}
    for r in todo:
        groups.setdefault(r["image_url"], []).append(r)
    print(f"unique hotlinked URLs: {len(groups)}")

    def group_key(item):
        url, grows = item
        dates = [g["date"] for g in grows if g.get("date")]
        upcoming = [d for d in dates if d >= TODAY]
        # Upcoming first (earliest upcoming date), then the rest (latest date).
        return (0, min(upcoming)) if upcoming else (1, "")

    items = sorted(groups.items(), key=group_key)
    if args.upcoming_only:
        items = [it for it in items
                 if any((g.get("date") or "") >= TODAY for g in it[1])]
        print(f"upcoming-only: {len(items)} URLs")
    if args.limit:
        items = items[:args.limit]
        print(f"limited to {len(items)} URLs")

    if args.dry_run:
        hosts = Counter(urlparse(u).netloc for u, _ in items)
        print("by host:", hosts.most_common(20))
        return 0

    os.makedirs(os.path.dirname(MAP_FILE), exist_ok=True)
    stats_host = defaultdict(Counter)
    total_bytes = 0
    rows_patched = 0
    consec_upload_fail = 0
    aborted = False
    done = 0

    def work(item):
        url, grows = item
        new_url, status, detail, nbytes = rehost_image(url, grows[0]["id"])
        return url, grows, new_url, status, detail, nbytes

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(work, it): it for it in items}
        for fut in as_completed(futures):
            url, grows, new_url, status, detail, nbytes = fut.result()
            host = urlparse(url).netloc or "(unknown)"
            done += 1
            if status in ("uploaded", "cached"):
                ids = [g["id"] for g in grows]
                if patch_rows(ids, new_url):
                    with open(MAP_FILE, "a") as f:
                        for g in grows:
                            f.write(json.dumps({
                                "event_id": g["id"], "source_url": url,
                                "our_url": new_url}) + "\n")
                    rows_patched += len(ids)
                    stats_host[host]["uploaded"] += 1
                    total_bytes += nbytes
                    consec_upload_fail = 0
                else:
                    stats_host[host]["patch-failed"] += 1
            elif status == "ours":
                stats_host[host]["ours"] += 1
            else:  # kept — original URL stays
                reason = detail.split(":")[0] if detail else "unknown"
                stats_host[host][f"kept:{reason}"] += 1
                if detail.startswith("upload:"):
                    consec_upload_fail += 1
                    if consec_upload_fail >= MAX_CONSEC_UPLOAD_FAILURES:
                        print(f"ABORT: {consec_upload_fail} consecutive upload "
                              "failures (possible storage quota) — stopping.")
                        aborted = True
                        for f2 in futures:
                            f2.cancel()
                        break
                else:
                    consec_upload_fail = 0
            if done % 100 == 0:
                print(f"  progress {done}/{len(items)} urls, "
                      f"{rows_patched} rows patched, "
                      f"{total_bytes/1e6:.1f} MB uploaded", flush=True)

    print("\n=== SUMMARY ===")
    print(f"URLs processed: {done}/{len(items)}"
          + (" (ABORTED EARLY)" if aborted else ""))
    print(f"Rows patched to our storage: {rows_patched}")
    print(f"Bytes uploaded this run: {total_bytes} ({total_bytes/1e6:.1f} MB)")
    for host in sorted(stats_host, key=lambda h: -sum(stats_host[h].values())):
        print(f"  {host}: {dict(stats_host[host])}")
    return 2 if aborted else 0


if __name__ == "__main__":
    sys.exit(main())
