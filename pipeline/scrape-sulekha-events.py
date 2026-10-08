#!/usr/bin/env python3 -u
"""Scrape Sulekha desi events (USA-wide) into the events table.

events.sulekha.com is a major desi event ticketing portal. Each metro page
embeds FULL JSON-LD Event data inline (name, dates, venue + geo coords,
images, organizer, prices) — no per-event page fetches needed.

We enumerate the FULL metro index from a metro page, walk every US metro
(entire USA, not just major metros), and upsert events with
source='scrape-sulekha', source_id=<sulekha numeric event id>.

(nripage.com was evaluated as an alternative but is fully Cloudflare-gated:
only its sitemap is reachable, and sitemap entries carry no event dates —
unusable for the events pipeline. Sulekha won on data richness + access.)

Polite: 2.5s+ between requests, 7-day cache. robots.txt allows these paths.

Run: python3 -u pipeline/scrape-sulekha-events.py [--dry-run] [--new-only]
     [--metros new-york-metro-area,chicago-metro-area] [--limit-metros 2]
"""
import argparse
import hashlib
import html as htmlmod
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, date, timezone

sys.stdout.reconfigure(line_buffering=True)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(REPO, "pipeline", ".state", "scrape-cache")
os.makedirs(CACHE_DIR, exist_ok=True)

UA = "TheVideshi/1.0 (+https://www.thevideshi.com; desi event aggregation)"
DELAY_S = 2.5

BASE = "https://events.sulekha.com"
SEED_METRO_URL = f"{BASE}/new-york-metro-area"

# non-US metros to skip
NON_US = {"calgary-metro-area", "montreal-metro-area", "toronto-metro-area",
          "vancouver-metro-area", "winnipeg-metro-area"}

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY", file=sys.stderr)
    sys.exit(1)
SB_HOST = SUPABASE_URL.replace("https://", "").replace("http://", "")


def curl_get(url: str, retries: int = 3) -> str:
    last_err = ""
    for attempt in range(retries):
        out = subprocess.run(
            ["curl", "-sSL", "-A", UA, "--max-time", "60", url],
            capture_output=True,
        )
        if out.returncode == 0 and out.stdout:
            return out.stdout.decode("utf-8", errors="replace")
        last_err = out.stderr.decode("utf-8", errors="replace")[:200]
        time.sleep(DELAY_S * (attempt + 1))
    raise RuntimeError(f"curl failed for {url}: {last_err}")


def cached_fetch(key: str, url: str, max_age_h: float = 168) -> str:
    path = os.path.join(CACHE_DIR, key)
    if os.path.exists(path):
        age_h = (time.time() - os.path.getmtime(path)) / 3600
        if age_h < max_age_h:
            return open(path, encoding="utf-8").read()
    time.sleep(DELAY_S)
    body = curl_get(url)
    open(path, "w", encoding="utf-8").write(body)
    return body


def get_metros() -> list:
    """Enumerate the full metro index from the seed metro page."""
    html = cached_fetch("sul-metros.html", SEED_METRO_URL)
    slugs = re.findall(r'href="(/[a-z0-9-]+-metro-area)"', html)
    seen, metros = set(), []
    for s in slugs:
        slug = s.strip("/").lower()
        if slug not in seen and slug not in NON_US and "tickets" not in slug:
            seen.add(slug)
            metros.append(slug)
    return sorted(metros)


def extract_event_jsons(html: str) -> list:
    """Parse embedded JSON-LD Event objects via brace matching."""
    out = []
    needle = '{"@context"'
    pos = 0
    while True:
        i = html.find(needle, pos)
        if i == -1:
            break
        # must be an Event block
        probe = html[i:i + 120]
        if '"Event"' not in probe:
            pos = i + 1
            continue
        # brace-match from i
        depth, j, in_str, esc = 0, i, False, False
        while j < len(html):
            c = html[j]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            else:
                if c == '"':
                    in_str = True
                elif c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        break
            j += 1
        if depth == 0:
            try:
                obj = json.loads(html[i:j + 1])
                if isinstance(obj, dict) and obj.get("@type") == "Event":
                    out.append(obj)
            except Exception:
                pass
            pos = j + 1
        else:
            pos = i + 1
    return out


CATEGORY_KEYWORDS = [
    (("comedy", "standup", "stand-up", "hasya"), "Comedy"),
    (("garba", "dandiya", "navratri", "diwali", "holi", "eid", "christmas",
      "festival", "mela", "utsav", "celebration"), "Festival"),
    (("concert", "live music", "musical", "sufi", "ghazal", "qawwali",
      "symphony", "orchestra"), "Music"),
    (("dance", "bharatanatyam", "kathak"), "Dance"),
    (("bhajan", "kirtan", "satsang", "devotional", "aarti", "puja",
      "pravachan", "katha"), "Religious"),
    (("food", "dinner", "brunch", "buffet", "tasting"), "Food"),
    (("workshop", "class", "seminar", "summit", "conference"), "Education"),
]


def guess_category(title: str) -> str:
    t = title.lower()
    for keywords, cat in CATEGORY_KEYWORDS:
        if any(k in t for k in keywords):
            return cat
    return "Entertainment"


