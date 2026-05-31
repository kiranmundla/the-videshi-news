#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-31 batch)
Writes 3 news articles: Delhi building collapse, Israel Beaufort Castle capture, India oil diversification
"""

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

# Load env
env_path = os.path.expanduser("~/.env.supabase")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

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
    """Fetch a relevant image from Pexels using curl (Python urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                [
                    "curl", "-sS",
                    f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                    "-H", f"Authorization: {PEXELS_API_KEY}",
                ],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    # Validate image
                    check = subprocess.run(
                        ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code} %{size_download} %{content_type}", url],
                        capture_output=True, text=True, timeout=10,
                    )
                    parts = check.stdout.strip().split()
                    if len(parts) >= 2 and parts[0] == "200" and int(parts[1]) > 5000:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate an image URL returns 200 with content > 5KB."""
    if not url:
        return False
    try:
        result = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code} %{size_download}", "-L", url],
            capture_output=True, text=True, timeout=15,
        )
        parts = result.stdout.strip().split()
        if len(parts) >= 2 and parts[0] == "200" and int(parts[1]) > 5000:
            return True
    except:
        pass
    return False


def publish_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    payload = {
        "id": str(uuid.uuid4()),
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": article["category"],
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution", ""),
        "sources": json.dumps(article.get("sources", [])),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        r = requests.post(url, headers=HEADERS, json=payload, timeout=15)
        if r.status_code in (200, 201):
            print(f"  ✓ Published: {article['headline'][:60]}...")
            return True
        else:
            print(f"  ✗ Failed ({r.status_code}): {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Error publishing: {e}")
        return False


# ============================================================
# ARTICLE 1: Delhi Building Collapse Near Saket
# ============================================================
print("\n=== Article 1: Delhi Building Collapse ===")

img1 = fetch_pexels_image("building collapse rescue India", "demolished building rubble rescue")
img1_attr = "Pexels" if img1 else ""

article1 = {
    "headline": "A Building Near Saket Metro Collapsed on a Saturday Evening. Four People Are Dead.",
    "subheadline": "The five-storey structure housed a coaching institute and cafés. Students preparing for medical entrance exams were eating dinner in a tin-shed canteen next door when it fell.",
    "slug": "delhi-saket-building-collapse-four-dead-coaching-institute-mehrauli-20260531",
    "category": "news",
    "image_url": img1,
    "image_attribution": img1_attr,
    "sources": [
        {"name": "PTI via Swadesi", "url": "https://swadesi.com"},
        {"name": "India Today", "url": "https://www.indiatoday.in"},
        {"name": "All India Radio News", "url": "https://airnews.in"},
        {"name": "News9", "url": "https://news9live.com"},
    ],
    "body": """A five-storey commercial building on Western Marg in Delhi's Saidulajab area collapsed on Saturday evening, killing at least four people and injuring several others who remain under treatment at AIIMS Trauma Centre. The structure, located near the Saket Metro station in south Delhi, housed a coaching institute on its ground floor, cafés, and office spaces — and construction work was reportedly underway on its upper floors when it gave way.

The Delhi Fire Service received a distress call at 7:44 PM and dispatched three water tenders and an incident response team to the site. What they found was a mound of concrete, twisted steel, and broken pillars. The building had collapsed entirely onto an adjacent tin-shed canteen, a place where students preparing for medical entrance examinations routinely stopped for dinner. Several of them were inside when the structure fell.

## A Night-Long Rescue Operation

A multi-agency rescue operation involving the National Disaster Response Force, Delhi Fire Services, the Delhi Disaster Management Authority, Delhi Police, and local volunteers ran through the night. Heavy machinery — JCBs, hydraulic cutters, victim-location cameras, and sniffer dogs — was deployed to clear the debris and search for survivors.

