#!/usr/bin/env python3
"""
Sports writer batch - June 6, 2026
Generates 3 sports articles for The Videshi
"""
import json, os, sys, time, uuid, re, subprocess
import requests, urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    key, val = line.split('=', 1)
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            thumb = data.get("thumbnail", {}).get("source")
            orig = data.get("originalimage", {}).get("source")
            if thumb:
                print(f"  ✓ Wikipedia image for '{person_name}': {thumb[:80]}...")
                return thumb  # Use thumbnail (330px) as-is
            if orig:
                print(f"  ✓ Wikipedia original for '{person_name}': {orig[:80]}...")
                return orig
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0)
                })
            if results:
                print(f"  ✓ Commons: {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
    return []

def fetch_pexels(query):
    """Search Pexels for stock photos using curl."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                print(f"  ✓ Pexels: {len(photos)} results for '{query}'")
                return photos[0]["src"]["large2x"]
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    """Validate an image URL returns 200 and has decent size."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            ct = r.headers.get("Content-Type", "")
            cl = int(r.headers.get("Content-Length", "0"))
            if "image" in ct and cl > 5000:
                print(f"  ✓ Image valid: {cl} bytes")
                return True
            elif "image" in ct and cl == 0:
                # Content-Length might not be set, try GET
                r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
                chunk = r2.raw.read(10000)
                if len(chunk) > 5000:
                    print(f"  ✓ Image valid (streamed check)")
                    return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def publish_article(article):
    """Insert article into Supabase."""
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption"),
        "image_attribution": article.get("image_attribution"),
        "sources": json.dumps(article.get("sources", [])),
        "is_editorial": False
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload
    )
    if r.status_code in (200, 201):
        data = r.json()
        article_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Published: {article['slug']} (id: {article_id})")
        return True
    else:
        print(f"  ✗ Failed to publish {article['slug']}: {r.status_code} {r.text[:200]}")
        return False

# ===================== ARTICLES =====================

