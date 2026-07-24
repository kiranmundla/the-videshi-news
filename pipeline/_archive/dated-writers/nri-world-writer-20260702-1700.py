#!/usr/bin/env python3
"""NRI World Writer — July 2, 2026 evening batch.

Article 1: Carnegie Corporation's 2026 'Great Immigrants, Great Americans' — 4 Indian Americans honored
Article 2: NFAP report — Indian immigrants founded 96 US unicorns, more than any other country
"""

import json, os, uuid, re, io, requests, subprocess
from datetime import datetime, timezone
from pathlib import Path

# ── env ──────────────────────────────────────────────────
env_file = Path.home() / "workspace" / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

pexels_env = Path.home() / "workspace" / ".env.pexels"
for line in pexels_env.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  ✗ INSERT {table} failed {r.status_code}: {r.text[:300]}")
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-20260702"


# ── image helpers ────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's photo from Wikipedia. Returns (thumb_url, original_url) or (None, None).
    thumb_url is pre-resized to ~1200px wide when available."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            original = data.get("originalimage", {}).get("source")
            thumb = data.get("thumbnail", {}).get("source")
            if original or thumb:
                print(f"  ✓ Wikipedia image found for '{person_name}'")
                # Try to get a 1200px thumb via Commons API
                if original:
                    fname = original.split("/")[-1]
                    try:
                        cr = requests.get(
                            "https://commons.wikimedia.org/w/api.php",
                            params={
                                "action": "query", "titles": f"File:{fname}",
                                "prop": "imageinfo", "iiprop": "url",
                                "iiurlwidth": "1200", "format": "json"
                            },
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                            timeout=10
                        )
                        if cr.status_code == 200:
                            pages = cr.json().get("query", {}).get("pages", {})
                            for pg in pages.values():
                                ii = pg.get("imageinfo", [{}])[0]
                                tu = ii.get("thumburl")
                                if tu:
                                    print(f"  ✓ Got 1200px thumbnail from Commons API")
                                    return tu, original
                    except Exception:
                        pass
                # Fallback: return whatever we have
                return (thumb or original), original
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None, None


def fetch_pexels_image(query):
    """Search Pexels for an image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            timeout=15,
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def download_image(url):
    """Download image bytes. Tries requests first, then curl for Wikimedia 429s."""
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
        elif r.status_code == 429:
            print(f"  ⚠ 429 on requests, trying curl...")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")

    # curl fallback (Wikimedia 429 workaround)
    tmp = "/tmp/img_download.jpg"
    result = subprocess.run(
        ["curl", "-sS", "-A", "TheVideshi/1.0 (thevideshi.com)", "-o", tmp, url],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0 and os.path.exists(tmp):
        data = open(tmp, "rb").read()
        if len(data) > 1000:
            return data
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def upload_image_to_supabase(jpeg_bytes, filename):
    """Upload compressed JPEG to article-images bucket. Returns public URL or None."""
    r = requests.post(
        f"{SB_URL}/storage/v1/object/article-images/{filename}",
        headers={
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        },
        data=jpeg_bytes,
        timeout=60,
    )
    if r.status_code not in (200, 201):
        print(f"  ⚠ Supabase upload failed {r.status_code}: {r.text[:200]}")
        return None
    public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
    return public_url


def source_and_upload_image(image_url, slug, attribution_source="Wikimedia Commons"):
    """Download, compress, upload. Returns (supabase_url, attribution) or (None, None)."""
    raw = download_image(image_url)
    if not raw:
        print(f"  ✗ Failed to download image")
        return None, None
    print(f"  → Downloaded {len(raw):,} bytes")
    compressed = compress_image(raw)
    print(f"  → Compressed to {len(compressed):,} bytes")
    if len(compressed) < 5000:
        print(f"  ⚠ Compressed image too small ({len(compressed)} bytes), skipping")
        return None, None
    filename = f"{slug}.jpg"
    sb_url = upload_image_to_supabase(compressed, filename)
    return sb_url, attribution_source


# ═══════════════════════════════════════════════════════════
# ARTICLE 1: Carnegie's Great Immigrants — 4 Indian Americans
# ═══════════════════════════════════════════════════════════

print("\n" + "="*60)
print("ARTICLE 1: Carnegie Great Immigrants 2026")
print("="*60)

art1_slug = make_slug("carnegie-great-immigrants-indian-americans-july-4th")

art1_body = """On the eve of America's 250th birthday, the Carnegie Corporation of New York released its annual "Great Immigrants, Great Americans" list — and four of the 25 names on it trace their roots to India. Nikesh Arora, Mahzarin Banaji, Sanjiv Chopra, and Reshma Kewalramani join a class of naturalized citizens drawn from 21 countries, announced on June 30 and timed, as always, to the Fourth of July.

