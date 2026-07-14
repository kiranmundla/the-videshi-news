#!/usr/bin/env python3
"""
Daycare & Childcare pipeline for The Videshi directory.
Searches Google Places API for Indian daycare/childcare centers across major US metros.
"""

import json, os, subprocess, time, re, hashlib

# ── Config ──
CATEGORY = "Daycare & Childcare"
SOURCE = "google_places"

# Top US metros by Indian-American population
METROS = [
    # California
    ("San Jose, CA", "Indian daycare"),
    ("Fremont, CA", "Indian childcare"),
    ("Sunnyvale, CA", "Indian daycare"),
    ("Cupertino, CA", "Indian preschool"),
    ("Milpitas, CA", "Indian daycare"),
    ("Santa Clara, CA", "desi daycare"),
    ("San Francisco, CA", "Indian daycare"),
    ("Irvine, CA", "Indian childcare"),
    ("Los Angeles, CA", "Indian daycare"),
    ("San Diego, CA", "Indian daycare"),
    ("Sacramento, CA", "Indian daycare"),
    
    # New Jersey / New York
    ("Edison, NJ", "Indian daycare"),
    ("Jersey City, NJ", "Indian childcare"),
    ("Plainsboro, NJ", "Indian daycare"),
    ("Iselin, NJ", "desi daycare"),
    ("Parsippany, NJ", "Indian preschool"),
    ("New York, NY", "Indian daycare"),
    ("Hicksville, NY", "Indian daycare"),
    ("Queens, NY", "Indian childcare"),
    
    # Texas
    ("Houston, TX", "Indian daycare"),
    ("Dallas, TX", "Indian childcare"),
    ("Plano, TX", "Indian daycare"),
    ("Irving, TX", "Indian daycare"),
    ("Austin, TX", "Indian daycare"),
    ("Sugar Land, TX", "Indian daycare"),
    ("Frisco, TX", "Indian childcare"),
    
    # Illinois
    ("Chicago, IL", "Indian daycare"),
    ("Naperville, IL", "Indian daycare"),
    ("Schaumburg, IL", "Indian childcare"),
    
    # East Coast
    ("Washington, DC", "Indian daycare"),
    ("Ashburn, VA", "Indian daycare"),
    ("Herndon, VA", "Indian childcare"),
    ("Tysons, VA", "Indian daycare"),
    ("Rockville, MD", "Indian daycare"),
    ("Philadelphia, PA", "Indian daycare"),
    ("Boston, MA", "Indian daycare"),
    ("Raleigh, NC", "Indian daycare"),
    ("Morrisville, NC", "Indian childcare"),
    ("Cary, NC", "Indian daycare"),
    ("Atlanta, GA", "Indian daycare"),
    ("Alpharetta, GA", "Indian daycare"),
    ("Johns Creek, GA", "Indian daycare"),
    
    # Pacific NW / Mountain
    ("Seattle, WA", "Indian daycare"),
    ("Bellevue, WA", "Indian daycare"),
    ("Redmond, WA", "Indian childcare"),
    ("Phoenix, AZ", "Indian daycare"),
    ("Chandler, AZ", "Indian daycare"),
    ("Denver, CO", "Indian daycare"),
    
    # Midwest
    ("Minneapolis, MN", "Indian daycare"),
    ("Troy, MI", "Indian daycare"),
    ("Columbus, OH", "Indian daycare"),
    ("Dublin, OH", "Indian daycare"),
    ("Indianapolis, IN", "Indian daycare"),
    
    # Additional queries with different search terms to cast a wider net
    ("San Jose, CA", "desi childcare"),
    ("Edison, NJ", "desi childcare"),
    ("Houston, TX", "desi daycare"),
    ("Fremont, CA", "Indian preschool"),
    ("Irving, TX", "desi daycare"),
    ("Naperville, IL", "desi daycare"),
    ("Ashburn, VA", "desi childcare"),
    ("Plano, TX", "desi childcare"),
    
    # Broader queries for less-specific areas
    ("Bay Area, CA", "Indian home daycare"),
    ("New Jersey", "Indian home daycare"),
    ("Houston area, TX", "desi home daycare"),
    ("Northern Virginia", "Indian home daycare"),
    ("Research Triangle, NC", "Indian home daycare"),
]

API_KEY = os.environ["GOOGLE_PLACES_API_KEY"]
SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
if not SUPABASE_URL.startswith("http"):
    SUPABASE_URL = "https://" + SUPABASE_URL
