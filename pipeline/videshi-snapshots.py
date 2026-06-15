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
    """DEPRECATED. The DiasporaPhotoStrip component no longer hardcodes a
    `const PHOTOS` array — it fetches /data/snapshots-pool.json at runtime and
    does a date-stable client-side shuffle to pick the display set. So there is
    nothing to patch in the .tsx anymore. Kept as a no-op shim for any caller."""
    return True


def cmd_rotate():
    """Rotation is now handled client-side by the component (date-stable shuffle
    over snapshots-pool.json). This command just validates the pool is healthy
    so the cron has a meaningful success/failure signal."""
    pool = load_pool()
    if not pool:
        print(f"ERROR: snapshots pool is empty or missing at {POOL_PATH}")
        sys.exit(1)
    if len(pool) < DISPLAY_COUNT:
        print(f"WARNING: pool has {len(pool)} photos, fewer than display count {DISPLAY_COUNT} "
              f"— strip will show all of them.")
    else:
        print(f"OK: snapshots pool healthy ({len(pool)} photos). "
              f"Component rotates {DISPLAY_COUNT}/day client-side (date-stable shuffle); "
              f"no component patching needed.")


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
