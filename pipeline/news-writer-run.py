#!/usr/bin/env python3
"""News writer - 2026-06-01 evening run. Publishes 3 articles."""

import json, os, sys, time, uuid, re, urllib.parse
import requests

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                key = key.replace('export ', '').strip()
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (Python urllib gets 403)."""
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            cmd = [
                'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                photos = data.get('photos', [])
                if photos:
                    url = photos[0]['src']['large2x']
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 with image content type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {r.status_code}, {ct}, {cl} bytes")
            return True
        # Try GET if HEAD fails
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct:
            # Read a chunk to verify size
            chunk = r.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {r.status_code}, {ct}")
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def publish_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article)
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Published: {data[0].get('headline', '?')[:60]}...")
            return True
        elif isinstance(data, dict):
            print(f"  ✓ Published: {data.get('headline', '?')[:60]}...")
            return True
    print(f"  ✗ Publish failed ({r.status_code}): {r.text[:200]}")
    return False

def word_count(text):
    return len(text.split())

# ============================================================
# ARTICLE 1: Delhi Saket Building Collapse
# ============================================================
print("\n=== ARTICLE 1: Delhi Saket Building Collapse ===")

img1 = fetch_pexels_image("building collapse rescue India debris", "collapsed building rubble rescue workers")
if img1 and not validate_image(img1):
    img1 = None

article1_body = """A three-storey commercial building near the Saket Metro Station in south Delhi collapsed on Saturday evening, killing six people and injuring eight others in one of the deadliest structural failures the city has seen this year.

The building, located on Western Marg in the Saidulajab area, housed a coaching institute, cafes, offices, and a tin shed canteen on its ground floor that served students preparing for medical entrance examinations. Construction work was reportedly underway on the upper floors when the structure gave way around 6 PM on May 30.

## A Night of Rescue

Rescue teams from the National Disaster Response Force, Delhi Fire Services, the Delhi Disaster Management Authority, and local police deployed heavy machinery, hydraulic cutters, victim-location cameras, and sniffer dogs to comb through the rubble. The operation continued for more than 24 hours.

Nine people were pulled alive from the debris and rushed to AIIMS Trauma Centre and Safdarjung Hospital. A green corridor was established to ensure unhindered ambulance movement from the site. Two of the injured were later discharged after receiving first aid, while five others remained in critical condition.

## The Dead and the Mourning

Among the six killed was Parvati, who ran the canteen on the premises. Her daughter Neelam told PTI that her mother had initially escaped the building after signs of collapse became evident — but went back inside to help students still trapped in the rubble.

"I asked her to open the canteen, but now I regret it," Neelam said. She alleged that the family had previously noticed pieces of concrete falling from parts of the building and had raised concerns about its structural condition. "The real fault lies with the building owner," she said, adding that construction materials had occasionally fallen during ongoing work on the upper floors.

## Owner Absconding, Engineers Suspended

Delhi Police registered an FIR under several sections related to culpable homicide and negligence against the building owner, who remains absconding as of Monday evening. Multiple police teams are searching for him.

The Municipal Corporation of Delhi suspended two engineers for oversight failures, confirming that early findings point to potential infrastructural lapses and regulatory violations. The structure was reportedly unauthorised, according to officials at the scene.

Chief Minister Rekha Gupta visited the site on Sunday to review the rescue operations and ordered strict action against unauthorised structures and the officials who enabled them.

## A Pattern That Keeps Repeating

Building collapses remain a persistent risk across Indian cities, particularly in areas where unauthorised construction is rampant. Poor construction materials, inadequate foundations, and the pressure to add floors to existing structures have all been cited as recurring causes. In Delhi, where land commands a premium, the incentive to build beyond sanctioned limits often outweighs the fear of enforcement.

The Saket collapse has renewed demands for a comprehensive audit of commercial buildings in south Delhi, particularly those housing coaching centres and student-facing businesses where occupancy is high and evacuation routes are often narrow.

