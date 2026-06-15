#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-15 PM6 batch (scheduled videshi-writer-news, 20:30 UTC run)
3 fresh articles, distinct from all earlier 2026-06-15 batches:
  1. US-Iran Gulf peace deal: India welcomes ceasefire, Strait of Hormuz to reopen, oil tumbles (geopolitics)
  2. MEA repatriation: 9.27 lakh Indians brought home from West Asia, multi-nation transit routes (diaspora-safety)
  3. Indian markets rally + RBI NRI deposit push: Sensex/Nifty climb ~3% in two sessions on Gulf peace (economy)
"""

import json, os, subprocess, re, time, datetime, urllib.parse, requests

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                key = key.strip().replace('export ', '')
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/.env.pexels'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=8):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers=UA, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                width = ii.get("width", 0)
                if url and "image" in mime and width > 300:
                    results.append({"url": url, "title": page.get("title", ""),
                                    "width": width, "height": ii.get("height", 0)})
            print(f"  \u2713 Wikimedia Commons: {len(results)} results for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        print("  \u26a0 No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        for photo in data.get("photos", []):
            url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
            if url:
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def validate_image(url):
    try:
        r = requests.get(url, timeout=12, stream=True, allow_redirects=True, headers=UA)
        ct = r.headers.get("Content-Type", "")
        chunk = r.raw.read(12000)
        if r.status_code == 200 and "image" in ct and len(chunk) > 5000:
            print(f"  \u2713 Image validated: {r.status_code}, {ct}, {len(chunk)}+ bytes")
            return True
        print(f"  \u2717 Image validation failed: {r.status_code}, {ct}, {len(chunk)} bytes")
    except Exception as e:
        print(f"  \u2717 Image validation error: {e}")
    return False


def pick_commons_image(query, keywords, caption):
    for img in fetch_wikimedia_commons_images(query, 8):
        tl = img["title"].lower()
        if any(kw in tl for kw in keywords) and validate_image(img["url"]):
            return img["url"], caption, "Wikimedia Commons"
    return None, "", ""


def insert_article(article):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=20)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  \u2713 Inserted: {result[0].get('slug', 'unknown')}")
            return True
        print("  \u2713 Inserted (no body returned)")
        return True
    print(f"  \u2717 Insert failed: {r.status_code} \u2014 {r.text[:300]}")
    return False


def finalize(article, image_url, image_caption, image_attribution):
    if image_url:
        article["image_url"] = image_url
        article["image_caption"] = image_caption
        article["image_attribution"] = image_attribution
    else:
        print("  \u26a0 No valid image found \u2014 inserting without image")
    return insert_article(article)


# ========================================================================
# ARTICLE 1: US-Iran Gulf peace deal — India welcomes, Hormuz to reopen
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: US-Iran Gulf peace deal")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Strait of Hormuz oil tanker ship",
        ["hormuz", "strait", "tanker", "ship", "oil", "persian gulf", "vessel"],
        "An oil tanker in the Strait of Hormuz, the waterway set to reopen toll-free under the US-Iran framework deal")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "oil tanker crude shipping sea",
            ["tanker", "oil", "ship", "crude", "vessel", "shipping"],
            "A crude oil tanker at sea as the Strait of Hormuz prepares to reopen to traffic")
    if not image_url:
        px = fetch_pexels_image("oil tanker ship sea cargo")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "An oil tanker at sea, the kind of vessel that carries crude through the Strait of Hormuz", "Pexels"

    slug = "india-welcomes-us-iran-gulf-peace-deal-strait-hormuz-reopen-oil-falls-20260615"

    body = """India breathed a little easier on Monday. After nearly four months of a war that choked off a fifth of the world's oil supply and stranded hundreds of ships inside the Persian Gulf, the United States and Iran announced a framework agreement to end the conflict and reopen the Strait of Hormuz \u2014 and few countries have more riding on that single waterway than India.

