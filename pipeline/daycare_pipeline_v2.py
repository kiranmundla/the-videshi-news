#!/usr/bin/env python3
"""
Daycare & Childcare pipeline for The Videshi directory.
Uses legacy Google Places API (Text Search + Place Details).
"""

import json, os, subprocess, time, re, hashlib, urllib.parse

CATEGORY = "Daycare & Childcare"
SOURCE = "google_places"

API_KEY = os.environ["GOOGLE_PLACES_API_KEY"]
SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
if not SUPABASE_URL.startswith("http"):
    SUPABASE_URL = "https://" + SUPABASE_URL
SUPA_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

SEARCHES = [
    # California
    ("Fremont CA", "Indian daycare"),
    ("San Jose CA", "Indian daycare"),
    ("Sunnyvale CA", "Indian daycare"),
    ("Milpitas CA", "Indian daycare"),
    ("Santa Clara CA", "Indian daycare"),
    ("Cupertino CA", "Indian preschool"),
    ("San Francisco CA", "Indian childcare"),
    ("Irvine CA", "Indian daycare"),
    ("Los Angeles CA", "Indian daycare"),
    ("San Diego CA", "Indian daycare"),
    ("Sacramento CA", "Indian daycare"),
    ("Pleasanton CA", "Indian daycare"),
    ("Dublin CA", "Indian daycare"),
    # NJ / NY
    ("Edison NJ", "Indian daycare"),
    ("Jersey City NJ", "Indian daycare"),
    ("Plainsboro NJ", "Indian daycare"),
    ("Parsippany NJ", "Indian daycare"),
    ("Iselin NJ", "Indian childcare"),
    ("New York NY", "Indian daycare"),
    ("Hicksville NY", "Indian daycare"),
    ("Queens NY", "Indian daycare"),
    # Texas
    ("Houston TX", "Indian daycare"),
    ("Dallas TX", "Indian daycare"),
    ("Plano TX", "Indian daycare"),
    ("Irving TX", "Indian daycare"),
    ("Austin TX", "Indian daycare"),
    ("Sugar Land TX", "Indian daycare"),
    ("Frisco TX", "Indian daycare"),
    # Illinois
    ("Chicago IL", "Indian daycare"),
    ("Naperville IL", "Indian daycare"),
    ("Schaumburg IL", "Indian daycare"),
    # DMV
    ("Washington DC", "Indian daycare"),
    ("Ashburn VA", "Indian daycare"),
    ("Herndon VA", "Indian daycare"),
    ("Rockville MD", "Indian daycare"),
    ("Columbia MD", "Indian daycare"),
    # East Coast
    ("Philadelphia PA", "Indian daycare"),
    ("Boston MA", "Indian daycare"),
    ("Raleigh NC", "Indian daycare"),
    ("Morrisville NC", "Indian daycare"),
    ("Cary NC", "Indian daycare"),
    ("Atlanta GA", "Indian daycare"),
    ("Alpharetta GA", "Indian daycare"),
    ("Johns Creek GA", "Indian daycare"),
    # PNW
    ("Seattle WA", "Indian daycare"),
    ("Bellevue WA", "Indian daycare"),
    ("Redmond WA", "Indian daycare"),
    # Mountain / SW
    ("Phoenix AZ", "Indian daycare"),
    ("Chandler AZ", "Indian daycare"),
    ("Denver CO", "Indian daycare"),
    # Midwest
    ("Minneapolis MN", "Indian daycare"),
    ("Troy MI", "Indian daycare"),
    ("Columbus OH", "Indian daycare"),
    ("Dublin OH", "Indian daycare"),
    ("Indianapolis IN", "Indian daycare"),
    # Extra searches with variant terms
    ("Fremont CA", "desi daycare"),
    ("Edison NJ", "desi daycare"),
    ("Houston TX", "desi daycare"),
    ("San Jose CA", "desi childcare"),
    ("Fremont CA", "Indian preschool"),
    ("Edison NJ", "Indian preschool"),
    ("Naperville IL", "desi daycare"),
    ("Ashburn VA", "desi daycare"),
    ("Plano TX", "desi daycare"),
    ("Alpharetta GA", "desi daycare"),
    ("Morrisville NC", "desi daycare"),
    ("Sunnyvale CA", "Indian home daycare"),
    ("Fremont CA", "Indian home daycare"),
    ("Edison NJ", "Indian home daycare"),
    ("Houston TX", "Indian home daycare"),
    ("Naperville IL", "Indian home daycare"),
]

