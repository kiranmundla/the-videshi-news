#!/usr/bin/env python3
"""
Videshi Lifestyle-Health & Markets-Finance Writer
Run: 2026-06-05 18:00 UTC
Articles:
  1. India GDP 7.8% Q4 FY26 — strong backward data, but Iran war clouds FY27 (markets-finance)
  2. WHO: Unsafe food kills 1.5M/year, South-East Asia hardest hit (lifestyle-health)
  3. India heatwave: 56 dead, 25K heatstroke cases — NRI summer travel risks (lifestyle-health)
"""

import json, os, sys, time, subprocess, re, uuid
from datetime import datetime, timezone

# Load env
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
                os.environ[key.strip()] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import requests

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
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

def fetch_pexels_image(query):
    """Search Pexels for a relevant image using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=5&orientation=landscape'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0].get('src', {}).get('large2x') or photos[0].get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {r.status_code}, {content_type}, {content_length} bytes")
            return True
        # Try GET if HEAD fails (some servers don't support HEAD well)
        if r.status_code != 200:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, stream=True)
            content_type = r2.headers.get('Content-Type', '')
            content_length = int(r2.headers.get('Content-Length', 0))
            if r2.status_code == 200 and 'image' in content_type:
                # Read a bit to check size
                chunk = r2.raw.read(6000)
                if len(chunk) > 5000:
                    print(f"  ✓ Image validated via GET: {content_type}, {len(chunk)}+ bytes")
                    return True
        print(f"  ✗ Image validation failed: {r.status_code}, {content_type}, {content_length}")
        return False
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
        return False

def insert_article(article):
    """Insert article into Supabase."""
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": article["category"],
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": article.get("image_url", ""),
        "image_caption": article.get("image_caption", ""),
        "image_attribution": article.get("image_attribution", ""),
        "sources": json.dumps(article.get("sources", [])),
        "is_editorial": False
    }
    
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=payload,
            timeout=30
        )
        if r.status_code in (200, 201):
            result = r.json()
            article_id = result[0]["id"] if isinstance(result, list) and result else "unknown"
            print(f"  ✓ Published: {article['headline'][:60]}... (id: {article_id})")
            return True
        else:
            print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Insert error: {e}")
        return False

# ============================================================
# ARTICLE 1: Markets-Finance — India GDP 7.8% Q4 FY26
# ============================================================
print("\n=== Article 1: India GDP 7.8% (markets-finance) ===")

# Image sourcing
print("Sourcing image...")
# Try Wikipedia for RBI / India economy
img1_url = None
img1_caption = ""
img1_attribution = ""

# Try Wikimedia Commons for India economy / RBI
commons_results = fetch_wikimedia_commons_images("Reserve Bank of India building Mumbai")
time.sleep(1)
if commons_results:
    for r in commons_results:
        url = r.get("url") or r.get("original_url")
        if url and validate_image(url):
            img1_url = url
            img1_caption = "The Reserve Bank of India headquarters in Mumbai"
            img1_attribution = "Wikimedia Commons"
            break
        time.sleep(1)

if not img1_url:
    commons_results = fetch_wikimedia_commons_images("India GDP economy growth")
    time.sleep(1)
    if commons_results:
        for r in commons_results:
            url = r.get("url") or r.get("original_url")
            if url and validate_image(url):
                img1_url = url
                img1_caption = "India's economy continues to be among the world's fastest-growing"
                img1_attribution = "Wikimedia Commons"
                break
            time.sleep(1)

if not img1_url:
    img1_url = fetch_pexels_image("India economy financial district Mumbai")
    if img1_url and validate_image(img1_url):
        img1_caption = "India's financial district in Mumbai, hub of the country's economic activity"
        img1_attribution = "Pexels"
    else:
        img1_url = None

article1 = {
    "headline": "India's Economy Grew 7.8 Per Cent Last Quarter. The RBI Just Cut This Year's Forecast to 6.6 Per Cent. Here Is Why Both Numbers Matter for NRIs.",
    "subheadline": "Strong backward-looking GDP data masks a sharp slowdown ahead as the Iran war pushes oil past $96, the rupee slides 5 per cent, and $28 billion leaves Indian equities. New measures targeting diaspora deposits could draw $40 billion in relief.",
    "slug": "india-gdp-78-percent-q4-fy26-rbi-cuts-fy27-forecast-66-iran-war-nri-deposits-20260605",
    "category": "markets-finance",
    "image_url": img1_url or "",
    "image_caption": img1_caption,
    "image_attribution": img1_attribution,
    "sources": [
        "Reuters — India's GDP grows 7.8% in January-March on resilient farm, construction output (June 5, 2026)",
        "Reuters — India ramps up defence of faltering rupee after holding fire on rates (June 5, 2026)",
        "Morningstar — India's Economy Continues to Post Robust Growth Amid Mideast Energy Shock (June 5, 2026)",
        "The Hindu BusinessLine — FY26 GDP growth beats estimates to reach 7.7% (June 5, 2026)",
        "Reuters — India's measures to protect rupee seen drawing about $40 billion (June 5, 2026)"
    ],
    "body": """India's economy grew 7.8 per cent in the January–March quarter of FY26, comfortably beating the 7.2 per cent consensus forecast compiled by Reuters and capping a full-year expansion of 7.7 per cent — the strongest in two years. Hours later, the Reserve Bank of India cut its growth projection for the current fiscal year to 6.6 per cent from 6.9 per cent. For the roughly five million NRIs with money, property, or family in India, both numbers demand attention.

