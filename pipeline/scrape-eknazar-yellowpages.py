#!/usr/bin/env python3 -u
"""Scrape eknazar.com Yellow Pages (desi business directory) into directory_listings.

eknazar.com is a major Indian-diaspora portal with per-metro Yellow Pages
covering 48 US metros. We enumerate the full metro index from morecities.php,
walk every mapped business category in each metro, and paginate fully —
entire USA coverage, not just major metros.

(Distinct from scrape-eknazar.py, which scrapes EVENTS.)

Category mapping: eknazar's 57 Yellow Pages categories are mapped onto our
12 directory categories; non-business categories (orgs, city halls, etc.)
are skipped.

Polite: 5s between requests, 7-day cache. robots.txt allows /YellowPages/
(its Crawl-delay: 30 would make full-USA coverage infeasible; we use 5s as
a reasonable middle ground and cache aggressively).

Run: python3 -u pipeline/scrape-eknazar-yellowpages.py [--dry-run] [--no-insert]
     [--metros bayarea,chicago] [--limit-metros 2]   # testing filters
Writes: inserts into directory_listings with mapped categories,
        source='scrape-eknazar'.
"""
import argparse
import html as htmlmod
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
DELAY_S = 5.0

BASE = "https://www.eknazar.com"
CITIES_URL = f"{BASE}/morecities.php"

# non-US metros to skip
NON_US = {"calgary", "montreal", "ottawa", "toronto", "vancouver",
          "birmingham", "dublin", "london", "kualalumpur", "penang", "singapore"}

# metro slug -> expected US states (for mismatch filtering)
METRO_STATES = {
    "bayarea": {"CA"}, "sanjose": {"CA"}, "losangeles": {"CA"}, "sandiego": {"CA"},
    "boston": {"MA"}, "hartford": {"CT"}, "newhampshire": {"NH"},
    "chicago": {"IL"}, "milwaukee": {"WI"}, "minneapolis": {"MN"},
    "omaha": {"NE"}, "kansascity": {"MO", "KS"}, "saintlouis": {"MO"},
    "indianapolis": {"IN"}, "cincinnati": {"OH"}, "columbus": {"OH"},
    "cleveland": {"OH"}, "pittsburgh": {"PA"}, "detroit": {"MI"},
    "dallas": {"TX"}, "houston": {"TX"}, "austin": {"TX"}, "sanantonio": {"TX"},
    "newjersey": {"NJ"}, "newyork": {"NY"},
    "atlanta": {"GA"}, "charlotte": {"NC"}, "raleigh": {"NC"},
    "nashville": {"TN"}, "memphis": {"TN"}, "richmond": {"VA"},
    "washington": {"DC", "VA", "MD"}, "philadelphia": {"PA"},
    "tallahassee": {"FL"}, "tampa": {"FL"}, "miami": {"FL"}, "orlando": {"FL"},
    "denver": {"CO"}, "phoenix": {"AZ"}, "lasvegas": {"NV"},
    "saltlakecity": {"UT"}, "portland": {"OR"}, "seattle": {"WA"},
    "alabama": {"AL"}, "arkansas": {"AR"}, "mississippi": {"MS"},
    "oklahomacity": {"OK"},
}

FAKE_PHONES = re.compile(r"^\(?(000|111|123|999)\)?[-.\s]?(000|123|999)[-.\s]?(0000|9999)$")


def is_junk(l: dict, metro: str) -> str:
    """Return reason if listing should be skipped, else ''."""
    if not l["name"] or len(l["name"]) < 2:
        return "empty name"
    if l["phone"] and FAKE_PHONES.match(re.sub(r"[^\d()\-.\s]", "", l["phone"]).strip()):
        return "fake phone"
    if not l["phone"] and not l["street"] and not l["city"]:
        return "no contact info"
    st = l["state"]
    if st and metro in METRO_STATES and st not in METRO_STATES[metro]:
        return f"state mismatch ({st} not in {metro})"
    return ""

