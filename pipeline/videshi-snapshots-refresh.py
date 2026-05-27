#!/usr/bin/env python3
"""
videshi-snapshots-refresh.py — Refresh the Snapshots photo pool with fresh
event-based photos from Pexels. Uploads to Supabase storage and updates
public/data/snapshots-pool.json.

Run: python3 pipeline/videshi-snapshots-refresh.py
"""

import json
import os
import random
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
POOL_FILE = PROJECT_ROOT / "public" / "data" / "snapshots-pool.json"

MAX_POOL_SIZE = 40
QUERIES_PER_RUN = 4
PHOTOS_PER_QUERY = 5

# --- Search query categories (event/culture themed) ---
SEARCH_QUERIES = [
    # Seasonal / timely
    "Indian monsoon rain",
    "Diwali festival lights",
    "Holi celebration colors India",
    "Indian harvest festival Pongal",
    "Indian wedding celebration",
    "Makar Sankranti kite festival",
    "Navratri Garba dance",
    "Onam Kerala celebration",
    "Eid celebration India",
    "Christmas celebration India",
    # Cultural events
    "Indian temple festival",
    "Indian street market bazaar",
    "Indian classical dance Bharatanatyam",
    "Bollywood film set",
    "Indian cricket stadium match",
    "Kathakali dance Kerala",
    "Indian folk music festival",
    "Durga Puja pandal Kolkata",
    "Ganesh Chaturthi procession",
    "Indian Republic Day parade",
    # Diaspora life
    "Indian food festival",
    "yoga meditation India",
    "Indian community celebration",
    "chai tea stall India",
    "Indian bazaar spices",
    "Indian restaurant kitchen",
    "Mehndi henna art",
    "Indian silk saree weaving",
    "Rangoli art floor design",
    "Indian flower market",
    # Landmarks / travel
    "Mumbai Gateway of India",
    "Jaipur Hawa Mahal palace",
    "Kerala houseboat backwaters",
    "Rajasthan desert camel",
    "Himalaya mountains Nepal",
    "Varanasi ghats sunrise",
    "Taj Mahal Agra",
    "Golden Temple Amritsar",
    "Mysore Palace illuminated",
    "Hampi ruins Karnataka",
    "Ladakh monastery",
    "Goa beach sunset India",
    "Rishikesh bridge Ganges",
    "Udaipur Lake Palace",
    "Jodhpur blue city",
]


def load_env(path: str) -> dict:
    """Read a .env file into a dict."""
    env = {}
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env