## The Backward-Looking Strength

The Q4 print was driven by resilient farm output, an 8.4 per cent jump in construction activity, and 7.1 per cent growth in private consumption. Manufacturing expanded 7.3 per cent, and gross value added — a cleaner measure that strips out volatile tax and subsidy swings — came in at 7.9 per cent. The full-year GDP of ₹323.12 lakh crore made India comfortably the world's fastest-growing large economy for the second consecutive year.

The government had initially estimated FY26 growth at 7.6 per cent in February. The upward revision to 7.7 per cent, combined with the October–December quarter being nudged up to 8.0 per cent from 7.8 per cent, suggests the domestic engine was running hotter than anyone measured at the time.

## The Forward-Looking Risk

But the numbers belong to a world that no longer exists. The U.S.–Iran conflict, now in its fourth month with no peace deal in sight, has pushed Brent crude to roughly $96 a barrel. India — the world's third-largest crude importer — is absorbing the shock through every layer of its economy: higher industrial input costs, rising food and transport inflation, and a rupee that has weakened more than 5 per cent this year, touching record lows near 96 to the dollar.

Foreign portfolio investors have pulled $28 billion out of Indian equities since the conflict escalated, making India one of the hardest-hit emerging markets by capital flight. The RBI acknowledged this reality on Friday by raising its inflation projection for FY27 to 5.1 per cent from 4.6 per cent while trimming growth expectations.

"Activity has already started slowing and will remain soft," said Alexandra Hermann Prasad, lead economist at Oxford Economics. "The RBI's dovish hold will cushion financing conditions, but not enough to prevent growth from undershooting."

## The Rate Decision

The central bank held its repo rate steady at 5.25 per cent, as widely expected. But Governor Sanjay Malhotra's language signalled a possible hawkish turn if inflation pressures deepen. With food and fuel prices climbing, a rate hike before year-end is now the base case for most economists, including Standard Chartered, which had called for an immediate 25-basis-point increase.

For NRIs with home loans in India or exposure to Indian fixed-income instruments, this is the pivotal signal. A hold preserves the status quo on EMIs and deposit rates for now. A hike later this year would push borrowing costs higher but also improve returns on NRI fixed deposits.

## The Rupee Rescue Package

Alongside the rate decision, India announced its most aggressive package of measures to defend the rupee in over a decade. The key provisions include scrapping capital gains tax on foreign investments in government bonds, offering concessional forex swaps for state-owned firms tapping dollar borrowings, and — most relevant for the diaspora — compensating banks for hedging costs on three-to-five-year foreign currency non-resident (FCNR) deposits.