The honour has been a fixture since 2006, when the foundation named after the Scottish-born steel magnate began recognising immigrants who had made outsized contributions to their adopted country. Over 790 people have been named across two decades. The Indian-origin alumni list now reads like a directory of institutional power: Sundar Pichai, Shantanu Narayen, Vivek Murthy, Abhijit Banerjee, Gita Gopinath. Four more names only thickens the pattern.

## The class of 2026

Nikesh Arora, born in Uttar Pradesh, runs Palo Alto Networks as chairman and CEO. Before building one of the world's largest cybersecurity firms — its market capitalisation now exceeds $100 billion — he spent a decade at Google, rising to chief business officer and one of the company's highest-paid executives. His path from the Indian Administrative Service exam halls of the 1990s to Silicon Valley's corner offices is, in one sense, a classic H-1B arc. In another, it is exceptional: Palo Alto Networks now protects the digital infrastructure of more than 80,000 organisations worldwide.

Mahzarin Banaji, born in Hyderabad, is the Richard Clarke Cabot Professor of Social Ethics at Harvard. Her work on implicit bias — the idea that unconscious attitudes shape behaviour in ways people cannot easily detect or control — has reshaped fields from psychology to law to corporate training. The Implicit Association Test she co-developed is among the most widely used instruments in social science.

Sanjiv Chopra, born in New Delhi, is a professor of medicine at Harvard Medical School and a specialist in liver disease who has trained generations of hepatologists. He is also the older brother of Deepak Chopra, the wellness author, though his own career has stayed firmly within academic medicine. His contributions to medical education earned him Harvard's Robert S. Stone Award for outstanding teaching.

Reshma Kewalramani, born in Mumbai, is president and CEO of Vertex Pharmaceuticals, the company whose cystic fibrosis treatments have transformed the disease from a near-certain early death sentence into a manageable condition. A nephrologist by training, she joined Vertex in 2017 and took the top job in 2020. Under her leadership, Vertex has expanded into gene editing and pain management, with a market capitalisation exceeding $100 billion.

## A 250th anniversary with an asterisk

This year's list carries an added weight. Carnegie chose to mark America's semiquincentennial by also recognising the eight foreign-born signers of the Declaration of Independence — a pointed reminder that the country's founding document was, in part, an immigrant production. In a commissioned essay, philosopher Kwame Anthony Appiah, himself a past honouree, reflected on the "unending project of defining and refining what it means to be American."

The timing is not lost on the diaspora. The honour arrives in a year when H-1B registrations have dropped 38.5 per cent and net migration to the United States has, by some measures, turned negative for the first time in half a century. For Indian Americans — who make up roughly 1.4 per cent of the US population but a far larger share of its tech workforce, medical establishment, and academic faculty — the juxtaposition is sharp. The same country that names them "Great Americans" is, in policy terms, making it harder for the next generation to arrive.

## The diaspora's long game

What the Carnegie list captures, year after year, is not merely individual brilliance but a structural reality. Indian immigrants have reached the commanding heights of American institutions — running Fortune 500 companies, leading Ivy League departments, heading federal agencies — at a rate that outstrips their numbers by an order of magnitude. The 2026 list, spanning cybersecurity, social science, medicine, and biotech, is a cross-section of that reach.

