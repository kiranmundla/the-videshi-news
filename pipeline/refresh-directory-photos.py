#!/usr/bin/env python3
"""Refresh directory listing photos via fresh Places references.

Two queues, processed in order:
  A) LEGACY — image_url is still a live maps.googleapis.com URL. Stale
     references serve Google's red-X placeholder graphic, so these are
     actively wrong covers.
  B) RESTORE — google_place_id present but image_url IS NULL. The
     2026-10-14 directory-photo repair nulled ~2,860 rotten legacy covers;
     the old version of this script (selection = image_url LIKE
     maps.googleapis.com) could never revisit them. Restored gradually
     here, most-visible listings first (review_count, then rating).

For each listing: fetch fresh photo references (Places API New, details
call), then hand the first photo to photo_rehost.rehost_v1_photos, which
downloads it, rejects Google's placeholder bytes, uploads to the
directory-photos bucket, and returns OUR durable URL for image_url.
Nothing is ever stored as a live Google URL; a failed/placeholder photo
leaves the listing imageless and queued for a later run.

Budget: every Places call goes through places_budget. This script
registers as consumer "photo_refresh" (cap 30 calls/day inside the shared
90/day total; ~2 calls per restored cover). It runs Sun 04:00, after the
daily 02:00 expansion, and only spends leftover budget — check_budget
stops the run cleanly when the day is spent, so kids (20) and directory
expansion (70) are never starved.
"""
import argparse, os, sys, time, requests
from places_budget import (check_budget, record_call, budget_remaining,
                           set_consumer, get_consumer_usage)
from photo_rehost import rehost_v1_photos  # download + validate + bucket-upload
import atexit as _atexit
def _budget_report():
    u, l = __import__("places_budget").get_usage()
    if u > 0: print(f"Places API budget: {u}/{l} calls used today")
_atexit.register(_budget_report)

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
GOOGLE_KEY   = os.environ["GOOGLE_PLACES_API_KEY"]
BUCKET       = "directory-photos"
HEADERS      = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
SELECT       = "id,name,slug,google_place_id,image_url,rating,review_count"
CANDIDATE_CAP = 1000  # ids fetched per queue; the budget stops runs far earlier
SLEEP_BETWEEN = 0.3   # seconds between listings

def ensure_bucket():
    """Create storage bucket if it doesn't exist."""
    r = requests.post(f"{SUPABASE_URL}/storage/v1/bucket",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"id": BUCKET, "name": BUCKET, "public": True},
        timeout=10)
    if r.status_code in (200, 201):
        print(f"✅ Created bucket '{BUCKET}'")
    elif r.status_code == 409 or "already exists" in r.text.lower():
        # Supabase now answers HTTP 400 with a BucketAlreadyExists body.
        print(f"✅ Bucket '{BUCKET}' exists")
    else:
        print(f"⚠️  Bucket creation: {r.status_code} {r.text[:200]}")

def _fetch_queue(extra_params, order):
    """One candidate queue from directory_listings (retries twice)."""
    params = {
        "select": SELECT,
        "google_place_id": "not.is.null",
        "order": order,
        "limit": str(CANDIDATE_CAP),
    }
    params.update(extra_params)
    for attempt in range(3):
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/directory_listings",
                headers=HEADERS, params=params, timeout=20)
            if r.status_code == 200:
                return r.json()
            print(f"  ⚠️  Candidate fetch HTTP {r.status_code}: {r.text[:150]}")
        except Exception as e:
            print(f"  ⚠️  Candidate fetch retry {attempt+1}: {e}")
        time.sleep(5 * (attempt + 1))
    return []

def fetch_candidates():
    """Ordered (queue, listing) pairs: legacy first, then cover restores.

    Fetched once up front because fixing a row removes it from its queue —
    offset pagination over the shrinking set would skip rows.
    """
    legacy = _fetch_queue({"image_url": "like.*maps.googleapis.com*"}, "id.asc")
    restore = _fetch_queue({"image_url": "is.null"},
                           "review_count.desc.nullslast,rating.desc.nullslast,id.asc")
    return ([("legacy", row) for row in legacy] +
            [("restore", row) for row in restore])