Analysts at HDFC Bank, YES Bank, and Emkay Global estimate the combined measures could attract $40 billion to $50 billion in inflows over the next four months. "The combined impact could certainly help bridge the $40–50 billion gap on the balance of payments estimated for FY27," said Sakshi Gupta, principal economist at HDFC Bank.

## What NRIs Should Watch

**Remittances**: The rupee at 95–96 means every dollar remitted converts to more rupees than at any point in history. NRIs sending money to family in India are getting peak value, but this also signals stress in the Indian economy that could affect property values and local purchasing power.

**FCNR deposits**: The RBI's hedging subsidy makes FCNR deposits temporarily more attractive for banks to offer competitive rates. If your bank announces higher FCNR rates in the coming weeks, the RBI is footing part of the bill — a window that closes at September end.

**Equity exposure**: With $28 billion gone from Indian stocks and more outflows likely if oil stays elevated, current prices reflect genuine fear. For long-term NRI investors, the 7.7 per cent underlying growth rate suggests fundamentals remain strong even as the cyclical picture darkens.

The GDP data tells you India's economy was strong. The RBI's actions tell you the people running it are worried about what comes next. Both can be true at the same time."""
}

print(f"  Headline: {article1['headline'][:80]}...")
print(f"  Body words: {len(article1['body'].split())}")
insert_article(article1)

# ============================================================
# ARTICLE 2: Lifestyle-Health — WHO Unsafe Food Report
# ============================================================
print("\n=== Article 2: WHO Unsafe Food (lifestyle-health) ===")

# Image sourcing
print("Sourcing image...")
img2_url = None
img2_caption = ""
img2_attribution = ""

commons_results = fetch_wikimedia_commons_images("food safety inspection hygiene")
time.sleep(1)
if commons_results:
    for r in commons_results:
        url = r.get("url") or r.get("original_url")
        if url and validate_image(url):
            img2_url = url
            img2_caption = "Food safety inspection — the WHO says unsafe food causes 866 million illnesses annually"
            img2_attribution = "Wikimedia Commons"
            break
        time.sleep(1)

if not img2_url:
    commons_results = fetch_wikimedia_commons_images("street food market India food stall")
    time.sleep(1)
    if commons_results:
        for r in commons_results:
            url = r.get("url") or r.get("original_url")
            if url and validate_image(url):
                img2_url = url
                img2_caption = "A street food stall — the WHO finds South-East Asia bears the heaviest foodborne disease burden"
                img2_attribution = "Wikimedia Commons"
                break
            time.sleep(1)

if not img2_url:
    img2_url = fetch_pexels_image("food market street vendor cooking")
    if img2_url and validate_image(img2_url):
        img2_caption = "Street food vendors prepare meals — unsafe food causes 866 million illnesses a year globally"
        img2_attribution = "Pexels"
    else:
        img2_url = None

article2 = {
    "headline": "Unsafe Food Kills 1.5 Million People a Year. South-East Asia and Africa Bear Three Quarters of the Burden.",
    "subheadline": "A WHO report covering 194 countries finds that chemical contamination from arsenic and lead now causes 73 per cent of foodborne deaths, children under five face triple the risk, and the global productivity cost exceeds $300 billion annually. The diaspora implications are personal.",
    "slug": "who-unsafe-food-866-million-illnesses-south-east-asia-africa-chemical-lead-arsenic-diaspora-20260605",
    "category": "lifestyle-health",
    "image_url": img2_url or "",
    "image_caption": img2_caption,
    "image_attribution": img2_attribution,
    "sources": [
        "World Health Organization — Unsafe food causes 866 million illnesses and 1.5 million deaths annually, young children at highest risk (June 4, 2026)",
        "The Lancet Global Health — WHO estimates of the global burden of foodborne diseases 2000–2021 (June 2026)",
        "WHO — World Food Safety Day 2026: From burden to solutions – safe food everywhere"
    ],
    "body": """The World Health Organization released its most comprehensive assessment of global food safety on Wednesday, and the numbers should make every NRI planning a summer trip home pause before they eat. Unsafe food causes roughly 866 million illnesses and 1.5 million deaths every year, with South-East Asia and Africa accounting for nearly three quarters of all foodborne illnesses and 60 per cent of deaths.

