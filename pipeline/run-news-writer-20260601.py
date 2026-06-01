#!/usr/bin/env python3
"""
News writer for The Videshi — 2026-06-01 batch (fixed)
"""

import json, os, sys, uuid, requests, subprocess, urllib.parse
from datetime import datetime, timezone

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
                print(f"  ✓ Wikipedia image: {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error: {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            encoded_q = urllib.parse.quote(q)
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={encoded_q}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                print(f"  ⚠ Pexels curl error: {result.stderr[:100]}")
                continue
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image: {url[:80]}...")
                    return url
            print(f"  ⚠ Pexels: no photos for '{q}'")
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct:
            if cl > 5000:
                print(f"  ✓ Image OK: {cl} bytes")
                return True
            if cl == 0:
                r2 = requests.get(url, timeout=10, stream=True,
                                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
                chunk = r2.raw.read(6000)
                r2.close()
                if len(chunk) > 5000:
                    print(f"  ✓ Image OK via GET: {len(chunk)}+ bytes")
                    return True
        print(f"  ✗ Image failed: {r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image error: {e}")
    return False

def create_topic(title, category):
    topic = {
        "id": str(uuid.uuid4()),
        "canonical_title": title[:200],
        "vertical": "politics",
        "urgency": "daily",
        "score_diaspora": 70,
        "score_significance": 75,
        "score_recency": 90,
        "score_source_avail": 80,
        "score_total": 78,
        "signal_count": 3,
        "status": "published",
        "keywords": title.split()[:5],
        "category": category
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_topics",
        headers=HEADERS,
        json=topic
    )
    if r.status_code in (200, 201):
        print(f"  ✓ Topic created: {topic['id']}")
        return topic['id']
    else:
        print(f"  ✗ Topic insert failed ({r.status_code}): {r.text[:200]}")
        return None

def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) and data else 'unknown'
        print(f"  ✓ Article published: {article['slug']}")
        return art_id
    else:
        print(f"  ✗ Article insert failed ({r.status_code}): {r.text[:300]}")
        return None

def count_words(text):
    return len(text.split())

# ============================================================
# ARTICLE 1
# ============================================================
def write_article_1():
    print("\n=== Article 1: India Manufacturing PMI ===")
    
    headline = "India's Factories Are Running Faster Than They Have in Three Months. The War Is Making Everything More Expensive."
    subheadline = "The HSBC India Manufacturing PMI rose to 55.0 in May on strong domestic demand, but input costs hit a near four-year high as the Middle East war pushes up energy and fuel prices."
    slug = "india-manufacturing-pmi-55-may-2026-three-month-high-cost-pressures"
    
    body = """India's manufacturing sector expanded at its fastest pace in three months in May, defying a punishing rise in input costs that firms are struggling to pass on to customers.

The HSBC India Manufacturing Purchasing Managers' Index, compiled by S&P Global, came in at 55.0 for May — up from 54.7 in April and comfortably above the flash estimate of 54.3. Any reading above 50 signals expansion. The final print marked the strongest improvement in factory conditions since February.

## Domestic Demand Is Doing the Heavy Lifting

New orders — the most closely watched forward-looking component — grew at the fastest clip since February. Civil engineering projects, competitive pricing, and broadly favorable demand conditions drove the acceleration. But the demand engine is running on one cylinder more than the other: domestic orders surged while export order growth slowed to a three-month low.

Factory output rose at its quickest pace in three months, led by intermediate and capital goods producers. Consumer goods makers, however, saw growth ease — an early sign that the cost squeeze may be filtering through to household-facing businesses.

Hiring continued, though the pace of job creation slowed from April. Companies added workers but were cautious about headcount expansion as margins tightened.

## The War Is in the Numbers

Input price inflation was the second-strongest in roughly four years, trailing only April's reading. Higher outlays for energy, fuel, raw materials, and transportation drove the spike, with survey respondents explicitly citing the Middle East conflict — now in its fourth month — as a contributing factor.

Capital goods producers bore the sharpest cost increases among the three sub-sectors tracked, a worrying signal for investment-heavy industries.

Yet selling price inflation actually eased from April. Competitive pressures prevented firms from passing on the full cost burden to buyers, compressing margins. That gap between what factories are paying and what they can charge is the central tension in India's manufacturing story right now.

## Stockpiling Continues as War Drags On

Despite the cost squeeze, manufacturers sharply increased purchasing activity at the fastest rate in three months — partly to build contingency stocks. Pranjul Bhandari, Chief India Economist at HSBC, called it "another month of possible precautionary stockpiling as the Middle East conflict remains unresolved."

Finished goods inventories also rose at a faster clip, suggesting firms are building buffers against potential supply chain disruptions tied to the Strait of Hormuz closure.

## Optimism Hits a Ceiling

Business confidence fell to its lowest level since February, though it remained in positive territory. Companies expressed hope that cost pressures would eventually ease, supported by strong order pipelines and marketing efforts.

The data lands on a critical week for India's economy. The RBI's Monetary Policy Committee meets June 3-5, with most economists expecting the repo rate to hold at 5.25 percent. The central bank faces a delicate balancing act: inflation remains below 4 percent, but crude oil at $92 per barrel and a rupee that has depreciated over 5 percent since February are creating imported inflation pressures that could accelerate sharply if the Strait of Hormuz disruption continues.

For NRI investors tracking the Indian economy from abroad, the PMI data offers a nuanced picture: the factory floor is busy, order books are full, but margins are under siege from a war that shows no sign of ending. The January-March GDP data, due Friday alongside the RBI decision, will reveal whether that resilience is translating into broader economic growth — or whether the war's drag is starting to bite.

*Sources: S&P Global/HSBC India PMI, Reuters, IANS, The Hindu BusinessLine*"""

    topic_id = create_topic(headline, "news")
    if not topic_id:
        return None

    img_url = fetch_pexels_image("factory manufacturing production", "industrial machinery workers")
    if img_url and not validate_image(img_url):
        img_url = None
    
    article = {
        "topic_id": topic_id,
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_attribution": "Pexels" if img_url else None,
        "sources": ["S&P Global/HSBC India PMI", "Reuters", "IANS", "The Hindu BusinessLine"],
        "word_count": count_words(body),
        "is_editorial": False,
        "is_featured": False,
        "diaspora_angle": "For NRI investors and professionals tracking the Indian economy, the PMI data shows a factory sector running hot on domestic demand but squeezed by war-driven energy costs — a tension that will shape RBI rate decisions and rupee trajectory in coming months.",
        "vertical": "politics",
        "tags": ["manufacturing", "PMI", "HSBC", "Indian economy", "Middle East war", "RBI", "cost inflation"],
        "urgency": "daily"
    }
    return insert_article(article)

# ============================================================
# ARTICLE 2
# ============================================================
def write_article_2():
    print("\n=== Article 2: Jensen Huang Computex / Vera CPU ===")
    
    headline = "Jensen Huang Just Unveiled the Chip That Could Power Every AI Agent on Earth. He Says It Will Not Cost a Single Engineer Their Job."
    subheadline = "At Computex in Taipei, Nvidia announced its Vera CPU for AI agents — with OpenAI, Anthropic, and SpaceX as early adopters — and a new line of AI-powered laptops built on its RTX Spark chip."
    slug = "jensen-huang-computex-2026-vera-cpu-ai-pcs-nvidia-150-billion-taiwan"
    
    body = """Jensen Huang walked onto the stage at Taipei's Music Hall in his signature black leather jacket and did what he has done every year since Nvidia became the most profitable company in the world: he redrew the map of computing.

The Nvidia CEO's GTC Taipei keynote, delivered ahead of the Computex trade show on Monday, centered on two announcements that could reshape the AI industry's next phase — and directly affect the millions of Indian-origin engineers who build on Nvidia's platforms.

## Vera: The CPU Built for a World of AI Agents

The headline product is Vera, a central processing unit designed specifically for AI agents — the autonomous bots that are rapidly replacing conversational chatbots as the dominant form of AI usage. During Nvidia's May earnings call, Huang had described Vera as giving the company access to a "$200 billion market." On Monday, he named its first customers: OpenAI, Anthropic, and SpaceX.

"This is going to be our new major growth driver," Huang said.

The strategic shift is significant. Nvidia built its $5 trillion valuation on graphics processing units that train large language models. But as AI moves from training to inference — and from chatbots to autonomous agents performing tasks without human prompting — the computational bottleneck is shifting to CPUs. Vera is Nvidia's play for that transition.

## AI PCs: 30 Laptop Models, RTX Spark Inside

Nvidia also introduced the RTX Spark, which it called "the most efficient PC chip ever built." The chip will power a new category of laptops designed to run AI agents locally — not in the cloud.

Six manufacturers — Dell, Lenovo, Microsoft, HP, Asus, and MSI — will build about 30 laptop models and 10 desktop models using RTX Spark. The thinnest devices will be 14 millimeters thick and weigh under three pounds.

The laptops are "targeted at creators, AI developers and gamers" and will sit at the premium end of the market, according to Mark Aevermann, Nvidia's senior director of product development. For the hundreds of thousands of Indian-origin developers working in Silicon Valley and Bangalore, these machines represent a shift from cloud-dependent AI workflows to local agent computing.

## Humanoid Robots — and a Geopolitical Tightrope

In a more surprising move, Nvidia announced a partnership with China's Unitree to build a standardized humanoid robot for academic researchers. The robot's body comes from Unitree, its hands from Singapore's Sharpa, and its computing brain from Nvidia. Stanford and UC San Diego are among the planned users.

The partnership is politically charged. U.S. lawmakers have alleged that Unitree has ties to the Chinese government and military, and have introduced a bill to ban its robots from government-funded research. Nvidia executives told Reuters the company plans to pursue similar partnerships with robotics firms in the U.S., South Korea, and Europe — a hedging strategy that mirrors how the entire AI industry is navigating U.S.-China tensions.

## "AI Replacing Jobs Is Complete Nonsense"

Huang delivered a direct rebuttal to the growing anxiety around AI and employment — a concern that weighs particularly heavily on Indian tech workers who dominate the H-1B visa pipeline.

"The number of engineers, software engineers, is actually increasing," Huang said. "People talk about AI reducing jobs — complete nonsense. It's causing more software engineers to be hired."

He claimed that GitHub's AI coding tools are generating "$9 trillion in value for companies," far exceeding the "$3 trillion" that software engineers' collective salaries represent. The math was Huang's own, and not everyone was convinced. But the message was clear: Nvidia's CEO sees AI as a force multiplier for technical talent, not a replacement.

For the hundreds of thousands of Indian engineers in the U.S. who have watched AI anxiety compound on top of visa uncertainty, Huang's words are worth noting — even if taking them entirely at face value requires trusting the CEO of the company that sells the picks and shovels in the AI gold rush.

## $150 Billion a Year in Taiwan

Huang, who was born in Taiwan's southern city of Tainan, announced plans to invest approximately $150 billion annually in the island — describing it as the epicenter of the AI revolution. Samsung and LG shares surged in South Korea ahead of Huang's planned meetings with Korean executives later this week, with investors betting on new AI chip partnerships.

The Computex trade show runs June 2-5. Nvidia's stock rose 1 percent in the Monday session.

*Sources: Reuters, Wall Street Journal, Gizmodo, The Motley Fool, WCCFTech*"""

    topic_id = create_topic(headline, "news")
    if not topic_id:
        return None

    img_url = fetch_wikipedia_person_image("Jensen Huang")
    if img_url and not validate_image(img_url):
        img_url = None
    
    img_attr = "Wikimedia Commons"
    if not img_url:
        img_url = fetch_pexels_image("computer chip AI technology", "semiconductor GPU chip")
        img_attr = "Pexels"
        if img_url and not validate_image(img_url):
            img_url = None
    
    article = {
        "topic_id": topic_id,
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_attribution": img_attr if img_url else None,
        "sources": ["Reuters", "Wall Street Journal", "Gizmodo", "The Motley Fool", "WCCFTech"],
        "word_count": count_words(body),
        "is_editorial": False,
        "is_featured": False,
        "diaspora_angle": "Jensen Huang's claim that AI is creating more software engineering jobs — not fewer — is directly relevant to the hundreds of thousands of Indian-origin tech workers in the U.S. navigating both AI anxiety and visa uncertainty. The Vera CPU and AI PC announcements also shape the tools Indian developers will use daily.",
        "vertical": "politics",
        "tags": ["Nvidia", "Jensen Huang", "Computex", "Vera CPU", "AI agents", "RTX Spark", "AI PCs", "technology"],
        "urgency": "daily"
    }
    return insert_article(article)

# ============================================================
# ARTICLE 3
# ============================================================
def write_article_3():
    print("\n=== Article 3: DigiYatra Expansion ===")
    
    headline = "India Will Let You Walk Through 65 Airports Without Showing a Document. The System Has Already Processed 10 Crore Journeys."
    subheadline = "The government is adding 27 airports to DigiYatra's facial recognition network by next year — a shift that could transform how NRIs experience Indian airports."
    slug = "digiyatra-65-airports-facial-recognition-nri-travel-10-crore-journeys-2026"
    
    body = """If you have flown through an Indian airport recently and breezed past the entry gate in five seconds flat, you have DigiYatra to thank. If you have not, you are about to.

The Civil Aviation Ministry announced on Saturday that DigiYatra — India's facial recognition-based contactless airport travel system — will expand to 27 more airports by next year, bringing its total footprint to 65 airports. The platform is currently active at 38 airports and has already enabled over 10 crore seamless passenger journeys.

## From 15 Seconds to 5

The numbers tell the story of a system that has quietly become one of India's most successful digital infrastructure deployments. DigiYatra has crossed 2.4 crore downloads. Average airport entry processing time has dropped from 15 seconds to 5 seconds per passenger — a three-fold improvement that compounds dramatically when multiplied across India's growing base of air travelers.

"While many nations continue to evaluate the large-scale deployment of biometric passenger processing, India has successfully operationalized and scaled DigiYatra within a remarkably short timeframe," Civil Aviation Minister K. Rammohan Naidu said.

The system works simply: passengers register on the DigiYatra app with their face biometrics, link their boarding pass, and then walk through airport entry gates and security checkpoints with just a face scan — no boarding pass flash, no ID fumble, no QR code dance.

## Why the Diaspora Should Pay Attention

For members of the Indian diaspora who fly home once or twice a year and dread the document-checking scrum at domestic airports, the expansion is directly relevant. The connecting flight from Delhi to Lucknow or Mumbai to Coimbatore often involves more friction than the 16-hour international leg. DigiYatra is designed to eliminate exactly that.

The upcoming greenfield airports at Navi Mumbai, Jewar, and Bhogapuram will be fully integrated with DigiYatra from day one. These are the three largest new airport projects in India — each designed to handle tens of millions of passengers — with facial recognition baked into their architecture from the ground up.

The 27 airports being added next year will prioritize regional hubs, extending the contactless experience to Tier-2 and Tier-3 cities. The ministry did not name the specific airports, but the focus on regional connectivity suggests that cities NRIs often fly to after landing at a metro — Jaipur, Ahmedabad, Kochi, Visakhapatnam, Chandigarh — are likely candidates.

## The Language Push

DigiYatra currently supports 11 languages. By the end of 2026, the ministry plans to add 11 more regional languages — a recognition that India's air travel market is expanding beyond English and Hindi-speaking metros into states where passengers navigate apps in Tamil, Telugu, Kannada, Marathi, Bengali, and Gujarati.

India's passenger traffic is projected to reach 50 crore annually by 2030 and nearly 100 crore by 2040, according to Minister Naidu. That doubling will be driven overwhelmingly by first-time flyers from smaller cities — passengers who are less likely to be comfortable with English-only interfaces.

## Privacy by Design — But Questions Remain

The ministry emphasized that DigiYatra follows a "privacy-by-design framework." Passenger data remains encrypted and stored on the user's own device. It is shared with the departure airport only for a limited verification window, and the ministry says no centralized biometric database exists.

The claim sets DigiYatra apart from facial recognition deployments in China and the United States, where centralized databases have drawn scrutiny from civil liberties groups. But privacy advocates in India have noted that the system operates without fully operationalized enforcement rules under the Digital Personal Data Protection Act passed in 2023.

For now, adoption rates suggest passengers are voting with their faces. The trajectory from zero to 10 crore journeys in under four years puts DigiYatra on par with India's other rapid-scale digital successes — UPI, Aadhaar, and CoWIN.

## Five Indian Airports in the Global Top 100

DigiYatra is part of a broader push that is lifting Indian airports in global rankings. Five Indian airports made the Skytrax World Airport Awards 2026 top-100 list — Delhi at 28th, followed by Bangalore, Hyderabad, Goa's Manohar International, and Mumbai.

The ministry is also deploying self-baggage drop systems, upgraded air traffic control automation, the AirSewa grievance portal, and AI-powered digital twins at major airports. The contactless check-in at 65 airports is the most visible piece of an infrastructure overhaul that is steadily making Indian airports more competitive internationally.

For the NRI who last flew domestically in India three years ago and remembers the paper-boarding-pass-and-ID-card ritual at the entry gate — the next trip home will feel different.

*Sources: Civil Aviation Ministry press release, The Hindu BusinessLine, Outlook Business, Storyboard18, All India Radio News*"""

    topic_id = create_topic(headline, "news")
    if not topic_id:
        return None

    img_url = fetch_pexels_image("airport terminal passengers modern", "airport gate boarding travelers")
    if img_url and not validate_image(img_url):
        img_url = None
    
    article = {
        "topic_id": topic_id,
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_attribution": "Pexels" if img_url else None,
        "sources": ["Civil Aviation Ministry", "The Hindu BusinessLine", "Outlook Business", "Storyboard18", "All India Radio News"],
        "word_count": count_words(body),
        "is_editorial": False,
        "is_featured": False,
        "diaspora_angle": "DigiYatra directly affects NRIs who fly domestically in India during visits home. The expansion to 65 airports — including regional hubs that NRIs often connect through — means the document-checking friction at domestic airports is being eliminated. The new greenfield airports at Navi Mumbai, Jewar, and Bhogapuram will have facial recognition from day one.",
        "vertical": "politics",
        "tags": ["DigiYatra", "Indian airports", "facial recognition", "NRI travel", "Civil Aviation Ministry", "aviation"],
        "urgency": "daily"
    }
    return insert_article(article)

# ============================================================
if __name__ == "__main__":
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Missing Supabase credentials")
        sys.exit(1)
    
    print(f"News writer batch — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    
    results = []
    for fn in [write_article_1, write_article_2, write_article_3]:
        try:
            results.append(fn())
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback; traceback.print_exc()
            results.append(None)
    
    ok = sum(1 for r in results if r)
    print(f"\n=== DONE: {ok}/{len(results)} articles published ===")