INDIAN_NAME_KW = [
    "indian", "desi", "hindi", "krishna", "lakshmi", "ganesha", "ganesh",
    "shanti", "patel", "sharma", "gupta", "kumar", "singh", "agarwal",
    "jain", "mehta", "shah", "bala", "vidya", "saraswati", "durga",
    "radha", "meera", "annapurna", "tulsi", "vedic", "gurukul", "bal",
    "bachpan", "nanhi", "chhota", "sapna", "angan", "jhula", "rangoli",
    "diya", "namaste", "om", "sanskar", "sanskaar", "nanny", "aunty",
    "auntie", "amma", "akka", "jayanthi", "govardhan", "aasaan",
    "nirmala", "priya", "deepa", "neha", "pooja", "puja", "aarti",
    "sita", "seema", "rekha", "sunita", "kavita", "nidhi", "ritu",
    "sneha", "anjali", "padma", "usha", "kiran", "choti", "munna",
    "champa", "rani", "raja", "chanda", "taara", "amrit", "rashi",
    "moksha", "ahimsa", "dharma", "mantra",
]

INDIAN_REVIEW_KW = [
    "indian", "hindi", "vegetarian", "veg food", "indian food",
    "desi", "bollywood", "sanskrit", "puja", "diwali", "holi",
    "rangoli", "dal", "roti", "chapati", "khichdi", "samosa",
    "south indian", "north indian", "tamil", "telugu", "gujarati",
    "marathi", "punjabi", "bengali", "kannada", "malayalam",
    "cultural", "indian culture", "indian families", "indian community",
    "indian kids", "indian children",
]

seen_ids = set()
api_calls = 0
stats = {"searched": 0, "found": 0, "indian": 0, "inserted": 0, "dupe": 0, "failed": 0}


def curl_json(url):
    global api_calls
    r = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=30)
    api_calls += 1
    try:
        return json.loads(r.stdout)
    except:
        return {"status": "PARSE_ERROR"}


