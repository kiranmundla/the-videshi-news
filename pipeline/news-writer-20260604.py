#!/usr/bin/env python3
"""
News Writer — June 4, 2026 run
Writes 3 news articles, sources images from Wikipedia/Wikimedia/Pexels,
uploads to Supabase storage, inserts articles.
"""

import json, os, sys, time, uuid, re, subprocess
import requests
from datetime import datetime, timezone
from io import BytesIO
from PIL import Image

# === ENV ===
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                k, v = line.split('=', 1)
                v = v.strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# === IMAGE HELPERS ===

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
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
    import urllib.parse
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
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
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(*queries):
    """Search Pexels for an image using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        return None
    for q in queries:
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={requests.utils.requote_uri(q)}&per_page=3&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    img = Image.open(BytesIO(img_bytes))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def download_image(url):
    """Download image bytes."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            ct = r.headers.get('Content-Type', '')
            if 'image' in ct or len(r.content) > 10000:
                return r.content
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None


def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase storage bucket 'article-images'."""
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    try:
        r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename} ({len(img_bytes)} bytes)")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def source_image(person_names=None, topic_queries=None, pexels_queries=None, slug="article"):
    """Multi-source image search, compare, pick best. Returns (url, attribution)."""
    candidates = []

    # Source 1: Wikipedia person images
    if person_names:
        for name in person_names:
            wiki_img = fetch_wikipedia_person_image(name)
            if wiki_img:
                candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": 3, "name": name})

    # Source 2: Wikimedia Commons
    if topic_queries:
        for q in topic_queries:
            commons = fetch_wikimedia_commons_images(q, limit=3)
            for c in commons[:2]:
                candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": 2, "name": q})

    # Source 3: Pexels
    if pexels_queries:
        pexels_img = fetch_pexels_image(*pexels_queries)
        if pexels_img:
            candidates.append({"url": pexels_img, "source": "pexels", "relevance": 1, "name": "pexels"})

    # Sort by relevance (highest first)
    candidates.sort(key=lambda x: x["relevance"], reverse=True)

    # Try to download, compress, upload the best candidate
    for cand in candidates:
        print(f"  Trying {cand['source']}: {cand['url'][:80]}...")
        raw = download_image(cand["url"])
        if raw:
            compressed = compress_image(raw)
            if len(compressed) > 5000:
                filename = f"{slug}.jpg"
                public_url = upload_to_supabase(compressed, filename)
                if public_url:
                    attr = "Wikimedia Commons" if cand["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
                    return public_url, attr

    print("  ✗ No suitable image found")
    return None, None


# === ARTICLE INSERTION ===

def insert_article(article):
    """Insert article into Supabase p2_articles."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# === ARTICLES ===

