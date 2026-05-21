#!/usr/bin/env python3
"""
Seed directory_listings from Google Places API.

Searches for Indian/desi businesses across major US metros and inserts
them into the Supabase directory_listings table.
"""

import os
import re
import sys
import json
import time
import requests
from typing import Optional

# ---------- Configuration ----------

def load_env():
    env = {}
    for path in [os.path.expanduser("~/.env.supabase"), os.path.expanduser("~/workspace/.env.supabase")]:
        if os.path.exists(path):
            for line in open(path):
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k] = v
    return env

ENV = load_env()
GOOGLE_API_KEY = ENV.get("GOOGLE_PLACES_API_KEY", "")
SUPABASE_URL = ENV["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]

if not GOOGLE_API_KEY:
    print("ERROR: GOOGLE_PLACES_API_KEY not found in env files")
    sys.exit(1)

SUPABASE_HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}

# ---------- Metro areas ----------

METROS = {
    "Bay Area":  {"lat": 37.5485, "lng": -121.9886},
    "NYC":       {"lat": 40.7128, "lng": -74.0060},
    "Chicago":   {"lat": 41.8781, "lng": -87.6298},
    "Houston":   {"lat": 29.7604, "lng": -95.3698},
    "Dallas":    {"lat": 32.7767, "lng": -96.7970},
    "LA":        {"lat": 34.0522, "lng": -118.2437},
    "Seattle":   {"lat": 47.6062, "lng": -122.3321},
    "DC":        {"lat": 38.9072, "lng": -77.0369},
    "Boston":    {"lat": 42.3601, "lng": -71.0589},
    "Atlanta":   {"lat": 33.7490, "lng": -84.3880},
}

# ---------- Category keywords ----------

CATEGORY_KEYWORDS = {
    "Doctors & Healthcare": [
        "indian doctor",
        "desi physician",
        "ayurvedic doctor",
        "indian dentist",
    ],
    "Attorneys & Immigration": [
        "indian attorney",
        "immigration lawyer indian",
        "desi lawyer",
    ],
    "Real Estate": [
        "indian real estate agent",
        "desi realtor",
    ],
    "Tax & Accounting": [
        "indian CPA",
        "indian tax accountant",
        "FBAR tax preparer",
    ],
    "Catering & Food": [
        "indian catering",
        "desi catering",
        # Skip "indian restaurant" — too many results
    ],
    "Yoga & Wellness": [
        "yoga studio indian",
        "ayurveda center",
        "indian yoga instructor",
    ],
    "Beauty & Grooming": [
        "indian salon",
        "threading salon",
        "mehndi artist",
        "indian barber",
    ],
    "Education & Tutoring": [
        "indian tutor",
        "hindi classes",
        "indian music teacher",
        "carnatic music",
    ],
    "Religious Services": [
        "hindu priest",
        "pandit",
        "indian astrologer",
        "puja services",
    ],
    "Home Services": [
        "indian handyman",
        "desi contractor",
        "indian electrician",
    ],
}

# ---------- Helpers ----------

def generate_slug(name: str, city: str) -> str:
    """Generate a URL-safe slug from name + city."""
    raw = f"{name} {city}".lower()
    raw = re.sub(r"[^a-z0-9\s-]", "", raw)
    raw = re.sub(r"\s+", "-", raw.strip())
    raw = re.sub(r"-+", "-", raw)
    return raw[:80].rstrip("-")


def parse_address(formatted_address: str):
    """Extract city, state, zip from a formatted Google address."""
    city = state = zip_code = None
    parts = [p.strip() for p in formatted_address.split(",")]
    # Typical format: "123 Main St, City, ST 12345, USA"
    if len(parts) >= 3:
        city = parts[-3] if len(parts) >= 4 else parts[-2]
        state_zip = parts[-2] if len(parts) >= 4 else parts[-1]
        # Strip country from last part
        state_zip = state_zip.replace("USA", "").replace("US", "").strip()
        m = re.match(r"([A-Z]{2})\s*(\d{5})?", state_zip)
        if m:
            state = m.group(1)
            zip_code = m.group(2)
    elif len(parts) == 2:
        city = parts[0]
        m = re.match(r"([A-Z]{2})\s*(\d{5})?", parts[1].replace("USA", "").strip())
        if m:
            state = m.group(1)
            zip_code = m.group(2)
    return city, state, zip_code


def get_photo_url(photo_ref: str, max_width: int = 800) -> str:
    """Build a Google Places photo URL."""
    return (
        f"https://maps.googleapis.com/maps/api/place/photo"
        f"?maxwidth={max_width}&photo_reference={photo_ref}&key={GOOGLE_API_KEY}"
    )


# ---------- API calls ----------

def text_search(query: str, lat: float, lng: float, radius: int = 50000, page_token: Optional[str] = None) -> dict:
    """Google Places Text Search."""
    params = {
        "query": query,
        "location": f"{lat},{lng}",
        "radius": radius,
        "key": GOOGLE_API_KEY,
    }
    if page_token:
        params["pagetoken"] = page_token
    r = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json", params=params)
    return r.json()


def place_details(place_id: str) -> dict:
    """Google Places Details."""
    fields = "name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,photos,geometry,types,opening_hours"
    params = {
        "place_id": place_id,
        "fields": fields,
        "key": GOOGLE_API_KEY,
    }
    r = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params=params)
    return r.json()


