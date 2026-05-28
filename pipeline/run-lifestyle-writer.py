#!/usr/bin/env python3
"""
Lifestyle-Health + Markets-Finance writer for The Videshi
Scheduled run: 2026-05-28
Articles:
1. Ultra-processed foods linked to 65% higher cardiovascular death (lifestyle-health)
2. Super El Niño threatens India's monsoon, food prices, and your family's grocery bills (markets-finance)
"""

import json, os, sys, uuid, requests, urllib.parse, re
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
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
    """Fetch an image from Pexels using curl (not urllib, which gets 403)."""
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for p in photos:
                url = p.get('src', {}).get('large2x') or p.get('src', {}).get('large')
                if url:
                    # Verify it's > 5KB
                    head = requests.head(url, timeout=10)
                    cl = int(head.headers.get('Content-Length', 0))
                    ct = head.headers.get('Content-Type', '')
                    if cl > 5000 and 'image' in ct:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=30, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Image download failed or too small: {r.status_code}, {len(r.content)} bytes")
            return None

        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            content_type = 'image/jpeg'

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': content_type,
            'x-upsert': 'true'
        }
        resp = requests.post(upload_url, data=r.content, headers=upload_headers, timeout=30)
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

def publish_article(article):
    """Insert article into Supabase."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    payload = {
        'id': art_id,
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': article['category'],
        'vertical': article['category'],
        'status': 'published',
        'published_at': now,
        'created_at': now,
        'sources': json.dumps(article['sources']),
        'tags': article.get('tags', []),
        'image_url': article.get('image_url'),
        'image_caption': article.get('image_caption'),
        'image_attribution': article.get('image_attribution'),
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        returned_id = result[0]['id'] if isinstance(result, list) and result else art_id
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {returned_id})")
        return returned_id
    else:
        print(f"  ✗ Publish failed: {r.status_code} {r.text[:300]}")
        return None

# ============================================================
# ARTICLE 1: Ultra-Processed Foods and Cardiovascular Death
# ============================================================

print("\n=== Article 1: Ultra-Processed Foods ===")

article1 = {
    'headline': "European Cardiologists Now Say Ultra-Processed Food Is a Clinical Risk Factor — Like Smoking. Indian-Americans Eat More of It Every Year They Live Here.",
    'subheadline': "A European Society of Cardiology consensus links UPFs to 65 per cent higher cardiovascular mortality. The traditional Indian kitchen was always the answer.",
    'slug': 'ultra-processed-food-cardiovascular-death-esc-consensus-indian-american-diet-shift-20260528',
    'category': 'lifestyle-health',
    'sources': [
        {"name": "European Heart Journal / ESC Consensus Statement", "url": "https://academic.oup.com/eurheartj"},
        {"name": "NaturalNews / ESC Congress Report", "url": "https://www.newstarget.com/2026-05-23-ultra-processed-food-consumption-risk-cardiovascular-health.html"},
        {"name": "Frontiers in Nutrition — UPFs and Accelerated Aging", "url": "https://www.frontiersin.org"},
        {"name": "The Lancet — UPF and Multimorbidity", "url": "https://www.thelancet.com"}
    ],
    'body': """The European Society of Cardiology has done something no medical body has done before. In a consensus statement published in the *European Heart Journal*, a multidisciplinary team of cardiologists and nutrition researchers declared that ultra-processed foods should be treated as a clinical risk factor for cardiovascular disease — the same category that includes smoking, high blood pressure, and physical inactivity.

The numbers are stark. Adults who consume the highest amounts of ultra-processed foods face a 65 per cent higher risk of dying from cardiovascular disease compared to those who eat the least. That finding held after researchers adjusted for smoking, obesity, socioeconomic status, and exercise habits. The processing itself — not the associated lifestyle — appears to be what drives the damage.

## What Counts as Ultra-Processed

The ESC statement defines ultra-processed foods as industrial formulations made from substances derived from foods and additives, with little or no intact food remaining. The list is longer than most people expect: flavoured yogurt, whole grain crackers, protein bars, oat milk, deli meats, breakfast cereals, instant noodles, soft drinks, packaged bread, frozen meals, and most fast food.