The report, published in *The Lancet Global Health* ahead of World Food Safety Day on 7 June, assessed 42 major foodborne hazards across 194 countries from 2000 to 2021 — the broadest analysis the WHO has ever conducted. Its findings upend a common assumption about what makes contaminated food deadly.

## The Chemical Surprise

Most people picture food poisoning as a stomach bug. Bacteria and viruses do cause the vast majority of foodborne illnesses — roughly 860 million of the 866 million total. But chemical contamination is what actually kills. Chemical hazards accounted for a staggering 73 per cent of all foodborne deaths in 2021. Inorganic arsenic was responsible for 42 per cent of those deaths, lead for 31 per cent.

These are not exotic industrial pollutants. Arsenic enters food through contaminated groundwater used to irrigate rice paddies — a staple crop across South Asia. Lead accumulates in soil from decades of leaded petrol, industrial runoff, and old plumbing. Once these metals enter the food chain, they are often impossible to remove.

The health consequences are not limited to acute poisoning. Chronic exposure to arsenic and lead increases the risk of cardiovascular disease and cancers. Together, these two metals are linked to more than one million deaths in a single year. For South Asians — who consume more rice per capita than almost any other population and whose home regions have documented arsenic contamination in groundwater from West Bengal to Bangladesh — the relevance is direct.

## Children Bear the Worst of It

Children under five make up just 9 per cent of the global population but suffer nearly one third of all foodborne disease cases. The WHO found they face almost three times the risk of illness compared with older children and adults, with diarrhoeal diseases posing the greatest threat.

But the longer-term damage may be even more consequential. Methylmercury — found in fish and seafood — can cross the placental barrier and harm the developing brain. The WHO report documents lifelong neurological and developmental problems linked to childhood exposure. For diaspora families feeding young children during visits to India, or importing traditional foods that may not meet Western safety standards, these are not abstract risks.

## The Equity Gap

The geographic concentration of foodborne disease mirrors global inequality. Africa and South-East Asia together bear roughly 75 per cent of the global illness burden despite representing a smaller share of the world's population. Within India, the burden falls disproportionately on communities with limited access to clean water, sanitation, and refrigeration.

The economic toll is enormous. The WHO estimates that foodborne illness caused $310 billion in lost productivity in 2021 — time people spent sick instead of working. When adjusted for cost-of-living differences between countries, the figure rises to $647 billion.

"Food safety is not an abstract issue — it touches every meal, every family, every day," said WHO Director-General Tedros Adhanom Ghebreyesus. "For the first time, countries have their own data to see where the burden is highest."

## What the Diaspora Should Know

For the millions of NRIs who travel to India each summer, the report carries practical weight. Street food is a cornerstone of Indian culture and a highlight of any visit home. But the WHO data suggests that the risks are not evenly distributed: water quality, cold chain integrity, and pesticide regulation all vary dramatically between regions.

**Water and ice**: Contaminated water remains the single largest vector for biological foodborne hazards. Avoid ice from unknown sources, even in restaurants that appear clean.

**Rice and grains**: South Asian rice varieties have among the highest inorganic arsenic concentrations globally. Washing rice thoroughly and cooking in excess water (then draining) reduces arsenic by up to 60 per cent, according to prior research.

**Children's meals**: If you are travelling with children under five, the WHO data is unambiguous about their elevated risk. Stick to freshly cooked, hot food. Avoid raw salads, cut fruit from vendors, and unpasteurised dairy.

**Imported foods at home**: NRIs who import spices, pickles, or snacks from India should be aware that not all products meet the food safety standards of the country they live in. Lead contamination in spices — particularly turmeric — has been documented in FDA testing.

