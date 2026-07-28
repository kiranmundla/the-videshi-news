#!/usr/bin/env python3
"""
backfill-spiritual-events.py — Enrich spiritual-scraper events with
image_url, long_description, street_address, and zip_code by visiting
each event's ticket_url.

Domains handled:
  - www.dhamma.org          — physical address, center description
  - isha.sadhguru.org       — og:image, og:description
  - innerengineering.sadhguru.org — og:image, og:description
  - bklosangeles.org        — og:image, meta description
  - gurudev.artofliving.org — og:image, meta description, address

Usage:
  python3 -u backfill-spiritual-events.py [--limit N] [--dry-run] [--sleep SECS]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from html.parser import HTMLParser
from urllib.parse import urlparse

# ── Env ──────────────────────────────────────────────────────────────────────

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/workspace/.env.supabase'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', '')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY or not SUPABASE_ANON_KEY:
    print("ERROR: Missing Supabase env vars", file=sys.stderr)
    sys.exit(1)

# Strip https:// — env already includes it
SB_HOST = SUPABASE_URL.replace('https://', '').rstrip('/')

# ── HTML text extractor ──────────────────────────────────────────────────────

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'):
            self.skip = True
        if tag in ('br', 'p', 'div', 'h1', 'h2', 'h3', 'h4', 'li', 'tr'):
            self.text.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript'):
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)

    def get_text(self):
        return re.sub(r'\n{3,}', '\n\n', ''.join(self.text)).strip()


def extract_text(html):
    """Strip HTML to plain text."""
    ext = TextExtractor()
    try:
        ext.feed(html)
    except Exception:
        pass
    return ext.get_text()


# ── HTTP fetch via curl ──────────────────────────────────────────────────────

def fetch_url(url, timeout=15):
    """Fetch URL with curl, return raw HTML string or None."""
    try:
        r = subprocess.run(
            ['curl', '-sL', '--max-time', str(timeout),
             '-A', 'Mozilla/5.0 (compatible; TheVideshi/1.0)',
             url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        if r.returncode == 0 and r.stdout:
            return r.stdout
    except Exception as e:
        print(f"  WARN: fetch failed for {url}: {e}", file=sys.stderr)
    return None


# ── Meta tag extraction ──────────────────────────────────────────────────────

def is_logo_or_icon(url):
    """Check if URL looks like a logo, icon, or favicon rather than content."""
    lower = url.lower()
    return any(kw in lower for kw in ['logo', 'favicon', 'icon', 'flag', 'badge', 'sprite'])


def extract_og_image(html, skip_logos=False):
    """Extract og:image from HTML."""
    m = re.search(
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        html, re.IGNORECASE
    )
    if not m:
        m = re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
            html, re.IGNORECASE
        )
    if m:
        url = m.group(1).strip()
        if url and not url.endswith('.ico') and len(url) > 10:
            if skip_logos and is_logo_or_icon(url):
                pass
            else:
                return url
    m = re.search(
        r'<meta[^>]+name=["\']image["\'][^>]+content=["\']([^"\']+)["\']',
        html, re.IGNORECASE
    )
    if m:
        url = m.group(1).strip()
        if url and not url.endswith('.ico'):
            if not (skip_logos and is_logo_or_icon(url)):
                return url
    return None


def extract_content_images(html):
    """Find actual content images in HTML, skipping logos/icons/flags/thumbnails."""
    imgs = re.findall(r'https?://[^\s"<>\']+\.(?:jpg|jpeg|png|webp)', html)
    seen = set()
    results = []
    for img in imgs:
        if img in seen:
            continue
        seen.add(img)
        if is_logo_or_icon(img):
            continue
        # Skip tiny thumbnails (URL contains dimension suffixes like -150x112)
        if re.search(r'-\d{2,3}x\d{2,3}\.', img):
            continue
        results.append(img)
    return results


def extract_meta_description(html):
    """Extract og:description or meta description."""
    # og:description first
    m = re.search(
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
        html, re.IGNORECASE
    )
    if not m:
        m = re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:description["\']',
            html, re.IGNORECASE
        )
    if not m:
        # plain meta description
        m = re.search(
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
            html, re.IGNORECASE
        )
    if not m:
        m = re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']',
            html, re.IGNORECASE
        )
    if m:
        desc = m.group(1).strip()
        if len(desc) > 20:
            # Skip very generic page descriptions
            if re.match(r'^Find upcoming .+ programs in ', desc, re.IGNORECASE):
                return None
            return desc
    return None


# ── Domain-specific extractors ───────────────────────────────────────────────

def extract_dhamma_address(html, text):
    """Extract physical address from dhamma.org schedule pages."""
    address = None
    zip_code = None

    # Look for "Physical Address: ..." pattern
    m = re.search(r'Physical Address:\s*(.+?)(?:<|$)', html, re.IGNORECASE)
    if m:
        address = re.sub(r'<[^>]+>', ' ', m.group(1)).strip()
        address = re.sub(r'\s+', ' ', address).strip()

    # Also try "Mailing Address:" if no physical
    if not address:
        m = re.search(r'Mailing Address:\s*(.+?)(?:<|$)', html, re.IGNORECASE)
        if m:
            address = re.sub(r'<[^>]+>', ' ', m.group(1)).strip()
            address = re.sub(r'\s+', ' ', address).strip()

    # Try address from the structured text — look for patterns like "1234 Road Name, City, ST 12345"
    if not address:
        m = re.search(r'(\d+\s+[A-Za-z\s]+(?:Road|Rd|Street|St|Avenue|Ave|Drive|Dr|Lane|Ln|Way|Blvd|Boulevard|Highway|Hwy|Route|County Road|CR)\b[^<\n]{5,80})', text)
        if m:
            address = m.group(1).strip().rstrip(',').strip()

    # Extract zip from address or broader text
    if address:
        zm = re.search(r'\b(\d{5}(?:-\d{4})?)\b', address)
        if zm:
            zip_code = zm.group(1)

    if not zip_code:
        # Try from the full text near "Address" context
        for block in re.finditer(r'(?:Address|Location)[:\s].{0,200}', text, re.IGNORECASE):
            zm = re.search(r'\b(\d{5}(?:-\d{4})?)\b', block.group())
            if zm:
                zip_code = zm.group(1)
                break

    return address, zip_code


def extract_dhamma_description(html, text):
    """Extract a useful description from dhamma.org pages."""
    # Look for the center name and description
    desc_parts = []

    # Center name (bold text usually)
    m = re.search(r'<p><strong>([^<]+(?:Vipassana|Dhamma)[^<]*)</strong></p>', html, re.IGNORECASE)
    if m:
        desc_parts.append(m.group(1).strip())

    # Look for descriptive paragraphs about the center or meditation
    for pm in re.finditer(r'<p>([^<]{50,500})</p>', html):
        p = pm.group(1).strip()
        # Skip navigation/form text
        if any(skip in p.lower() for skip in ['javascript', 'cookie', 'email', 'password', 'login', 'registration']):
            continue
        if 'vipassana' in p.lower() or 'meditation' in p.lower() or 'course' in p.lower():
            desc_parts.append(p)
            break

    if desc_parts:
        return ' '.join(desc_parts)

    # Fallback: generic Vipassana description
    return None


def extract_isha_data(html):
    """Extract data from Isha/InnerEngineering pages."""
    image = extract_og_image(html, skip_logos=True)
    desc = extract_meta_description(html)

    # If no og:image, try content images (skip generic buttons/nav)
    if not image:
        content_imgs = extract_content_images(html)
        # Filter to Sadhguru/Isha-related images
        for ci in content_imgs:
            if 'static.sadhguru.org' in ci or 'innerengineering' in ci:
                # Skip tiny nav images
                if 'menu' in ci.lower() or 'btn' in ci.lower() or 'subscribe' in ci.lower() or 'footer' in ci.lower():
                    continue
                image = ci
                break

    # Try to find address in structured data or page content
    address = None
    zip_code = None

    # Check for JSON-LD
    for m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE):
        try:
            ld = json.loads(m.group(1))
            if isinstance(ld, dict):
                loc = ld.get('location', {})
                if isinstance(loc, dict):
                    addr = loc.get('address', {})
                    if isinstance(addr, dict):
                        street = addr.get('streetAddress', '')
                        postal = addr.get('postalCode', '')
                        if street:
                            address = street
                        if postal:
                            zip_code = postal
        except Exception:
            pass

    return image, desc, address, zip_code


def extract_aol_data(html, text):
    """Extract data from Art of Living pages."""
    # Skip logo og:image, look for real content images
    image = extract_og_image(html, skip_logos=True)
    if not image:
        content_imgs = extract_content_images(html)
        if content_imgs:
            image = content_imgs[0]  # First content image is usually hero

    desc = extract_meta_description(html)

    address = None
    zip_code = None

    # Look for venue/address in page
    m = re.search(r'(?:Address|Location|Venue)[:\s]+([^<\n]{10,100})', text, re.IGNORECASE)
    if m:
        address = m.group(1).strip()
        zm = re.search(r'\b(\d{5}(?:-\d{4})?)\b', address)
        if zm:
            zip_code = zm.group(1)

    # Check JSON-LD for address
    for m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE):
        try:
            ld = json.loads(m.group(1))
            if isinstance(ld, dict):
                addr = ld.get('address', ld.get('location', {}).get('address', {}))
                if isinstance(addr, dict):
                    if not address and addr.get('streetAddress'):
                        address = addr['streetAddress']
                    if not zip_code and addr.get('postalCode'):
                        zip_code = addr['postalCode']
        except Exception:
            pass

    return image, desc, address, zip_code


def extract_bk_data(html, text):
    """Extract data from Brahma Kumaris pages."""
    image = extract_og_image(html, skip_logos=True)
    desc = extract_meta_description(html)

    address = None
    zip_code = None

    # BK LA address is usually on their contact page
    m = re.search(r'(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Blvd|Boulevard|Drive|Dr|Road|Rd)[^<\n]{5,80})', text)
    if m:
        address = m.group(1).strip().rstrip(',').strip()
        zm = re.search(r'\b(\d{5}(?:-\d{4})?)\b', address)
        if zm:
            zip_code = zm.group(1)

    return image, desc, address, zip_code


# ── Main enrichment logic ────────────────────────────────────────────────────

def enrich_event(event, dry_run=False):
    """Fetch event's ticket_url, extract fields, return dict of updates."""
    url = event.get('ticket_url', '')
    if not url:
        print(f"  SKIP: no ticket_url")
        return {}

    domain = urlparse(url).netloc.lower()
    print(f"  Fetching: {url}")
    print(f"  Domain: {domain}")

    html = fetch_url(url)
    if not html:
        print(f"  WARN: could not fetch page")
        return {}

    text = extract_text(html)
    print(f"  Fetched {len(html)} chars HTML, {len(text)} chars text")

    image = None
    description = None
    address = None
    zip_code = None

    if 'dhamma.org' in domain:
        address, zip_code = extract_dhamma_address(html, text)
        description = extract_dhamma_description(html, text)
        image = extract_og_image(html)  # Usually none, but try

    elif 'sadhguru.org' in domain or 'innerengineering' in domain:
        image, description, address, zip_code = extract_isha_data(html)

    elif 'artofliving.org' in domain:
        image, description, address, zip_code = extract_aol_data(html, text)

    elif 'bklosangeles.org' in domain:
        image, description, address, zip_code = extract_bk_data(html, text)

    else:
        # Generic: try og:image + meta description
        image = extract_og_image(html)
        description = extract_meta_description(html)

    # Build update dict — only fields that are currently null AND we found data
    updates = {}
    if event.get('image_url') is None and image:
        # Fix protocol-relative URLs and skip logos
        if image.startswith('//'):
            image = 'https:' + image
        if not is_logo_or_icon(image):
            updates['image_url'] = image
    if event.get('long_description') is None and description:
        updates['long_description'] = description
    if event.get('street_address') is None and address:
        # Clean up address
        address = re.sub(r'\s+', ' ', address).strip()
        if len(address) > 200:
            address = address[:200]
        updates['street_address'] = address
    if event.get('zip_code') is None and zip_code:
        updates['zip_code'] = zip_code

    return updates


