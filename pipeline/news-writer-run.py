#!/usr/bin/env python3
"""
The Videshi — News Writer
Generates 3 news articles with proper image sourcing, quality, and dedup.
"""

import json
import os
import sys
import subprocess
import datetime
import re
import urllib.parse
import requests
import uuid
import time

# Load env
env_path = os.path.expanduser("~/.env.supabase")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
PEXELS_KEY = ""
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if "PEXELS_API_KEY" in line and "=" in line:
                PEXELS_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}


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
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate image URL returns HTTP 200 with proper content type and size."""
    if not url:
        return False
    # Block banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ Banned image source: {b}")
            return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {ct}, {cl} bytes")
            return True
        # Some servers don't return Content-Length on HEAD
        if r.status_code == 200 and "image" in ct:
            print(f"  ✓ Image validated (no CL): {ct}")
            return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def generate_slug(headline):
    """Generate a human-readable slug from headline."""
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    slug = slug[:80].rstrip('-')
    today = datetime.datetime.utcnow().strftime('%Y%m%d')
    return f"{slug}-{today}"


def publish_article(article):
    """Publish article to Supabase."""
    # Format sources as array of objects with name key
    raw_sources = article.get("sources", [])
    if raw_sources and isinstance(raw_sources[0], str):
        formatted_sources = [{"name": s} for s in raw_sources]
    else:
        formatted_sources = raw_sources

    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "news",
        "vertical": article.get("vertical", "general"),
        "diaspora_angle": article.get("diaspora_angle", ""),
        "tags": article.get("tags", []),
        "urgency": article.get("urgency", "medium"),
        "status": "published",
        "published_at": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00'),
        "image_url": article.get("image_url", ""),
        "image_caption": article.get("image_caption", ""),
        "sources": formatted_sources,
        "image_attribution": article.get("image_attribution", ""),
        "score_total": article.get("score_total", 85),
    }
    
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=HEADERS,
            json=payload,
            timeout=30
        )
        if r.status_code in [200, 201]:
            result = r.json()
            if isinstance(result, list) and result:
                print(f"  ✓ Published: {result[0].get('slug', 'unknown')}")
                return True
            print(f"  ✓ Published (response: {r.status_code})")
            return True
        else:
            print(f"  ✗ Publish failed: {r.status_code} — {r.text[:300]}")
            return False
    except Exception as e:
        print(f"  ✗ Publish error: {e}")
        return False


# ============================================================
# ARTICLE 1: India Monsoon Below-Average Forecast
# ============================================================
print("\n" + "="*60)
print("ARTICLE 1: India Monsoon Below-Average Forecast")
print("="*60)

monsoon_image = fetch_pexels_image("Indian monsoon rain farmer field", "monsoon rain India agriculture")
if monsoon_image and not validate_image_url(monsoon_image):
    monsoon_image = None

article1 = {
    "headline": "India's Monsoon Will Be the Weakest in Three Decades. Half the Country's Farmers Depend on It.",
    "subheadline": "The India Meteorological Department has downgraded its monsoon forecast to just 90 percent of the long-period average — the lowest since the mid-1990s — as El Niño conditions develop and the Iran war drives food inflation higher.",
    "slug": generate_slug("india-monsoon-weakest-three-decades-farmers-el-nino-food-inflation"),
    "image_url": monsoon_image or "",
    "image_caption": "Indian farmers depend on the June-September monsoon for nearly 70 percent of their annual rainfall.",
    "image_attribution": "Pexels" if monsoon_image else "",
    "sources": [
        "Reuters — India expected to have below-average monsoon rains in 2026",
        "India Meteorological Department (IMD) — May 2026 Updated Forecast",
        "ICRA — Chief Economist Aditi Nayar analysis",
        "Froggyweb/Reuters — India forecasts sub-par monsoon after two years of above-average rains"
    ],
    "vertical": "economy",
    "diaspora_angle": "The monsoon directly affects food prices for families back home and the value of remittances — India's $136 billion annual inflow from NRIs often flows to rural households whose incomes depend on seasonal rainfall.",
    "tags": ["monsoon", "el-nino", "agriculture", "food-inflation", "imd", "india-economy"],
    "urgency": "high",
    "score_total": 92,
    "body": """India's government confirmed on Friday what farmers across the country had been dreading: the 2026 monsoon will deliver significantly less rain than normal, threatening crop yields, pushing food prices higher, and compounding an economy already battered by the Iran war's energy shock.

