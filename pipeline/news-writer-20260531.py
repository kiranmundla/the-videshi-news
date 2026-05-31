#!/usr/bin/env python3
"""News writer for The Videshi — 2026-05-31 batch"""

import os, json, re, time, uuid, requests, urllib.parse
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
load_env(os.path.expanduser('~/workspace/.env.supabase'))
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
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
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
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    # Validate
                    check = requests.head(url, timeout=10)
                    if check.status_code == 200:
                        cl = int(check.headers.get('Content-Length', 0))
                        ct = check.headers.get('Content-Type', '')
                        if cl > 5000 and 'image' in ct:
                            print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                            return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Validate image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ Banned source detected: {b}")
            return False
    # Trust Wikipedia/Wikimedia URLs
    if 'upload.wikimedia.org' in url:
        print(f"  ✓ Trusted Wikimedia URL")
        return True
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "TheVideshi/1.0"})
        if r.status_code == 200:
            cl = int(r.headers.get('Content-Length', 0))
            ct = r.headers.get('Content-Type', '')
            if cl > 5000 and 'image' in ct:
                return True
            if cl == 0 and 'image' in ct:
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, CL={r.headers.get('Content-Length')}, CT={r.headers.get('Content-Type')}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def publish_article(article):
    """Publish an article to Supabase."""
    # Validate required fields
    assert len(article['headline']) >= 20, f"Headline too short: {article['headline']}"
    assert len(article['headline']) <= 200, f"Headline too long: {article['headline']}"
    assert len(article.get('subheadline', '')) >= 15, f"Subheadline too short or missing"
    assert len(article['body']) >= 400, f"Body too short: {len(article['body'])} chars"
    assert article['category'] == 'news', f"Wrong category: {article['category']}"
    assert not re.match(r'^[0-9a-f]{8}-', article['slug']), f"Slug looks like UUID: {article['slug']}"
    assert len(article.get('sources', [])) >= 2, f"Not enough sources: {len(article.get('sources', []))}"

    payload = {
        'id': str(uuid.uuid4()),
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': article['category'],
        'vertical': article.get('vertical', 'news'),
        'image_url': article.get('image_url'),
        'image_attribution': article.get('image_attribution'),
        'sources': json.dumps(article.get('sources', [])),
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat()
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload
    )
    if r.status_code in (200, 201):
        print(f"  ✓ Published: {article['headline']}")
        return True
    else:
        print(f"  ✗ Failed to publish: {r.status_code} - {r.text[:200]}")
        return False

# ============================================================
# ARTICLE 1: Delhi Saket Building Collapse
# ============================================================
print("\n📰 Article 1: Delhi Saket Building Collapse")

img1 = fetch_pexels_image("building collapse rescue India rubble", "rescue operation building debris")

