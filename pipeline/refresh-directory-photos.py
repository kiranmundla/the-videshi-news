#!/usr/bin/env python3
"""Refresh expired Google Places photo references for directory listings.

Fetches fresh photo_references via Places API, downloads the first photo,
uploads to Supabase storage (permanent URLs), and updates the listing.
"""
import os, sys, json, time, requests, hashlib

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

def get_fresh_photo_ref(place_id):
    """Get fresh photo reference from Places API."""
    url = f"https://maps.googleapis.com/maps/api/place/details/json"
    r = requests.get(url, params={
        "place_id": place_id,
        "fields": "photos",
        "key": GOOGLE_KEY
    }, timeout=15)
    if r.status_code != 200:
        return None
    data = r.json()
    photos = data.get("result", {}).get("photos", [])
    if not photos:
        return None
    return photos[0]["photo_reference"]

def download_photo(photo_ref, max_width=800):
    """Download photo bytes from Google."""
    url = f"https://maps.googleapis.com/maps/api/place/photo"
    r = requests.get(url, params={
        "maxwidth": max_width,
        "photo_reference": photo_ref,
        "key": GOOGLE_KEY
    }, allow_redirects=True, timeout=15)
    if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
        return r.content, r.headers["content-type"]
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
            if offset > 5000:  # safety cap
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
                # Get fresh photo reference
                ref = get_fresh_photo_ref(place_id)
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
