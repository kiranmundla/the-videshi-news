#!/usr/bin/env python3
"""
backfill-event-enrichment.py — Enrich existing events with full descriptions,
street addresses, and zip codes by visiting each event's source page.

Supports: allevents, eventbrite, meetup

Usage:
  python3 -u backfill-event-enrichment.py --source allevents           # AllEvents
  python3 -u backfill-event-enrichment.py --source eventbrite          # Eventbrite
  python3 -u backfill-event-enrichment.py --source meetup              # Meetup
  python3 -u backfill-event-enrichment.py --source all                 # All sources
  python3 -u backfill-event-enrichment.py --source allevents --dry-run # Preview
  python3 -u backfill-event-enrichment.py --source allevents --limit 5 # Limit
"""

import os, sys, json, re, time, subprocess, argparse
from html.parser import HTMLParser

sys.stdout.reconfigure(line_buffering=True)

# ── Env ──────────────────────────────────────────────────────────────────────

ENV_FILE = os.path.expanduser("~/.env.supabase")
if os.path.exists(ENV_FILE):
    for line in open(ENV_FILE):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SB_HOST = SUPABASE_URL.replace("https://", "")

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


# ── HTML helpers ─────────────────────────────────────────────────────────────

def strip_html(html_text):
    """Convert HTML to plain text, preserving paragraph breaks."""
    if not html_text:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', html_text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&#39;', "'").replace('&quot;', '"').replace('&nbsp;', ' ')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


# ── DB helpers ───────────────────────────────────────────────────────────────

def fetch_events_needing_enrichment(source, limit):
    """Fetch upcoming events missing long_description OR street_address."""
    # Build filter: upcoming events from this source that need enrichment
    url = (
        f"{SUPABASE_URL}/rest/v1/events"
        f"?source=eq.{source}"
        f"&date=gte.{time.strftime('%Y-%m-%d')}"
        f"&ticket_url=neq."
        f"&select=id,title,ticket_url,source_id,description,long_description,street_address,zip_code,venue_name"
        f"&order=date.asc"
        f"&limit={limit}"
    )
    r = subprocess.run(
        ["curl", "-sS", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True, timeout=30
    )
    try:
        events = json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"  Failed to parse: {r.stdout[:200]}")
        return []

    # Filter to events that actually need enrichment
    needing = []
    for e in events:
        ld = e.get("long_description") or ""
        desc = e.get("description") or ""
        needs_desc = not ld or ld == desc or len(ld) < 200
        needs_addr = not e.get("street_address")
        if needs_desc or needs_addr:
            needing.append(e)
    return needing


def update_event(event_id, updates):
    """Patch an event record."""
    updates = {k: v for k, v in updates.items() if v is not None}
    if not updates:
        return False
    payload = json.dumps(updates)
    url = f"{SUPABASE_URL}/rest/v1/events?id=eq.{event_id}"
    r = subprocess.run(
        ["curl", "-sS", "-X", "PATCH", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal",
         "-d", payload],
        capture_output=True, text=True, timeout=15
    )
    return r.returncode == 0 and "error" not in r.stdout.lower()


# ── AllEvents enrichment ─────────────────────────────────────────────────────

def enrich_allevents(event):
    """Fetch AllEvents detail page, extract full description + address from JSON-LD + HTML."""
    url = event.get("ticket_url", "")
    # If ticket_url isn't an allevents URL, reconstruct it from source_id
    if not url or "allevents.in" not in url:
        sid = event.get("source_id", "")
        ae_id = sid.replace("allevents_", "") if sid.startswith("allevents_") else ""
        if not ae_id:
            return None
        # Can't reconstruct full URL without city slug, skip
        return None

    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "20", "--max-redirs", "5",
             "-H", f"User-Agent: {UA}",
             "-H", "Accept: text/html,application/xhtml+xml",
             "-H", "Accept-Language: en-US,en;q=0.9",
             url],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0 or not r.stdout or len(r.stdout) < 2000:
            return None
        html = r.stdout
    except Exception as e:
        print(f"    Fetch error: {e}")
        return None

    result = {}

    # 1. JSON-LD for address
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    for block in blocks:
        try:
            data = json.loads(block)
            if isinstance(data, dict) and data.get("@type") == "Event":
                loc = data.get("location", {})
                if isinstance(loc, dict):
                    addr = loc.get("address", {})
                    if isinstance(addr, dict):
                        street = addr.get("streetAddress", "")
                        postal = addr.get("postalCode", "")
                        if street:
                            result["street_address"] = street
                        if postal:
                            result["zip_code"] = postal
                break
        except json.JSONDecodeError:
            continue

    # 2. Full description from HTML
    desc_match = re.search(
        r'<div\s+class="event-description-html">\s*(.*?)\s*</div>',
        html, re.DOTALL
    )
    if desc_match:
        full_desc = strip_html(desc_match.group(1))
        if len(full_desc) > 100:
            result["long_description"] = full_desc[:2000]

    return result if result else None


