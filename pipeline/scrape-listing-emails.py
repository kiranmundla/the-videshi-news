#!/usr/bin/env python3
"""Scrape contact emails from directory listing websites.

Visits each listing's website (homepage, then /contact, /contact-us, /about)
and extracts contact email addresses, storing them in the `email` column of
`directory_listings` in Supabase.

Respectful scraping:
- User-Agent identifies as TheVideshi-Bot
- 2s delay between sites
- 15s timeout per page
- Skips sites that fail/timeout
- Skips aggregator/directory domains (muslimguide.com etc.) — those pages
  are not the business's own site, so their emails are not outreach targets

Usage:
  python3 scrape-listing-emails.py --limit 5          # dry-run test (5 sites)
  python3 scrape-listing-emails.py --apply            # write results to DB
  python3 scrape-listing-emails.py --limit 200 --apply # daily cron batch

Progress is checkpointed in pipeline/.state/email-scrape-progress.json
so runs resume where the previous run left off.
"""
import json, subprocess, os, sys, re, time, argparse
from urllib.parse import urljoin, urlparse

SUPABASE_URL = os.environ['SUPABASE_URL'].rstrip('/')
KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          ".state", "email-scrape-progress.json")

BOT_UA = "TheVideshi-Bot/1.0 (+https://thevideshi.com)"
EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

# Emails / domains to never store
GARBAGE_DOMAINS = {
    'example.com', 'example.org', 'example.net', 'test.com',
    'sentry.io', 'sentry.wixpress.com', 'schema.org',
}

# Domain suffixes that are never a business inbox: error-tracking ingest
# endpoints (Sentry DSNs live on hosts like o123.ingest.us.sentry.io,
# whose exact subdomains change per project, so match the suffix).
GARBAGE_DOMAIN_SUFFIXES = ('.sentry.io',)


def is_garbage_domain(domain):
    """True for known garbage domains, incl. Wix Sentry DSN trap addresses.

    Wix sites embed error-reporting addresses like
    <hex>@sentry-next.wixpress.com in their JS — never a real inbox.
    """
    if domain in GARBAGE_DOMAINS:
        return True
    if domain.startswith('example.'):
        return True  # any @example.* placeholder domain, any TLD
    if domain.endswith(GARBAGE_DOMAIN_SUFFIXES):
        return True
    if '.ingest.' in f'.{domain}':
        return True  # telemetry/ingest subdomains on any provider
    if domain.endswith('.wixpress.com') and domain.split('.')[0].startswith('sentry'):
        return True
    return False
GARBAGE_LOCAL = re.compile(
    r'^(noreply|no-reply|donotreply|do-not-reply|mailer-daemon|postmaster|abuse|spam)'
    r'(@|$)', re.IGNORECASE)
# Template placeholder local parts (email@email.com, your@email.com,
# name@email.com …) — form/template filler, never a real inbox.
PLACEHOLDER_LOCAL = re.compile(
    r'^(e-?mail|your|your-?name|your-?e-?mail|name|example|sample|placeholder)$',
    re.IGNORECASE)
IMAGE_EXT = re.compile(r'\.(png|jpe?g|gif|webp|svg|ico|bmp)$', re.IGNORECASE)

# Preferred generic inboxes, in order
PREFERRED = ['info@', 'contact@', 'hello@', 'support@', 'office@',
             'admin@', 'mail@', 'enquiry@', 'inquiries@']

# Directory/aggregator domains whose pages are NOT the business's own site.
# Any email scraped there belongs to the aggregator, not the listing —
# writing it into the listing's email column pollutes outreach data
# (e.g. 2,798 listings point at muslimguide.com aggregator pages).
AGGREGATOR_DOMAINS = {
    'muslimguide.com',
    'yelp.com', 'yellowpages.com', 'yp.com', 'foursquare.com',
    'tripadvisor.com', 'opentable.com', 'zocdoc.com', 'healthgrades.com',
    'vitals.com', 'webmd.com', 'manta.com', 'chamberofcommerce.com',
    'bbb.org', 'mapquest.com', 'citysearch.com', 'dexknows.com',
    'superpages.com', 'merchantcircle.com', 'hotfrog.com', 'yext.com',
    'groupon.com', 'doordash.com', 'grubhub.com', 'ubereats.com',
    'seamless.com', 'postmates.com', 'thumbtack.com', 'angi.com',
    'homeadvisor.com', 'houzz.com', 'zillow.com', 'trulia.com',
    'realtor.com', 'apartments.com', 'glassdoor.com', 'indeed.com',
}


def db_get(path):
    out = subprocess.run(
        ["curl", "-sS", f"{SUPABASE_URL}{path}",
         "-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}"],
        capture_output=True, text=True, timeout=60)
    return json.loads(out.stdout)


def db_patch(path, data):
    out = subprocess.run(
        ["curl", "-sS", "-X", "PATCH", f"{SUPABASE_URL}{path}",
         "-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal",
         "-d", json.dumps(data)],
        capture_output=True, text=True, timeout=30)
    return out.returncode == 0


def fetch_page(url):
    """Fetch a page with curl. Returns HTML or None on failure."""
    try:
        out = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "15",
             "--max-redirs", "3",
             "-A", BOT_UA,
             "-o", "-", url],
            capture_output=True, timeout=25)
        if out.returncode != 0:
            return None
        # Only accept text/html
        html = out.stdout.decode('utf-8', errors='ignore')
        if '<html' not in html.lower() and '<body' not in html.lower():
            # Might still be HTML without tags; require some markup
            if len(html) < 500:
                return None
        return html
    except Exception:
        return None


