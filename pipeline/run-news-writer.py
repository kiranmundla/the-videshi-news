#!/usr/bin/env python3
"""
The Videshi — News Writer
Generates 3 news articles for thevideshi.com
Run: 2026-05-30
"""

import json, os, uuid, time, re, subprocess
import requests
import urllib.parse
from datetime import datetime, timezone

# Load Supabase credentials
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                key, val = line.split('=', 1)
                val = val.strip('"').strip("'")
                env[key] = val
    return env

env = load_env('~/.env.supabase')
SUPABASE_URL = env['SUPABASE_URL']
SUPABASE_KEY = env['SUPABASE_SERVICE_ROLE_KEY']

# Load Pexels key
pexels_env = load_env('~/workspace/.env.pexels')
PEXELS_KEY = pexels_env.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def sb_insert(table, data):
    """Insert a row into Supabase."""
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        return result[0] if isinstance(result, list) and result else result
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None

def sb_patch(table, match, data):
    """Patch a row in Supabase."""
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return False

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
    """Fetch an image from Pexels using curl (Python urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
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
    try:
        r = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ✗ Image download failed ({r.status_code}) for {image_url[:80]}")
            return image_url  # fall back to original
        
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if not content_type.startswith('image/'):
            content_type = 'image/jpeg'
        
        if len(r.content) < 5000:
            print(f"  ✗ Image too small ({len(r.content)} bytes), skipping upload")
            return image_url
        
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true"
        }
        
        upload_r = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
            headers=upload_headers,
            data=r.content,
            timeout=30
        )
        
        if upload_r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed ({upload_r.status_code}): {upload_r.text[:200]}")
            return image_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return image_url

def validate_image_url(url):
    """Check if an image URL is valid and not too small."""
    if not url:
        return False
    # Check for banned domains
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        print(f"  ✗ Banned domain in URL: {url[:60]}")
        return False
    banned_params = ['_nc_ht=', '_nc_cat=', 'ccb=']
    if any(p in url for p in banned_params):
        print(f"  ✗ Banned params in URL: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "TheVideshi/1.0"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' not in ct:
            print(f"  ✗ Not an image: {ct}")
            return False
        if cl > 0 and cl < 5000:
            print(f"  ✗ Image too small: {cl} bytes")
            return False
        return True
    except:
        return True  # optimistic if HEAD fails


# ─── ARTICLES ───────────────────────────────────────────────────────

articles = []

# ─── ARTICLE 1: China Ghosts Shangri-La Dialogue ───────────────────

articles.append({
    "headline": "China Has Skipped the Shangri-La Dialogue for Two Years in a Row. The Rest of Asia Noticed.",
    "subheadline": "Beijing sent a low-profile delegation of PLA academics while India held five bilateral defence meetings and the US, UK, and Australia announced a new undersea drone programme.",
    "slug": "china-skips-shangri-la-dialogue-second-year-india-aukus-undersea-drones-20260530",
    "category": "news",
    "vertical": "news",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com"},
        {"name": "Bhasha Times", "url": "https://bhashatimes.com"}
    ]),
    "image_search_person": "Dong Jun",
    "image_search_alt": "Shangri-La Dialogue Singapore defence forum",
    "body": """For the second consecutive year, China's Defence Minister Dong Jun has skipped the Shangri-La Dialogue — Asia's most important annual defence forum — and the absence is becoming harder for Beijing to explain away.

The three-day summit in Singapore, which draws defence ministers and senior officials from more than 40 countries, opened this weekend with a conspicuous gap in its programme. The slot traditionally reserved for a keynote speech by a senior Chinese official has been dropped entirely, replaced by a low-profile delegation of People's Liberation Army "experts and scholars."

Even US Defense Secretary Pete Hegseth took note. "I wish my counterpart was here at this conference," he said during his own keynote address on Saturday. "But I look forward to other options when we can cross paths and communicate."

## A Calculated Absence

Australia's Deputy Prime Minister and Defence Minister Richard Marles was less diplomatic. He called China's decision a "missed opportunity" at precisely the moment when countries in the region need more "strategic reassurance" from Beijing.

"We've seen China engage in the biggest conventional military buildup in the world since the end of the Second World War, and that has not happened with a strategic reassurance for other countries," Marles told Reuters on the sidelines of the event.

Analysts point to several reasons Beijing may prefer to stay away. A high-profile appearance would invite pointed questions about Taiwan tensions, China's expanding military footprint in the South China Sea, and the sweeping anti-corruption purges that have consumed the PLA's senior leadership in recent years. Several top generals have disappeared from public view since the purges began in 2023.

