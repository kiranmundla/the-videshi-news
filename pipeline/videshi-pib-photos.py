#!/usr/bin/env python3
"""
videshi-pib-photos.py — PIB Photo RSS ingestion and matching for The Videshi.

Fetches the Press Information Bureau (Government of India) Photo Gallery RSS
feed, builds a local caption index, and matches article headlines against
photo captions for relevant government/political imagery.

Usage:
    python3 videshi-pib-photos.py ingest                  # Fetch RSS, update index
    python3 videshi-pib-photos.py match "headline text"   # Find best caption match
    python3 videshi-pib-photos.py status                  # Show index stats
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import requests
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PIB_RSS_URL = "https://www.pib.gov.in/RssMain.aspx?ModId=8&Lang=1&Regid=1&reg=1"
PIB_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pib-photo-index.json")
MAX_INDEX_SIZE = 200  # Rolling window: keep last N entries
MIN_MATCH_SIMILARITY = 0.3  # Minimum Jaccard similarity to consider a match

# Stop words to exclude from keyword extraction
STOP_WORDS = {
    "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or",
    "is", "was", "are", "were", "be", "been", "being", "has", "had", "have",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "shall", "can", "with", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "under", "over", "about",
    "up", "out", "off", "its", "his", "her", "their", "our", "my", "your",
    "this", "that", "these", "those", "it", "he", "she", "they", "we", "you",
    "not", "no", "but", "so", "if", "than", "too", "very", "just", "also",
    "new", "said", "says", "shri", "smt", "mr", "mrs",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_keywords(text):
    """Extract significant words from text for matching."""
    if not text:
        return set()
    # Normalize
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    words = text.split()
    # Keep words >= 3 chars, not in stop words
    return {w for w in words if len(w) >= 3 and w not in STOP_WORDS}


def compute_similarity(headline_keywords, caption_keywords):
    """
    Compute similarity between headline and caption keyword sets.
    Uses a weighted approach: how many headline keywords appear in the caption.
    This handles the asymmetry where PIB captions are much longer than headlines.
    """
    if not headline_keywords or not caption_keywords:
        return 0.0

    # What fraction of headline keywords appear in the caption?
    headline_in_caption = len(headline_keywords & caption_keywords)
    headline_coverage = headline_in_caption / len(headline_keywords)

    # Jaccard for overall similarity
    jaccard = len(headline_keywords & caption_keywords) / len(headline_keywords | caption_keywords)

    # Weighted: 70% headline coverage, 30% Jaccard
    return headline_coverage * 0.7 + jaccard * 0.3


def extract_category_id(url):
    """Extract CategoryId from PIB gallery URL."""
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        cat_ids = params.get("CategoryId", [])
        return cat_ids[0] if cat_ids else None
    except Exception:
        return None


def extract_date_from_caption(caption):
    """Try to extract a date from the caption text."""
    # Look for patterns like "May 15, 2026" or "on May 15, 2026"
    date_pattern = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}"
    match = re.search(date_pattern, caption, re.IGNORECASE)
    if match:
        try:
            date_str = match.group().replace(",", "")
            dt = datetime.strptime(date_str, "%B %d %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------

def load_index():
    """Load the photo index from disk."""
    if not os.path.exists(INDEX_PATH):
        return {"last_updated": None, "photos": []}
    try:
        with open(INDEX_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"last_updated": None, "photos": []}


def save_index(index):
    """Save the photo index to disk."""
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# RSS Ingestion
# ---------------------------------------------------------------------------

def fetch_pib_rss():
    """Fetch PIB Photo Gallery RSS feed."""
    headers = {
        "User-Agent": PIB_USER_AGENT,
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }
    try:
        resp = requests.get(PIB_RSS_URL, headers=headers, timeout=15)
        resp.raise_for_status()
        # PIB serves UTF-8 with BOM — decode with utf-8-sig to strip it
        return resp.content.decode("utf-8-sig")
    except requests.RequestException as e:
        print(f"  ⚠ Failed to fetch PIB RSS: {e}")
        return None


def parse_pib_rss(xml_text):
    """Parse PIB RSS XML into photo entries."""
    photos = []
    try:
        root = ET.fromstring(xml_text)
        seen_ids = set()

        for item in root.findall(".//item"):
            title_el = item.find("title")
            link_el = item.find("link")

            if title_el is None or link_el is None:
                continue

            caption = (title_el.text or "").strip()
            gallery_url = (link_el.text or "").strip()

            if not caption or not gallery_url:
                continue

            category_id = extract_category_id(gallery_url)
            if not category_id or category_id in seen_ids:
                continue
            seen_ids.add(category_id)

            photo_date = extract_date_from_caption(caption)

            photos.append({
                "caption": caption,
                "gallery_url": gallery_url,
                "category_id": category_id,
                "date": photo_date,
            })

    except ET.ParseError as e:
        print(f"  ⚠ Failed to parse PIB RSS XML: {e}")

    return photos


def cmd_ingest():
    """Fetch PIB RSS and update the local photo index."""
    print("📷 PIB Photo RSS Ingestion")

    xml_text = fetch_pib_rss()
    if not xml_text:
        print("  ❌ No data from PIB RSS")
        return

    new_photos = parse_pib_rss(xml_text)
    if not new_photos:
        print("  ⚠ No photos parsed from RSS")
        return

    # Load existing index
    index = load_index()
    existing_ids = {p["category_id"] for p in index["photos"]}

    # Merge new photos (prepend, dedup by category_id)
    added = 0
    for photo in new_photos:
        if photo["category_id"] not in existing_ids:
            index["photos"].insert(0, photo)
            existing_ids.add(photo["category_id"])
            added += 1

    # Trim to MAX_INDEX_SIZE (keep most recent)
    if len(index["photos"]) > MAX_INDEX_SIZE:
        index["photos"] = index["photos"][:MAX_INDEX_SIZE]

    index["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_index(index)

    print(f"  ✅ Ingested {added} new photos (total: {len(index['photos'])} in index)")


# ---------------------------------------------------------------------------
# Caption Matching
# ---------------------------------------------------------------------------

def cmd_match(headline):
    """Find the best matching PIB photo for an article headline."""
    index = load_index()

    if not index["photos"]:
        print(json.dumps({"match": False, "reason": "Empty index"}))
        return

    headline_keywords = extract_keywords(headline)
    if not headline_keywords:
        print(json.dumps({"match": False, "reason": "No keywords in headline"}))
        return

    best_match = None
    best_similarity = 0.0

    for photo in index["photos"]:
        caption_keywords = extract_keywords(photo["caption"])
        similarity = compute_similarity(headline_keywords, caption_keywords)

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = photo

    if best_match and best_similarity >= MIN_MATCH_SIMILARITY:
        result = {
            "match": True,
            "caption": best_match["caption"],
            "gallery_url": best_match["gallery_url"],
            "category_id": best_match["category_id"],
            "date": best_match["date"],
            "similarity": round(best_similarity, 3),
        }
    else:
        result = {
            "match": False,
            "reason": "No caption match above threshold",
            "best_similarity": round(best_similarity, 3) if best_similarity > 0 else 0,
        }

    print(json.dumps(result))


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def cmd_status():
    """Show index statistics."""
    index = load_index()
    total = len(index["photos"])
    last_updated = index.get("last_updated", "never")

    print(f"📷 PIB Photo Index Status")
    print(f"  Total photos: {total}")
    print(f"  Last updated: {last_updated}")

    if total > 0:
        dates = [p.get("date", "unknown") for p in index["photos"]]
        unique_dates = sorted(set(dates), reverse=True)
        print(f"  Date range: {unique_dates[-1]} to {unique_dates[0]}")
        print(f"  Recent captions:")
        for p in index["photos"][:3]:
            print(f"    • {p['caption'][:80]}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "ingest":
        cmd_ingest()
    elif cmd == "match":
        if len(sys.argv) < 3:
            print("Usage: videshi-pib-photos.py match \"headline text\"")
            sys.exit(1)
        cmd_match(sys.argv[2])
    elif cmd == "status":
        cmd_status()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
