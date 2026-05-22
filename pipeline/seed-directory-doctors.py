#!/usr/bin/env python3
"""
Seed additional doctor/healthcare specialist listings from Google Places API.
Searches for specific specialist types and sets subcategory accordingly.
"""

import os
import re
import json
import time
import requests
from typing import Optional

# ---------- Config ----------

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
SUPABASE_URL = ENV["SUPABASE_URL"]
SERVICE_KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
GOOGLE_API_KEY = ENV.get("GOOGLE_PLACES_API_KEY") or ENV.get("GOOGLE_API_KEY", "")
SUPABASE_HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

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

# Keywords mapped to subcategories
SPECIALIST_KEYWORDS = {
    "Urgent Care": [
        "indian urgent care",
        "south asian urgent care",
        "desi walk in clinic",
    ],
    "Dentist": [
        "indian dentist",
        "south asian dentist",
        "desi dental",
    ],
    "Pediatrician": [
        "indian pediatrician",
        "south asian pediatrician",
    ],
    "Dermatologist": [
        "indian dermatologist",
        "south asian dermatologist",
    ],
    "Cardiologist": [
        "indian cardiologist",
        "south asian cardiologist",
    ],
    "Ophthalmologist": [
        "indian eye doctor",
        "south asian ophthalmologist",
    ],
    "OB/GYN": [
        "indian ob gyn",
        "indian gynecologist",
        "south asian ob gyn",
    ],
    "Orthopedic": [
        "indian orthopedic doctor",
        "south asian orthopedic",
    ],
    "Psychiatrist / Mental Health": [
        "indian psychiatrist",
        "south asian therapist",
        "indian mental health",
    ],
    "Primary Care": [
        "indian family doctor",
        "indian primary care physician",
    ],
}


# ---------- Helpers ----------

def generate_slug(name: str, city: str) -> str:
    raw = f"{name} {city}".lower()
    raw = re.sub(r"[^a-z0-9\s-]", "", raw)
    raw = re.sub(r"\s+", "-", raw.strip())
    raw = re.sub(r"-+", "-", raw)
    return raw[:80].rstrip("-")


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


def get_photo_url(photo_ref: str, max_width: int = 800) -> str:
    return (
        f"https://maps.googleapis.com/maps/api/place/photo"
        f"?maxwidth={max_width}&photo_reference={photo_ref}&key={GOOGLE_API_KEY}"
    )


# ---------- API calls ----------

def text_search(query: str, lat: float, lng: float, radius: int = 50000) -> dict:
    params = {
        "query": query,
        "location": f"{lat},{lng}",
        "radius": radius,
        "key": GOOGLE_API_KEY,
    }
    r = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json", params=params)
    return r.json()


def place_details(place_id: str) -> dict:
    fields = "name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,photos,geometry,types,opening_hours"
    params = {
        "place_id": place_id,
        "fields": fields,
        "key": GOOGLE_API_KEY,
    }
    r = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params=params)
    return r.json()


# ---------- Main ----------

def process_place(place: dict, subcategory: str) -> Optional[dict]:
    place_id = place.get("place_id")
    if not place_id:
        return None

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

    photos = []
    photo_refs = result.get("photos", [])[:3]
    for p in photo_refs:
        ref = p.get("photo_reference")
        if ref:
            photos.append(get_photo_url(ref))

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
        "category": "Doctors & Healthcare",
        "subcategory": subcategory,
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


def upsert_listing(listing: dict) -> str:
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/directory_listings",
        headers=SUPABASE_HEADERS,
        json=listing,
    )
    if r.status_code >= 400:
        if r.status_code == 409 or "duplicate" in r.text.lower():
            return "skipped_dup"
        print(f"  ERROR inserting {listing.get('name', '?')}: {r.status_code} {r.text[:200]}")
        return "error"
    return "ok"


def main():
    total_new = 0
    total_dup = 0
    total_err = 0

    for subcategory, keywords in SPECIALIST_KEYWORDS.items():
        print(f"\n{'='*60}")
        print(f"Subcategory: {subcategory}")
        print(f"{'='*60}")

        sub_new = 0
        seen_place_ids = set()

        for keyword in keywords:
            for metro_name, coords in METROS.items():
                print(f"  [{metro_name}] Searching: {keyword}")
                resp = text_search(keyword, coords["lat"], coords["lng"])

                if resp.get("status") != "OK":
                    print(f"    Status: {resp.get('status')}")
                    continue

                results = resp.get("results", [])[:15]  # limit per keyword+city
                print(f"    Found {len(results)} results")

                for place in results:
                    pid = place.get("place_id")
                    if pid in seen_place_ids:
                        continue
                    seen_place_ids.add(pid)

                    listing = process_place(place, subcategory)
                    if not listing:
                        continue

                    status = upsert_listing(listing)
                    if status == "ok":
                        sub_new += 1
                        total_new += 1
                        print(f"    + {listing['name']} ({listing.get('city', '?')})")
                    elif status == "skipped_dup":
                        total_dup += 1
                    else:
                        total_err += 1

                time.sleep(0.2)

        print(f"  → {sub_new} new listings for {subcategory}")

    print(f"\n{'='*60}")
    print(f"DONE: {total_new} new, {total_dup} duplicates skipped, {total_err} errors")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
