#!/usr/bin/env python3 -u
"""Scrape US Hindu temple DIRECTORIES into directory_listings.

(Distinct from scrape-temples.py, which scrapes temple EVENTS into the
events table from per-temple websites listed in event_sources.)

Sources (polite: 2.5s+ between requests, cached 7d):
  1. lokgeets.com Hindu temple directory (state-wise, name/address/phone)
  2. Wikipedia "List of Hindu temples in the United States" (supplement)

Quality gate: dedupe vs existing directory_listings (name+city fuzzy),
US address validation. Temples are inherently Indian-relevant.
Geocodes via Google Geocoding API ($5/1000).

Tradition inferred from name keywords.

Run: python3 -u pipeline/scrape-temple-directory.py [--dry-run] [--no-insert]
Writes: inserts into directory_listings, category='Religious Services',
        source='scrape-temple-directory'.
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

LOKGEETS_URL = "https://lokgeets.com/hindu-temples-near-me-usa-complete-directory/"
WIKI_API = "https://en.wikipedia.org/w/api.php"

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
GKEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")

# tradition keywords (checked in order)
TRADITIONS = [
    ("Swaminarayan", ["swaminarayan", "baps", "akshardham"]),
    ("ISKCON", ["iskcon", "hare krishna", "krishna temple", "radha"]),
    ("Shirdi Sai", ["sai baba", "shirdi"]),
    ("Shaivite", ["shiva", "murugan", "kartikeya", "ganesh", "ganapati", "vinayaka"]),
    ("Vaishnavite", ["venkateswara", "balaji", "vishnu", "lakshmi", "narayan"]),
    ("Shakti", ["durga", "kali", "meenakshi", "mariamman", "ambaji"]),
    ("Jain", ["jain"]),
]


def infer_tradition(name: str) -> str:
    nl = name.lower()
    for trad, kws in TRADITIONS:
        if any(k in nl for k in kws):
            return trad
    return "Hindu (general)"


def curl_get(url: str) -> str:
    out = subprocess.run(
        ["curl", "-sS", "-A", UA, "--max-time", "30", url],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise RuntimeError(f"curl failed for {url}: {out.stderr[:200]}")
    return out.stdout


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


def parse_lokgeets(html: str) -> list[dict]:
    """Parse lokgeets state-wise temple directory."""
    temples = []
    parts = re.split(r'<h3 class="wp-block-heading">([^<]+)</h3>', html)
    for i in range(1, len(parts), 2):
        state = parts[i].strip()
        content = parts[i + 1] if i + 1 < len(parts) else ""
        for m in re.finditer(
            r"<strong>([^<]+)</strong><br>\s*Address:\s*([^<]+?)<br>\s*"
            r"(?:Phone:\s*([^<]+?)<br>\s*)?"
            r'(?:Google Maps:.*?<a href="([^"]+)"[^>]*>)?',
            content,
        ):
            name = re.sub(r"\s+", " ", m.group(1)).strip()
            addr = re.sub(r"\s+", " ", m.group(2)).strip()
            phone = re.sub(r"\s+", " ", (m.group(3) or "")).strip()
            maps = m.group(4) or ""
            temples.append(
                {
                    "name": name,
                    "raw_address": addr,
                    "phone": phone,
                    "maps_url": maps,
                    "state_heading": state,
                    "source": "lokgeets",
                }
            )
    return temples


def parse_address(raw: str) -> dict:
    out = {"address": raw, "city": "", "state": "", "zip": ""}
    m = re.match(r"^(.*?),\s*([^,]+?),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)?\s*$", raw)
    if m:
        out["address"] = m.group(1).strip()
        out["city"] = m.group(2).strip()
        out["state"] = m.group(3).strip()
        out["zip"] = m.group(4) or ""
    return out


def fetch_wikipedia_temples() -> list[dict]:
    """Supplement via MediaWiki API (name + city by state)."""
    params = urllib.parse.urlencode(
        {
            "action": "parse",
            "page": "List of Hindu temples in the United States",
            "format": "json",
            "prop": "text",
        }
    )
    body = cached_fetch("wiki-temples.json", f"{WIKI_API}?{params}")
    data = json.loads(body)
    html = data.get("parse", {}).get("text", {}).get("*", "")
    temples = []
    for sec in re.finditer(r"<h3[^>]*>([^<]+)</h3>(.*?)(?=<h3|$)", html, re.S):
        state = re.sub(r"<[^>]+>", "", sec.group(1)).strip()
        for row in re.finditer(r"<tr>(.*?)</tr>", sec.group(2), re.S):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", row.group(1), re.S)
            if len(cells) >= 2:
                name = re.sub(r"\[\d+\]", "", re.sub(r"<[^>]+>", "", cells[0])).strip()
                loc = re.sub(r"<[^>]+>", "", cells[1]).strip()
                city = re.split(r"\d+\s*°", loc)[0].strip(" ,")
                if name and city and len(name) > 3:
                    temples.append(
                        {
                            "name": name,
                            "raw_address": "",
                            "phone": "",
                            "maps_url": "",
                            "city": city,
                            "state_heading": state,
                            "source": "wikipedia",
                        }
                    )
    return temples


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
        if nn == en or (len(nn) > 10 and len(en) > 10 and (nn in en or en in nn)):
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
        out = subprocess.run(
            ["curl", "-sS", "--max-time", 15, url],
            capture_output=True, text=True,
        )
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

    print("fetching lokgeets...", flush=True)
    html = cached_fetch("lokgeets-temples.html", LOKGEETS_URL)
    temples = parse_lokgeets(html)
    print(f"lokgeets: {len(temples)} parsed", flush=True)

    print("fetching wikipedia supplement...", flush=True)
    try:
        wiki = fetch_wikipedia_temples()
        print(f"wikipedia: {len(wiki)} parsed", flush=True)
        temples.extend(wiki)
    except Exception as e:
        print(f"wikipedia failed: {e}", flush=True)

    for t in temples:
        if t.get("raw_address"):
            t.update(parse_address(t["raw_address"]))
        t.setdefault("city", "")
        t.setdefault("state", "")
        t.setdefault("zip", "")
        t["tradition"] = infer_tradition(t["name"])

    temples = [t for t in temples if t["name"] and len(t["name"]) > 3]
    print(f"total candidates: {len(temples)}", flush=True)

    existing = sb_select("name,city,state", "category=eq.Religious%20Services&limit=5000")
    print(f"existing religious listings: {len(existing)}", flush=True)

    new, skipped_dup, seen = [], 0, set()
    for t in temples:
        key = (norm_name(t["name"]), t["city"].lower())
        if key in seen or already_listed(t["name"], t["city"], existing):
            skipped_dup += 1
            continue
        seen.add(key)
        new.append(t)
    print(f"new: {len(new)}, dupes skipped: {skipped_dup}", flush=True)

    if dry:
        for t in new[:20]:
            print(f"  + {t['name']} | {t.get('address','')}, {t['city']} {t['state']} | {t['tradition']}")
        print("(dry run — no geocode, no insert)")
        return

    inserted, failed = 0, 0
    for i, t in enumerate(new):
        full_addr = ", ".join(
            p for p in [t.get("address"), t.get("city"), t.get("state"), t.get("zip")] if p
        ) or t.get("raw_address", "")
        lat, lon = geocode(full_addr)
        row = {
            "name": t["name"][:200],
            "address": (t.get("address") or "")[:300],
            "city": (t.get("city") or "")[:120],
            "state": (t.get("state") or "")[:10],
            "zip": (t.get("zip") or "")[:12],
            "phone": (t.get("phone") or "")[:40],
            "category": "Religious Services",
            "latitude": lat,
            "longitude": lon,
            "website": "",
            "source": "scrape-temple-directory",
        }
        if no_insert:
            inserted += 1
            continue
        if sb_insert(row):
            inserted += 1
        else:
            failed += 1
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{len(new)} inserted={inserted} failed={failed}", flush=True)

    print(f"DONE inserted={inserted} failed={failed}", flush=True)


if __name__ == "__main__":
    main()