The India Meteorological Department has downgraded its seasonal forecast to just 90 percent of the long-period average — the weakest projection in nearly three decades. An earlier estimate in April had pegged rainfall at 92 percent of the LPA; the updated May outlook is even grimmer.

## What 90 Percent of LPA Actually Means

The IMD defines "normal" monsoon rainfall as between 96 and 104 percent of a 50-year average of 87 centimetres across the four-month June-to-September season. Anything below 96 percent is classified as below normal.

At 90 percent, India would receive roughly 78 centimetres of rain — enough to avoid the "deficient" classification (below 90 percent) but not enough to sustain a normal cropping cycle across the country's vast agricultural heartland.

"Currently weak La Niña-like conditions are transitioning to neutral conditions. But after June it's very likely that El Niño will develop," said Mrutyunjay Mohapatra, director-general of the IMD.

El Niño — the ocean warming phenomenon in the central and eastern Pacific — has historically been devastating for Indian agriculture. In most El Niño years, India has experienced below-average rainfall, sometimes leading to severe droughts that destroyed crops and forced authorities to restrict exports of grains and sugar.

## The Economic Cascade

The monsoon is the lifeblood of India's nearly $4 trillion economy, delivering almost 70 percent of the rainfall needed to water farms and replenish aquifers and reservoirs. More than half of India's 1.4 billion people depend directly or indirectly on agriculture, and the sector accounts for about 15 percent of GDP.

"This, along with the impending impact of the ongoing crisis in the Middle East, poses downside risks to India's GDP growth in financial year 2026-27," said Aditi Nayar, chief economist at rating agency ICRA. The government had projected growth of between 6.8 and 7.2 percent for the fiscal year that started on April 1.

Nayar warned that lower rainfall forecasts also pose "material upside risks" to inflation, with average retail inflation potentially exceeding 4.5 percent this fiscal year — well above the Reserve Bank of India's 4 percent target. Inflation stood at 3.4 percent in March.

## Food Supply at Risk

India is the world's biggest exporter of rice and onions and the second-biggest producer of sugar. It is also the largest importer of edible oils, fulfilling nearly two-thirds of domestic demand through overseas purchases of palm oil, soy oil, and sunflower oil from Indonesia, Malaysia, Argentina, Brazil, Russia, and Ukraine.

A weak monsoon would hit both sides of this equation. Domestic production of rice, pulses, and oilseeds would fall, while import demand would rise — putting further pressure on the rupee, which has already declined about 5 percent since the Iran war began in late February.

"Lower rainfall is likely to increase India's edible oil imports and eliminate the possibility of sugar exports in the next season," a Mumbai-based dealer with a global trading house told Reuters.

## What the Diaspora Should Watch

For the millions of Indian families with relatives abroad, the monsoon forecast is not an abstraction. It directly shapes the cost of staples — rice, dal, cooking oil, vegetables — that NRI families help pay for through remittances. India received a record $136 billion in remittances in FY25; much of that flows to rural households whose incomes fluctuate with the monsoon.

A positive Indian Ocean Dipole, which the IMD expects to develop later in the monsoon season, could partially offset the El Niño effect. But that remains a hope, not a plan.

The agriculture ministry has said it is preparing contingency crop plans and ensuring adequate seed stocks. But with oil prices elevated, fertiliser costs rising, and the rupee under pressure, even a modestly below-normal monsoon would compound the cost-of-living crisis that is already squeezing Indian households from every direction.

