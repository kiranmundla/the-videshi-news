#!/usr/bin/env python3
"""
Expand The Videshi directory with Indian-origin DOCTORS nationwide.
Google Places Text Search → Indian relevance filter → insert.
FAST version: skips Place Details API (phone/website backfilled later).
Inserts per-city so progress is saved incrementally.
"""

import json, os, re, subprocess, sys, time, hashlib, logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from indian_relevance import is_indian_business
from places_budget import check_budget, record_call, budget_remaining  # daily cost guard
import atexit as _atexit
def _budget_report():
    u, l = __import__("places_budget").get_usage()
    if u > 0: print(f"Places API budget: {u}/{l} calls used today")
_atexit.register(_budget_report)

GKEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("/tmp/doctors-expand.log", mode="w"), logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)

DOCTOR_QUERIES = {
    "Pediatrician": ["Indian pediatrician", "South Asian pediatrician"],
    "Primary Care": ["Indian primary care doctor", "Indian family medicine doctor"],
    "OB/GYN": ["Indian OB/GYN doctor", "Indian gynecologist"],
    "Dentist": ["Indian dentist"],
    "Dermatologist": ["Indian dermatologist"],
    "Cardiologist": ["Indian cardiologist", "South Asian heart doctor"],
    "Psychiatrist / Mental Health": ["Indian psychiatrist", "South Asian therapist counselor"],
}

TARGET_CITIES = {
    "CA": ["San Jose","Fremont","Sunnyvale","Santa Clara","Milpitas","Cupertino",
           "Palo Alto","Mountain View","San Francisco","Oakland","Hayward",
           "Pleasanton","Dublin","Union City","Newark",
           "Los Angeles","Irvine","Anaheim","San Diego","Cerritos",
           "Artesia","Torrance","Pasadena","Sacramento","Bakersfield","Fresno"],
    "TX": ["Houston","Dallas","Plano","Irving","Sugar Land","Austin","San Antonio","Frisco"],
    "NJ": ["Edison","Jersey City","Iselin","Parsippany","Cherry Hill","Princeton"],
    "NY": ["New York","Queens","Flushing","Hicksville"],
    "IL": ["Chicago","Naperville","Schaumburg","Skokie"],
    "GA": ["Atlanta","Alpharetta","Duluth","Suwanee","Marietta"],
    "VA": ["Fairfax","Ashburn","Herndon","Chantilly","Richmond"],
    "MD": ["Rockville","Columbia","Gaithersburg","Silver Spring","Baltimore"],
    "PA": ["Philadelphia","Pittsburgh","King of Prussia"],
    "MI": ["Detroit","Troy","Ann Arbor","Novi","Canton"],
    "OH": ["Columbus","Cleveland","Cincinnati","Dayton"],
    "NC": ["Charlotte","Raleigh","Durham","Cary","Morrisville"],
    "FL": ["Miami","Orlando","Tampa","Jacksonville","Fort Lauderdale"],
    "WA": ["Seattle","Bellevue","Redmond","Kirkland"],
    "MA": ["Boston","Cambridge","Waltham","Lowell"],
    "CT": ["Stamford","Hartford","Danbury"],
    "MN": ["Minneapolis","Bloomington","Plymouth"],
    "AZ": ["Phoenix","Scottsdale","Chandler","Tempe"],
    "CO": ["Denver","Aurora","Boulder"],
    "TN": ["Nashville","Memphis","Franklin"],
    "IN": ["Indianapolis","Carmel","Fishers"],
    "WI": ["Milwaukee","Madison"],
    "MO": ["St Louis","Kansas City"],
    "OR": ["Portland","Beaverton"],
    "SC": ["Greenville","Charleston"],
    "AL": ["Birmingham","Huntsville"],
    "KY": ["Louisville","Lexington"],
    "UT": ["Salt Lake City","Provo"],
    "LA": ["New Orleans","Baton Rouge"],
    "NV": ["Las Vegas","Henderson"],
}

def curl_json(url, headers=None, timeout=15):
    cmd = ["curl", "-sS", "--max-time", str(timeout)]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return json.loads(r.stdout) if r.returncode == 0 else None
    except:
        return None

def curl_post(url, headers, data, timeout=30):
    cmd = ["curl", "-sS", "-w", "\nHTTP_CODE:%{http_code}", "--max-time", str(timeout), "-X", "POST", "-d", data]
    for k, v in headers.items():
        cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        parts = r.stdout.rsplit("HTTP_CODE:", 1)
        return int(parts[-1].strip()) if len(parts) > 1 else 0
    except:
        return 0

def slugify(text, place_id=None):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower().strip()).strip("-")[:100]
    if place_id:
        s = f"{s}-{hashlib.md5(place_id.encode()).hexdigest()[:6]}"
    return s

def parse_address(addr):
    parts = [p.strip() for p in addr.split(",")]
    city = state = zip_code = None
    if len(parts) >= 3:
        city = parts[-3]
        m = re.match(r"([A-Z]{2})\s+(\d{5}(?:-\d{4})?)", parts[-2].strip())
        if m:
            state, zip_code = m.group(1), m.group(2)
    return city, state, zip_code

def google_search(query, page_token=None):
    import urllib.parse
    params = {"query": query, "key": GKEY}
    if page_token:
        params["pagetoken"] = page_token
    return curl_json(f"https://maps.googleapis.com/maps/api/place/textsearch/json?{urllib.parse.urlencode(params)}") or {"status": "ERROR", "results": []}

