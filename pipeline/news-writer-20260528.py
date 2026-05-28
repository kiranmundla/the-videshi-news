#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-28)
Generates 3 news articles with proper images and publishes to Supabase.
"""

import json
import os
import subprocess
import uuid
import re
import time
from datetime import datetime, timezone

# --- Load environment ---
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# --- Wikipedia person image ---
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', 'User-Agent: TheVideshi/1.0 (thevideshi.com)',
             f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            img = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


# --- Pexels image ---
def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels. Returns URL or None."""
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_API_KEY}',
                 f'https://api.pexels.com/v1/search?query={q}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                photos = data.get('photos', [])
                if photos:
                    url = photos[0].get('src', {}).get('large2x') or photos[0].get('src', {}).get('original')
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


# --- Upload image to Supabase storage ---
def upload_image_to_supabase(image_url, filename):
    """Download image from URL and upload to Supabase storage. Returns public URL."""
    tmp_path = f'/tmp/{filename}'
    try:
        # Download
        dl = subprocess.run(
            ['curl', '-sS', '-L', '-o', tmp_path, '-H', 'User-Agent: TheVideshi/1.0 (thevideshi.com)', image_url],
            capture_output=True, text=True, timeout=30
        )
        if dl.returncode != 0:
            print(f"  ⚠ Download failed for {image_url[:60]}")
            return None

        # Check file size
        size = os.path.getsize(tmp_path)
        if size < 5000:
            print(f"  ⚠ Image too small ({size} bytes), skipping")
            return None

        # Upload to Supabase storage
        upload_url = f'{SUPABASE_URL}/storage/v1/object/article-images/{filename}'
        up = subprocess.run(
            ['curl', '-sS', '-X', 'POST',
             '-H', f'Authorization: Bearer {SUPABASE_KEY}',
             '-H', 'Content-Type: image/jpeg',
             '-H', 'x-upsert: true',
             '--data-binary', f'@{tmp_path}',
             upload_url],
            capture_output=True, text=True, timeout=30
        )
        if up.returncode == 0:
            pub_url = f'{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}'
            print(f"  ✓ Uploaded to Supabase: {pub_url[:80]}")
            return pub_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    return None