In the Netherlands, ultra-processed foods now account for 61 per cent of daily calories. In the United Kingdom, 54 per cent. In the United States, the figure hovers around 58 per cent. These are not outliers — they are the norm in wealthy nations, and India's urban centres are catching up fast.

## The Indian-American Dietary Shift

This is where the data becomes personal for the diaspora. The first generation arrives with a kitchen vocabulary that is inherently minimally processed: dal, sabzi, roti, rice, raita, pickles made from whole ingredients. There are no emulsifiers in your mother's chana masala. No maltodextrin in her sambar.

But study after study — including the MASALA cohort, the largest longitudinal study of South Asian cardiovascular health in America — shows that dietary acculturation is real and accelerating. The longer an Indian family lives in the United States, the more ultra-processed food enters their diet. The kids grow up on Goldfish and Lunchables. The adults swap home-cooked dals for protein shakes and meal-replacement bars. Weekend chai gives way to Starbucks Frappuccinos.

The ESC consensus found that ultra-processed foods trigger damage through multiple biological pathways simultaneously: gut microbiome disruption, systemic inflammation, hormonal dysregulation, and the promotion of obesity, hypertension, and insulin resistance. For South Asians — who already carry a disproportionate burden of metabolic disease and cardiovascular risk at lower body weights — the compounding effect is particularly dangerous.

## The Paradox of "Healthy" Processed Foods

One of the most striking findings in the ESC report is that foods marketed as healthy are frequently ultra-processed. The protein cookie your trainer recommended. The probiotic yogurt drink. The organic granola bar. The plant-based meat substitute.

Researchers found that the body processes a food made from isolated soy protein, maltodextrin, and natural flavours very differently from how it processes whole foods like eggs, almonds, or an apple. The nutrient label might look acceptable. The ingredient list tells a different story.

This challenges the entire framework of how most Indian-Americans think about food in America. The instinct is to read the calories, check the protein, look for "organic" or "whole grain" on the label. The ESC consensus says none of that matters as much as a simpler question: how many steps did this food go through between the farm and your plate?

## What the Doctors Say to Do

The ESC now recommends that physicians screen patients for ultra-processed food intake as part of routine cardiovascular risk assessment — the same way they check blood pressure and cholesterol. The practical advice is unglamorous but effective: swap one or two ultra-processed items per day for minimally processed alternatives. An apple instead of a snack bar. A handful of almonds instead of protein chips. Dal and rice instead of a frozen biryani.

A 2024 systematic review of nearly 10 million participants found that higher ultra-processed food consumption was directly associated with increased risk of obesity, heart disease, cancer, cognitive decline, and premature death. The ESC consensus builds on that evidence with clinical authority: this is now a formal risk factor, not a dietary preference.

## Your Mother Was Right

The traditional Indian kitchen — not the one that Instagram influencers recreate with avocado toast and turmeric lattes, but the one where your grandmother ground her own masalas and pressure-cooked dal from dried lentils — was always optimised for minimal processing. Whole spices. Fresh vegetables. Legumes cooked from scratch. Fermented foods like dahi and idli batter. Rice that came in a sack, not a microwaveable pouch.

The ESC consensus does not name the Indian kitchen by name. But the description of what protects against cardiovascular death — whole, minimally processed foods, prepared at home from recognisable ingredients — is a clinical endorsement of what Indian families have done for centuries.

The data is in. Ultra-processed food is not just unhealthy. It is now, officially, a clinical risk factor for dying of heart disease. The further the diaspora drifts from its own food traditions, the higher the price it pays.

