#!/usr/bin/env python3
"""
The Videshi News Writer — June 10, 2026 batch
Writes 3 articles: Zoho Nathu La server, FIFA World Cup DD Sports broadcast, India petrochemical import tax extension
"""

import json, os, re, sys, time, uuid
from datetime import datetime, timezone
import requests
from urllib.parse import quote

# ── Load env ──
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                key, _, val = line.partition('=')
                val = val.strip().strip('"').strip("'")
                os.environ.setdefault(key.strip(), val)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                if url and ii.get("mime", "").startswith("image/"):
                    width = ii.get("thumbwidth") or ii.get("width", 0)
                    height = ii.get("thumbheight") or ii.get("height", 0)
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": width,
                        "height": height
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for a stock image. Uses curl to avoid 403."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={quote(query)}&per_page=5&orientation=landscape'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        for photo in photos:
            url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
            if url:
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def validate_image(url):
    """Validate that an image URL returns HTTP 200 with image content-type and sufficient size."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get('content-type', '')
        cl = int(r.headers.get('content-length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Try GET if HEAD doesn't have content-length
        if r.status_code == 200 and 'image' in ct and cl == 0:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: >5000 bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def insert_article(article):
    """Insert article into Supabase p2_articles table."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Inserted: {result[0].get('headline', 'unknown')}")
            return result[0]
        print(f"  ✓ Inserted (no return data)")
        return result
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ══════════════════════════════════════════════════
# ARTICLE 1: Zoho's Nathu La Server
# ══════════════════════════════════════════════════
def write_zoho_article():
    print("\n═══ Article 1: Zoho Nathu La Server ═══")

    # Image sourcing — try Sridhar Vembu first (founder), then Shailesh Davey (CEO)
    print("Sourcing image...")
    img_url = fetch_wikipedia_person_image("Sridhar Vembu")
    img_caption = "Sridhar Vembu, founder of Zoho Corporation"
    img_attr = "Wikimedia Commons"

    if not img_url or not validate_image(img_url):
        # Try Zoho Corporation page
        commons_results = fetch_wikimedia_commons_images("Zoho Corporation office", limit=5)
        for r in commons_results:
            if validate_image(r["url"]):
                img_url = r["url"]
                img_caption = "Zoho Corporation headquarters"
                img_attr = "Wikimedia Commons"
                break
        else:
            # Fallback to Pexels for server/data center
            img_url = fetch_pexels_image("server data center technology")
            img_caption = "A modern data center server rack"
            img_attr = "Pexels"
            if img_url and not validate_image(img_url):
                img_url = None

    if not img_url:
        print("  ✗ No valid image found, skipping article")
        return None

    body = """Zoho Corporation has unveiled Nathu La, a server designed and engineered entirely in India — a move that makes the Chennai-headquartered company one of the few technology firms in the world to own its full technology stack from hardware to software.

The server, named after the Himalayan mountain pass connecting Sikkim to Tibet, was developed over five years by a team based in Nagpur, a city not typically associated with cutting-edge hardware R&D. Roughly 90 per cent of that team were hired as freshers, recruited through Zoho's SETU programme — Student's Engagement for Transformative Upskilling — which trains engineers from colleges across Central India.

"We are proud to build a server system that is truly designed in India and taking a step towards creating sovereign technology," said Shailesh Davey, CEO of Zoho Corporation. "Through focused investments in R&D and skill development, this foray into hardware enables us not only to build and own the technology, but also to cultivate the expertise and talent behind it."

## What Nathu La Actually Does

Built on Intel Xeon 6 processors and designed around the Open Compute Project's principles of modularity and thermal efficiency, Nathu La delivers performance equivalent to global OEM servers while consuming 12–18 per cent less power and cutting total cost of ownership by 20–30 per cent. Zoho has already deployed 1,000 units across its Indian data centres and plans to scale to 2,000 by year's end.

The server is optimised for virtualisation, high-performance computing, AI inference, and storage — workloads that have become dramatically more expensive in recent months. Ramprakash Ramamoorthy, Zoho's Director of AI, noted that server costs for services like Zoho Mail and Zoho Meeting have risen fourfold in the past six months alone, driven by the global AI hardware frenzy.

"For the first time in two years, the whole 'ROI on AI' conversation is getting louder," Ramamoorthy said.

## Why It Matters for the Indian Tech Ecosystem

India's digital infrastructure is expanding at an unprecedented pace, yet the server technology underpinning it has historically been sourced from abroad. Indian enterprises have paid royalties and licensing fees to foreign entities for decades. Nathu La's intellectual property is entirely owned in India — metal sheets manufactured in Pune, chassis bent and assembled in Nagpur, PCB assembly in Chennai, testing in Bangalore.

The timing is significant. In 2023, the Indian government imposed import restrictions on compute devices including servers, signalling a broader push toward technological self-reliance. Zoho's announcement lands as electronic imports, especially servers, continue rising amid growing AI and digital workloads.

## The Diaspora Angle

For Indian-origin engineers working at global tech firms, Zoho's approach represents an alternative model of innovation — one that prioritises problem-driven R&D over capital-intensive moonshots. The company does not plan to commercialise Nathu La externally, but its success could inspire a broader ecosystem of indigenous hardware development.

Zoho operates 20 data centres worldwide and employs over 15,000 people globally. Its suite of business software competes directly with offerings from Microsoft, Google, and Salesforce — and now, its infrastructure does too."""

    article = {
        "headline": "Zoho Just Built Its Own Server From Scratch. In Nagpur.",
        "subheadline": "The Chennai-based tech company's Nathu La server — designed by a team of freshers in Central India — cuts costs by 30% and marks a rare claim to technological sovereignty.",
        "body": body.strip(),
        "slug": "zoho-nathu-la-server-designed-india-nagpur-tech-sovereignty-20260610",
        "category": "news",
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "sources": json.dumps(["The Hindu BusinessLine", "Business Wire", "CXOToday"]),
        "status": "review",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ══════════════════════════════════════════════════
# ARTICLE 2: FIFA World Cup on DD Sports
# ══════════════════════════════════════════════════
def write_fifa_ddsports_article():
    print("\n═══ Article 2: FIFA World Cup DD Sports ═══")

    # Image sourcing — Wikimedia Commons for FIFA World Cup 2026
    print("Sourcing image...")
    img_url = None
    img_caption = ""
    img_attr = ""

    commons_results = fetch_wikimedia_commons_images("FIFA World Cup 2026 trophy", limit=5)
    for r in commons_results:
        if validate_image(r["url"]):
            img_url = r["url"]
            img_caption = "The FIFA World Cup trophy"
            img_attr = "Wikimedia Commons"
            break

    if not img_url:
        commons_results = fetch_wikimedia_commons_images("FIFA World Cup trophy", limit=5)
        for r in commons_results:
            if validate_image(r["url"]):
                img_url = r["url"]
                img_caption = "The FIFA World Cup trophy"
                img_attr = "Wikimedia Commons"
                break

    if not img_url:
        img_url = fetch_pexels_image("football stadium world cup soccer")
        img_caption = "Football fans at a major international tournament"
        img_attr = "Pexels"
        if img_url and not validate_image(img_url):
            img_url = None

    if not img_url:
        print("  ✗ No valid image found, skipping article")
        return None

    body = """The Indian government has amended its sports broadcasting regulations to bring key FIFA World Cup 2026 matches to Doordarshan's free-to-air platform — a last-minute intervention that guarantees hundreds of millions of viewers access to football's biggest tournament without a subscription.

Under the revised mandatory sharing framework, DD Sports 1.0 will broadcast the opening match between Mexico and South Africa, all quarter-finals, both semi-finals, and the final. The matches will be available on DD Free Dish, India's government-run direct-to-home platform that reaches approximately 45 million households, predominantly in rural and semi-urban areas.

## A Deal That Nearly Didn't Happen

The broadcast arrangement arrives after weeks of uncertainty. FIFA had struggled to finalise deals in both India and China — two of the world's most populous nations — with just days to go before the tournament kicks off on June 12. Out of 180-plus territories worldwide, India and China were among the last holdouts.

Zee Entertainment's Z network eventually secured the primary broadcast rights for India, covering all matches through Unite8 Sports on television and Zee5 for streaming, as part of a wider deal extending through 2034. The Doordarshan arrangement supplements this by ensuring the biggest matches reach viewers who lack cable or streaming access.

The move is a significant departure from the 2022 World Cup cycle, when Viacom18 handled coverage through Sports18 and JioCinema. Indian football fans accustomed to those platforms will need to adjust.

## Why This Matters for NRIs

For the Indian diaspora, the broadcast details carry practical weight. NRIs in North America will follow the tournament across three host nations — the United States, Canada, and Mexico — with 48 teams competing in the largest-ever World Cup field. Several matches will take place in cities with large Indian-American populations: the San Francisco Bay Area (Santa Clara), New York-New Jersey (East Rutherford), and Los Angeles (Inglewood).

The tournament opens on June 12 with Mexico vs South Africa in Mexico City, followed by Switzerland vs Qatar at the San Francisco Bay Area Stadium in Santa Clara on June 13, and Morocco vs Brazil at the New York New Jersey Stadium the same day.

While India did not qualify for the tournament, the country's rapidly growing football fanbase — particularly among younger urban demographics — has made World Cup broadcast rights increasingly valuable. The Premier League's popularity in India has tripled viewership for international football over the past decade.

## The DD Free Dish Factor

The government's mandatory sharing framework exists precisely for moments like this. Designed to ensure that sporting events of national importance reach the widest possible audience, the framework allows Prasar Bharati to carry key matches alongside the primary rights holder.

DD Sports confirmed the arrangement on social media, describing the tournament as "football's biggest festival." The decision is particularly significant given DD Free Dish's penetration in rural India, where cable and internet access remain limited.

For Indian football fans — whether in Chennai or Chicago — the path to watching the 2026 World Cup is now clear. The question of how India's national team might one day make it to the tournament itself remains, as always, a longer conversation."""

    article = {
        "headline": "India Will Show the FIFA World Cup for Free. Here's How to Watch.",
        "subheadline": "DD Sports will broadcast the opening match and all knockout games from the quarter-finals on free-to-air television, after a last-minute deal nearly left 1.4 billion people without access.",
        "body": body.strip(),
        "slug": "fifa-world-cup-2026-dd-sports-free-broadcast-india-zee-unite8-20260610",
        "category": "news",
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "sources": json.dumps(["KhelNow", "Sporting News", "BestMediaInfo", "Nonce Media"]),
        "status": "review",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ══════════════════════════════════════════════════
# ARTICLE 3: India Petrochemical Import Tax Extension
# ══════════════════════════════════════════════════
def write_petrochemical_article():
    print("\n═══ Article 3: India Petrochemical Import Tax Extension ═══")

    # Image sourcing
    print("Sourcing image...")
    img_url = None
    img_caption = ""
    img_attr = ""

    commons_results = fetch_wikimedia_commons_images("Indian pharmaceutical factory", limit=5)
    for r in commons_results:
        if validate_image(r["url"]):
            img_url = r["url"]
            img_caption = "An Indian pharmaceutical manufacturing facility"
            img_attr = "Wikimedia Commons"
            break

    if not img_url:
        commons_results = fetch_wikimedia_commons_images("petrochemical plant India refinery", limit=5)
        for r in commons_results:
            if validate_image(r["url"]):
                img_url = r["url"]
                img_caption = "A petrochemical refinery in India"
                img_attr = "Wikimedia Commons"
                break

    if not img_url:
        img_url = fetch_pexels_image("pharmaceutical manufacturing factory")
        img_caption = "A pharmaceutical manufacturing facility"
        img_attr = "Pexels"
        if img_url and not validate_image(img_url):
            img_url = None

    if not img_url:
        print("  ✗ No valid image found, skipping article")
        return None

    body = """India is considering extending emergency import tax exemptions on 40 petrochemical products beyond their June 30 expiration, as the Iran war continues to choke the global supply of raw materials used to make plastics, packaging, and pharmaceutical drugs.

The exemptions, first imposed in April after the U.S.-Israeli strikes on Iran disrupted petrochemical supply chains, suspended import duties on derivatives essential for industries ranging from generic drug manufacturing to food packaging. Ravi Teja, deputy director at the Department of Commerce, told Reuters that the Ministry of Commerce is "monitoring the situation" and will make a final decision based on the evolving geopolitical picture.

"They are monitoring the situation. The final decision on extension will be taken only after assessing the geopolitical situation and if the ministry feels it is necessary," Teja said.

## The Supply Chain Under Pressure

India is a net importer of petrochemical derivatives, even though it produces some domestically using feedstocks such as liquefied petroleum gas, naphtha, and ethane. When the Iran war began in late February, it disrupted a critical node in the global petrochemical supply chain. Iran is a major producer of methanol and other base chemicals that feed into downstream industries worldwide.

The immediate government response was aggressive. Within days of the U.S.-Israeli strikes, India ordered companies to divert locally produced petrochemical components toward LPG production — prioritising cooking gas for 800 million people receiving subsidised rations. That diversion, while necessary, deepened the shortage of raw materials for pharmaceutical and plastics manufacturers.

The 40 products covered by the exemption include ethylene glycol, purified terephthalic acid, and various polymer precursors — materials that sound obscure but underpin everyday consumer goods and life-saving medications.

## What This Means for India's Pharma Industry

India manufactures approximately 20 per cent of the world's generic drugs by volume. Many of those generics rely on petrochemical-derived active pharmaceutical ingredients and excipients. When raw material costs spike, the ripple effects travel quickly: production costs rise, margins compress, and eventually prices increase for consumers — including in the United States, where Indian-made generics account for nearly 40 per cent of the market.

This is not a hypothetical scenario. Benchmark international oil prices have remained roughly 30 per cent above pre-war levels, while gas prices have surged 75 per cent. The Reserve Bank of India now projects inflation averaging 5.1 per cent for the current fiscal year, up from 3.48 per cent in April.

## The NRI Connection

For the Indian diaspora, particularly in the United States, the stakes are direct. Generic drugs from Indian manufacturers supply pharmacy shelves from CVS to Costco. A sustained disruption to India's petrochemical supply could translate into prescription drug shortages and price increases that hit American wallets.

The broader economic picture is equally concerning. India's oil-and-gas import bill jumped 53 per cent in April alone. HSBC projects the balance of payments deficit could swell to $65 billion in 2026-27 without intervention. The government's emergency measures — curbing gold imports, discouraging foreign travel, promoting public transport — suggest policymakers are bracing for a prolonged disruption.

Whether the import tax exemption extension goes through will depend on how the Iran situation evolves over the next three weeks. But for an economy that supplies generic medicines to half the world, the decision carries weight far beyond India's borders."""

    article = {
        "headline": "India May Extend Emergency Tax Breaks on 40 Chemicals. Your Prescription Drugs Depend on It.",
        "subheadline": "The Iran war disrupted the petrochemical supply chain that feeds India's generic drug factories. The import duty waiver expires June 30 — and the government is still deciding.",
        "body": body.strip(),
        "slug": "india-petrochemical-import-tax-exemption-extension-pharma-iran-war-20260610",
        "category": "news",
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "sources": json.dumps(["Reuters", "Reserve Bank of India", "HSBC Research"]),
        "status": "review",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ══════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"═══ The Videshi News Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} ═══")

    results = []
    for writer_fn in [write_zoho_article, write_fifa_ddsports_article, write_petrochemical_article]:
        try:
            result = writer_fn()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            results.append(None)

    success = sum(1 for r in results if r is not None)
    print(f"\n═══ Done: {success}/{len(results)} articles inserted ═══")
