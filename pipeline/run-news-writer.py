#!/usr/bin/env python3
"""News writer for The Videshi — generates and publishes news articles."""

import json
import os
import sys
import uuid
import re
from datetime import datetime, timezone
import subprocess

# Load env
env_file = os.path.expanduser("~/.env.supabase")
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

import requests
import urllib.parse

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
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

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            # Use curl because Python urllib gets 403 from Pexels
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage. Returns public URL."""
    try:
        # Try with User-Agent, then retry with different headers
        for ua in ["TheVideshi/1.0 (thevideshi.com)", "Mozilla/5.0 (compatible; TheVideshi/1.0)"]:
            r = requests.get(image_url, headers={"User-Agent": ua}, timeout=15)
            if r.status_code == 200:
                break
            if r.status_code == 429:
                print(f"  ⚠ Rate limited, trying alternate UA...")
                import time
                time.sleep(2)
                continue
        
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            # For Wikipedia/Pexels, return direct URL as fallback
            if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
                return image_url
            return None
        
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if "image" not in content_type:
            print(f"  ⚠ Not an image: {content_type}")
            return image_url
        
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return image_url
        
        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true"
            },
            data=r.content,
            timeout=30
        )
        
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
            # Fall back to direct URL if it's from Wikipedia/Pexels
            if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
                return image_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
            return image_url
        return None

def sb_insert(table, data):
    """Insert a row into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(
        url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        },
        json=data,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

def check_image_skip_list(article_id):
    """Check if article is in the image skip list."""
    skip_file = os.path.expanduser("~/workspace/the-videshi-news/pipeline/image-skip-list.json")
    if os.path.exists(skip_file):
        with open(skip_file) as f:
            skip_list = json.load(f)
            return article_id in skip_list
    return False

def validate_image_url(url):
    """Validate image URL is not from banned sources."""
    if not url:
        return False
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "scontent-"]
    banned_params = ["_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ BANNED source detected: {b}")
            return False
    for p in banned_params:
        if p in url:
            print(f"  ✗ BANNED param detected: {p}")
            return False
    return True

# ============================================================
# ARTICLES
# ============================================================

articles = []

# ---------- ARTICLE 1: India-Oman CEPA ----------
articles.append({
    "headline": "India's New Trade Deal With Oman Just Went Live. It May Be the Country's Most Important FTA This Decade.",
    "subheadline": "The CEPA gives 99% of Indian exports duty-free access and secures $7.2 billion in energy imports — right as the Strait of Hormuz remains under threat.",
    "slug": "india-oman-cepa-fta-energy-security-hormuz-bypass-duty-free-exports-20260602",
    "category": "news",
    "sources_json": ["Reuters", "The Hindu BusinessLine", "Devdiscourse", "GTRI"],
    "image_search_person": None,
    "vertical": "economy",
    "image_search_pexels": "Oman port shipping cargo",
    "image_search_pexels_fallback": "oil tanker shipping sea",
    "body": """India's free trade agreement with Oman officially came into force on June 1 — and its timing could not be more consequential.

The Comprehensive Economic Partnership Agreement, signed in Muscat in December 2025 in the presence of Prime Minister Narendra Modi and Sultan Haitham bin Tarik Al Said, gives duty-free access to 99.38 per cent of India's exports by value. That covers 98 per cent of Oman's tariff lines — up from just 15 per cent under the previous Most Favoured Nation regime.

## Why This Deal Matters Now

The agreement would have been significant in peacetime. During the Iran war, it becomes strategic.

Oman sits just outside the Strait of Hormuz — the 33-kilometre-wide chokepoint between Iran and the Arabian Peninsula through which roughly 20 per cent of the world's oil and a third of its seaborne liquefied natural gas once flowed. Since Iran's Revolutionary Guards began restricting passage in March, that corridor has been effectively shut to commercial traffic.

Oman's ports at Duqm and Sohar, however, face the Gulf of Oman and the Arabian Sea — bypassing the Strait entirely. That geographic advantage makes Oman a critical alternate trade route for India at precisely the moment its traditional Gulf shipping lanes are disrupted.

"The agreement deepens India's energy security by ensuring access to Omani crude oil, LNG, fertilisers, methanol and ammonia, worth over $7.2 billion in imports in FY2026," said Ajay Srivastava, founder of the Global Trade Research Initiative.

## What India Gets

India imported $7.2 billion worth of goods from Oman in fiscal 2026. Crude oil accounted for $1.6 billion, LNG for $1.2 billion, and fertilisers for $843 million. These three categories alone make up 38 per cent of all imports from the Gulf country.

Under the CEPA, Oman has also offered to increase supply of petrochemicals and fertilisers to India. Pankaj Khimji, Oman's foreign trade advisor, said the country would consider diverting its share of production from the Oman India Fertiliser Project — a joint venture between IFFCO, KRIBHCO and the Oman Investment Authority — to India if needed.

Indian consumers will also see cheaper Omani dates, which will enjoy quota-based duty concessions under the agreement.

## The Diaspora Angle

For the estimated 800,000 Indians living and working in Oman, the deal brings tangible benefits. Indian firms investing in Oman can now hire Indian workers above and beyond the local employment quotas mandated by Oman's government. Indian pharmaceuticals approved by the US, European or UK regulators will also get faster regulatory clearance in Oman.

Commerce Minister Piyush Goyal called Oman "a bridge for our people and a gateway to the Gulf and East Africa."

## Bilateral Trade Is Growing

Bilateral trade between India and Oman reached $11.18 billion in FY2025-26, up from $10.61 billion the previous year. Oman is now India's second-largest trading partner in the Gulf region.

This is India's fifth FTA implemented in the last five years and its 15th overall. The first consignments under the new preferential tariff — including agriculture and gems and jewellery exports from Mumbai, Kolkata and Chennai — were flagged off on June 1.

## What's Next

The CEPA is the second such agreement India has signed with a Gulf Cooperation Council country, after the UAE deal in 2022. Negotiations for a broader India-GCC FTA remain ongoing, but the Oman deal gives India an immediate hedge against the energy and trade disruptions that have defined the first half of 2026."""
})