Zhou Bo, a retired PLA senior colonel who was part of China's delegation, tried to downplay the absence. "This is not the first time the defence minister is not attending," he said. "And academic delegations have come before. But it is true that the level of the delegation is relatively low this time."

## India Fills the Vacuum

While China sent scholars, India sent its Defence Secretary Rajesh Kumar Singh, who held five bilateral meetings in a single day — with counterparts from the Netherlands, Australia, the European Union, and two other Indo-Pacific partners. India's delegation articulated a vision for "a stable, secure, and inclusive Indo-Pacific" that was sharply at odds with Beijing's preference for bilateral deal-making.

Hegseth went further in his praise for New Delhi, calling India "a critical anchor to hold the line" in South Asia. "A powerful India acting in its own self-interest advances our shared goal of maintaining a balance of power across the region," he said.

He highlighted India's growing defence-industrial capacity, its expanding ability to sustain high-end military operations in the Indian Ocean, and the two countries' commitment to co-produce Javelin anti-tank guided munitions — a significant step in US-India defence cooperation.

## AUKUS Makes Its Move

The Shangri-La sidelines also produced a concrete announcement: the United States, United Kingdom, and Australia unveiled plans to jointly develop unmanned undersea vehicles under the AUKUS pact's "Pillar Two" advanced technology programme.

"This will rapidly give our forces the very most advanced battlefield technologies as together we produce a range of cutting-edge sensors and weapons systems for undersea drones," said Britain's Defence Secretary John Healey. "For too long in AUKUS, we talked too much and delivered too little."

The programme is designed to counter China's growing power in the maritime domain and protect critical undersea infrastructure including cables and pipelines.

## The Bigger Picture

China's absence from Shangri-La is not merely a diplomatic snub — it is a signal. By declining to show up at the region's premier security forum for two years running, Beijing is ceding the floor to an increasingly coordinated set of partners who are filling the space with new alliances, new announcements, and new frameworks that explicitly aim to constrain Chinese influence.

For India, which has sometimes been criticised for its own patchy attendance at previous editions of the dialogue, this year's robust showing represents a deliberate repositioning. New Delhi is not just attending the conversation about Indo-Pacific security — it is helping to set its terms.

The question now is whether Beijing's absence is a temporary sulk or a longer-term strategic withdrawal from multilateral security diplomacy. Either way, the rest of Asia is not waiting for an answer."""
})

# ─── ARTICLE 2: India Heatwave Study ───────────────────────────────