New Delhi welcomed the ceasefire within hours. External Affairs Ministry spokesperson Randhir Jaiswal, addressing an inter-ministerial briefing in the capital, said India hoped the agreement would lead to "lasting peace in the region" and stressed India's stake in "unimpeded freedom of navigation through the Strait of Hormuz." He added that India welcomed all steps towards peace and regional stability, and hoped the breakthrough would encourage peace efforts in Ukraine as well.

## What Was Agreed

U.S. President Donald Trump, arriving in France for a G7 summit, said the deal had "all been signed," with a formal memorandum of understanding to be inked in Switzerland on Friday, June 19, attended by Vice President JD Vance. Pakistani Prime Minister Shehbaz Sharif, whose country mediated, confirmed the signing date. The framework reopens the Strait of Hormuz on a toll-free basis, lifts the U.S. naval blockade of Iranian ports, and establishes a 60-day technical negotiation window to tackle the harder questions of Iran's nuclear programme, sanctions relief and reconstruction.

The market reaction was immediate. Brent crude tumbled about 5 percent to roughly $82.8 a barrel \u2014 its lowest since March \u2014 as traders anticipated the return of flows through a strait that, before the war, saw more than 130 ships pass daily carrying about 20 percent of the world's oil.

## Why the Strait Matters So Much to India

India is the world's third-largest oil importer, and it buys the overwhelming majority of that crude from the Gulf. Every dollar off the oil price eases pressure on three things at once: inflation, the rupee, and the country's trade deficit. The rupee, Asia's second-worst-performing major currency this year, gained 0.41 percent to 94.71 per dollar on the news, while the 10-year government bond yield fell.

The first tangible sign of normalisation was already at sea. India's Petronet sent the LNG carrier Disha through the Strait of Hormuz on Monday \u2014 the only clearly visible shipment in vessel-tracking data \u2014 carrying 62,370 metric tonnes of liquefied natural gas, due to arrive at Dahej in Gujarat on June 18.

## Caution Before Celebration

The optimism comes with caveats. Global shippers said confidence in resuming Hormuz transits could take weeks to rebuild, and that navigation will only restart once safety \u2014 including the clearing of mines \u2014 is assured. Industry body BIMCO estimates at least 600 vessels remain trapped inside the Persian Gulf, including 250 tankers. The U.S. military, in an advisory note, said its blockade of Iranian ports "remains in effect" pending completion of the agreement on June 19, warning vessels not to cross "until explicit direction is given."

Energy analysts at Wood Mackenzie cautioned that even once the strait reopens, the more than 14 million barrels per day of output shut by the war could take three months to return to 70 percent of prior levels and six months to reach 90 percent. A full recovery, in other words, is a story measured in months, not days.

## Why It Matters to the Diaspora

For the Indian diaspora, the Gulf peace deal lands on two fronts at once. The first is economic: lower oil prices and a steadier rupee directly affect the value of remittances, the returns on NRI deposits, and the health of the Indian markets in which so many overseas Indians invest. A war-driven oil shock is precisely the kind of macro event that erodes the purchasing power of money sent home.

The second is deeply human. The Gulf is home to roughly nine million Indians \u2014 the largest concentration of the diaspora anywhere in the world \u2014 working in the UAE, Saudi Arabia, Qatar, Kuwait, Oman and Bahrain. For those families, and for the relatives in India who depend on their earnings, a ceasefire means reopened airspaces, resumed flights and a path back to normal life after months of evacuations and closed skies. The strait reopening is, in the end, about more than barrels of crude. It is about whether millions of Indian workers in the Gulf can stop living week to week on the edge of a war.