The simplest thing you can do this week is cook one more meal from scratch than you did last week. Your grandmother would approve. So would the European Society of Cardiology."""
}

# Image sourcing — Pexels for concept article (no specific person)
img_url = fetch_pexels_image("Indian home cooking traditional kitchen dal", "traditional Indian food cooking spices")
if img_url:
    filename = f"{article1['slug']}.jpg"
    final_url = upload_image_to_supabase(img_url, filename)
    if final_url:
        article1['image_url'] = final_url
        article1['image_caption'] = "The traditional Indian kitchen — dal, sabzi, whole spices — is inherently minimally processed. European cardiologists now say that matters more than calorie counts."
        article1['image_attribution'] = "Pexels"

art1_id = publish_article(article1)

# ============================================================
# ARTICLE 2: Super El Niño, Monsoon, Food Prices (markets-finance)
# ============================================================

print("\n=== Article 2: El Niño + Monsoon + Food Inflation ===")

article2 = {
    'headline': "A Super El Niño Is Forming. India's Monsoon Is Already Forecast Below Normal. Your Family's Grocery Bill Back Home Is About to Change.",
    'subheadline': "NOAA says there is a 67 per cent chance of a Super El Niño. Citi warns food prices are skewed to the upside. The RBI just did a $5 billion emergency swap. Here is what it means for NRI money.",
    'slug': 'super-el-nino-india-monsoon-food-inflation-rbi-swap-nri-money-20260528',
    'category': 'markets-finance',
    'sources': [
        {"name": "NOAA — El Niño Forecast", "url": "https://www.climate.gov"},
        {"name": "Citi Research — Food Inflation Risk Report", "url": "https://www.chinimandi.com"},
        {"name": "Reuters — RBI $5 Billion FX Swap", "url": "https://www.reuters.com"},
        {"name": "SBI Research — Weather and Inflation Risks", "url": "https://www.thehindubusinessline.com"},
        {"name": "IMD — Below Normal Monsoon Forecast", "url": "https://mausam.imd.gov.in"},
        {"name": "Skymet Weather — El Niño Monsoon Analysis", "url": "https://www.skymetweather.com"}
    ],
    'body': """Three things are converging on India's economy at the same time, and all of them point in the same direction: higher food prices, a weaker rupee, and tighter monetary policy. If you send money home, buy property in India, or simply call your parents every week and hear about the price of onions, this is the story you need to understand.

## The El Niño

The US National Oceanic and Atmospheric Administration now puts the probability of an El Niño event emerging between May and July at 82 per cent. More alarming, there is a 67 per cent chance it becomes a "Super El Niño" — the kind of event that last occurred in 2015-16 and 2023-24, bringing record heat, crop failures, and flooding to different parts of the world simultaneously.

India's meteorological department has already forecast a below-normal monsoon season. El Niño years in India historically mean less total rainfall — the Indian Institute of Tropical Meteorology estimates 10 to 15 per cent deficits — with paradoxically more extreme rainfall events when it does rain. Sixty per cent of El Niño years since 1951 have produced below-average monsoon rainfall.

The monsoon waters roughly 52 per cent of India's net sown area. It drives the kharif crop — rice, sugarcane, cotton, pulses, oilseeds. When the monsoon fails, food prices rise. When food prices rise in India, everything else follows.

## The Food Price Signal

Citi Research published a report this month warning that agricultural price risks are "heavily skewed to the upside over the next six to twelve months." The bank identified two simultaneous supply shocks: El Niño weather disruptions and the prolonged closure of the Strait of Hormuz, which has sent energy costs spiralling and disrupted fertiliser supply chains.

Sugar, coffee, and cocoa are the most exposed commodities. India is the world's second-largest sugar producer; a weak monsoon in Maharashtra — which produces roughly a third of the country's sugar — would tighten global supply. Maharashtra has already begun drought preparedness measures for the kharif season.

But the bigger worry for Indian households is rice and pulses. Rice production requires predictable, sustained monsoon rainfall. A 10 per cent shortfall in monsoon precipitation can reduce rice output by 5 to 8 per cent. Pulse crops — the protein backbone of vegetarian India — are even more sensitive to drought stress.

An SBI Research report published this month connected the dots explicitly: El Niño, combined with war-related energy disruptions and trade route closures, creates a perfect storm for Indian inflation. The State Bank's economists warned that food inflation could push the RBI into a tighter monetary stance at exactly the wrong time for growth.

## The RBI's Emergency Response

