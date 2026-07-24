#!/usr/bin/env python3
"""News writer for The Videshi — June 2, 2026 evening batch."""

import json
import os
import re
import subprocess
import sys
import time
import uuid
import requests
import urllib.parse
from datetime import datetime, timezone

# Load environment
env_path = os.path.expanduser("~/.env.supabase")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None

    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                [
                    "curl", "-sS",
                    f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                    "-H", f"Authorization: {PEXELS_KEY}",
                ],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                src = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if src:
                    print(f"  ✓ Pexels image found for '{q}': {src[:80]}...")
                    return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate an image URL returns HTTP 200 and is > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_length} bytes, {content_type}")
            return True
        # Try GET for servers that don't support HEAD properly
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type:
            if content_length > 5000:
                return True
            # Read some bytes if content-length not provided
            chunk = r.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def insert_article(article):
    """Insert an article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('headline', 'unknown')[:60]}")
            return True
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
    return False


# ============================================================
# ARTICLE 1: RBI's toughest rate decision
# ============================================================
print("\n=== Article 1: RBI Policy Bind ===")

rbi_image = fetch_wikipedia_person_image("Reserve Bank of India")
if not rbi_image or not validate_image(rbi_image):
    rbi_image = fetch_pexels_image("Indian rupee currency notes", "Reserve Bank India building")
    if not validate_image(rbi_image):
        rbi_image = None

rbi_attribution = "Wikimedia Commons" if rbi_image and "wikimedia" in (rbi_image or "").lower() else "Pexels" if rbi_image else None

article1 = {
    "headline": "The RBI Faces Its Hardest Rate Call in Years. The Iran War, a Sinking Rupee and a Failing Monsoon All Want Different Things.",
    "subheadline": "Nearly 80% of economists expect the central bank to hold rates at 5.25% on Friday, but interest rate swaps are pricing in 100 basis points of tightening over the next year. Something has to give.",
    "slug": "rbi-rate-decision-june-2026-iran-war-rupee-monsoon-policy-bind",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": rbi_image,
    "image_attribution": rbi_attribution,
    "body": """The Reserve Bank of India walks into its three-day monetary policy meeting this week carrying the weight of three simultaneous crises — and no clean way out of any of them.

The Iran war has pushed crude oil past $90 a barrel. The rupee has fallen to record lows near 96 per dollar, losing ground in nearly every session since February. And the India Meteorological Department has forecast the weakest monsoon in eleven years, threatening food prices, rural demand, and kharif crop output in a country where agriculture still employs nearly half the workforce.

## The Impossible Triangle

A rate hike would comfort currency markets and signal the RBI is serious about defending the rupee. But it would also slam the brakes on an economy already showing strain — Indian equity benchmarks have fallen nearly 3% in four sessions, foreign portfolio investors have pulled out more money in 2026 than they did in all of 2025, and Goldman Sachs last week named India the most vulnerable major economy to the Hormuz crisis.

A rate cut is off the table. Holding steady is the path of least resistance — and the one nearly 80% of 56 economists in a Reuters poll expect the RBI to take, keeping the repo rate unchanged at 5.25%.

But the bond and swap markets are telling a different story. Interest rate swaps are pricing in nearly 100 basis points of tightening over the next twelve months, with the one-year overnight indexed swap rate climbing 65 basis points since March. Benchmark ten-year government bond yields have risen 37 basis points over the same period.

"The RBI is approaching the June meeting with a dilemma of whether to respond to market pressures or incoming data," Rahul Bajoria, chief India economist at Bank of America Global Research, wrote in a note. "A hold with hawkish guidance would likely be the most elegant compromise."

## The Rupee Problem

The rupee's slide has been relentless. Since the Iran war broke out on February 28, the currency has tumbled from around 87 per dollar to a record low of 96.96 in mid-May. The RBI has intervened in almost every session since, selling dollars and conducting buy/sell swaps to manage liquidity — but the pressure keeps building.

India's foreign exchange reserves have dipped to an over one-year low of $681 billion. The central bank's short forward dollar commitments declined to $95.3 billion at the end of April from over $100 billion in March, suggesting the RBI is drawing down its ammunition.

The root cause is structural. India imports nearly 90% of its crude oil, and the Hormuz closure has forced it to scramble for alternative supplies from the Americas, Africa, and Russia at elevated prices. The current account deficit is widening. Foreign investors are leaving.

## The Monsoon Wildcard

Making things worse, the monsoon forecast has deteriorated. If rainfall falls significantly below normal, food inflation — which has been relatively contained — could spike. That would close the narrow window of below-target consumer inflation that has given the RBI room to hold rates.

The El Niño conditions driving the weak forecast typically reduce kharif crop yields, push up vegetable and pulse prices, and dampen rural spending — exactly the kind of supply-side shock a central bank cannot easily counter with interest rate tools.