The WHO frames its report as a call for governments to invest in surveillance, regulation, and multisectoral collaboration. For individual families, the message is simpler: the food you love can still hurt you, and the youngest members of your family are the most vulnerable."""
}

print(f"  Headline: {article2['headline'][:80]}...")
print(f"  Body words: {len(article2['body'].split())}")
insert_article(article2)

# ============================================================
# ARTICLE 3: Lifestyle-Health — India Heatwave Deaths + NRI Travel
# ============================================================
print("\n=== Article 3: India Heatwave (lifestyle-health) ===")

# Image sourcing
print("Sourcing image...")
img3_url = None
img3_caption = ""
img3_attribution = ""

commons_results = fetch_wikimedia_commons_images("India heatwave summer heat")
time.sleep(1)
if commons_results:
    for r in commons_results:
        url = r.get("url") or r.get("original_url")
        if url and validate_image(url):
            img3_url = url
            img3_caption = "Extreme heat across northern India has killed dozens and hospitalised thousands"
            img3_attribution = "Wikimedia Commons"
            break
        time.sleep(1)

if not img3_url:
    commons_results = fetch_wikimedia_commons_images("heat wave India water summer")
    time.sleep(1)
    if commons_results:
        for r in commons_results:
            url = r.get("url") or r.get("original_url")
            if url and validate_image(url):
                img3_url = url
                img3_caption = "People seek relief from scorching temperatures in northern India"
                img3_attribution = "Wikimedia Commons"
                break
            time.sleep(1)

if not img3_url:
    img3_url = fetch_pexels_image("extreme heat sun scorching summer India")
    if img3_url and validate_image(img3_url):
        img3_caption = "Scorching temperatures across India have caused 25,000 suspected heatstroke cases since March"
        img3_attribution = "Pexels"
    else:
        img3_url = None

article3 = {
    "headline": "India's Heatwave Has Killed 56 People and Caused 25,000 Cases of Suspected Heatstroke Since March. If You Are Visiting This Summer, Read This.",
    "subheadline": "Thirty-four people died in a single district in Uttar Pradesh in two days — all over 60 with preexisting conditions. Temperatures have breached 42°C across northern India while power outages leave families without fans or running water. The diaspora's summer travel season has collided with a public health emergency.",
    "slug": "india-heatwave-56-dead-25000-heatstroke-cases-up-ballia-nri-summer-travel-risks-20260605",
    "category": "lifestyle-health",
    "image_url": img3_url or "",
    "image_caption": img3_caption,
    "image_attribution": img3_attribution,
    "sources": [
        "The Indian Eye — Heat wave kills 56 in India; 25,000 cases of suspected heatstroke registered from March-May (June 5, 2026)",
        "Associated Press — Doctors advise people over 60 to stay indoors as India's northern state swelters in extreme heat (June 4, 2026)",
        "Outlook Business — How Parametric Insurance Is Emerging as a Safety Net Against Heatwaves (June 1, 2026)",
        "India Meteorological Department — Heatwave advisory data, June 2026"
    ],
    "body": """Fifty-six people have died from heat-related causes in India since March, and 25,000 cases of suspected heatstroke have been registered across the country from March through May, according to official data released this week. For the millions of NRIs who travel to India every summer with elderly parents, young children, and school-age kids in tow, this is not a weather story. It is a medical one.

The deadliest cluster occurred in Ballia district, Uttar Pradesh, where 34 people died in just two days — 23 on Thursday and 11 on Friday. Every single victim was over 60 years old and had preexisting health conditions that worsened in the extreme heat. Heart attacks, brain strokes, and severe diarrhoea were the primary causes of death, according to Ballia's Chief Medical Officer Jayant Kumar.

Ballia recorded a maximum temperature of 42.2°C (108°F) on Friday — 4.7°C above normal. But this is not an outlier. Parts of Madhya Pradesh, Rajasthan, Uttar Pradesh, and Haryana have seen temperatures soar past 45°C (113°F) in recent weeks. The India Meteorological Department has issued heatwave and severe heatwave warnings across northern, central, and eastern India.

## The Nighttime Problem

What makes this summer's heat especially dangerous is not just the daytime peaks — it is the loss of nighttime cooling. The IMD reports that India's average nighttime temperatures are rising by approximately 0.21°C per decade. In urban areas with dense concrete construction, temperatures barely drop after sunset.