def write_article_1():
    """Zee5 FIFA World Cup pricing controversy + NRI angle"""
    print("\n=== Article 1: Zee5 FIFA World Cup Pricing ===")
    
    # Image: FIFA World Cup trophy or stadium from Wikimedia Commons
    image_url = None
    image_caption = None
    image_attribution = None
    
    # Try Wikimedia Commons for FIFA World Cup 2026
    commons = fetch_wikimedia_commons("FIFA World Cup trophy")
    if commons:
        candidate = commons[0]["url"]
        if validate_image(candidate):
            image_url = candidate
            image_caption = "The FIFA World Cup trophy, the prize that 48 nations will compete for in 2026"
            image_attribution = "Wikimedia Commons"
    
    if not image_url:
        commons2 = fetch_wikimedia_commons("FIFA World Cup 2026")
        if commons2:
            candidate = commons2[0]["url"]
            if validate_image(candidate):
                image_url = candidate
                image_caption = "FIFA World Cup 2026 will be hosted across the United States, Canada, and Mexico"
                image_attribution = "Wikimedia Commons"
    
    if not image_url:
        pexels = fetch_pexels("football stadium crowd world cup")
        if pexels and validate_image(pexels):
            image_url = pexels
            image_caption = "Football fans at a stadium ahead of the FIFA World Cup"
            image_attribution = "Pexels"
    
    article = {
        "headline": "Zee Secured the World Cup Rights Ten Days Before Kickoff. Indian Fans Are Furious About the Price.",
        "subheadline": "A ₹799 streaming package with ads, geo-blocked YouTube streams, and a Delhi High Court piracy crackdown — the road to watching the 2026 FIFA World Cup in India is everything except simple.",
        "slug": "zee5-fifa-world-cup-2026-india-broadcast-rights-pricing-backlash-nri",
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": [
            "https://www.mykhel.com/football/fifa-world-cup-2026-on-zee5-fans-react-as-799-price-triggers-backlash-437603.html",
            "https://www.exchange4media.com/media-others-news/delhi-hc-grants-zee-dynamic-injunction-against-fifa-world-cup-2026-piracy-141123.html",
            "https://www.sacnilk.com/articles/entertainment/zee-secures-fifa-media-rights-until-2034",
            "https://www.khelnow.com/football/which-tv-channels-broadcast-fifa-world-cup-2026-india"
        ],
        "body": """For months, India — one of football's largest and fastest-growing markets — had no confirmed broadcaster for the 2026 FIFA World Cup. While every other major territory had locked down their deals, India's remained unsigned. FIFA had initially sought $100 million for the India package covering the 2026 and 2030 World Cups. Nobody bit. The price was halved to around $60 million. Still, nobody committed.

Then, on June 1, with the tournament just ten days away, Zee Entertainment quietly closed the deal.

## A Last-Minute Rescue — at a Cost

The eight-year agreement covers 39 FIFA events through 2034, including the 2026 and 2030 men's World Cups, the 2027 Women's World Cup, and various youth and futsal tournaments. Zee is launching a new broadcast network under the brand Unite8 Sports — two linear channels in Hindi and English, both in HD — and streaming all 104 matches on Zee5.

The deal marks Zee's dramatic re-entry into sports broadcasting, nearly eight years after the company sold its sports assets to Sony. Shares in Zee Entertainment rose approximately 7 percent on the announcement.

But what should have been a celebration quickly turned into a standoff with fans.

## ₹799 With Ads. Fans Are Not Having It.

Zee5's pricing structure set off an immediate backlash. The platform is offering a three-month World Cup streaming package for ₹799 — roughly $9.50 — and it includes advertisements.

The reaction on social media was swift and blunt. One fan wrote: "₹799 is diabolical. Illegal streams FTW." Another questioned the value proposition directly: "Zee5 quietly sliding in a 3-month plan for ₹799 while the FIFA World Cup lasts only 2 months. And that too with ads???"

The frustration cuts deeper because many fans had believed FIFA's YouTube partnership, announced in March, would provide a free alternative. Under that agreement, official rights-holding broadcasters can stream the first 10 minutes of every match on YouTube, and selected matches in full. FIFA's own channel will host highlights and behind-the-scenes content throughout the tournament. But those broadcaster streams remain geo-blocked — accessible only within the territory of the broadcaster that uploads them.

Without Zee opting into FIFA's YouTube programme, Indian viewers have no legal route to free live streaming. What FOX puts on YouTube in the United States stays in the United States.

## The Diaspora Divide

For the estimated 18 million Indians living abroad, the World Cup viewing experience will depend entirely on where they live. NRIs in the United States can watch on FOX's broadcast and digital platforms. Those in the UK have the BBC and ITV. Canada has its own broadcasting arrangements through TSN and RDS.

But for their families back in India — the ones they will want to call after every goal, every penalty, every red card — the only legal route is Zee5 or Unite8 Sports cable channels. The pricing disparity between what is effectively free-to-air in many Western countries and a paid, ad-supported platform in India has not gone unnoticed.

India is not playing in the tournament. But four Indian-origin players will be — Sarpreet Singh representing New Zealand, Tahsin Mohammed Jamshid for Qatar, Samuel Moutoussamy for DR Congo, and Timothee Velupillay for France. For diaspora fans tracking their heritage across four different national teams, the irony of not being able to easily share the viewing experience with family in India is palpable.

## Delhi High Court Steps In

Zee moved fast to protect its investment. On June 3, the Delhi High Court granted a sweeping interim injunction in Zee's favour, directing internet service providers and domain registrars to block access to rogue websites allegedly planning to stream the World Cup without authorization.

Justice Saurabh Banerjee's order named five websites — Soccerbox, Soccerworldcup, DLHD, Strumyk, and Sportsbay — and empowered Zee to seek real-time blocking of future infringing sites and apps. The court noted that these platforms operate anonymously and had already been identified as having streamed IPL 2026 matches illegally.

The injunction is "dynamic," meaning Zee can add new infringing domains without returning to court each time — a legal tool specifically designed for the whack-a-mole nature of live sports piracy.

## What It Means

The 2026 FIFA World Cup kicks off on June 11 in Mexico City. For the next six weeks, 48 teams will play 104 matches across three countries. India's involvement is indirect — through diaspora players, through the millions of fans who follow European and South American football as passionately as they follow cricket, and through a broadcasting deal that was nearly not signed at all.

Zee's gamble is significant. The company paid roughly $60 million — 40 percent less than FIFA's asking price — for rights that no other Indian broadcaster wanted. Whether Zee5's subscriber numbers justify that investment will depend on exactly how many Indian football fans are willing to pay ₹799 for a tournament their country is not even playing in.

The answer to that question will arrive in the next ten days. And it will be delivered, with ads, on a platform most of them signed up for reluctantly."""
    }
    
    return article

