#!/usr/bin/env python3
"""
Backfill focal_x / focal_y / img_w / img_h for existing p2_articles.

Downloads each hero image, runs focal-point detection, and PATCHes the row.
Processes articles where focal_x is still the default 0.5 and image_url exists.
"""

import os, sys, json, time, subprocess, urllib.parse
from focal_point import compute_focal_point, image_dimensions

def env(k):
    v = os.environ.get(k)
    if not v:
        sys.exit(f"Missing env var: {k}")
    return v

SUPABASE_URL = env("SUPABASE_URL")
SUPABASE_KEY = env("SUPABASE_SERVICE_ROLE_KEY")
API = SUPABASE_URL.rstrip("/")

def supabase_get(path):
    cmd = [
        "curl", "-sS",
        f"{API}/rest/v1/{path}",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Accept: application/json",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout) if r.stdout.strip() else []

def supabase_patch(table, id_val, data):
    cmd = [
        "curl", "-sS", "-X", "PATCH",
        f"{API}/rest/v1/{table}?id=eq.{id_val}",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal",
        "-d", json.dumps(data),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return r.returncode == 0

def download_image(url):
    """Download image bytes via curl."""
    try:
        cmd = ["curl", "-sS", "-L", "--max-time", "10",
               "-A", "TheVideshi/1.0 (thevideshi.com)", "-o", "-", url]
        r = subprocess.run(cmd, capture_output=True, timeout=15)
        if r.returncode == 0 and len(r.stdout) > 1000:
            return r.stdout
    except Exception as e:
        print(f"    ⚠ download error: {e}")
    return None

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100, help="batch size")
    parser.add_argument("--offset", type=int, default=0, help="starting offset")
    parser.add_argument("--all", action="store_true", help="process ALL articles (not just default focal)")
    args = parser.parse_args()

    # Fetch articles that need focal point data
    if args.all:
        path = f"p2_articles?select=id,image_url&image_url=not.is.null&order=published_at.desc&limit={args.limit}&offset={args.offset}"
    else:
        path = f"p2_articles?select=id,image_url&image_url=not.is.null&focal_x=eq.0.5&focal_y=eq.0.5&order=published_at.desc&limit={args.limit}&offset={args.offset}"

    articles = supabase_get(path)
    print(f"Found {len(articles)} articles to process")

    done = 0
    skipped = 0
    errors = 0

    for i, a in enumerate(articles):
        img_url = a.get("image_url", "")
        if not img_url or len(img_url) < 10:
            skipped += 1
            continue

        print(f"[{i+1}/{len(articles)}] {a['id'][:8]}... ", end="", flush=True)

        img_bytes = download_image(img_url)
        if not img_bytes:
            print("⚠ download failed")
            errors += 1
            continue

        fx, fy = compute_focal_point(img_bytes)
        w, h = image_dimensions(img_bytes)

        patch = {"focal_x": fx, "focal_y": fy}
        if w > 0 and h > 0:
            patch["img_w"] = w
            patch["img_h"] = h

        ok = supabase_patch("p2_articles", a["id"], patch)
        if ok:
            face_flag = "👤" if (fx != 0.5 or fy != 0.5) else "📐"
            print(f"{face_flag} ({fx}, {fy}) {w}×{h}")
            done += 1
        else:
            print("⚠ patch failed")
            errors += 1

        # Small delay to be kind to Supabase
        time.sleep(0.1)

    print(f"\n✅ Done: {done} updated, {skipped} skipped, {errors} errors")

if __name__ == "__main__":
    main()
