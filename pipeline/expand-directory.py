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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from indian_relevance import is_indian_business

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
    cmd = ["curl", "-sS", "-w", "\nHTTP_CODE:%{http_code}",
           "--max-time", str(timeout), "-X", "POST", "-d", data]
    for k, v in headers.items():
        cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        parts = r.stdout.rsplit("HTTP_CODE:", 1)
        code = int(parts[-1].strip()) if len(parts) > 1 else 0
        if code >= 400:
            body = parts[0].strip()[:200] if parts else ""
            log.warning(f"POST {code}: {body}")
        return code
    except Exception as e:
        log.error(f"curl_post error: {e}")
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
    # Major states (already have some data, expand with curated queries)
    "CA": ["Los Angeles", "San Francisco", "San Jose", "Fremont", "Sunnyvale",
           "Irvine", "San Diego", "Sacramento", "Cupertino", "Santa Clara"],
    "TX": ["Houston", "Dallas", "Austin", "San Antonio", "Plano", "Irving",
           "Sugar Land", "Frisco", "Fort Worth"],
    "NY": ["New York", "Queens", "Jersey City", "Flushing", "Hicksville",
           "Buffalo", "Rochester", "Albany"],
    "NJ": ["Edison", "Jersey City", "Iselin", "Parsippany", "Princeton",
           "Cherry Hill", "Piscataway"],
    "IL": ["Chicago", "Naperville", "Schaumburg", "Skokie", "Des Plaines"],
    "GA": ["Atlanta", "Alpharetta", "Duluth", "Marietta", "Decatur", "Suwanee"],
    "VA": ["Fairfax", "Ashburn", "Herndon", "Chantilly", "Richmond", "Virginia Beach"],
    "MA": ["Boston", "Cambridge", "Waltham", "Lowell", "Worcester"],
    "MD": ["Rockville", "Columbia", "Baltimore", "Gaithersburg", "Silver Spring"],
    "WA": ["Seattle", "Bellevue", "Redmond", "Kirkland", "Bothell"],
    "IN": ["Indianapolis", "Carmel", "Fishers", "Greenwood"],
    "CT": ["Stamford", "Hartford", "New Haven", "Danbury"],
    "NV": ["Las Vegas", "Reno", "Henderson"],
    "NH": ["Nashua", "Manchester", "Concord"],
    "RI": ["Providence", "Warwick", "Cranston"],
    "AK": ["Anchorage", "Fairbanks"],
}

SEARCH_QUERIES = [
    # Restaurants & Food
    ("Indian restaurant", "Catering & Food"),
    ("Indian grocery store", "Catering & Food"),
    ("Indian sweets shop", "Catering & Food"),
    # Doctors
    ("Indian doctor", "Doctors & Healthcare"),
    ("Indian dentist", "Doctors & Healthcare"),
    # Temples
    ("Hindu temple", "Religious Services"),
    ("Gurudwara Sikh temple", "Religious Services"),
    ("Jain temple", "Religious Services"),
    # Yoga
    ("Indian yoga class", "Yoga & Wellness"),
    # Salons
    ("mehndi artist", "Beauty & Grooming"),
    ("Indian beauty salon threading", "Beauty & Grooming"),
    # Education
    ("Indian tutoring center", "Education & Tutoring"),
    ("Bharatanatyam dance class", "Education & Tutoring"),
    ("Indian music class", "Education & Tutoring"),
    # Event Venues
    ("Indian banquet hall", "Event Venues"),
    ("Indian wedding venue", "Event Venues"),
    # Immigration & Legal
    ("Indian immigration lawyer", "Attorneys & Immigration"),
    # Tax & Accounting
    ("Indian CPA accountant", "Tax & Accounting"),
    # Indian Clothing & Jewelry
    ("Indian clothing store saree", "Beauty & Grooming"),
    ("Indian jewelry store", "Beauty & Grooming"),
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


def slugify(text, place_id=None):
    import hashlib
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s)
    s = s.strip("-")[:100]
    if place_id:
        h = hashlib.md5(place_id.encode()).hexdigest()[:6]
        s = f"{s}-{h}"
    return s


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
    for off in range(0, 20000, 1000):
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
    url = f"{SUPABASE_URL}/rest/v1/directory_listings?on_conflict=slug"
    hdrs = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal"}
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

    # ── Relevance + quality gate ──
    resolved_cat = categorize(result.get("types", []), cat)
    is_relevant, skip_quality = is_indian_business(name, resolved_cat)
    if not is_relevant:
        return None

    if not skip_quality:
        rating = result.get("rating") or 0
        reviews = result.get("user_ratings_total") or 0
        if rating < 4.0 or reviews < 10:
            return None

    loc = result.get("geometry", {}).get("location", {})
    pu = photo_urls(result.get("photos", []))

    row = {
        "name": name,
        "category": resolved_cat,
        "address": addr,
        "city": p["city"],
        "state": p["state"],
        "zip": p["zip"],
        "slug": slugify(f"{name}-{p['city']}", pid),
        "google_place_id": pid,
        "source": "google_places",
        "latitude": loc.get("lat"),
        "longitude": loc.get("lng"),
        "rating": result.get("rating"),
        "review_count": result.get("user_ratings_total"),
        "image_url": pu[0] if pu else None,
        "photos": json.dumps(pu) if pu else None,
    }

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
