#!/usr/bin/env python3
"""
Expand The Videshi directory with Google Places searches
for Indian/South Asian businesses in underrepresented US states.
Uses curl for HTTP (proxy-safe).
"""

import json
import os
import re
import subprocess
import sys
import time
import logging
from typing import Optional

GKEY = "AIzaSyB-KBpDQExIKfEl4J4fxUVMBviTpY7tfZ8"
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

LOG_FILE = "/tmp/directory-expansion.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def curl_json(url, headers=None, timeout=20):
    cmd = ["curl", "-sS", "--max-time", str(timeout)]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except Exception as e:
        log.error(f"curl_json error: {e}")
        return None


def curl_post(url, headers, data, timeout=30):
    cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
           "--max-time", str(timeout), "-X", "POST", "-d", data]
    for k, v in headers.items():
        cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        return int(r.stdout.strip())
    except Exception:
        return 0


STATE_CITIES = {
    "FL": ["Miami", "Orlando", "Tampa", "Jacksonville", "Fort Lauderdale"],
    "PA": ["Philadelphia", "Pittsburgh", "Allentown", "King of Prussia"],
    "OH": ["Columbus", "Cleveland", "Cincinnati", "Dayton"],
    "MI": ["Detroit", "Troy", "Ann Arbor", "Grand Rapids", "Novi"],
    "NC": ["Charlotte", "Raleigh", "Durham", "Cary", "Morrisville"],
    "AZ": ["Phoenix", "Scottsdale", "Tempe", "Chandler", "Mesa"],
    "CO": ["Denver", "Aurora", "Boulder", "Colorado Springs"],
    "MN": ["Minneapolis", "Bloomington", "Plymouth", "Maple Grove"],
    "OR": ["Portland", "Beaverton", "Hillsboro", "Salem"],
    "TN": ["Nashville", "Memphis", "Knoxville", "Franklin"],
    "SC": ["Greenville", "Charleston", "Columbia"],
    "WI": ["Milwaukee", "Madison"],
    "MO": ["St Louis", "Kansas City"],
    "LA": ["New Orleans", "Baton Rouge"],
    "UT": ["Salt Lake City", "Provo"],
    "AL": ["Birmingham", "Huntsville"],
    "KY": ["Louisville", "Lexington"],
    "OK": ["Oklahoma City", "Tulsa"],
    "KS": ["Overland Park", "Wichita"],
    "IA": ["Des Moines", "Iowa City"],
    "NE": ["Omaha", "Lincoln"],
    "NM": ["Albuquerque", "Santa Fe"],
    "HI": ["Honolulu"],
    "AR": ["Little Rock"],
    "MS": ["Jackson"],
    "DE": ["Wilmington", "Newark"],
    "WV": ["Charleston"],
    "ME": ["Portland"],
    "VT": ["Burlington"],
    "ID": ["Boise"],
    "MT": ["Bozeman", "Missoula"],
    "WY": ["Cheyenne"],
    "SD": ["Sioux Falls"],
    "ND": ["Fargo"],
}

SEARCH_QUERIES = [
    ("Indian restaurant", "Catering & Food"),
    ("Indian grocery store", "Catering & Food"),
    ("Indian doctor", "Doctors & Healthcare"),
    ("Indian dentist", "Doctors & Healthcare"),
    ("Hindu temple", "Religious Services"),
    ("Gurudwara Sikh temple", "Religious Services"),
    ("Indian immigration lawyer", "Attorneys & Immigration"),
    ("Indian real estate agent", "Real Estate"),
    ("Indian beauty salon", "Beauty & Grooming"),
    ("Indian tax accountant CPA", "Tax & Accounting"),
    ("Indian yoga studio", "Yoga & Wellness"),
    ("Indian tutoring center", "Education & Tutoring"),
]

TYPE_TO_CATEGORY = {
    "restaurant": "Catering & Food", "food": "Catering & Food",
    "meal_delivery": "Catering & Food", "meal_takeaway": "Catering & Food",
    "bakery": "Catering & Food", "grocery_or_supermarket": "Catering & Food",
    "doctor": "Doctors & Healthcare", "dentist": "Doctors & Healthcare",
    "hospital": "Doctors & Healthcare", "pharmacy": "Doctors & Healthcare",
    "physiotherapist": "Doctors & Healthcare",
    "hindu_temple": "Religious Services", "mosque": "Religious Services",
    "church": "Religious Services", "place_of_worship": "Religious Services",
    "lawyer": "Attorneys & Immigration",
    "real_estate_agent": "Real Estate", "real_estate_agency": "Real Estate",
    "beauty_salon": "Beauty & Grooming", "hair_care": "Beauty & Grooming",
    "spa": "Beauty & Grooming",
    "accounting": "Tax & Accounting",
    "gym": "Yoga & Wellness",
    "school": "Education & Tutoring", "university": "Education & Tutoring",
    "plumber": "Home Services", "electrician": "Home Services",
    "roofing_contractor": "Home Services", "moving_company": "Home Services",
    "general_contractor": "Home Services",
}


def slugify(text):
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")[:120]