def extract_emails(html):
    """Extract candidate emails from HTML, filtering garbage."""
    found = []
    for m in EMAIL_RE.finditer(html or ""):
        email = m.group(0).strip().rstrip('.,;:')
        if len(email) > 80:
            continue
        local, _, domain = email.partition('@')
        domain = domain.lower()
        if not local or not domain:
            continue
        if is_garbage_domain(domain):
            continue
        if GARBAGE_LOCAL.match(email):
            continue
        if PLACEHOLDER_LOCAL.match(local):
            continue
        if IMAGE_EXT.search(email):
            continue
        # Skip emails that look like file paths or CSS
        if '/' in email or '\\' in email:
            continue
        found.append(email)
    # Dedupe, case-insensitive
    seen = set()
    clean = []
    for e in found:
        key = e.lower()
        if key not in seen:
            seen.add(key)
            clean.append(e)
    return clean


def pick_best(emails):
    """Prefer generic inboxes over personal ones."""
    if not emails:
        return None
    for prefix in PREFERRED:
        for e in emails:
            if e.lower().startswith(prefix):
                return e
    return emails[0]


def normalize_url(site):
    site = (site or '').strip()
    if not site:
        return None
    if not site.startswith(('http://', 'https://')):
        site = 'https://' + site
    return site.rstrip('/')


def scrape_site(site):
    """Scrape a website for emails. Returns best email or None."""
    base = normalize_url(site)
    if not base:
        return None, "no-url"
    host = urlparse(base).netloc.lower().lstrip('www.')
    if host in AGGREGATOR_DOMAINS:
        return None, "aggregator"  # not the business's own site; skip
    pages = [base, urljoin(base + '/', 'contact'),
             urljoin(base + '/', 'contact-us'),
             urljoin(base + '/', 'about')]
    all_emails = []
    for page in pages:
        html = fetch_page(page)
        if html:
            emails = extract_emails(html)
            all_emails.extend(e for e in emails
                              if e.lower() not in [x.lower() for x in all_emails])
        if all_emails and page != base:
            break  # found something on a subpage, stop
    best = pick_best(all_emails)
    return best, ("found" if best else "none")


def load_progress():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except Exception:
            pass
    return {"last_id": None, "processed": 0, "found": 0, "failed": 0}


def save_progress(p):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    json.dump(p, open(STATE_FILE, "w"), indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=200,
                    help="max sites to process this run")
    ap.add_argument("--apply", action="store_true",
                    help="write emails to DB (default: dry run)")
    args = ap.parse_args()

    progress = load_progress()
    print(f"Resuming from id={progress['last_id']} "
          f"(processed={progress['processed']}, found={progress['found']})",
          flush=True)

    # Fetch listings with websites but no email, ordered by id.
    # Resume past the checkpoint in the query itself (id=gt.last_id):
    # filtering in memory after offset paging breaks the "short page =
    # end of list" check, because the first page after a resume is mostly
    # already-visited rows and looks short even when thousands of
    # unvisited rows remain at later offsets.
    batch_size = 100
    todo = []
    offset = 0
    while len(todo) < args.limit:
        q = ("/rest/v1/directory_listings?"
             "select=id,name,website&website=not.is.null&email=is.null"
             f"&order=id&limit={batch_size}&offset={offset}")
        if progress["last_id"]:
            q += f"&id=gt.{progress['last_id']}"
        batch = db_get(q)
        if not batch:
            break
        todo.extend(batch)
        if len(batch) < batch_size:
            break
        offset += batch_size
    todo = todo[:args.limit]

    if not todo:
        print("No listings left to process — all websites scraped.")
        return

    print(f"Processing {len(todo)} sites (dry run={not args.apply})...", flush=True)
    run_found = 0
    run_failed = 0
    run_skipped = 0
    progress.setdefault("skipped", 0)
    for i, row in enumerate(todo):
        email, status = scrape_site(row.get("website"))
        progress["processed"] += 1
        if status == "aggregator":
            run_skipped += 1
            progress["skipped"] += 1
            print(f"  [{i+1}/{len(todo)}] skip: aggregator site "
                  f"{row.get('name','?')[:40]} ({row.get('website','?')[:40]})",
                  flush=True)
        elif email:
            run_found += 1
            progress["found"] += 1
            tag = "APPLY " if args.apply else "WOULD "
            print(f"  [{i+1}/{len(todo)}] {tag}{row.get('name','?')[:40]} -> {email}",
                  flush=True)
            if args.apply:
                ok = db_patch(
                    f"/rest/v1/directory_listings?id=eq.{row['id']}",
                    {"email": email})
                if not ok:
                    print(f"    WARNING: PATCH failed for {row['id']}", flush=True)
        else:
            run_failed += 1
            progress["failed"] += 1
            print(f"  [{i+1}/{len(todo)}] no email: {row.get('name','?')[:40]} "
                  f"({row.get('website','?')[:40]})", flush=True)
        progress["last_id"] = row["id"]
        # Checkpoint every 10
        if (i + 1) % 10 == 0:
            save_progress(progress)
        # Rate limit between sites we actually fetched; aggregator skips
        # make no HTTP requests, so there is nothing to be polite about
        if status != "aggregator":
            time.sleep(2)

    save_progress(progress)
    print(f"\n{'='*50}")
    print(f"Run complete: {run_found} emails found, {run_failed} no-email/failed, "
          f"{run_skipped} aggregator-skipped")
    print(f"Totals: processed={progress['processed']}, found={progress['found']}, "
          f"failed={progress['failed']}")
    if not args.apply:
        print("(dry run — use --apply to write to DB)")


if __name__ == "__main__":
    main()