## What the Diaspora Should Know

For NRIs with family members preparing for competitive exams in coaching hubs across Delhi, Kota, and Hyderabad, the collapse is a grim reminder of the safety conditions students often endure. Many coaching centres operate out of buildings that were never designed or approved for high-occupancy commercial use. Parents calling from abroad have limited ability to verify the structural safety of facilities their children use daily — a gap that no government inspection regime has yet closed."""

wc1 = word_count(article1_body)
print(f"  Word count: {wc1}")

article1 = {
    "headline": "A Building Near Delhi's Saket Metro Collapsed on Saturday. Six People Are Dead and the Owner Is Missing.",
    "subheadline": "Rescue teams pulled survivors from the rubble for 24 hours. The structure housed a coaching centre, cafes, and a canteen that served medical aspirants.",
    "body": article1_body.strip(),
    "slug": "delhi-saket-building-collapse-six-dead-owner-absconding-fir-culpable-homicide-20260601",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": "2026-06-01T18:30:00Z",
    "sources": [
        {"name": "PTI via Swadesi News", "url": "https://swadesi.com"},
        {"name": "ANI via LatestLY", "url": "https://latestly.com"},
        {"name": "Devdiscourse", "url": "https://devdiscourse.com"}
    ],
    "vertical": "news",
    "image_url": img1 or "",
    "image_attribution": "Pexels" if img1 else ""
}

# ============================================================
# ARTICLE 2: Rajya Sabha Elections - 27 Seats
# ============================================================
print("\n=== ARTICLE 2: Rajya Sabha Elections 27 Seats ===")

img2 = fetch_pexels_image("Indian parliament building New Delhi", "India Rajya Sabha parliament")
if img2 and not validate_image(img2):
    img2 = None

article2_body = """The Election Commission of India on Monday formally kicked off the process for elections to 27 Rajya Sabha seats and multiple state Legislative Council seats across the country, setting June 18 as the date for polling and counting.

The nomination process began at 11 AM on June 1. Candidates have until June 8 to submit their papers. Scrutiny of nominations will take place on June 9, with the final date for withdrawal of candidature fixed as June 11. If contests remain, polling will be held on June 18 from 8 AM to 4 PM, with counting beginning at 5 PM the same day.

## The Scale of the Contest

The elections cover biennial vacancies for 24 Rajya Sabha seats across 10 states — Andhra Pradesh (4), Gujarat (4), Karnataka (4), Madhya Pradesh (3), Rajasthan (3), Jharkhand (2), and one each in Manipur, Meghalaya, Arunachal Pradesh, and Mizoram. Additionally, bye-elections will fill vacancies in Maharashtra, Tamil Nadu, and Odisha.

In Maharashtra, the seat fell vacant after Sunetra Pawar resigned from the Rajya Sabha following her win in the Baramati by-election earlier this year. In Odisha, BJD's Debashish Samantaray resigned on May 25, creating a vacancy that BJP is expected to fill. In Tamil Nadu, AIADMK's C.V. Shanmugam vacated his seat after being elected to the state assembly.

Beyond the Rajya Sabha, the Election Commission has also announced elections for nine Legislative Council seats in Bihar and seven in Karnataka, along with a by-election for one Bihar Legislative Council seat vacated by former Chief Minister Nitish Kumar.

## The Political Math

For the NDA coalition, the arithmetic is favourable in several states. In Gujarat, Madhya Pradesh, and Rajasthan — all BJP-ruled — the ruling party is expected to sweep its quota of seats comfortably. In Karnataka, where the BJP-JD(S) alliance holds a majority, the NDA should secure most of the four seats on offer.

The real contest will play out in Jharkhand, where both the ruling JMM-Congress alliance and the BJP have staked claims. The JMM-led INDIA bloc, with 56 members in the 81-seat assembly, argues that both seats should go to them since each candidate needs 28 first-preference votes to win. The ruling alliance wrote to the Election Commission on May 26, flagging concerns about potential horse trading.

