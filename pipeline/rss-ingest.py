#!/usr/bin/env python3
"""
RSS Ingest Pipeline for The Videshi — v2 (optimized).
"""

import os, json, hashlib, re, sys, time
from pathlib import Path
from datetime import datetime, timezone
import email.utils

# Force unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

import requests
import feedparser

# Load env
env_file = Path.home() / ".env.supabase"
if env_file.exists():
    for line in env_file.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_ANON_KEY", ""))
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
}
NOW_ISO = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')

def url_hash(url):
    return hashlib.md5(url.encode()).hexdigest()

def parse_pub_date(date_str):
    if not date_str:
        return NOW_ISO
    try:
        t = email.utils.parsedate_to_datetime(date_str)
        return t.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    except:
        pass
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    except:
        pass
    return NOW_ISO

print("═══ Videshi RSS Ingest ═══")
print(f"  Time: {NOW_ISO} UTC")

# Step 1: Get active feeds
r = requests.get(f"{SB_URL}/rest/v1/p2_feed_sources",
    headers=HEADERS,
    params={"is_active": "eq.true", "select": "id,name,url,type,verticals,tier"})
r.raise_for_status()
feeds = r.json()
print(f"\n  📡 Active feed sources: {len(feeds)}")

# Step 2: Load existing hashes (26k+, paginate efficiently)
print("  🔍 Loading existing signal hashes...")
existing = set()
offset = 0
PAGE = 1000
while True:
    r = requests.get(f"{SB_URL}/rest/v1/p2_signals",
        headers={**HEADERS, "Range": f"{offset}-{offset+PAGE-1}", "Prefer": "count=none"},
        params={"select": "url_hash"}, timeout=30)
    data = r.json()
    if not data or isinstance(data, dict):
        break
    for row in data:
        existing.add(row["url_hash"])
    if len(data) < PAGE:
        break
    offset += PAGE
    print(f"    ... loaded {len(existing)} hashes")
print(f"  📊 Existing signals: {len(existing)}")

# Step 3: Fetch feeds sequentially with timeouts
print("\n  📥 Fetching feeds...")
all_new = []
total_items = 0

for feed in feeds:
    name = feed["name"]
    url = feed["url"]
    items = []
    try:
        if "rss2json.com" in url:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("items", []):
                t = (item.get("title") or "").strip()
                u = (item.get("link") or "").strip()
                if t and u:
                    items.append({"title": t, "url": u, "pub": item.get("pubDate", "")})
        else:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (TheVideshi Bot)"})
            d = feedparser.parse(resp.content)
            for entry in d.entries:
                t = (entry.get("title") or "").strip()
                u = (entry.get("link") or "").strip()
                pub = getattr(entry, "published", getattr(entry, "updated", ""))
                if t and u:
                    items.append({"title": t, "url": u, "pub": pub})
    except Exception as e:
        print(f"  ⚠ {name}: {e}")
        continue

    # Dedup against existing
    new_for_feed = 0
    for item in items:
        h = url_hash(item["url"])
        if h not in existing:
            all_new.append({
                "feed_source_id": feed["id"],
                "title": item["title"][:500],
                "original_url": item["url"][:2000],
                "url_hash": h,
                "published_at": parse_pub_date(item["pub"]),
                "fetched_at": NOW_ISO,
                "is_processed": False,
            })
            existing.add(h)
            new_for_feed += 1
    total_items += len(items)
    status = f"+{new_for_feed}" if new_for_feed else "0 new"
    print(f"    {name}: {len(items)} items ({status})")

print(f"\n  📰 Total items scanned: {total_items}")
print(f"  🆕 New signals: {len(all_new)}")

# Step 4: Insert new signals
if all_new:
    inserted = 0
    for i in range(0, len(all_new), 50):
        batch = all_new[i:i+50]
        r = requests.post(f"{SB_URL}/rest/v1/p2_signals",
            headers={**HEADERS, "Prefer": "return=minimal, resolution=ignore-duplicates"},
            json=batch)
        if r.status_code in (200, 201):
            inserted += len(batch)
        elif r.status_code == 409:
            # Batch had duplicates; fall back to individual inserts
            for item in batch:
                ri = requests.post(f"{SB_URL}/rest/v1/p2_signals",
                    headers={**HEADERS, "Prefer": "return=minimal, resolution=ignore-duplicates"},
                    json=item)
                if ri.status_code in (200, 201):
                    inserted += 1
                elif ri.status_code != 409:
                    print(f"  ⚠ Insert error: {ri.status_code} {ri.text[:200]}")
        else:
            print(f"  ⚠ Insert error: {r.status_code} {r.text[:200]}")
    print(f"  ✅ Inserted {inserted} new signals")
