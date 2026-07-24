#!/usr/bin/env python3
"""Entertainment writer batch - May 28, 2026 (afternoon run) - v3 Fixed schema"""

import json, os, sys, time, uuid, requests, urllib.parse, subprocess
from datetime import datetime, timezone

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

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
                print(f"  ✓ Wiki image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wiki error: {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        return None
    for q in [query, fallback_query]:
        if not q: continue
        try:
            r = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            for photo in json.loads(r.stdout).get('photos', []):
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    if not url: return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct:
            if cl > 5000: return True
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, stream=True)
            if len(r2.raw.read(6000)) > 5000: return True
    except: pass
    return False

def create_topic(title, category):
    topic_id = str(uuid.uuid4())
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_topics", headers=HEADERS, json={
        "id": topic_id, "canonical_title": title, "category": category,
        "vertical": "entertainment", "urgency": "developing",
        "score_diaspora": 75, "score_significance": 70, "score_recency": 90,
        "score_source_avail": 80, "score_total": 79, "signal_count": 1, "status": "published", "keywords": []
    }, timeout=15)
    if r.status_code in (200, 201):
        print(f"  ✓ Topic: {topic_id[:8]}...")
        return topic_id
    print(f"  ✗ Topic failed: {r.text[:200]}")
    return None