The Reserve Bank of India is not waiting for the monsoon to fail. On Tuesday, the RBI executed a $5 billion three-year dollar-rupee buy-sell swap — essentially injecting rupees into the banking system while absorbing dollars. The auction drew $9.8 billion in bids, nearly double the amount on offer, signalling intense demand from banks desperate for rupee liquidity.

The swap comes as the rupee has fallen to consecutive record lows, touching 96.96 per dollar last week before recovering to around 95.50 on the back of central bank intervention. Foreign investors have pulled $24.3 billion out of Indian equities in 2026 so far, surpassing the record annual outflows of 2025.

Zerodha founder Nithin Kamath called it bluntly: India faces a "terrible year ahead." His analysis centres on the collision of weak monsoons, high oil prices from the Iran conflict, and the RBI being forced into rate hikes to defend the rupee and contain food inflation. Goldman Sachs now forecasts 50 basis points of rate hikes from the RBI, alongside 100 basis points in the Philippines and 50 in Indonesia.

## What This Means for NRI Money

**Remittances.** If you send dollars to India, the weak rupee means your money goes further — for now. But if the RBI is forced to hike rates aggressively, the rupee could stabilise or strengthen later in the year, reducing the advantage. The window for locking in favourable exchange rates on large transfers may be narrower than it looks.

**FCNR deposits.** The RBI is already dusting off its 2013 playbook — NRI bonds, FCNR deposit schemes, emergency swaps — to attract dollar inflows. If history repeats, NRI deposit rates will rise, making Indian fixed deposits more attractive for dollar-earners. Watch for announcements in the next 30 to 60 days.

**Property.** If you are buying in India, the weak rupee is a tailwind. But rising interest rates could cool the domestic property market, creating a buyer's market for NRIs who can pay in dollars. Timing matters: buying before rate hikes fully price in gives you both the currency advantage and pre-correction pricing.

**Equities.** Indian markets are closed today for Eid al-Adha. When they reopen, June is expected to be a stock-picker's market. Market-wide derivatives rollover stood at 94.2 per cent in the May series, outperforming three-month and six-month averages. Small-caps and mid-caps have risen 3 per cent this year while the Nifty 50 has fallen 8.5 per cent — the divergence suggests money is moving into specific sectors rather than fleeing entirely.

**Grocery bills back home.** Call your parents. Ask about onion prices, dal prices, cooking oil. If El Niño hits as forecast, the kharif season will underperform, and winter staples will get expensive by October. Families on fixed incomes — retired parents, in particular — will feel it first. The time to have that conversation about adjusting monthly support is before prices spike, not after.

## The Bottom Line

India is heading into monsoon season with three headwinds that individually would be manageable but together create genuine stress: a potential Super El Niño, a three-month-old war that has sent oil above $94, and a currency under pressure from $24 billion in foreign outflows. The RBI has tools — and it is using them aggressively — but it cannot make it rain.

For NRIs, the practical move is to pay attention to three numbers over the next 60 days: the El Niño index (ONI), the rupee-dollar rate, and the RBI repo rate. Together, they will tell you whether this is a buying opportunity or a storm to weather. Either way, it is not a year to look away."""
}

# Image sourcing for El Niño article
img_url = fetch_pexels_image("India monsoon rain farming crops", "Indian agriculture drought dry field")
if img_url:
    filename = f"{article2['slug']}.jpg"
    final_url = upload_image_to_supabase(img_url, filename)
    if final_url:
        article2['image_url'] = final_url
        article2['image_caption'] = "India's monsoon waters 52 per cent of its farmland. A Super El Niño threatens the kharif crop — and the grocery bills of 1.4 billion people."
        article2['image_attribution'] = "Pexels"

art2_id = publish_article(article2)

# ============================================================
# Summary
# ============================================================
print("\n=== Run Summary ===")
print(f"Article 1 (lifestyle-health): {'✓ ' + art1_id if art1_id else '✗ FAILED'}")
print(f"Article 2 (markets-finance): {'✓ ' + art2_id if art2_id else '✗ FAILED'}")
print("Done.")