articles.append({
    "headline": "A Single Day of Extreme Heat Kills 3,400 People Across India. A New Study Finally Counted.",
    "subheadline": "UC Berkeley researchers found that a five-day heatwave causes nearly 30,000 excess deaths — and India is heading into its worst monsoon in 11 years.",
    "slug": "india-extreme-heat-3400-deaths-per-day-uc-berkeley-study-heatwave-monsoon-20260530",
    "category": "news",
    "vertical": "news",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Frontiers in Environmental Health", "url": "https://www.frontiersin.org"},
        {"name": "The Bharat Affairs", "url": "https://bharataffairs.com"},
        {"name": "India Meteorological Department", "url": "https://mausam.imd.gov.in"}
    ]),
    "image_search_person": None,
    "image_search_alt": "India heatwave extreme heat summer",
    "body": """India already knew its summers were getting deadlier. Now there is a number to put on it.

A single day of extreme heat is associated with approximately 3,400 excess deaths across India, according to a study by researchers at the University of California, Berkeley's India Energy and Climate Center. A heatwave lasting five consecutive days pushes that figure to nearly 30,000.

The findings, published in the journal *Frontiers in Environmental Health*, represent one of the most comprehensive attempts to quantify what climate scientists and public health officials have long described as a "silent public health emergency" — one that kills far more Indians than floods, cyclones, and earthquakes combined, but attracts a fraction of the attention.

## How They Counted

The study's authors, Piyush Narang and Ashok Gadgil, faced a fundamental problem: India does not systematically track heat-related deaths at the district level. State governments report heat deaths inconsistently, and many fatalities — particularly among the elderly, outdoor labourers, and the rural poor — are attributed to other causes or simply go uncounted.

To get around this, the researchers adapted findings from a multi-city study of heat-related mortality across 10 Indian cities, then applied them to all districts nationwide using population data from the Civil Registration System and 2024 projections. The result is an estimate, not a precise tally — but it is the most granular picture of heat mortality that India has.

"We estimate that a single day of extreme heat causes approximately 3,400 excess deaths nationally; a five-day heatwave causes nearly 30,000," the authors wrote. Excess deaths refer to fatalities above what historical trends would predict for any given period.

## A Crisis Already Underway

The timing of the study is grimly relevant. Temperatures across northern, central, and eastern India have been hovering above 45°C (113°F) for days. Parts of Madhya Pradesh, Rajasthan, Uttar Pradesh, and Haryana have recorded some of the most extreme readings. Hospitals in affected areas report surging admissions for heatstroke, dehydration, cardiovascular stress, and kidney failure.

The India Meteorological Department (IMD) has forecast that June will bring above-normal maximum and minimum temperatures across most of the country, with heatwave conditions expected in Uttar Pradesh, Haryana, Punjab, Bihar, Odisha, Chhattisgarh, Gujarat, Andhra Pradesh, and parts of Maharashtra, Telangana, and Tamil Nadu.

Relief from the monsoon — which typically arrives in southern India around June 1 and spreads nationwide by mid-July — may come later and weaker than usual. The IMD this week revised its monsoon rainfall forecast down to 90% of the long-period average, the weakest projection in 11 years. An El Niño is expected to develop by July, further suppressing rainfall.

## Who Dies

The study's authors and doctors treating heatwave patients describe a consistent pattern. The victims are overwhelmingly outdoor workers — construction labourers, rickshaw pullers, farm workers, street vendors — along with the elderly and those without access to cooling infrastructure. In rural India, where electricity supply remains unreliable and air conditioning is a luxury, entire communities are exposed.

Urban India is not spared. Cities amplify heat through the "urban heat island" effect — concrete, asphalt, and dense construction trap heat during the day and prevent cooling at night. Delhi, which recorded temperatures above 46°C in recent days, sees nighttime temperatures that barely drop below 30°C, denying residents the overnight recovery that human bodies need.

## The Diaspora Connection

For the millions of NRIs whose parents and extended families still live in India — particularly in the Hindi belt states of UP, Bihar, Rajasthan, and MP that bear the worst of summer heat — the study quantifies a risk that has always been abstract. Phone calls home during Indian summers often include casual mentions of power cuts and unbearable heat. The Berkeley study suggests those conditions are killing thousands of people every day they persist.

## What Comes Next

India's public health response to extreme heat remains largely reactive — advisories to stay indoors, drink water, and avoid the afternoon sun. But the scale of the crisis the Berkeley study describes demands something more: early warning systems linked to hospital surge capacity, outdoor work regulations with enforceable rest-hour mandates, and cooling infrastructure in the most vulnerable districts.

With the weakest monsoon in over a decade approaching and El Niño on the horizon, the window for preparation is closing faster than the temperatures are rising."""
})

# ─── ARTICLE 3: SEBI Clears NDTV ──────────────────────────────────