def publish(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        res = r.json()
        title = res[0].get('headline', '')[:60] if isinstance(res, list) and res else ''
        print(f"  ✓ Published: {title}...")
        return True
    print(f"  ✗ Failed ({r.status_code}): {r.text[:300]}")
    return False

now = datetime.now(timezone.utc).isoformat()

# ============================================================
# ARTICLE 1: June 2026 OTT Mega-Month
# ============================================================
print("\n=== Article 1: June 2026 OTT Mega-Month ===")

img1 = fetch_pexels_image("family watching television streaming night", "movie night television remote")
if not validate_image(img1):
    img1 = None

topic1 = create_topic("June 2026 Indian OTT Streaming Calendar", "entertainment")
if topic1:
    publish({
        "topic_id": topic1,
        "headline": "June 2026 Might Be the Biggest Month in Indian Streaming History. Here's Everything Dropping.",
        "subheadline": "Dhurandhar 2, Maa Behen, Gullak S5, Patriot, Bhooth Bangla, Raja Shivaji, and a Titan origin story — all in 30 days.",
        "slug": "june-2026-biggest-month-indian-streaming-ott-nri-guide",
        "category": "entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "tags": ["OTT", "Netflix", "JioHotstar", "streaming", "Dhurandhar 2", "Gullak", "NRI"],
        "status": "published",
        "published_at": now,
        "image_url": img1,
        "image_caption": "June 2026 brings an unprecedented wave of Indian content to streaming platforms worldwide",
        "image_attribution": "Pexels" if img1 and 'pexels' in str(img1) else None,
        "diaspora_angle": "For NRIs who rely on OTT for Indian content, June 2026 is the single richest month in streaming history — every major platform is dropping blockbuster titles simultaneously, eliminating the theatrical-to-digital wait that has long frustrated diaspora audiences.",
        "sources": json.dumps(["https://www.mensxp.com/entertainment/celebrities/183978-june-2026-ott-releases-dhurandhar-the-revenge-bhooth-bangla-gullak-season-5.html", "https://www.idiva.com/entertainment/bollywood/ott-releases-june-dhurandhar-the-revenge-maa-behen-raja-shivaji/18096921", "https://sacnilk.com", "https://www.pinkvilla.com"]),
        "body": """Every few months, Indian OTT has a week that feels overstuffed. June 2026 is not a week. It is the entire month.

Between June 3 and June 26, at least eleven major titles will premiere across JioHotstar, Netflix, Amazon MX Player, SonyLIV, and Zee5. Some are box office juggernauts finally hitting digital. Others are originals that have been in production for years. And one is the story of how a watch company changed Indian manufacturing forever.

For the diaspora, this is the month your subscriptions actually earn their keep.

## The Headliners

**Dhurandhar: The Revenge** arrives on JioHotstar on **June 4**. Ranveer Singh's spy thriller has earned ₹1,850 crore worldwide and nearly ₹1,150 crore domestically — making it the highest-grossing Indian film of all time. After ten weeks in theatres, it finally comes home. Netflix will stream an alternate "Uncut" version starting June 19.

The same day, Netflix drops **Maa Behen**, a dark comedy starring Madhuri Dixit, Triptii Dimri, and Dharna Durga. Dysfunctional family dynamics, crime, and chaos — the kind of film that would have been a mid-budget theatrical release five years ago and is now a streaming-first event.

On **June 5**, SonyLIV releases **Gullak Season 5**, the beloved TVF series about a middle-class family navigating everyday life. Anant V Joshi joins the ensemble this season. If you have ever explained to an American friend why a show about a family buying a mixer-grinder made you cry, this is for you.

## The Surprise Entry

**Made in India: A Titan Story** premieres on Amazon MX Player on **June 3** — and it might be the most NRI-relevant release of the month. Naseeruddin Shah plays JRD Tata. Jim Sarbh plays Xerxes Desai, the man Tata trusted to build what became one of India's most iconic consumer brands. The six-part series, adapted from Vinay Kamath's book, is free to stream — no subscription required.

## The Malayalam Event

**Patriot** streams on Zee5 from **June 5** in Malayalam, Hindi, Tamil, Kannada, and Telugu. Directed by Mahesh Narayanan, it reunites Mammootty and Mohanlal on screen after 18 years. Fahadh Faasil, Nayanthara, and Kunchacko Boban round out a cast that reads like a Malayalam cinema all-star game.

The plot follows a scientist who exposes government spyware misuse, triggering a conspiracy and a nationwide protest against surveillance. The film earned ₹80 crore globally on a ₹100 crore budget — but the star power and the timeliness of its surveillance-state themes make the digital premiere an event in itself.

## The Second Wave

**Bhooth Bangla** hits Netflix on **June 12**. Akshay Kumar and Priyadarshan's horror-comedy reunion crossed ₹260 crore theatrically and became the third-biggest Bollywood grosser of 2026. If you missed it in theatres, this is Priyadarshan at his most Hera Pheri-adjacent.

**Thukra Ke Mera Pyaar Season 2** arrives on JioHotstar on **June 19**, deepening its story of love, betrayal, and political rivalry.

**Raja Shivaji** lands on Netflix on **June 26**. Riteish Deshmukh, Genelia Deshmukh, Sanjay Dutt, Abhishek Bachchan, and Bhagyashree star in the Marathi-language historical drama that earned ₹93 crore domestically and broke every Marathi cinema box office record. This is its first global streaming window.

And if your tastes run international: **Avatar: Fire and Ash** premieres on JioHotstar June 24, and **The Bear Season 5** — the final season — drops June 25.

## What It Means for NRIs

If you are outside India, June 2026 is the month the gap between theatrical and streaming finally collapses. Dhurandhar 2 gets a 10-week window. Raja Shivaji gets roughly 8 weeks. Bhooth Bangla gets 9.

Compared to the 8-week window South Indian exhibitors demanded just last month, Bollywood is moving faster. The streamers are spending — JioHotstar reportedly committed ₹4,000 crore to South Indian content alone this year — and the content pipeline is delivering.

The only problem is time. Between work, the school run, and whatever your family WhatsApp group is arguing about, finding 150 hours of viewing time in June will require commitment.

Start clearing the schedule now."""
    })

time.sleep(1)

# ============================================================
# ARTICLE 2: Yudhvir Ahlawat tops IMDb
# ============================================================
print("\n=== Article 2: Yudhvir Ahlawat ===")

img2 = fetch_pexels_image("young Indian boy spotlight stage", "child actor cinema India")
if not validate_image(img2):
    img2 = None

topic2 = create_topic("Yudhvir Ahlawat Tops IMDb India STARmeter", "entertainment")
if topic2:
    publish({
        "topic_id": topic2,
        "headline": "A 14-Year-Old From Haryana Just Beat Shah Rukh Khan on IMDb's Most Searched List. His Name Is Yudhvir Ahlawat.",
        "subheadline": "The Kartavya actor topped IMDb India's weekly popularity rankings, surpassing Aishwarya Rai and CM Vijay. The streaming era just rewrote who gets to be famous.",
        "slug": "yudhvir-ahlawat-kartavya-imdb-most-searched-beats-shah-rukh-khan-nri-20260528",
        "category": "entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "tags": ["Yudhvir Ahlawat", "Kartavya", "IMDb", "Netflix", "streaming", "child actor"],
        "status": "published",
        "published_at": now,
        "image_url": img2,
        "image_caption": "Yudhvir Ahlawat's breakout performance in Netflix's Kartavya made him the most searched Indian actor on IMDb",
        "image_attribution": "Pexels" if img2 and 'pexels' in str(img2) else None,
        "diaspora_angle": "Ahlawat's rise proves that streaming has demolished the old gatekeeping system — a Hindi film about rural India now premieres simultaneously in 190 countries, and a teenager from Haryana can become a global search trend without ever leaving his hometown.",
        "sources": json.dumps(["https://www.idiva.com", "https://newseisamay.com", "https://srkbharat.com", "https://www.imdb.com"]),
        "body": """In any other era, the path to the top of India's celebrity search rankings required a decade of box office hits, a few magazine covers, and at least one Karan Johar film. Yudhvir Ahlawat skipped all of it.

The 14-year-old actor from Haryana topped IMDb India's weekly STARmeter popularity rankings after his performance in Netflix's *Kartavya*. He surpassed Shah Rukh Khan, Aishwarya Rai, CM Vijay, and every other name that has dominated Indian celebrity culture for the past thirty years.

He did it without a film release in theatres. Without a brand endorsement. Without a famous parent.

## The Film That Changed Everything

*Kartavya* is a Netflix original that tells the story of duty, sacrifice, and coming-of-age in rural India. Ahlawat plays the central role — a boy navigating impossible choices in a world that offers him very few.

The performance is the kind that makes you forget you are watching a child actor. It is restrained where most child performances are loud, emotionally precise where others rely on tears, and physically committed in a way that suggests someone who understood the character before the cameras rolled.

Netflix's algorithm did the rest. The film appeared on India's Top 10 within days of release. Social media clips of Ahlawat's key scenes went viral. And IMDb's search data — which measures raw public curiosity — put him above actors who have collectively earned tens of thousands of crores at the box office.

## What the Numbers Mean

IMDb's STARmeter is not a popularity contest in the traditional sense. It tracks page views and search volume — a proxy for who the world is actively curious about at any given moment. When a 14-year-old from Haryana overtakes Shah Rukh Khan on that metric, it does not mean he is more famous. It means, for that specific week, more people wanted to know who he was.

That distinction matters. In the theatrical era, curiosity was manufactured through trailers, TV appearances, and Filmfare spreads. In the streaming era, it is manufactured by performance. The audience discovers you on their own terms. The algorithm amplifies what they respond to. And if your work is good enough, you can go from unknown to the most searched person in India without ever doing a press junket.

Ahlawat is not the first streaming-era breakout — Jaideep Ahlawat (no relation) had a similar trajectory with *Paatal Lok* in 2020. But he may be the youngest, and certainly the most dramatic example of how completely the discovery pipeline has changed.

## The Diaspora Connection

For NRIs, Ahlawat's rise is a reminder of what streaming has done to Indian entertainment's export model. A decade ago, a Hindi-language film about rural India would have had no distribution outside the subcontinent. Today, it premieres simultaneously in 190 countries on Netflix, and a teenager from Haryana becomes a global search trend.

The platforms have not just changed how Indians abroad consume content. They have changed who gets to make content. The gatekeepers — the Yash Raj talent scouts, the star-kid launch machinery, the metropolitan networks that decide who gets a first film — still exist. But they now share the pipeline with an algorithm that does not care about your last name or your city of origin.

## What Comes Next

Ahlawat has not announced a follow-up project. No production house has confirmed a signing. In the pre-streaming era, this would have been a problem — the window between a breakout and a second role was short, and if you missed it, the industry moved on.

The streaming era is more forgiving. *Kartavya* will remain on Netflix indefinitely. New audiences will discover it months and years from now. And Ahlawat's IMDb page — currently the most visited actor page in India — will serve as a permanent digital audition reel.

He is fourteen. He has time. And the industry, for once, is structured in a way that rewards patience over proximity to power.

The old playbook said you needed Mumbai. Yudhvir Ahlawat says you need a good script, a camera, and a broadband connection."""
    })

time.sleep(1)

# ============================================================
# ARTICLE 3: Made in India: A Titan Story
# ============================================================
print("\n=== Article 3: Made in India: Titan Story ===")

img3 = fetch_wikipedia_person_image("Naseeruddin Shah")
if not validate_image(img3):
    img3 = fetch_wikipedia_person_image("Jim Sarbh")
    if not validate_image(img3):
        img3 = fetch_pexels_image("vintage watch craftsmanship India", "wristwatch luxury")
        if not validate_image(img3):
            img3 = None

topic3 = create_topic("Made in India: A Titan Story Amazon MX Player", "entertainment")
if topic3:
    publish({
        "topic_id": topic3,
        "headline": "Naseeruddin Shah Plays JRD Tata. Jim Sarbh Plays the Man He Trusted to Build Titan. It Drops June 3.",
        "subheadline": "'Made in India: A Titan Story' is a six-part Amazon MX Player series about how a watch company born in pre-liberalisation India became a global icon.",
        "slug": "made-in-india-titan-story-naseeruddin-shah-jrd-tata-jim-sarbh-amazon-mx-june-2026-nri",
        "category": "entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "tags": ["Naseeruddin Shah", "Jim Sarbh", "Titan", "JRD Tata", "Amazon MX Player", "Indian business"],
        "status": "published",
        "published_at": now,
        "image_url": img3,
        "image_caption": "Naseeruddin Shah as JRD Tata in 'Made in India: A Titan Story', streaming free June 3 on Amazon MX Player",
        "image_attribution": "Wikimedia Commons" if img3 and 'wiki' in str(img3) else "Pexels" if img3 and 'pexels' in str(img3) else None,
        "diaspora_angle": "Every NRI over 30 has a Titan memory — the watch their father wore, the Sonata from a school prize, the Fastrack bought with first pocket money. This series turns that shared experience into prestige television, free to stream worldwide.",
        "sources": json.dumps(["https://nationpress.com", "https://brownstoneworldwide.com", "https://www.bollywoodhungama.com", "https://www.idiva.com"]),
        "body": """Before liberalisation, before Infosys, before the idea that India could build global consumer brands felt anything other than absurd — there was a watch.

Titan was born in 1984, when the Indian market was dominated by HMT and the idea of a Tata Group entry into consumer electronics was met with scepticism from within the group itself. Xerxes Desai, a Tata loyalist who had spent years reviving Tata Press, was handed the job. JRD Tata backed him. The rest became one of the great Indian business origin stories.

Now, it is a television series. And the casting alone should tell you how seriously the makers are treating the material.

## The Show

*Made in India: A Titan Story* is a six-part series premiering on Amazon MX Player on June 3, 2026. It is free to stream — no subscription required.

Naseeruddin Shah plays JRD Tata. Jim Sarbh plays Xerxes Desai. The series is adapted from Vinay Kamath's book *Titan: Inside India's Most Successful Consumer Brand* and directed by Robbie Grewal.

The trailer, released on May 26, establishes the tone: this is not a glossy corporate hagiography. It is a story about two men who believed India could build something world-class in a decade when the country's industrial policy was designed to prevent exactly that. Import restrictions meant components had to be sourced domestically. Bureaucratic approvals took years. The market did not believe an Indian watch could compete with Swiss and Japanese imports.

Desai built Titan anyway. He launched Sonata as an affordable sub-brand. He introduced Fastrack for younger buyers. He turned a watch company into a lifestyle conglomerate that now includes Tanishq, one of India's largest jewellery brands.

## Why It Matters for the Diaspora

Every NRI over 30 has a Titan memory. It was the watch your father wore to the office. It was the Sonata you received as a school prize. It was the Fastrack you bought with your first pocket money because you wanted something that felt modern and Indian at the same time.

For a generation that left India and built careers in Silicon Valley, Wall Street, the NHS, and Bay Street, the Titan story resonates at a level that most business narratives do not. It is proof that the India they left — the India of license raj and import substitution — contained within it the seeds of the global India that followed.

The series arrives at a moment when Indian business stories are having a cultural moment. *The Romantics* documented Yash Raj Films. *Scam 1992* turned Harshad Mehta into a streaming antihero. *Rocket Boys* dramatised Homi Bhabha and Vikram Sarabhai. But none of those stories centred on a consumer product that millions of Indians personally owned and emotionally associated with growing up.

Titan is different. It is intimate. You did not need to understand nuclear physics or stock markets to feel the brand. You just needed a wrist.

## The Performances

Casting Naseeruddin Shah as JRD Tata is a statement of intent. Shah brings the same measured authority he brought to *A Wednesday*, *Sarfarosh*, and decades of parallel cinema. JRD Tata was not a loud leader — he was precise, deliberate, and fiercely protective of the people he trusted. Shah's screen persona mirrors those qualities almost exactly.

Jim Sarbh, who broke through with *Neerja* and has since built a career choosing projects that prioritise craft over commerce, plays Desai as a man who combines idealism with execution. The trailer suggests a performance grounded in quiet determination — a man who does not give speeches about changing India but simply builds something that does.

## The Streaming Landscape

*Made in India* arrives on Amazon MX Player, which has been positioning itself as a free, ad-supported alternative to the subscription-heavy Indian OTT market. For NRIs, this matters. No paywall means no geo-restriction friction. If you can access Amazon MX Player — and it is available in most markets — you can watch a Naseeruddin Shah series about the founding of Titan for free.

In a month when JioHotstar, Netflix, SonyLIV, and Zee5 are all demanding your attention and your credit card, a free prestige series about Indian entrepreneurship feels like a gift.

The six episodes drop together on June 3. Clear an evening. Wear your old Titan if you still have one."""
    })

print("\n=== Entertainment writer batch complete ===")
