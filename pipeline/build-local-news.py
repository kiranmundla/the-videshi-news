#!/usr/bin/env python3 -u
"""Build per-metro local news index for Your Hub.

Scans published article JSONs for US metro mentions (city name in
title/excerpt/body) and writes public/data/local-news.json:
  { "metros": { "San Jose, CA": [{slug,title,excerpt,published_at,hero_image_url,category}, ...] } }

Top 5 most recent per metro. Ambiguous city names (Washington, Portland)
require state context to avoid false positives.

Run: python3 -u pipeline/build-local-news.py
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIR = os.path.join(REPO, "public", "data", "articles")
OUT_PATH = os.path.join(REPO, "public", "data", "local-news.json")

# (city, state, [extra aliases]) — mirrors the frontend METRO_PICKER
METROS = [
    ("New York", "NY", ["NYC", "New York City"]),
    ("San Jose", "CA", []),
    ("San Francisco", "CA", ["SF", "Bay Area"]),
    ("Los Angeles", "CA", ["LA"]),
    ("Chicago", "IL", []),
    ("Houston", "TX", []),
    ("Dallas", "TX", ["DFW"]),
    ("Austin", "TX", []),
    ("Seattle", "WA", []),
    ("Boston", "MA", []),
    ("Atlanta", "GA", []),
    ("Washington", "DC", []),   # requires DC context (see below)
    ("Edison", "NJ", []),
    ("Philadelphia", "PA", ["Philly"]),
    ("Miami", "FL", []),
    ("Denver", "CO", []),
    ("Phoenix", "AZ", []),
    ("San Diego", "CA", []),
    ("Minneapolis", "MN", ["Twin Cities"]),
    ("Detroit", "MI", []),
    ("Portland", "OR", []),     # requires Oregon context (see below)
    ("Columbus", "OH", []),
    ("Raleigh", "NC", ["Research Triangle"]),
    ("Tampa", "FL", []),
    ("Las Vegas", "NV", ["Vegas"]),
]

PER_METRO = 5


def compile_patterns():
    compiled = []
    for city, state, aliases in METROS:
        pats = [city] + aliases
        if city == "Washington":
            # "Washington" alone is ambiguous (DC vs state) — require DC context
            rx = re.compile(
                r"\bWashington(?:,?\s+D\.?C\.?|\s+DC\b)|\bD\.?C\.?\b.*\bWashington\b",
                re.IGNORECASE,
            )
        elif city == "Portland":
            # Portland OR vs ME — require Oregon context
            rx = re.compile(
                r"\bPortland\b(?=.{0,60}\b(?:Oregon|\bOR\b))|(?:Oregon|\bOR\b).{0,60}\bPortland\b",
                re.IGNORECASE,
            )
        else:
            alt = "|".join(re.escape(p) for p in pats)
            rx = re.compile(r"\b(?:" + alt + r")\b", re.IGNORECASE)
        compiled.append((f"{city}, {state}", rx))
    return compiled


def main():
    patterns = compile_patterns()
    matches: dict[str, list[dict]] = {label: [] for label, _ in patterns}

    files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".json")]
    scanned = 0
    for fn in files:
        try:
            with open(os.path.join(ARTICLES_DIR, fn), encoding="utf-8") as fh:
                a = json.load(fh)
        except Exception:
            continue
        if a.get("status") != "published":
            continue
        scanned += 1
        hay = " ".join(
            str(a.get(k) or "") for k in ("title", "excerpt", "body")
        )
        if len(hay) < 50:
            continue
        for label, rx in patterns:
            if rx.search(hay):
                matches[label].append(
                    {
                        "slug": a.get("slug"),
                        "title": a.get("title"),
                        "excerpt": a.get("excerpt") or "",
                        "published_at": a.get("published_at") or "",
                        "hero_image_url": a.get("hero_image_url") or "",
                        "category": a.get("category") or "",
                    }
                )

    # keep 5 most recent per metro
    out = {}
    total = 0
    for label, items in matches.items():
        items.sort(key=lambda x: x["published_at"], reverse=True)
        # drop items with no slug
        items = [i for i in items if i["slug"]][:PER_METRO]
        out[label] = items
        total += len(items)

    payload = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "metros": out,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    print(f"scanned={scanned} metros={len(out)} total_matches={total} -> {OUT_PATH}")

    # coverage summary
    empty = [label for label, items in out.items() if not items]
    print(f"metros_with_news={len(out) - len(empty)}/{len(out)}")
    if empty:
        print("empty: " + ", ".join(empty))


if __name__ == "__main__":
    sys.exit(main())
