#!/usr/bin/env python3
"""
Targeted expansion for the 10 missing US states.
Self-contained — borrows core logic from expand-directory.py.
"""
import json, os, re, subprocess, sys, time, hashlib, logging

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from indian_relevance import is_indian_business

GKEY = os.environ.get("GOOGLE_PLACES_API_KEY", "AIzaSyB-KBpDQExIKfEl4J4fxUVMBviTpY7tfZ8")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)

MISSING_STATES = {
    "AK": ["Anchorage", "Fairbanks"],
    "HI": ["Honolulu", "Maui", "Hilo"],
    "IA": ["Des Moines", "Iowa City", "Cedar Rapids", "Davenport"],
    "ID": ["Boise", "Meridian", "Nampa", "Idaho Falls"],
    "ME": ["Portland", "South Portland", "Lewiston", "Bangor"],
    "MT": ["Bozeman", "Missoula", "Billings", "Great Falls"],
    "ND": ["Fargo", "Bismarck", "Grand Forks"],
    "SD": ["Sioux Falls", "Rapid City"],
    "VT": ["Burlington", "South Burlington", "Montpelier"],
    "WY": ["Cheyenne", "Laramie", "Casper", "Jackson"],
}

SEARCH_QUERIES = [
    ("Indian restaurant", "Catering & Food"),
    ("Indian grocery store", "Catering & Food"),
    ("Indian sweets shop", "Catering & Food"),
    ("Indian doctor", "Doctors & Healthcare"),
    ("Indian dentist", "Doctors & Healthcare"),
    ("Hindu temple", "Religious Services"),
    ("Gurudwara Sikh temple", "Religious Services"),
    ("Jain temple", "Religious Services"),
    ("Indian yoga class", "Yoga & Wellness"),
    ("mehndi artist", "Beauty & Grooming"),
    ("Indian beauty salon threading", "Beauty & Grooming"),
    ("Indian tutoring center", "Education & Tutoring"),
    ("Bharatanatyam dance class", "Education & Tutoring"),
    ("Indian music class", "Education & Tutoring"),
    ("Indian banquet hall", "Event Venues"),
    ("Indian wedding venue", "Event Venues"),
    ("Indian immigration lawyer", "Attorneys & Immigration"),
    ("Indian CPA accountant", "Tax & Accounting"),
    ("Indian clothing store saree", "Beauty & Grooming"),
    ("Indian jewelry store", "Beauty & Grooming"),
]

TYPE_TO_CATEGORY = {
    "restaurant": "Catering & Food", "food": "Catering & Food",
    "meal_delivery": "Catering & Food", "meal_takeaway": "Catering & Food",
    "bakery": "Catering & Food", "grocery_or_supermarket": "Catering & Food",
    "doctor": "Doctors & Healthcare", "dentist": "Doctors & Healthcare",
    "hospital": "Doctors & Healthcare", "pharmacy": "Doctors & Healthcare",
    "hindu_temple": "Religious Services", "mosque": "Religious Services",
    "place_of_worship": "Religious Services",
    "lawyer": "Attorneys & Immigration",
    "beauty_salon": "Beauty & Grooming", "hair_care": "Beauty & Grooming",
    "spa": "Beauty & Grooming", "accounting": "Tax & Accounting",
    "gym": "Yoga & Wellness",
    "school": "Education & Tutoring", "university": "Education & Tutoring",
}


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
        return code
    except Exception as e:
        log.error(f"curl_post error: {e}")
        return 0


def slugify(text, place_id=None):
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")[:100]
    if place_id:
        s = f"{s}-{hashlib.md5(place_id.encode()).hexdigest()[:6]}"
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
        "name": name, "category": resolved_cat, "address": addr,
        "city": p["city"], "state": p["state"], "zip": p["zip"],
        "slug": slugify(f"{name}-{p['city']}", pid),
        "google_place_id": pid, "source": "google_places",
        "latitude": loc.get("lat"), "longitude": loc.get("lng"),
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
    log.info("Targeted Expansion — 10 Missing States")
    log.info("=" * 60)

    seen = fetch_existing_ids()
    total_found = 0
    total_ins = 0
    results = {}

    for state, cities in MISSING_STATES.items():
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
        results[state] = len(buf)
        log.info(f"  ► {state}: {len(buf)} found, {ins} inserted")

    log.info("\n" + "=" * 60)
    log.info(f"DONE — {total_found} found, {total_ins} inserted")
    for st, c in sorted(results.items(), key=lambda x: -x[1]):
        log.info(f"  {st}: {c}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