# --- Insert article ---
def insert_article(article):
    """Insert article into Supabase p2_articles table."""
    payload = json.dumps(article)
    result = subprocess.run(
        ['curl', '-sS', '-X', 'POST',
         f'{SUPABASE_URL}/rest/v1/p2_articles',
         '-H', f'apikey: {SUPABASE_KEY}',
         '-H', f'Authorization: Bearer {SUPABASE_KEY}',
         '-H', 'Content-Type: application/json',
         '-H', 'Prefer: return=representation',
         '-d', payload],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        try:
            resp = json.loads(result.stdout)
            if isinstance(resp, list) and len(resp) > 0:
                art_id = resp[0].get('id')
                print(f"  ✓ Published: {article['headline'][:60]}... (id: {art_id})")
                return art_id
            elif isinstance(resp, dict) and resp.get('message'):
                print(f"  ✗ Error: {resp.get('message')}")
                return None
        except json.JSONDecodeError:
            print(f"  ✗ Response parse error: {result.stdout[:200]}")
    else:
        print(f"  ✗ curl error: {result.stderr[:200]}")
    return None


# ===================================================================
# ARTICLE 1: India's Basmati Rice Exports
# ===================================================================

def write_article_1():
    print("\n=== ARTICLE 1: Basmati Rice Exports ===")

    slug = "india-basmati-rice-exports-crash-iran-war-gulf-trade-routes-20260528"
    headline = "India's Basmati Rice Exports Just Crashed 27 Percent. The Iran War Has Choked Every Gulf Trade Route."
    subheadline = "Four hundred thousand tonnes of premium basmati are stuck at Indian ports. Iran, Iraq, Saudi Arabia, and Qatar have all but stopped placing new orders."

    body = """India's rice export machine — the largest in the world, accounting for more than 40 percent of global shipments — is seizing up. And the damage is concentrated in exactly the market segment that matters most to Indian exporters and Gulf-based consumers alike: basmati.

## The Numbers Are Stark

India's basmati rice exports fell 27 percent in April 2026 compared to the same month last year, according to data from India's Directorate General of Commercial Intelligence and Statistics. For the January-to-April period, total rice exports slipped 1.3 percent year-on-year to 8.39 million metric tons. But the headline figure masks a sharper divergence: basmati shipments dropped 7 percent to 2.3 million tons, while cheaper non-basmati varieties edged up slightly to 6.09 million tons.

The culprit is geography. India's premium basmati rice goes overwhelmingly to Gulf markets — Saudi Arabia, Iran, Iraq, Qatar, and the United Arab Emirates. These are precisely the markets that the three-month-old Iran war has made nearly impossible to serve reliably.

## Four Hundred Thousand Tonnes Stuck at Port

The Strait of Hormuz, through which roughly a fifth of the world's oil and a significant share of Indian agricultural exports pass, has been disrupted since U.S.-Israeli airstrikes on Iran began on February 28. Shipping insurance premiums have spiked. Freight rates on India-Gulf routes have doubled in some cases. And cargo vessels carrying basmati rice to Iran, Iraq, Qatar, and Saudi Arabia remain stranded in transit or anchored at Indian ports waiting for clearance.

An estimated 400,000 metric tonnes of basmati rice are backed up at ports, according to industry reports. Exporters in Karnal, Haryana — the heart of India's basmati belt — describe a market in paralysis. New deals have effectively stalled.

"No buyer in the Gulf is placing fresh orders," said one New Delhi-based exporter who spoke to Reuters on condition of anonymity. "Shipments are expected to remain below typical levels until the war ends."

## The Gulf Connection Runs Deep

Iran was India's largest basmati buyer until last year, when Saudi Arabia overtook it. Together with Iraq and the UAE, these four markets absorb the bulk of India's $5 billion annual basmati trade. The disruption is not just a trade statistic — it is a kitchen-table reality for millions of families across the Gulf, including the roughly 9 million Indians living in the region.

For NRIs in Dubai, Riyadh, Doha, and Kuwait City, basmati rice is a staple that connects them to home. Rising prices and intermittent availability at Gulf supermarkets are a tangible reminder that the war is not just a geopolitical abstraction but a daily grocery problem.

## Domestic Prices Are Falling — But That Is Not Good News

Paradoxically, the export crunch is pushing domestic basmati prices down. Indian rice prices have fallen more than 5 percent this year, squeezed by a record harvest on one side and collapsing Gulf demand on the other. Farmers in Punjab, Haryana, and western Uttar Pradesh — who planted basmati expecting export-driven premiums — are being hit hardest.

The All India Rice Exporters Association has urged the government to intervene with freight subsidies and alternative market development. Pakistan, which competes directly in the global basmati market, is watching closely. Any prolonged Indian absence from Gulf shelves could open a window for Pakistani exporters to fill.

## What Comes Next

The Iran war shows no signs of a quick resolution. While a draft framework for a U.S.-Iran memorandum of understanding has surfaced — including a plan to restore commercial shipping through Hormuz within 30 days — Trump dismissed the reported deal on Thursday, and fresh air strikes between the two sides this week have further dimmed prospects for de-escalation.

For India's rice industry, the math is grim. The basmati export season runs roughly from October to March, and the current disruption is eating into what should be peak shipping months. If the war drags into the monsoon season, when domestic logistics slow anyway, the compounding effect on exports could be severe.

India ships more rice than Thailand, Vietnam, Myanmar, and Pakistan combined. When that pipeline breaks, the world's food trade feels it — and the Gulf's Indian kitchens feel it first.

*Sources: Reuters, Directorate General of Commercial Intelligence and Statistics (India), All India Rice Exporters Association, Rural Voice*"""

    # Image: Try Pexels for basmati rice fields
    print("  Sourcing image...")
    img_url = fetch_pexels_image("basmati rice field India harvest", "rice paddy field green")
    final_image = None
    if img_url:
        final_image = upload_image_to_supabase(img_url, f"{slug}.jpg")

    article = {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'news',
        'vertical': 'news',
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'image_url': final_image,
        'image_attribution': 'Pexels' if final_image else None,
        'image_caption': 'India\'s basmati rice exports to Gulf markets have crashed as the Iran war disrupts Strait of Hormuz shipping routes',
        'sources': json.dumps(['Reuters', 'Directorate General of Commercial Intelligence and Statistics', 'Rural Voice', 'All India Rice Exporters Association']),
        'tags': ['rice exports', 'basmati', 'Iran war', 'Gulf trade', 'agriculture'],
        'score_total': 82,
    }

    return insert_article(article)


# ===================================================================
# ARTICLE 2: India-Canada Free Trade Deal
# ===================================================================

def write_article_2():
    print("\n=== ARTICLE 2: India-Canada Trade Deal ===")

    slug = "india-canada-cepa-free-trade-deal-50-billion-goyal-carney-20260528"
    headline = "India and Canada Are Racing to Close a Free Trade Deal by December. The Target Is $50 Billion."
    subheadline = "Commerce Minister Piyush Goyal and Canadian PM Mark Carney call the CEPA a 'game changer.' The third round of negotiations is underway in Ottawa this week."

    # Try Wikipedia for Piyush Goyal and Mark Carney
    print("  Sourcing images...")
    img_url = fetch_wikipedia_person_image("Piyush Goyal")
    if not img_url:
        img_url = fetch_wikipedia_person_image("Mark Carney")
    if not img_url:
        img_url = fetch_pexels_image("India Canada trade diplomacy", "international trade agreement handshake")

    final_image = None
    if img_url:
        final_image = upload_image_to_supabase(img_url, f"{slug}.jpg")

    body = """Two years ago, India and Canada were barely speaking. A diplomatic crisis over the assassination of Sikh separatist leader Hardeep Singh Nijjar in British Columbia in June 2023 had frozen relations, expelled diplomats, and made a trade deal unthinkable. Now, Commerce Minister Piyush Goyal is in Ottawa, sitting across the table from Canada's Trade Minister Maninder Sidhu, and both governments are publicly racing to close a Comprehensive Economic Partnership Agreement by December.

## The Stakes Are Enormous

The headline number is $50 billion — three times the current bilateral trade of roughly $17 billion. India and Canada want to reach that target by 2030, and the CEPA is the vehicle to get there.

The third round of negotiations is underway in Ottawa from May 25 to 29, with India's chief negotiator, Joint Secretary Brij Mohan Mishra, leading the Indian delegation. The talks cover goods, services, investments, intellectual property, and government procurement — the full architecture of a modern free trade agreement.

"Our prime ministers have tasked us not only with completing the free trade agreement with a comprehensive outlook before the end of this year or earlier," Goyal said at a joint press appearance with Sidhu on May 25, "but also with tripling our trade."

Canadian Prime Minister Mark Carney was even more direct. "We're negotiating a free trade deal with India," he wrote on social media after meeting Goyal. "This will be a game changer for Canadian workers and businesses — unlocking a massive new market."

## What India Exports, What Canada Needs

The trade complementarity is striking. India exports pharmaceuticals, iron and steel, seafood, cotton garments, electronic goods, and chemicals to Canada. Canada ships back pulses, coal, crude oil, fertilizer, and paper — exactly the commodities India needs to feed its population and power its industry.

But the real growth potential is in services. India's telecommunications, IT, and business process outsourcing sectors are already deeply embedded in the Canadian economy. A CEPA would formalize and expand that relationship, potentially opening Canadian government procurement contracts to Indian IT firms for the first time.

Energy is another frontier. Canada is a major producer of oil, natural gas, and uranium. With India desperate to diversify its energy sources away from the war-disrupted Gulf, Canadian crude and nuclear fuel could become strategic imports. Both sides have discussed nuclear fuel cooperation as part of the broader package.

## The Diaspora Factor

None of this happens in a vacuum. Canada is home to over 425,000 Indian students — the largest international student population in the country. The broader Indian diaspora in Canada numbers well over a million. These are not just trade statistics; they are families, businesses, and voting constituencies that create organic economic demand.

The student pipeline alone is worth billions in tuition and living expenses. A CEPA that eases work permit pathways and recognizes Indian professional credentials could deepen that flow further. For NRIs already in Canada, the deal could reduce costs on everything from imported Indian food products to pharmaceutical generics.

## The Diplomatic Reset

The speed of the turnaround is remarkable. After the Nijjar crisis, India and Canada expelled each other's diplomats, trade talks were shelved, and bilateral relations hit their lowest point in decades. The reset began in early 2026, driven partly by shared concerns about the Iran war's impact on energy security and partly by the Carney government's strategic pivot toward Asia.

Carney, who took office in March 2025, has made diversifying Canada's trade partnerships a signature priority — explicitly to reduce dependence on the United States, where Trump's tariff policies have created persistent uncertainty. India, with its 1.4 billion consumers and 7-percent-plus growth rate, is the obvious partner.

The July round of negotiations will focus on tariff structures and market access timelines. Both sides are targeting a framework agreement by October and a final text by December.

## What Could Go Wrong

The optimism is real, but so are the obstacles. Agricultural market access is a perennial sticking point — India's farmers' lobbies resist cheap Canadian pulse imports, while Canada's dairy sector opposes Indian competition. Intellectual property rules for pharmaceuticals, where India's generic drug industry clashes with Canadian patent protections, will require creative compromises.

And the political ghosts have not fully disappeared. The Khalistan issue, while no longer dominating headlines, has not been resolved. Any flare-up could freeze the talks overnight.

But for now, the momentum is unmistakable. After two years of silence, India and Canada are talking again — and talking fast.

*Sources: Outlook Business, Reuters, Government of Canada, Ministry of Commerce and Industry (India)*"""

    wiki_used = final_image and ('wikipedia' in (img_url or '').lower() or 'wikimedia' in (img_url or '').lower())
    article = {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'news',
        'vertical': 'news',
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'image_url': final_image,
        'image_attribution': 'Wikimedia Commons' if wiki_used else ('Pexels' if final_image else None),
        'image_caption': 'India\'s Commerce Minister Piyush Goyal is in Ottawa for the third round of CEPA negotiations with Canada',
        'sources': json.dumps(['Outlook Business', 'Reuters', 'Government of Canada', 'Ministry of Commerce and Industry (India)']),
        'tags': ['India-Canada', 'CEPA', 'free trade', 'Piyush Goyal', 'Mark Carney'],
        'score_total': 84,
    }

    return insert_article(article)


# ===================================================================
# ARTICLE 3: India Heatwave
# ===================================================================

def write_article_3():
    print("\n=== ARTICLE 3: India Heatwave ===")

    slug = "india-heatwave-50-cities-record-temperatures-wet-bulb-survival-limits-20260528"
    headline = "Fifty Indian Cities Just Hit Record Temperatures. Scientists Say the Heat Is Approaching Human Survival Limits."
    subheadline = "Delhi touched 46°C on Wednesday. Wet-bulb temperatures in parts of India are nearing 33°C — dangerously close to the threshold where the human body can no longer cool itself."

    # Image: Pexels for heatwave/Delhi heat
    print("  Sourcing image...")
    img_url = fetch_pexels_image("extreme heat India summer sun cracked earth", "hot summer dry land drought")
    final_image = None
    if img_url:
        final_image = upload_image_to_supabase(img_url, f"{slug}.jpg")

    body = """India is being cooked. Not metaphorically — the country is experiencing a heatwave so severe that climate scientists are warning some regions are approaching the physical limits of human survival. Fifty cities have recorded their highest-ever temperatures this month. Delhi touched 46°C on Wednesday. And the most dangerous number is one most people have never heard of: the wet-bulb temperature.

## What the Wet-Bulb Number Means

Regular temperature readings tell you how hot the air is. Wet-bulb temperature tells you whether your body can survive in it. It measures the combined effect of heat and humidity — specifically, whether sweat can evaporate fast enough to cool the body. When the wet-bulb reading approaches 35°C, the human body cannot shed heat regardless of hydration, shade, or fitness. Death from hyperthermia becomes inevitable within hours.

Parts of India are now recording wet-bulb temperatures of 33°C. Portuguese climate analyst Bruno Brezenski, who has been tracking the heatwave, issued a blunt warning: "At that threshold, no human can last beyond two hours, and vulnerable groups such as infants and the elderly may collapse within half an hour."

Research from Penn State University has shown that even healthy young adults begin losing the ability to regulate body temperature at wet-bulb levels near 31°C — a threshold that several Indian cities have already crossed.

## The Nautapa Is Not Normal This Year

The current heatwave coincides with Nautapa, the traditional nine-day period of peak summer heat in the Hindu calendar. But 2026's Nautapa is being supercharged by El Niño, the Pacific Ocean warming pattern that amplifies heat across South and Southeast Asia.

The India Meteorological Department has issued red alerts — the highest category — across Punjab, Haryana, Delhi, Uttar Pradesh, Rajasthan, Madhya Pradesh, and Vidarbha. Temperatures in several districts have breached 47°C. In Telangana, twelve districts recorded above 46°C in a single day. The IMD says relief is unlikely before May 29, when western disturbances are expected to bring some cooling.

But the heat is not just a daytime problem. A 2024 Climate Trends study in Chennai found that indoor nighttime temperatures in several homes remained above 32°C and occasionally crossed 35°C. Fishers in Kerala's Alappuzha district report that nights no longer cool down. Labourers in Odisha's coastal districts describe severe dehydration within an hour of outdoor work.

## The Power Grid Is Buckling

India's peak power demand hit a record 270.8 gigawatts last week as air conditioning usage surged. Despite 228 GW of non-fossil fuel capacity, coal still generates more than 70 percent of India's electricity. And the coal supply chain is straining.

Twenty-one power plants now have critically low coal stocks — enough for less than a week of operation, according to the Central Electricity Authority. Coal India, the world's largest coal miner, has ordered its eight subsidiaries to maximize dispatches using all transport modes, including direct mine-to-plant rail links. The company's production fell 9.7 percent in April to 56.1 million metric tons, even as demand surged.

Several states are already imposing power cuts, mainly at night when solar and wind generation drops to zero. The grid is being held together by emergency measures.

## The Economic Toll

The heatwave is not just a humanitarian crisis. Manufacturing output is dipping as factories face unplanned downtime from overheated equipment and worker absenteeism. Agricultural yields for wheat, rice, and pulses — all in critical growth stages — are under threat. Supply chains for perishable goods are disrupted as cold chains struggle to maintain temperatures during transit.

Odisha, a major producer of minerals and steel, is particularly vulnerable. If industrial output there slows further, the effects will cascade through India's broader manufacturing index. Global investors with exposure to Indian commodities are already flagging supply chain risks.

## What NRIs Need to Know

For the roughly 32 million Indians living abroad, this is personal. Elderly parents, grandparents, and extended family across northern and central India are enduring conditions that scientists describe as life-threatening. The standard advice — stay hydrated, avoid midday sun, use air conditioning — assumes access to reliable power and cooling infrastructure that millions of Indians simply do not have.

If your family is in Delhi, UP, Rajasthan, MP, Haryana, or Telangana, this is the week to check in. The IMD's heatwave warning system is at imd.gov.in. Municipal heat action plans vary wildly in quality, but most major cities now operate cooling centers during peak hours.

The broader pattern is unmistakable. The Indian Institute of Tropical Meteorology reports that heatwave frequency in India's core heatwave zone has increased by 2.5 days per decade since 1961, with the trend accelerating sharply. This is not an anomaly. It is the new baseline.

*Sources: India Meteorological Department, Reuters, Central Electricity Authority, Penn State University, Climate Trends (Chennai), Bruno Brezenski/climate analysis*"""

    article = {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'news',
        'vertical': 'news',
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'image_url': final_image,
        'image_attribution': 'Pexels' if final_image else None,
        'image_caption': 'Fifty Indian cities have hit record temperatures as a severe heatwave grips the country',
        'sources': json.dumps(['India Meteorological Department', 'Reuters', 'Central Electricity Authority', 'Penn State University', 'Climate Trends']),
        'tags': ['heatwave', 'climate', 'wet-bulb temperature', 'power grid', 'El Nino', 'Delhi'],
        'score_total': 86,
    }

    return insert_article(article)


# ===================================================================
# MAIN
# ===================================================================

if __name__ == '__main__':
    print(f"=== The Videshi News Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} ===")
    
    results = []
    
    art1 = write_article_1()
    results.append(('Basmati Rice Exports', art1))
    time.sleep(1)
    
    art2 = write_article_2()
    results.append(('India-Canada Trade Deal', art2))
    time.sleep(1)
    
    art3 = write_article_3()
    results.append(('India Heatwave', art3))
    
    print("\n=== SUMMARY ===")
    for name, art_id in results:
        status = f"✓ {art_id}" if art_id else "✗ FAILED"
        print(f"  {name}: {status}")
    
    successes = sum(1 for _, a in results if a)
    print(f"\n  Published: {successes}/3 articles")