article1 = {
    'headline': "A Building Collapsed Near Delhi's Saket Metro Station. At Least Four People Are Dead.",
    'subheadline': "A four-storey structure housing a coaching centre, cafes and offices came down without warning on Saturday evening. Rescue teams worked through the night.",
    'category': 'news',
    'vertical': 'news',
    'slug': 'delhi-saket-building-collapse-four-dead-coaching-centre-rescue-ndrf-20260531',
    'image_url': img1 if validate_image_url(img1) else None,
    'image_attribution': 'Pexels' if img1 else None,
    'sources': [
        {"name": "PTI via Swadesi News", "url": "https://swadesi.com"},
        {"name": "The Bharat Affairs", "url": "https://bharataffairs.com"},
        {"name": "India Today", "url": "https://www.indiatoday.in"},
        {"name": "hi INDiA (IANS)", "url": "https://hiindia.com"}
    ],
    'body': """The Delhi Fire Services received the call at 7.44 pm on Saturday. A four-storey building on Western Marg in Saidulajab — a congested neighbourhood barely a few hundred metres from the Saket Metro station — had collapsed without warning. The structure came down onto an adjacent tin-shed canteen where young students preparing for medical entrance exams were having dinner. Their evening ended under tonnes of concrete and twisted steel.

By Sunday morning, at least four people were confirmed dead and eight others had been pulled from the rubble, all of them admitted to the AIIMS Trauma Centre with injuries that officials described as serious. One of the dead, a 26-year-old man identified only as Ravi, was declared brought dead by the medical officer on duty. The names of the other deceased had not been released as rescue teams continued combing through debris.

The building housed a coaching institute on the ground floor along with cafes and offices. Construction work was reportedly underway on the upper floors at the time of the collapse — a detail that investigators are expected to examine closely. Preliminary assessments suggest the structure gave way suddenly, leaving its occupants almost no time to escape.

## The Rescue Operation

A multi-agency rescue operation began within minutes of the collapse. Delhi Fire Services dispatched three water tenders and an incident response team. The National Disaster Response Force deployed a specialised team with heavy cutting equipment and search dogs. The Delhi Disaster Management Authority, Delhi Police, civil defence units and local volunteers joined the operation, which continued through the night under floodlights.

Seven of the survivors were pulled out by NDRF and DDMA personnel. Two were rescued by local residents who reached the site before official teams. Eyewitnesses described screams rising from beneath the rubble as rescuers worked to clear concrete slabs and steel reinforcement bars. The narrow lanes of Saidulajab — barely wide enough for a single vehicle — complicated the effort, with ambulances struggling to reach the site.

Delhi Chief Minister Rekha Gupta visited the collapse site to oversee rescue operations and said the administration had deployed all available resources. An FIR has been registered against the building owner under provisions of culpable homicide, and police raids are underway to secure an arrest.

## A Familiar Tragedy

Building collapses are disturbingly common in Indian cities. Unauthorised construction, the illegal addition of floors to existing structures, the use of substandard materials and the failure of municipal authorities to enforce building codes have created a crisis that claims hundreds of lives each year.

In Delhi specifically, where land prices make every square foot valuable, builders routinely flout height restrictions and safety regulations. The Saidulajab building reportedly had construction underway on its upper floors — raising immediate questions about whether it had the necessary permits and whether structural assessments were conducted before additional loads were placed on the foundation.

The presence of a coaching centre and student cafes in the building adds another dimension to the tragedy. India's coaching industry — particularly for medical and engineering entrance examinations — operates in a vast grey zone of regulation, with institutes frequently occupying buildings that were never designed for the foot traffic and density they generate.

## What Comes Next

The rescue operation continued on Sunday, with authorities warning that the death toll could rise as teams cleared more debris. Structural engineers have been called in to assess adjacent buildings that may have been weakened by the collapse.

For the families of those trapped, the wait continues in the narrow lanes of Saidulajab. For the diaspora watching from abroad, the scene is grimly recognizable — another preventable tragedy in a city that builds faster than it can regulate. The question that follows every such collapse is whether this one will finally produce the enforcement reforms that decades of similar disasters have failed to deliver.

*The injured are identified as Tarun Kumar (26) of Gurugram, Saika Khan (27) from Bihar's Motihari, Neelam Yadav (25) of Saidulajab, Aditya Sharma (24) of Saket, Kshitij Pratap (25) of Noida, Anuj Dikshi (25) of Saket, Aastha (25) of Saidulajab and Vishal (24) of Saket.*"""
}

publish_article(article1)
time.sleep(1)

# ============================================================
# ARTICLE 2: DK Shivakumar — India's Richest CM
# ============================================================
print("\n📰 Article 2: DK Shivakumar to become India's Richest CM")

img2 = fetch_wikipedia_person_image("D. K. Shivakumar")
if not img2 or not validate_image_url(img2):
    img2 = fetch_wikipedia_person_image("D.K. Shivakumar")
if not img2 or not validate_image_url(img2):
    img2 = fetch_pexels_image("Karnataka state legislature Bengaluru Vidhana Soudha", "India politician government")
    img2_attr = 'Pexels'
else:
    img2_attr = 'Wikimedia Commons'

