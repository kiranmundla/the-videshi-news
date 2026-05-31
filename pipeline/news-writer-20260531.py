#!/usr/bin/env python3
"""News writer for The Videshi — 2026-05-31 batch"""

import json, os, sys, uuid, re, time
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), val)

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

def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels API using curl (urllib gets 403)."""
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                img_url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{q}': {img_url[:80]}...")
                return img_url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Check image URL returns valid image with decent size."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD well
        r = requests.get(url, timeout=10, stream=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct:
            # Read first chunk to check size
            chunk = next(r.iter_content(8192), b'')
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False

def publish_article(article):
    """Insert article into Supabase."""
    article_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    payload = {
        'id': article_id,
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': article['category'],
        'status': 'published',
        'published_at': now,
        'created_at': now,
        'updated_at': now,
        'vertical': article.get('vertical', 'news'),
        'sources': json.dumps(article.get('sources', [])),
    }
    
    if article.get('image_url'):
        payload['image_url'] = article['image_url']
    if article.get('image_attribution'):
        payload['image_attribution'] = article['image_attribution']
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload
    )
    
    if r.status_code in (200, 201):
        result = r.json()
        aid = result[0]['id'] if isinstance(result, list) else result.get('id', article_id)
        print(f"  ✅ Published: {article['headline'][:60]}... (id: {aid})")
        return aid
    else:
        print(f"  ❌ Failed to publish: {r.status_code} {r.text[:200]}")
        return None

# ─── ARTICLE 1: Scripps Spelling Bee ──────────────────────────────────────
def write_spelling_bee():
    print("\n📝 Writing: Scripps Spelling Bee article...")
    
    headline = "An Indian American Kid Just Won the Scripps Spelling Bee. Again."
    subheadline = "Shrey Parikh, 14, from California shattered the spell-off record with 32 words in 90 seconds. The runner-up was also Indian American."
    slug = "shrey-parikh-wins-2026-scripps-spelling-bee-indian-american-record-spell-off-20260531"
    
    body = """Shrey Parikh does not get nervous once he sees the word. "Before I get the word, it's just like, what word am I gonna get?" the 14-year-old told reporters after winning the 2026 Scripps National Spelling Bee on Thursday night. "Once I get the word, I'm not really nervous anymore, because then it's all in my control."

That calm served him well. In a 90-second lightning-round spell-off at DAR Constitution Hall in Washington, D.C., Parikh correctly spelled 32 words — shattering the previous record of 29 set in 2024 — and clinched the title with "bromocriptine," a polypeptide alkaloid derived from ergot. The word rolled off his tongue like it was nothing.

His opponent in the final showdown was 12-year-old Ishaan Gupta from Jersey City, New Jersey, who managed an impressive 25 words in his own 90 seconds. Third place went to Sarv Dharavane, a 12-year-old from Dunwoody, Georgia, who finished third for the second consecutive year and still has two more years of eligibility.

All three finalists were of Indian origin. This is not a coincidence, and it has not been for a very long time.

## A Two-Decade Dynasty

Indian American kids have dominated the Scripps Bee for more than 20 years. The streak began in earnest with Nupur Lala's win in 1999, and since then, contestants of Indian origin have won 22 of the last 27 championships. The phenomenon is well-documented: a combination of a deeply competitive academic culture, organized study circuits within the Indian American community, structured coaching networks, and families that treat spelling preparation with the same seriousness as competitive math or science olympiads.

Parikh is a product of this ecosystem. An eighth-grader at Day Creek Intermediate School in Rancho Cucamonga, California, he first reached the national Bee in 2022, tying for 89th place. He returned in 2024 and tied for third — heartbreakingly close after blending two letters in a word. Then he missed the 2025 national competition entirely after faltering at his school bee.

"I was really dejected and just very upset," he said of that moment. "It didn't even sink in until the next day."

He took six months off. Then he went back to work.

## The Spell-Off

The 98th edition of the Bee started with 247 spellers from all 50 states, the District of Columbia, Guam, Puerto Rico, the U.S. Virgin Islands, and five other countries. By the finals, it was down to nine. After 18 grueling rounds of conventional spelling, the judges could not separate Parikh and Gupta, triggering only the third spell-off in the Bee's history.

The format is deliberately high-pressure. One contestant stays on stage while the other is sequestered in an isolated room wearing noise-canceling headphones. Both are given an identical word list in the same sequence. Then they have 90 seconds each to correctly spell as many words as possible.

Parikh was methodical and relentless. His pace was almost mechanical. "Spelling fast is what I do everyday, so a spell-off came naturally," he said. "It's just another day of spelling."