# ── Eventbrite enrichment ────────────────────────────────────────────────────

def enrich_eventbrite(event):
    """Re-fetch Eventbrite search page to get address info, or visit detail page."""
    url = event.get("ticket_url", "")
    if not url:
        return None

    # Try fetching event page directly for JSON-LD
    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "20",
             "-H", f"User-Agent: {UA}",
             "-H", "Accept: text/html,application/xhtml+xml",
             "-H", "Accept-Language: en-US,en;q=0.9",
             url],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0 or not r.stdout:
            return None
        html = r.stdout
    except Exception as e:
        print(f"    Fetch error: {e}")
        return None

    result = {}

    # Try JSON-LD
    ld_blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    for block in ld_blocks:
        try:
            data = json.loads(block)
            if isinstance(data, list):
                data = data[0] if data else {}
            if data.get("@type") == "Event":
                # Description
                desc = data.get("description", "")
                if desc and len(desc) > 100:
                    result["long_description"] = strip_html(desc)[:5000]
                # Address
                loc = data.get("location", {})
                if isinstance(loc, dict):
                    addr = loc.get("address", {})
                    if isinstance(addr, dict):
                        street = addr.get("streetAddress", "")
                        postal = addr.get("postalCode", "")
                        if street:
                            result["street_address"] = street
                        if postal:
                            result["zip_code"] = postal
                break
        except json.JSONDecodeError:
            continue

    # Try __SERVER_DATA__ for richer description
    start = html.find("window.__SERVER_DATA__")
    if start >= 0:
        eq_pos = html.find("=", start)
        brace_start = html.find("{", eq_pos)
        if brace_start >= 0:
            depth = 0
            end = brace_start
            for i in range(brace_start, min(len(html), brace_start + 500000)):
                if html[i] == "{": depth += 1
                elif html[i] == "}": depth -= 1
                if depth == 0:
                    end = i
                    break
            try:
                server_data = json.loads(html[brace_start:end + 1])
                components = server_data.get("components", {})
                for path_key in ["eventDescription", "listing_event"]:
                    if path_key in components:
                        comp = components[path_key]
                        desc = comp.get("description", {})
                        if isinstance(desc, dict):
                            html_desc = desc.get("html", "") or desc.get("text", "")
                        else:
                            html_desc = str(desc) if desc else ""
                        if html_desc and len(html_desc) > 100:
                            cleaned = strip_html(html_desc)
                            if len(cleaned) > len(result.get("long_description", "")):
                                result["long_description"] = cleaned[:5000]
                        break

                # Venue address from server data
                venue = (components.get("eventPage", {}) or {}).get("venue", {})
                if not venue:
                    # Try the event listing itself
                    listing = components.get("listing", {})
                    venue = listing.get("venue", {}) if listing else {}
                if isinstance(venue, dict):
                    addr = venue.get("address", {}) or {}
                    if isinstance(addr, dict):
                        street = addr.get("address_1", "")
                        postal = addr.get("postal_code", "")
                        if street and not result.get("street_address"):
                            result["street_address"] = street
                        if postal and not result.get("zip_code"):
                            result["zip_code"] = postal
            except (json.JSONDecodeError, KeyError):
                pass

    # Fallback: og:description
    if not result.get("long_description"):
        og_desc = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if og_desc and len(og_desc.group(1).strip()) > 100:
            result["long_description"] = og_desc.group(1).strip()[:5000]

    return result if result else None


# ── Meetup enrichment ────────────────────────────────────────────────────────

