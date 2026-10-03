#!/usr/bin/env python3
"""
Expand The Videshi kids_local_places with Google Places searches
for Indian/diaspora-focused kids activities across all US states.
Uses curl for HTTP (proxy-safe). Shares the daily Places API budget
with the directory expander via pipeline/places_budget.py.
"""
import json
import os
import re
import subprocess
import sys
import time
import logging
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from indian_relevance import is_indian_business
from places_budget import check_budget, record_call, budget_remaining
import atexit as _atexit
def _budget_report():
    u, l = __import__("places_budget").get_usage()
    if u > 0: print(f"Places API budget: {u}/{l} calls used today")
_atexit.register(_budget_report)

# Reuse the 50-state city map from the directory expander
_spec = importlib.util.spec_from_file_location(
    "expand_directory", os.path.join(os.path.dirname(os.path.abspath(__file__)), "expand-directory.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
STATE_CITIES = _mod.STATE_CITIES

GKEY = "AIzaSyB-KBpDQExIKfEl4J4fxUVMBviTpY7tfZ8"
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

LOG_FILE = "/tmp/kids-expansion.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, mode="w"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# (query, category, subcategory) — Indian/diaspora-focused kids activities
SEARCH_QUERIES = [
    ("Bharatanatyam dance class kids", "Dance", "Bharatanatyam"),
    ("Kathak dance class children", "Dance", "Kathak"),
    ("Bollywood dance class kids", "Dance", "Bollywood"),
    ("Indian classical dance school", "Dance", "Indian Classical"),
    ("Carnatic music class kids", "Music", "Carnatic"),
    ("Hindustani music class children", "Music", "Hindustani"),
    ("tabla lessons kids", "Music", "Tabla"),
    ("Hindi language class kids", "Language", "Hindi"),
    ("Tamil language school children", "Language", "Tamil"),
    ("Telugu classes kids", "Language", "Telugu"),
    ("cricket coaching kids", "Sports", "Cricket"),
    ("chess coaching children", "Sports", "Chess"),
    ("Indian art class kids", "Arts", "Indian Art"),
    ("Indian daycare", "Daycare", "Indian Daycare"),
    ("Indian preschool", "Daycare", "Preschool"),
    ("Indian tutoring center", "Tutoring", "Tutoring"),
]


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
    if not check_budget():
        log.warning(f"Places API daily budget exhausted ({budget_remaining()} remaining). Skipping search.")
        return {"status": "BUDGET_EXHAUSTED", "results": []}
    import urllib.parse
    params = {"query": query, "key": GKEY}
    if page_token:
        params["pagetoken"] = page_token
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?{urllib.parse.urlencode(params)}"
    r = curl_json(url)
    record_call()
    return r or {"status": "ERROR", "results": []}


def photo_urls(photos):
    return [f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={p['photo_reference']}&key={GKEY}"
            for p in photos[:3] if p.get("photo_reference")]


def fetch_existing_ids():
    ids = set()
    for off in range(0, 20000, 1000):
        url = f"{SUPABASE_URL}/rest/v1/kids_local_places?select=slug&offset={off}&limit=1000"
        data = curl_json(url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
        if not data or not isinstance(data, list):
            break
        for d in data:
            if d.get("slug"):
                ids.add(d["slug"])
        if len(data) < 1000:
            break
    log.info(f"Loaded {len(ids)} existing kids place slugs")
    return ids


def insert_batch(places):
    if not places:
        return 0
    ok = 0
    url = f"{SUPABASE_URL}/rest/v1/kids_local_places?on_conflict=slug"
    hdrs = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal"}
    for i in range(0, len(places), 50):
        batch = places[i:i+50]
        code = curl_post(url, hdrs, json.dumps(batch))
        if code in (200, 201):
            ok += len(batch)
        else:
            log.warning(f"Insert returned {code} for batch of {len(batch)}")
        time.sleep(0.2)
    return ok


def process(result, cat, subcat, seen):
    pid = result.get("place_id")
    if not pid:
        return None
    name = result.get("name", "").strip()
    addr = result.get("formatted_address", "")
    if not name or not addr or "USA" not in addr:
        return None
    p = parse_address(addr)
    if not p["city"] or not p["state"]:
        return None

    slug = slugify(f"{name}-{p['city']}", pid)
    if slug in seen:
        return None

    # Indian/diaspora relevance gate — flag but don't hard-require for
    # generic kids queries (chess, cricket often Indian-run)
    is_relevant, _ = is_indian_business(name, cat)
    if not is_relevant:
        rating = result.get("rating") or 0
        reviews = result.get("user_ratings_total") or 0
        if rating < 4.0 or reviews < 5:
            return None

    loc = result.get("geometry", {}).get("location", {})
    pu = photo_urls(result.get("photos", []))

    row = {
        "name": name,
        "category": cat,
        "subcategory": subcat,
        "address": addr,
        "city": p["city"],
        "state": p["state"],
        "zip_code": p["zip"],
        "slug": slug,
        "source": "google_places",
        "latitude": loc.get("lat"),
        "longitude": loc.get("lng"),
        "rating": result.get("rating"),
        "review_count": result.get("user_ratings_total"),
        "image_url": pu[0] if pu else None,
        "is_indian_focused": is_relevant,
        "website": None,
    }
    seen.add(slug)
    return row


def search_city(city, state, query, cat, subcat, seen):
    fq = f"{query} in {city}, {state}"
    out = []
    data = google_search(fq)
    if data.get("status") not in ("OK", "ZERO_RESULTS"):
        return out
    for r in data.get("results", []):
        item = process(r, cat, subcat, seen)
        if item:
            out.append(item)
    tok = data.get("next_page_token")
    if tok:
        time.sleep(2.2)
        data = google_search(fq, page_token=tok)
        if data.get("status") == "OK":
            for r in data.get("results", []):
                item = process(r, cat, subcat, seen)
                if item:
                    out.append(item)
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Expand kids_local_places via Google Places")
    ap.add_argument("--states", help="Comma-separated 2-letter state codes to target (default: all)")
    args = ap.parse_args()

    targets = STATE_CITIES
    if args.states:
        want = {s.strip().upper() for s in args.states.split(",") if s.strip()}
        targets = {s: c for s, c in STATE_CITIES.items() if s in want}
        if not targets:
            log.error(f"No matching states for: {args.states}")
            return
        log.info(f"Targeting states: {sorted(targets)}")

    log.info("=" * 60)
    log.info("Kids Places Expansion (curl-based)")
    log.info(f"{len(targets)} states, {len(SEARCH_QUERIES)} query types")
    log.info("=" * 60)

    seen = fetch_existing_ids()
    total_found = total_ins = 0
    sc = {}

    for state, cities in targets.items():
        buf = []
        log.info(f"\n── {state} ({len(cities)} cities) ──")
        for city in cities:
            cf = 0
            for q, cat, subcat in SEARCH_QUERIES:
                res = search_city(city, state, q, cat, subcat, seen)
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
        if c:
            log.info(f"  {st}: {c}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