## The Diaspora Dimension

For Indian American families, the Spelling Bee is more than a competition. It is a gateway — proof that academic excellence can be a form of cultural identity in a country that often struggles to see Asian Americans as anything more than a monolithic "model minority."

The Bee circuit in the Indian American community has its own infrastructure: the South Asian Spelling Bee (SASB), regional competitions, WhatsApp study groups, word-list databases, and coaches who specialize in etymology and Latin roots. Families drive hours to regional bees. Kids study 3,000 to 5,000 words a year.

Parikh takes home the Scripps Cup, a $50,000 cash prize, $2,500 from Merriam-Webster, $1,000 in Delta Air Lines flight credits, reference works from Encyclopaedia Britannica, and a trip to Universal Studios Orlando.

He also visits India frequently to spend time with his grandparents. According to his Scripps biography, he plays percussion in his school band — snare drum, bass drum, timpani, toms, triangle, glockenspiel, and marimba — and recently qualified for the California state Mathcounts competition.

The Spelling Bee will be back next year. So will Dharavane, the third-place finisher from Georgia, who is only 12. And somewhere in the Indian American community, a kid with a word list and a dream is already preparing."""

    # Image sourcing — try Pexels for spelling bee
    img_url = fetch_pexels_image("spelling bee competition stage", "student spelling competition award")
    img_attribution = "Pexels"
    
    if img_url and not validate_image(img_url):
        print("  ⚠ Image validation failed, skipping image")
        img_url = None
    
    return {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'news',
        'image_url': img_url,
        'image_attribution': img_attribution,
        'source': 'The Videshi',
        'sources': [
            {"name": "New York Post", "url": "https://nypost.com"},
            {"name": "Bleacher Report", "url": "https://bleacherreport.com"},
            {"name": "Scripps National Spelling Bee", "url": "https://spellingbee.com"}
        ]
    }


# ─── ARTICLE 2: India's Monsoon Forecast ──────────────────────────────────
def write_monsoon():
    print("\n📝 Writing: Monsoon forecast article...")
    
    headline = "India Is Bracing for Its Driest Monsoon in 11 Years. Farmers Are Already Worried."
    subheadline = "The IMD now forecasts just 90 percent of normal rainfall this season. El Niño is building, the rupee is sliding, and two-thirds of the country still depends on rain-fed agriculture."
    slug = "india-imd-monsoon-forecast-2026-driest-11-years-el-nino-agriculture-inflation-20260531"
    
    body = """The India Meteorological Department has delivered the news that farmers, policymakers, and commodity traders had been dreading. In its second-stage long-range forecast released on May 29, the IMD projected that the 2026 southwest monsoon will bring only 90 percent of the Long Period Average rainfall — with a margin of error of plus or minus 4 percent. If the forecast holds, this will be India's driest monsoon since 2015, when rainfall came in at 86 percent of normal and triggered severe crop losses across the country.

The arithmetic is stark. Two-thirds of India's 1.4 billion people live in rural areas. More than half the country's net sown area is rain-fed, with no irrigation backup. When the monsoon fails, it does not just affect harvests. It reverberates through incomes, rural demand, consumer goods sales, and ultimately GDP.

## What Is Driving the Forecast

Two climate drivers are shaping the outlook. El Niño — the periodic warming of equatorial Pacific waters — is emerging and expected to strengthen through the monsoon season. Historically, El Niño years correlate strongly with below-normal Indian monsoons. The last consecutive drought years, 2014 and 2015, were both El Niño years.

The second variable is the Indian Ocean Dipole, the temperature differential between the Arabian Sea and the Bay of Bengal. A positive IOD can offset some of El Niño's suppressive effects on the monsoon. This year, the IMD expects the IOD to remain neutral — offering no counterbalance.

"The near-term outlook for the Indian economy is one of cautious resilience," the Finance Ministry said in its monthly report on Saturday, in what amounted to a carefully worded warning.

## Regional Breakdown

The damage will not be uniform. The IMD forecasts below-normal rainfall for Northwest India, Central India, South Peninsular India, and the critical Monsoon Core Zone — the belt of rain-fed agricultural land that produces much of India's food. Only Northeast India is expected to receive normal rainfall.

For June specifically, the picture is even worse. Rainfall is forecast to be below 92 percent of normal across most of the country, and the monsoon's arrival at the Kerala coast — which typically happens around June 1 — is expected to be delayed.

The IMD also warned of above-normal temperatures through June, with more heatwave days expected in Uttar Pradesh, Haryana, Punjab, Bihar, Odisha, Chhattisgarh, Gujarat, and Andhra Pradesh. Parts of northern India have already been recording temperatures above 47°C.