SUPA_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Track seen place IDs to avoid dupe API calls
seen_place_ids = set()
all_places = []
api_calls = 0

def search_places(query, location_text):
    """Search Google Places Text Search API."""
    global api_calls
    
    text_query = f"{query} near {location_text}"
    
    body = json.dumps({
        "textQuery": text_query,
        "languageCode": "en",
        "maxResultCount": 20,
    })
    
    fields = "places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount,places.location,places.googleMapsUri,places.primaryTypeDisplayName,places.reviews,places.currentOpeningHours,places.photos"
    
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://places.googleapis.com/v1/places:searchText",
        "-H", f"X-Goog-Api-Key: {API_KEY}",
        "-H", f"X-Goog-FieldMask: {fields}",
        "-H", "Content-Type: application/json",
        "-d", body,
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    api_calls += 1
    
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  ⚠ JSON parse error for: {text_query}")
        return []
    
    if "error" in data:
        print(f"  ⚠ API error: {data['error'].get('message', 'unknown')}")
        return []
    
    places = data.get("places", [])
    return places


def is_indian_daycare(place):
    """
    Check if a place is likely an Indian-run daycare/childcare.
    Look at name, reviews, and type for Indian cultural indicators.
    """
    name = (place.get("displayName", {}).get("text", "") or "").lower()
    address = (place.get("formattedAddress", "") or "").lower()
    
    # Indian name indicators
    indian_keywords = [
        "indian", "desi", "hindi", "montessori indian", "krishna", "lakshmi",
        "ganesha", "ganesh", "sita", "rama", "shanti", "patel", "sharma",
        "gupta", "kumar", "singh", "agarwal", "jain", "mehta", "shah",
        "nanny", "auntie", "aunty", "amma", "akka", "bala", "vidya",
        "saraswati", "durga", "radha", "meera", "annapurna", "tulsi",
        "vedic", "gurukul", "bal", "bachpan", "nanhi", "chhota", "sapna",
        "angan", "jhula", "rangoli", "diya", "namaste", "om", "sanskar",
        "sanskaar", "little", "precious", "tiny",
        "preschool", "childcare", "daycare", "child care", "day care",
        "nurtury", "kidz", "smiley",
    ]
    
    # Check name
    name_match = any(kw in name for kw in indian_keywords)
    
    # Check reviews for Indian cultural indicators  
    reviews = place.get("reviews", [])
    indian_review_keywords = [
        "indian", "hindi", "vegetarian", "veg food", "indian food",
        "desi", "bollywood", "sanskrit", "puja", "diwali", "holi",
        "rangoli", "dal", "roti", "chapati", "khichdi", "samosa",
        "south indian", "north indian", "tamil", "telugu", "gujarati",
        "marathi", "punjabi", "bengali", "kannada", "malayalam",
        "cultural", "homeland",
    ]
    
    review_texts = []
    for r in reviews[:5]:
        txt = (r.get("text", {}).get("text", "") or "").lower()
        review_texts.append(txt)
    
    all_review_text = " ".join(review_texts)
    review_match_count = sum(1 for kw in indian_review_keywords if kw in all_review_text)
    
    # Accept if: name matches, OR 2+ review keyword hits
    return name_match or review_match_count >= 2