def fetch_place_photos(place_id):
    """Fresh photo dicts for a place (Places API New details). 1 Places call.

    Returns the photos list (possibly empty), or None on HTTP failure."""
    r = requests.get(f"https://places.googleapis.com/v1/places/{place_id}",
        headers={"X-Goog-Api-Key": GOOGLE_KEY, "X-Goog-FieldMask": "photos"},
        timeout=15)
    record_call()
    if r.status_code != 200:
        print(f"details HTTP {r.status_code}", end=" ")
        return None
    return r.json().get("photos", [])

def update_listing(listing_id, new_image_url):
    """Update listing's image_url in DB."""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/directory_listings",
        headers={**HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
        params={"id": f"eq.{listing_id}"},
        json={"image_url": new_image_url},
        timeout=10
    )
    return r.status_code in (200, 204)

def process_listing(listing):
    """Restore one listing's cover through photo_rehost. True if fixed."""
    lid = listing["id"]
    print(f"  [{lid}] {listing['name'][:50]}...", end=" ", flush=True)
    photos = fetch_place_photos(listing["google_place_id"])
    if photos is None:
        print("❌ details call failed")
        return False
    if not photos:
        print("❌ place has no photos")
        return False
    # Download + placeholder-validate + bucket-upload; records its own
    # budget call and returns [] on failure/placeholder/budget-block.
    stem = listing.get("slug") or str(lid)
    urls = rehost_v1_photos(photos, stem, GOOGLE_KEY, max_photos=1, use_budget=True)
    if not urls:
        print("❌ photo download/placeholder/budget — left imageless")
        return False
    if update_listing(lid, urls[0]):
        print("✅ cover restored")
        return True
    print("❌ DB update failed")
    return False

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=None,
                    help="max listings to process this run (default: until budget/selection exhausted)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the candidate queues and exit (no Places calls, no writes)")
    args = ap.parse_args()

    set_consumer("photo_refresh")
    candidates = fetch_candidates()
    n_legacy = sum(1 for q, _ in candidates if q == "legacy")
    n_restore = len(candidates) - n_legacy
    print(f"Candidates: {n_legacy} legacy Google-URL covers, "
          f"{n_restore} nulled covers with place_id (restore queue)")

    if args.dry_run:
        for q, row in candidates[:10]:
            print(f"  [{q}] {row['name'][:60]} "
                  f"(rating={row.get('rating')}, reviews={row.get('review_count')})")
        print("Dry run — nothing processed.")
        return

    ensure_bucket()
    fixed = failed = processed = 0
    for queue, listing in candidates:
        if args.limit is not None and processed >= args.limit:
            print(f"--limit {args.limit} reached — stopping.")
            break
        # A listing costs up to 2 calls (details + media). If the shared
        # day or this consumer's cap can't cover a full listing, stop
        # cleanly; the rest stay queued for the next run.
        if not check_budget(2):
            print(f"Places budget stop after {processed} listings "
                  f"({budget_remaining()} shared calls left today, "
                  f"photo_refresh used {get_consumer_usage('photo_refresh')}). "
                  f"Remaining candidates stay queued.")
            break
        processed += 1
        try:
            ok = process_listing(listing)
        except Exception as e:
            print(f"❌ error: {e}")
            ok = False
        if ok:
            fixed += 1
        else:
            failed += 1
        time.sleep(SLEEP_BETWEEN)

    print(f"\n{'='*50}")
    print(f"Done! Processed: {processed}, Fixed: {fixed}, Failed: {failed}, "
          f"photo_refresh calls today: {get_consumer_usage('photo_refresh')}")

if __name__ == "__main__":
    main()