## The Economic Cascade

A weak monsoon triggers a predictable chain reaction. Pulses, cotton, oilseeds, and coarse grains — all planted early in the monsoon season — face the most immediate risk. Rice paddy is vulnerable in non-irrigated areas across the north and northwest. India is the world's largest exporter of rice and onions and the second-largest producer of sugar, so domestic shortfalls quickly ripple into global commodity markets.

"Below-normal rainfall could affect early-season planting of pulses, cotton, edible oilseeds and coarse grains such as corn," said Ashwini Bansod, vice president for commodities research at Phillip Capital India.

The Finance Ministry's report highlighted an additional complication: the Strait of Hormuz disruption, which it called the "single most consequential variable" for India's price outlook. With crude oil prices elevated by the Middle East conflict and the rupee under pressure, fuel price hikes are already passing through to transport, energy, and food costs. A weak monsoon on top of that creates a compounding effect.

India's retail inflation currently sits at 3.48 percent — comfortably below the RBI's 4 percent target. But economists expect it to climb above 5 percent this fiscal year, breaching the RBI's projection of 4.6 percent. The RBI's Monetary Policy Committee meets on June 5 to decide on interest rates, and the monsoon forecast will weigh heavily on that decision.

## What India Has in Its Favor

There is some resilience built into the system. India holds sufficient stockpiles of rice and wheat, which provides a buffer against immediate food shortages. Irrigation coverage has expanded significantly over the past decade. And the government has learned from past droughts — the 2015 experience prompted investments in crop insurance, buffer stocks, and early warning systems.

But these buffers have limits. Lower rural incomes dampen sales of everything from motorcycles to refrigerators, dragging on broader economic growth. Consumer companies that depend on rural India — from FMCG giants to two-wheeler manufacturers — are already factoring in a tough quarter.

The monsoon is India's annual referendum on vulnerability. Despite all the talk of a $4 trillion economy and semiconductor missions and nuclear power expansion, the country's agricultural backbone still depends on rain falling from the sky at the right time, in the right amount, in the right places. This year, the sky is not cooperating."""

    # Image sourcing — try Pexels for monsoon/farming
    img_url = fetch_pexels_image("Indian farmer monsoon rain field", "rice paddy field India agriculture")
    img_attribution = "Pexels"
    
    if img_url and not validate_image(img_url):
        print("  ⚠ Image validation failed, skipping image")
        img_url = None
    
    return {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'news',
        'image_url': img_url,
        'image_attribution': img_attribution,
        'source': 'The Videshi',
        'sources': [
            {"name": "Reuters", "url": "https://reuters.com"},
            {"name": "India Meteorological Department", "url": "https://mausam.imd.gov.in"},
            {"name": "The Hindu BusinessLine", "url": "https://thehindubusinessline.com"},
            {"name": "Livemint", "url": "https://livemint.com"}
        ]
    }


# ─── ARTICLE 3: BRICS Foreign Ministers Meeting ──────────────────────────
def write_brics():
    print("\n📝 Writing: BRICS Foreign Ministers article...")
    
    headline = "India Just Hosted Every BRICS Foreign Minister in Delhi. The Agenda Was Bigger Than Anyone Expected."
    subheadline = "From MSME technology access to alternative payment systems, India's BRICS chairship is shaping up as its most ambitious multilateral play in years. The leaders' summit is in September."
    slug = "india-brics-2026-chairship-foreign-ministers-delhi-msme-technology-payment-summit-20260531"
    
    body = """India is not just hosting the next BRICS summit. It is trying to reshape what BRICS means.

In the span of two weeks, New Delhi has convened a foreign ministers' meeting, an SME working group focused on technology access for small businesses, and a series of preparatory sessions that reveal the scale of India's ambitions for its 2026 chairship. The 18th BRICS Summit, scheduled for September 12–13, will be chaired by Prime Minister Narendra Modi. The groundwork being laid right now suggests India wants it to be more than a photo opportunity.

## The Foreign Ministers' Meeting

Between May 14 and 15, foreign ministers from all BRICS member states — Brazil, Russia, India, China, South Africa, Egypt, Ethiopia, Indonesia, Iran, and the United Arab Emirates — gathered in Delhi. External Affairs Minister S. Jaishankar used the platform to position India as a bridge between the bloc's competing interests.

The headline numbers are impressive. Intra-BRICS trade has surged from $89 billion in 2004 to $1.17 trillion in 2024 — a thirteen-fold increase. But Jaishankar also acknowledged the gap between ambition and reality: intra-BRICS trade still accounts for only about 5 percent of global trade.