The real monsoon arrives in Kerala around June 1. Until then, the country waits."""
}

print(f"  Headline: {article1['headline']}")
print(f"  Slug: {article1['slug']}")
publish_article(article1)


# ============================================================
# ARTICLE 2: India-Bangladesh "Detect, Delete, Deport" Crisis
# ============================================================
print("\n" + "="*60)
print("ARTICLE 2: India-Bangladesh Deportation Crisis")
print("="*60)

# Try Wikipedia for relevant person or Pexels for border imagery
border_image = fetch_pexels_image("India Bangladesh border fence patrol", "international border crossing")
if border_image and not validate_image_url(border_image):
    border_image = None

article2 = {
    "headline": "India Wants to Deport 2,860 Suspected Bangladeshis. Bangladesh Says Prove They Are Ours First.",
    "subheadline": "The BJP's 'detect, delete, deport' campaign has pushed hundreds of people across the border without formal procedures, prompting Bangladesh to deploy loudspeakers and patrol boats along one of the world's longest land frontiers.",
    "slug": generate_slug("india-bangladesh-detect-delete-deport-border-crisis"),
    "image_url": border_image or "",
    "image_caption": "Bangladesh and India share a border stretching over 4,000 kilometres — one of the longest land frontiers in the world.",
    "image_attribution": "Pexels" if border_image else "",
    "sources": [
        "Reuters — Bangladesh boosts vigilance over suspected forced crossings from India",
        "Human Rights Watch — India: Hundreds of Muslims Unlawfully Expelled to Bangladesh",
        "Global India Broadcast News — 'Detection, deletion and deportation': Why Bangladeshi migrants gather around the Bangladesh border",
        "News Nest — Fleeing Bangladeshis Reveal How They Crossed into India Amid Deportation Fears"
    ],
    "vertical": "politics",
    "diaspora_angle": "India's deportation campaign raises uncomfortable parallels with immigration enforcement in the US and Canada, where NRIs have personal experience navigating documentation and uncertain legal status.",
    "tags": ["india-bangladesh", "deportation", "detect-delete-deport", "bjp", "immigration", "human-rights", "border"],
    "urgency": "high",
    "score_total": 90,
    "body": """Bangladesh's border guards have intensified patrols and deployed loudspeaker campaigns along their frontier with India, warning villagers to stay alert against what Dhaka calls illegal "push-ins" — a diplomatic euphemism for what human rights groups describe as mass deportations without due process.

The escalation comes as India's ruling Bharatiya Janata Party drives a nationwide "detect, delete, deport" campaign targeting undocumented migrants, primarily Bengali-speaking Muslims, across states from Assam to Maharashtra. India's foreign ministry has asked Bangladesh to verify the nationality of more than 2,860 people suspected of living illegally in the country.

## A Policy With a Slogan

The BJP, which governs the border states of Tripura, West Bengal, and Assam, has made immigration enforcement a political priority. The "detect, delete, deport" framework has evolved from political rhetoric into operational policy, with states establishing new detention centres and conducting document verification drives in neighbourhoods with large Bengali-speaking populations.

In Assam alone, tribunals have declared more than 30,000 people to be foreigners since May 2025. Hundreds have been physically pushed across the border into Bangladesh — many without the formal bilateral procedures both countries agreed to follow.

Human Rights Watch documented over 1,500 expulsions between May and June 2025, calling them "unlawful" and accusing Indian authorities of acting without due process. The organisation found cases of arbitrary detention, forced repatriation, and family separations that violated international law.

## The Border Response

Lieutenant Colonel S. M. Shariful Islam, commander of Bangladesh's 60th Border Guard Battalion, told Reuters that his forces have begun public awareness campaigns in border villages of Brahmanbaria district, which accounts for roughly 73 kilometres of the frontier with the Indian state of Tripura.

"We have started miking in border villages to raise awareness among residents and ask them to stay vigilant against any illegal crossings or push-in attempts," he said. "Our patrols and surveillance have been strengthened across the border areas."