This matters because the human body relies on cooler nights to recover from daytime heat stress. When nighttime temperatures stay elevated, the body accumulates stress over consecutive days, leading to chronic heat exhaustion that can trigger organ failure in vulnerable individuals — particularly the elderly, young children, and anyone with cardiovascular or kidney conditions.

The problem is compounded by power outages. Uttar Pradesh, India's most populous state with over 240 million people, has experienced widespread electricity failures, leaving families without fans, air conditioners, or running water. Protests have broken out across the state. Chief Minister Yogi Adityanath issued a statement urging citizens to use electricity judiciously — cold comfort for families in villages where the grid has been down for hours.

## The Scale of the Crisis

A study by the India Energy and Climate Centre at the University of California, Berkeley estimates that a single day of extreme heat causes approximately 3,400 excess deaths nationally. A five-day heatwave causes nearly 30,000. These figures count deaths above what would normally be expected — meaning the official toll of 56 almost certainly understates the true impact.

The World Bank has warned that heat stress could cost India up to 4.5 per cent of GDP by 2030 through reduced working hours, infrastructure damage, and direct productivity losses. India's electricity demand has already crossed an unprecedented 270 gigawatts during recent peak heat days, straining a grid that was not built for this load.

## What NRI Families Should Know Before Travelling

The diaspora's summer travel season — June through August, aligned with American and British school holidays — coincides directly with India's most dangerous heat period. Here is what medical professionals and public health officials are advising:

**Elderly relatives**: If your parents or grandparents are over 60 and living in northern or central India, the Ballia deaths are a direct warning. Doctors are advising all people over 60 to stay indoors between 11 AM and 4 PM. If your relatives lack reliable air conditioning or uninterrupted power, this is not a lifestyle inconvenience — it is a survival risk. Consider whether a visit during peak heat is wise, or whether you can time your travel for September.

**Children under five**: Young children are disproportionately vulnerable to heat because their bodies regulate temperature less efficiently than adults. Keep them hydrated with oral rehydration solution, not just water. Avoid outdoor activities during peak hours. Watch for warning signs: irritability, rapid breathing, hot dry skin, and refusal to drink.

**Hydration and diet**: Drink before you are thirsty. The traditional Indian approach of *nimbu pani* (lemon water with salt and sugar) is medically sound — it replaces both electrolytes and fluids. Avoid alcohol, caffeine, and heavy meals during peak heat hours. Fresh curd, buttermilk, and watermelon are not just cultural staples — they are evidence-based cooling strategies.

**Power outages and planning**: If you are staying in a city or town with unreliable electricity, pack a battery-operated fan, ensure you have access to bottled water, and identify the nearest hospital with a dedicated heat stroke ward. Many state governments have set these up, but they are often overwhelmed during peak events.

**Travel timing**: If your itinerary is flexible, the medical advice is clear. Avoid northern India in June and early July. Coastal and southern destinations — Kerala, Goa, Karnataka — are typically cooler and have more reliable infrastructure. If you must be in the north, travel during early morning or evening hours and rest indoors during the day.

## A Structural Problem

India's heatwave crisis is not an anomaly. It is a structural consequence of climate change, urbanisation, and infrastructure that has not kept pace with rising temperatures. The country created South Asia's first heat action plan after a deadly 2010 heatwave in Ahmedabad — a programme that saves an estimated 1,190 lives per year. But coverage remains patchy, and enforcement is inconsistent.

For NRIs, the emotional pull of summer in India — family weddings, temple visits, the mango season — is powerful. But this year, the data is asking you to plan differently. Check the IMD's heatwave forecasts before you book. Talk to your relatives about their cooling infrastructure. And if someone over 60 or under five is in your travel party, treat the heat as a medical condition, not a weather complaint."""
}

print(f"  Headline: {article3['headline'][:80]}...")
print(f"  Body words: {len(article3['body'].split())}")
insert_article(article3)

print("\n=== Writer run complete ===")
