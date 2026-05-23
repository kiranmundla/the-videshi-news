#!/usr/bin/env python3
"""
Seed restaurants table from Google Places API (legacy).

Searches for Indian/South Asian restaurants across major US metros
and inserts them into the Supabase restaurants table.
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
    print("ERROR: GOOGLE_PLACES_API_KEY not found")
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

# ---------- Search queries with cuisine mapping ----------

SEARCH_QUERIES = [
    ("indian restaurant",        "Pan-Indian"),
    ("south indian restaurant",  "South Indian"),
    ("north indian restaurant",  "North Indian"),
    ("pakistani restaurant",     "Pakistani"),
    ("bangladeshi restaurant",   "Bangladeshi"),
    ("nepali restaurant",        "Nepali"),
    ("sri lankan restaurant",    "Sri Lankan"),
    ("biryani restaurant",       "Biryani & Kebabs"),
    ("dosa restaurant",          "South Indian"),
]

# ---------- Helpers ----------

def generate_slug(name: str, city: str) -> str:
    raw = f"{name} {city}".lower()
    raw = re.sub(r"[^a-z0-9\s-]", "", raw)
    raw = re.sub(r"\s+", "-", raw.strip())
    raw = re.sub(r"-+", "-", raw)
    return raw[:100].rstrip("-")


def parse_address(formatted_address: str):
    city = state = zip_code = None
    parts = [p.strip() for p in formatted_address.split(",")]
    if len(parts) >= 3:
        city = parts[-3] if len(parts) >= 4 else parts[-2]
        state_zip = parts[-2] if len(parts) >= 4 else parts[-1]
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


def detect_cuisine(query_cuisine: str, name: str, types: list) -> str:
    name_lower = name.lower()
    if any(k in name_lower for k in ["dosa", "idli", "uttapam", "saravana", "udupi", "chettinad", "madras"]):
        return "South Indian"
    if any(k in name_lower for k in ["biryani", "kebab", "tandoor", "mughlai"]):
        return "Biryani & Kebabs"
    if any(k in name_lower for k in ["chaat", "pani puri", "bhel"]):
        return "Street Food"
    if any(k in name_lower for k in ["pakistani", "lahore", "karachi", "peshawar"]):
        return "Pakistani"
    if any(k in name_lower for k in ["nepali", "himalayan", "sherpa", "kathmandu", "everest"]):
        return "Nepali"
    if any(k in name_lower for k in ["bengali", "bangladesh", "dhaka"]):
        return "Bangladeshi"
    if any(k in name_lower for k in ["sri lankan", "ceylon"]):
        return "Sri Lankan"
    if any(k in name_lower for k in ["vegetarian", "veg ", "pure veg"]):
        return "Vegetarian Indian"
    if any(k in name_lower for k in ["indo-chinese", "indo chinese", "hakka", "manchurian"]):
        return "Indo-Chinese"
    return query_cuisine


def detect_vegetarian(name: str, types: list) -> bool:
    name_lower = name.lower()
    if any(k in name_lower for k in ["vegetarian", "veg ", "pure veg", "saravana", "udupi", "jain"]):
        return True
    if "vegetarian_restaurant" in types:
        return True
    return False


def get_photo_url(photo_ref: str, max_width: int = 800) -> str:
    return (
        f"https://maps.googleapis.com/maps/api/place/photo"
        f"?maxwidth={max_width}&photo_reference={photo_ref}&key={GOOGLE_API_KEY}"
    )


# ---------- Google Places API (Legacy) ----------

def text_search(query: str, lat: float, lng: float, radius: int = 50000, page_token: str = None) -> dict:
    params = {
        "query": query,
        "location": f"{lat},{lng}",
        "radius": radius,
        "key": GOOGLE_API_KEY,
    }
    if page_token:
        params["pagetoken"] = page_token
    r = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json", params=params, timeout=15)
    return r.json()


def place_details(place_id: str) -> dict:
    fields = "name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,photos,geometry,types,opening_hours,price_level"
    params = {
        "place_id": place_id,
        "fields": fields,
        "key": GOOGLE_API_KEY,
    }
    r = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params=params, timeout=15)
    return r.json()


# ---------- Process + Insert ----------

def process_place(place: dict, query_cuisine: str) -> Optional[dict]:
    place_id = place.get("place_id")
    if not place_id:
        return None

    # Fetch detailed info
    time.sleep(0.3)
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
    price_level = result.get("price_level")
    geometry = result.get("geometry", {}).get("location", {})
    lat = geometry.get("lat")
    lng = geometry.get("lng")
    types = result.get("types", [])

    city, state, zip_code = parse_address(address)
    cuisine = detect_cuisine(query_cuisine, name, types)
    vegetarian = detect_vegetarian(name, types)

    # Photos (up to 5)
    photos = []
    for p in result.get("photos", [])[:5]:
        ref = p.get("photo_reference")
        if ref:
            photos.append(get_photo_url(ref))

    # Hours
    hours = {}
    opening_hours = result.get("opening_hours", {})
    for line in opening_hours.get("weekday_text", []):
        parts = line.split(": ", 1)
        if len(parts) == 2:
            hours[parts[0]] = parts[1]

    # Delivery / dine_in from types
    delivery = "meal_delivery" in types or "delivery" in types
    dine_in = "restaurant" in types or "food" in types

    slug = generate_slug(name, city or "")

    return {
        "name": name,
        "slug": slug,
        "google_place_id": place_id,
        "cuisine": cuisine,
        "address": address,
        "city": city,
        "state": state,
        "zip": zip_code,
        "latitude": lat,
        "longitude": lng,
        "phone": phone,
        "website": website,
        "rating": float(rating) if rating else None,
        "review_count": review_count,
        "price_level": price_level,
        "image_url": photos[0] if photos else None,
        "photos": photos,
        "hours": hours if hours else None,
        "vegetarian_friendly": vegetarian,
        "delivery": delivery,
        "dine_in": dine_in if dine_in else True,
        "source": "google_places",
    }


def upsert_restaurant(row: dict):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/restaurants",
        headers=SUPABASE_HEADERS,
        json=row,
    )
    if r.status_code >= 400:
        if r.status_code == 409 or "duplicate" in r.text.lower():
            return "skipped_dup"
        print(f"  ERROR inserting {row.get('name', '?')}: {r.status_code} {r.text[:200]}")
        return "error"
    return None if r.status_code < 300 else "error"


# ---------- Main ----------

def seed_restaurants():
    total_inserted = 0
    total_skipped = 0
    total_errors = 0
    seen_place_ids = set()
    metro_counts = {m: 0 for m in METROS}

    # Load existing
    print("Loading existing restaurants from DB...")
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/restaurants?select=google_place_id&limit=5000",
        headers={
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        },
    )
    if r.status_code == 200:
        for row in r.json():
            if row.get("google_place_id"):
                seen_place_ids.add(row["google_place_id"])
        print(f"  Found {len(seen_place_ids)} existing restaurants\n")

    for metro_name, coords in METROS.items():
        print(f"\n{'='*60}")
        print(f"Metro: {metro_name}")
        print(f"{'='*60}")

        for query, default_cuisine in SEARCH_QUERIES:
            print(f"\n  Searching: '{query}'")

            try:
                resp = text_search(query, coords["lat"], coords["lng"])
            except Exception as e:
                print(f"    Search error: {e}")
                time.sleep(1)
                continue

            if resp.get("status") not in ("OK", "ZERO_RESULTS"):
                print(f"    API error: {resp.get('status')} - {resp.get('error_message', '')}")
                continue

            results = resp.get("results", [])[:20]
            print(f"    Found {len(results)} results")

            for place in results:
                pid = place.get("place_id")
                if pid in seen_place_ids:
                    total_skipped += 1
                    continue
                seen_place_ids.add(pid)

                try:
                    row = process_place(place, default_cuisine)
                except Exception as e:
                    print(f"    Error processing: {e}")
                    total_errors += 1
                    continue

                if not row:
                    total_errors += 1
                    continue

                status = upsert_restaurant(row)
                if status is None:
                    total_inserted += 1
                    metro_counts[metro_name] += 1
                    print(f"    ✓ {row['name']} ({row['city']}, {row['state']}) [{row['cuisine']}]")
                elif status == "skipped_dup":
                    total_skipped += 1
                else:
                    total_errors += 1

                time.sleep(0.5)

            time.sleep(0.3)

    print(f"\n{'='*60}")
    print(f"RESTAURANTS SEEDING COMPLETE")
    print(f"{'='*60}")
    print(f"Total inserted: {total_inserted}")
    print(f"Total skipped:  {total_skipped}")
    print(f"Total errors:   {total_errors}")
    print(f"\nPer metro:")
    for metro, count in metro_counts.items():
        print(f"  {metro}: {count}")
    print(f"{'='*60}")

    return total_inserted


if __name__ == "__main__":
    seed_restaurants()