def parse_event(obj: dict) -> dict | None:
    url = obj.get("url", "")
    m = re.search(r"_(\d+)$", url)
    if not m:
        return None
    sid = m.group(1)
    name = htmlmod.unescape(obj.get("name", "")).strip()
    if not name:
        return None

    start = obj.get("startDate", "")
    dm = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})", start)
    if not dm:
        return None
    date_str = f"{dm.group(1)}-{dm.group(2)}-{dm.group(3)}"
    time_str = f"{dm.group(4)}:{dm.group(5)}"
    # skip past events
    if date_str < date.today().isoformat():
        return None

    end = obj.get("endDate", "")
    em = re.match(r"(\d{4})-(\d{2})-(\d{2})", end)
    end_date_str = f"{em.group(1)}-{em.group(2)}-{em.group(3)}" if em else None

    loc = obj.get("location", {}) or {}
    addr = loc.get("address", {}) or {}
    geo = loc.get("geo", {}) or {}
    images = obj.get("image", []) or []
    org = obj.get("organizer", {}) or {}
    offers = obj.get("offers", {}) or {}
    if isinstance(offers, list):
        offers = offers[0] if offers else {}

    price = None
    lo, hi = offers.get("lowPrice"), offers.get("highPrice") or offers.get("price")
    if lo and hi and lo != hi:
        price = f"${lo} - ${hi}"
    elif lo or hi:
        price = f"${lo or hi}"

    title = re.sub(r"\s+", " ", name)[:200]
    city = (addr.get("addressLocality") or "").strip()
    state = (addr.get("addressRegion") or "").strip()

    event = {
        "title": title,
        "date": date_str,
        "time": time_str,
        "venue_name": (loc.get("name") or "").strip()[:200] or None,
        "street_address": (addr.get("streetAddress") or "").strip()[:300] or None,
        "city": city[:120],
        "state": state[:10] or None,
        "zip_code": (addr.get("postalCode") or "").strip()[:12] or None,
        "latitude": geo.get("latitude"),
        "longitude": geo.get("longitude"),
        "category": guess_category(title),
        "description": htmlmod.unescape(
            re.sub(r"\s+", " ", obj.get("description", ""))).strip()[:500] or None,
        "image_url": (images[0] if images else None),
        "ticket_url": url,
        "organizer": (org.get("name") or "").strip()[:200] or None,
        "price_range": price,
        "source": "scrape-sulekha",
        "source_id": f"sulekha_{sid}",
        "slug": re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
                + f"-{date_str}",
    }
    return {k: v for k, v in event.items() if v is not None}


def sb_get_existing_source_ids() -> set:
    """All source_ids already in events for source='scrape-sulekha'."""
    out, offset, step = set(), 0, 1000
    while True:
        url = (f"https://{SB_HOST}/rest/v1/events"
               f"?select=source_id&source=eq.scrape-sulekha"
               f"&limit={step}&offset={offset}")
        r = subprocess.run(
            ["curl", "-sS", url,
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
            capture_output=True, text=True)
        try:
            batch = json.loads(r.stdout or "[]")
        except Exception:
            break
        for row in batch:
            if row.get("source_id"):
                out.add(row["source_id"])
        if len(batch) < step:
            break
        offset += step
    return out


def upsert_event(record: dict) -> bool:
    url = f"https://{SB_HOST}/rest/v1/events?on_conflict=source,source_id"
    r = subprocess.run(
        ["curl", "-sS", "-X", "POST", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: resolution=merge-duplicates,return=minimal",
         "-d", json.dumps(record)],
        capture_output=True, text=True, timeout=30)
    out = r.stdout.strip()
    if r.returncode != 0 or ('"code"' in out and '"message"' in out):
        if "duplicate" not in out.lower():
            print(f"    upsert failed '{record.get('title', '?')[:40]}': {out[:150]}")
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--new-only", action="store_true",
                    help="skip events already in DB (light monthly refresh)")
    ap.add_argument("--metros", default="")
    ap.add_argument("--limit-metros", type=int, default=0)
    args = ap.parse_args()

    metros = get_metros()
    print(f"US metros found: {len(metros)}", flush=True)
    if args.metros:
        want = {m.strip().lower() for m in args.metros.split(",")}
        metros = [m for m in metros if m in want]
    if args.limit_metros:
        metros = metros[:args.limit_metros]

    existing_ids = sb_get_existing_source_ids() if args.new_only else set()
    if args.new_only:
        print(f"existing sulekha events in DB: {len(existing_ids)}", flush=True)

    all_events, metro_counts, seen = [], {}, set()
    for mi, metro in enumerate(metros):
        html = cached_fetch(f"sul-{metro}.html", f"{BASE}/{metro}")
        objs = extract_event_jsons(html)
        m_new = 0
        for obj in objs:
            ev = parse_event(obj)
            if not ev or ev["source_id"] in seen:
                continue
            if args.new_only and ev["source_id"] in existing_ids:
                continue
            seen.add(ev["source_id"])
            ev["_metro"] = metro
            all_events.append(ev)
            m_new += 1
        metro_counts[metro] = m_new
        print(f"  [{mi+1}/{len(metros)}] {metro}: +{m_new} (total: {len(all_events)})",
              flush=True)

    print(f"TOTAL new candidates: {len(all_events)}", flush=True)
    nz = {m: c for m, c in metro_counts.items() if c}
    print(f"metros with events: {len(nz)}/{len(metros)}", flush=True)

    # per-state coverage
    from collections import Counter
    states = Counter(e["state"] for e in all_events if e.get("state"))
    print("events per state:", dict(sorted(states.items())), flush=True)

    if args.dry_run:
        for e in all_events[:20]:
            print(f"  + {e['date']} | [{e['category']}] {e['title'][:55]} | "
                  f"{e.get('venue_name', '')[:30]} | {e['city']}")
        print("(dry run — no insert)")
        return

    inserted, failed = 0, 0
    for i, e in enumerate(all_events):
        e.pop("_metro", None)
        if upsert_event(e):
            inserted += 1
        else:
            failed += 1
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(all_events)} ok={inserted} failed={failed}", flush=True)
    print(f"DONE inserted/upserted={inserted} failed={failed}", flush=True)


if __name__ == "__main__":
    main()