**Sources:** Reuters, LiveMint, Dainik Bhaskar (Bhaskar English)"""

    article = {
        "headline": "The War That Choked India's Oil Lifeline May Be Ending. New Delhi Welcomes the US-Iran Gulf Deal.",
        "subheadline": "A framework agreement to reopen the Strait of Hormuz sent crude tumbling 5 percent and lifted the rupee \u2014 a rare piece of good macro news for the world's third-largest oil importer and the nine million Indians in the Gulf.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "The Gulf hosts roughly nine million Indians \u2014 the world's largest diaspora concentration \u2014 and India is the third-largest oil importer, so a ceasefire that reopens the Strait of Hormuz directly affects remittance values, NRI deposit returns, Indian markets, and the daily lives of millions of Indian workers who endured months of evacuations and closed airspaces.",
        "sources": ["Reuters", "LiveMint", "Bhaskar English"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: MEA repatriation — 9.27 lakh Indians home from West Asia
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: MEA repatriation from West Asia")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Ministry of External Affairs India South Block New Delhi",
        ["south block", "external affairs", "new delhi", "secretariat", "building", "india"],
        "South Block in New Delhi, home to India's Ministry of External Affairs, which is coordinating the West Asia repatriation effort")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Air India aircraft airport passengers",
            ["air india", "aircraft", "airport", "boeing", "airbus", "plane"],
            "Special flights have brought hundreds of thousands of Indians home from the Gulf and West Asia")
    if not image_url:
        px = fetch_pexels_image("airport passengers airplane terminal")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "Passengers at an airport terminal, as repatriation flights from West Asia continue", "Pexels"

    slug = "mea-repatriation-927000-indians-home-west-asia-multi-nation-transit-routes-20260615"

    body = """Behind the headlines about oil prices and ceasefires lies one of the largest peacetime movements of Indian citizens in recent memory. Since the West Asia war erupted on February 28, the Ministry of External Affairs says around 9.27 lakh \u2014 roughly 927,000 \u2014 people have returned to India from the Gulf and conflict-affected zones, in an operation that has stitched together special flights, partially reopened airspaces and improvised overland routes through neighbouring countries.

The scale of the effort, and the machinery behind it, was laid out by Aseem R. Mahajan, Joint Secretary (Gulf) at the MEA, during an inter-ministerial briefing in New Delhi. A dedicated control room in the Ministry remains operational around the clock, he said, coordinating with Indian missions whose round-the-clock helplines are "pro-actively assisting our citizens."

## A Logistics Operation Across a War Zone

The numbers tell the story of a region in flux. Mahajan said around 100 flights were expected to operate from the UAE to India in a single day, with additional flights from Saudi Arabia and Oman. With Qatar's airspace partially open, Qatar Airways was expected to run eight to 10 flights to India; Bahrain's airspace had reopened, and Gulf Air announced limited operations from Bahrain and non-scheduled commercial flights from Dammam in Saudi Arabia.

For Indians trapped inside the war's epicentre, the routes have been more circuitous. The Indian Embassy in Tehran has facilitated the movement of more than 2,230 nationals out of Iran \u2014 including 987 students and 657 fishermen \u2014 overland to Armenia and Azerbaijan, from where they fly home. Earlier government figures recorded 1,777 Indians brought back specifically via the Armenia and Azerbaijan corridors, and 4,415 evacuated from conflict zones in Iran and Israel aboard 19 special flights. As airspaces across the region closed, the government activated these multi-nation transit routes to keep an exit path open.

## Parliament Steps In

The crisis has drawn the attention of India's lawmakers. The Parliamentary Standing Committee on External Affairs, chaired by Congress MP Shashi Tharoor, held what he called one of its most comprehensive discussions ever \u2014 all 17 members present spoke, and the session ran well beyond its scheduled hours. MEA officials briefed members on the safety, security and repatriation of the diaspora, while members raised concerns ranging from oil and gas supplies to the plight of Indian students in West Asia whose exams had been disrupted.

"Everyone had questions and concerns about the overall situation, the impact, the safety and security of our nationals, the diaspora, the oil and gas supplies," Tharoor told reporters after the meeting. "We got some answers, but didn't get all."

## Seafarers in the Crosshairs

One group has remained especially exposed: Indian seafarers, who crew a significant share of the world's merchant fleet. The Ministry of Ports, Shipping and Waterways said it is coordinating with the MEA, Indian missions and shipping companies to ensure their welfare as vessels navigate the contested Strait of Hormuz. The concern is not abstract \u2014 Indian sailors have been among the casualties of the Gulf conflict, and the Directorate General of Shipping has moved to restrict deployment into the most dangerous waters.