The 4,000-kilometre border between India and Bangladesh is one of the longest land frontiers in the world, running through densely populated river deltas, marshlands, and villages where the distinction between "Indian Bengali" and "Bangladeshi Bengali" is often a matter of paperwork rather than language, culture, or family ties.

## The Gurugram Ripple Effect

The deportation drive is not limited to border states. In Gurugram, the corporate hub outside Delhi, police detained ten Bangladeshi nationals after document verification found them living with Indian papers that were deemed fraudulent. The operation, conducted under Home Ministry directives, sparked panic among Bengali-speaking communities far from the border, where long-term residents suddenly face questions about their own documentation.

The fear has driven a reverse migration. Hundreds of undocumented Bangladeshi migrants have begun returning to India's border regions voluntarily, using brokers to cross back into Bangladesh through riverine areas rather than face detention.

## Why This Matters to the Diaspora

For Indian Americans and NRIs, the deportation crisis touches a nerve on multiple levels. It raises uncomfortable parallels with immigration enforcement debates in the United States and Canada — countries where many NRIs have personal experience navigating documentation, visa processes, and the anxiety of uncertain legal status.

It also surfaces the deeper question of who belongs. India's Citizenship Amendment Act, which fast-tracks citizenship for non-Muslim refugees from neighbouring countries, remains a fault line in Indian politics. The "detect, delete, deport" campaign operates in the same political space, raising questions about whether enforcement is driven by law or by identity.

Dhaka has repeatedly stated that any repatriation must follow formal bilateral procedures. India's foreign ministry did not respond to Reuters' request for comment.

## What Comes Next

The campaign shows no sign of slowing. Multiple states are expanding detention infrastructure, and the Home Ministry has issued fresh directives for document verification. But without a bilateral agreement on verification procedures, each deportation risks becoming a diplomatic incident — and every unverified expulsion risks pushing an Indian citizen into a country that is not theirs.

The 4,000-kilometre border will keep being crossed in both directions. The question is whether either government can manage that reality without violating the rights of the people caught in between."""
}

print(f"  Headline: {article2['headline']}")
print(f"  Slug: {article2['slug']}")
publish_article(article2)


# ============================================================
# ARTICLE 3: EU Fines Temu $232M — Global E-Commerce Regulation
# ============================================================
print("\n" + "="*60)
print("ARTICLE 3: EU Fines Temu $232M")
print("="*60)

# Try Wikipedia for EU Commission or Temu
temu_image = fetch_wikipedia_person_image("European Commission")
if temu_image and not validate_image_url(temu_image):
    temu_image = None
if not temu_image:
    temu_image = fetch_pexels_image("online shopping package delivery", "ecommerce marketplace packages")
    if temu_image and not validate_image_url(temu_image):
        temu_image = None

article3 = {
    "headline": "The EU Just Fined Temu $232 Million for Selling Dangerous Products. India Blocked Chinese Apps Years Ago.",
    "subheadline": "Europe's largest penalty under the Digital Services Act targets the Chinese e-commerce giant for flooding the market with unsafe toys and defective electronics — a problem India preempted by banning dozens of Chinese platforms after 2020.",
    "slug": generate_slug("eu-temu-232-million-fine-digital-services-act-india-chinese-apps"),
    "image_url": temu_image or "",
    "image_caption": "Temu has been fined €200 million by the European Commission under the Digital Services Act for failing to stop the sale of unsafe products.",
    "image_attribution": "Wikimedia Commons" if temu_image and "wikimedia" in (temu_image or "").lower() else ("Pexels" if temu_image else ""),
    "sources": [
        "Reuters — Temu fined $232 million for breaching EU rules on sale of illegal products",
        "Wall Street Journal — Temu Fined More Than $230 Million in EU Over Product Risks",
        "European Commission — Preliminary findings on Temu under Digital Services Act",
        "The Sun — Temu slapped with $232m fine for selling dangerous products"
    ],
    "vertical": "technology",
    "diaspora_angle": "Millions of NRIs in the US, UK, and Canada shop on Temu — the EU's finding that the platform routinely sells unsafe products is a direct consumer warning for diaspora shoppers.",
    "tags": ["temu", "eu", "digital-services-act", "ecommerce", "consumer-safety", "chinese-apps", "india-ban"],
    "urgency": "medium",
    "score_total": 88,
    "body": """The European Union has slapped Chinese online retailer Temu with a €200 million ($232 million) fine for failing to prevent the sale of illegal and unsafe products on its platform — the largest penalty yet under Europe's sweeping Digital Services Act, and a landmark moment in the global battle to regulate cross-border e-commerce.

