#!/usr/bin/env python3
"""
News writer batch — publishes 3 articles to Supabase.
Run: source ~/.env.supabase && source ~/workspace/.env.pexels && python3 writer-news-batch.py
"""

import json, os, re, sys, time, uuid, hashlib
from datetime import datetime, timezone

import requests

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ── helpers ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = requests.utils.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img, "Wikimedia Commons"
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None, None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels. Returns (url, attribution) or (None, None)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None, None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for photo in photos:
                    url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url, "Pexels"
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None, None


def validate_image(url):
    """Check image URL returns 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD properly
        if r.status_code != 200 or "image" not in ct:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            ct2 = r2.headers.get("Content-Type", "")
            if r2.status_code == 200 and "image" in ct2:
                chunk = r2.raw.read(6000)
                if len(chunk) > 5000:
                    return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False


def sb_insert(table, payload):
    """Insert a row into Supabase and return the response."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0]
        return data
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


def publish_article(article):
    """Publish a single article to Supabase."""
    print(f"\n{'='*60}")
    print(f"Publishing: {article['headline']}")
    print(f"  Slug: {article['slug']}")
    print(f"  Category: {article['category']}")

    # Image sourcing
    img_url = None
    img_attr = None

    # Try Wikipedia for person articles
    if article.get("primary_person"):
        img_url, img_attr = fetch_wikipedia_person_image(article["primary_person"])
        if img_url and not validate_image(img_url):
            print(f"  ⚠ Wikipedia image failed validation, trying alternate...")
            img_url, img_attr = None, None
        # Try alternate names
        if not img_url and article.get("alt_person_names"):
            for alt in article["alt_person_names"]:
                img_url, img_attr = fetch_wikipedia_person_image(alt)
                if img_url and validate_image(img_url):
                    break
                img_url, img_attr = None, None

    # Pexels fallback
    if not img_url and article.get("pexels_query"):
        img_url, img_attr = fetch_pexels_image(
            article["pexels_query"],
            article.get("pexels_fallback")
        )
        if img_url and not validate_image(img_url):
            print(f"  ⚠ Pexels image failed validation")
            img_url, img_attr = None, None

    if img_url:
        print(f"  ✓ Image: {img_url[:80]}...")
    else:
        print(f"  ℹ No image found — publishing without")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    art_id = str(uuid.uuid4())

    payload = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "body": article["body"],
        "category": article["category"],
        "sources": article["sources"],
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "vertical": article["category"],
        "image_url": img_url,
        "image_attribution": img_attr,
    }

    result = sb_insert("p2_articles", payload)
    if result:
        print(f"  ✓ Published: {art_id}")
    else:
        print(f"  ✗ FAILED to publish")
    return result


# ── Articles ──

