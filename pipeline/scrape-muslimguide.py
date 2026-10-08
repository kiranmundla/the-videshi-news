#!/usr/bin/env python3 -u
"""Scrape US mosque/musalla listings from muslimguide.com into directory_listings.

muslimguide.com is a US mosque directory with category-browsable listings.
Search is location-based; we query from the geographic center of the
contiguous US with a large radius to cover the entire country in one walk,
then paginate through all results.

Fills the Religious Services gap for Muslim desis.

Polite: 2.5s+ between requests, 7-day cache. robots.txt allows all.

Run: python3 -u pipeline/scrape-muslimguide.py [--dry-run] [--no-insert]
Writes: inserts into directory_listings, category='Religious Services',
        source='scrape-muslimguide'.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(REPO, "pipeline", ".state", "scrape-cache")
os.makedirs(CACHE_DIR, exist_ok=True)

UA = "TheVideshi/1.0 (+https://www.thevideshi.com; directory research)"
DELAY_S = 2.5

BASE = "https://muslimguide.com"
# Geographic center of contiguous US; distance in km (server accepts large values)
US_CENTER = "39.8,-98.5"
RADIUS_KM = "5000"

# category=1 is Places of Worship; subcategories for mosques
SUBCATS = {
    "100": "Mosques and Islamic Centers",
    "102": "Musalla",
    "104": "Friday Prayer Only",
}

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
GKEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")


def curl_get(url: str, retries: int = 3) -> str:
    last_err = ""
    for attempt in range(retries):
        out = subprocess.run(
            ["curl", "-sSL", "-A", UA, "--max-time", "60", url],
            capture_output=True, text=True,
        )
        if out.returncode == 0 and out.stdout:
            return out.stdout
        last_err = out.stderr[:200]
        time.sleep(DELAY_S * (attempt + 1))
    raise RuntimeError(f"curl failed for {url} after {retries} tries: {last_err}")


def cached_fetch(key: str, url: str, max_age_h: float = 168) -> str:
    path = os.path.join(CACHE_DIR, key)
    if os.path.exists(path):
        age_h = (time.time() - os.path.getmtime(path)) / 3600
        if age_h < max_age_h:
            return open(path, encoding="utf-8").read()
    time.sleep(DELAY_S)
    body = curl_get(url)
    open(path, "w", encoding="utf-8").write(body)
    return body


def search_url(subcat: str, page: int = 1) -> str:
    q = urllib.parse.urlencode({
        "category": "1",
        "subCategory": subcat,
        "coors": US_CENTER,
        "distance": RADIUS_KM,
        "page": str(page),
    })
    return f"{BASE}/listing?{q}"


def max_page(html: str) -> int:
    # HTML-encode &amp; appears in pagination hrefs
    text = html.replace("&amp;", "&")
    pages = [int(p) for p in re.findall(r"[?&]page=(\d+)", text)]
    return max(pages) if pages else 1


US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA",
    "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
    "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX",
    "UT", "VT", "VA", "WA", "WV", "WI", "WY",
}


def parse_listings(html: str) -> list[dict]:
    """Parse listing-item blocks: detail URL, title, address."""
    out = []
    for m in re.finditer(
        r'<div class="listing-item-container"[^>]*>\s*'
        r'<a href="([^"]+)"[^>]*>.*?'
        r'<p class="title"[^>]*>([^<]+)</p>.*?'
        r'<span class="address">([^<]+)</span>',
        html, re.S,
    ):
        url, name, addr = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        out.append({"url": url, "name": re.sub(r"\s+", " ", name),
                    "raw_address": re.sub(r"\s+", " ", addr)})
    return out


def parse_address(raw: str) -> dict:
    """muslimguide format: 'street, city, ST, city, ST' (city/state duplicated)."""
    out = {"address": raw, "city": "", "state": "", "zip": ""}
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) >= 3:
        out["address"] = parts[0]
        out["city"] = parts[1]
        st = re.match(r"([A-Z]{2})\b", parts[2])
        if st:
            out["state"] = st.group(1)
        z = re.search(r"(\d{5}(?:-\d{4})?)", raw)
        if z:
            out["zip"] = z.group(1)
    return out


def sb_select_all(select: str, filt: str = "") -> list:
    """Paginate through all rows (Supabase REST caps at 1000/page)."""
    out, offset, step = [], 0, 1000
    while True:
        url = (f"{SUPABASE_URL}/rest/v1/directory_listings"
               f"?select={select}&{filt}&limit={step}&offset={offset}")
        r = subprocess.run(
            ["curl", "-sS", url,
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
            capture_output=True, text=True,
        )
        try:
            batch = json.loads(r.stdout or "[]")
        except Exception:
            break
        out.extend(batch)
        if len(batch) < step:
            break
        offset += step
    return out


def sb_select(select: str, params: str = "") -> list:
    url = f"{SUPABASE_URL}/rest/v1/directory_listings?select={select}&{params}"
    out = subprocess.run(
        ["curl", "-sS", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True,
    )
    try:
        return json.loads(out.stdout or "[]")
    except Exception:
        return []


def sb_insert(row: dict) -> bool:
    out = subprocess.run(
        ["curl", "-sS", "-X", "POST",
         f"{SUPABASE_URL}/rest/v1/directory_listings",
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(row)],
        capture_output=True, text=True,
    )
    return out.returncode == 0 and '"code"' not in out.stdout[:300]


def norm_name(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def already_listed(name: str, city: str, existing: list[dict]) -> bool:
    nn = norm_name(name)
    for e in existing:
        en = norm_name(e.get("name") or "")
        if not en or not nn:
            continue
        if nn == en or (len(nn) > 8 and len(en) > 8 and (nn in en or en in nn)):
            ecity = (e.get("city") or "").lower()
            if not city or not ecity or city.lower() in ecity or ecity in city.lower():
                return True
    return False


def geocode(address: str) -> tuple:
    if not GKEY or not address:
        return None, None
    time.sleep(0.2)
    url = "https://maps.googleapis.com/maps/api/geocode/json?" + urllib.parse.urlencode(
        {"address": address, "key": GKEY}
    )
    try:
        out = subprocess.run(["curl", "-sS", "--max-time", 15, url],
                             capture_output=True, text=True)
        d = json.loads(out.stdout or "{}")
        if d.get("status") == "OK" and d.get("results"):
            loc = d["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
    except Exception:
        pass
    return None, None


def main():
    dry = "--dry-run" in sys.argv
    no_insert = "--no-insert" in sys.argv or dry

    all_listings: dict[str, dict] = {}  # url -> listing (dedupe across subcats)
    for subcat, label in SUBCATS.items():
        print(f"subcat {subcat} ({label})...", flush=True)
        first = cached_fetch(f"mg-subcat{subcat}-p1.html", search_url(subcat, 1))
        pages = max_page(first)
        print(f"  {pages} pages", flush=True)
        for p in range(1, pages + 1):
            html = first if p == 1 else cached_fetch(
                f"mg-subcat{subcat}-p{p}.html", search_url(subcat, p))
            for l in parse_listings(html):
                l["subcat"] = label
                all_listings.setdefault(l["url"], l)
        print(f"  cumulative unique: {len(all_listings)}", flush=True)

    listings = list(all_listings.values())
    print(f"total unique listings: {len(listings)}", flush=True)

    for l in listings:
        l.update(parse_address(l["raw_address"]))

    existing = sb_select_all("name,city,state",
                               "category=eq.Religious%20Services")
    print(f"existing religious listings: {len(existing)}", flush=True)

    new, skipped_dup, skipped_nonus, seen = [], 0, 0, set()
    for l in listings:
        key = (norm_name(l["name"]), l["city"].lower())
        if not l["name"] or key in seen or already_listed(l["name"], l["city"], existing):
            skipped_dup += 1
            continue
        if l["state"] and l["state"] not in US_STATES:
            skipped_nonus += 1
            continue
        seen.add(key)
        new.append(l)
    print(f"new: {len(new)}, dupes skipped: {skipped_dup}, non-US skipped: {skipped_nonus}",
          flush=True)

    # per-state coverage report
    from collections import Counter
    states = Counter(l["state"] for l in new if l["state"])
    print("new listings per state:", dict(sorted(states.items())), flush=True)

    if dry:
        for l in new[:20]:
            print(f"  + {l['name']} | {l['address']}, {l['city']} {l['state']} {l['zip']} | {l['subcat']}")
        print("(dry run — no geocode, no insert)")
        return

    inserted, failed = 0, 0
    for i, l in enumerate(new):
        full_addr = ", ".join(
            p for p in [l["address"], l["city"], l["state"], l["zip"]] if p)
        lat, lon = geocode(full_addr)
        row = {
            "name": l["name"][:200],
            "address": l["address"][:300],
            "city": l["city"][:120],
            "state": l["state"][:10],
            "zip": l["zip"][:12],
            "category": "Religious Services",
            "subcategory": l["subcat"][:80],
            "latitude": lat,
            "longitude": lon,
            "website": l["url"][:300],
            "source": "scrape-muslimguide",
        }
        if no_insert:
            inserted += 1
            continue
        if sb_insert(row):
            inserted += 1
        else:
            failed += 1
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(new)} inserted={inserted} failed={failed}", flush=True)

    print(f"DONE inserted={inserted} failed={failed}", flush=True)


if __name__ == "__main__":
    main()