"Resilient supply chains," "technology transfer," and "equitable participation" were recurring themes — diplomatic language for a shared anxiety about dependence on Western-controlled financial systems and supply chains. The subtext is clear: BRICS countries want alternatives, and India wants to be the one building them.

Delegates also visited Gujarat International Finance Tec-City (GIFT City), which India is positioning as a future global financial hub. The symbolism was deliberate.

## The MSME Technology Push

On May 26, India convened the second SME Working Group meeting under the BRICS Partnership on the New Industrial Revolution (PartNIR). The theme: "Enhancing Access to Technology for MSMEs."

This is not glamorous diplomacy. It is practical, ground-level economic coordination — and it matters enormously. MSMEs account for the bulk of employment and GDP in most BRICS economies. In India alone, MSMEs employ over 110 million people and contribute roughly 30 percent of GDP.

The working group discussions focused on three areas: harnessing innovations and technology commercialization for MSMEs, skilling and developing industry-ready workforces, and bridging the digital inclusion gap that leaves small businesses locked out of global value chains.

India plans to host three SME meetings and the inaugural BRICS MSME Forum during its chairship year. The Ministry of MSME described the discussions as centering on "deeper collaboration among BRICS economies in technology access, innovation ecosystems, and skills development."

## The Bigger Picture

India's BRICS chairship comes at a complicated moment. The bloc has expanded rapidly — adding Egypt, Ethiopia, Indonesia, Iran, and the UAE as members — but that expansion has also introduced new fault lines. Iran and the UAE have different interests. China and India have an unresolved border dispute. Russia is at war in Ukraine.

India is navigating these tensions by focusing on economic cooperation rather than geopolitical grandstanding. The chairship theme — "Building for Resilience, Innovation, Cooperation and Sustainability" — is deliberately anodyne. The substance underneath it is not.

The BRICS de-dollarization conversation continues to evolve. Russia, China, and India are exploring CBDC interoperability — linking the digital ruble, yuan, and rupee as an alternative to SWIFT. The New Development Bank is targeting one-third of all loans in member nations' domestic currencies by 2026. BRICS Pay has already reduced USD usage in intra-bloc trade significantly.

But India is careful not to overplay this hand. Jaishankar clarified the bloc's official position in March: "I don't think there's any policy on our part to replace the dollar. The dollar as the reserve currency is the source of global economic stability, and right now what we want in the world is more economic stability, not less."

## What Comes Next

The September summit will bring all BRICS leaders to India. Modi has personally invited Chinese President Xi Jinping. Whether Xi attends — and what bilateral conversations happen on the margins — will be closely watched.

For the Indian diaspora, BRICS matters for pragmatic reasons. Alternative payment systems could make remittances cheaper. MSME technology partnerships could open new export markets. And India's credibility as a convener of the Global South has direct implications for how the country — and its diaspora — is perceived on the world stage.

India assumed the BRICS chair on January 1, 2026, succeeding Brazil. The official logo and website were launched on January 13. The machinery has been running for five months. The September summit will be the test of whether it produced anything that outlasts the presidency."""

    # Image sourcing — try Wikipedia for Jaishankar
    img_url = fetch_wikipedia_person_image("S. Jaishankar")
    img_attribution = "Wikimedia Commons"
    
    if not img_url:
        img_url = fetch_pexels_image("international diplomatic summit meeting", "world leaders conference")
        img_attribution = "Pexels"
    
    if img_url and not validate_image(img_url):
        print("  ⚠ Image validation failed, skipping image")
        img_url = None
    
    return {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'news',
        'image_url': img_url,
        'image_attribution': img_attribution,
        'source': 'The Videshi',
        'sources': [
            {"name": "ANI", "url": "https://aninews.in"},
            {"name": "Devdiscourse", "url": "https://devdiscourse.com"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com"},
            {"name": "Wikipedia - 18th BRICS Summit", "url": "https://en.wikipedia.org/wiki/18th_BRICS_summit"}
        ]
    }


# ─── MAIN ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("The Videshi — News Writer (2026-05-31)")
    print("=" * 60)
    
    articles = [
        write_spelling_bee(),
        write_monsoon(),
        write_brics(),
    ]
    
    published = 0
    for article in articles:
        aid = publish_article(article)
        if aid:
            published += 1
        time.sleep(1)
    
    print(f"\n{'=' * 60}")
    print(f"Done. Published {published}/{len(articles)} articles.")
    print(f"{'=' * 60}")