def photo_urls(photos):
    return [f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={p['photo_reference']}&key={GKEY}"
            for p in (photos or [])[:5] if p.get("photo_reference")]

def fetch_existing_ids():
    ids = set()
    for off in range(0, 25000, 1000):
        data = curl_json(f"{SUPABASE_URL}/rest/v1/directory_listings?select=google_place_id&offset={off}&limit=1000",
                         headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
        if not data or not isinstance(data, list):
            break
        for d in data:
            if d.get("google_place_id"):
                ids.add(d["google_place_id"])
        if len(data) < 1000:
            break
    log.info(f"Loaded {len(ids)} existing place_ids")
    return ids

def insert_listings(listings):
    if not listings:
        return 0
    ok = 0
    hdrs = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json", "Prefer": "resolution=ignore-duplicates,return=minimal"}
    url = f"{SUPABASE_URL}/rest/v1/directory_listings"
    for i in range(0, len(listings), 25):
        batch = listings[i:i+25]
        code = curl_post(url, hdrs, json.dumps(batch))
        if code in (200, 201):
            ok += len(batch)
        else:
            for item in batch:
                c = curl_post(url, hdrs, json.dumps([item]))
                if c in (200, 201):
                    ok += 1
        time.sleep(0.1)
    return ok

def process(result, subcategory, seen):
    pid = result.get("place_id")
    if not pid or pid in seen:
        return None
    name = result.get("name", "").strip()
    addr = result.get("formatted_address", "")
    if not name or not addr:
        return None
    if "USA" not in addr and "United States" not in addr:
        return None
    city, state, zip_code = parse_address(addr)
    if not city or not state:
        return None

    is_rel, skip_q = is_indian_business(name, "Doctors & Healthcare")
    if not is_rel:
        nl = name.lower()
        if any(kw in nl for kw in ("indian","south asian","desi","hindi","tamil","telugu","punjabi","gujarati")):
            is_rel, skip_q = True, True
    if not is_rel:
        return None

    loc = result.get("geometry", {}).get("location", {})
    pu = photo_urls(result.get("photos"))

    spec_desc = {
        "Pediatrician": "pediatrics, providing comprehensive care for children and adolescents",
        "Primary Care": "primary care and family medicine",
        "OB/GYN": "obstetrics and gynecology, specializing in women's health",
        "Dentist": "dentistry, offering preventive, restorative, and cosmetic dental services",
        "Dermatologist": "dermatology, treating skin conditions",
        "Cardiologist": "cardiology, providing heart and cardiovascular health services",
        "Psychiatrist / Mental Health": "mental health services, offering therapy and psychiatric care",
    }

    seen.add(pid)
    return {
        "name": name,
        "category": "Doctors & Healthcare",
        "subcategory": subcategory,
        "address": addr,
        "city": city,
        "state": state,
        "zip": zip_code,
        "slug": slugify(f"{name}-{city}", pid),
        "google_place_id": pid,
        "source": "google_places",
        "latitude": loc.get("lat"),
        "longitude": loc.get("lng"),
        "rating": result.get("rating"),
        "review_count": result.get("user_ratings_total") or 0,
        "image_url": pu[0] if pu else None,
        "photos": json.dumps(pu) if pu else None,
        "ai_description": f"{name} specializes in {spec_desc.get(subcategory, subcategory.lower())} in {city}, {state}, catering to the South Asian community.",
    }

def search_and_collect(city, state, subcategory, queries, seen):
    out = []
    for q in queries:
        fq = f"{q} in {city}, {state}"
        data = google_search(fq)
        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            continue
        for r in data.get("results", []):
            item = process(r, subcategory, seen)
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
                item = process(r, subcategory, seen)
                if item:
                    out.append(item)
        time.sleep(0.15)
    return out

def main():
    if not GKEY or not SUPABASE_URL or not SUPABASE_KEY:
        log.error("Missing env vars"); sys.exit(1)

    total_cities = sum(len(c) for c in TARGET_CITIES.values())
    log.info(f"Doctor expansion: {len(TARGET_CITIES)} states, {total_cities} cities, {len(DOCTOR_QUERIES)} specialties")

    seen = fetch_existing_ids()
    grand_found = 0
    grand_ins = 0
    by_state = {}
    by_sub = {}

    state_order = ["CA"] + [s for s in TARGET_CITIES if s != "CA"]

    for state in state_order:
        cities = TARGET_CITIES[state]
        state_found = 0
        log.info(f"\n── {state} ({len(cities)} cities) ──")

        for city in cities:
            city_buf = []
            for subcat, queries in DOCTOR_QUERIES.items():
                results = search_and_collect(city, state, subcat, queries, seen)
                if results:
                    city_buf.extend(results)
                    by_sub[subcat] = by_sub.get(subcat, 0) + len(results)
            if city_buf:
                ins = insert_listings(city_buf)
                state_found += len(city_buf)
                log.info(f"  {city}: {len(city_buf)} found, {ins} inserted")
                grand_ins += ins
            else:
                log.info(f"  {city}: 0")

        grand_found += state_found
        by_state[state] = state_found
        log.info(f"  ► {state} total: {state_found}")

    log.info(f"\n{'='*60}")
    log.info(f"DONE — {grand_found} found, {grand_ins} inserted")
    for st, c in sorted(by_state.items(), key=lambda x: -x[1]):
        if c: log.info(f"  {st}: {c}")
    log.info("By specialty:")
    for sub, c in sorted(by_sub.items(), key=lambda x: -x[1]):
        if c: log.info(f"  {sub}: {c}")

if __name__ == "__main__":
    main()
