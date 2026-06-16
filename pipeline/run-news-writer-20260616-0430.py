#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-16 04:30 UTC run (scheduled videshi-writer-news)
3 fresh articles, distinct from the 02:30 batch (Canada deportations / reverse brain
drain / fiscal deficit) and all saturated 2026-06-15 topics (Iran/Gulf/oil/markets-
rally/Modi-Macron/exam-scandal/AI-offshoring/Australia-migrants):
  1. Federal judge strikes down Trump's $100,000 H-1B fee — immigration
  2. India-US trade deal nears first tranche; USTR Greer to visit June 23-24 — trade
  3. US to pilot domestic H-1B visa renewal in December, mostly for Indians — diaspora-services
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


def wc(body):
    return len(re.sub(r'[#*>\n]', ' ', body).split())


def finalize(article, image_url, image_caption, image_attribution):
    if image_url:
        article["image_url"] = image_url
        article["image_caption"] = image_caption
        article["image_attribution"] = image_attribution
    else:
        print("  \u26a0 No valid image found \u2014 inserting without image")
    article["word_count"] = wc(article["body"])
    print(f"  word_count={article['word_count']}")
    return insert_article(article)


# ========================================================================
# ARTICLE 1: Federal judge strikes down Trump's $100,000 H-1B fee
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: Federal judge strikes down $100,000 H-1B fee")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "John Joseph Moakley United States Courthouse Boston",
        ["moakley", "courthouse", "court house", "federal court", "district court"],
        "The John Joseph Moakley federal courthouse in Boston, where Judge Leo Sorokin struck down the $100,000 H-1B fee")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "United States federal courthouse exterior",
            ["courthouse", "court house", "federal", "district court", "judicial"],
            "A United States federal courthouse; a district judge ruled the $100,000 H-1B fee an unauthorised tax")
    if not image_url:
        px = fetch_pexels_image("courthouse justice law gavel")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "A courtroom gavel; a federal judge voided the $100,000 H-1B visa fee", "Pexels"

    slug = "federal-judge-strikes-down-trump-100000-dollar-h1b-fee-indian-tech-workers-20260616"

    body = """A single ruling from a federal courtroom in Massachusetts has, for now, dismantled the most expensive obstacle ever placed in front of the visa that built the Indian-American tech story. On Monday, U.S. District Judge Leo Sorokin struck down the Trump administration's $100,000 fee on new H-1B petitions, finding that the charge was in substance a tax \u2014 and that the Constitution gives only Congress, not the president, the power to levy it.

For the roughly 70 percent of approved H-1B petitions that go to Indian nationals each year, the decision lands as the most consequential immigration news of 2026 so far. The fee, imposed by presidential proclamation in September 2025, had hung over every Indian engineer, doctor, and researcher hoping to come to the United States on the program, threatening to price out all but the highest earners and the largest employers.

## What the Judge Actually Ruled

Sorokin's reasoning was narrow but decisive. "The Court finds that the Policy imposes a tax on H-1B petitions without the requisite delegation by Congress," he wrote, adding that "there are no statutory powers authorizing Defendants to implement a $100,000 tax on H-1B petitions." Article I of the Constitution reserves the power to authorize and levy taxes to Congress \u2014 and lawmakers, the judge held, never handed that authority to the executive branch.

The lawsuit was brought by a coalition of Democratic state attorneys general, who argued the fee was an unauthorized tax that crippled their ability to staff publicly run colleges, schools, and healthcare systems \u2014 sectors that lean heavily on H-1B talent. Using a provision of the Administrative Procedure Act, Sorokin voided the payment requirement nationwide rather than offering the limited, state-by-state relief the administration had urged.

## A Year of Chaos

The fee's brief life was turbulent from the start. When it was rolled out in the fall of 2025, applying to any petition filed after September 21, it sparked confusion and panic. Some of the biggest technology companies scrambled to bring workers back into the country before the rule took hold, until the administration clarified that the charge applied only to new petitions filed for workers outside the United States \u2014 not to renewals or to those already in the country on eligible status, such as F-1 students changing status.

That clarification softened the blow but did not remove the threat. Layered on top of a new weighted lottery that now favors higher-wage positions and an expansion of consular vetting that includes mandatory social media reviews, the fee had reshaped how Indian professionals and their would-be employers approached the entire system. Monday's ruling does not undo those other changes \u2014 it removes the single largest financial barrier.

## The Fight Is Not Over

The administration is unlikely to accept the defeat quietly, and Congress may yet revive the fee by other means. Within a day of the ruling, Republican Representative Mike Kennedy of Utah began promoting the PROTECT Act, legislation that would codify the $100,000 charge at the congressional level \u2014 precisely the authority Sorokin said the executive lacked. Kennedy's bill would require an H-1B applicant to pay the greater of prevailing wage rates or a $100,000 base, and would press employers to hire American-born workers first.

The legal picture is also muddier than a single ruling suggests. In a separate challenge brought by the U.S. Chamber of Commerce, another judge, Beryl Howell, sided with the administration in December, finding the fee lawful. Appeals are all but certain, and the issue may ultimately travel toward higher courts. For applicants and employers, the practical reality is uncertainty: the barrier is down today, but the ground could shift again.

## Why It Matters to the Diaspora

No single visa is more central to the modern Indian diaspora than the H-1B, the bridge that carried a generation from campuses in Hyderabad and Chennai to boardrooms in Silicon Valley. A $100,000 entry toll did not just raise the cost of that bridge; it changed who could afford to cross it, tilting the program toward elite earners and deep-pocketed firms and away from the early-career strivers who have always defined the pipeline.

Monday's decision restores, at least temporarily, the lower-cost path that built the community. But the diaspora has learned to read these victories carefully. With the PROTECT Act in play, conflicting rulings on the books, and appeals looming, the smart posture is cautious relief rather than celebration. The barrier has fallen \u2014 but the people who erected it have not given up, and the next chapter of the H-1B story will be written in Congress and the appellate courts, not in a single Boston courtroom.

**Sources:** Reuters, The Wall Street Journal, NBC News"""

    article = {
        "headline": "A Federal Judge Just Struck Down Trump's $100,000 H-1B Fee. Indian Tech Workers Are the Biggest Winners.",
        "subheadline": "U.S. District Judge Leo Sorokin ruled the charge an unauthorised tax that only Congress could impose \u2014 lifting, for now, the steepest barrier ever placed in front of the visa that carries 70 percent of its approvals to Indian nationals.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Indians receive more than 70 percent of approved H-1B petitions each year, so a court striking down the $100,000 fee directly reopens the lower-cost path that built the Indian-American tech community \u2014 but with a PROTECT Act bill, a conflicting ruling, and appeals looming, the relief is provisional and every prospective applicant must weigh that the barrier could return.",
        "sources": ["Reuters", "The Wall Street Journal", "NBC News"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: India-US trade deal nears first tranche; Greer to visit
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: India-US trade deal nears first tranche")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "container ship cargo port India shipping",
        ["container", "cargo", "port", "ship", "harbour", "harbor", "terminal", "freight"],
        "A container terminal; India and the United States are racing to finalise the first tranche of a bilateral trade deal")
    if not image_url:
        # Trade story but Goyal is central → Wikipedia fallback for a named official
        wiki = fetch_wikipedia_person_image("Piyush Goyal")
        if wiki and validate_image(wiki):
            image_url = wiki
            image_caption = "Commerce Minister Piyush Goyal, who says the first tranche of the India-US trade deal could close by mid-July"
            image_attribution = "Wikimedia Commons"
    if not image_url:
        px = fetch_pexels_image("cargo container ship port export trade")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "Cargo containers at a port, symbol of India-US trade negotiations", "Pexels"

    slug = "india-us-trade-deal-first-tranche-ustr-greer-visit-june-2026-may-exports-jump-20260616"

    body = """India and the United States are entering the final stretch of a trade negotiation that has been two years in the making, with both sides now signalling that the first tranche of a bilateral pact could be signed within weeks. U.S. Trade Representative Jamieson Greer will travel to New Delhi on June 23 and 24 for talks aimed at "giving final touches" to the interim agreement, India's Trade Secretary Rajesh Agrawal said \u2014 a visit that comes just days after Prime Minister Narendra Modi and President Donald Trump met on the sidelines of the G7 summit in France.

The timing is no accident. Commerce Minister Piyush Goyal has said for weeks that the first phase of the deal could be executed by the middle of July, calling it a "very, very vibrant" opening tranche. The negotiations trace back to early 2025, when Modi and Trump agreed to pursue an arrangement aimed at more than doubling bilateral trade to $500 billion by 2030. Goods trade between the two countries already crossed roughly $140 billion in 2025-26.

## Fresh Data, Fresh Pressure

The diplomacy is unfolding against a backdrop of trade numbers that capture both India's strength and its strain. Merchandise exports jumped 18 percent in May to an estimated $45.2 billion, led by engineering goods, petroleum products, and electronics \u2014 a robust showing. But imports climbed even faster, up nearly 21 percent to $73.41 billion, widening the year-on-year merchandise trade deficit to $28.21 billion from $22.56 billion a year earlier. Measured against April, the gap actually narrowed slightly, easing from $28.38 billion as exporters navigated volatile energy prices and Gulf disruptions.

That mix underscores why New Delhi is pressing so hard for preferential access to the American market. April-to-May goods exports were nearly flat against a year earlier, and India badly needs the tariff relief a deal would bring to keep its export engine running. Services remain the quiet strength: exports there rose to $36.76 billion in May, leaving a healthy services surplus that cushions the goods gap.

## The Sticking Points

The road to a signature is not smooth. Under the framework agreed in February, the United States was to bring tariffs on Indian goods down to 18 percent from the punishing 50 percent imposed earlier \u2014 a level that included penalties tied to India's purchases of Russian oil. But Washington has opened new fronts even as it negotiates. This month the USTR proposed an additional 12.5 percent tariff on imports from India and other countries, citing forced-labour concerns, and is separately weighing a tariff under a Section 301 probe alleging that India has excess capacity in textiles and steel.

India has rejected those characterizations and is engaging through the Section 301 process, with officials saying they will seek clear answers on the proposed new tariffs while finalising the pact. "Discussions with USTR will be centred around giving final touches to our interim deal," Agrawal said. The deal is also expected to commit India to buying more American energy \u2014 a lever that has taken on new weight as the Gulf war reshaped global oil flows.

## A Relationship Repaired

The warming mood is itself notable. Ties between New Delhi and Washington had been strained by the U.S. tariffs and by Trump's repeated claims, which India denies, that he helped end India's brief conflict with Pakistan last year. The easing of the U.S.-Iran war and the reopening of the Strait of Hormuz have added a tailwind, lowering the energy-cost pressures that complicated India's trade math. U.S. officials have been careful to manage expectations \u2014 no deal was expected to close at the G7 itself \u2014 but one senior administration official said a "very good deal is possible."

## Why It Matters to the Diaspora

For the Indian diaspora, a U.S.-India trade pact is more than an abstraction about tariff schedules. It shapes the fortunes of the Indian exporters and small businesses \u2014 nearly half of the country's exports come from smaller firms \u2014 whose growth ripples back through family networks and investment flows. It influences the strength of the rupee against the dollar, and with it the value of every remittance sent home and every NRE deposit held back in India.

A deeper economic partnership also tends to smooth the broader relationship that governs how Indians move, study, and work between the two countries. As the diaspora has learned from the parallel battles over visas and fees, trade and migration are threads of the same fabric: when New Delhi and Washington are negotiating in good faith on commerce, the climate for the people who connect the two economies tends to improve as well. The next test comes on June 23, when Greer lands in New Delhi.

**Sources:** Reuters, Mint, Outlook Business"""

    article = {
        "headline": "India and the US Are Days From a Trade Deal. Their Top Negotiator Lands in Delhi on June 23.",
        "subheadline": "USTR Jamieson Greer will visit New Delhi to finalise the first tranche of a bilateral pact that aims to double trade to $500 billion \u2014 even as May exports jumped 18 percent and Washington floats fresh tariffs on Indian textiles and steel.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "trade",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "A US-India trade pact shapes the rupee-dollar rate that determines the real value of every remittance and NRE deposit, lifts the Indian exporters and small businesses whose fortunes ripple back through diaspora family and investment networks, and signals a warming bilateral climate that historically eases the visa and mobility rules governing how NRIs move between the two countries.",
        "sources": ["Reuters", "Mint", "Outlook Business"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: US to pilot domestic H-1B visa renewal in December
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: US to pilot domestic H-1B visa renewal in December")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Embassy of the United States New Delhi India",
        ["embassy", "united states", "new delhi", "consulate", "chancery"],
        "The U.S. Embassy in New Delhi; a new pilot will let many H-1B holders renew visas inside the United States instead")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "United States visa passport document",
            ["visa", "passport", "us visa", "stamp", "document"],
            "A United States visa; the State Department will pilot domestic H-1B renewals from December")
    if not image_url:
        px = fetch_pexels_image("passport visa travel documents airport")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "A passport with travel visas; the US is piloting domestic H-1B renewals", "Pexels"

    slug = "us-domestic-h1b-visa-renewal-pilot-december-2026-indian-tech-professionals-20260616"

    body = """For years, one of the quiet miseries of life on an H-1B visa has been the renewal trip \u2014 the obligation to fly thousands of miles back to India, queue at a consulate, and gamble on a wait that can stretch from six months to a year before a stamp lets a worker return to the job they never left. That ritual is about to ease. The U.S. State Department will launch a pilot program in December to allow certain H-1B visa holders to renew their visas from inside the United States, and officials say the vast majority of those first in line will be Indian nationals.

Julie Stufft, the Deputy Assistant Secretary of State for Visa Services, laid out the plan in unusually direct terms. "In India, the demand is still very high. The wait time of 6, 8, and 12 months is not what we need and is not indicative of how we view India," she said. Over a three-month window beginning in December, the department will issue 20,000 visas to foreign nationals already inside the country \u2014 and "the vast majority of those will be Indian nationals living in the U.S.," she added, with the program set to expand as it matures.

## How the Pilot Works

The mechanism is deceptively simple but has been years in the making. Under the current system, a visa stamp \u2014 the document that permits re-entry into the United States \u2014 generally must be obtained at a U.S. consulate abroad, even for someone who has lived and worked in America for years on a valid status. The pilot removes that requirement for eligible H-1B holders, letting them renew domestically rather than travelling overseas and risking long administrative delays that can separate workers from their jobs and families.

"We want to make sure that Indian travelers can get appointments as quickly as possible. One way we are doing that is through the domestic visa renewal program, which is focused very much on India. We are piloting that," Stufft said. The first group will number 20,000, and the State Department expects to expand it over time. A Federal Register notice \u2014 the first official publication of the program's rules \u2014 is expected soon and will spell out who is eligible to apply in the opening tranche and how the process will work.

## A Promise From the Reagan Centre

The program is not arriving out of nowhere. It was mentioned in the joint statement between the two governments and was announced by Prime Minister Narendra Modi during his address to the Indian diaspora at the Ronald Reagan Centre \u2014 a moment that drew loud approval from a community that has long borne the brunt of consular backlogs. Because Indians are the largest group of skilled workers in the United States, Stufft said, "we hope that India will benefit quite a bit from this program."

The relief is also strategic. By letting people renew at home, the State Department frees its missions in India to concentrate on first-time applicants \u2014 the students, the new hires, the families joining relatives \u2014 who have faced some of the longest queues in the world. "It will prevent people from having to travel back to India or anywhere for a visa appointment to get their visa renewed. It will allow our missions in India to concentrate on new applicants," she said.

## A Rare Piece of Good News

The pilot lands at a fraught moment for Indian professionals navigating the American immigration system. It comes alongside a court battle over a $100,000 H-1B fee, a new weighted lottery that favors higher wages, and an expansion of consular vetting that now includes social media reviews. Against that backdrop, a program that removes a concrete, recurring hardship \u2014 the dreaded renewal trip \u2014 stands out as a tangible win rather than a contested policy.

It is also a revival of an idea with a track record. A similar domestic renewal pilot ran in 2024 and was widely seen as a success before lapsing; the December program represents its return at a larger scale, with India explicitly at its center.

## Why It Matters to the Diaspora

For hundreds of thousands of Indian families building lives in the United States, the renewal trip has been a source of genuine anxiety \u2014 a forced separation, an unpredictable wait, and the small but real fear that something will go wrong at a consulate window an ocean away from home and work. Removing that hurdle for even 20,000 people in the first wave, with expansion to follow, changes the texture of daily life for the community that depends most on the H-1B.

The deeper significance is in the signal. After a year defined by restrictions, fees, and friction, a program built explicitly around Indian convenience reads as an acknowledgement of how central Indian talent has become to the American economy. The diaspora will watch the Federal Register notice closely for the eligibility fine print \u2014 but for once, the news is something to look forward to rather than to brace against.

**Sources:** The Indian Eye, Press Trust of India, U.S. Department of State"""

    article = {
        "headline": "No More Flying Home to Renew a Visa: The US Will Pilot Domestic H-1B Renewals in December, Mostly for Indians",
        "subheadline": "The State Department will issue 20,000 visas over three months to holders already in the country, ending the dreaded renewal trip for thousands \u2014 and officials say the vast majority of the first group will be Indian nationals.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-services",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Indians are the largest group of skilled workers in the US and have borne the worst of consular backlogs, so a domestic H-1B renewal pilot \u2014 20,000 slots from December, mostly for Indian nationals \u2014 ends the forced, months-long renewal trip home that has separated diaspora families from their jobs, and frees India's missions to clear the queues facing first-time student and worker applicants.",
        "sources": ["The Indian Eye", "Press Trust of India", "U.S. Department of State"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# MAIN
# ========================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"VIDESHI NEWS WRITER \u2014 {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    results = []
    results.append(("H-1B fee struck down", write_article_1()))
    results.append(("India-US trade deal first tranche", write_article_2()))
    results.append(("Domestic H-1B renewal pilot", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
