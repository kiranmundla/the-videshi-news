#!/usr/bin/env python3
"""
videshi-snapshots.py — Refresh the Snapshots photo strip on the homepage.

Pulls the 20 most recent published articles that have images,
generates a new PHOTOS array for DiasporaPhotoStrip.tsx, and writes it.

Usage:
    python3 videshi-snapshots.py
"""

import json
import os
import re
import requests

# Config
SB_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
if not SB_KEY:
    env_file = os.path.expanduser("~/workspace/.env.supabase")
    if os.path.exists(env_file):
        for line in open(env_file):
            if line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                SB_KEY = line.strip().split("=", 1)[1]

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
}

COMPONENT_PATH = os.path.expanduser(
    "~/workspace/the-videshi-news/src/components/DiasporaPhotoStrip.tsx"
)

# Category labels for captions
CAT_LABELS = {
    "news": "India News",
    "nri-world": "NRI World",
    "markets-finance": "Markets",
    "technology": "Technology",
    "sports": "Sports",
    "entertainment": "Entertainment",
    "lifestyle-health": "Lifestyle",
    "travel": "Travel",
    "food": "Food",
}


def fetch_recent_articles_with_images(limit=20):
    """Fetch recent published articles that have images."""
    resp = requests.get(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        params={
            "status": "eq.published",
            "image_url": "not.is.null",
            "category": "neq.travel",  # travel has its own gallery
            "order": "published_at.desc",
            "limit": str(limit + 10),  # fetch extra in case some images are bad
            "select": "headline,image_url,image_attribution,category,published_at",
        },
    )
    resp.raise_for_status()
    articles = resp.json()

    # Filter to articles with valid http image URLs
    valid = []
    for a in articles:
        url = a.get("image_url", "")
        if url and url.startswith("http"):
            valid.append(a)
        if len(valid) >= limit:
            break

    return valid


def build_photo_entries(articles):
    """Build photo entries from articles."""
    entries = []
    for a in articles:
        cat = CAT_LABELS.get(a.get("category", ""), "News")
        headline = a["headline"]
        # Shorten headline for label if too long
        if len(headline) > 60:
            headline = headline[:57] + "..."
        label = f"{headline} · {cat}"
        entries.append({"src": a["image_url"], "label": label})
    return entries


def update_component(entries):
    """Update the PHOTOS array in DiasporaPhotoStrip.tsx."""
    with open(COMPONENT_PATH, "r") as f:
        content = f.read()

    # Build the new PHOTOS array
    lines = []
    for e in entries:
        src = e["src"].replace('"', '\\"')
        label = e["label"].replace('"', '\\"')
        lines.append(f'  {{ src: "{src}", label: "{label}" }}')

    new_array = "const PHOTOS: { src: string; label: string }[] = [\n"
    new_array += ",\n".join(lines)
    new_array += ",\n];"

    # Replace the existing PHOTOS array using regex
    pattern = r"const PHOTOS: \{ src: string; label: string \}\[\] = \[[\s\S]*?\];"
    if not re.search(pattern, content):
        print("ERROR: Could not find PHOTOS array in component")
        return False

    new_content = re.sub(pattern, new_array, content)

    # Also remove the hardcoded SUPABASE_BASE const if present (no longer needed)
    new_content = re.sub(
        r'const SUPABASE_BASE =\n\s*"[^"]*";\n\n', "", new_content
    )

    with open(COMPONENT_PATH, "w") as f:
        f.write(new_content)

    return True


def main():
    print("Fetching recent articles with images...")
    articles = fetch_recent_articles_with_images(20)
    print(f"  Found {len(articles)} articles with images")

    if len(articles) < 5:
        print("  Not enough articles with images, skipping refresh")
        return

    entries = build_photo_entries(articles)
    print(f"  Built {len(entries)} photo entries")

    if update_component(entries):
        print(f"  Updated {COMPONENT_PATH}")
        print("  Done! Commit and push to deploy.")
    else:
        print("  Failed to update component")


if __name__ == "__main__":
    main()