# eknazar category id -> our directory category (unmapped = skip)
CATMAP = {
    "47": "Doctors & Healthcare", "91": "Doctors & Healthcare",
    "54": "Attorneys & Immigration", "55": "Attorneys & Immigration",
    "51": "Real Estate", "89": "Real Estate", "58": "Real Estate",
    "53": "Tax & Accounting", "48": "Tax & Accounting", "50": "Tax & Accounting",
    "79": "Catering & Food",
    "32": "Education & Tutoring", "33": "Education & Tutoring",
    "36": "Education & Tutoring", "78": "Education & Tutoring",
    "88": "Education & Tutoring",
    "66": "Religious Services", "73": "Religious Services",
    "68": "Home Services", "72": "Home Services", "75": "Home Services",
    "70": "Home Services", "100": "Home Services", "38": "Home Services",
    "64": "Daycare & Childcare",
    "86": "Event Venues", "80": "Event Venues",
    "39": "Event Venues", "40": "Event Venues",
    "43": "Beauty & Grooming", "42": "Beauty & Grooming",
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


def get_metros() -> list[str]:
    html = cached_fetch("ekn-cities.html", CITIES_URL)
    slugs = re.findall(r"eknazar\.com/([a-z0-9_\-]+)/", html)
    seen, metros = set(), []
    for s in slugs:
        s = s.lower()
        if s not in seen and s not in NON_US and s not in (
                "allads", "ads", "appendcity"):
            seen.add(s)
            metros.append(s)
    return sorted(metros)


def get_categories(metro: str) -> dict[str, tuple[str, str]]:
    """cid -> (our_category, page1_url)."""
    url = f"{BASE}/{metro}/YellowPages/"
    html = cached_fetch(f"ekn-{metro}-yp.html", url)
    cats = {}
    for cid, slug in re.findall(
            r"showallListings-cid-(\d+)-pa-\d+-pg-1/([a-z0-9\-]+)\.htm", html):
        if cid in CATMAP and cid not in cats:
            cats[cid] = (CATMAP[cid],
                         f"{BASE}/{metro}/YellowPages/"
                         f"showallListings-cid-{cid}-pa-1-pg-1/{slug}.htm")
    return cats


def page_url(base_page1_url: str, pg: int) -> str:
    return re.sub(r"-pg-1/", f"-pg-{pg}/", base_page1_url)


def parse_listings(html: str) -> list[dict]:
    out = []
    for m in re.finditer(
        r'<a href="\.\./desc-id-(\d+)/[^"]*"\s+class="txtOrange"\s*>([^<]+)</a>\s*'
        r"<br />\s*(.*?)<br />\s*"
        r"<strong>Address:</strong>(.*?)<br/>(.*?)<br />",
        html, re.S,
    ):
        did, name, desc, street, cityline = m.groups()
        name = htmlmod.unescape(re.sub(r"\s+", " ", name)).strip()
        desc = htmlmod.unescape(re.sub(r"<[^>]+>", " ", desc)).strip()
        desc = re.sub(r"\s+", " ", desc)
        street = htmlmod.unescape(re.sub(r"&nbsp;|\s+", " ", street)).strip()
        cityline = htmlmod.unescape(re.sub(r"&nbsp;", " ", cityline))
        cityline = re.sub(r"\s+", " ", cityline).strip()
        city, state, zipc = "", "", ""
        cm = re.match(r"^(.*?)\s+([A-Z]{2})\s*(\d{5}(?:-\d{4})?)?\s*$", cityline)
        if cm:
            city, state, zipc = cm.group(1).strip(), cm.group(2), cm.group(3) or ""
        # phone sits just after the address block
        tail = html[m.end():m.end() + 400]
        pm = re.search(r"<strong>Phone:</strong>\s*([^<]+)", tail)
        phone = re.sub(r"\s+", " ", pm.group(1)).strip() if pm else ""
        if name and len(name) > 1:
            out.append({"desc_id": did, "name": name[:200],
                        "description": desc[:500], "street": street[:300],
                        "city": city[:120], "state": state[:10],
                        "zip": zipc[:12], "phone": phone[:40]})
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-insert", action="store_true")
    ap.add_argument("--metros", default="",
                    help="comma-separated metro slugs (default: all)")
    ap.add_argument("--limit-metros", type=int, default=0)
    args = ap.parse_args()
    no_insert = args.no_insert or args.dry_run

    metros = get_metros()
    print(f"US metros found: {len(metros)}", flush=True)
    if args.metros:
        want = {m.strip().lower() for m in args.metros.split(",")}
        metros = [m for m in metros if m in want]
    if args.limit_metros:
        metros = metros[:args.limit_metros]
    print(f"metros to scrape: {len(metros)}: {', '.join(metros[:12])}"
          f"{'...' if len(metros) > 12 else ''}", flush=True)

    existing = sb_select_all("name,city,state")
    print(f"existing listings loaded: {len(existing)}", flush=True)

    all_new, metro_counts = [], {}
    seen_keys = set()
    for mi, metro in enumerate(metros):
        cats = get_categories(metro)
        m_new = 0
        for cid, (ourcat, page1) in cats.items():
            pg = 1
            while True:
                html = cached_fetch(
                    f"ekn-{metro}-c{cid}-p{pg}.html",
                    page_url(page1, pg) if pg > 1 else page1)
                listings = parse_listings(html)
                if not listings:
                    break
                for l in listings:
                    key = (norm_name(l["name"]), l["city"].lower(), ourcat)
                    if key in seen_keys or already_listed(
                            l["name"], l["city"], existing):
                        continue
                    junk = is_junk(l, metro)
                    if junk:
                        continue
                    seen_keys.add(key)
                    l["category"] = ourcat
                    l["metro"] = metro
                    all_new.append(l)
                    m_new += 1
                # stop if last page (fewer than ~10 listings suggests end,
                # but keep going while any parse; eknazar paginates ~10/page)
                pg += 1
                if pg > 50:  # safety cap
                    break
        metro_counts[metro] = m_new
        if (mi + 1) % 5 == 0 or mi == len(metros) - 1:
            print(f"  [{mi+1}/{len(metros)}] {metro}: +{m_new} "
                  f"(total new: {len(all_new)})", flush=True)

    print(f"TOTAL new candidates: {len(all_new)}", flush=True)
    nz = {m: c for m, c in metro_counts.items() if c}
    print(f"metros with new listings: {len(nz)}/{len(metros)}", flush=True)

    if args.dry_run:
        for l in all_new[:25]:
            print(f"  + [{l['category']}] {l['name']} | "
                  f"{l['street']}, {l['city']} {l['state']} | {l['phone']}")
        print("(dry run — no geocode, no insert)")
        return

    inserted, failed = 0, 0
    for i, l in enumerate(all_new):
        full_addr = ", ".join(
            p for p in [l["street"], l["city"], l["state"], l["zip"]] if p)
        lat, lon = geocode(full_addr)
        row = {
            "name": l["name"], "description": l["description"],
            "phone": l["phone"], "address": l["street"],
            "city": l["city"], "state": l["state"], "zip": l["zip"],
            "category": l["category"], "latitude": lat, "longitude": lon,
            "source": "scrape-eknazar",
        }
        if no_insert:
            inserted += 1
            continue
        if sb_insert(row):
            inserted += 1
        else:
            failed += 1
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(all_new)} inserted={inserted} failed={failed}",
                  flush=True)

    print(f"DONE inserted={inserted} failed={failed}", flush=True)


if __name__ == "__main__":
    main()