article2 = {
    'headline': "DK Shivakumar Will Be Sworn In as Karnataka CM on June 3. He Will Also Be India's Richest.",
    'subheadline': "The Congress leader's declared assets of ₹1,413 crore place him ahead of Chandrababu Naidu and Thalapathy Vijay. All three of India's wealthiest chief ministers are now from the south.",
    'category': 'news',
    'vertical': 'politics',
    'slug': 'dk-shivakumar-karnataka-cm-richest-1413-crore-assets-june-3-swearing-in-20260531',
    'image_url': img2 if validate_image_url(img2) else None,
    'image_attribution': img2_attr if img2 else None,
    'sources': [
        {"name": "The Bharat Affairs", "url": "https://bharataffairs.com"},
        {"name": "Association for Democratic Reforms (ADR)", "url": "https://adrindia.org"},
        {"name": "Dainik Bhaskar English", "url": "https://bhaskarenglish.in"},
        {"name": "NewsPoint", "url": "https://newspointapp.com"}
    ],
    'body': """DK Shivakumar will take the oath of office as Karnataka's Chief Minister on June 3 at the Glass House in Lok Bhavan, Bengaluru. The 64-year-old Congress leader was formally elected as the leader of the Karnataka Congress Legislature Party on Saturday, following the resignation of Siddaramaiah after three years in office — the completion of a reported power-sharing arrangement within the party.

When Shivakumar assumes office, he will carry a distinction beyond political rank. His declared family net worth of ₹1,413 crore will make him India's wealthiest sitting Chief Minister, surpassing Andhra Pradesh CM N Chandrababu Naidu (₹931 crore) and Tamil Nadu CM Thalapathy Vijay (₹648 crore). An analysis by the Association for Democratic Reforms based on election affidavits confirms the ranking. A striking detail: India's three richest chief ministers are now all from the south.

## The Fortune

Shivakumar's election affidavit presents a detailed picture of accumulated wealth. His personal assets are listed at ₹1,214.93 crore, comprising movable assets worth ₹251.69 crore and immovable properties valued at ₹972.65 crore. The family's combined declaration — including his wife's holdings — reaches the ₹1,413 crore headline figure, with total movable assets of ₹1,140 crore and immovable properties of ₹273 crore. Liabilities stand at approximately ₹265 crore.

The bulk of the wealth sits in real estate. He owns commercial buildings and office spaces worth ₹852 crore, including a major property at Pantharapalya in Bengaluru and the Vinayaka Touring Talkies in Kodihalli. Agricultural land across Kodihalli and Kanakapura Taluk is valued at ₹28.60 crore. Non-agricultural land in Bengaluru South, Mysore and Bhoopasandra is worth ₹60.53 crore. Residential holdings include a house in Krishna Nagar in Delhi and apartments on Palace Road in Bengaluru, together worth ₹18.51 crore.

The affidavit also records gold and silver holdings, luxury watches from Rolex and Hublot, and a single registered vehicle — a Toyota Qualis.

His business interests are centered on land development, real estate and construction enterprises, a portfolio that has grown substantially over his decades in Karnataka politics.

## The Political Journey

Shivakumar's ascent to the chief ministership is the culmination of a 37-year political career. He entered electoral politics in 1989 and has won multiple consecutive Assembly elections from the Kanakapura constituency. He served as Deputy Chief Minister in the Siddaramaiah government and simultaneously held the position of Karnataka Congress president — a dual role that gave him control over both governance and party machinery.

Within Congress, Shivakumar is regarded as the party's foremost Vokkaliga face in Karnataka. The Vokkaliga community — one of the state's most influential agrarian groupings — forms a critical pillar of the party's caste arithmetic in the state. His elevation is widely read as Congress balancing community representation by handing the top job to a leader rooted in the Vokkaliga base, after Siddaramaiah, a Kuruba, held office for three years.

Shivakumar is also known within the party as a crisis manager and "troubleshooter," a reputation built through years of managing defections, floor management and backroom negotiations. His role in the Congress party's return to power in Karnataka was widely acknowledged as central.

## Wealth and Power in Indian Politics

The ADR rankings present an uncomfortable but unavoidable portrait of Indian democracy. When Shivakumar takes office, the top tier of chief ministers by wealth will include three leaders whose combined declared assets exceed ₹2,990 crore. In the 2025 ADR list, after Naidu, Arunachal Pradesh CM Pema Khandu ranked third with ₹332 crore — a fraction of the wealth now concentrated in the south.

For Indian Americans watching from the diaspora, the figures are a reminder of the entanglement of political power and private wealth that defines much of Indian public life. Karnataka, which is home to Bengaluru's tech ecosystem — the same ecosystem that employs tens of thousands of NRIs and their families — is now led by a real estate billionaire who has navigated multiple legal challenges, including a 2017 income tax raid that recovered undisclosed assets and led to Enforcement Directorate investigations. Shivakumar has denied all charges of impropriety.

The swearing-in on June 3 will mark the formal completion of a transition that has been expected for months. What it will not settle is the broader question of whether the concentration of wealth in Indian politics strengthens or undermines the institutions those leaders are elected to serve."""
}

publish_article(article2)
time.sleep(1)

# ============================================================
# ARTICLE 3: Kasol Shooting
# ============================================================
print("\n📰 Article 3: Kasol Shooting — Tourist Fires at Local Youth")

img3 = fetch_pexels_image("Kasol valley Himachal Pradesh mountains Parvati", "Himachal Pradesh mountain village")