For the four honourees, the recognition is personal. For the diaspora watching from WhatsApp groups and LinkedIn feeds, it is something else: a data point in an ongoing argument about who belongs and what belonging costs. This Fourth of July, at least, the Carnegie Corporation has made its position clear."""

# Image: Nikesh Arora Wikipedia
print("\nSourcing hero image for Article 1...")
wiki_thumb, wiki_orig = fetch_wikipedia_person_image("Nikesh Arora")
art1_img_url = None
art1_img_attr = "Wikimedia Commons"
art1_img_caption = "Nikesh Arora, chairman and CEO of Palo Alto Networks, one of four Indian Americans named to Carnegie's 2026 Great Immigrants list"

if wiki_thumb:
    art1_img_url, art1_img_attr = source_and_upload_image(wiki_thumb, art1_slug)
    if not art1_img_url and wiki_orig and wiki_orig != wiki_thumb:
        print("  → Thumbnail failed, trying original...")
        art1_img_url, art1_img_attr = source_and_upload_image(wiki_orig, art1_slug)

if not art1_img_url:
    # Fallback: try Pexels
    pexels_url = fetch_pexels_image("American flag celebration July 4th patriotic")
    if pexels_url:
        art1_img_url, art1_img_attr = source_and_upload_image(pexels_url, art1_slug, "Pexels")
        art1_img_caption = "The Carnegie Corporation's Great Immigrants initiative honours naturalized citizens every Fourth of July"

if art1_img_url:
    print(f"  ✓ Hero image ready: {art1_img_url[:60]}...")
else:
    print("  ✗ No hero image — will insert without image")
    art1_img_url = ""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Carnegie Names Four Indian Americans to Its 'Great Immigrants' List — on the Eve of America's 250th Birthday",
    "subheadline": "Nikesh Arora, Mahzarin Banaji, Sanjiv Chopra, and Reshma Kewalramani join a class of 25 naturalized citizens honoured by the Carnegie Corporation for the Fourth of July.",
    "slug": art1_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Four Indian-born leaders — spanning cybersecurity, social psychology, medicine, and biotech — are honoured as 'Great Americans' at a moment when immigration restrictions are tightening. The recognition underscores the diaspora's institutional reach across American life.",
    "tags": ["nri", "diaspora", "carnegie", "great-immigrants", "nikesh-arora", "palo-alto-networks", "mahzarin-banaji", "sanjiv-chopra", "reshma-kewalramani", "vertex", "july-4th", "america-250"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Carnegie Corporation of New York", "url": "https://www.carnegie.org/awards/great-immigrants/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/world/nikesh-arora-mahzarin-banaji-dr-sanjiv-chopra-and-reshma-kewalramani-named-to-carnegies-great-immigrants-list-for-2026/article69753017.ece"},
        {"name": "Connected to India", "url": "https://connectedtoindia.com/carnegie-names-4-indian-americans-to-prestigious-great-immigrants-list/"},
        {"name": "Tezzbuzz", "url": "https://tezzbuzz.com/hyderabad-born-mahzarin-banaji-among-carnegies-great-immigrants-honourees/"},
        {"name": "Associated Press / Barchart", "url": "https://www.barchart.com/story/news/31923783/the-full-list-of-the-2026-class-of-great-immigrants-great-americans"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art1_img_url,
    "image_caption": art1_img_caption,
    "image_attribution": art1_img_attr,
    "body": art1_body.strip(),
}


# ═══════════════════════════════════════════════════════════
# ARTICLE 2: Indian Immigrants Founded 96 US Unicorns
# ═══════════════════════════════════════════════════════════

print("\n" + "="*60)
print("ARTICLE 2: Indian Immigrants Founded 96 US Unicorns")
print("="*60)

art2_slug = make_slug("indian-immigrants-96-us-unicorns-nfap-founders")

art2_body = """India is the single largest source of immigrant founders behind America's billion-dollar startup companies — and it is not close. A new analysis by the National Foundation for American Policy has found that Indian-born entrepreneurs have founded or co-founded 96 US unicorns, placing India ahead of every other country by a wide margin. Israel comes second with 60, followed by the United Kingdom with 47 and China with 41.

The numbers are drawn from a comprehensive study of all 775 privately held US startup companies valued at $1 billion or more as of April 2026. Across those companies, immigrants from 76 countries have contributed to the founding of 59 per cent of America's unicorns — 455 companies collectively generating roughly $5 trillion in value and creating hundreds of thousands of jobs. India's 96-company slice of that pie is, by itself, worth more than the entire stock market of Germany.

## The names behind the numbers

The highest-valued US unicorn with an Indian-born founder is Perplexity, the AI search company co-founded by Aravind Srinivas, valued at $20 billion and ranked 12th overall. But the list stretches far beyond a single headline name. Prasanna Sankar co-founded Rippling, the HR platform. Mohit Aron built Cohesity, the data management company. Deepak Pathak and Abhinav Gupta co-founded Skild AI, now one of the hottest robotics startups in Pittsburgh. Jyoti Bansal, who founded AppDynamics and later Harness, is one of six Indian-origin entrepreneurs who have built two or more unicorns.

What links most of these founders is the pipeline that brought them to America. Of the 96 Indian-origin unicorn founders, at least 76 first arrived in the United States as international students — overwhelmingly from the Indian Institutes of Technology. IIT Delhi alone has produced 16 unicorn founders; IIT Bombay, 14. The journey is almost formulaic: an IIT undergraduate degree, a US graduate programme, a stint at a tech giant, and then a startup. The formula, of course, understates the ambition required to execute it.

## A structural advantage — under threat

The NFAP study arrives at an uncomfortable moment. H-1B visa registrations for the 2026-2027 cycle dropped 38.5 per cent from the previous year, according to US Citizenship and Immigration Services data. The Brookings Institution reports that 2025 marked the first year of net negative migration to the United States in half a century. The Department of Homeland Security has proposed replacing the open-ended "duration of status" framework for international students with fixed admission periods — a change that, if implemented, would add bureaucratic friction to the exact pipeline that produced these 96 companies.