def enrich_meetup(event):
    """Fetch Meetup event page to extract venue address."""
    url = event.get("ticket_url", "")
    if not url:
        return None

    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "15", "--max-redirs", "5",
             "-H", f"User-Agent: {UA}", url],
            capture_output=True, text=True, timeout=25
        )
        if r.returncode != 0 or not r.stdout or len(r.stdout) < 1000:
            return None
        html = r.stdout
    except Exception as e:
        print(f"    Fetch error: {e}")
        return None

    result = {}

    # Try JSON-LD
    ld_blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    for block in ld_blocks:
        try:
            data = json.loads(block)
            if isinstance(data, list):
                data = data[0] if data else {}
            if data.get("@type") == "Event":
                loc = data.get("location", {})
                if isinstance(loc, dict):
                    addr = loc.get("address", {})
                    if isinstance(addr, dict):
                        street = addr.get("streetAddress", "")
                        postal = addr.get("postalCode", "")
                        if street:
                            result["street_address"] = street
                        if postal:
                            result["zip_code"] = postal
                # Also get full description if ours is short
                desc = data.get("description", "")
                if desc and len(desc) > 200:
                    result["long_description"] = strip_html(desc)[:2000]
                break
        except json.JSONDecodeError:
            continue

    # Try __NEXT_DATA__
    if not result.get("street_address"):
        nd_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if nd_match:
            try:
                nd_data = json.loads(nd_match.group(1))
                apollo = nd_data.get("props", {}).get("pageProps", {}).get("__APOLLO_STATE__", {})
                for k, v in apollo.items():
                    if k.startswith("Venue:"):
                        street = v.get("address", "")
                        if street:
                            result["street_address"] = street
                            result["zip_code"] = v.get("postalCode", "") or ""
                        break
            except (json.JSONDecodeError, KeyError):
                pass

    return result if result else None


# ── Main ─────────────────────────────────────────────────────────────────────

ENRICHERS = {
    "allevents": enrich_allevents,
    "eventbrite": enrich_eventbrite,
    "meetup": enrich_meetup,
}


def main():
    parser = argparse.ArgumentParser(description="Backfill events with full descriptions and addresses")
    parser.add_argument("--source", required=True, help="Event source: allevents, eventbrite, meetup, or 'all'")
    parser.add_argument("--limit", type=int, default=500, help="Max events per source (default 500)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without updating DB")
    parser.add_argument("--sleep", type=float, default=1.0, help="Seconds between fetches (default 1.0)")
    args = parser.parse_args()

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        sys.exit(1)

    sources = list(ENRICHERS.keys()) if args.source == "all" else [args.source]

    for source in sources:
        enricher = ENRICHERS.get(source)
        if not enricher:
            print(f"⚠ Unknown source '{source}'. Supported: {', '.join(ENRICHERS.keys())}")
            continue

        print(f"\n{'='*60}")
        print(f"Enriching {source} events")
        print(f"{'='*60}")

        events = fetch_events_needing_enrichment(source, args.limit)
        print(f"Found {len(events)} events needing enrichment")

        if not events:
            continue

        updated = 0
        skipped = 0
        failed = 0
        desc_added = 0
        addr_added = 0
        zip_added = 0

        for i, ev in enumerate(events):
            title = ev.get("title", "")[:60]
            print(f"\n[{i+1}/{len(events)}] {title}")

            details = enricher(ev)
            if not details:
                print("  ⚠ No data extracted")
                failed += 1
                time.sleep(args.sleep)
                continue

            # Build patch — only update fields that are currently missing
            patch = {}
            ld = ev.get("long_description") or ""
            desc = ev.get("description") or ""

            if details.get("long_description"):
                new_ld = details["long_description"]
                if len(new_ld) > len(ld) and len(new_ld) > len(desc):
                    patch["long_description"] = new_ld
                    print(f"  📝 Description: {len(new_ld)} chars")

            if details.get("street_address") and not ev.get("street_address"):
                patch["street_address"] = details["street_address"]
                print(f"  📍 Address: {details['street_address']}")

            if details.get("zip_code") and not ev.get("zip_code"):
                patch["zip_code"] = details["zip_code"]
                print(f"  📮 Zip: {details['zip_code']}")

            if not patch:
                print("  ⏭ No new data")
                skipped += 1
                time.sleep(args.sleep)
                continue

            if args.dry_run:
                print(f"  🔍 Would update: {list(patch.keys())}")
                if patch.get("long_description"):
                    print(f"     Preview: {patch['long_description'][:120]}...")
                updated += 1
            else:
                ok = update_event(ev["id"], patch)
                if ok:
                    print(f"  ✅ Updated")
                    updated += 1
                else:
                    print(f"  ❌ Update failed")
                    failed += 1

            if "long_description" in patch: desc_added += 1
            if "street_address" in patch: addr_added += 1
            if "zip_code" in patch: zip_added += 1

            time.sleep(args.sleep)

        print(f"\n{'─'*40}")
        print(f"{source} backfill complete:")
        print(f"  Processed: {len(events)}")
        print(f"  Updated:   {updated}")
        print(f"  Skipped:   {skipped}")
        print(f"  Failed:    {failed}")
        print(f"  Descriptions added: {desc_added}")
        print(f"  Addresses added:    {addr_added}")
        print(f"  Zip codes added:    {zip_added}")


if __name__ == "__main__":
    main()