The BJP has already announced it will field a candidate for one of the two Jharkhand seats. Congress, part of the ruling alliance, has also staked a claim to one — setting up a potential intra-alliance negotiation that will be closely watched.

## Why It Matters for the Upper House

Every Rajya Sabha election shifts the balance of power in India's upper chamber. The BJP-led NDA has been steadily building its strength in the Rajya Sabha over the past decade, but it still does not command a clear majority on its own. The outcome of these 27 seats — along with the Legislative Council results — will determine whether the ruling alliance moves closer to that threshold or whether the opposition INDIA bloc can hold its current position.

For bills that require passage in both houses, the composition of the Rajya Sabha remains decisive. Key legislative battles — including potential amendments to the Waqf Act, the proposed Uniform Civil Code, and pending judicial reform bills — all depend on the government's Upper House numbers.

## What the Diaspora Should Know

The Rajya Sabha elections are decided by state legislators, not the general public — which means they reflect the cumulative outcome of recent assembly elections rather than a fresh public mandate. For NRIs tracking Indian politics, these elections are a useful barometer of how India's political coalitions are consolidating after the 2024 general election and the assembly polls that followed. The results on June 18 will clarify the legislative roadmap for the Modi government's remaining term."""

wc2 = word_count(article2_body)
print(f"  Word count: {wc2}")

article2 = {
    "headline": "India Just Began Nominations for 27 Rajya Sabha Seats. The Votes Will Be Cast on June 18.",
    "subheadline": "The elections span 10 states and three by-elections. The real fight is in Jharkhand, where the ruling alliance and the BJP both want both seats.",
    "body": article2_body.strip(),
    "slug": "rajya-sabha-27-seats-nominations-begin-june-18-polling-jharkhand-nda-india-bloc-20260601",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": "2026-06-01T18:35:00Z",
    "sources": [
        {"name": "Election Commission of India via News Ei Samay", "url": "https://newseisamay.com"},
        {"name": "PTI via Swadesi News (Jharkhand)", "url": "https://swadesi.com"},
        {"name": "PingTV India", "url": "https://pingtvindia.com"}
    ],
    "vertical": "news",
    "image_url": img2 or "",
    "image_attribution": "Pexels" if img2 else ""
}

# ============================================================
# ARTICLE 3: MAHA Water Mission + ISRO MoU
# ============================================================
print("\n=== ARTICLE 3: MAHA Water Mission + ISRO MoU ===")

# Try Wikipedia for Jitendra Singh or C.R. Patil
img3 = fetch_wikipedia_person_image("C. R. Patil")
if not img3 or not validate_image(img3):
    img3 = fetch_wikipedia_person_image("Jitendra Singh (politician)")
    if not img3 or not validate_image(img3):
        img3 = fetch_pexels_image("satellite water management India", "India water innovation technology")
        if img3 and not validate_image(img3):
            img3 = None

article3_body = """The Indian government on Monday launched a ₹200 crore programme to fund water technology startups and signed a landmark agreement with ISRO to bring satellite-based monitoring to the country's water management infrastructure.

The Mission for Advancement in High-Impact Areas for Water — known as MAHA Water — was unveiled at a national workshop on water research and development at Dr. Ambedkar International Centre in New Delhi. The programme is jointly run by the Anusandhan National Research Foundation and the Ministry of Jal Shakti.

## How the Money Will Work

The ₹200 crore outlay will be spread over five years, jointly contributed by ANRF and the Ministry of Jal Shakti. Selected multidisciplinary consortia — which can include universities, national laboratories, research organisations, startups, MSMEs, and industry partners — will be eligible for up to ₹20 crore each.

The funds can be used for technology development, field assessment, validation, and deployment of water solutions. An open call for research proposals was announced at the launch, alongside a separate open call for startups and MSMEs through the BHARAT-WIN Portal for product and prototype development.