else:
    print("  ℹ️  All signals already ingested")

# Step 5: Cluster unprocessed signals into topics
print("\n  🧩 Clustering unprocessed signals...")
r = requests.get(f"{SB_URL}/rest/v1/p2_signals",
    headers={**HEADERS, "Range": "0-499"},
    params={"is_processed": "eq.false", "select": "id,title,feed_source_id,original_url,published_at", "order": "fetched_at.desc"})
signals = r.json() if r.status_code == 200 else []
if isinstance(signals, dict):
    signals = []

if not signals:
    print("  No unprocessed signals to cluster.")
else:
    print(f"  Found {len(signals)} unprocessed signals.")

    def normalize(t):
        t = t.lower().strip()
        t = re.sub(r'[^a-z0-9\s]', '', t)
        t = re.sub(r'\s+', ' ', t)
        return t

    clusters = {}
    for sig in signals:
        key = normalize(sig["title"])[:40]
        clusters.setdefault(key, []).append(sig)

    topics_created = 0
    ids_to_mark = []

    for key, sigs in clusters.items():
        best = max(sigs, key=lambda s: len(s["title"]))
        title = best["title"]
        n = len(sigs)
        title_lower = title.lower()

        # Category detection
        cat = "news"
        if any(w in title_lower for w in ["cricket", "ipl", "sports", "tennis", "match", "wicket", "runs scored", "goal "]):
            cat = "sports"
        elif any(w in title_lower for w in ["bollywood", "film", "movie", "actor", "actress", "box office", "ott", "netflix"]):
            cat = "entertainment"
        elif any(w in title_lower for w in ["tech", "ai ", "startup", "software", "google", "apple", "meta ", "chip"]):
            cat = "technology"
        elif any(w in title_lower for w in ["nri", "visa", "immigration", "green card", "h1b", "diaspora"]):
            cat = "nri-world"
        elif any(w in title_lower for w in ["market", "sensex", "nifty", "stock", "gdp", "rupee", "rbi"]):
            cat = "markets-finance"
        elif any(w in title_lower for w in ["health", "food", "yoga", "wellness", "recipe", "travel"]):
            cat = "lifestyle-health"

        vert_map = {"news":"politics","markets-finance":"economy","technology":"tech",
                     "nri-world":"diaspora","sports":"sports","entertainment":"entertainment",
                     "lifestyle-health":"culture"}
        vertical = vert_map.get(cat, "politics")

        sc_sig = min(50 + n * 10, 90)
        sc_src = min(n * 20, 90)
        sc_total = round(70*0.25 + sc_sig*0.3 + 50*0.25 + sc_src*0.2)

        keywords = list(set(re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*', title)))[:5]
        if not keywords:
            keywords = [title.split()[0]] if title.split() else ["news"]

        topic = {
            "canonical_title": title[:200],
            "vertical": vertical,
            "urgency": "daily",
            "score_diaspora": 50,
            "score_significance": sc_sig,
            "score_recency": 70,
            "score_source_avail": sc_src,
            "score_total": sc_total,
            "signal_count": n,
            "status": "pending",
            "keywords": keywords,
            "category": cat,
            "created_at": NOW_ISO,
            "updated_at": NOW_ISO,
        }

        r = requests.post(f"{SB_URL}/rest/v1/p2_topics",
            headers={**HEADERS, "Prefer": "return=representation"}, json=topic)
        if r.status_code in (200, 201):
            topics_created += 1
            td = r.json()
            tid = td[0]["id"] if isinstance(td, list) else td["id"]
            for sig in sigs:
                ids_to_mark.append(sig["id"])
        else:
            # Still mark as processed to avoid re-clustering
            for sig in sigs:
                ids_to_mark.append(sig["id"])

    # Mark processed
    for i in range(0, len(ids_to_mark), 50):
        batch_ids = ",".join(ids_to_mark[i:i+50])
        requests.patch(f"{SB_URL}/rest/v1/p2_signals?id=in.({batch_ids})",
            headers={**HEADERS, "Prefer": "return=minimal"},
            json={"is_processed": True})

    print(f"  ✅ Created {topics_created} topics from {len(signals)} signals")

print(f"\n═══ Ingest Complete ═══")