article3 = {
    'headline': "A Tourist Shot a Local Youth in Kasol Over a Parking Dispute. He Then Chased Him Down the Street With a Pistol.",
    'subheadline': "The shooting in Himachal Pradesh's most popular backpacker destination has renewed calls for a crackdown on violent tourists. Four suspects from Punjab have been arrested.",
    'category': 'news',
    'vertical': 'news',
    'slug': 'kasol-shooting-tourist-punjab-fires-local-youth-parking-dispute-himachal-arrests-20260531',
    'image_url': img3 if validate_image_url(img3) else None,
    'image_attribution': 'Pexels' if img3 else None,
    'sources': [
        {"name": "News89", "url": "https://news89.com"},
        {"name": "Northeast Herald", "url": "https://northeastherald.in"},
        {"name": "The News Himachal", "url": "https://thenewshimachal.com"},
        {"name": "Bhasha Times", "url": "https://bhashatimes.com"}
    ],
    'body': """The bullet hit the local youth in the leg at around 6 pm on Saturday in Kasol, a hamlet in Himachal Pradesh's Kullu district that has become one of North India's most popular tourist destinations. What followed was captured on video and has since gone viral: the injured man limping out of the Green Valley hotel's parking area, being carried to safety on another man's back, while the shooter — a tourist from Punjab — allegedly tried to reload his weapon and fire again before being restrained by his own companions.

The incident began, according to police, as an argument over parking at the hotel. The verbal exchange between a group of tourists from Punjab and local residents escalated into a physical confrontation. During the fight, one of the tourists pulled out a pistol and fired, hitting a young man from the nearby village of Bagiyanda in the leg.

Witnesses told local media that even as the injured man was being rushed to hospital, the armed tourist followed him down Kasol's narrow main road, brandishing the pistol in full view of shopkeepers, tourists and residents. The sound of the gunshot sent the crowded market into panic, with people scrambling for cover in what is ordinarily a laid-back backpacker village known for its cafes, mountain treks and a complicated relationship with recreational drugs.

## Four Arrested, One Absconding

Kullu police reached the scene shortly after the incident and detained four suspects. They have been identified as Manpreet Singh, 29, from Tarn Taran; Aman Randhawa, 22, from Amritsar; Sukhmandeep Singh, 17, from Ferozepur; and Karndeep Singh, 22, from Gurdaspur. A fifth suspect, identified as Taman from Gurdaspur, is currently absconding. Police have launched a search operation to locate him.

The weapon and the vehicle in which the group was travelling have been seized. An FIR has been registered under relevant sections of the Bharatiya Nyaya Sanhita and the Arms Act. Kullu Superintendent of Police Madan Lal Kaushal confirmed the arrests and said the incident stemmed from a parking dispute.

"Such incidents will not be tolerated in Himachal Pradesh," Kaushal said. "Any attempt to disturb law and order in Dev Bhoomi will be dealt with strictly."

The injured youth was rushed to Kullu Hospital, where he is undergoing treatment for the gunshot wound to his leg. His condition is reported to be stable.

## A Pattern, Not an Aberration

The Kasol shooting has triggered renewed outrage across Himachal Pradesh, where concerns about violent and unruly tourist behaviour have been building for years. As soaring temperatures across northern India drive millions of visitors to hill stations each summer, incidents of fights, vandalism, drunk driving and confrontations between tourists and locals have become increasingly frequent.

Kasol, in particular, occupies a fraught position. The village in the Parvati Valley has long been a magnet for both domestic and international backpackers, drawn by its mountain scenery, Israeli-influenced cafe culture and a reputation for easy availability of drugs. Local residents and business owners have watched their village transform from a quiet Himalayan hamlet into a high-traffic destination that brings both revenue and disorder.

The shooting has amplified voices that have long called for stricter regulation of tourist behaviour in the state. Demands include enhanced policing during peak season, mandatory vehicle registration and identity verification at entry points to sensitive areas, and a zero-tolerance policy toward visitors who carry weapons or engage in violence.

## The Tourism Dilemma

For Himachal Pradesh, tourism is both lifeline and liability. The state depends heavily on visitor spending — particularly during the summer months, when the plains become unbearable and hill stations fill to capacity. But the sheer volume of traffic has begun to overwhelm the infrastructure, policing and social fabric of small mountain communities.

For the Indian diaspora, many of whom plan summer trips to Kullu, Manali and the Parvati Valley when visiting family, the Kasol shooting is a stark reminder that the places they remember from childhood are changing. The village where travellers once sat in open-air cafes watching the Parvati River has become a place where a parking dispute can end with a gunshot — and a man being chased down the street by an armed stranger in broad daylight.

The viral videos from Saturday have ensured that this incident will not fade quietly. Whether it produces the policy response that residents are demanding remains an open question."""
}

publish_article(article3)

print("\n✅ News writer batch complete.")