## What It Means for NRIs

For the Indian diaspora, the RBI's decision will ripple through remittance values, property loan rates, and equity market sentiment. The rupee's weakness has been a double-edged sword — remittances buy more in India, but the underlying economic fragility that drives the weakness erodes asset values.

If the RBI holds but signals it is ready to hike, expect the rupee to stabilize near current levels. If it surprises with a hike, expect a short-term equity selloff but a firmer currency. If it holds without hawkish guidance, the rupee could test fresh lows.

The decision comes Friday. The markets are already pricing in their answer. The question is whether the RBI agrees.""",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Bank of America Global Research", "url": "https://www.bofaml.com"},
        {"name": "India Meteorological Department", "url": "https://mausam.imd.gov.in"}
    ]),
}

insert_article(article1)


# ============================================================
# ARTICLE 2: Silver import restrictions
# ============================================================
print("\n=== Article 2: Silver Import Restrictions ===")

silver_image = fetch_pexels_image("silver bars bullion precious metal", "silver coins investment")
if not validate_image(silver_image):
    silver_image = None

article2 = {
    "headline": "India Just Restricted Silver Imports for the Second Time in a Month. The $12 Billion Bill Is the Reason.",
    "subheadline": "Silver in grain and powder form now requires prior government approval. India spent a record $12 billion importing the metal last year — more than double the previous year — and the rupee cannot afford it.",
    "slug": "india-silver-import-restrictions-grain-powder-dgft-rupee-pressure-20260602",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": silver_image,
    "image_attribution": "Pexels" if silver_image else None,
    "body": """India on Tuesday extended its tightening grip on silver imports, adding grain and powder forms to the restricted list and requiring importers to secure prior authorization from the Directorate General of Foreign Trade before bringing any shipment into the country.

It is the second restriction in a month. In May, the government placed silver bars with 99.9% purity and all other semi-manufactured forms under the restricted category. It also more than doubled import tariffs on gold and silver — from 6% to 15% — in a broader push to reduce overseas purchases that are draining foreign exchange reserves at a time when the rupee is under severe pressure from elevated crude oil prices.

## The Numbers Behind the Crackdown

The scale of India's silver appetite explains the urgency. The country spent a record $12 billion on silver imports in the financial year ended March 2026 — up from $4.8 billion a year earlier, a 150% increase. In April alone, silver imports jumped 157% year-on-year to $411 million, trade ministry data showed.

The surge has been driven less by the traditional buyers — jewellers, silversmiths, the wedding industry — and more by investment demand. Inflows into silver exchange-traded funds have climbed to record highs as retail and institutional investors bet on the metal as a hedge against inflation and geopolitical uncertainty.

"The government has made it harder for the bullion industry to bring in silver," a Mumbai-based bullion dealer with a private bank told Reuters. "Importers now need approval first, and there is no clear idea if they will get it or how long it will take."

## Why Now

The timing is not coincidental. The rupee has fallen to record lows against the dollar since the Iran war broke out in February, tumbling from around 87 to nearly 97 before Reserve Bank of India interventions pulled it back to around 95. India's foreign exchange reserves have dropped to an over one-year low of $681 billion.

Every dollar spent importing silver is a dollar that does not go toward crude oil — which India needs far more urgently with Hormuz effectively closed. The government is triaging its foreign exchange spending, and silver, for all its industrial and cultural importance, is not crude.

The restriction also reflects a broader pattern. India has historically swung between liberalizing and restricting precious metal imports depending on the state of its current account. In 2013, when the rupee was in a similar crisis, the government imposed strict curbs on gold imports — the so-called 80:20 rule — that stayed in place for years.

## The Industrial Angle

Silver is not purely an investment metal. India uses it extensively in solar panels, electronics, medical devices, and industrial applications. The restriction on grain and powder forms — the types most commonly used in industrial manufacturing — could create bottlenecks for companies that depend on imported silver as a raw material.

The solar industry, in particular, may feel the pinch. India has ambitious targets for solar energy capacity and silver paste is a critical input for photovoltaic cell manufacturing. Whether the DGFT will fast-track approvals for industrial users or apply the same gatekeeping to all importers remains unclear.

## What NRIs Should Watch

For the diaspora, the silver story is a barometer of how hard the Hormuz crisis is hitting India's external accounts. When a government starts restricting imports of a metal that is woven into the country's cultural fabric — silver is central to festivals, weddings, and religious offerings — the balance of payments pressure is real.

