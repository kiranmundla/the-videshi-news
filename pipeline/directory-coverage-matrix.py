#!/usr/bin/env python3
"""Directory coverage matrix: prove every category is covered across the USA.

600 cells = 50 states x 12 categories. For each cell:
  - listing_count: rows in directory_listings WHERE state=<ST> AND category=<CAT>
  - last_swept: latest ts from pipeline/.state/sweep-log.jsonl for (state, category)
  - status: "covered" (count>0) | "swept_empty" (searched, nothing found) | "unswept"

Usage:
  python3 -u pipeline/directory-coverage-matrix.py --update   # rebuild matrix from DB + sweep log
  python3 -u pipeline/directory-coverage-matrix.py --report   # print summary from saved matrix
  python3 -u pipeline/directory-coverage-matrix.py --update --report  # both
"""
import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(HERE, ".state")
SWEEP_LOG = os.path.join(STATE_DIR, "sweep-log.jsonl")
MATRIX_PATH = os.path.join(STATE_DIR, "coverage-matrix.json")

CATEGORIES = [
    "Doctors & Healthcare",
    "Attorneys & Immigration",
    "Real Estate",
    "Tax & Accounting",
    "Catering & Food",
    "Yoga & Wellness",
    "Beauty & Grooming",
    "Education & Tutoring",
    "Religious Services",
    "Home Services",
    "Daycare & Childcare",
    "Event Venues",
]


def get_states():
    """Parse STATE_CITIES keys from expand-directory.py."""
    src = open(os.path.join(HERE, "expand-directory.py")).read()
    m = re.search(r'STATE_CITIES = \{(.*?)\n\}', src, re.S)
    return sorted(re.findall(r'"([A-Z]{2})":', m.group(1)))


def load_env():
    env = {}
    for name in ("supabase",):
        p = os.path.expanduser(f"~/workspace/.env.{name}")
        if os.path.exists(p):
            for line in open(p):
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


def curl_json(url, headers):
    r = subprocess.run(
        ["curl", "-sS", url,
         "-H", f"apikey: {headers['key']}",
         "-H", f"Authorization: Bearer {headers['key']}"],
        capture_output=True, text=True, timeout=60)
    return json.loads(r.stdout)


def fetch_cell_counts(states, env):
    """Fetch all (state, category) pairs in bulk pages, count locally."""
    base = env["SUPABASE_URL"].rstrip("/")
    counts = defaultdict(int)
    total = 0
    offset = 0
    while True:
        url = (f"{base}/rest/v1/directory_listings"
               f"?select=state,category&order=id&limit=1000&offset={offset}")
        rows = curl_json(url, {"key": env["SUPABASE_SERVICE_ROLE_KEY"]})
        if not rows:
            break
        for r in rows:
            st, cat = r.get("state"), r.get("category")
            if st in states and cat in CATEGORIES:
                counts[(st, cat)] += 1
        total += len(rows)
        offset += 1000
        if len(rows) < 1000:
            break
    return counts, total


def load_sweep_log():
    """Latest sweep timestamp per (state, category)."""
    latest = {}
    if not os.path.exists(SWEEP_LOG):
        return latest
    with open(SWEEP_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            key = (e.get("state"), e.get("category"))
            if key[0] and key[1]:
                ts = e.get("ts", "")
                if ts > latest.get(key, ""):
                    latest[key] = ts
    return latest


def build_matrix():
    env = load_env()
    states = get_states()
    counts, total = fetch_cell_counts(states, env)
    swept = load_sweep_log()

    cells = {}
    for st in states:
        for cat in CATEGORIES:
            n = counts.get((st, cat), 0)
            ts = swept.get((st, cat))
            if n > 0:
                status = "covered"
            elif ts:
                status = "swept_empty"
            else:
                status = "unswept"
            cells[f"{st}|{cat}"] = {
                "state": st, "category": cat,
                "listing_count": n, "last_swept": ts,
                "status": status,
            }
    matrix = {"cells": cells, "total_listings": total,
              "states": states, "categories": CATEGORIES}
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(MATRIX_PATH, "w") as f:
        json.dump(matrix, f)
    return matrix


def print_report(matrix):
    cells = matrix["cells"]
    covered = sum(1 for c in cells.values() if c["status"] == "covered")
    empty = sum(1 for c in cells.values() if c["status"] == "swept_empty")
    unswept = sum(1 for c in cells.values() if c["status"] == "unswept")
    total = len(cells)
    print(f"Coverage: {covered}/{total} cells covered, "
          f"{empty} swept-empty, {unswept} unswept")

    # Thinnest categories nationally
    cat_totals = defaultdict(int)
    for c in cells.values():
        cat_totals[c["category"]] += c["listing_count"]
    print("\nListings per category (national):")
    for cat, n in sorted(cat_totals.items(), key=lambda x: x[1]):
        print(f"  {n:6}  {cat}")

    # Emptiest states (fewest covered cells)
    state_covered = defaultdict(int)
    for c in cells.values():
        if c["status"] == "covered":
            state_covered[c["state"]] += 1
    print("\n10 emptiest states (covered cells / 12):")
    for st, n in sorted(state_covered.items(), key=lambda x: x[1])[:10]:
        print(f"  {st}: {n}/12")

    # 10 emptiest cells (unswept first, then swept-empty)
    def emptiness(c):
        return (0 if c["status"] == "unswept" else 1, c["listing_count"])
    print("\n10 emptiest cells:")
    for key in sorted(cells, key=lambda k: emptiness(cells[k]))[:10]:
        c = cells[key]
        print(f"  {c['state']:3} {c['category']:22} {c['status']:11} "
              f"count={c['listing_count']} swept={c['last_swept'] or '-'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    if not args.update and not args.report:
        args.update = True

    matrix = None
    if args.update:
        matrix = build_matrix()
        print(f"Matrix rebuilt: {MATRIX_PATH}")
    if args.report:
        if matrix is None:
            if not os.path.exists(MATRIX_PATH):
                print("No saved matrix — run with --update first.", file=sys.stderr)
                sys.exit(1)
            matrix = json.load(open(MATRIX_PATH))
        print_report(matrix)


if __name__ == "__main__":
    main()
