#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-29)
Publishes 3 fresh news articles with proper image sourcing.
"""

import json
import os
import re
import sys
import time
import uuid
import urllib.parse
import subprocess
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
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def sb_post(table, data):
    """Insert into Supabase via curl (requests can throw IncompleteRead)."""
    cmd = [
        'curl', '-sS', '-w', '\n%{http_code}',
        f'{SUPABASE_URL}/rest/v1/{table}',
        '-H', f'apikey: {SUPABASE_KEY}',
        '-H', f'Authorization: Bearer {SUPABASE_KEY}',
        '-H', 'Content-Type: application/json',
        '-H', 'Prefer: return=representation',
        '-d', json.dumps(data)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    lines = result.stdout.strip().rsplit('\n', 1)
    body = lines[0] if len(lines) > 1 else result.stdout
    code = int(lines[1]) if len(lines) > 1 else 0
    if code >= 400:
        print(f"  ✗ Supabase POST {table} failed ({code}): {body[:200]}")
        return None
    try:
        parsed = json.loads(body)
        return parsed[0] if isinstance(parsed, list) and parsed else parsed
    except:
        return None

def sb_patch(table, match, data):
    """Update Supabase row via curl."""
    url = f'{SUPABASE_URL}/rest/v1/{table}?{match}'
    cmd = [
        'curl', '-sS', '-X', 'PATCH', '-w', '\n%{http_code}',
        url,
        '-H', f'apikey: {SUPABASE_KEY}',
        '-H', f'Authorization: Bearer {SUPABASE_KEY}',
        '-H', 'Content-Type: application/json',
        '-H', 'Prefer: return=representation',
        '-d', json.dumps(data)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    lines = result.stdout.strip().rsplit('\n', 1)
    code = int(lines[1]) if len(lines) > 1 else 0
    if code >= 400:
        print(f"  ✗ Supabase PATCH {table} failed ({code})")
    return code < 400

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        cmd = [
            'curl', '-sS', '-m', '10',
            '-H', 'User-Agent: TheVideshi/1.0 (thevideshi.com)',
            f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            img = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch a specific image from Pexels using curl."""
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            cmd = [
                'curl', '-sS', '-m', '10',
                '-H', f'Authorization: {PEXELS_API_KEY}',
                f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                photos = data.get('photos', [])
                if photos:
                    # Pick the first landscape photo with good resolution
                    for photo in photos:
                        url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                        if url:
                            print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                            return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    tmp_path = f'/tmp/{filename}'
    try:
        # Download
        dl_cmd = ['curl', '-sS', '-L', '-m', '15', '-o', tmp_path, image_url]
        subprocess.run(dl_cmd, capture_output=True, timeout=20)
        
        # Verify file size
        if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) < 5000:
            print(f"  ✗ Downloaded image too small or missing: {tmp_path}")
            return None
        
        # Upload to Supabase storage
        upload_cmd = [
            'curl', '-sS', '-X', 'POST', '-w', '\n%{http_code}',
            f'{SUPABASE_URL}/storage/v1/object/article-images/{filename}',
            '-H', f'apikey: {SUPABASE_KEY}',
            '-H', f'Authorization: Bearer {SUPABASE_KEY}',
            '-H', 'Content-Type: image/jpeg',
            '-H', 'x-upsert: true',
            '--data-binary', f'@{tmp_path}'
        ]
        result = subprocess.run(upload_cmd, capture_output=True, text=True, timeout=30)
        lines = result.stdout.strip().rsplit('\n', 1)
        code = int(lines[1]) if len(lines) > 1 else 0
        
        if code < 300:
            public_url = f'{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}'
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed ({code}): {lines[0][:200] if lines else 'unknown'}")
            return None
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
        return None
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def validate_image_url(url):
    """Check that the URL returns a valid image."""
    if not url:
        return False
    try:
        cmd = ['curl', '-sS', '-I', '-m', '10', '-L', url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        headers = result.stdout.lower()
        has_image = 'content-type: image/' in headers
        # Check content-length
        cl_match = re.search(r'content-length:\s*(\d+)', headers)
        size_ok = int(cl_match.group(1)) > 5000 if cl_match else True  # if no CL header, assume OK
        return has_image and size_ok
    except:
        return False

# ─── ARTICLE DEFINITIONS ──────────────────────────────────────────────

articles = [
    {
        "headline": "A Russian Drone Just Hit an Apartment Block in NATO Member Romania. The War in Ukraine Has Crossed a New Line.",
        "subheadline": "For the first time since Russia's invasion began, a military drone struck a densely populated area in an EU and NATO country — injuring two civilians in the city of Galati and triggering condemnation from every Western capital.",
        "slug": "russia-drone-hits-romania-apartment-nato-escalation-india-strategic-20260529",
        "category": "news",
        "vertical": "global-security",
        "urgency": "high",
        "tags": ["russia", "ukraine", "nato", "romania", "drone-strike", "article-5", "india-strategic-autonomy", "eu-sanctions"],
        "diaspora_angle": "India's strategic balancing act between Russia and the West faces a new stress test. A NATO Article 5 scenario would force every major power to pick a side — and India's 4.5 million diaspora across Europe would be directly affected by any escalation.",
        "sources": "Reuters, CNN, The Times, Fox News, NATO official statements",
        "image_search_person": "Mark Rutte",
        "image_search_pexels": "NATO military alliance",
        "image_search_pexels_fallback": "European military defense drone",
        "body": """For four minutes early Friday morning, a Russian military drone flew unchallenged through Romanian airspace before slamming into the roof of a ten-storey apartment block in the city of Galati. The explosion ripped through the top floor, sparked a fire, and sent seventy residents scrambling into the predawn darkness. A woman and her child were hospitalised with injuries. Two others were treated for panic attacks at the scene.

It was, by every measure, a first. Russian drones have breached Romanian airspace 28 times since Moscow began systematically targeting Ukrainian ports along the Danube. Drone fragments have been recovered 47 times. But never before had a wartime drone struck a densely populated area inside a NATO and EU member state and injured civilians.

## NATO's Response Was Immediate

Within hours, the entire Western alliance had lined up behind Bucharest. NATO Secretary General Mark Rutte said the alliance "stands ready to defend every inch of Allied territory." EU Commission President Ursula von der Leyen announced she is preparing a 21st round of sanctions against Moscow. France summoned Russia's ambassador. Romania did the same.

Romanian President Nicusor Dan called it a "systematic disregard for international law" and demanded a "firm, coordinated and proportionate response — at national, allied and international level." Foreign Minister Oana Toiu said Romania has requested accelerated transfers of anti-drone capabilities from NATO.

The Romanian military scrambled two F-16 fighter jets and a military helicopter to monitor the attack. Under recently enacted Romanian law, pilots were authorised to shoot down any drones threatening lives or property — but no drones were intercepted.

## The Escalation Pattern Is Unmistakable

The Galati strike did not happen in isolation. In recent weeks, drones have strayed into Baltic airspace with increasing frequency. A NATO fighter jet shot down a suspected Ukrainian drone over Estonia days earlier. Lithuania warned citizens to take cover after a drone approached its airspace. Flights were grounded at a major European airport after a drone sighting.

Moscow's drone warfare campaign against Ukraine's Danube port infrastructure — Izmail, Reni, and surrounding areas — has been intensifying precisely because these targets sit within kilometres of Romania's border. The closer Russia's targets get to NATO territory, the higher the probability of exactly this kind of incident.

EU Foreign Policy Chief Kaja Kallas put it bluntly: "Russia has long ago stopped respecting borders. Moscow cannot be allowed to breach European airspace with impunity."

## Why India Is Watching This Closely

For New Delhi, the Romania strike crystallises a set of calculations that India's foreign policy establishment has been making since Russia invaded Ukraine in February 2022.

India has maintained what it calls strategic autonomy — refusing to join Western sanctions against Russia while simultaneously deepening its security partnerships with the United States and its Quad allies. Prime Minister Modi's government has argued that dialogue, not isolation, is the path to peace. India has continued purchasing discounted Russian crude oil, defended its position in multilateral forums, and avoided directly condemning Moscow.

But the Galati incident tests the limits of that balancing act. If Russia's war physically threatens NATO civilians — and if NATO responds with a harder security posture — India's room to straddle both camps narrows. Any Article 5 invocation, however unlikely at this stage, would force every major power to pick a side.

India also has a direct interest in the drone warfare dimension. New Delhi has been investing heavily in indigenous drone capabilities and counter-drone systems, particularly after the 2020 Ladakh standoff with China exposed gaps in India's surveillance architecture. The Romania strike demonstrates that even sophisticated NATO air defences — Romania operates US-made Merops anti-drone systems — can struggle against low-flying drones in urban environments.

## What Happens Next

Russia has not commented on the strike. It rarely does when its drones stray across borders, treating each incident as a byproduct of its war against Ukraine rather than an act of aggression against a sovereign state.

Romania, however, is not treating it that way. Bucharest has formally requested enhanced NATO anti-drone capabilities and has signalled it will push for stronger collective defence measures at the next alliance summit.

The question now is whether Galati becomes the incident that finally forces NATO to establish a permanent drone defence corridor along its eastern border — and whether that, in turn, draws the alliance deeper into the conflict Moscow insists is not Europe's war.

For the 70 residents evacuated from their apartment block at 1 a.m. on a Friday morning, the war has already arrived."""
    },
    {
        "headline": "India and China Just Held Their 35th Border Meeting in Beijing. Both Sides Called It 'Constructive.'",
        "subheadline": "Six years after the Galwan Valley clash killed twenty Indian soldiers, the two Asian giants are methodically rebuilding trust — one working mechanism meeting at a time. The next step is a Special Representatives summit in China.",
        "slug": "india-china-35th-wmcc-border-talks-beijing-delimitation-lac-20260529",
        "category": "news",
        "vertical": "india-diplomacy",
        "urgency": "medium",
        "tags": ["india", "china", "lac", "galwan", "border-talks", "wmcc", "jaishankar", "xi-jinping", "ladakh", "quad"],
        "diaspora_angle": "A stable India-China border means India can redirect defence spending toward modernisation, Indian tech companies can plan without escalation risk, and the Quad framework that NRIs in the US benefit from can function as strategy rather than emergency.",
        "sources": "Ministry of External Affairs (India), The Hindu BusinessLine, News Dive, The Kashmir Horizon, NewKerala",
        "image_search_person": "S. Jaishankar",
        "image_search_pexels": "India China border Ladakh mountains",
        "image_search_pexels_fallback": "Himalayan mountain border landscape",
        "body": """India and China held the 35th meeting of the Working Mechanism for Consultation and Coordination on India-China Border Affairs in Beijing on Wednesday, with both sides describing the discussions as "constructive and forward-looking" — diplomatic language that, in the context of a relationship that nearly collapsed into armed conflict six years ago, counts as progress.

The Indian delegation was led by Sujit Ghosh, Joint Secretary for East Asia at the Ministry of External Affairs. The Chinese side was led by Hou Yanqi, Director General of the Boundary and Oceanic Affairs Department at China's Ministry of Foreign Affairs. Both are seasoned negotiators — Ghosh served as India's Deputy High Commissioner in the UK and as Director for China; Hou Yanqi was China's Ambassador to Nepal from 2018 to 2022.

## What Was Actually Discussed

The agenda covered four substantive areas: delimitation of the border, border management protocols, mechanism-building for regular diplomatic and military contacts, and cross-border cooperation — a deliberately broad portfolio that signals both sides are ready to move beyond crisis management toward longer-term institution-building.

India specifically pushed for an early meeting of the Expert Level Mechanism on Trans-border Rivers, a technically unglamorous but strategically critical issue. China's upstream dam-building on rivers that flow into India — the Brahmaputra chief among them — has been a source of deep anxiety in New Delhi for years. Getting Beijing to agree to regular expert-level consultations on water data would be a meaningful confidence-building measure.

Both sides agreed to maintain regular exchanges through the diplomatic and military channels established as outcomes of the 24th Special Representatives talks held last year, when National Security Advisor Ajit Doval and Chinese Foreign Minister Wang Yi met in New Delhi and produced a suite of agreements to stabilise the border.

## The Long Road From Galwan

The trajectory here matters. In June 2020, Indian and Chinese soldiers fought a brutal hand-to-hand battle in the Galwan Valley that killed twenty Indian soldiers and an undisclosed number of Chinese troops. It was the deadliest border clash between the two nations in over four decades and sent bilateral relations to their lowest point since the 1962 war.

What followed was a grinding, multi-year process of disengagement. Approximately 50,000 troops remained deployed on each side of the Line of Actual Control through years of talks. The breakthrough came in October 2024, when Prime Minister Narendra Modi and President Xi Jinping met in Kazan, Russia, and agreed on patrolling arrangements in the contested Depsang and Demchok areas.

Since then, disengagement from all friction points has been completed. Patrolling activities and grazing have resumed along pre-2020 patterns. The Ministry of External Affairs confirmed this week that the Kazan agreement "has been fully implemented according to agreed modalities and timelines."

## Why the NRI Community Should Pay Attention

For the Indian diaspora, the India-China relationship is not an abstract geopolitical chess game. It directly shapes India's economic trajectory, its defence spending priorities, and its position in the technology supply chain that Indian-American professionals dominate.

A stable LAC means India can redirect defence spending from emergency border infrastructure toward longer-term modernisation. It means Indian technology companies can plan without the shadow of a sudden escalation disrupting supply chains through Southeast Asia. And it means the Quad — which India has deepened alongside the US, Japan, and Australia — can function as a strategic framework rather than an emergency coalition.

The next milestone is a meeting of the Special Representatives in China. No date has been announced, but both sides agreed this week to "make substantive preparation" for it — language that suggests the meeting is being treated as a near-term priority, not a distant aspiration.

Chinese Ambassador to India Xu Feihong said on X that Assistant Foreign Minister Hong Lei met with Ghosh during the visit and that both sides "exchanged views on bilateral relations, multilateral cooperation, and boundary issues."

## The Bigger Picture

India's border diplomacy with China is happening against a backdrop of intensifying strategic competition in Asia. China has been deepening its ties with Pakistan — President Xi Jinping praised "unbreakable" ties with Islamabad during Pakistani Prime Minister Shehbaz Sharif's visit to Beijing this week.

India, meanwhile, has been consolidating its partnerships with the US, Japan, and Australia through the Quad, and recently hosted Secretary of State Marco Rubio for discussions on trade, defence, and critical minerals.

The 35th WMCC meeting suggests that despite all this, both New Delhi and Beijing have decided that a stable border serves their respective interests — even if broader strategic competition continues on every other front. Whether that pragmatism holds through the next crisis is the question neither side can answer yet."""
    },
    {
        "headline": "India Just Ordered a 30-Day Strategic Reserve of Cooking Gas. The Iran War Explains Why.",
        "subheadline": "New Delhi has told state-run fuel companies to build LPG storage for a full month of national demand — a direct response to the Strait of Hormuz crisis that has already choked India's basmati exports and driven up global energy prices.",
        "slug": "india-lpg-30-day-strategic-reserve-iran-war-hormuz-energy-security-20260529",
        "category": "news",
        "vertical": "energy-security",
        "urgency": "high",
        "tags": ["india", "lpg", "strategic-reserve", "iran", "hormuz", "energy-security", "oil-ministry", "ujjwala", "crude-oil"],
        "diaspora_angle": "Energy security is the thread connecting kitchen budgets in Lucknow to remittance values in New Jersey. When LPG prices spike, the rupee weakens, inflation rises, and the purchasing power of dollar-denominated NRI remittances shifts.",
        "sources": "Reuters, Ministry of Petroleum and Natural Gas (India)",
        "image_search_person": None,
        "image_search_pexels": "LPG gas cylinders India cooking gas storage",
        "image_search_pexels_fallback": "oil refinery India petroleum storage",
        "body": """India's oil ministry has directed state-run fuel retailers to build liquefied petroleum gas storage capacity sufficient to meet 30 days of national demand — a significant escalation of the country's energy security posture that comes as the Iran-US conflict continues to threaten the Strait of Hormuz, through which roughly 60 percent of India's crude oil imports transit.

Sujata Sharma, a joint secretary in the federal oil ministry, confirmed the directive on Friday, adding that India is also working on expanding its strategic crude oil reserves.

## What 30 Days of LPG Actually Means

India consumes approximately 30 million metric tonnes of LPG annually, making it the world's second-largest consumer after China. Nearly 320 million Indian households — overwhelmingly in rural areas — depend on subsidised LPG cylinders distributed through the Pradhan Mantri Ujjwala Yojana scheme and commercial distribution networks run by Indian Oil Corporation, Bharat Petroleum, and Hindustan Petroleum.

Building a 30-day strategic reserve means storing roughly 2.5 million metric tonnes of LPG at any given time — a logistically enormous undertaking that will require new storage terminals, expanded port infrastructure, and potentially underground cavern storage similar to India's existing Strategic Petroleum Reserves at Visakhapatnam, Mangalore, and Padur.

Currently, India's LPG storage capacity covers approximately 12 to 15 days of demand. Doubling that buffer is not a routine upgrade. It is a wartime measure dressed in peacetime language.

## The Hormuz Factor

The directive's timing is inseparable from the Iran crisis. Since military hostilities resumed between the United States and Iran, the Strait of Hormuz — the 33-kilometre-wide chokepoint connecting the Persian Gulf to the Arabian Sea — has been subject to intermittent disruptions that have sent oil and gas prices spiking globally.

India imports roughly 85 percent of its crude oil and is heavily dependent on Middle Eastern suppliers. The Hormuz bottleneck has already hammered India's export economy: basmati rice exports crashed 27 percent as Gulf trade routes seized up. Cooking oil prices have risen. And the Reserve Bank of India has been forced to recalibrate its inflation forecasts to account for sustained energy price volatility.

A framework deal between Iran and the US is reportedly close, with a 60-day memorandum of understanding that would extend the current ceasefire and reopen Hormuz. But India's oil ministry is clearly not betting on diplomacy alone.

## The Crude Reserve Expansion

Sharma's mention of expanding crude oil storage is equally significant. India currently has Strategic Petroleum Reserves holding approximately 5.33 million metric tonnes of crude — enough for about 9.5 days of imports. The government had already approved a second phase of strategic reserves at Chandikhol in Odisha and Padur Phase II in Karnataka, but construction has been slow.

The Iran crisis appears to have accelerated that timeline. Building LPG and crude reserves simultaneously signals that New Delhi is preparing for a scenario in which Hormuz disruptions last months, not weeks — and that India cannot rely on any single diplomatic outcome to secure its energy supply.

## What This Means for NRIs

For the Indian diaspora, energy security is the thread that connects kitchen budgets in Lucknow to remittance values in New Jersey. When LPG prices spike in India, the rupee weakens, inflation rises, and the purchasing power of dollar-denominated remittances shifts.

The 30-day LPG reserve directive is also a test of India's institutional capacity to execute large-scale infrastructure projects under pressure. The Ujjwala scheme — which connected over 100 million households to LPG for the first time — was a signature achievement of the Modi government. Protecting that achievement from supply disruptions is both an economic necessity and a political imperative ahead of state elections.

India is also working to diversify its LPG sourcing away from the Middle East. Imports from the United States, Australia, and Qatar have been increasing, and the government has been negotiating long-term supply contracts that reduce dependence on any single geographic corridor.

## The Broader Energy Security Picture

The LPG directive sits alongside a series of energy security measures India has taken since the Iran conflict escalated. The government has been accelerating its shift toward renewable energy, with solar and wind capacity additions running ahead of schedule. India's nuclear energy programme received a boost with the enactment of the Sustainable Harnessing and Advancement of Nuclear Energy bill. And discussions with Russia on discounted crude — one of the most diplomatically sensitive aspects of India's energy policy — have continued despite Western pressure.

But for 320 million households that cook with LPG every day, the strategic reserve is the measure that matters most. If Hormuz closes for a month, India's kitchens need to keep working.

The oil ministry's directive makes that calculation explicit: prepare for the worst, negotiate for the best, and store enough gas to bridge the gap between the two."""
    }
]

# ─── MAIN ──────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"The Videshi — News Writer")
    print(f"Run: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Articles to write: {len(articles)}")
    print(f"{'='*60}\n")

    published_count = 0

    for i, article in enumerate(articles, 1):
        print(f"\n--- Article {i}/{len(articles)}: {article['headline'][:60]}... ---")

        # Image sourcing
        img_url = None
        img_attribution = None

        # Step 1: Wikipedia for person articles
        if article.get('image_search_person'):
            print(f"  Trying Wikipedia for '{article['image_search_person']}'...")
            img_url = fetch_wikipedia_person_image(article['image_search_person'])
            if img_url:
                img_attribution = "Wikimedia Commons"

        # Step 2: Pexels fallback
        if not img_url and article.get('image_search_pexels'):
            print(f"  Trying Pexels for '{article['image_search_pexels']}'...")
            img_url = fetch_pexels_image(
                article['image_search_pexels'],
                article.get('image_search_pexels_fallback')
            )
            if img_url:
                img_attribution = "The Videshi"

        # Validate image
        if img_url:
            print(f"  Validating image URL...")
            if not validate_image_url(img_url):
                print(f"  ✗ Image validation failed, skipping image")
                img_url = None

        # Generate article ID
        art_id = str(uuid.uuid4())

        # Upload image to Supabase for permanence
        final_img_url = None
        if img_url:
            print(f"  Uploading to Supabase storage...")
            final_img_url = upload_image_to_supabase(img_url, f"{art_id}.jpg")

        # Build article record
        now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
        word_count = len(article["body"].split())
        record = {
            "id": art_id,
            "headline": article["headline"],
            "subheadline": article["subheadline"],
            "slug": article["slug"],
            "body": article["body"].strip(),
            "category": article["category"],
            "vertical": article["vertical"],
            "urgency": article["urgency"],
            "tags": article["tags"],
            "diaspora_angle": article["diaspora_angle"],
            "status": "published",
            "published_at": now_iso,
            "created_at": now_iso,
            "sources": article["sources"],
            "word_count": word_count,
            "image_attribution": img_attribution or "The Videshi"
        }

        if final_img_url:
            record["image_url"] = final_img_url

        # Validate article quality
        print(f"  Word count: {word_count}")
        if word_count < 400:
            print(f"  ✗ REJECTED: body too short ({word_count} words, need 400+)")
            continue
        if len(article["headline"]) > 200:
            print(f"  ✗ REJECTED: headline too long ({len(article['headline'])} chars)")
            continue
        if len(article["subheadline"]) < 15:
            print(f"  ✗ REJECTED: subheadline too short")
            continue

        # Publish
        print(f"  Publishing to Supabase...")
        result = sb_post("p2_articles", record)
        if result:
            print(f"  ✓ Published: {article['slug']}")
            print(f"    ID: {art_id}")
            print(f"    Image: {'yes' if final_img_url else 'no'}")
            published_count += 1
        else:
            print(f"  ✗ Failed to publish: {article['slug']}")

        # Small delay between articles
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Done. Published {published_count}/{len(articles)} articles.")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