def parse_address(addr):
    parts = [p.strip() for p in addr.split(",")]
    city = state = zip_code = None
    if len(parts) >= 3:
        city = parts[-3]
        sz = parts[-2].strip()
        m = re.match(r"([A-Z]{2})\s+(\d{5}(?:-\d{4})?)", sz)
        if m:
            state, zip_code = m.group(1), m.group(2)
    return {"city": city, "state": state, "zip": zip_code}


def google_search(query, page_token=None):
    import urllib.parse
    params = {"query": query, "key": GKEY}
    if page_token:
        params["pagetoken"] = page_token
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?{urllib.parse.urlencode(params)}"
    r = curl_json(url)
    return r or {"status": "ERROR", "results": []}


def photo_urls(photos):
    return [f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={p['photo_reference']}&key={GKEY}"
            for p in photos[:5] if p.get("photo_reference")]


def categorize(types, fallback):
    for t in types:
        if t in TYPE_TO_CATEGORY:
            return TYPE_TO_CATEGORY[t]
    return fallback


def fetch_existing_ids():
    ids = set()
    for off in range(0, 5000, 1000):
        url = f"{SUPABASE_URL}/rest/v1/directory_listings?select=google_place_id&offset={off}&limit=1000"
        data = curl_json(url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
        if not data or not isinstance(data, list):
            break
        for d in data:
            if d.get("google_place_id"):
                ids.add(d["google_place_id"])
        if len(data) < 1000:
            break
    log.info(f"Loaded {len(ids)} existing place_ids")
    return ids


def insert_batch(listings):
    if not listings:
        return 0
    ok = 0
    url = f"{SUPABASE_URL}/rest/v1/directory_listings"
    hdrs = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=ignore-duplicates,return=minimal"}
    for i in range(0, len(listings), 50):
        batch = listings[i:i+50]
        code = curl_post(url, hdrs, json.dumps(batch))
        if code in (200, 201):
            ok += len(batch)
        else:
            log.warning(f"Insert returned {code} for batch of {len(batch)}")
        time.sleep(0.2)
    return ok


def process(result, cat, seen):
    pid = result.get("place_id")
    if not pid or pid in seen:
        return None
    name = result.get("name", "").strip()
    addr = result.get("formatted_address", "")
    if not name or not addr or "USA" not in addr:
        return None
    p = parse_address(addr)
    if not p["city"] or not p["state"]:
        return None

    loc = result.get("geometry", {}).get("location", {})
    pu = photo_urls(result.get("photos", []))

    row = {
        "name": name, "category": categorize(result.get("types", []), cat),
        "address": addr, "city": p["city"], "state": p["state"],
        "slug": slugify(f"{name}-{p['city']}"),
        "google_place_id": pid, "source": "google_places",
    }
    if p["zip"]: row["zip"] = p["zip"]
    if loc.get("lat") is not None: row["latitude"] = loc["lat"]
    if loc.get("lng") is not None: row["longitude"] = loc["lng"]
    if result.get("rating") is not None: row["rating"] = result["rating"]
    if result.get("user_ratings_total") is not None: row["review_count"] = result["user_ratings_total"]
    if pu:
        row["image_url"] = pu[0]
        row["photos"] = json.dumps(pu)

    seen.add(pid)
    return row


def search_city(city, state, query, cat, seen):
    fq = f"{query} in {city}, {state}"
    out = []
    data = google_search(fq)
    if data.get("status") not in ("OK", "ZERO_RESULTS"):
        return out
    for r in data.get("results", []):
        item = process(r, cat, seen)
        if item:
            out.append(item)
    for _ in range(2):
        tok = data.get("next_page_token")
        if not tok:
            break
        time.sleep(2.2)
        data = google_search(fq, page_token=tok)
        if data.get("status") != "OK":
            break
        for r in data.get("results", []):
            item = process(r, cat, seen)
            if item:
                out.append(item)
    return out


def main():
    log.info("=" * 60)
    log.info("Directory Expansion (curl-based)")
    log.info(f"{len(STATE_CITIES)} states, {len(SEARCH_QUERIES)} query types")
    log.info("=" * 60)

    seen = fetch_existing_ids()
    total_found = 0
    total_ins = 0
    sc = {}

    for state, cities in STATE_CITIES.items():
        buf = []
        log.info(f"\n── {state} ({len(cities)} cities) ──")
        for city in cities:
            cf = 0
            for q, cat in SEARCH_QUERIES:
                res = search_city(city, state, q, cat, seen)
                if res:
                    buf.extend(res)
                    cf += len(res)
                time.sleep(0.3)
            if cf:
                log.info(f"  {city}: {cf} new")
        ins = insert_batch(buf)
        total_found += len(buf)
        total_ins += ins
        sc[state] = len(buf)
        log.info(f"  ► {state}: {len(buf)} found, {ins} inserted")

    log.info("\n" + "=" * 60)
    log.info(f"DONE — {total_found} found, {total_ins} inserted")
    for st, c in sorted(sc.items(), key=lambda x: -x[1]):
        if c: log.info(f"  {st}: {c}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