def patch_event(event_id, updates):
    """PATCH event in Supabase."""
    url = f"https://{SB_HOST}/rest/v1/events?id=eq.{event_id}"
    payload = json.dumps(updates)

    r = subprocess.run(
        ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
         '-X', 'PATCH', url,
         '-H', f'apikey: {SUPABASE_SERVICE_KEY}',
         '-H', f'Authorization: Bearer {SUPABASE_SERVICE_KEY}',
         '-H', 'Content-Type: application/json',
         '-H', 'Prefer: return=minimal',
         '-d', payload],
        capture_output=True, text=True, timeout=15
    )

    code = r.stdout.strip()
    if code in ('200', '204'):
        return True
    else:
        print(f"  WARN: PATCH returned {code}", file=sys.stderr)
        return False


# ── Supabase query ───────────────────────────────────────────────────────────

def get_events_needing_backfill(limit=200):
    """Query spiritual-scraper events missing image/description/address."""
    # Get all spiritual-scraper events, then filter in Python
    url = (
        f"https://{SB_HOST}/rest/v1/events"
        f"?source=eq.spiritual-scraper"
        f"&select=id,title,ticket_url,image_url,long_description,street_address,zip_code,category"
        f"&order=date.desc"
        f"&limit={limit}"
    )

    r = subprocess.run(
        ['curl', '-s', url,
         '-H', f'apikey: {SUPABASE_ANON_KEY}',
         '-H', f'Authorization: Bearer {SUPABASE_ANON_KEY}'],
        capture_output=True, text=True, timeout=15
    )

    try:
        events = json.loads(r.stdout)
    except Exception:
        print(f"ERROR: Could not parse Supabase response: {r.stdout[:200]}", file=sys.stderr)
        return []

    if isinstance(events, dict) and 'message' in events:
        print(f"ERROR: Supabase error: {events['message']}", file=sys.stderr)
        return []

    # Filter to events that need enrichment
    needing = [
        e for e in events
        if e.get('image_url') is None
        or e.get('long_description') is None
        or e.get('street_address') is None
    ]

    print(f"Found {len(events)} total spiritual-scraper events, {len(needing)} need enrichment")
    return needing


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Backfill spiritual event details')
    parser.add_argument('--limit', type=int, default=200, help='Max events to process')
    parser.add_argument('--dry-run', action='store_true', help='Extract but do not update DB')
    parser.add_argument('--sleep', type=float, default=2.0, help='Sleep between requests (seconds)')
    args = parser.parse_args()

    events = get_events_needing_backfill(limit=500)  # Fetch more, limit processing
    if not events:
        print("No events to backfill")
        return

    events = events[:args.limit]
    print(f"\nProcessing {len(events)} events (dry_run={args.dry_run}, sleep={args.sleep}s)\n")

    stats = {'processed': 0, 'updated': 0, 'skipped': 0, 'errors': 0,
             'image_filled': 0, 'desc_filled': 0, 'addr_filled': 0, 'zip_filled': 0}

    # Group by domain to avoid hammering same site
    for i, event in enumerate(events, 1):
        title = event.get('title', '???')
        eid = event.get('id')
        print(f"[{i}/{len(events)}] {title}")

        try:
            updates = enrich_event(event, dry_run=args.dry_run)
        except Exception as e:
            print(f"  ERROR: {e}")
            stats['errors'] += 1
            continue

        stats['processed'] += 1

        if not updates:
            print(f"  No new data found")
            stats['skipped'] += 1
        else:
            print(f"  Found: {list(updates.keys())}")
            for k, v in updates.items():
                val_preview = str(v)[:80] + ('...' if len(str(v)) > 80 else '')
                print(f"    {k}: {val_preview}")

            if 'image_url' in updates:
                stats['image_filled'] += 1
            if 'long_description' in updates:
                stats['desc_filled'] += 1
            if 'street_address' in updates:
                stats['addr_filled'] += 1
            if 'zip_code' in updates:
                stats['zip_filled'] += 1

            if not args.dry_run:
                ok = patch_event(eid, updates)
                if ok:
                    print(f"  ✓ Updated")
                    stats['updated'] += 1
                else:
                    print(f"  ✗ Update failed")
                    stats['errors'] += 1
            else:
                print(f"  (dry run — not saved)")
                stats['updated'] += 1

        if i < len(events):
            time.sleep(args.sleep)

    print(f"\n{'='*60}")
    print(f"DONE — Backfill complete")
    print(f"  Processed: {stats['processed']}")
    print(f"  Updated:   {stats['updated']}")
    print(f"  Skipped:   {stats['skipped']}")
    print(f"  Errors:    {stats['errors']}")
    print(f"  Images filled:       {stats['image_filled']}")
    print(f"  Descriptions filled: {stats['desc_filled']}")
    print(f"  Addresses filled:    {stats['addr_filled']}")
    print(f"  Zip codes filled:    {stats['zip_filled']}")


if __name__ == '__main__':
    main()
