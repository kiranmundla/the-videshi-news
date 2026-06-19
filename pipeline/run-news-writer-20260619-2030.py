#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-19 20:30 UTC run (scheduled videshi-writer-news)
3 fresh articles distinct from all 2026-06-18/19 published news topics
(H-1B fee ruling, foreigners registration rules, India-Canada CEPA, RBI NRI
deposit caps, AAPI physician fee, Hormuz reopening, UAE consular operator,
fuel retailer losses, PM-VBRY disbursal, NSE IPO, OCI overhaul, Mumbai water,
defence production, rupee recovery, remittances record, Yoga Day, US student
collapse, anti-Hindu hate, Anil Menon, World Cup players, DHS duration-of-status,
VivaTech, Iran war, UK-India clean energy, Warsh Fed, Modi Paris, EU-India FTA):

  1. Indian IT stocks crash to a 3-year low after Accenture's weak outlook —
     economy/markets (Nifty IT -5.6%, TCS/Infosys/Wipro/HCL down 5-8%)
  2. Reliance files for Jio Platforms IPO — could be India's largest ever
     (~$4bn fresh issue, ~$180bn valuation) — economy/markets
  3. RBI's GIFT City dollar-lending push to pull in diaspora dollars under the
     revived FCNR(B) swap scheme — economy/diaspora-finance
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
# ARTICLE 1: Indian IT stocks crash on Accenture outlook
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: Indian IT stocks crash on Accenture")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Tata Consultancy Services building",
        ["tcs", "tata consultancy"],
        "A Tata Consultancy Services campus; Indian IT majors fell 5-8% after Accenture's weak guidance")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Infosys Bangalore campus",
            ["infosys"],
            "The Infosys campus in Bengaluru; the Nifty IT index sank to a three-year low on June 19")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Bombay Stock Exchange building Mumbai",
            ["bse", "bombay stock exchange"],
            "The Bombay Stock Exchange in Mumbai, where IT stocks dragged benchmarks lower on June 19")

    slug = "indian-it-stocks-crash-accenture-weak-outlook-nifty-it-three-year-low-tcs-infosys-20260619"

    body = """India's information-technology giants suffered one of their worst days in years on Friday, after a grim outlook from Accenture \u2014 the global bellwether for the consulting and outsourcing trade \u2014 sent investors fleeing the sector. The Nifty IT index slumped as much as 5.6 percent to a three-year low, with Tata Consultancy Services, Infosys, HCLTech and Wipro all falling between 5 and 8 percent at various points in the session. All ten constituents of the IT index were in the red.

The trigger came from across the ocean. Accenture, whose quarterly results are treated as a leading indicator for the entire IT services industry, forecast revenue below Wall Street estimates and lowered the top end of its annual growth guidance to 3-4 percent from 3-5 percent. The company cited a roughly $400 million hit to bookings from the now-easing war in West Asia and, more ominously for the long term, clients who remain deeply cautious about discretionary technology spending. Accenture shares plunged about 18 percent overnight in New York \u2014 their steepest single-day fall on record.

## Why Accenture Moves Mumbai

Indian IT firms draw the bulk of their revenue from the same global pipeline of corporate technology projects that Accenture services. When Accenture signals that clients are holding back, analysts read it as a warning for the whole sector. "Because Indian IT firms rely heavily on the same global pipeline for discretionary tech projects, Accenture's forecast is a warning for the entire sector," said Shashwat Singh, a fundamental analyst at Bajaj Broking. Goldman Sachs flagged a "negative read-across" given "continued low visibility on demand outlook," while Morgan Stanley warned that hopes of a meaningful pickup early in the next fiscal year could now be fading.

The sell-off rippled through the broader market. The Nifty 50 fell about 0.6 percent and the BSE Sensex shed roughly 0.8 percent, snapping a five-session winning streak that had been built on falling oil prices after the U.S.-Iran deal and the central bank's moves to steady the rupee. Heavyweights HDFC Bank and Reliance Industries also slipped, the latter as investors booked profits around its plan to list Jio Platforms in Mumbai.

## The Deeper Anxiety: AI

Beneath the Accenture headline sits a more existential worry. India's roughly $315 billion IT services industry was built on a labour-intensive model \u2014 armies of engineers billing hours to maintain and modernise client software. The fear gripping investors is that generative AI tools can automate exactly that work, hollowing out the traditional pool of revenue faster than the firms can pivot.

Accenture's own response has been telling: rather than fight the AI model makers, it has gone on an acquisition spree, announcing $4.2 billion in cybersecurity deals and partnerships with the likes of Palantir and Databricks. To investors, the message reads two ways \u2014 the market is being disrupted faster than expected, and future growth may have to be bought rather than earned organically. "The traditional pool of revenue is evaporating," one industry executive told Mint.

## What's Next

The real test comes in mid-July, when TCS, Infosys, HCLTech and Wipro report their own quarterly numbers and, crucially, their guidance for the year. Analysts will be parsing every word for signs of whether the caution Accenture described is a temporary, war-driven freeze or a structural slowdown. Morgan Stanley, for its part, still believes the sector is positioned for "an eventual recovery," but conceded the timing is "increasingly uncertain."

## Why It Matters to the Diaspora

For the Indian diaspora, the IT sector is not a distant abstraction \u2014 it is, for hundreds of thousands of families, the industry that carried them abroad in the first place. TCS, Infosys, Wipro and HCL are among the largest sponsors of H-1B visas and the biggest employers of Indian-origin technologists in the United States, Britain and Canada. A prolonged demand slowdown, layered on top of a tightening US visa regime and the threat of AI-driven white-collar layoffs, raises uncomfortable questions about the pipeline of jobs that has long underpinned diaspora migration.

There is a financial dimension too. Many NRIs hold Indian IT names directly or through mutual funds and pension allocations back home, and the sector's roughly 15 percent weight in the Nifty makes it a core holding for diaspora portfolios. A three-year low in the IT index is a reminder that the engine room of India's services export economy \u2014 and of so many diaspora careers \u2014 is navigating its most uncertain stretch in a decade.

**Sources:** Reuters, The Hindu BusinessLine, Mint, Barron's"""

    article = {
        "headline": "Indian IT Stocks Just Crashed to a Three-Year Low. One Warning From Accenture Did It.",
        "subheadline": "The Nifty IT index sank as much as 5.6 percent on June 19, with TCS, Infosys, Wipro and HCLTech falling 5-8 percent, after Accenture flagged cautious client spending and an AI-driven shift that threatens the sector's labour-heavy model.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "India's IT majors are the largest sponsors of H-1B visas and the biggest employers of diaspora technologists abroad, so a demand slowdown colliding with a tighter US visa regime and AI layoffs threatens the very job pipeline that carried many NRIs overseas \u2014 even as the sector's heavy weighting in the Nifty hits diaspora portfolios directly.",
        "sources": ["Reuters", "The Hindu BusinessLine", "Mint", "Barron's"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: Reliance files for Jio Platforms IPO
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: Jio Platforms IPO filing")
    print("=" * 60)

    image_url = fetch_wikipedia_person_image("Mukesh Ambani")
    image_caption = "Reliance chairman Mukesh Ambani, who announced the Jio Platforms IPO filing at the AGM"
    image_attribution = "Wikimedia Commons"
    if image_url and not validate_image(image_url):
        image_url = None
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Bombay Stock Exchange building Mumbai",
            ["bse", "bombay stock exchange"],
            "The Bombay Stock Exchange in Mumbai, where Jio Platforms plans to list")

    slug = "reliance-jio-platforms-ipo-drhp-filed-sebi-largest-india-listing-ambani-agm-20260619"

    body = """Mukesh Ambani has finally pulled the trigger on the listing the Indian market has waited years for. At Reliance Industries' 49th annual general meeting on Friday, the chairman announced that the board of Jio Platforms had approved its draft red herring prospectus and would file it with the Securities and Exchange Board of India the same day \u2014 setting the stage for what could become the largest initial public offering in Indian corporate history.

"With great delight, let me tell you that the board of Jio Platforms has approved the draft red herring prospectus earlier today, and it will be filed with SEBI today," Ambani told shareholders, calling the listing "the most important value creation milestone this year." He said his three children \u2014 Akash, Isha and Anant \u2014 would lead the IPO process and the next generation of value creation at the company.

## The Numbers

According to the stock-exchange filing, the IPO comprises a fresh issue of up to 270 million (27 crore) new equity shares with a face value of 10 rupees each; the price will be set later through a book-building process. Reuters, citing sources, reported the company is targeting a raise of around 360 billion rupees, or roughly $3.8 billion \u2014 equivalent to about 2.9 percent of Jio's post-issue equity. The Financial Times put the target closer to $4 billion. At that size, the offering would eclipse Hyundai Motor India's $3.3 billion listing to become the biggest stock-market debut the country has ever seen.

The valuation context is even more striking. Brokerages peg Jio Platforms at around $180 billion, which would make it one of the most valuable companies ever to list in India. Jio Platforms houses Reliance Jio Infocomm \u2014 the world's second-largest telecom operator by subscribers after China Mobile, with roughly 500 million users and about 60 percent of India's data traffic \u2014 alongside the group's cloud, enterprise and artificial-intelligence businesses.

## Why Now

The decision to list arrives at a delicate moment. Reliance's stock is down roughly 17 percent from its 52-week high, and India's primary market has been subdued this year amid valuation concerns and the fallout from the West Asia conflict. The benchmark Sensex has fallen nearly 10 percent in 2026. Yet Ambani is betting that the scale of the Jio story can cut through the gloom. The Economic Times reported that Reliance reworked the deal structure, shifting from an offer-for-sale to a fresh issue after pricing disagreements with existing investors.

Those investors are a who's who of global technology capital. When Jio raised funds in 2020, it sold stakes to Meta, Google and Vista Equity Partners, among others. Reliance still owns more than 66 percent of Jio Platforms, with Meta holding nearly 10 percent and Google around 7.7 percent. The capital from the IPO is earmarked for next-generation network infrastructure, AI and data-centre ventures \u2014 including a recently announced 168 MW data-centre project with Meta in Jamnagar \u2014 and enterprise digital services.

## More Than a Telecom Story

The pitch Ambani made to shareholders was deliberately national in scope. "The proposed listing of Jio will demonstrate to the world that India can build technology companies of global scale, global capability, and global value," he said. The larger question for investors is whether Jio can convincingly evolve from a telecom operator into a digital and AI platform that justifies a premium valuation \u2014 the difference between a utility and a growth stock.

The Jio filing also lands in the same week the National Stock Exchange filed its own draft papers, signalling that India's biggest names are racing to tap public markets even in a cautious climate.

## Why It Matters to the Diaspora

For the global Indian diaspora, the Jio IPO is shaping up to be the most closely watched investment event of the year. Non-resident Indians have long sought direct exposure to India's digital growth story, and a Jio listing offers a rare, large-cap, liquid way to own the infrastructure underpinning 500 million Indian internet users. NRIs are permitted to invest in Indian IPOs through their NRE and NRO accounts under the portfolio investment scheme, and demand from diaspora investors for a marquee name of this scale is likely to be intense.

There is also a symbolic resonance. Jio is the company that put cheap data in the hands of nearly every Indian household, transforming how families back home bank, shop and stay in touch with relatives abroad. For a diaspora that wires home a record amount each year and watches India's rise from a distance, owning a slice of Jio is a way of buying into the country's digital future \u2014 and the firm's listing will be a real-time referendum on whether the world still believes in that future.

**Sources:** Reuters, The Hindu BusinessLine, The Wall Street Journal, Outlook Business"""

    article = {
        "headline": "Reliance Just Filed for the Jio IPO. It Could Be the Biggest Stock Debut in India's History.",
        "subheadline": "At the Reliance AGM on June 19, Mukesh Ambani said Jio Platforms' draft prospectus was filed with SEBI \u2014 a fresh issue of up to 27 crore shares targeting roughly $4 billion, on a business brokerages value near $180 billion.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "The Jio IPO offers NRIs a rare large-cap, liquid way to own the infrastructure behind 500 million Indian internet users \u2014 investable through NRE/NRO portfolio accounts \u2014 and stands as a real-time referendum on whether the diaspora and the world still believe in India's digital growth story.",
        "sources": ["Reuters", "The Hindu BusinessLine", "The Wall Street Journal", "Outlook Business"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: GIFT City dollar-lending push for diaspora dollars
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: GIFT City dollar-lending diaspora push")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Gujarat International Finance Tec-City",
        ["gift", "gujarat international finance", "gift one"],
        "Gujarat International Finance Tec-City (GIFT City), India's offshore financial hub")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Reserve Bank of India building Mumbai",
            ["reserve bank", "rbi", "mint road"],
            "The Reserve Bank of India, which revived an FCNR swap scheme to draw diaspora dollars")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Indian rupee US dollar currency",
            ["dollar", "rupee", "currency", "banknote"],
            "US dollars and Indian rupees; the RBI is courting diaspora deposits to stabilise the currency")

    slug = "gift-city-banks-dollar-lending-fcnr-swap-scheme-diaspora-dollars-rbi-rupee-20260619"

    body = """India's banks are pressing the central bank for permission to lend dollars through their GIFT City units, in a bid to supercharge a freshly revived scheme designed to pull billions of diaspora dollars into the country and shore up the rupee. The request, reported by Reuters on Friday, is the latest move in a coordinated campaign to harness the financial firepower of overseas Indians at a moment of strain for the currency.

Earlier this month, the Reserve Bank of India offered to subsidise the hedging costs banks incur on Foreign Currency Non-Resident, or FCNR(B), deposits \u2014 a mechanism last deployed in 2013 to defend the rupee during a balance-of-payments scare. The scheme typically works through leverage: banks offer loans to depositors, who then park the borrowed money in dollar deposits with Indian lenders, magnifying the inflow of foreign currency. Now the banks want to route that lending through their branches in Gujarat International Finance Tec-City.

## What the Banks Are Asking For

GIFT City, India's tax-neutral offshore financial hub near Gandhinagar, operates under offshore banking rules that the banks argue make their units there function much like foreign banks. On that logic, they contend, GIFT City branches should be allowed to extend the loans that power the deposit scheme. "Most banks have branches in GIFT City, but many of them do not have a presence in foreign countries. If the leverage is not allowed through GIFT, these banks will have to depend on foreign lenders," said VRC Reddy, treasury head at Karur Vysya Bank.

The technical sticking point is whether existing RBI rules \u2014 which allow customers to take leverage and permit Indian lenders to issue standby letters of credit guaranteeing repayment to overseas banks \u2014 also apply to the overseas branches of Indian banks, including those in GIFT City. The RBI did not respond to Reuters' queries.

## The Prize: $55 Billion

The numbers under discussion are large enough to move India's external accounts. Brokerage Nomura estimates the scheme could attract as much as $55 billion, with the bulk expected to arrive in August and September. "Compared to 2013, while U.S. dollar rates are much higher, the scheme will also provide leverage to investors, which will boost returns," Nomura noted. In other words, the higher global interest-rate environment that has squeezed so many emerging markets could, in this case, make parking dollars in India more attractive to the diaspora than it was a decade ago.

That matters because India's capital account has been under pressure. Net foreign direct investment has dwindled to single digits, and foreign portfolio investors pulled around $16.5 billion out of Indian equities last fiscal year. Against that backdrop, the steady, sticky flow of diaspora money has become a crucial stabiliser.

## A Currency on the Mend

The push comes as the rupee claws back from recent lows. After sliding toward record-weak territory during the West Asia conflict, the currency has firmed to around 94 to the dollar on the back of falling oil prices following the U.S.-Iran deal and the RBI's interventions. The deposit scheme is the supply-side complement to that effort: rather than burning through its roughly $691 billion in foreign-exchange reserves to defend the rupee, the central bank is trying to engineer fresh dollar inflows from a more reliable source \u2014 Indians abroad.

It is part of a broader RBI charm offensive aimed squarely at the diaspora. The central bank recently lifted interest-rate caps on NRI deposits, prompting banks to raise rates toward 7 percent, and it is now wiring together the plumbing \u2014 GIFT City lending, hedging subsidies, standby credit \u2014 to make those deposits flow at scale.

## Why It Matters to the Diaspora

For non-resident Indians, this is a rare moment when New Delhi is actively competing for their savings. FCNR(B) deposits let NRIs hold money in foreign currency, eliminating exchange-rate risk on the principal, while earning interest that is now climbing as banks chase dollars. If the GIFT City leverage mechanism is approved, diaspora depositors could see still more attractive structured products marketed to them in the coming months.

The deeper significance is strategic. India's record $135-billion-plus in annual remittances already cushions nearly half the trade deficit; layering a $55 billion deposit surge on top would hand the diaspora an outsized role in defending the rupee itself. For Indians abroad, the message from Mumbai is unusually direct: your dollars are not just welcome \u2014 they are being courted as a pillar of the country's financial stability.

**Sources:** Reuters, Mint, Nomura research note"""

    article = {
        "headline": "India's Banks Want to Lend Dollars Out of GIFT City. The Target: $55 Billion in Diaspora Money.",
        "subheadline": "Lenders are asking the RBI to route loans through their offshore GIFT City units to amplify a revived FCNR deposit scheme \u2014 a 2013-style bid to pull in diaspora dollars and steady a rupee just recovering toward 94.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "New Delhi is openly competing for NRI savings: rising FCNR deposit rates, hedging subsidies and a proposed GIFT City lending mechanism could channel up to $55 billion in diaspora dollars into India, handing overseas Indians an outsized role in defending the rupee and earning more attractive, currency-risk-free returns.",
        "sources": ["Reuters", "Mint", "Nomura research note"],
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
    results.append(("Indian IT stocks crash on Accenture", write_article_1()))
    results.append(("Jio Platforms IPO filing", write_article_2()))
    results.append(("GIFT City diaspora dollar push", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