## Five Priority Themes

The mission will focus on five areas: water resource assessment and sustainable management; drinking water quality and access; water quality and ecological health; water use efficiency and the circular economy; and climate resilience and adaptation.

"ANRF is democratising research funding by expanding opportunities for startups, MSMEs, universities and innovators," said Dr. Jitendra Singh, Union Minister of State for Science and Technology, who launched the mission. "National missions, scientific resources and innovation support are no longer confined to a limited number of institutions."

## ISRO Enters the Water Sector

In a parallel development at the same event, the Department of Water Resources and the Department of Space signed a memorandum of understanding to deepen cooperation on satellite-based water management. ISRO Chairman V. Narayanan said the partnership will support groundwater assessment, water resource monitoring, and flood forecasting.

"Space technology today offers unprecedented capacity for observing, assessing, forecasting and managing water resources," Narayanan said, adding that ISRO has been working with the water sector since 1982 but that the formal MoU marks a new phase of structured collaboration.

The event also saw the launch of the Jal Sanchay Jan Bhagidari portal and app — a citizen tracking and reporting platform designed to crowdsource water conservation data from the ground level.

## The Scale of India's Water Challenge

India faces a water crisis that is simultaneously a drought problem, a pollution problem, and a governance problem. The country is home to 18 percent of the world's population but only 4 percent of its freshwater resources. Groundwater — which supplies 85 percent of drinking water in rural areas — is being depleted faster than it can recharge across large parts of northern and western India.

The monsoon season, which is forecast to be the driest in a decade due to El Niño conditions, will put additional pressure on an already strained system. The government's decision to invest ₹200 crore in research and innovation is modest relative to the scale of the challenge, but it signals an effort to move beyond traditional engineering solutions toward technology-driven approaches.

## What the Diaspora Should Know

For NRIs with ancestral homes in water-stressed regions — particularly in Rajasthan, Punjab, Tamil Nadu, and Maharashtra — the MAHA Water Mission represents an opportunity for engagement. The open call for startups explicitly includes MSMEs and private-sector innovators, creating a pathway for diaspora-funded or diaspora-founded ventures to participate in India's water infrastructure buildout. The ISRO partnership also opens doors for remote sensing and data analytics ventures that can operate across borders."""

wc3 = word_count(article3_body)
print(f"  Word count: {wc3}")

article3 = {
    "headline": "India Just Launched a ₹200 Crore Fund for Water Tech Startups and Signed an MoU With ISRO to Monitor Water From Space.",
    "subheadline": "The MAHA Water Mission will fund consortia of universities, labs, and startups with up to ₹20 crore each. ISRO will bring satellite data to groundwater and flood forecasting.",
    "body": article3_body.strip(),
    "slug": "india-maha-water-mission-200-crore-isro-mou-satellite-water-management-startups-20260601",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": "2026-06-01T18:40:00Z",
    "sources": [
        {"name": "IANS via Dailyworld", "url": "https://dailyworld.in"},
        {"name": "Madhyamam Online", "url": "https://madhyamamonline.com"},
        {"name": "India Education Diary", "url": "https://indiaeducationdiary.in"}
    ],
    "vertical": "news",
    "image_url": img3 or "",
    "image_attribution": "Wikimedia Commons" if (img3 and 'wiki' in str(img3).lower()) else ("Pexels" if img3 else "")
}

# ============================================================
# PUBLISH ALL
# ============================================================
print("\n=== PUBLISHING ===")
success = 0
for i, article in enumerate([article1, article2, article3], 1):
    print(f"\nArticle {i}: {article['headline'][:60]}...")
    if not article['image_url']:
        print("  ⚠ No image found — publishing without image")
    if publish_article(article):
        success += 1
    time.sleep(1)

print(f"\n=== DONE: {success}/3 articles published ===")