def write_articles():
    now = datetime.now(timezone.utc).isoformat()
    articles = []

    # ─── ARTICLE 1: EB-2 Visa Limit Exhausted for Indians ───
    print("\n=== Article 1: EB-2 Visa Limit Exhausted ===")

    slug1 = "us-eb2-visa-limit-exhausted-indians-fy2026-october-green-card-backlog"
    img1_url, img1_attr = source_image(
        topic_queries=["US visa immigration office", "US Citizenship and Immigration Services"],
        pexels_queries=["US immigration visa passport", "US embassy visa appointment"],
        slug=slug1
    )

    body1 = """The United States has officially exhausted its entire allocation of Employment-Based Second Preference (EB-2) immigrant visas for Indian nationals for Fiscal Year 2026, shutting down one of the most critical pathways to permanent residency for tens of thousands of highly skilled professionals already living and working in America.

The Department of State confirmed in a notice issued on May 22 that all available EB-2 visas allocated to applicants chargeable to India have been fully used, in coordination with US Citizenship and Immigration Services (USCIS). As a result, US embassies and consulates worldwide have been instructed not to issue additional EB-2 visas to Indian applicants for the remainder of the fiscal year. Processing will not resume until October 1, when FY 2027 begins and annual limits reset.

## Who Gets Hurt

The EB-2 category is the primary immigration channel for professionals holding advanced degrees or demonstrating exceptional ability — software engineers, data scientists, physicians, researchers, senior executives, and other specialists who form the backbone of America's knowledge economy. Under current law, the EB-2 allocation accounts for 28.6 percent of the worldwide employment-based immigration quota, while a per-country cap limits any single nation to no more than seven percent of total employment-based and family-sponsored visas combined.

For Indian nationals, who represent the single largest source country for employment-based immigration, this statutory cap has created a backlog stretching over a decade. The June 2026 Visa Bulletin shows the EB-2 India filing cut-off date sitting at July 15, 2014 — meaning applicants who filed twelve years ago are only now becoming eligible for final adjudication. USCIS has also announced it will use the more restrictive Final Action Dates chart for June, rather than the Dates for Filing chart, further tightening the pipeline.

## A Pattern That Repeats

This is not an anomaly. The EB-2 cap was exhausted for Indian applicants in FY 2024 (September 2024), FY 2025 (September 2025), and now FY 2026 — each year hitting the ceiling earlier. In FY 2026, the quota ran dry in May, the earliest exhaustion in recent memory. Immigration attorneys say the accelerating timeline reflects both rising demand from India's growing technology workforce and the structural inadequacy of a per-country cap system that treats India — with 1.4 billion people — the same as countries with populations a fraction of its size.

## What Applicants Can Do

For the estimated hundreds of thousands of Indian professionals caught in the backlog, the options are limited but not nonexistent. Applicants with approved I-140 petitions can continue to maintain their H-1B status and accrue time toward the six-year limit. Those eligible for a National Interest Waiver (NIW) under EB-2 may file independently without employer sponsorship, though the underlying backlog still applies. Some may explore EB-1 classification, which has a separate and typically more current priority date, though the qualifications are significantly more demanding.

The Biden-era executive actions that temporarily eased processing have not been renewed under the current administration, and legislative reform — including proposals to eliminate per-country caps entirely — remains stalled in Congress despite bipartisan support in previous sessions.

## The Diaspora Impact

For Indian families in the US, the EB-2 freeze is not an abstract policy matter. It determines whether a spouse can work, whether children age out of dependent status before a green card materialises, and whether a decade of building a life in America leads to permanence or forced departure. Advocacy groups including the Immigration Voice coalition have renewed calls for Congress to pass the EAGLE Act, which would phase out per-country caps over nine years, but the bill has not advanced in the current session.

The annual limits will reset on October 1, 2026, when FY 2027 begins. Until then, the pipeline is frozen — and the line just got longer.

*Sources: US Department of State, USCIS June 2026 Visa Bulletin, Berry Appleman & Leiden LLP, Manifest Law*"""

    articles.append({
        "headline": "The US Just Froze EB-2 Visas for Indians. The Backlog Now Stretches Back to 2014.",
        "subheadline": "All employment-based second-preference visas for Indian nationals have been exhausted for FY 2026. Processing will not resume until October.",
        "slug": slug1,
        "body": body1,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": now,
        "image_url": img1_url,
        "image_attribution": img1_attr,
        "is_editorial": False,
        "source": "videshi-news-writer",
        "sources": json.dumps(["US Department of State", "USCIS Visa Bulletin June 2026", "Berry Appleman & Leiden LLP", "Bharat Horizon"])
    })

    # ─── ARTICLE 2: New York State Senate India Independence Day Resolution ───
    print("\n=== Article 2: NY Senate India Independence Day Resolution ===")

    slug2 = "new-york-senate-resolution-india-independence-day-august-2026-jeremy-cooney"
    img2_url, img2_attr = source_image(
        person_names=["Jeremy Cooney"],
        topic_queries=["New York State Senate chamber", "New York State Capitol Albany"],
        pexels_queries=["New York State Capitol building Albany", "government senate legislative chamber"],
        slug=slug2
    )

    body2 = """The New York State Senate has adopted Resolution J1935, urging Governor Kathy Hochul to proclaim August 15, 2026, as India Independence Day in the State of New York — a formal legislative recognition that reflects the growing political weight of the Indian-American community in one of America's most influential states.

The resolution was sponsored by State Senator Jeremy Cooney, a Democrat from Rochester who made history in 2020 as the first Asian American elected to state office from upstate New York. Cooney, who was adopted from an orphanage in Kolkata and raised by a single mother in Rochester, has become one of the most prominent advocates for Indian-American interests in New York's legislature.

## What the Senators Said

During deliberations on the resolution, multiple senators offered remarks that went beyond pro-forma ceremony. Senator Joseph P. Addabbo Jr. quoted Mahatma Gandhi — "the future depends on what we do in the present" — calling the message an enduring inspiration for Indian Americans. Senator John C. Liu noted that India has been "a model of democracy for actually a lot longer than our country," and praised the Indian-American community's contributions across New York.

Senator Jeremy Zellner described the Indian-American community as "woven into the fabric of our everyday life" in his district. "They are our neighbours raising families here, working in critical professions, and helping shape the character of our region," he said.

Senator Toby Ann Stavisky called for continuing the "tradition of friendship" between India and the United States, noting that the similarities between the two democracies outweigh their differences.

## Why It Matters for the Diaspora

New York is home to one of the largest Indian-American populations in the Western Hemisphere, with particularly dense communities in Queens, Jersey City, and the wider metropolitan area. The resolution explicitly acknowledged the community's contributions to STEM, business, the arts, philanthropy, defence, and government at all levels — a legislative record that carries weight in future policy debates around immigration, trade, and cultural recognition.

The Consulate General of India in New York issued a statement expressing "sincere gratitude" to Senator Cooney and the full chamber, noting that the senators' remarks reflected the "deep people-to-people bonds" between the two nations and the "growing role of the Indian-American diaspora in strengthening communities across New York."

## A Growing Pattern of Recognition

The resolution follows a broader trend of American legislatures formally recognising Indian heritage. New York adopted a similar resolution commemorating the 75th anniversary of the Indian Constitution in November 2025, also sponsored by Cooney. Several other states, including New Jersey, Texas, and California, have adopted their own Indian Independence Day proclamations in recent years, reflecting the community's demographic growth and increasing civic engagement.

India will celebrate its 80th Independence Day on August 15, 2026. For the nearly 4.5 million Indian Americans across the country — and the estimated 700,000 in New York State alone — the Senate resolution is not just a symbolic gesture. It is a legislative acknowledgement that the community's presence has moved from the margins to the mainstream of American public life.

*Sources: New York State Senate Resolution J1935, The Indian EYE, hi INDiA, India Weekly*"""

    articles.append({
        "headline": "New York's Senate Just Voted to Recognise India's Independence Day. The Man Behind It Was Adopted From Kolkata.",
        "subheadline": "Resolution J1935 urges the governor to proclaim August 15, 2026, as India Independence Day across New York State. The sponsor, Jeremy Cooney, is the first Asian American elected to state office from upstate New York.",
        "slug": slug2,
        "body": body2,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": now,
        "image_url": img2_url,
        "image_attribution": img2_attr,
        "is_editorial": False,
        "source": "videshi-news-writer",
        "sources": json.dumps(["New York State Senate", "The Indian EYE", "hi INDiA", "India Weekly"])
    })

    # ─── ARTICLE 3: India's Consumer Watchdog Fines PhysicsWallah and McAfee for Dark Patterns ───
    print("\n=== Article 3: PhysicsWallah / McAfee Dark Patterns Fine ===")

    slug3 = "ccpa-fines-physicswallah-mcafee-dark-patterns-consumer-protection-india"
    img3_url, img3_attr = source_image(
        person_names=["Alakh Pandey"],
        topic_queries=["PhysicsWallah edtech India", "Central Consumer Protection Authority India"],
        pexels_queries=["consumer protection digital dark patterns", "online checkout manipulation interface"],
        slug=slug3
    )

    body3 = """India's consumer watchdog has imposed its most high-profile penalties yet under the country's dark patterns framework, fining edtech giant PhysicsWallah ₹5 lakh and cybersecurity firm McAfee Software India ₹1 lakh for deploying manipulative interface designs that steered users into purchases and subscriptions they did not explicitly choose.

The Central Consumer Protection Authority (CCPA), in orders issued on Wednesday by Chief Commissioner Nidhi Khare and Commissioner Anupam Mishra, directed both companies to immediately discontinue the identified practices and ensure consumers can make decisions "without manipulation or pressure."

## What PhysicsWallah Did

The CCPA took suo motu cognisance of practices on PhysicsWallah's platform and identified three distinct violations — all textbook examples of the design tricks that India's 2023 dark patterns guidelines were written to prevent.

The most striking finding involved a ₹10 donation to the PW Foundation that was automatically pre-selected during checkout and bundled into the final payment amount without explicit consumer consent. This practice — known as "basket sneaking" in regulatory parlance — meant users were paying for something they never chose.

When users attempted to remove the ₹10 charge, the platform displayed emotionally manipulative messages about children's education, healthcare, and marriages — a technique classified as "confirm shaming," designed to make consumers feel guilty about protecting their own wallets.

The regulator also flagged courses advertised as "free" that required users to hand over their mobile numbers and email addresses before access was granted. The CCPA noted that the course material was identical across accounts, meaning the personal data collection served no functional purpose for delivering the service.

The authority emphasised that a large proportion of PhysicsWallah's users are students, including minors, making the violations "particularly significant" from a consumer protection standpoint.

## What McAfee Did

McAfee's violations were simpler but no less calculated. The CCPA examined the company's subscription renewal interface and found it presented two options to users: "Renew Now" and "Accept Risk." The second option — the one that would let a consumer decline renewal — was framed as a dangerous choice, implying that users would be exposed to immediate cybersecurity threats if they did not continue paying.

The regulator identified four overlapping dark patterns in McAfee's interface: confirm shaming (making non-renewal feel irresponsible), interface interference (giving visual prominence to the renewal button), trick questions (using emotionally loaded language instead of neutral options), and forced action (not providing a clearly visible opt-out).

## Why the Fines Are Small but the Signal Is Loud

At ₹5 lakh and ₹1 lakh respectively, the penalties are trivially small for companies of this scale — PhysicsWallah was valued at over $1 billion at its last funding round, and McAfee is a global cybersecurity corporation. But regulatory observers say the real significance lies in the precedent.

These are among the first enforcement actions under the Guidelines for Prevention and Regulation of Dark Patterns, 2023 — a framework that India adopted ahead of most countries. The guidelines define 13 categories of dark patterns, from drip pricing and subscription traps to bait-and-switch and disguised advertising. The CCPA's willingness to act suo motu, without waiting for consumer complaints, signals that the regulator intends to be proactive rather than reactive.

For India's booming edtech, SaaS, and e-commerce sectors — where pre-ticked checkboxes, forced data collection, and guilt-tripping cancellation flows are standard practice — the message is clear: the 2023 rules have teeth, and the regulator is now using them.

## What It Means for NRIs

For Indian professionals working in technology abroad, the CCPA's enforcement is a notable development. India is building a consumer protection regime that in some areas now exceeds what exists in the US, where the Federal Trade Commission has pursued dark patterns cases but Congress has not enacted comprehensive legislation equivalent to India's 2023 guidelines. The approach offers a model that other countries, including those with large Indian diaspora populations, may follow.

*Sources: CCPA Order, Storyboard18, Livemint, Exchange4Media, BizzBuzz*"""

    articles.append({
        "headline": "India Just Fined PhysicsWallah for Sneaking a ₹10 Donation Into Every Checkout. McAfee Got Caught Too.",
        "subheadline": "The consumer watchdog penalised both companies for dark patterns — auto-added charges, guilt-tripping cancellation screens, and data harvesting disguised as free courses.",
        "slug": slug3,
        "body": body3,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": now,
        "image_url": img3_url,
        "image_attribution": img3_attr,
        "is_editorial": False,
        "source": "videshi-news-writer",
        "sources": json.dumps(["CCPA", "Storyboard18", "Livemint", "Exchange4Media", "BizzBuzz"])
    })

    # === INSERT ALL ===
    print("\n=== Inserting articles ===")
    for art in articles:
        # Remove None image fields
        if art["image_url"] is None:
            del art["image_url"]
        if art["image_attribution"] is None:
            del art["image_attribution"]
        insert_article(art)

    print(f"\n✓ Done. {len(articles)} articles processed.")


if __name__ == "__main__":
    write_articles()
