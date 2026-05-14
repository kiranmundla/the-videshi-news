#!/usr/bin/env python3
"""
videshi-snapshots.py — Refresh the Snapshots photo strip on the homepage.

Maintains a curated pool of editorial/cultural photos in snapshots-pool.json.
Each refresh picks 20 photos randomly from the pool so the strip feels fresh
without showing the same article thumbnails that are already on the page.

Usage:
    python3 videshi-snapshots.py                  # Rotate selection from pool
    python3 videshi-snapshots.py add <url> <label> # Add a photo to the pool
"""

import json
import os
import random
import re
import sys

POOL_PATH = os.path.join(os.path.dirname(__file__), "..", "public", "data", "snapshots-pool.json")
COMPONENT_PATH = os.path.expanduser(
    "~/workspace/the-videshi-news/src/components/DiasporaPhotoStrip.tsx"
)
DISPLAY_COUNT = 20


def load_pool():
    if os.path.exists(POOL_PATH):
        with open(POOL_PATH) as f:
            return json.load(f)
    return []


def save_pool(pool):
    os.makedirs(os.path.dirname(POOL_PATH), exist_ok=True)
    with open(POOL_PATH, "w") as f:
        json.dump(pool, f, indent=2)


def update_component(entries):
    with open(COMPONENT_PATH, "r") as f:
        content = f.read()

    lines = []
    for e in entries:
        src = e["src"].replace('"', '\\"')
        label = e["label"].replace('"', '\\"')
        lines.append(f'  {{ src: "{src}", label: "{label}" }}')

    new_array = "const PHOTOS: { src: string; label: string }[] = [\n"
    new_array += ",\n".join(lines)
    new_array += ",\n];"

    pattern = r"const PHOTOS: \{ src: string; label: string \}\[\] = \[[\s\S]*?\];"
    if not re.search(pattern, content):
        print("ERROR: Could not find PHOTOS array in component")
        return False

    new_content = re.sub(pattern, new_array, content)
    with open(COMPONENT_PATH, "w") as f:
        f.write(new_content)
    return True


def cmd_rotate():
    pool = load_pool()
    if len(pool) < DISPLAY_COUNT:
        print(f"Pool has {len(pool)} photos, need at least {DISPLAY_COUNT}. Showing all.")
        selection = pool[:]
    else:
        selection = random.sample(pool, DISPLAY_COUNT)

    random.shuffle(selection)

    if update_component(selection):
        print(f"Rotated {len(selection)} photos from pool of {len(pool)}")
    else:
        print("Failed to update component")


def cmd_add(url, label):
    pool = load_pool()
    # Check for duplicate URL
    if any(p["src"] == url for p in pool):
        print(f"Already in pool: {url}")
        return
    pool.append({"src": url, "label": label})
    save_pool(pool)
    print(f"Added to pool ({len(pool)} total): {label}")


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "add":
        cmd_add(sys.argv[2], " ".join(sys.argv[3:]))
    else:
        cmd_rotate()


if __name__ == "__main__":
    main()