By Sunday morning, at least ten people had been pulled from the rubble. Eight of the injured were admitted to AIIMS Trauma Centre, with some in critical condition. Two were declared dead on arrival. The deceased included a 26-year-old man identified as Ravi. The injured ranged in age from 24 to 27, hailing from Gurugram, Bihar, Noida, and the Saidulajab and Saket neighbourhoods.

"All we could hear were screams," recalled Arvind Kumar, a resident who was standing outside the building when it fell.

## A System That Keeps Failing

Delhi Chief Minister Rekha Gupta visited the collapse site and ordered a criminal probe. Police have filed a First Information Report against the building owner under culpable homicide charges. Raids are underway to secure an arrest.

But the collapse is not an isolated incident. A 2025 audit flagged 1,500 buildings in South Delhi alone as structurally deficient. Experts have repeatedly warned that rapid urban growth, unauthorized construction on upper floors, and lax enforcement by municipal authorities have turned many of Delhi's older structures into hazards.

The Saidulajab building appeared to be one of them. Fire service officials said preliminary information suggested that additional construction was being carried out on the third or upper floor at the time of the collapse, and that the structure gave way suddenly, leaving occupants no time to react.

## The Diaspora Connection

For NRI families in the United States, the United Kingdom, and Canada whose children study in Delhi's coaching hub ecosystem — particularly in areas around Saket, Kalu Sarai, and Mukherjee Nagar — the collapse is a reminder of the infrastructure risks that rarely make it into glossy college brochures. South Delhi's coaching belt serves hundreds of thousands of students preparing for NEET, UPSC, and other competitive examinations. Many of them live and study in buildings that have never been structurally audited.

The incident has renewed calls for a comprehensive structural audit of all commercial buildings in Delhi, particularly those housing coaching institutes and educational facilities. Whether those calls will translate into action remains an open question.

*Search and rescue operations continued at the site as of Sunday afternoon.*"""
}

# ============================================================
# ARTICLE 2: Israel Captures Beaufort Castle in Lebanon
# ============================================================
print("\n=== Article 2: Israel Captures Beaufort Castle ===")

img2 = fetch_wikipedia_person_image("Beaufort Castle (Lebanon)")
if not img2 or not validate_image_url(img2):
    img2 = fetch_pexels_image("ancient castle hilltop middle east fortress", "crusader castle ruins")
    img2_attr = "Pexels" if img2 else ""
else:
    img2_attr = "Wikimedia Commons"

article2 = {
    "headline": "Israel Just Captured a 900-Year-Old Crusader Castle in Lebanon. It Is Their Deepest Incursion in 26 Years.",
    "subheadline": "The seizure of Beaufort Castle and its strategic ridge gives Israeli forces an overlook over much of southern Lebanon. Three and a half million Indians live in the Gulf states next door.",
    "slug": "israel-captures-beaufort-castle-lebanon-deepest-incursion-26-years-hezbollah-india-20260531",
    "category": "news",
    "image_url": img2,
    "image_attribution": img2_attr,
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Associated Press via Audacy", "url": "https://www.audacy.com"},
        {"name": "CNN", "url": "https://www.cnn.com"},
        {"name": "Livemint", "url": "https://www.livemint.com"},
    ],
    "body": """Israeli troops have seized Beaufort Castle, a 900-year-old Crusader-era fortress perched on a strategic ridge in southern Lebanon, in what the Associated Press called their deepest incursion into Lebanese territory in more than a quarter century. The capture came on Sunday after days of intense fighting and airstrikes in nearby villages, and despite a nominal ceasefire that has been in place since April 17.

The castle, built on a high cliff overlooking the Litani River near the city of Nabatiyeh, has been a coveted military position for centuries. Israeli forces previously held it from 1982 until their withdrawal from Lebanon in 2000. Its ridge offers a commanding overlook over much of southern Lebanon and northern Israel — terrain from which Hezbollah has launched hundreds of rockets and drones toward Israeli civilian areas since the current conflict began.

## The Operation