The irony is not subtle. The same policy apparatus that is tightening the door is celebrating the output of the people who walked through it when it was open. Stuart Anderson, the NFAP's executive director and author of the study, has been making this point for years: immigrant-founded companies do not merely create wealth for their founders. They create jobs, tax revenue, and entire industries. Fifteen immigrants, including Elon Musk, have founded two or more unicorns. Nearly 80 per cent of US unicorns have either an immigrant founder or an immigrant in a key leadership role.

## The diaspora's entrepreneurial turn

For the Indian diaspora specifically, the 96-unicorn figure represents something relatively new. As The Hindu Business Line noted, most of these companies were founded in the past decade. Earlier generations of Indian immigrants in the United States gravitated toward stable employment — medicine, engineering, academia — rather than the high-risk world of venture-backed startups. The cultural shift is generational: the children and grandchildren of H-1B holders who watched their parents build careers at Cisco and Google are now building companies of their own.

But the study also reveals a ceiling. The highest-valued unicorns in the United States — SpaceX ($1.5 trillion), Anthropic ($965 billion), OpenAI ($852 billion) — were not founded by Indians. The majority of the 96 Indian-founded unicorns are valued below $10 billion. India leads in volume; it has not yet produced the singular, category-defining company that rewrites an industry.

That distinction may matter less than the aggregate. Ninety-six billion-dollar companies, built by people who arrived on student visas and work permits, constitute an argument that no policy paper can match. Whether the United States continues to make that argument possible is, at this point, an open question."""

# Image: Pexels Silicon Valley / tech startup
print("\nSourcing hero image for Article 2...")
pexels_queries = [
    "Silicon Valley tech startup office",
    "startup founders technology meeting",
    "San Francisco skyline tech",
]
art2_img_url = None
art2_img_attr = "Pexels"
art2_img_caption = "Indian-born entrepreneurs have founded or co-founded 96 US unicorn startups, leading all countries by a wide margin"

for q in pexels_queries:
    pexels_url = fetch_pexels_image(q)
    if pexels_url:
        art2_img_url, art2_img_attr = source_and_upload_image(pexels_url, art2_slug, "Pexels")
        if art2_img_url:
            break

if not art2_img_url:
    print("  ✗ No hero image — will insert without image")
    art2_img_url = ""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian Immigrants Have Built 96 Billion-Dollar Startups in America. No Other Country Comes Close.",
    "subheadline": "A new NFAP study finds India is the largest source of immigrant unicorn founders in the US, with 96 companies collectively worth more than Germany's stock market.",
    "slug": art2_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian-born entrepreneurs account for 96 of America's 775 unicorns — the most of any country. Most arrived as IIT graduates on student visas, building the exact pipeline now threatened by tightening H-1B and student visa policies.",
    "tags": ["nri", "diaspora", "unicorns", "startups", "silicon-valley", "nfap", "h1b", "iit", "perplexity", "founders", "immigration", "tech"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Livemint / NFAP", "url": "https://www.livemint.com/news/india/indian-immigrants-built-96-unicorns-in-america-now-worth-more-than-germanys-stock-market-nfap-study-11749009143925.html"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/india-is-largest-source-for-immigrant-founders-of-us-unicorns-but-still-not-shooting-for-the-stars/article69621693.ece"},
        {"name": "DevDiscourse", "url": "https://www.devdiscourse.com/article/business/3401966-immigrant-entrepreneurs-ignite-us-innovation-amid-tightening-visa-policies"},
        {"name": "Swadesi / PTI", "url": "https://swadesi.com/us/india-born-entrepreneurs-found-96-us-unicorns/"}
    ]),
    "score_total": 79,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art2_img_url,
    "image_caption": art2_img_caption,
    "image_attribution": art2_img_attr,
    "body": art2_body.strip(),
}


# ── Insert into Supabase ─────────────────────────────────

print("\n" + "="*60)
print("INSERTING ARTICLES")
print("="*60)

for i, art in enumerate([art1, art2], 1):
    print(f"\n{'─'*40}")
    print(f"Article {i}: {art['headline'][:70]}...")
    print(f"  Slug: {art['slug']}")
    print(f"  Words: {len(art['body'].split())}")
    print(f"  Image: {'✓' if art['image_url'] else '✗ NONE'}")
    try:
        result = sb_post("p2_articles", art)
        print(f"  ✓ Inserted! ID: {art['id']}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "="*60)
print("DONE")
print("="*60)
