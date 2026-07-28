#!/usr/bin/env python3
"""
Backfill Eventbrite events with full descriptions and proper venue addresses.

Fetches each Eventbrite event page, extracts the full description and
localized address, and updates the DB record.

Usage:
  python3 -u backfill-event-details.py              # Default 50 events
  python3 -u backfill-event-details.py --limit 10   # Custom limit
  python3 -u backfill-event-details.py --dry-run     # Preview without updating
  python3 -u backfill-event-details.py --source allevents  # Other sources
"""

import os, sys, json, re, time, subprocess, argparse
from html.parser import HTMLParser

# ── Env ──────────────────────────────────────────────────────────────────────

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)

SB_HOST = SUPABASE_URL.replace("https://", "")

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


# ── HTML helpers ─────────────────────────────────────────────────────────────

class HTMLStripper(HTMLParser):
    """Strip HTML tags, preserve newlines for block elements."""
    BLOCK_TAGS = {"p", "div", "br", "h1", "h2", "h3", "h4", "li", "tr"}

    def __init__(self):
        super().__init__()
        self.pieces = []
        self.tag_stack = []

    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)
        if tag in self.BLOCK_TAGS:
            self.pieces.append("\n")

    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        if tag in self.BLOCK_TAGS:
            self.pieces.append("\n")

    def handle_data(self, data):
        self.pieces.append(data)

    def get_text(self):
        raw = "".join(self.pieces)
        # Collapse multiple newlines to double, strip excessive whitespace
        raw = re.sub(r'\n{3,}', '\n\n', raw)
        raw = re.sub(r'[ \t]+', ' ', raw)
        return raw.strip()


def strip_html(html_text):
    """Convert HTML to readable plain text with paragraph breaks."""
    if not html_text:
        return ""
    s = HTMLStripper()
    try:
        s.feed(html_text)
        return s.get_text()
    except Exception:
        # Fallback: just strip tags
        return re.sub(r'<[^>]+>', ' ', html_text).strip()


# ── Eventbrite page fetch ────────────────────────────────────────────────────

def extract_server_data(html):
    """Extract __SERVER_DATA__ JSON from Eventbrite page HTML."""
    start = html.find("window.__SERVER_DATA__")
    if start < 0:
        return {}
    eq_pos = html.find("=", start)
    brace_start = html.find("{", eq_pos)
    if brace_start < 0:
        return {}
    depth = 0
    end = brace_start
    for i in range(brace_start, min(len(html), brace_start + 500000)):
        if html[i] == "{":
            depth += 1
        elif html[i] == "}":
            depth -= 1
        if depth == 0:
            end = i
            break
    try:
        return json.loads(html[brace_start:end + 1])
    except json.JSONDecodeError:
        return {}