## Why It Matters to the Diaspora

For the global Indian community, the repatriation effort is a real-time test of a promise the Indian state makes to its citizens abroad: that wherever they are, the government will come for them. The Gulf is home to roughly nine million Indians, the largest concentration of the diaspora anywhere, and the vast majority are blue-collar and white-collar workers whose remittances are a lifeline for families back home.

The crisis exposes the diaspora's structural vulnerability. Unlike tourists, Gulf workers cannot simply leave \u2014 their livelihoods, contracts and savings are tied to the region. When war closes the skies, hundreds of thousands of families on both ends of the remittance chain are thrown into uncertainty at once. The MEA's control rooms, the overland convoys through the Caucasus, and the parliamentary scrutiny all point to a single recognition: that India's relationship with its diaspora is no longer just about pride and investment, but about the hard duty of protection. How well the system performs in this war will shape how secure the next generation of Indian migrants feels about working abroad at all.

**Sources:** The Hindu BusinessLine, The Indian Eye (ANI), Ministry of External Affairs briefings"""

    article = {
        "headline": "9.27 Lakh Indians Brought Home From a War Zone. Inside India's Largest Peacetime Evacuation.",
        "subheadline": "Special flights, reopened airspaces and overland convoys through Armenia and Azerbaijan have carried nearly a million Indians out of West Asia \u2014 a real-time test of the promise the Indian state makes to its citizens abroad.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "The Gulf hosts roughly nine million Indians \u2014 mostly workers whose remittances sustain families back home \u2014 and the MEA's evacuation of 9.27 lakh people via flights and overland routes through the Caucasus is a direct test of India's duty to protect its diaspora when war closes the skies, shaping how secure the next generation of migrants feels about working abroad.",
        "sources": ["The Hindu BusinessLine", "The Indian Eye (ANI)", "Ministry of External Affairs"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: Indian markets rally on Gulf peace + RBI NRI deposit push
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: Markets rally + NRI deposit push")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Bombay Stock Exchange building Mumbai",
        ["bombay stock exchange", "bse", "mumbai", "stock exchange", "building", "dalal street"],
        "The Bombay Stock Exchange in Mumbai, where the Sensex jumped on news of the Gulf peace deal")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Reserve Bank of India building Mumbai",
            ["reserve bank", "rbi", "mumbai", "bank", "building"],
            "The Reserve Bank of India, which has rolled out measures to attract NRI deposits and steady the rupee")
    if not image_url:
        px = fetch_pexels_image("stock market trading chart finance")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "A stock market trading display, as Indian equities rallied on the Gulf peace deal", "Pexels"

    slug = "indian-markets-rally-gulf-peace-rbi-nri-deposit-rate-hike-rupee-stabilise-20260615"

    body = """For Indian markets, the end of a war is the best stimulus money can't buy. The benchmark Nifty 50 rose 0.98 percent to 23,853.90 on Monday and the BSE Sensex added 0.97 percent to 76,264.33, capping a two-session run of roughly 3 percent gains, as oil prices tumbled on news that the United States and Iran had reached a framework deal to end their war and reopen the Strait of Hormuz.

"Now that the Iran war appears to be nearing an end, investors have a significant source of comfort," said Gaurav Bhandari, chief executive of Monarch Networth Capital, who expects the Nifty to reach the 27,000-28,000 range by year-end, provided monsoon risks recede. The index is still down about 8.7 percent for 2026.

## A Broad-Based Rally

The advance was wide. Fourteen of the 16 major sectors rose, broader small-caps and mid-caps gained 1.1 and 1.3 percent, and Asian markets jumped 2.7 percent in tandem. Infrastructure major Larsen & Toubro, which earns significant revenue from the Middle East, climbed 3 percent. Brent crude's 5.2 percent slide to about $82.8 a barrel \u2014 its lowest since March \u2014 was the engine behind it all: for the world's third-largest oil importer, cheaper crude eases inflation, the trade deficit and pressure on the rupee at once. The currency duly gained 0.41 percent to 94.71 per dollar, and the 10-year bond yield fell.