The Israel Defense Forces said the operation began several days ago, focused on establishing operational control of the Beaufort Ridge and the Wadi al-Saluki valley. One Israeli soldier was killed during the advance. Israeli troops have now crossed the Litani River — previously used as a de facto boundary — and are positioned approximately five kilometres from Nabatiyeh, a major Hezbollah stronghold.

"This is a clear message to our enemies: anyone who threatens Israeli civilians will lose their strategic assets one by one," Israeli Defence Minister Israel Katz said.

The advance came after Saturday saw some of the heaviest Hezbollah fire toward northern Israel since the April ceasefire. Hezbollah fighters launched rockets at Kiryat Shmona and Safed, prompting school closures and civilian restrictions. The group also claimed to have destroyed an Israeli Merkava tank near the castle.

The Lebanese state news agency NNA reported Israeli air raids and "intense bombardment" in the surrounding area. Three days before the capture, the Arnoun Municipality had denounced Israeli bombing near the castle and urged international organizations to protect the historic site.

## Why This Matters for the Region

The seizure of Beaufort Castle deepens Israel's military footprint in Lebanon at a time when the broader Iran-US conflict remains unresolved. A two-hour White House Situation Room meeting on Friday ended without a deal to extend the fragile ceasefire. Pentagon chief Pete Hegseth said on Saturday that the United States has "plentiful munitions" to resume operations if necessary, while 50,000 US troops remain stationed across the region.

The continuing instability has direct consequences for the Strait of Hormuz, through which roughly half of India's oil supply transits. The strait remains partially disrupted, forcing Indian refiners to diversify purchases toward Latin America and Africa.

## The India Connection

For the 3.5 million Indians living in the Gulf states — the UAE, Qatar, Kuwait, Bahrain, Oman, and Saudi Arabia — every escalation in the Israel-Hezbollah-Iran triangle is a livelihood calculation. Many are construction workers, nurses, engineers, and IT professionals whose remittances sustain families back in India. The Indian government's Finance Ministry has already named the Strait of Hormuz as the single biggest risk to India's economy in 2026.

The broader question remains whether the Israel-Hezbollah front will remain contained or widen into something that forces a Gulf evacuation. India's Ministry of External Affairs has maintained contingency plans since the conflict began in February, but each Israeli advance deeper into Lebanon makes that calculation harder.

Israel last held Beaufort Castle for 18 years. Whether this occupation lasts as long depends on negotiations that are, for the moment, going nowhere."""
}

# ============================================================
# ARTICLE 3: India Diversifies Oil Imports Away From Middle East
# ============================================================
print("\n=== Article 3: India Oil Diversification ===")

img3 = fetch_pexels_image("oil tanker ship ocean", "crude oil refinery India")
img3_attr = "Pexels" if img3 else ""

article3 = {
    "headline": "India Is Buying Oil From Venezuela and Angola Now. The Strait of Hormuz Made That Decision for Them.",
    "subheadline": "Indian refiners have sharply increased purchases from Latin America and Africa as the Iran conflict continues to squeeze their traditional Middle East supply routes.",
    "slug": "india-oil-imports-venezuela-angola-latin-america-hormuz-disruption-diversification-20260531",
    "category": "news",
    "image_url": img3,
    "image_attribution": img3_attr,
    "sources": [
        {"name": "The Indian Eye", "url": "https://theindianeye.com"},
        {"name": "Barron's", "url": "https://www.barrons.com"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
    ],
    "body": """India has sharply increased crude oil purchases from Latin America and Africa as the continuing disruption in the Strait of Hormuz squeezes the country's traditional supply routes from the Middle East. Refiners are now leaning on Venezuela, Brazil, Angola, and Nigeria to keep flows stable — a shift that looks less like a temporary fix and more like a structural realignment of India's energy sourcing strategy.

According to preliminary data from Kpler, a commodity analytics firm, Indian imports from Venezuela, Brazil, Angola, and Nigeria rose in April and May to cover shortfalls caused by the Israeli-US conflict with Iran and the resulting shipping chaos in Hormuz. Venezuela is on track to become India's fourth-largest oil supplier in May, reflecting stronger demand for heavy crude as Gulf flows remain constrained.