articles.append({
    "headline": "SEBI Has Finally Cleared NDTV of Disclosure Violations. The Case Began in 2009.",
    "subheadline": "India's markets regulator ruled that no change of control occurred under a 2009 loan agreement — ending a 17-year-old saga for the Adani-owned broadcaster.",
    "slug": "sebi-clears-ndtv-disclosure-violations-17-year-case-adani-loan-agreement-20260530",
    "category": "news",
    "vertical": "news",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Securities and Exchange Board of India", "url": "https://www.sebi.gov.in"},
        {"name": "Securities Appellate Tribunal", "url": "https://sat.gov.in"}
    ]),
    "image_search_person": None,
    "image_search_alt": "NDTV India news broadcaster",
    "body": """It took 17 years, but the Securities and Exchange Board of India has finally closed the book on one of its longest-running corporate disputes — and NDTV walked away clean.

In an order issued on Friday, SEBI disposed of proceedings against New Delhi Television Ltd (NDTV), ruling that the company did not violate disclosure regulations in connection with a 2009 loan agreement that the regulator had previously claimed amounted to a change in control.

The decision marks the end of a regulatory saga that began during the UPA government era, survived the transition to NDA rule, and outlasted NDTV's own transformation from an independently owned broadcaster to a unit of the Adani Group.

## The 2009 Agreement

The case traces back to a loan agreement entered into by NDTV's founders, Prannoy Roy and Radhika Roy, in 2009. Under the terms, the lender was granted options to acquire a significant stake in the broadcaster — provisions that SEBI later argued constituted a de facto change in control.

In June 2018 — nearly a decade after the agreement was signed — SEBI formally held that the arrangement did indeed result in a change in control of NDTV. The regulator then launched disclosure violation proceedings, arguing that NDTV should have informed stock exchanges about SEBI's finding at the time.

NDTV contested the proceedings, and the case went to the Securities Appellate Tribunal (SAT).

## SAT Overturns SEBI

In 2022, the SAT set aside SEBI's 2018 ruling, holding that the loan agreement did not amount to a change in control because the options it contained were never actually exercised. The distinction was critical: SEBI had treated the mere existence of the options as a control event, while SAT ruled that unexercised options do not transfer control.

With SAT's ruling standing, SEBI was left in an awkward position. Its disclosure violation case depended entirely on the premise that a change in control had occurred. If it hadn't — as SAT held — then there was nothing to disclose, and therefore no violation.

## Friday's Order

That is exactly what SEBI concluded in its Friday order. The regulator noted that since there was no change in control, no disclosure obligation arose under listing regulations, and therefore no violation of the rules occurred. The proceedings were disposed of without penalty.

For NDTV, the ruling removes one of the last regulatory clouds from its pre-Adani era. The Adani Group completed its takeover of NDTV in 2023, acquiring a majority stake through a combination of indirect share purchases and an open offer. Prannoy Roy and Radhika Roy subsequently stepped down from their executive roles.

## What It Means

The SEBI-NDTV case is a case study in how Indian securities regulation can become entangled in its own timelines. A 2009 transaction was first scrutinised in 2018, overturned in 2022, and finally cleared in 2026. Throughout, NDTV operated under a cloud of regulatory uncertainty that affected its market reputation, its ability to attract investors, and — some analysts argue — its editorial independence.

The case also highlights a recurring tension in Indian corporate law: the question of when financial arrangements that fall short of actual share transfers can nonetheless be treated as control events. SEBI's aggressive interpretation in 2018 was ultimately rejected, but the mere act of bringing the case had consequences for the company that no subsequent ruling can undo.

For investors, the takeaway is narrower but relevant. SEBI's disposal of the case confirms that disclosure obligations under Indian listing rules are triggered by actual control changes, not by the theoretical possibility of future changes embedded in financial instruments. Companies with complex ownership structures and option-laden agreements can take some comfort from that precedent — though the 17-year timeline for resolution offers rather less reassurance about regulatory efficiency.

The Adani Group, which now controls NDTV's editorial and commercial operations, has not commented on the ruling. The company's shares closed unchanged on Friday."""
})

# ─── PUBLISH ────────────────────────────────────────────────────────

published_count = 0

for i, article in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {article['headline'][:70]}...")
    
    # Image sourcing
    img_url = None
    
    # Try Wikipedia for person articles
    if article.get('image_search_person'):
        person = article['image_search_person']
        print(f"  → Trying Wikipedia for '{person}'...")
        img_url = fetch_wikipedia_person_image(person)
        
        # Try alternate names
        if not img_url and '(' not in person:
            for suffix in ['(politician)', '(military)', '(general)']:
                img_url = fetch_wikipedia_person_image(f"{person} {suffix}")
                if img_url:
                    break
    
    # Fall back to Pexels
    if not img_url and article.get('image_search_alt'):
        print(f"  → Trying Pexels for '{article['image_search_alt']}'...")
        img_url = fetch_pexels_image(article['image_search_alt'])
    
    # Upload to Supabase if we have an image
    final_img_url = None
    if img_url:
        slug = article['slug']
        ext = 'jpg'
        if '.png' in img_url.lower():
            ext = 'png'
        filename = f"{slug}.{ext}"
        final_img_url = upload_image_to_supabase(img_url, filename)
        
        # Validate
        if final_img_url and not validate_image_url(final_img_url):
            print(f"  ✗ Image validation failed, skipping image")
            final_img_url = None
    
    if not final_img_url:
        print(f"  ⚠ No image found — publishing without image (no image > wrong image)")
    
    # Prepare article data
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    
    data = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "body": article["body"],
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": now,
        "sources": json.loads(article["sources"]),
        "image_url": final_img_url,
        "image_attribution": "Wikimedia Commons" if (final_img_url and 'wikimedia' in str(img_url).lower()) else "The Videshi" if final_img_url else None,
    }
    
    result = sb_insert("p2_articles", data)
    if result:
        print(f"  ✓ Published: {article['slug']}")
        published_count += 1
    else:
        print(f"  ✗ Failed to publish: {article['slug']}")
    
    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {published_count}/{len(articles)} articles.")