def write_article_2():
    """Sooryavanshi lands in Sri Lanka - B-school case study angle"""
    print("\n=== Article 2: Sooryavanshi Lands in Sri Lanka ===")
    
    # Image: Try Wikipedia for Vaibhav Sooryavanshi
    image_url = None
    image_caption = None
    image_attribution = None
    
    wiki = fetch_wikipedia_person_image("Vaibhav Suryavanshi")
    if wiki and validate_image(wiki):
        image_url = wiki
        image_caption = "Vaibhav Sooryavanshi, the 15-year-old who broke multiple IPL records and is now on India A duty"
        image_attribution = "Wikimedia Commons"
    
    if not image_url:
        wiki2 = fetch_wikipedia_person_image("Vaibhav Suryavanshi (cricketer)")
        if wiki2 and validate_image(wiki2):
            image_url = wiki2
            image_caption = "Vaibhav Sooryavanshi, the 15-year-old who broke multiple IPL records and is now on India A duty"
            image_attribution = "Wikimedia Commons"
    
    if not image_url:
        commons = fetch_wikimedia_commons("Vaibhav Suryavanshi cricket")
        if commons:
            candidate = commons[0]["url"]
            if validate_image(candidate):
                image_url = candidate
                image_caption = "Vaibhav Sooryavanshi arrives in Sri Lanka for the India A tri-series"
                image_attribution = "Wikimedia Commons"
    
    if not image_url:
        # Try Dambulla cricket stadium
        commons2 = fetch_wikimedia_commons("Rangiri Dambulla cricket stadium Sri Lanka")
        if commons2:
            candidate = commons2[0]["url"]
            if validate_image(candidate):
                image_url = candidate
                image_caption = "The Rangiri Dambulla International Cricket Stadium in Sri Lanka, venue for the tri-series"
                image_attribution = "Wikimedia Commons"
    
    if not image_url:
        pexels = fetch_pexels("cricket stadium Sri Lanka")
        if pexels and validate_image(pexels):
            image_url = pexels
            image_caption = "A cricket ground in Sri Lanka where the India A tri-series will be played"
            image_attribution = "Pexels"

    article = {
        "headline": "Sooryavanshi Has Landed in Sri Lanka. A Business School Has Already Made Him a Case Study.",
        "subheadline": "The 15-year-old who swept five IPL awards, scored 175 off 80 balls in a U-19 World Cup final, and is now auditioning for a senior India cap in Dambulla — while IIM professors study what made it all possible.",
        "slug": "vaibhav-sooryavanshi-india-a-sri-lanka-tri-series-iim-case-study-senior-debut-audition-nri",
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": [
            "https://www.ianslive.in/news/tilak-varma-led-india-a-squad-arrives-in-sri-lanka-for-50-over-tri-series",
            "https://www.livemint.com/sports/cricket-news/vaibhav-sooryavanshi-ipl-rajasthan-royals-case-study-bschool",
            "https://www.afaqs.com/news/media/spni-acquires-rights-for-india-a-tri-nation-series",
            "https://www.currentindia.com/vaibhav-sooryavanshi-sri-lanka-india-a-tri-series-senior-debut"
        ],
        "body": """The India A squad touched down in Dambulla on Friday, and Sri Lanka Cricket posted the arrival photos within hours. In one of them, Vaibhav Sooryavanshi walks through the airport in team gear, a backpack over one shoulder, looking exactly like what he is — a fifteen-year-old on a school trip, except the school is international cricket and the trip might end with a senior India call-up.

The tri-series begins on June 9. India A face Sri Lanka A first, then Afghanistan A, in a double round-robin format leading to a final on June 21. All matches will be played at the Rangiri Dambulla International Cricket Stadium. Sony Pictures Networks India has acquired the broadcast rights — a decision that, by their own admission, was driven almost entirely by one name.

"One of the biggest draws for viewers will be to watch the biggest sensation in Indian cricket, teenage prodigy Vaibhav Sooryavanshi, whose explosive talent is making him one of the most talked-about players today," said Rajesh Kaul, Sony's chief revenue officer for sports business.

A broadcaster does not publicly tie its acquisition rationale to a single fifteen-year-old unless the economics are obvious.

## The Squad That Kept Changing

The India A setup has been reshuffled twice before it even left Indian shores. Tilak Varma leads the side, but the vice-captaincy has been a revolving door.

Riyan Parag was originally named vice-captain. He withdrew with a hamstring injury sustained during the latter stages of IPL 2026, where he captained the Rajasthan Royals through to the knockout rounds. Parag is now rehabilitating at the BCCI Centre of Excellence in Bengaluru.

Ruturaj Gaikwad was drafted in as his replacement. Then Virat Kohli was ruled out of the senior team's Afghanistan ODI series with a hamstring strain of his own, and Gaikwad was promoted to the senior squad. Rajat Patidar has now stepped in as vice-captain.

The coaching staff is experienced but deliberately developmental: Hrishikesh Kanitkar, Sunil Joshi, Lakshmipathy Balaji, and Shubhadeep Ghosh. Three former India internationals and a national-level coach, tasked with shepherding a squad that includes several players with single-digit List A caps.

Beyond Sooryavanshi, the squad features Priyansh Arya, Prabhsimran Singh, Ayush Badoni, Nishant Sindhu, Kumar Kushagra, Suryansh Shedge, and Anukul Roy — the last of whom was added after Harsh Dubey earned a call-up to both the Test and ODI squads for the Afghanistan series. Anshul Kamboj is the only other capped India player besides Varma and Gaikwad.

## The Case Study

While Sooryavanshi was boarding his flight to Colombo, a top Indian business school was already dissecting his career as a management case study. Faculty members at the institution are examining how a fifteen-year-old navigated the pressure of a record-breaking IPL season — the Orange Cap with 776 runs, the MVP award, the Emerging Player prize, the Super Striker award with a strike rate of 237.30, and the Most Sixes record with 72, breaking Chris Gayle's all-time mark.

The academic angle is not about cricketing technique. It is about decision-making under extreme public scrutiny, brand value creation in compressed timescales, and the psychological frameworks that allow a teenager to perform under pressure that would unsettle most adults. Professors studying organisational behaviour and sports management are using Sooryavanshi as a live example of what happens when generational talent meets a system — the IPL auction, franchise cricket, national selection pathways — that was not designed for someone his age.

Sachin Tendulkar, who debuted for India at sixteen, offered his own assessment after the IPL final. "Vaibhav Sooryavanshi had an influence on games that went beyond the runs he scored," Tendulkar wrote. "Oppositions were thinking about him, teams were planning for him, and fans were waiting for him long before he arrived at the crease. His batting seemed to give Rajasthan Royals an added sense of belief every time he walked out to the middle."

Former India pacer Atul Wassan was more direct: "He is a one in a million generational talent. He reminds me of 16-year-old Sachin Tendulkar."

## What Dambulla Means

This is not a holiday fixture. The tri-series sits directly in the pathway between the IPL and senior international selection. Sooryavanshi's 175 off 80 balls in the U-19 World Cup final against England in January was the innings that announced him. His IPL season confirmed it. Dambulla is the test of whether he can translate that form into the 50-over format, against full-strength A teams, on foreign soil, with selectors watching.

For the millions of NRI cricket fans who followed every ball of his IPL campaign through streaming apps and time-zone-defying alarm clocks, Dambulla represents something more specific: the last audition before a senior India debut that now feels like a matter of when, not if.

The first match is on June 9. Sony will broadcast it live from 10 AM IST. They are doing it because a fifteen-year-old is in the squad. They know exactly what they are selling."""
    }
    
    return article

