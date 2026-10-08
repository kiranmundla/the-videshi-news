#!/usr/bin/env python3 -u
"""Directory coverage check: does ANY random US zipcode have listings nearby?

Samples N random US zipcodes (fixed seed for reproducibility), geocodes each
via zippopotam (free, no key), and for each directory category measures the
haversine distance to the nearest listing in our DB.

Output: per-category % of sampled zipcodes with a listing within
25mi / 50mi / 100mi, worst-covered zipcodes per category, and a
machine-readable gap list for the expander to target.

Uses NO Places API calls (DB + zippopotam only).

Run: python3 -u pipeline/directory-coverage-check.py [--zips N] [--seed S]
"""
import json
import math
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(REPO, "pipeline", ".state")
ZIP_CACHE = os.path.join(STATE_DIR, "coverage-zips.json")
GAP_FILE = os.path.join(STATE_DIR, "coverage-gaps.json")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

# Category -> representative query (for gap-closing recommendations)
CATEGORY_QUERY = {
    "Catering & Food": "Indian restaurant",
    "Doctors & Healthcare": "Indian doctor",
    "Religious Services": "Hindu temple",
    "Yoga & Wellness": "Indian yoga class",
    "Beauty & Grooming": "Indian beauty salon",
    "Education & Tutoring": "Indian tutoring center",
    "Event Venues": "Indian banquet hall",
    "Attorneys & Immigration": "Indian immigration lawyer",
    "Tax & Accounting": "Indian CPA accountant",
    "Real Estate": "Indian real estate agent",
    "Home Services": "Indian handyman",
    "Daycare & Childcare": "Indian daycare",
}


def curl_json(url, timeout=15):
    try:
        r = subprocess.run(["curl", "-sS", "--max-time", str(timeout), url],
                           capture_output=True, text=True, timeout=timeout + 5)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except Exception:
        return None


def sb_select(table, select, extra=""):
    host = SUPABASE_URL.replace("https://", "")
    key = SUPABASE_KEY
    out, off = [], 0
    while True:
        url = (f"https://{host}/rest/v1/{table}?select={select}"
               f"&offset={off}&limit=1000{extra}")
        r = subprocess.run(
            ["curl", "-sS", url, "-H", f"apikey: {key}",
             "-H", f"Authorization: Bearer {key}"],
            capture_output=True, text=True, timeout=30)
        try:
            rows = json.loads(r.stdout)
        except Exception:
            rows = []
        if not rows:
            break
        out.extend(rows)
        off += 1000
        if len(rows) < 1000:
            break
    return out


def haversine_mi(lat1, lon1, lat2, lon2):
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    dlat, dlon = rlat2 - rlat1, rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(a))


def geocode_zip(z):
    d = curl_json(f"https://api.zippopotam.us/us/{z:05d}")
    if not d or not d.get("places"):
        return None
    p = d["places"][0]
    try:
        return {"zip": f"{z:05d}", "city": p["place name"],
                "state": p["state abbreviation"],
                "lat": float(p["latitude"]), "lon": float(p["longitude"])}
    except (KeyError, ValueError):
        return None


