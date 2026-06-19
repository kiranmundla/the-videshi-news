#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-19 22:30 UTC run (scheduled videshi-writer-news)
3 fresh articles distinct from all 2026-06-18/19 published news topics
(IT-stock crash, Jio IPO, GIFT City dollars, foreigners registration rules,
India-Canada CEPA, RBI NRI deposit caps, AAPI physician fee, Hormuz reopening,
UAE consular operator, fuel retailer losses, PM-VBRY disbursal, NSE IPO, OCI
overhaul, Mumbai water rationing, defence production, rupee recovery,
remittances record, Yoga Day, US student collapse, anti-Hindu hate, Anil
Menon, World Cup players, DHS duration-of-status, VivaTech, Iran war, UK-India
clean energy, Warsh Fed, Modi Paris, EU-India FTA):

  1. India's weakest monsoon in 11 years — El Niño-driven deficit threatens
     food inflation and crops (broader story than the Mumbai-only water piece)
  2. The $100,000 H-1B fee is BACK — June 12 administrative stay reinstated it
     as of June 17, reversing the strike-down NRIs celebrated days earlier
  3. India-US trade deal nears the finish — USTR Greer visits June 23-24 to
     finalise the framework; first tranche expected by mid-July
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
                if url and "image" in mime and width > 300 and not url.lower().endswith(".svg"):
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
        r = requests.get(url, timeout=15, stream=True, allow_redirects=True, headers=UA)
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
# ARTICLE 1: Weakest monsoon in 11 years
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: Weakest monsoon in 11 years")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "monsoon rain India farmer paddy field",
        ["monsoon", "rain", "paddy", "farmer", "field", "agriculture"],
        "A farmer in an Indian paddy field; a delayed, deficient monsoon is threatening summer-sown crops")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "drought India cracked earth reservoir",
            ["drought", "reservoir", "dry", "lake"],
            "Parched land in India as the 2026 monsoon runs the weakest in 11 years")
    if not image_url:
        image_url = fetch_pexels_image("monsoon rain india farm field")
        if image_url and validate_image(image_url):
            image_caption = "Monsoon rains over an Indian field; the 2026 season is the country's weakest in 11 years"
            image_attribution = "Pexels"
        else:
            image_url = None

    slug = "india-monsoon-weakest-11-years-el-nino-deficit-food-inflation-crops-20260619"

    body = """India is staring at its weakest monsoon in eleven years, and the consequences are already rippling from parched reservoirs in Mumbai to the price of vegetables in kitchens across the country \u2014 and, increasingly, into the grocery bills of the diaspora that buys Indian rice, spices and produce abroad.

The India Meteorological Department is forecasting the lowest seasonal rainfall since 2015, with the June-to-September monsoon expected to deliver around 90 percent of the long-period average. After arriving over Kerala on June 4 \u2014 three days late \u2014 the monsoon raced across nineteen states in two weeks, then stalled. For seven days it sat motionless at Bhadrachalam in Telangana, leaving the skies over Maharashtra, Gujarat, Madhya Pradesh, Rajasthan and Karnataka largely cloudless well into the third week of June. In the first ten days of the month, the country received rainfall 26.5 percent below normal.

## El Ni\u00f1o, the Culprit

The villain this year is a strengthening El Ni\u00f1o, the Pacific warming pattern that reliably suppresses the Indian monsoon and is, by several measures, shaping up to be more intense than usual. Western disturbances \u2014 weather systems drifting in from the Mediterranean \u2014 have compounded the problem by blocking the monsoon's northward march. Eight states recorded heatwave conditions in mid-June, with the mercury topping 45 degrees Celsius in Prayagraj.

The IMD expects a revival around June 25, when a circulation near the Odisha\u2013West Bengal coast could finally drag moisture deep into the country's core farming belt. West-coast rains are forecast to pick up from June 22, reaching Mumbai and Surat. But forecasters are blunt that the coming spell is unlikely to erase the deficits already banked: the season has been hobbled from the start.

## Why It Matters for the Economy

The monsoon delivers roughly 70 percent of India's annual rainfall and waters a farm sector where nearly half the land lacks irrigation and about half the population earns its living. A weak monsoon delays the planting of rice, cotton, soybeans and pulses, and threatens the harvests that anchor food prices. The Reserve Bank of India has already pared its growth forecast and raised its inflation estimate, naming the monsoon among its chief risks.

The damage is becoming visible crop by crop. In Karnataka and Kerala's coffee-growing districts, cumulative rainfall is running 29 to 45 percent below normal, and growers warn of stunted berry development and a surge in white stem borer infestations. India, the world's second-largest sugar producer, could see output cut by around a million tonnes even under a moderate El Ni\u00f1o. Mumbai, meanwhile, has rationed water \u2014 cutting supply to construction sites and slashing industrial use by 20 percent \u2014 after its driest June in over a decade left the city's seven feeder lakes at barely 10 percent of capacity, roughly forty days of water.

## A Thinner Safety Net

There is a measure of reassurance. Economists at Barclays and HSBC point out that India's agriculture is less hostage to the rains than it once was: 55 percent of the cropped area is now irrigated, up from 40 percent in 2010-11, and reservoir storage nationally sits near 29 percent, above the ten-year average thanks to last year's abundant rains. The bigger threat, several argue, may be the heat itself, which is hardest on perishable fruit and vegetables. Still, the buffers are thinner in the rain-fed heartland, and a prolonged dry spell would test them.

## Why It Matters to the Diaspora

For the global Indian diaspora, a failing monsoon is not a distant agricultural footnote \u2014 it lands on the dinner table. Indian grocery stores from Edison to Southall to Brampton stock basmati rice, atta, lentils, tea, coffee, sugar and spices whose prices and availability track the harvest back home. A deficient season tends to push New Delhi toward export curbs on rice and sugar to protect domestic supply, exactly the kind of move that sent diaspora basmati and onion prices spiking in past drought years.

There is a financial dimension too. A weak monsoon stokes food inflation, pressures the rupee and complicates the RBI's rate path \u2014 all of which shape the returns NRIs earn on Indian deposits and investments, and the rate at which their remittances convert at home. And for the millions of diaspora families with relatives still farming in Maharashtra, Karnataka or the Gangetic plains, a dry year is a personal worry as much as a macroeconomic one: it is parents and cousins whose incomes hinge on rain that has not yet come.

**Sources:** Reuters, The Hindu BusinessLine, India Meteorological Department, Dainik Bhaskar"""

    article = {
        "headline": "India Is Heading for Its Weakest Monsoon in 11 Years. The Bill Will Land on Dinner Tables \u2014 Including the Diaspora's.",
        "subheadline": "A strengthening El Ni\u00f1o has left the 2026 monsoon delayed and deficient, with the IMD forecasting the lowest rainfall since 2015, Mumbai rationing water, and coffee, sugar and pulse crops already at risk.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "A failing monsoon stokes food inflation and pushes New Delhi toward rice and sugar export curbs \u2014 the moves that spike basmati and onion prices in diaspora grocery stores abroad \u2014 while pressuring the rupee and the returns NRIs earn on Indian deposits, and threatening the incomes of relatives still farming back home.",
        "sources": ["Reuters", "The Hindu BusinessLine", "India Meteorological Department", "Dainik Bhaskar"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: The $100,000 H-1B fee is back
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: $100,000 H-1B fee reinstated")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "United States visa H-1B passport",
        ["visa", "passport", "uscis", "immigration"],
        "A US visa; the contested $100,000 H-1B fee is back in force while the courts fight it out")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "John F. Kennedy United States Courthouse Boston",
            ["courthouse", "court", "boston"],
            "The federal courthouse in Boston, where a judge struck down \u2014 then briefly paused his own order on \u2014 the H-1B fee")
    if not image_url:
        image_url = fetch_pexels_image("us passport visa immigration document")
        if image_url and validate_image(image_url):
            image_caption = "A US passport and visa documents; the $100,000 H-1B fee remains in force amid conflicting court rulings"
            image_attribution = "Pexels"
        else:
            image_url = None

    slug = "h1b-100000-fee-reinstated-administrative-stay-first-circuit-indian-tech-workers-20260619"

    body = """For a few heady days this month, Indian tech workers thought they had won. A federal judge in Boston had struck down the Trump administration's $100,000 fee on new H-1B petitions, and social-media feeds filled with relieved celebration. Then, almost as fast, the relief evaporated. As of June 17, the $100,000 fee is back in force \u2014 and the whiplash has left applicants, employers and immigration lawyers scrambling to figure out which rule actually governs the petition on their desk.

The reversal came through a procedural twist. On June 8, U.S. District Judge Leo Sorokin in Massachusetts vacated Presidential Proclamation 10973, ruling that the $100,000 charge \u2014 imposed in September 2025 \u2014 amounted to a tax that only Congress, not the president, has the power to levy. Because it was a summary judgment, the order applied nationwide. But the government appealed to the First Circuit on June 11, and on June 12 Sorokin himself granted a temporary administrative stay, pausing his own ruling while the appeal proceeds. The upshot: USCIS is once again permitted to demand the fee for H-1B petitions filed for, or only approvable through, consular processing.

## A Legal Hall of Mirrors

The Boston case is only one of three. Back on December 23, 2025, Judge Beryl Howell in the District of Columbia reached the opposite conclusion in *Chamber of Commerce v. DHS*, treating the $100,000 charge as a permissible condition on entry rather than a revenue measure \u2014 and the fee remained in effect in that proceeding. A third suit, brought in San Francisco by religious and labour groups, could yet produce a third outcome. With circuits potentially splitting, legal scholars increasingly expect the question to land before the Supreme Court, which could lean on its February 2026 tariff decision in *Learning Resources v. Trump* about the limits of executive revenue power.

Crucially, the administrative stay is conditional: the government had to file its stay motion with the First Circuit by June 18. If it stumbles, Sorokin's June 8 order vacating the fee could snap back into force. "This is a snapshot, not a settled rule," one immigration analyst cautioned, warning applicants to "check the date" on any viral post claiming the fee is dead or alive. The proclamation also expires by its own terms in September 2026, adding a ticking clock to the whole dispute.

## Who Pays, and Who Doesn't

The fee's scope matters enormously. The Department of Homeland Security has clarified that the $100,000 charge does not apply to H-1B change of status, extensions, or change-of-employer petitions \u2014 it bites hardest on new petitions for workers being processed at consulates abroad, overwhelmingly in India. Nearly three-quarters of all H-1B approvals go to Indian nationals, and the consulate in Chennai alone has processed more than 200,000 H-1B visas in a single year. DHS retains discretion to waive the fee in the "national interest," but it remains unclear whether any waiver has been granted.

The fee lands atop an already punishing environment. Consulates in India have been mass-rescheduling H-1B and H-4 interviews into mid-2026 to accommodate a new online-presence vetting regime, and the February 2026 shift from a random lottery to a wage-weighted selection system has tilted the odds toward higher-paid roles.

## Why It Matters to the Diaspora

For the Indian diaspora, this is the single most consequential immigration fight of the year. The H-1B is the principal on-ramp through which Indian engineers, doctors and researchers build lives in the United States, and a $100,000 levy \u2014 if it survives \u2014 would price out all but the largest employers and the highest earners, choking the pipeline that has defined Indian-American migration for three decades. Indian IT majors such as TCS, Infosys and Wipro, among the biggest sponsors of the visa, would feel it acutely.

The on-again, off-again nature of the fee is its own cruelty. Families weighing whether to travel home for stamping, students converting from F-1 to H-1B, and physicians staffing rural American hospitals are all being forced to make irreversible decisions against a legal backdrop that can flip in 72 hours. Until the appeals courts \u2014 or the Supreme Court \u2014 settle the matter, the only safe assumption for diaspora applicants is that the fee is real, in force, and best planned around.

**Sources:** Reuters, Associated Press, LiveLaw, The Indian Eye"""

    article = {
        "headline": "The $100,000 H-1B Fee Is Back. Indian Tech Workers Who Celebrated Its Defeat Have 72 Hours of Whiplash to Show for It.",
        "subheadline": "A Boston judge struck down the fee on June 8, then paused his own order on June 12 \u2014 so as of June 17 the $100,000 charge is again in force, with conflicting rulings in three courts pointing toward the Supreme Court.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Nearly three-quarters of H-1B visas go to Indians, so a reinstated $100,000 fee threatens the principal on-ramp for Indian engineers, doctors and researchers \u2014 and the on-again, off-again legal whiplash forces diaspora families, students and physicians to make irreversible decisions against a rule that can flip in 72 hours.",
        "sources": ["Reuters", "Associated Press", "LiveLaw", "The Indian Eye"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: India-US trade deal nears the finish
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: India-US trade deal nears finish")
    print("=" * 60)

    image_url = fetch_wikipedia_person_image("Piyush Goyal")
    image_caption = "Indian Commerce Minister Piyush Goyal, who says the first tranche of the India-US trade deal could be done by mid-July"
    image_attribution = "Wikimedia Commons"
    if image_url and not validate_image(image_url):
        image_url = None
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "India United States flags trade",
            ["flag", "india", "united states", "trade"],
            "Flags of India and the United States; the two sides are racing to finalise a trade framework")
    if not image_url:
        image_url = fetch_pexels_image("india usa flags trade agreement")
        if image_url and validate_image(image_url):
            image_caption = "Flags of India and the United States as trade negotiators push toward a deal"
            image_attribution = "Pexels"
        else:
            image_url = None

    slug = "india-us-trade-deal-ustr-greer-visit-june-23-24-first-tranche-mid-july-20260619"

    body = """After a year of stop-start negotiation, the India-United States trade deal is finally entering the home stretch. U.S. Trade Representative Jamieson Greer lands in New Delhi on the evening of June 22 for two days of talks on June 23-24, and Indian officials say the agenda is explicit: put the final touches on the interim framework agreement and map the path to the broader bilateral trade agreement (BTA) that has been under discussion for months.

"We expect that discussions will be centred around giving final touches to the framework deal and also on the larger BTA," India's Commerce Secretary Rajesh Agrawal said this week. Commerce Minister Piyush Goyal has gone further, predicting that the first tranche of the agreement could be "executed" by the middle of July. "By sometime in the middle of next month or so, we should be in a position to execute a very vibrant first tranche," Goyal said, adding that both sides were "fast moving towards closing all the open ends."

## A Deal With a Tangled History

The two countries reached an initial understanding in February, but momentum stalled after President Trump's sweeping tariff measures were struck down by the U.S. Supreme Court, and again when Washington floated an additional 12.5 percent tariff on Indian imports over forced-labour concerns. The talks regained pace in New Delhi this month, and at the G7 summit in France, Trump and Modi held their first structured in-person meeting in more than a year. Trump pronounced the deal "very close," called Modi "one of the toughest" negotiators he had faced, and said he intended to visit India.

The first tranche is expected to hand India preferential access ahead of competitors, while the full BTA aims to address the entire sweep of the trade relationship \u2014 including the unresolved Section 301 proceedings. India's negotiating hand has been strengthened by a striking run of export numbers: merchandise exports jumped 18 percent year-on-year in May to $45.2 billion, among the highest monthly totals on record, and the country's overall exports have nearly doubled over twelve years to $863 billion.

## What's Actually on the Table

The contours, sketched in the February joint statement, are ambitious. Both sides have committed to preferential market access in sectors of mutual interest and to establishing rules of origin so the benefits accrue chiefly to India and the United States. New Delhi has agreed to tackle long-standing non-tariff barriers \u2014 on U.S. medical devices, information-and-communication-technology goods, and agricultural products \u2014 while Washington has signalled willingness to lower tariffs on Indian goods as the BTA is negotiated. The deal sits inside the wider India-US COMPACT framework spanning defence, strategic technology and energy.

Sticking points remain. Agriculture and dairy are politically radioactive in India, and the forced-labour tariff threat and the Section 301 file are live irritants. But the political will on both sides \u2014 a president eager for a win and a prime minister keen to lock in preferential access before rivals \u2014 is the strongest it has been since talks began.

## Why It Matters to the Diaspora

For the Indian diaspora, a trade deal is more than an abstraction about tariff schedules \u2014 it is the scaffolding of the economic bridge so many NRIs straddle. Lower duties and smoother market access shape the fortunes of the Indian exporters, IT-services firms and pharmaceutical companies that employ diaspora professionals and anchor cross-border careers. Indian-American business owners who import textiles, jewellery, generic drugs and food products stand to see costs and supply chains shift directly with the fine print Greer and Goyal hammer out this week.

There is a strategic resonance too. A durable India-US trade pact would knit the world's largest and most influential economies closer at exactly the moment the diaspora is ascending in American business, technology and politics. For a community that has long served as the human bridge between the two countries \u2014 and that lobbies hard for warmer ties \u2014 watching the deal cross the finish line would be a validation of the very relationship it embodies.

**Sources:** Reuters, The Hindu BusinessLine, The Indian Eye, Outlook Business"""

    article = {
        "headline": "The India-US Trade Deal Is Entering the Home Stretch. America's Top Trade Negotiator Lands in Delhi Monday.",
        "subheadline": "USTR Jamieson Greer visits India on June 23-24 to finalise the framework agreement, with Commerce Minister Piyush Goyal predicting the first tranche could be executed by mid-July.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "A trade deal reshapes the fortunes of the Indian exporters, IT-services firms and pharma companies that employ diaspora professionals, and directly shifts costs for Indian-American importers of textiles, jewellery and generic drugs \u2014 while knitting the two countries the diaspora bridges ever closer.",
        "sources": ["Reuters", "The Hindu BusinessLine", "The Indian Eye", "Outlook Business"],
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
    results.append(("Weakest monsoon in 11 years", write_article_1()))
    results.append(("$100,000 H-1B fee reinstated", write_article_2()))
    results.append(("India-US trade deal nears finish", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
