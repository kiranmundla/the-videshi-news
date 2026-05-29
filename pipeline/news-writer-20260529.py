#!/usr/bin/env python3
"""News writer for The Videshi — May 29, 2026 evening batch."""

import json, os, sys, uuid, re, urllib.parse
from datetime import datetime, timezone

import requests

# ── Load credentials ────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k, v)

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Wikipedia image helper ──────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
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

# ── Pexels image helper ─────────────────────────────────────────────
def fetch_pexels_image(query, fallback_query=None):
    """Search Pexels for a relevant image using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

# ── Image validation ────────────────────────────────────────────────
def validate_image_url(url):
    """Check URL returns a real image (HTTP 200, image/*, >5KB)."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD didn't return Content-Length
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False

# ── Upload to Supabase storage ──────────────────────────────────────
def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase article-images bucket."""
    try:
        r = requests.get(image_url, timeout=15,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed: status={r.status_code}, size={len(r.content)}")
            return None
        
        ct = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": ct,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

# ── Publish article ─────────────────────────────────────────────────
def publish_article(article):
    """Insert article into p2_articles."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    payload = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": article["category"],
        "status": "published",
        "published_at": now,
        "sources": json.dumps(article["sources"]),
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution", ""),
    }
    
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=15,
    )
    if r.status_code in (200, 201):
        result = r.json()
        returned_id = result[0]["id"] if isinstance(result, list) and result else art_id
        print(f"  ✓ Published: {article['headline'][:60]}... (id={returned_id})")
        return returned_id
    else:
        print(f"  ✗ FAILED to publish: {r.status_code} {r.text[:300]}")
        return None


# ══════════════════════════════════════════════════════════════════════
# ARTICLE 1: Intel $3.3B semiconductor plant in Odisha
# ══════════════════════════════════════════════════════════════════════

article1 = {
    "headline": "Intel Just Signed a $3.3 Billion Deal to Build a Semiconductor Plant in Odisha. This Is Not a Promise. It Is an MoU.",
    "subheadline": "The facility will make glass-core substrates for AI and 5G chips. It is the biggest single-site semiconductor investment India has ever landed.",
    "slug": "intel-3dgs-3-3-billion-semiconductor-substrate-plant-odisha-20260529",
    "category": "news",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com/technology/intel-3dgs-set-up-33-billion-substrate-plant-indias-odisha-state-2026-05-29/"},
        {"name": "The Tech Portal", "url": "https://thetechportal.com/2026/05/29/intel-set-up-3-3bn-substrate-manufacturing-plant-india/"},
        {"name": "TechGolly", "url": "https://techgolly.com/intel-india-semiconductor-expansion/"},
    ],
    "body": """On Friday morning, the government of Odisha signed a Memorandum of Understanding with Intel Corporation and 3D Glass Solutions, a U.S.-based advanced packaging company, to build a $3.3 billion semiconductor substrate manufacturing facility in the Bhubaneswar-Khurda region.

The announcement, confirmed by India's IT Minister Ashwini Vaishnaw on social media, marks one of the largest foreign direct investments in India's semiconductor history. It is also the clearest signal yet that Intel — which has spent years circling India without committing to a major manufacturing presence — is ready to put real money on the ground.

## What Will the Plant Actually Make?

Not chips. Not the transistor-etched silicon wafers that TSMC and Samsung produce. The Odisha facility will manufacture **advanced packaging glass-core substrates** — the foundational material on which semiconductor components are mounted, connected, and packaged into finished products.

Glass substrates are emerging as a critical upgrade over traditional organic substrates. They offer better thermal stability, tighter interconnect density, and more reliable signal transmission — all of which matter enormously for AI accelerators, 5G/6G telecommunications equipment, defense electronics, and high-performance computing systems.

Intel will act as the technology partner, providing process expertise, technology licensing, quality systems, and workforce training. 3DGS, a specialist in glass-based semiconductor packaging, will co-develop the facility. The plant will be located within Odisha's Info Valley industrial park and will be built in phases over five to six years.

## The Jobs and the Ecosystem

The project is expected to generate more than 1,800 direct high-skilled jobs, plus thousands of indirect positions across electronics manufacturing, logistics, chemicals, precision engineering, and semiconductor supply chains.

For Odisha, a state that has traditionally been associated with mining and steel rather than high technology, the deal represents a potentially transformative pivot. Chief Minister Mohan Charan Majhi presided over the MoU signing and has been aggressively courting semiconductor investments as part of his administration's industrial strategy.

## Where This Fits in India's Chip Ambitions

India has pledged tens of billions of dollars in subsidies to attract semiconductor manufacturing under Prime Minister Narendra Modi's push for domestic production. The Tata Group is already building India's first fabrication facility in Gujarat with Taiwan's Powerchip, and a separate assembly and testing plant in Assam.

But substrate manufacturing is a different link in the chain — one that has been almost entirely dominated by Japanese, South Korean, and Taiwanese firms. Landing Intel's involvement in this segment gives India a presence in the advanced packaging layer, which is increasingly important as chipmakers push beyond Moore's Law limitations by stacking and interconnecting chips in novel ways.

## Why It Matters for the Diaspora

The semiconductor industry employs tens of thousands of Indian engineers in the United States, many of them at Intel, AMD, Nvidia, Qualcomm, and Broadcom. A major Intel-backed facility in India could create a reverse talent pipeline — offering experienced diaspora engineers a reason to return, consult, or lead operations closer to home.

For NRIs in tech, the Odisha announcement is also a signal about the trajectory of India's industrial strategy. The country is no longer just chasing chip fabrication as a nationalist prestige project. It is building out the supply chain piece by piece — packaging, substrates, testing, assembly — in a way that could eventually make India a credible alternative in a global semiconductor ecosystem that remains dangerously concentrated in Taiwan.

## The Reality Check

An MoU is not a factory. India has seen semiconductor announcements collapse before — most notably the Foxconn-Vedanta partnership that fell apart in 2023 after months of uncertainty. Implementation timelines, land acquisition, environmental clearances, water supply, and power infrastructure all remain variables that can derail even well-funded projects.

The five-to-six-year timeline also means the plant will not contribute to India's industrial output until the early 2030s, by which time the global semiconductor landscape could look very different.

But the Intel brand carries a weight that previous Indian semiconductor ventures lacked. If this plant moves from MoU to groundbreaking on schedule, it will be the most consequential single investment in India's chip ecosystem to date.""",
}

# ══════════════════════════════════════════════════════════════════════
# ARTICLE 2: Rupee surges to best day in 2 months
# ══════════════════════════════════════════════════════════════════════

article2 = {
    "headline": "The Rupee Just Had Its Best Day in Two Months. The Reason: Oil Fell and the RBI Stepped In.",
    "subheadline": "India's currency jumped 0.7 percent to 95 per dollar as Iran deal hopes collided with central bank intervention. But $24 billion has already left since March.",
    "slug": "rupee-best-day-two-months-rbi-intervention-oil-iran-deal-20260529",
    "category": "news",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com/markets/currencies/rupee-soars-best-day-nearly-two-months-central-bank-steps-oil-drops-2026-05-29/"},
        {"name": "Reuters", "url": "https://www.reuters.com/markets/rates-bonds/rbi-hold-rates-june-majority-now-expect-hike-by-year-end-2026-05-29/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/energy/oil-prices-fall-market-awaits-possible-us-iran-ceasefire-deal-2026-05-29/"},
    ],
    "body": """The Indian rupee surged 0.7 percent on Friday, its sharpest single-day gain since early April, as two forces converged at once: the Reserve Bank of India likely sold dollars into the market, and crude oil prices plunged on reports that the United States and Iran were close to extending their ceasefire for another 60 days.

The rupee closed at 95 per dollar, briefly breaking below that level during the session. It had been trading weaker earlier in the day before what multiple traders described as central bank intervention reversed the trajectory.

## Why Oil Is the Rupee's Puppet Master

India is the world's third-largest oil importer. Every dollar move in Brent crude translates directly into India's import bill, its current account deficit, and ultimately its currency. Since the U.S.-Israeli war with Iran began on February 28, oil has traded in a volatile band between $87 and $114 a barrel, with most of that time spent well above pre-war levels.

On Friday, Brent crude dropped more than 2 percent to around $92 a barrel, on track for its steepest weekly decline in seven weeks. Reports emerged that U.S. and Iranian negotiators had reached a framework to extend the ceasefire for 60 days and begin reopening the Strait of Hormuz to shipping — though President Donald Trump had yet to give final approval.

The rupee rallied in tandem. But the relief may be temporary. Even under the most optimistic deal scenario, analysts at Société Générale estimate it could take two months from a notional reopening date before oil actually begins flowing at pre-war volumes. Mines must be cleared, insurers reassured, and tankers repositioned.

## The $24 Billion Exodus

The single-day gain barely dents a much larger wound. Since the Iran war began in late February, overseas investors have pulled more than $24 billion from Indian debt and equities on a net basis. The outflows reflect a combination of rising global risk aversion, higher U.S. yields, and the direct economic threat to India from elevated oil prices.

For NRIs with investments in Indian markets, the capital flight has been particularly painful. The Sensex has lost ground steadily, the rupee has weakened more than 5 percent year-to-date, and the foreign investor exodus has drained liquidity from precisely the mid-cap and growth segments where diaspora portfolios tend to be concentrated.

## What Comes Next: The RBI Decision on June 5

All eyes now turn to the Reserve Bank of India's monetary policy decision on June 5. A Reuters poll of 56 economists found that nearly 80 percent expect the RBI to hold its repo rate steady at 5.25 percent — but a significant and growing minority now forecast at least one rate hike before the end of 2026.

India's headline inflation remains relatively benign at 3.48 percent in April, well below the RBI's 4 percent target. But wholesale inflation has accelerated sharply, and with crude prices still roughly 30 percent above pre-war levels, the pass-through to consumer prices is a question of when, not if.

Capital Economics forecasts the RBI could raise the repo rate to 6.00 percent before year-end — but only if the Iran crisis is resolved and energy prices fall back. If it isn't, the central bank faces an impossible trilemma: defend the currency, support growth, or fight inflation. It cannot do all three.

## What NRIs Should Watch

For the Indian diaspora, three numbers now matter more than any headline:

**The rupee at 95.** If it weakens past 97-98, remittances become more attractive but Indian asset values erode further in dollar terms. NRIs considering real estate purchases or equity investments in India are effectively betting on the currency stabilizing before deploying capital.

**Brent at $92.** Every sustained $10 drop in oil prices gives the RBI room to hold rates and allows the government to avoid politically painful fuel price hikes. Every $10 rise does the opposite.

**The June 5 RBI decision.** A hold signals confidence that the Iran crisis will pass. A hike signals the central bank has decided the oil shock is not transitory — and that NRI deposit rates, bond yields, and mortgage costs in India are all headed higher.

Friday's rupee rally was a reprieve, not a resolution. The Iran deal is not signed. The oil is not flowing. And $24 billion of foreign capital is already gone.""",
}

# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def source_and_publish(article, person_names=None, pexels_query=None, pexels_fallback=None):
    """Source image, validate, upload, and publish."""
    print(f"\n{'='*60}")
    print(f"Processing: {article['headline'][:70]}...")
    print(f"{'='*60}")
    
    img_url = None
    attribution = ""
    
    # Try Wikipedia for named persons
    if person_names:
        for name in person_names:
            img_url = fetch_wikipedia_person_image(name)
            if img_url:
                attribution = "Wikimedia Commons"
                break
    
    # Try Pexels fallback
    if not img_url and pexels_query:
        img_url = fetch_pexels_image(pexels_query, pexels_fallback)
        if img_url:
            attribution = "Pexels"
    
    # Validate
    if img_url and validate_image_url(img_url):
        # Upload to Supabase storage
        ext = "jpg"
        filename = f"{article['slug']}.{ext}"
        uploaded_url = upload_image_to_supabase(img_url, filename)
        if uploaded_url:
            article["image_url"] = uploaded_url
            article["image_attribution"] = "The Videshi"
        else:
            # Use direct URL only if from permanent source
            if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                article["image_url"] = img_url
                article["image_attribution"] = attribution
            else:
                article["image_url"] = None
    else:
        print("  ⚠ No valid image found — publishing without image")
        article["image_url"] = None
    
    # Publish
    art_id = publish_article(article)
    
    # If published and image uploaded, update with image
    if art_id and article.get("image_url"):
        print(f"  ✓ Article published with image")
    elif art_id:
        print(f"  ✓ Article published without image")
    
    return art_id


if __name__ == "__main__":
    results = []
    
    # Article 1: Intel semiconductor plant
    r1 = source_and_publish(
        article1,
        person_names=["Intel"],
        pexels_query="semiconductor chip manufacturing",
        pexels_fallback="microchip circuit board",
    )
    results.append(("Intel semiconductor", r1))
    
    # Article 2: Rupee rally
    r2 = source_and_publish(
        article2,
        person_names=["Indian rupee"],
        pexels_query="Indian currency rupee banknotes",
        pexels_fallback="stock market trading screen",
    )
    results.append(("Rupee rally", r2))
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, rid in results:
        status = "✓ PUBLISHED" if rid else "✗ FAILED"
        print(f"  {status}: {name}")
    
    # Exit with error if any failed
    if any(r is None for _, r in results):
        sys.exit(1)
