#!/usr/bin/env python3
"""Refresh expired Google Places photo references for directory listings.

Fetches fresh photo_references via Places API, downloads the first photo,
uploads to Supabase storage (permanent URLs), and updates the listing.
"""
import os, sys, json, time, requests, hashlib
from places_budget import check_budget, record_call, budget_remaining  # daily cost guard
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

BATCH_SIZE = 50
SLEEP_BETWEEN = 0.3  # seconds between API calls

def ensure_bucket():
    """Create storage bucket if it doesn't exist."""
    r = requests.post(f"{SUPABASE_URL}/storage/v1/bucket",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"id": BUCKET, "name": BUCKET, "public": True},
        timeout=10)
    if r.status_code in (200, 201):
        print(f"✅ Created bucket '{BUCKET}'")
    elif r.status_code == 409:
        print(f"✅ Bucket '{BUCKET}' exists")
    else:
        print(f"⚠️  Bucket creation: {r.status_code} {r.text[:200]}")

def get_fresh_photo_name(place_id):
    """Get fresh photo resource name from Places API (New)."""
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    r = requests.get(url, headers={
        "X-Goog-Api-Key": GOOGLE_KEY,
        "X-Goog-FieldMask": "photos",
    }, timeout=15)
    if r.status_code != 200:
        return None
    data = r.json()
    photos = data.get("photos", [])
    if not photos:
        return None
    return photos[0]["name"]  # e.g. "places/PLACE_ID/photos/PHOTO_REF"

def download_photo(photo_name, max_width=800):
    """Download photo bytes via Places API (New) media endpoint."""
    url = f"https://places.googleapis.com/v1/{photo_name}/media"
    r = requests.get(url, params={
        "maxWidthPx": max_width,
        "skipHttpRedirect": "true",
    }, headers={
        "X-Goog-Api-Key": GOOGLE_KEY,
    }, timeout=15)
    if r.status_code != 200:
        return None, None
    photo_uri = r.json().get("photoUri")
    if not photo_uri:
        return None, None
    # Download the actual image from the URI
    img_r = requests.get(photo_uri, timeout=15)
    if img_r.status_code == 200 and img_r.headers.get("content-type", "").startswith("image"):
        return img_r.content, img_r.headers["content-type"]
    return None, None

def upload_to_supabase(listing_id, image_bytes, content_type):
    """Upload image to Supabase storage, return public URL."""
    ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]
    path = f"{listing_id}.{ext}"
    
    r = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{path}",
        headers={
            **HEADERS,
            "Content-Type": content_type,
            "x-upsert": "true",
        },
        data=image_bytes,
        timeout=15
    )
    if r.status_code in (200, 201):
        return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{path}"
    print(f"    ⚠️  Upload failed: {r.status_code} {r.text[:200]}")
    return None

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

def main():
    ensure_bucket()
    
    # Fetch listings with expired Google photo URLs
    offset = 0
    total_fixed = 0
    total_failed = 0
    total_skipped = 0
    
    while True:
        for attempt in range(3):
            try:
                r = requests.get(f"{SUPABASE_URL}/rest/v1/directory_listings",
                    headers=HEADERS,
                    params={
                        "select": "id,name,google_place_id,image_url",
                        "google_place_id": "not.is.null",
                        "image_url": "like.*maps.googleapis.com*",
                        "order": "id",
                        "limit": str(BATCH_SIZE),
                        "offset": str(offset)
                    },
                    timeout=15)
                listings = r.json()
                break
            except Exception as e:
                if attempt < 2:
                    print(f"  ⚠️  Batch fetch retry {attempt+1}: {e}")
                    time.sleep(5 * (attempt + 1))
                else:
                    print(f"  ❌ Batch fetch failed after 3 tries: {e}")
                    listings = None
        
        if listings is None:
            # Skip this batch, try next
            offset += BATCH_SIZE
            if offset > 10000:  # safety cap
                break
            continue
        if not listings:
            break
        
        print(f"\n--- Batch at offset {offset}: {len(listings)} listings ---")
        
        for listing in listings:
            lid = listing["id"]
            name = listing["name"][:50]
            place_id = listing["google_place_id"]
            
            if not place_id:
                total_skipped += 1
                continue
            
            # Already has a Supabase URL? Skip
            if listing.get("image_url", "").startswith(SUPABASE_URL):
                total_skipped += 1
                continue
            
            print(f"  [{lid}] {name}...", end=" ", flush=True)
            
            try:
                # Get fresh photo name
                ref = get_fresh_photo_name(place_id)
                if not ref:
                    print("❌ no photos")
                    total_failed += 1
                    time.sleep(SLEEP_BETWEEN)
                    continue
                
                # Download
                img_bytes, ctype = download_photo(ref)
                if not img_bytes:
                    print("❌ download failed")
                    total_failed += 1
                    time.sleep(SLEEP_BETWEEN)
                    continue
                
                # Upload to Supabase
                pub_url = upload_to_supabase(lid, img_bytes, ctype)
                if not pub_url:
                    total_failed += 1
                    time.sleep(SLEEP_BETWEEN)
                    continue
                
                # Update DB
                if update_listing(lid, pub_url):
                    print(f"✅ {len(img_bytes)//1024}KB")
                    total_fixed += 1
                else:
                    print("❌ DB update failed")
                    total_failed += 1
            except Exception as e:
                print(f"❌ error: {e}")
                total_failed += 1
            
            time.sleep(SLEEP_BETWEEN)
        
        offset += BATCH_SIZE
    
    print(f"\n{'='*50}")
    print(f"Done! Fixed: {total_fixed}, Failed: {total_failed}, Skipped: {total_skipped}")

if __name__ == "__main__":
    main()