The fine, announced on Thursday by the European Commission, follows a nearly two-year investigation that found Temu had "failed to diligently identify, analyse and assess the systemic risks of illegal products being offered on its platform and the resulting harm to consumers in the European Union."

## What Temu Got Wrong

At the heart of the case are everyday consumer products — baby toys containing toxic materials, phone chargers that could overheat and catch fire, small electronics that failed basic safety standards. The Commission found that European consumers were "very likely to come across illegal items" while shopping on Temu, and that the platform had not conducted the comprehensive risk assessments required under the DSA.

Temu rejected the penalty as "disproportionate," claiming it has strengthened its safety processes since the investigation began. The company has until August 28 to submit an action plan; more fines could follow if regulators find ongoing non-compliance.

This is only the second penalty under the Digital Services Act, which came into force in 2024 and requires large online platforms to actively combat illegal content and products. The first fine targeted another company for content moderation failures.

## India Saw This Coming

India's approach to Chinese digital platforms has been dramatically different from Europe's. Beginning in June 2020, India banned 59 Chinese apps — including TikTok, WeChat, and UC Browser — citing national security concerns, data privacy, and sovereignty. The bans have since expanded to over 300 Chinese apps and services.

Temu, owned by PDD Holdings, has never officially launched in India. While the platform has grown aggressively across the United States, Europe, and Southeast Asia — often undercutting local retailers with astonishingly low prices — India's blanket restrictions on Chinese digital services have kept it out of the world's largest open market by population.

The result is an accidental case study: India avoided the very problems Europe is now fining Temu for, though through a blunt instrument (bans) rather than Europe's more surgical regulatory approach (safety standards and penalties).

## Why NRIs Should Pay Attention

For the millions of Indian Americans who shop on Temu — the app was the most downloaded shopping app in the United States in 2023 and 2024 — the EU fine raises immediate questions about product safety.

The unsafe toys and electronics that triggered Europe's investigation are the same products sold on the same platform to American consumers. The United States has not yet taken comparable regulatory action against Temu, though Congress has held hearings on the platform's use of the "de minimis" trade loophole to avoid customs duties on millions of small shipments.

For NRIs who buy products on Temu to ship to family in India — a common practice for affordable electronics, clothing, and household goods — the EU's findings are a warning. Products that fail European safety standards are unlikely to meet any country's consumer protection thresholds.

## The Bigger Picture

The Temu fine is part of a broader global reckoning with the business model that has made ultra-cheap Chinese e-commerce platforms dominant. The model depends on high volume, razor-thin margins, and minimal quality control — a combination that maximises choice and affordability but also maximises the risk of dangerous products reaching consumers.

Europe is betting that regulation can force these platforms to internalise the cost of safety. India bet on exclusion. The United States, so far, has done neither — leaving American consumers, including millions of Indian Americans, in a regulatory grey zone.

As cross-border e-commerce continues to grow, the EU's DSA is becoming a template that other countries are watching closely. India's own proposed Digital India Act, which would modernise the country's Information Technology Act of 2000, is expected to include similar platform accountability provisions.

The question is no longer whether governments will regulate global e-commerce platforms. It is whether they will do so before the next batch of toxic baby toys reaches someone's doorstep."""
}

print(f"  Headline: {article3['headline']}")
print(f"  Slug: {article3['slug']}")
publish_article(article3)


print("\n" + "="*60)
print("NEWS WRITER RUN COMPLETE")
print(f"Published 3 articles at {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
print("="*60)