# ---------- Insert into Supabase ----------

def upsert_listing(listing: dict):
    """Upsert a single listing into directory_listings via Supabase REST."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/directory_listings",
        headers=SUPABASE_HEADERS,
        json=listing,
    )
    if r.status_code >= 400:
        # Check for constraint violation (duplicate)
        if r.status_code == 409 or "duplicate" in r.text.lower():
            return "skipped_dup"
        print(f"  ERROR inserting {listing.get('name', '?')}: {r.status_code} {r.text[:200]}")
        return "error"
    return "ok"


# ---------- Main pipeline ----------

def process_place(place: dict, category: str) -> Optional[dict]:
    """Convert a Google Places result into a directory_listing row."""
    place_id = place.get("place_id")
    if not place_id:
        return None

    # Get detailed info
    time.sleep(0.1)
    details_resp = place_details(place_id)
    if details_resp.get("status") != "OK":
        return None

    result = details_resp.get("result", {})
    name = result.get("name", place.get("name", ""))
    address = result.get("formatted_address", "")
    phone = result.get("formatted_phone_number")
    website = result.get("website")
    rating = result.get("rating")
    review_count = result.get("user_ratings_total", 0)
    geometry = result.get("geometry", {}).get("location", {})
    lat = geometry.get("lat")
    lng = geometry.get("lng")

    city, state, zip_code = parse_address(address)

    # Get up to 3 photos
    photos = []
    photo_refs = result.get("photos", [])[:3]
    for p in photo_refs:
        ref = p.get("photo_reference")
        if ref:
            photos.append(get_photo_url(ref))

    # Opening hours
    hours = {}
    opening_hours = result.get("opening_hours", {})
    weekday_text = opening_hours.get("weekday_text", [])
    for line in weekday_text:
        parts = line.split(": ", 1)
        if len(parts) == 2:
            hours[parts[0]] = parts[1]

    slug = generate_slug(name, city or "")

    return {
        "name": name,
        "category": category,
        "description": None,
        "phone": phone,
        "website": website,
        "address": address,
        "city": city,
        "state": state,
        "zip": zip_code,
        "latitude": lat,
        "longitude": lng,
        "image_url": photos[0] if photos else None,
        "photos": json.dumps(photos),
        "rating": rating,
        "review_count": review_count,
        "google_place_id": place_id,
        "hours": json.dumps(hours) if hours else None,
        "source": "google_places",
        "slug": slug,
    }


def seed_directory(metros=None, categories=None, max_per_keyword_city=20):
    """Main seeding function."""
    target_metros = metros or list(METROS.keys())
    target_cats = categories or list(CATEGORY_KEYWORDS.keys())

    total_inserted = 0
    total_skipped = 0
    total_errors = 0
    seen_place_ids = set()

    # Load existing place IDs from DB to skip
    print("Loading existing listings from DB...")
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/directory_listings?select=google_place_id",
        headers={
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        },
    )
    if r.status_code == 200:
        for row in r.json():
            if row.get("google_place_id"):
                seen_place_ids.add(row["google_place_id"])
        print(f"  Found {len(seen_place_ids)} existing listings")

    for category in target_cats:
        keywords = CATEGORY_KEYWORDS.get(category, [])
        print(f"\n{'='*60}")
        print(f"Category: {category}")
        print(f"{'='*60}")

        for keyword in keywords:
            for metro_name in target_metros:
                metro = METROS[metro_name]
                print(f"\n  Searching '{keyword}' in {metro_name}...")

                try:
                    resp = text_search(keyword, metro["lat"], metro["lng"])
                except Exception as e:
                    print(f"    Search error: {e}")
                    continue

                if resp.get("status") not in ("OK", "ZERO_RESULTS"):
                    print(f"    API error: {resp.get('status')} - {resp.get('error_message', '')}")
                    continue

                results = resp.get("results", [])[:max_per_keyword_city]
                print(f"    Found {len(results)} results")

                for i, place in enumerate(results):
                    pid = place.get("place_id")
                    if pid in seen_place_ids:
                        total_skipped += 1
                        continue

                    seen_place_ids.add(pid)

                    try:
                        listing = process_place(place, category)
                    except Exception as e:
                        print(f"    Error processing place: {e}")
                        total_errors += 1
                        continue

                    if not listing:
                        total_errors += 1
                        continue

                    status = upsert_listing(listing)
                    if status == "ok":
                        total_inserted += 1
                        print(f"    ✓ {listing['name']} ({listing['city']}, {listing['state']})")
                    elif status == "skipped_dup":
                        total_skipped += 1
                    else:
                        total_errors += 1

                    time.sleep(0.1)  # Rate limit

    print(f"\n{'='*60}")
    print(f"DONE: {total_inserted} inserted, {total_skipped} skipped, {total_errors} errors")
    print(f"{'='*60}")

    return total_inserted


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed desi business directory from Google Places")
    parser.add_argument("--metros", nargs="+", help="Specific metros to search (default: all)")
    parser.add_argument("--categories", nargs="+", help="Specific categories (default: all)")
    parser.add_argument("--max-per-keyword", type=int, default=20, help="Max results per keyword per city")
    args = parser.parse_args()

    seed_directory(
        metros=args.metros,
        categories=args.categories,
        max_per_keyword_city=args.max_per_keyword,
    )