# ---------- ARTICLE 2: India drops to 7th in market cap ----------
articles.append({
    "headline": "India Just Dropped to Seventh in Global Market Cap Rankings. South Korea's AI Chip Boom Is the Reason.",
    "subheadline": "In 18 months, India went from a market cap three-and-a-half times South Korea's to being overtaken. Foreign investors have pulled $26.4 billion this year.",
    "slug": "india-seventh-global-market-cap-south-korea-overtakes-ai-chips-fpi-outflow-20260602",
    "category": "news",
    "sources_json": ["Reuters", "Bernstein", "Carmignac", "Equirus Securities"],
    "image_search_person": None,
    "vertical": "economy",
    "image_search_pexels": "stock market trading screen India",
    "image_search_pexels_fallback": "stock exchange financial charts",
    "body": """India's equity markets slipped to seventh place globally in total market capitalisation on Tuesday — overtaken by South Korea's chip-heavy stock market, which has been propelled by the artificial intelligence boom that India's listed universe has largely missed.

The combined value of companies listed on South Korea's KOSPI, KOSDAQ and KONEX exchanges reached $5.01 trillion, surpassing the $4.85 trillion value of firms on India's National Stock Exchange, according to exchange data.

It is the second time in a fortnight that India has been leapfrogged. Taiwan overtook India in May.

## A Stunning Reversal

The speed of India's decline in the global rankings has stunned analysts.

"About 18 months ago, India's equity market cap was roughly 3.5 times South Korea's and more than twice Taiwan's. Fast forward just five months into 2026 and that lead has evaporated," Bernstein analysts Venugopal Garre and Nikhil Arela wrote in a note.

India's benchmark Nifty 50 and Sensex have lost 10.1 per cent and 12.5 per cent respectively this year. The IT index — the second-heaviest sector on both benchmarks — has tumbled 19 per cent, pressured by subdued earnings and persistent foreign selling.

## The Foreign Exodus

Foreign portfolio investors have pulled out $26.4 billion from Indian stocks in 2026 so far — already surpassing the $18.91 billion they withdrew in all of 2025, which was itself a record.

India's share in the MSCI Global Standard index has shrunk to 12.3 per cent from a peak of 21 per cent in September 2024.

"It's really a remarkable decline and a restructure of the whole investment environment for us because of, obviously, the rise of South Korea and Taiwan as well," said Naomi Waistell, a fund manager at French asset manager Carmignac, which manages €41 billion.

The record $2.22 billion sell-off on Friday alone — triggered by MSCI's May rebalancing — underlined the scale of the retreat.

## Why South Korea and Taiwan Are Surging

Both countries have benefited from their deep exposure to AI-related semiconductor manufacturing. South Korea's Samsung Electronics and SK Hynix dominate the global market for high-bandwidth memory chips, a critical and supply-constrained component in AI data centres. Taiwan's TSMC is the world's largest contract chipmaker.

India's listed market, by contrast, is dominated by financials, consumer staples and legacy IT services — none of which have caught the AI tailwind in the same way.

## Some Relief on Tuesday

Indian markets snapped a four-session losing streak on Tuesday, with the Nifty 50 rising 0.43 per cent to 23,483 and the Sensex gaining 0.52 per cent to 74,650.

IT stocks surged 4.2 per cent, taking their gains to 7 per cent in two sessions, after commentary from global software companies suggested that rising AI adoption is driving demand for traditional IT services as well.

"We are seeing value buying as well as sectoral rotation," said Anita Gandhi, head of institutional business at Arihant Capital Markets. "Markets are still in the midst of uncertainties regarding the U.S.-Iran war and a delayed monsoon and will need clarity on these two fronts for any further material gains."

## What It Means for NRIs

For the millions of non-resident Indians invested in Indian equities through PIS accounts, mutual funds and NRE deposits, the message is sobering. Eight consecutive quarters of single-digit earnings growth, combined with the Iran war's impact on oil-dependent India and the forecast of the weakest monsoon in 11 years, have eroded the structural premium that Indian markets once commanded.

The Reserve Bank of India's policy decision on Friday — where most economists expect rates to be held at 5.25 per cent despite a collapsing rupee — will be the next major catalyst."""
})