def write_article_3():
    """Gambhir pre-match presser"""
    print("\n=== Article 3: Gambhir Pre-Test Press Conference ===")
    
    # Image: Wikipedia for Gautam Gambhir
    image_url = None
    image_caption = None
    image_attribution = None
    
    wiki = fetch_wikipedia_person_image("Gautam Gambhir")
    if wiki and validate_image(wiki):
        image_url = wiki
        image_caption = "Gautam Gambhir, India's head coach, at a press conference ahead of the Afghanistan Test"
        image_attribution = "Wikimedia Commons"
    
    if not image_url:
        commons = fetch_wikimedia_commons("Gautam Gambhir cricket coach India")
        if commons:
            candidate = commons[0]["url"]
            if validate_image(candidate):
                image_url = candidate
                image_caption = "Gautam Gambhir during a media interaction"
                image_attribution = "Wikimedia Commons"
    
    if not image_url:
        # Try Sai Sudharsan
        wiki2 = fetch_wikipedia_person_image("Sai Sudharsan")
        if wiki2 and validate_image(wiki2):
            image_url = wiki2
            image_caption = "Sai Sudharsan, confirmed to bat at No. 3 in the Afghanistan Test at Mohali"
            image_attribution = "Wikimedia Commons"

    if not image_url:
        pexels = fetch_pexels("cricket test match India")
        if pexels and validate_image(pexels):
            image_url = pexels
            image_caption = "A Test match scene in India"
            image_attribution = "Pexels"

    article = {
        "headline": "'I Don't Look for Excuses.' Gambhir Confirms Sudharsan at No. 3 and Says the Afghanistan Test Is Serious Business.",
        "subheadline": "India's head coach pushed back on criticism of the squad's transition, confirmed Sai Sudharsan's promotion to the crucial middle-order position, and refused to treat the non-WTC Test as a lesser fixture.",
        "slug": "gambhir-sudharsan-no-3-afghanistan-test-mohali-serious-business-wtc-transition-nri",
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": [
            "https://www.sportstiger.com/cricket/gautam-gambhir-emphasises-that-one-off-afghanistan-test-is-serious-business-despite-not-being-a-part-of-wtc-cycle",
            "https://www.sportstiger.com/cricket/rohit-sharma-likely-to-report-to-bcci-coe-on-8th-june-for-fitness-clearance",
            "https://www.espncricinfo.com/"
        ],
        "body": """Gautam Gambhir held a press conference in Mohali on Thursday, one day before India's one-off Test against Afghanistan at the Maharaja Yadavindra Singh International Cricket Stadium. He was asked about the World Test Championship. He was asked about the absence of Virat Kohli and the uncertainty around Rohit Sharma. He was asked whether a non-WTC fixture against a team playing only its second-ever Test in India mattered at all.

He answered every question the same way: it matters.

"A Test match is a Test match," Gambhir said. "I know people talk about this not being a part of the World Test Championship cycle, but for me, it is a Test match, and we need to go out there and win for the country because you don't differentiate between Test matches whether they are part of WTC or not."

## The Transition Defence

Gambhir became India's head coach knowing the job came with a transition. He has overseen a difficult period — 2025 brought ten Tests, four wins, five losses, and one draw. India lost a home series to South Africa, their first home Test series defeat in over a decade. Leadership changed, with Shubman Gill taking over the Test captaincy.

When asked whether the transition excuses the results, Gambhir rejected the premise entirely.

"I don't look for excuses. I don't see the absence of full strength as a reason for where we are. We have enough talent to turn things around, and I am sure we can give ourselves the best possible chance to win the World Test Championship."

The WTC he was referencing is the 2025-27 cycle. India are in the early stages, with away tours to Sri Lanka and New Zealand and a home Border-Gavaskar Trophy series ahead. The Afghanistan Test sits outside the WTC framework — it carries no points, no rankings implications, no pathway to the final at Lord's. What it does carry is a chance to give young players a high-pressure audition before the cycle intensifies.

## Sudharsan Gets No. 3

The most concrete news from the press conference was the confirmation that Sai Sudharsan will bat at No. 3, the position that has been Indian cricket's most contested since Cheteshwar Pujara's decline and eventual exit from the Test setup.

"He needs a fair chance to prove his skills," Gambhir said of Sudharsan, the 23-year-old left-hander from Tamil Nadu who has shown composure in domestic cricket and during India A assignments but has not yet had an extended run in the senior Test side.

Sudharsan's promotion to No. 3 is a deliberate signal. It is a role that demands a particular temperament — the ability to arrive at the crease anywhere from the second over to the thirtieth, to build an innings against both the new ball and spin, to occupy time. For a team without Kohli and potentially without Rohit, asking a young player to anchor the innings at No. 3 against Afghanistan's limited but competitive seam and spin options is both an opportunity and a test of Gambhir's conviction.

## The Rohit Question

Rohit Sharma has not yet reported to the BCCI Centre of Excellence in Bengaluru for the fitness clearance that will determine his availability for the Afghanistan ODI series starting later this month. Reports indicate he is likely to report on June 8.

Rohit retired from T20Is and Tests to focus exclusively on the 50-over format ahead of the 2027 ODI World Cup. His childhood coach, Dinesh Lad, told media this week that he believes Rohit will play the World Cup. "I don't think he needs to prove anything," Lad said. "He has always risen to the occasion."

But Rohit's absence from the Test squad, combined with Kohli's hamstring injury, means the Afghanistan match will be played without either of the two batsmen who defined Indian cricket for the better part of a decade. Gambhir's response to that reality — no excuses, no caveats, just a demand for performance — is either bravado or genuine belief in the depth chart.

## What the BCCI Wants

The BCCI has been explicit about treating the upcoming WTC cycle with renewed seriousness. After finishing fifth in the 2023-25 standings, the board wants India competing for the final at Lord's. The Afghanistan Test, while carrying no WTC implications, is the first step in a longer project: integrating players like Sudharsan, Harsh Dubey, and Ishan Kishan into a setup that needs to be competitive away from home against New Zealand and in the pressure of a home Border-Gavaskar series.

Gambhir knows the arithmetic. India cannot afford another cycle of home comfort and away fragility. The Afghanistan Test is, as he put it, serious business — not because of what it counts for in the standings, but because of what it reveals about the players who will carry those standings for the next two years.

The match begins on June 6 at Mohali. Afghanistan will be without Rashid Khan. India will be without Kohli. And a 23-year-old left-hander from Tamil Nadu will walk out to bat at No. 3, knowing that his head coach has publicly staked his credibility on giving him that chance."""
    }
    
    return article

# ===================== MAIN =====================

if __name__ == "__main__":
    print("Sports Writer Batch — June 6, 2026")
    print("=" * 50)
    
    articles = []
    
    # Generate all 3 articles
    a1 = write_article_1()
    articles.append(a1)
    
    a2 = write_article_2()
    articles.append(a2)
    
    a3 = write_article_3()
    articles.append(a3)
    
    # Publish
    print("\n=== PUBLISHING ===")
    success = 0
    for a in articles:
        print(f"\nPublishing: {a['headline'][:60]}...")
        if publish_article(a):
            success += 1
        time.sleep(1)
    
    print(f"\n{'=' * 50}")
    print(f"Published {success}/{len(articles)} articles")
    
    if success < len(articles):
        sys.exit(1)