def parse_place(place):
    """Parse a Google Places result into a directory_listings row."""
    place_id = place.get("id", "")
    name = place.get("displayName", {}).get("text", "")
    address = place.get("formattedAddress", "")
    phone = place.get("nationalPhoneNumber")
    website = place.get("websiteUri")
    rating = place.get("rating")
    review_count = place.get("userRatingCount")
    lat = place.get("location", {}).get("latitude")
    lng = place.get("location", {}).get("longitude")
    
    # Parse address components
    city, state, zipcode = "", "", ""
    if address:
        # Typical format: "123 Main St, City, ST 12345, USA"
        parts = [p.strip() for p in address.split(",")]
        if len(parts) >= 3:
            city = parts[-3] if len(parts) >= 4 else parts[-2]
            state_zip = parts[-2].strip()
            # Extract state and zip
            m = re.match(r"([A-Z]{2})\s+(\d{5}(?:-\d{4})?)", state_zip)
            if m:
                state = m.group(1)
                zipcode = m.group(2)
            else:
                state = state_zip[:2] if len(state_zip) >= 2 else state_zip
    
    # Parse hours
    hours_data = None
    opening_hours = place.get("currentOpeningHours", {})
    if opening_hours and "weekdayDescriptions" in opening_hours:
        hours_data = opening_hours["weekdayDescriptions"]
    
    # Get first photo URL
    image_url = None
    photos = place.get("photos", [])
    if photos:
        photo_name = photos[0].get("name", "")
        if photo_name:
            image_url = f"https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx=800&key={API_KEY}"
    
    # Build slug
    slug_base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:50]
    slug_hash = hashlib.md5(place_id.encode()).hexdigest()[:6]
    slug = f"{slug_base}-{slug_hash}"
    
    # Build description from reviews
    description = ""
    reviews = place.get("reviews", [])
    if reviews:
        # Use the first positive review as description seed
        for r in reviews[:3]:
            txt = r.get("text", {}).get("text", "")
            if txt and len(txt) > 30:
                description = txt[:300]
                break
    
    if not description:
        ptype = place.get("primaryTypeDisplayName", {}).get("text", "daycare")
        description = f"{name} - {ptype} in {city}, {state}"
    
    return {
        "name": name,
        "category": CATEGORY,
        "subcategory": "Daycare",
        "description": description,
        "phone": phone,
        "website": website,
        "address": address,
        "city": city,
        "state": state,
        "zip": zipcode,
        "latitude": lat,
        "longitude": lng,
        "image_url": image_url,
        "rating": rating,
        "review_count": review_count,
        "google_place_id": place_id,
        "hours": json.dumps(hours_data) if hours_data else None,
        "source": SOURCE,
        "slug": slug,
        "verified": False,
        "featured": False,
    }


def check_existing_place_ids():
    """Get all existing google_place_ids to avoid duplicates."""
    cmd = [
        "curl", "-s",
        f"{SUPABASE_URL}/rest/v1/directory_listings?select=google_place_id&google_place_id=not.is.null&limit=10000",
        "-H", f"apikey: {SUPA_KEY}",
        "-H", f"Authorization: Bearer {SUPA_KEY}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        data = json.loads(result.stdout)
        return {d["google_place_id"] for d in data if d.get("google_place_id")}
    except:
        return set()


def insert_listing(listing):
    """Insert a single listing into directory_listings."""
    # Remove None values
    clean = {k: v for k, v in listing.items() if v is not None}
    
    cmd = [
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/directory_listings",
        "-H", f"apikey: {SUPA_KEY}",
        "-H", f"Authorization: Bearer {SUPA_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal",
        "-d", json.dumps(clean),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout.strip()


def main():
    global seen_place_ids, all_places
    
    print("🔍 Loading existing google_place_ids...")
    existing_ids = check_existing_place_ids()
    print(f"  Found {len(existing_ids)} existing listings")
    seen_place_ids = set(existing_ids)
    
    total_searched = 0
    total_found = 0
    total_indian = 0
    total_inserted = 0
    total_skipped_dupe = 0
    total_failed = 0
    
    for location, query in METROS:
        print(f"\n📍 {query} near {location}")
        
        try:
            places = search_places(query, location)
        except Exception as e:
            print(f"  ⚠ Error: {e}")
            continue
        
        total_searched += 1
        found = len(places)
        total_found += found
        print(f"  Found {found} results")
        
        for place in places:
            pid = place.get("id", "")
            name = place.get("displayName", {}).get("text", "")
            
            if pid in seen_place_ids:
                total_skipped_dupe += 1
                continue
            
            seen_place_ids.add(pid)
            
            if not is_indian_daycare(place):
                continue
            
            total_indian += 1
            listing = parse_place(place)
            
            status = insert_listing(listing)
            if status == "201":
                total_inserted += 1
                print(f"  ✅ {name} ({listing['city']}, {listing['state']})")
            elif status == "409":
                total_skipped_dupe += 1
                print(f"  ⏭ Dupe: {name}")
            else:
                total_failed += 1
                print(f"  ❌ Failed ({status}): {name}")
        
        # Rate limit: be gentle with Google API
        time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print(f"📊 DAYCARE PIPELINE RESULTS")
    print(f"{'='*60}")
    print(f"  Searches run:    {total_searched}")
    print(f"  API calls:       {api_calls}")
    print(f"  Places found:    {total_found}")
    print(f"  Indian matches:  {total_indian}")
    print(f"  Inserted:        {total_inserted}")
    print(f"  Skipped (dupe):  {total_skipped_dupe}")
    print(f"  Failed:          {total_failed}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