def fetch_eventbrite_details(url):
    """Fetch an Eventbrite event page and extract full description + address.

    Returns dict with:
      - long_description: full text description (HTML stripped)
      - venue_name: venue name with street address
      - image_urls: list of image URLs found
    """
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
    except Exception as e:
        print(f"    Fetch error: {e}")
        return None

    html = r.stdout

    result = {}

    # Try structured data first (ld+json)
    ld_match = re.search(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    if ld_match:
        try:
            ld_data = json.loads(ld_match.group(1))
            if isinstance(ld_data, list):
                ld_data = ld_data[0] if ld_data else {}
            desc_html = ld_data.get("description", "")
            if desc_html and len(desc_html) > 50:
                result["long_description"] = strip_html(desc_html)[:5000]

            # Address from ld+json
            location = ld_data.get("location", {})
            if isinstance(location, dict):
                address = location.get("address", {})
                if isinstance(address, dict):
                    street = address.get("streetAddress", "")
                    venue_name = location.get("name", "")
                    if street and street not in venue_name:
                        result["venue_name"] = f"{venue_name}, {street}" if venue_name else street
                    elif venue_name:
                        result["venue_name"] = venue_name
        except (json.JSONDecodeError, KeyError):
            pass

    # Try __SERVER_DATA__ for richer content
    server_data = extract_server_data(html)
    if server_data:
        # Navigate to event details
        components = server_data.get("components", {})

        # Try multiple paths to find description
        for path_key in ["eventDescription", "listing_event"]:
            if path_key in components:
                comp = components[path_key]
                desc = comp.get("description", {})
                if isinstance(desc, dict):
                    html_desc = desc.get("html", "") or desc.get("text", "")
                else:
                    html_desc = str(desc) if desc else ""
                if html_desc and len(html_desc) > 50:
                    cleaned = strip_html(html_desc)
                    if len(cleaned) > len(result.get("long_description", "")):
                        result["long_description"] = cleaned[:5000]
                break

        # Structured description from listing
        listing = components.get("listing", {})
        if listing:
            structured_desc = listing.get("structuredContent", {})
            if structured_desc:
                modules = structured_desc.get("modules", [])
                text_parts = []
                for mod in modules:
                    if mod.get("type") == "text":
                        text_parts.append(strip_html(mod.get("text", "")))
                if text_parts:
                    joined = "\n\n".join(text_parts)
                    if len(joined) > len(result.get("long_description", "")):
                        result["long_description"] = joined[:5000]

    # Fallback: extract description from meta tags
    if "long_description" not in result or not result["long_description"]:
        og_desc = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if og_desc:
            desc_text = og_desc.group(1).strip()
            if len(desc_text) > 50:
                result["long_description"] = desc_text[:5000]

    # Fallback: look for structured content div
    if "long_description" not in result or not result["long_description"]:
        desc_div = re.search(
            r'<div[^>]*class="[^"]*structured-content[^"]*"[^>]*>(.*?)</div>\s*</div>',
            html, re.DOTALL | re.IGNORECASE
        )
        if desc_div:
            cleaned = strip_html(desc_div.group(1))
            if len(cleaned) > 50:
                result["long_description"] = cleaned[:5000]

    # Extract multiple images for venue_images
    image_urls = []
    # From og:image
    og_img = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if og_img:
        image_urls.append(og_img.group(1).strip())
    # From data attributes or picture tags in the gallery area
    for img_match in re.finditer(r'data-src=["\']([^"\']*evbuc[^"\']+)["\']', html):
        img_url = img_match.group(1)
        if img_url not in image_urls:
            image_urls.append(img_url)
    # From img tags with eventbrite CDN
    for img_match in re.finditer(r'<img[^>]+src=["\']([^"\']*(?:img\.evbuc|cdn\.evbuc)[^"\']+)["\']', html):
        img_url = img_match.group(1)
        if img_url not in image_urls and "loading" not in img_url.lower():
            image_urls.append(img_url)

    if len(image_urls) > 1:
        result["venue_images"] = image_urls[:10]  # Cap at 10

    return result if result else None


def fetch_allevents_details(url):
    """Fetch an AllEvents event page and extract description + image."""
    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "20",
             "-H", f"User-Agent: {UA}", url],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0 or not r.stdout:
            return None
    except Exception as e:
        print(f"    Fetch error: {e}")
        return None

    html = r.stdout
    result = {}

    # og:description
    og_desc = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if og_desc:
        desc = og_desc.group(1).strip()
        if len(desc) > 50:
            result["long_description"] = desc[:5000]

    # ld+json
    ld_match = re.search(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    if ld_match:
        try:
            ld_data = json.loads(ld_match.group(1))
            if isinstance(ld_data, list):
                ld_data = ld_data[0] if ld_data else {}
            desc_html = ld_data.get("description", "")
            if desc_html and len(desc_html) > len(result.get("long_description", "")):
                result["long_description"] = strip_html(desc_html)[:5000]
        except (json.JSONDecodeError, KeyError):
            pass

    return result if result else None


# ── DB helpers ───────────────────────────────────────────────────────────────

def fetch_events_to_backfill(source, limit):
    """Fetch events that need backfilling (no long_description, have ticket_url)."""
    url = (
        f"{SUPABASE_URL}/rest/v1/events"
        f"?source=eq.{source}"
        f"&long_description=is.null"
        f"&ticket_url=not.is.null"
        f"&select=id,title,ticket_url,venue_name,date"
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
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"  Failed to parse events list: {r.stdout[:200]}")
        return []


def update_event(event_id, updates):
    """Patch an event record with new fields."""
    # Remove None values
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


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Backfill event details from source pages")
    parser.add_argument("--limit", type=int, default=50, help="Max events to process (default 50)")
    parser.add_argument("--dry-run", action="store_true", help="Fetch but don't update DB")
    parser.add_argument("--source", default="eventbrite", help="Event source to backfill (default: eventbrite)")
    parser.add_argument("--sleep", type=float, default=1.5, help="Seconds between fetches (default 1.5)")
    args = parser.parse_args()

    fetch_fn = {
        "eventbrite": fetch_eventbrite_details,
        "allevents": fetch_allevents_details,
    }.get(args.source)

    if not fetch_fn:
        print(f"No fetcher for source '{args.source}'. Supported: eventbrite, allevents")
        sys.exit(1)

    events = fetch_events_to_backfill(args.source, args.limit)
    print(f"Found {len(events)} {args.source} events to backfill")

    if not events:
        print("Nothing to do.")
        return

    updated = 0
    skipped = 0
    failed = 0

    for i, ev in enumerate(events):
        title = ev.get("title", "")[:50]
        ticket_url = ev.get("ticket_url", "")
        print(f"\n[{i+1}/{len(events)}] {title}...")

        if not ticket_url:
            print("  ⏭ No ticket URL")
            skipped += 1
            continue

        details = fetch_fn(ticket_url)

        if not details:
            print("  ⚠ Could not extract details")
            failed += 1
            time.sleep(args.sleep)
            continue

        # Build update payload
        patch = {}
        if details.get("long_description"):
            patch["long_description"] = details["long_description"]
            print(f"  📝 Description: {len(details['long_description'])} chars")

        if details.get("venue_name"):
            # Only update if the new name has more info (contains address)
            current_venue = ev.get("venue_name", "")
            new_venue = details["venue_name"]
            if len(new_venue) > len(current_venue or ""):
                patch["venue_name"] = new_venue
                print(f"  📍 Venue: {new_venue[:60]}")

        if details.get("venue_images"):
            patch["venue_images"] = details["venue_images"]
            print(f"  🖼 Images: {len(details['venue_images'])}")

        if not patch:
            print("  ⏭ No new data found")
            skipped += 1
            time.sleep(args.sleep)
            continue

        if args.dry_run:
            print(f"  🔍 Would update: {list(patch.keys())}")
            if patch.get("long_description"):
                print(f"     Preview: {patch['long_description'][:150]}...")
            updated += 1
        else:
            ok = update_event(ev["id"], patch)
            if ok:
                print(f"  ✅ Updated")
                updated += 1
            else:
                print(f"  ❌ Update failed")
                failed += 1

        time.sleep(args.sleep)

    # Summary
    print(f"\n{'='*50}")
    print(f"Backfill complete for {args.source}")
    print(f"  Processed: {len(events)}")
    print(f"  Updated:   {updated}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")


if __name__ == "__main__":
    main()