def search_pexels(query: str, api_key: str) -> list[dict]:
    """Search Pexels API using curl (urllib gets 403)."""
    from urllib.parse import quote
    encoded_query = quote(query)
    result = subprocess.run(
        [
            "curl", "-sS",
            f"https://api.pexels.com/v1/search?query={encoded_query}&orientation=landscape&per_page={PHOTOS_PER_QUERY}",
            "-H", f"Authorization: {api_key}",
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"  ✗ curl failed for query '{query}': {result.stderr[:100]}")
        return []
    try:
        data = json.loads(result.stdout)
        return data.get("photos", [])
    except json.JSONDecodeError:
        print(f"  ✗ Invalid JSON from Pexels for query '{query}'")
        return []


def download_image(url: str, dest: str) -> bool:
    """Download image via curl to a local path."""
    result = subprocess.run(
        ["curl", "-sS", "-L", "-o", dest, url],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0 or not os.path.exists(dest) or os.path.getsize(dest) < 5000:
        return False
    return True


def upload_to_supabase(local_path: str, remote_name: str, supabase_url: str, supabase_key: str) -> str | None:
    """Upload image to Supabase storage. Returns public URL or None."""
    storage_path = f"diaspora/snapshots/{remote_name}"
    upload_url = f"{supabase_url}/storage/v1/object/article-images/{storage_path}"

    result = subprocess.run(
        [
            "curl", "-sS", "-X", "POST", upload_url,
            "-H", f"apikey: {supabase_key}",
            "-H", f"Authorization: Bearer {supabase_key}",
            "-H", "Content-Type: image/jpeg",
            "--data-binary", f"@{local_path}",
        ],
        capture_output=True, text=True, timeout=60,
    )

    # Check for errors — Supabase returns JSON with error on failure
    if result.returncode != 0:
        print(f"  ✗ Upload failed: {result.stderr[:100]}")
        return None

    try:
        resp = json.loads(result.stdout)
        if "error" in resp or "statusCode" in resp:
            # If duplicate, try upsert
            if "Duplicate" in resp.get("message", "") or "already exists" in resp.get("error", ""):
                # File already exists — just return the public URL
                pass
            else:
                print(f"  ✗ Upload error: {resp}")
                return None
    except json.JSONDecodeError:
        pass  # Non-JSON response is fine (204 No Content on success)

    public_url = f"{supabase_url}/storage/v1/object/public/article-images/{storage_path}"
    return public_url


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text[:60].strip("-")


def main():
    print("=== Snapshots Pool Refresh ===")

    # Load credentials
    pexels_env = load_env("~/workspace/.env.pexels")
    supabase_env = load_env("~/workspace/.env.supabase")

    pexels_key = pexels_env.get("PEXELS_API_KEY")
    supabase_url = supabase_env.get("SUPABASE_URL")
    supabase_key = supabase_env.get("SUPABASE_SERVICE_ROLE_KEY")

    if not pexels_key:
        print("ERROR: PEXELS_API_KEY not found in ~/workspace/.env.pexels")
        sys.exit(1)
    if not supabase_url or not supabase_key:
        print("ERROR: Supabase creds not found in ~/workspace/.env.supabase")
        sys.exit(1)

    # Load current pool
    pool = []
    if POOL_FILE.exists():
        try:
            pool = json.loads(POOL_FILE.read_text())
        except json.JSONDecodeError:
            print("  Warning: corrupt pool JSON, starting fresh with curated only")
            pool = []

    curated = [p for p in pool if p.get("source") == "curated"]
    auto_added = [p for p in pool if p.get("source") != "curated"]

    # Track existing Pexels photo IDs to avoid duplicates
    existing_srcs = {p["src"] for p in pool}

    print(f"  Pool: {len(curated)} curated + {len(auto_added)} auto-added = {len(pool)} total")

    # Pick random queries for this run
    queries = random.sample(SEARCH_QUERIES, min(QUERIES_PER_RUN, len(SEARCH_QUERIES)))
    print(f"  Queries: {queries}")

    new_photos = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for query in queries:
            print(f"\n  Searching: '{query}'")
            results = search_pexels(query, pexels_key)
            print(f"  → {len(results)} results")

            for photo in results:
                pexels_id = photo.get("id")
                photographer = photo.get("photographer", "Pexels")
                # Prefer large2x (1880px) > large (940px)
                img_url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                alt = photo.get("alt", "")

                if not img_url or not pexels_id:
                    continue

                # Generate filename from query + pexels ID
                filename = f"{slugify(query)}-{pexels_id}.jpg"

                # Check if we already have this photo
                expected_url_suffix = f"diaspora/snapshots/{filename}"
                if any(expected_url_suffix in s for s in existing_srcs):
                    print(f"    Skip (already in pool): {filename}")
                    continue

                # Download
                local_path = os.path.join(tmpdir, filename)
                if not download_image(img_url, local_path):
                    print(f"    Skip (download failed): {filename}")
                    continue

                # Upload to Supabase
                public_url = upload_to_supabase(local_path, filename, supabase_url, supabase_key)
                if not public_url:
                    print(f"    Skip (upload failed): {filename}")
                    continue

                # Build label from alt text or query + photographer
                label = alt.strip() if alt else query.replace("-", " ").title()
                label = f"{label} · 📷 {photographer}"

                new_photos.append({
                    "src": public_url,
                    "label": label,
                    "source": "pexels",
                    "added_date": date.today().isoformat(),
                    "pexels_id": pexels_id,
                })
                existing_srcs.add(public_url)
                print(f"    ✓ Added: {filename} ({photographer})")

                # Cap new photos per run to fill available slots
                max_auto_slots = MAX_POOL_SIZE - len(curated)
                if len(auto_added) + len(new_photos) >= max_auto_slots:
                    break

            max_auto_slots = MAX_POOL_SIZE - len(curated)
            if len(auto_added) + len(new_photos) >= max_auto_slots:
                print("  → Pool full, stopping search")
                break

    if not new_photos:
        print("\n  No new photos added this run.")
        return

    # Merge: curated (always kept) + auto_added + new, capped at MAX_POOL_SIZE
    all_auto = auto_added + new_photos
    max_auto_slots = MAX_POOL_SIZE - len(curated)
    if len(all_auto) > max_auto_slots:
        # FIFO: keep the newest, drop the oldest auto-added
        all_auto = all_auto[-max_auto_slots:]

    final_pool = curated + all_auto
    POOL_FILE.write_text(json.dumps(final_pool, indent=2, ensure_ascii=False) + "\n")

    print(f"\n  ✅ Added {len(new_photos)} new photos")
    print(f"  Pool now: {len(curated)} curated + {len(all_auto)} auto-added = {len(final_pool)} total")
    print(f"  Wrote {POOL_FILE}")


if __name__ == "__main__":
    main()