# ---------- ARTICLE 3: Rubio to face Congress on Iran war ----------
articles.append({
    "headline": "Rubio Will Testify in Public for the First Time on the Iran War This Week. His Own Party Wants Answers.",
    "subheadline": "Republicans are asking about strategy, gasoline prices and an exit plan. Democrats say the war should end 'no matter the terms at this point.'",
    "slug": "rubio-congress-testimony-iran-war-strategy-republicans-gasoline-prices-india-oil-20260602",
    "category": "news",
    "sources_json": ["Reuters", "CBS News", "CNBC"],
    "vertical": "geopolitics",
    "image_search_person": "Marco Rubio",
    "image_search_pexels": None,
    "image_search_pexels_fallback": "US Congress Capitol building",
    "body": """Secretary of State Marco Rubio will testify publicly on the Iran war for the first time this week — and the sharpest questions may come from his own party.

Rubio, who also serves as President Trump's national security adviser, will appear before the Senate Foreign Relations Committee, the House Foreign Affairs Committee and appropriations subcommittees in both chambers over two days. The hearings are nominally about the State Department's budget request, which includes a proposed 30 per cent cut to the foreign affairs budget and a 50 per cent increase in military spending.

But lawmakers have made clear they will use the sessions to press Rubio on the three-month-old war that began with US and Israeli strikes on Iran on February 28 — and that has no end date in sight.

## The Republican Dilemma

Republicans face a political bind. The Iran war has sent gasoline prices soaring, squeezing American consumers and businesses ahead of November's midterm elections. The party needs to retain its slim majorities in both chambers, and lawmakers are increasingly anxious about the economic fallout.

At the same time, Iran hawks within the party oppose any concessions to Tehran, insisting the war must continue until Iran's nuclear programme is permanently dismantled.

Trump has insisted for weeks that he is close to signing a peace agreement and that gasoline prices will come down. But despite a fragile ceasefire that has largely held since early April, the two sides have exchanged strikes several times in the past week, and Iran's Revolutionary Guards have threatened to expand their blockade to include the Bab el-Mandeb Strait at the mouth of the Red Sea.

## Democrats Want Out

Democratic Senator Chris Murphy of Connecticut said on CBS's Face the Nation on Sunday that the war should end "no matter the terms at this point," citing the impact on American consumers.

Last month, the Senate voted to advance a war powers resolution that would end the conflict unless Trump obtains congressional authorisation. The House postponed a similar vote when it looked likely to pass — an unusual sign of Republican unease.

## What India Is Watching

For India, these hearings carry enormous stakes. The Iran war has effectively shut down the Strait of Hormuz, through which nearly a fifth of the world's oil once flowed. India imports close to 90 per cent of its crude oil needs, and the disruption has sent Brent crude to $94 a barrel.

The rupee has tumbled to record lows since the war began. Foreign investors have pulled a record $26.4 billion from Indian equities this year. The Reserve Bank of India faces one of its toughest policy decisions in years when it meets this Friday, caught between a collapsing currency that argues for higher rates and an economy that needs cheaper money.

India's fiscal deficit for FY2025-26 came in at 4.4 per cent of GDP — in line with government estimates — but the outlook for the current year is cloudier. Every dollar increase in the oil price costs India roughly $2.1 billion in additional import expenditure annually.

Any signal from Rubio that a deal is imminent — or that one is not — will move oil markets and, by extension, India's economic trajectory.

## The Bigger Picture

Congress also wants answers on Venezuela, where Trump sent forces to seize President Nicolás Maduro in January and where US forces have been firing on boats off the coast in a campaign that has killed more than 200 people. And there are growing questions about a possible military action against Cuba.

Rubio has spoken to lawmakers behind closed doors about Iran but has never testified publicly on the conflict. His former colleagues in the Senate are hoping their one-time colleague will spell out what the endgame looks like.

Trump, for his part, said in a CNBC interview on Monday that the Iran peace talks had "started to get very boring" and that he did not care if they were over. "I really don't care, I couldn't care less," he said.

Oil prices fell 1.3 per cent on Tuesday to $93.7 a barrel after Trump said talks with Iran were still underway — contradicting earlier reports from Iranian state media that Tehran had suspended negotiations."""
})