India imports silver mainly from the United Arab Emirates, Britain, and China. If the restrictions hold, expect domestic silver prices to diverge further from international benchmarks, creating both risks and opportunities depending on which side of the trade you are on.""",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Directorate General of Foreign Trade (DGFT)", "url": "https://dgft.gov.in"},
        {"name": "India Trade Ministry", "url": "https://commerce.gov.in"}
    ]),
}

insert_article(article2)


# ============================================================
# ARTICLE 3: US crude exports to Asia
# ============================================================
print("\n=== Article 3: US Crude Exports to Asia ===")

oil_image = fetch_pexels_image("oil tanker ship ocean", "crude oil refinery pipeline")
if not validate_image(oil_image):
    oil_image = None

article3 = {
    "headline": "US Crude Exports Just Hit a Record. Asia Is Buying Everything America Can Ship. It Is Not Nearly Enough.",
    "subheadline": "American crude shipments surged to 5.6 million barrels per day in May as Asian refiners scramble for alternatives to Middle Eastern supply. But with 10 million barrels per day still locked behind Hormuz, the math does not work.",
    "slug": "us-crude-exports-record-asia-india-japan-hormuz-gap-not-enough-20260602",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": oil_image,
    "image_attribution": "Pexels" if oil_image else None,
    "body": """The United States exported a record 5.6 million barrels of crude oil per day in May, smashing the previous record of 5.2 million barrels set just a month earlier, as the Iran war triggers the largest reshuffling of global energy flows in modern history.

Asia took the lion's share. The continent imported 2.45 million barrels per day of American crude in May, with Europe close behind at 2.4 million barrels per day — both record figures. Japan, which historically sources most of its oil from the Persian Gulf, imported a record 808,000 barrels per day from the US, a 32% jump from April.

The numbers tell a story of desperate adaptation. And they also tell a story of fundamental inadequacy.

## The Gap That Cannot Be Closed

Before the war, about 13.54 million barrels per day of crude reached Asia through the Strait of Hormuz. In May, that number was 1.2 million — a 91% collapse — as only vessels with Iranian approval managed to transit.

Asia's total seaborne crude arrivals in May were 19.47 million barrels per day, up from April's decade-low of 18.7 million, but still 22% below the pre-war average of 24.82 million barrels per day.

The additional American crude — roughly 680,000 barrels per day more than the pre-war average — is a rounding error against the 12 million barrels per day that vanished. Even with more US oil on the way — Kpler tracks arrivals of 2.32 million barrels per day for June and 3.07 million for July — the arithmetic is unforgiving.

## The Price Signal

The economics of the trade have shifted dramatically. West Texas Intermediate crude traded at a discount of up to $20.69 per barrel to Brent in March, the widest gap in thirteen years. In April, when most May export deals were struck, the WTI-Brent spread averaged around minus $8.86, compared with minus $4.85 before the war.

That discount is what makes American crude attractive enough to ship across the Pacific. But it also reflects a two-speed oil market: plentiful supply in the Americas, acute scarcity in Asia and Europe. The spread is a measure of how badly the global system is broken.

On Monday, Brent surged above $95 a barrel after fresh US-Iran clashes dimmed hopes for a quick deal, while an ExxonMobil executive warned last week that global inventories are approaching "unheard of" lows and prices could spike to $160 if the strait stays closed.

## India's Position

India is scrambling harder than most. The country imports nearly 90% of its crude and was heavily dependent on Middle Eastern suppliers before the war. It has pivoted aggressively — Venezuela is now India's fourth-largest oil supplier, and the India-Oman trade pact that went live this week opens additional routes that bypass Hormuz entirely.

But the diversification has limits. Indian refiners are paying more for every barrel, the rupee is at record lows, and Goldman Sachs has estimated that a sustained Hormuz closure could shave 3.6% off India's GDP — the highest exposure among major economies.

The Reserve Bank of India meets this week to decide on interest rates, and the oil backdrop is the central variable. Higher crude means a wider current account deficit, more pressure on the rupee, and a harder choice between defending the currency and supporting growth.

## China's Strategic Drawdown

China, the world's largest crude importer, is taking a different path. Rather than importing at elevated prices, Beijing is drawing down its record crude inventories — the strategic reserves built up over years of aggressive buying. May seaborne imports may fall to a decade-low of 6.45 million barrels per day.

Chinese independent refiners in Shandong province are losing an average of 752 yuan ($111) for every ton of imported crude they process, up from 202 yuan in April. Beijing has responded by allowing some refiners to cut output, maximizing domestic drilling, and providing extra import quotas for discounted Russian and Iranian oil.

## The Bottom Line

The surge in US crude exports is real and unprecedented. American producers and shippers are benefiting enormously from the crisis. But framing it as a solution to the Hormuz disruption is misleading. The US is filling a thimble when the world needs a bucket. Until the strait reopens — or the war ends — the global energy market remains structurally short, and the countries that depend most on Middle Eastern oil, India chief among them, will continue to pay the price.""",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Kpler", "url": "https://www.kpler.com"},
        {"name": "ExxonMobil / Bernstein Conference", "url": "https://www.exxonmobil.com"}
    ]),
}

insert_article(article3)

print("\n=== News writer complete ===")