## The Other Half of the Story: Wooing NRI Money

The rally lands at a delicate moment. Foreign portfolio investors have pulled a record \u20b92.87 lakh crore \u2014 roughly $30 billion \u2014 out of Indian equities so far in 2026, the most ever, as global funds fled to South Korea and Taiwan's semiconductor-heavy markets. To shore up the rupee and pull in dollars, the Reserve Bank of India and the country's banks have turned to a familiar and loyal source of capital: the diaspora.

In the past week, the RBI said it would bear the full hedging cost on three- to five-year non-resident deposits, part of a broader package to encourage overseas inflows. Banks responded fast. HDFC Bank raised rates on three- to five-year NRI foreign-currency deposits by 235-265 basis points to 6 percent. State Bank of India lifted rates by as much as 300 basis points. AU Small Finance Bank now offers 7.1 percent on three-year deposits, and Yes Bank up to 7.10 percent on five-year tenures. Lenders could raise $35 billion to $40 billion through these foreign-currency deposits by September, and the RBI has even signalled it is open to banks guaranteeing offshore loans to NRIs who then place those funds as deposits.

## Why the Optimism May Hold

Some strategists argue the worst of the foreign exodus is over. Abhay Laijawala of Lighthouse Canton said India's outflows may have "largely run their course," and that the country's very lack of exposure to chip fabrication \u2014 the trade that has dominated Korea and Taiwan \u2014 could prove an "advantage of absence," leaving India a deep universe of power, data-centre, cooling and capital-goods stocks tied to the next phase of AI spending. BlackRock has similarly argued that Indian equities were "over-punished" for lacking a direct AI play. Monarch's Bhandari noted that with the RBI's measures stabilising the rupee and inflation under control, the record $30 billion in outflows "could start to reverse."

## Why It Matters to the Diaspora

For NRIs, this is a rare moment when patriotism and self-interest point the same way. The deposit-rate war means an overseas Indian can now park dollars in an Indian bank at 6 to 7.1 percent \u2014 yields that comfortably beat most Western savings products \u2014 with the RBI absorbing the currency-hedging risk on longer tenures. For a community that has long used NRI and FCNR deposits as a bridge between two financial lives, the new rates are among the most attractive in years.

The timing matters too. A market that has fallen 8.7 percent in 2026 and a rupee near record lows mean diaspora investors looking to buy Indian equities or send money home are doing so at relatively cheap levels \u2014 and the Gulf peace deal offers a plausible catalyst for a rebound. India is, in effect, asking its diaspora to do what it has done in every past crisis: anchor the homeland's finances when global capital takes flight. The unusually generous terms on offer suggest New Delhi knows exactly how much it is counting on that loyalty.

**Sources:** Reuters, NSDL data via Dainik Jagran, Morningstar Investment Research India"""

    article = {
        "headline": "India's Markets Just Got the One Thing Money Can't Buy: an End to War. The Diaspora Is Being Asked to Help.",
        "subheadline": "The Sensex and Nifty rallied nearly 3 percent in two sessions as the Gulf peace deal sank oil \u2014 even as the RBI and banks hike NRI deposit rates to 7 percent to pull dollars back after a record $30 billion foreign exodus.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "The RBI and banks have hiked NRI and FCNR deposit rates to 6-7.1 percent \u2014 beating most Western savings products \u2014 while absorbing currency-hedging risk, so for the diaspora this is a rare moment when patriotism and self-interest align: India is explicitly asking overseas Indians to anchor its finances after a record $30 billion foreign exodus, and the cheap rupee and post-war market rebound make it a compelling entry point.",
        "sources": ["Reuters", "NSDL data via Dainik Jagran", "Morningstar Investment Research India"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# MAIN
# ========================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"VIDESHI NEWS WRITER (PM6) \u2014 {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    results = []
    results.append(("US-Iran Gulf peace deal", write_article_1()))
    results.append(("MEA repatriation West Asia", write_article_2()))
    results.append(("Markets rally + NRI deposits", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