def text_search(query, location):
    q = urllib.parse.quote(f"{query} near {location}")
    return curl_json(f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={q}&key={API_KEY}")


def get_details(place_id):
    fields = "name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,geometry,opening_hours,reviews,photos,types,url"
    return curl_json(f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={fields}&key={API_KEY}")


def is_indian(name, review_text):
    n = name.lower()
    if any(kw in n for kw in INDIAN_NAME_KW):
        return True
    rt = review_text.lower()
    return sum(1 for kw in INDIAN_REVIEW_KW if kw in rt) >= 2


def parse_address(addr):
    city, state, zipcode = "", "", ""
    if not addr:
        return city, state, zipcode
    parts = [p.strip() for p in addr.split(",")]
    if len(parts) >= 3:
        city = parts[-3].strip() if len(parts) >= 4 else parts[-2].strip()
        sz = parts[-2].strip()
        m = re.match(r"([A-Z]{2})\s+(\d{5}(?:-\d{4})?)", sz)
        if m:
            state, zipcode = m.group(1), m.group(2)
        elif len(sz) >= 2:
            state = sz[:2]
    return city, state, zipcode


def build_listing(details_resp, place_id):
    d = details_resp.get("result", {})
    name = d.get("name", "")
    addr = d.get("formatted_address", "")
    city, state, zipcode = parse_address(addr)
    
    hours = None
    oh = d.get("opening_hours", {})
    if oh and "weekday_text" in oh:
        hours = oh["weekday_text"]
    
    image_url = None
    photos = d.get("photos", [])
    if photos:
        ref = photos[0].get("photo_reference")
        if ref:
            image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={ref}&key={API_KEY}"
    
    slug_base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:50]
    slug = f"{slug_base}-{hashlib.md5(place_id.encode()).hexdigest()[:6]}"
    
    desc = ""
    for r in d.get("reviews", [])[:3]:
        t = r.get("text", "")
        if t and len(t) > 30:
            desc = t[:300]
            break
    if not desc:
        desc = f"{name} - Daycare & childcare in {city}, {state}"
    
    return {
        "name": name,
        "category": CATEGORY,
        "subcategory": "Daycare",
        "description": desc,
        "phone": d.get("formatted_phone_number"),
        "website": d.get("website"),
        "address": addr,
        "city": city,
        "state": state,
        "zip": zipcode,
        "latitude": d.get("geometry", {}).get("location", {}).get("lat"),
        "longitude": d.get("geometry", {}).get("location", {}).get("lng"),
        "image_url": image_url,
        "rating": d.get("rating"),
        "review_count": d.get("user_ratings_total"),
        "google_place_id": place_id,
        "hours": json.dumps(hours) if hours else None,
        "source": SOURCE,
        "slug": slug,
        "verified": False,
        "featured": False,
    }


def load_existing():
    r = subprocess.run([
        "curl", "-s",
        f"{SUPABASE_URL}/rest/v1/directory_listings?select=google_place_id&google_place_id=not.is.null&limit=10000",
        "-H", f"apikey: {SUPA_KEY}",
        "-H", f"Authorization: Bearer {SUPA_KEY}",
    ], capture_output=True, text=True, timeout=30)
    try:
        return {d["google_place_id"] for d in json.loads(r.stdout) if d.get("google_place_id")}
    except:
        return set()


def insert(listing):
    clean = {k: v for k, v in listing.items() if v is not None}
    r = subprocess.run([
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/directory_listings",
        "-H", f"apikey: {SUPA_KEY}",
        "-H", f"Authorization: Bearer {SUPA_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal",
        "-d", json.dumps(clean),
    ], capture_output=True, text=True, timeout=30)
    return r.stdout.strip()


def main():
    global seen_ids
    
    print("🔍 Loading existing place IDs...")
    seen_ids = load_existing()
    print(f"  {len(seen_ids)} existing listings\n")
    
    # Phase 1: Text Search — collect candidates
    candidates = {}
    
    for location, query in SEARCHES:
        print(f"📍 {query} near {location}")
        try:
            data = text_search(query, location)
        except Exception as e:
            print(f"  ⚠ {e}")
            continue
        
        stats["searched"] += 1
        
        if data.get("status") not in ("OK",):
            s = data.get("status", "?")
            print(f"  {s}" if s == "ZERO_RESULTS" else f"  ⚠ {s}")
            continue
        
        results = data.get("results", [])
        stats["found"] += len(results)
        new = 0
        
        for r in results:
            pid = r.get("place_id", "")
            if pid in seen_ids or pid in candidates:
                continue
            candidates[pid] = r.get("name", "")
            new += 1
        
        print(f"  {len(results)} results, {new} new")
        time.sleep(0.3)
    
    print(f"\n{'='*60}")
    print(f"Phase 1: {len(candidates)} unique candidates from {stats['searched']} searches")
    print(f"{'='*60}\n")
    
    # Phase 2: Details + Indian filter + insert
    for i, (pid, name) in enumerate(candidates.items()):
        print(f"[{i+1}/{len(candidates)}] {name}")
        
        try:
            details = get_details(pid)
        except Exception as e:
            print(f"  ⚠ Details error: {e}")
            stats["failed"] += 1
            continue
        
        if details.get("status") != "OK":
            print(f"  ⚠ {details.get('status')}")
            stats["failed"] += 1
            continue
        
        d = details.get("result", {})
        review_text = " ".join(r.get("text", "") for r in d.get("reviews", [])[:5])
        actual_name = d.get("name", name)
        
        if not is_indian(actual_name, review_text):
            print(f"  ⏭ Not Indian")
            continue
        
        stats["indian"] += 1
        listing = build_listing(details, pid)
        code = insert(listing)
        
        if code == "201":
            stats["inserted"] += 1
            print(f"  ✅ {actual_name} ({listing['city']}, {listing['state']})")
        elif code == "409":
            stats["dupe"] += 1
            print(f"  ⏭ Dupe")
        else:
            stats["failed"] += 1
            print(f"  ❌ {code}")
        
        time.sleep(0.2)
    
    print(f"\n{'='*60}")
    print(f"📊 DAYCARE PIPELINE RESULTS")
    print(f"{'='*60}")
    for k, v in stats.items():
        print(f"  {k:18s} {v}")
    print(f"  {'api_calls':18s} {api_calls}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