def sample_zips(n, seed):
    """Random valid US zips, reproducible via seed. Cached on disk."""
    os.makedirs(STATE_DIR, exist_ok=True)
    if os.path.exists(ZIP_CACHE):
        try:
            cached = json.load(open(ZIP_CACHE))
            if cached.get("seed") == seed and len(cached.get("zips", [])) >= n:
                return cached["zips"][:n]
        except Exception:
            pass
    rng = random.Random(seed)
    # US zips live roughly in 00501..99950; validate candidates via zippopotam
    candidates = set()
    while len(candidates) < n * 8:
        candidates.add(rng.randint(501, 99950))
    zips = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        for g in ex.map(geocode_zip, sorted(candidates)):
            if g:
                zips.append(g)
            if len(zips) >= n:
                break
    zips = zips[:n]
    json.dump({"seed": seed, "zips": zips}, open(ZIP_CACHE, "w"))
    return zips


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--zips", type=int, default=250)
    ap.add_argument("--sample", type=int, default=None, help="Alias for --zips (sample size)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    if args.sample is not None:
        args.zips = args.sample

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set", flush=True)
        sys.exit(1)

    print(f"Sampling {args.zips} random US zipcodes (seed {args.seed})...", flush=True)
    zips = sample_zips(args.zips, args.seed)
    print(f"  geocoded {len(zips)} valid zips", flush=True)

    print("Loading directory listings...", flush=True)
    rows = sb_select("directory_listings", "latitude,longitude,category")
    listings = [(r["latitude"], r["longitude"], r["category"])
                for r in rows
                if r.get("latitude") and r.get("longitude") and r.get("category")]
    print(f"  {len(listings)} listings with coordinates", flush=True)
    cats = sorted({c for _, _, c in listings} | set(CATEGORY_QUERY))

    # Precompute radians for speed
    lats = [math.radians(la) for la, _, _ in listings]
    lons = [math.radians(lo) for _, lo, _ in listings]
    lcat = [c for _, _, c in listings]

    results = {}  # zip -> {cat: min_dist_mi}
    worst = {c: [] for c in cats}  # cat -> [(dist, zip, city, state)]
    t0 = time.time()
    for i, z in enumerate(zips):
        zlat, zlon = math.radians(z["lat"]), math.radians(z["lon"])
        # vector-ish loop in pure python
        best = {}
        for la, lo, c in zip(lats, lons, lcat):
            dlat, dlon = la - zlat, lo - zlon
            a = math.sin(dlat / 2) ** 2 + math.cos(zlat) * math.cos(la) * math.sin(dlon / 2) ** 2
            d = 3958.8 * 2 * math.asin(math.sqrt(a))
            if c not in best or d < best[c]:
                best[c] = d
        results[z["zip"]] = {"geo": z, "best": best}
        for c, d in best.items():
            worst[c].append((d, z["zip"], z["city"], z["state"]))
        if (i + 1) % 50 == 0:
            print(f"  ...{i + 1}/{len(zips)} ({time.time()-t0:.0f}s)", flush=True)

    print(f"\nComputed in {time.time()-t0:.0f}s", flush=True)
    print("\n" + "=" * 72)
    print(f"COVERAGE — {len(zips)} random US zipcodes, {len(listings)} listings")
    print("=" * 72)
    print(f"{'Category':<22} {'<=25mi':>8} {'<=50mi':>8} {'<=100mi':>9} {'median':>8}")
    print("-" * 72)
    summary = {}
    for c in sorted(CATEGORY_QUERY):
        ds = sorted(results[z]["best"].get(c, float("inf")) for z in results)
        n = len(ds)
        p25 = sum(1 for d in ds if d <= 25) / n * 100
        p50 = sum(1 for d in ds if d <= 50) / n * 100
        p100 = sum(1 for d in ds if d <= 100) / n * 100
        med = ds[n // 2] if n else float("inf")
        summary[c] = {"p25": p25, "p50": p50, "p100": p100,
                      "median_mi": None if med == float("inf") else round(med, 1)}
        med_s = "inf" if med == float("inf") else f"{med:.0f}mi"
        print(f"{c:<22} {p25:>7.1f}% {p50:>7.1f}% {p100:>8.1f}% {med_s:>8}")

    print("\n" + "-" * 72)
    print("WORST-COVERED ZIPCODES PER CATEGORY (gap-closing targets)")
    print("-" * 72)
    gaps = []
    for c in sorted(CATEGORY_QUERY):
        wl = sorted(worst.get(c, []), reverse=True)[:5]
        print(f"\n{c}:")
        for d, z, city, st in wl:
            q = CATEGORY_QUERY[c]
            print(f"  {z} ({city}, {st}): nearest {d:.0f} mi  ->  \"{q} in {city}, {st}\"")
            gaps.append({"zip": z, "city": city, "state": st, "category": c,
                         "query": f"{q} in {city}, {st}",
                         "nearest_mi": round(d, 1)})
    gaps.sort(key=lambda g: -g["nearest_mi"])
    json.dump({"built": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "zips_sampled": len(zips), "seed": args.seed,
               "summary": summary, "gaps": gaps[:50]},
              open(GAP_FILE, "w"), indent=1)
    print(f"\nGap list ({len(gaps[:50])} targets) -> {GAP_FILE}")


if __name__ == "__main__":
    main()