India is still receiving approximately 1.9 million barrels per day of Russian oil and about 41,000 barrels per day from Iraq. But the direction of travel is clear: away from a chokepoint that now accounts for the single biggest risk to the Indian economy, according to the Finance Ministry's own assessment.

## Half of India's Oil Came Through Hormuz

The Strait of Hormuz, a narrow waterway between Iran and Oman, has historically carried about half of India's crude oil supply. When Iran partially disrupted navigation through the strait after the US-Israeli military campaign began in February, it set off a chain reaction across India's energy system.

Cooking gas prices spiked. Fuel subsidies strained the fiscal deficit. Consumer spending weakened. Indian stocks entered their worst year in three decades relative to Asian peers. Remittances from the Gulf — where 3.5 million Indians work — declined as the regional economy slowed.

The government responded with austerity measures to reduce energy consumption and rushed out subsidies to cushion the impact. But the fundamental problem remained: India was too dependent on a single transit route for too much of its oil.

## The Diversification Play

The pivot to Latin American and African suppliers is an attempt to fix that vulnerability. Venezuela, which has the world's largest proven oil reserves, offers heavy crude that Indian refineries are well-equipped to process. Brazil's pre-salt fields provide high-quality light crude. Angola and Nigeria offer diversified sourcing from a continent that India has been courting for broader trade and diplomatic reasons.

But diversification comes at a cost. Longer shipping routes from South America and West Africa mean higher freight charges. Insurance premiums remain elevated. And the reliability of some of these suppliers — particularly Venezuela, which operates under US sanctions — introduces its own risks.

## What NRIs Should Watch

For the Indian diaspora, the oil supply chain might seem abstract. It is not. Cooking gas prices in India have a direct impact on household budgets — particularly for the families that NRI remittances support. The weakening rupee, driven partly by the energy import bill, affects the purchasing power of every dollar sent home. And any extended disruption to Gulf economies hits the 3.5 million Indians who live and work there.

Barron's noted this week that a resolution of the Iran conflict could offer Indian stocks "a much-needed catalyst," with the iShares MSCI India ETF offering broad exposure to a potential recovery. But that catalyst requires a deal that, after a two-hour White House meeting ended without one on Friday, remains elusive.

For now, India's oil tankers are taking longer routes, paying higher freight, and buying from countries that were not on the supplier list six months ago. The Strait of Hormuz made that decision for them. Whether it becomes permanent depends on whether the ceasefire holds — and right now, it barely is."""
}


# ============================================================
# Publish all articles
# ============================================================
print("\n=== Publishing Articles ===")
articles = [article1, article2, article3]
published = 0
failed = 0

for i, article in enumerate(articles, 1):
    print(f"\n--- Article {i}: {article['headline'][:60]}... ---")
    
    # Validate before publishing
    if len(article["headline"]) < 20 or len(article["headline"]) > 200:
        print(f"  ✗ Headline length issue: {len(article['headline'])} chars")
        failed += 1
        continue
    if len(article["subheadline"]) < 15:
        print(f"  ✗ Subheadline too short: {len(article['subheadline'])} chars")
        failed += 1
        continue
    word_count = len(article["body"].split())
    if word_count < 400:
        print(f"  ✗ Body too short: {word_count} words")
        failed += 1
        continue
    if article["category"] != "news":
        print(f"  ✗ Wrong category: {article['category']}")
        failed += 1
        continue
    if not article.get("image_url"):
        print(f"  ⚠ No image — publishing without image")
    
    print(f"  Word count: {word_count}")
    print(f"  Image: {'✓' if article.get('image_url') else '✗ none'}")
    
    if publish_article(article):
        published += 1
    else:
        failed += 1
    
    time.sleep(1)  # Rate limit

print(f"\n=== Done: {published} published, {failed} failed ===")