# ============================================================
# PUBLISH
# ============================================================

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
published_count = 0

for i, article in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {article['headline'][:60]}...")
    
    art_id = str(uuid.uuid4())
    
    # Image sourcing
    image_url = None
    image_attribution = None
    
    # Try Wikipedia for person articles
    if article.get("image_search_person"):
        print(f"  Looking up Wikipedia image for: {article['image_search_person']}")
        img = fetch_wikipedia_person_image(article["image_search_person"])
        if img and validate_image_url(img):
            filename = f"{art_id}.jpg"
            image_url = upload_image_to_supabase(img, filename)
            image_attribution = "Wikimedia Commons"
    
    # Fallback to Pexels
    if not image_url and article.get("image_search_pexels"):
        print(f"  Trying Pexels: {article['image_search_pexels']}")
        img = fetch_pexels_image(article["image_search_pexels"], article.get("image_search_pexels_fallback"))
        if img and validate_image_url(img):
            filename = f"{art_id}.jpg"
            image_url = upload_image_to_supabase(img, filename)
            image_attribution = "The Videshi"
    
    # Fallback Pexels with fallback query only
    if not image_url and not article.get("image_search_pexels") and article.get("image_search_pexels_fallback"):
        print(f"  Trying Pexels fallback: {article['image_search_pexels_fallback']}")
        img = fetch_pexels_image(article["image_search_pexels_fallback"])
        if img and validate_image_url(img):
            filename = f"{art_id}.jpg"
            image_url = upload_image_to_supabase(img, filename)
            image_attribution = "The Videshi"
    
    if not image_url:
        print("  ⚠ No image found — publishing without image")
    
    # Build article data
    data = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": article.get("vertical", "news"),
        "body": article["body"],
        "status": "published",
        "published_at": now,
        "sources": json.dumps(article["sources_json"]),
        "is_editorial": False
    }
    
    if image_url:
        data["image_url"] = image_url
    if image_attribution:
        data["image_attribution"] = image_attribution
    
    result = sb_insert("p2_articles", data)
    if result:
        print(f"  ✓ Published: {article['slug']}")
        published_count += 1
    else:
        print(f"  ✗ Failed to publish: {article['slug']}")

print(f"\n{'='*60}")
print(f"Done! Published {published_count}/{len(articles)} articles.")