articles = [
    {
        "headline": "Missiles Hit Kuwait and Bahrain as Iran War Flares Again. Millions of Indian Workers Are in the Danger Zone.",
        "subheadline": "Air raid sirens sounded across both countries as Iranian ballistic missiles and drones targeted Gulf states. Over a million Indians live in Kuwait alone.",
        "slug": "iran-missiles-kuwait-bahrain-indian-workers-gulf-war-escalation-20260603",
        "category": "news",
        "primary_person": None,
        "pexels_query": "Kuwait city skyline",
        "pexels_fallback": "Persian Gulf coast",
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "USA Today", "url": "https://www.usatoday.com"},
            {"name": "The Sun", "url": "https://www.thesun.co.uk"},
            {"name": "US Central Command (CENTCOM)", "url": "https://www.centcom.mil"}
        ],
        "body": """The Iran war erupted into a dangerous new phase on Wednesday when Iranian ballistic missiles and drones struck at Kuwait and Bahrain — two Gulf states that are home to more than 1.3 million Indian expatriates.

Kuwait's army confirmed its air defences were intercepting hostile missile and drone attacks. Bahrain's interior ministry sounded warning sirens and urged "citizens and residents to head to the nearest safe place." It subsequently banned all citizen travel to Iran and Iraq, citing the "continued tense security situation."

## What Happened

US Central Command (CENTCOM) said it "successfully defeated multiple Iranian ballistic missiles and drones" fired at Gulf allies. According to CENTCOM, two Iranian missiles aimed at Kuwait "fell short or broke apart en route," and three missiles launched at Bahrain "were immediately intercepted by US and Bahrain air defense forces."

The Pentagon confirmed that US military forces launched "self-defence strikes" against Iran's Qeshm Island, located near the Strait of Hormuz, in direct response to the Iranian attacks. Iran's Revolutionary Guards claimed the strikes were retaliation for a US attack on an Iranian vessel and a telecommunications antenna.

The exchange marks the most significant flare-up since the April ceasefire, which has held together by a thread even as the Strait of Hormuz remains largely shut to commercial shipping.

## India's Gulf Diaspora at Risk

The escalation puts an enormous Indian diaspora population directly in harm's way. India's Ministry of External Affairs estimates that approximately 1.03 million Indian nationals live and work in Kuwait, making them the largest expatriate community there. Bahrain hosts an additional 350,000 Indian workers, primarily in construction, retail, hospitality, and the oil and gas sector.

India has maintained contingency evacuation plans for its Gulf diaspora since the war began in February. The Indian embassy in Kuwait activated its emergency helpline during the March missile attacks and has kept it operational since. Indian embassies in both countries have urged citizens to stay vigilant, keep identity documents accessible, and avoid non-essential travel.

During the initial round of Iranian strikes on Gulf states in early March, the GCC Secretary General condemned the attacks as "a flagrant and unacceptable violation of all international norms." India's Ministry of External Affairs expressed "deep concern" and asked its citizens to follow local authority instructions.

## The Diplomatic Backdrop

The missile exchange came as Secretary of State Marco Rubio testified before Congress for the first time since the war began. In a heated exchange with Senator Cory Booker, Rubio declared "the war is over" — a claim Booker immediately rejected, saying the fighting clearly continues.

Rubio told the Senate Foreign Relations Committee that Iran has "agreed to negotiate aspects of their nuclear program that just a month ago, just a year ago, they were refusing to even mention." But he offered no guarantee that negotiations would produce an acceptable deal.

Meanwhile, President Trump reportedly had an expletive-laden phone call with Israeli Prime Minister Benjamin Netanyahu, demanding Israel halt strikes on Hezbollah in Beirut that were threatening to collapse the fragile ceasefire framework.

## What It Means for India

The escalation deepens India's triple vulnerability in the Gulf conflict: energy security, diaspora safety, and economic exposure.

India imports nearly 90 percent of its crude oil, and the Hormuz closure has already forced a wholesale rewiring of supply chains toward Latin America and Africa. Goldman Sachs recently named India the most vulnerable major economy to a prolonged Hormuz disruption, estimating a 3.6 percent GDP hit.

Every new round of fighting makes a deal to reopen the strait less certain. Oil prices rose to a one-week high of $96.07 per barrel on Tuesday as markets priced in the possibility that the ceasefire could collapse entirely.

For the 9 million Indians living across the six GCC states, the question is no longer hypothetical. The missiles are landing in their cities, the sirens are sounding in their neighbourhoods, and the evacuation plans that seemed precautionary four months ago may need to become operational."""
    },
    {
        "headline": "Adani Portfolio Just Spent ₹1.53 Lakh Crore in a Single Year. No Indian Company Has Ever Invested That Much.",
        "subheadline": "Record capex of $16.1 billion, an $82 billion asset base, and the opening of Navi Mumbai airport mark what the group calls an inflection point.",
        "slug": "adani-portfolio-record-capex-153000-crore-fy26-navi-mumbai-airport-renewables-20260603",
        "category": "news",
        "primary_person": "Gautam Adani",
        "alt_person_names": ["Gautam_Adani"],
        "pexels_query": "Mumbai infrastructure construction",
        "pexels_fallback": "India airport modern",
        "sources": [
            {"name": "IANS", "url": "https://ianslive.in"},
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "Business Standard", "url": "https://www.business-standard.com"}
        ],
        "body": """The Adani Portfolio has delivered the highest annual capital expenditure by any Indian corporate in history — ₹1,52,967 crore ($16.1 billion) in the financial year ended March 2026.

The group's asset base now stands at ₹7,85,098 crore ($82.2 billion), and its EBITDA reached an all-time high of ₹94,834 crore ($10 billion), up 5.6 percent year-on-year. Core infrastructure — spanning energy, utilities, transport, and logistics — contributed 87 percent of total earnings.

## Where the Money Went

Nearly 80 percent of the ₹1.53 lakh crore was directed toward infrastructure platforms that the group considers its core engine.

The most visible milestone was the opening of the Navi Mumbai International Airport, a greenfield facility that becomes the second major airport serving India's financial capital. The airport features two passenger terminals, dual runways, a multi-modal transport hub, and a dedicated metro link.

In the energy vertical, the group added 5.1 GW of renewable energy capacity and commissioned 3.37 GWh of battery energy storage systems. The Guwahati terminal and the Ganga Expressway also entered operations, along with a copper smelter in the primary industries segment.

"The scale of capital deployment during the year is comparable to the asset base we had built over our first 25 years," the group said in a statement, describing FY26 as an "important inflection point."

## Financial Health Indicators

Cash at year-end stood at ₹55,852 crore ($5.9 billion), equivalent to 15 percent of gross debt. Borrowing costs declined to 7.8 percent from 9 percent two years ago, supported by consistent credit rating upgrades across the portfolio.

The numbers come at a time when private investment in India has been sluggish. Economists have flagged that government capital expenditure has shouldered a disproportionate share of India's growth, with corporate India reluctant to commit to large-scale capacity expansion amid geopolitical uncertainty.

Adani's willingness to deploy capital at this scale — during a year in which the Iran war disrupted global energy markets and the rupee hit record lows — represents a notable counter-trend.

## The Defence Pivot

Beyond traditional infrastructure, the Adani Group has deepened its presence in defence manufacturing. The group's Drishti 10 unmanned aerial vehicles have been inducted into the Indian Navy and Army for intelligence, surveillance, and reconnaissance missions.

Adani Defence & Aerospace has emerged as India's largest integrated private-sector defence player, with capabilities spanning unmanned aerial and underwater systems, guided weapons, small arms, aircraft maintenance, repair and overhaul (MRO), and airborne warning systems.

The company has committed to further investment in autonomous systems, AI-enabled multi-domain operations, and advanced guided weapons in the current fiscal year — positioning itself as a cornerstone of India's self-reliance push in defence.

## Diaspora Investment Angle

For NRI investors who hold Adani group stocks — several of which have recovered significantly from the post-Hindenburg lows of 2023 — the record capex raises the question of when these infrastructure assets begin generating proportionate cash flows. The new airport, battery storage systems, and renewable energy capacity are expected to contribute meaningfully to earnings in FY27 and beyond.

The group's borrowing cost reduction from 9 percent to 7.8 percent signals improving credit quality, but the debt-to-equity dynamics across individual listed entities remain a key metric to watch.

With India's infrastructure build-out now at a scale that few private conglomerates anywhere in the world are matching, the Adani Portfolio's ₹1.53 lakh crore year is less an outlier and more a preview of the capital cycle that India's urbanisation and energy transition will demand over the next decade."""
    },
    {
        "headline": "India's Factories Just Had Their Best Month Since February. The War Is Making Everything More Expensive.",
        "subheadline": "Manufacturing PMI climbed to 55.0 in May on strong domestic demand, but input costs are at a near four-year high as the Hormuz disruption drives up fuel and material prices.",
        "slug": "india-manufacturing-pmi-55-may-2026-cost-pressures-iran-war-hormuz-20260603",
        "category": "news",
        "primary_person": None,
        "pexels_query": "India factory manufacturing industrial",
        "pexels_fallback": "Indian manufacturing workers",
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "S&P Global", "url": "https://www.spglobal.com"},
            {"name": "HSBC", "url": "https://www.hsbc.com"}
        ],
        "body": """India's manufacturing sector expanded at its fastest pace in three months in May, even as the Iran war drove input costs to near four-year highs — a snapshot of an economy that is growing through pain rather than despite it.

The HSBC India Manufacturing Purchasing Managers' Index (PMI), compiled by S&P Global, rose to 55.0 in May from 54.7 in April, beating a preliminary estimate of 54.3. Any reading above 50 indicates expansion.

## Domestic Demand Is Carrying the Load

New orders — the most closely watched component of the PMI — grew at their fastest rate since February. The demand was driven by civil engineering projects, competitive pricing, and what S&P Global described as "favourable demand conditions."

But the growth is increasingly lopsided. Domestic demand remains the primary engine, while export orders, although still expanding, grew at their slowest pace in three months. For an economy whose export sector was already under pressure from US tariffs and global uncertainty, the softening in external demand is a warning signal.

Factory output rose at its quickest pace in three months, led by intermediate and capital goods. Consumer goods manufacturers, by contrast, saw growth ease — a sign that the cost pressures rippling through the supply chain are beginning to affect the end consumer.

## The Cost Problem

The most striking number in the May PMI is the cost side. Input price inflation was the second-strongest in roughly four years, driven by higher outlays for energy, fuel, raw materials, and transportation. The survey explicitly cited the Iran war and the Hormuz disruption as contributing factors.

Capital goods producers faced the sharpest cost increases among the three sub-sectors tracked. The pattern is consistent with what Goldman Sachs, Vitol, and other commodity analysts have been warning: the physical supply of refined fuel and petrochemical products is tighter than crude oil benchmarks suggest, and the cost is being transmitted through every link of the industrial supply chain.

Yet manufacturers are absorbing much of the hit rather than passing it on. Selling price inflation eased from April and remained below the rate of input cost growth, as competitive pressures restrained firms from raising prices fully. The gap between input and output inflation is a measure of how much corporate margins are being squeezed.

## Hiring and Stockpiling

Employment continued to grow, although the pace of job creation slowed from April. More notably, firms sharply increased purchasing activity — at the fastest rate in three months — partly to build contingency stocks. In an environment of supply-chain uncertainty, manufacturers are choosing to hold more inventory as a buffer against potential disruptions.

This stockpiling behaviour mirrors what the global oil market is experiencing in reverse: while industrial firms hoard inputs, global crude and product inventories are being drawn down to dangerously low levels.

## Business Confidence Falls

Despite the strong demand numbers, business confidence fell to its lowest level since February. Companies remain positive overall, expressing hope that cost pressures will ease, but the optimism is qualified. The war, the rupee's weakness, and the approaching monsoon season — forecast to be the weakest in 11 years — are all weighing on the outlook.

## What It Means for the RBI

The PMI data arrives two days before the Reserve Bank of India's Monetary Policy Committee announces its rate decision on June 5. The central bank is widely expected to hold the repo rate at 5.25 percent, but the cost inflation embedded in the manufacturing data complicates that stance.

Retail inflation remains below the RBI's 4 percent target at 3.48 percent in April, but wholesale inflation has climbed to 8.3 percent. The PMI data suggests that the gap between producer costs and consumer prices is being bridged by margin compression rather than stable supply conditions — a pattern that is sustainable in the short term but not indefinitely.

If the Hormuz situation deteriorates further or the monsoon disappoints, the cost pressures visible in the PMI data could eventually spill over into retail inflation, forcing the RBI's hand on rates.

For now, India's factories are running hot. The question is how long they can absorb the heat."""
    },
]


if __name__ == "__main__":
    successes = 0
    for art in articles:
        result = publish_article(art)
        if result:
            successes += 1
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Published {successes}/{len(articles)} articles")
    if successes < len(articles):
        sys.exit(1)
