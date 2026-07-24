#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-15 PM4 batch (scheduled videshi-writer-news, 16:30 UTC run)
3 fresh articles, distinct from all earlier 2026-06-15 batches:
  1. EB-2 India green card category hits FY2026 cap — issuance frozen (immigration)
  2. FPIs pull ₹62,853 cr in 15 days; Wall Street bets on India rebound as AI trade cools (markets)
  3. India's balance of payments goes monthly; April deficit but remittances jump to $16bn (economy/remittances)
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
# ARTICLE 1: EB-2 India green card cap exhausted
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: EB-2 India green card cap exhausted")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "United States Citizenship and Immigration Services building",
        ["uscis", "immigration", "citizenship", "federal", "building", "department"],
        "A U.S. immigration services office; the EB-2 India green card category has hit its annual cap")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "US Department of State Washington building",
            ["state", "department", "washington", "building", "harry truman", "federal"],
            "The U.S. State Department in Washington, which manages immigrant visa issuance abroad")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "United States passport visa green card",
            ["passport", "visa", "green card", "permanent resident", "immigration", "document"],
            "A U.S. permanent resident card; EB-2 visas for India are frozen until the fiscal year resets")
    if not image_url:
        px = fetch_pexels_image("united states flag government building")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "A U.S. government building", "Pexels"

    slug = "eb2-india-green-card-category-hits-fy2026-cap-issuance-frozen-20260615"

    body = """For tens of thousands of Indian professionals who did everything right \u2014 advanced degrees, approved petitions, years in the queue \u2014 the door to a U.S. green card just quietly closed for the rest of the year. The EB-2 employment-based category for India has hit its annual limit for fiscal year 2026, and the government will issue no more EB-2 immigrant visas to Indian nationals until the new cycle begins on October 1.

This is not a policy change, a new rule, or a sudden tightening. It is the U.S. immigration system working exactly as Congress designed it \u2014 and that, for the Indian diaspora, is precisely the problem.

## What Just Happened

According to coordination between the U.S. Department of State and U.S. Citizenship and Immigration Services (USCIS), all available EB-2 visa numbers allocated to India for FY 2026 have been used up. EB-2 is the category reserved for professionals holding advanced degrees or those with exceptional ability \u2014 the bread-and-butter route for Indian engineers, doctors, scientists and senior technology workers seeking permanent residence.

When a category hits its cap, consulates and embassies are instructed to stop issuing visas in it. Approved applicants do not lose their place; their petitions stay valid and their priority dates intact. But the practical effect is stark: even a fully approved applicant cannot receive a visa until fresh numbers become available when the fiscal year resets on October 1.

## Why India Runs Out First

The exhaustion is a direct consequence of two structural features of U.S. law working against each other. The Immigration and Nationality Act caps the total number of employment-based green cards issued each year, and a separate per-country rule prevents any single nation from claiming more than roughly 7 percent of the total in any category.

For most countries, that ceiling is never a constraint. For India \u2014 which sends more skilled workers to the United States than almost any other nation \u2014 demand dwarfs the per-country allotment by orders of magnitude. The result is a backlog measured not in months but in years, sometimes decades, and annual quotas that exhaust well before the fiscal year ends.

The mechanics play out through the State Department's monthly Visa Bulletin, the single most-watched document in the Indian immigrant community. When EB-2 India reaches its limit, the bulletin reflects it by freezing or restricting final action dates \u2014 the signal to consulates worldwide to halt issuance.

## A Pattern, Not an Accident

The EB-2 freeze lands in the same week that the EB-5 investor category for India also ran dry, and amid a broader squeeze on Indian access to U.S. immigration channels \u2014 from H-1B turbulence to a steeper visa fee regime. For diaspora families, the cumulative message is hard to miss: nearly every legal pathway to the United States is simultaneously narrowing, backing up, or getting more expensive.

What makes the EB-2 cap especially painful is who it hits. These are not speculative applicants. They are professionals already living and working legally in the United States, often for a decade or more, whose green card cases are approved and merely waiting for a visa number. Each year the cap is reached, their lives \u2014 job changes, home purchases, their children's status \u2014 stay frozen alongside it.

## What Happens Next

Nothing about the underlying cases changes. USCIS records remain active, priority dates hold, and applicants stay queued. When the new fiscal year opens on October 1, fresh EB-2 allocations re-enter circulation, issuance to India resumes, and the Visa Bulletin publishes updated charts showing how far the queue can move.

But the reset only restarts the same machine. With demand from India continuing to exceed supply by a wide margin, immigration attorneys expect the FY 2027 numbers to begin draining almost as soon as they appear. Absent congressional action to lift per-country caps or expand the employment-based quota \u2014 reforms debated for years without resolution \u2014 the annual cycle of exhaustion and reset will keep repeating.

## Why It Matters to the Diaspora

For the Indian diaspora, the EB-2 freeze is a concrete reminder that the U.S. green card backlog is not an abstraction \u2014 it is a structural ceiling that turns approved cases into open-ended waits. A skilled worker weighing whether to stay in the United States, accept a promotion that requires a new petition, or relocate a family now has to factor in a system that can stop issuing visas mid-year with no recourse.

It also sharpens a calculation many in the diaspora are already making: whether to keep waiting in a queue that may not move for years, or to look at countries \u2014 Canada, the UK, Australia, the Gulf \u2014 actively courting the same Indian talent with faster, more predictable routes to residence. Every year the EB-2 cap is reached, that question gets a little louder.

**Sources:** U.S. Department of State Visa Bulletin, U.S. Citizenship and Immigration Services (USCIS), Travel And Tour World reporting"""

    article = {
        "headline": "America Has Run Out of EB-2 Green Cards for India. Approved Applicants Now Wait Until October.",
        "subheadline": "The employment-based category that most skilled Indian professionals rely on has hit its FY2026 cap \u2014 freezing issuance until the new fiscal year, even for fully approved cases.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "EB-2 is the primary green card route for skilled Indian professionals \u2014 engineers, doctors, scientists \u2014 already living and working in the U.S.; the FY2026 cap freezes their approved cases until October and sharpens the diaspora's calculation of whether to keep waiting or pursue faster residence routes in Canada, the UK or Australia.",
        "sources": ["U.S. Department of State Visa Bulletin", "U.S. Citizenship and Immigration Services (USCIS)", "Travel And Tour World"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: FPI exodus + Wall Street India rebound bet
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: FPI exodus + Wall Street India rebound bet")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Bombay Stock Exchange building Mumbai",
        ["bombay stock exchange", "bse", "mumbai", "dalal", "phiroze", "tower"],
        "The Bombay Stock Exchange in Mumbai, where foreign investors have pulled out a record sum in 2026")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "National Stock Exchange India Mumbai building",
            ["national stock exchange", "nse", "mumbai", "bandra", "exchange", "building"],
            "India's stock exchange in Mumbai; FPIs have withdrawn a record amount from equities this year")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Mumbai financial district skyline",
            ["mumbai", "skyline", "financial", "bandra", "kurla", "tower", "building"],
            "Mumbai's financial district, the centre of India's equity markets")
    if not image_url:
        px = fetch_pexels_image("stock exchange trading screen financial market")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "A stock market trading display", "Pexels"

    slug = "fpi-record-outflow-india-equities-wall-street-rebound-bet-ai-trade-cools-20260615"

    body = """Foreign investors have spent 2026 fleeing Indian stocks at a pace never seen before. Foreign portfolio investors (FPIs) pulled \u20b962,853 crore out of Indian equities in just the first fifteen days of June, pushing total outflows for the year to an unprecedented \u20b92.87 lakh crore \u2014 already far above the \u20b91.66 lakh crore that left across all of 2025. Yet some of Wall Street's biggest names are quietly betting that the worst is over, and that India is now one of the most mispriced opportunities in the emerging-market universe.

For the diaspora investors who track Indian markets as a piece of home \u2014 and often a piece of their portfolio \u2014 the gap between the panic in the data and the optimism among strategists has rarely been wider.

## The Exodus, in Numbers

The selling has been relentless and broad-based. The Nifty 50 and Sensex are down roughly 11 percent and 13 percent for the year, dragged lower by a brutal slide in the heavyweight IT index and a crude-price spike triggered by the Iran war. The rupee has weakened nearly 6 percent in 2026 and around 10 percent over the past year, sliding from the mid-80s to about 95 against the dollar despite repeated intervention by the Reserve Bank of India.

Analysts point to a familiar cocktail: geopolitical friction, worries about global growth, a persistently weak currency, and Indian valuations that still look rich next to cheaper emerging-market peers. Where global money has gone instead is telling \u2014 into South Korea and Taiwan, both dominated by the semiconductor and memory names riding the artificial-intelligence boom. At one point this year, both markets overtook India by market capitalisation.

## The Contrarian Case

It is precisely India's absence from the AI trade that a growing chorus of investors now sees as its hidden strength. Major Wall Street firms \u2014 Morgan Stanley, Citigroup and Goldman Sachs among them \u2014 have flagged a strong potential recovery for Indian equities, arguing that a rotation out of overhyped AI stocks could funnel foreign capital back into laggards like India.

"We have plenty of picks and shovels," said Abhay Laijawala, chief investment officer for India at Lighthouse Canton, describing the country's "advantage of absence." India has little exposure to chip fabrication, he argued, but offers a deep, listed universe tied to the next phase of AI spending \u2014 power, data centres, electrical equipment, cooling systems, engineering and capital goods. When sector concentration in markets like Korea and Taiwan reaches extremes, he warned, investors tend to underprice the risk that trouble could come from outside the core business model.

BlackRock has echoed the view, saying India's market has been "over-punished" for lacking a direct AI play. The fundamentals offer some support: GDP grew 8.2 percent in the September quarter, and India's top 100 firms posted 12 percent profit growth, halting a run of earnings downgrades.

## The Policy Backstop

New Delhi is not waiting passively for foreign money to return. The RBI has rolled out a battery of measures to draw dollars and steady the rupee \u2014 absorbing hedging costs on foreign-currency deposits raised from non-resident Indians, widening the forex swap window, expanding foreign access to government bonds through the Fully Accessible Route, and raising investment limits for NRIs and overseas citizens in domestic equities.

Those measures are already showing up in the data. Even as FPIs dumped equities, they poured more than \u20b913,200 crore into Indian debt through the FAR route in the first fortnight of June. And the sharp drop in crude prices after the U.S.-Iran peace framework \u2014 Brent fell below $84 a barrel \u2014 is a significant tailwind for the world's third-largest oil importer, easing pressure on inflation, the rupee and the trade deficit all at once.

## The Honest Uncertainty

Not everyone is convinced the turn is imminent. India remains a harder call than North Asia: the rupee is still weak, earnings growth has disappointed, and unlike Korea or Taiwan, India has no single AI-driven catalyst to magnetise foreign capital back overnight. The pace of selling did moderate in the latter half of last week \u2014 FPIs sold just \u20b91,082 crore on one session \u2014 but a few quiet days do not make a trend.

## Why It Matters to the Diaspora

For NRIs, the divergence is more than a spectator sport. Many hold Indian equities and mutual funds, and the RBI's new deposit and bond incentives are aimed squarely at diaspora dollars. The contrarian thesis \u2014 that India has been oversold precisely because it sat out the AI frenzy \u2014 frames a decision facing diaspora investors right now: whether to treat the record outflows as a warning to stay away, or as the kind of capitulation that has historically marked a bottom.

The honest answer, as strategists frame it, is that India offers a different bet than the crowded AI trade \u2014 cheaper, broader, and tied to the unglamorous infrastructure that any AI build-out ultimately runs on. Whether foreign money agrees, and when, will determine if 2026's exodus was the prelude to a rebound or just the middle of a longer drought.

**Sources:** NSDL data via Dainik Jagran, Reuters (Lighthouse Canton interview), The Hindu BusinessLine"""

    article = {
        "headline": "Foreign Investors Pulled a Record \u20b92.87 Lakh Crore From Indian Stocks. Wall Street Is Quietly Betting They Will Come Back.",
        "subheadline": "FPIs yanked \u20b962,853 crore from equities in just 15 days of June \u2014 but Morgan Stanley, Goldman and others argue India's absence from the AI frenzy has left it oversold and primed for a rebound.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Many NRIs hold Indian equities and mutual funds, and the RBI's new deposit and bond incentives target diaspora dollars directly \u2014 so the record FPI exodus versus Wall Street's contrarian rebound thesis frames a real decision for diaspora investors: treat the outflows as a warning, or as a capitulation bottom.",
        "sources": ["NSDL data (via Dainik Jagran)", "Reuters", "The Hindu BusinessLine"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: India BoP goes monthly; remittances surge to $16bn
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: India BoP monthly + remittances surge")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Reserve Bank of India building Mumbai",
        ["reserve bank", "rbi", "mumbai", "central bank", "building"],
        "The Reserve Bank of India in Mumbai, which began publishing monthly balance of payments data")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Reserve Bank of India headquarters",
            ["reserve bank", "rbi", "headquarters", "india", "bank", "building"],
            "The Reserve Bank of India headquarters; April data showed remittances jumping sharply")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Indian rupee currency notes money",
            ["rupee", "currency", "india", "note", "money", "bank"],
            "Indian rupee notes; remittances from overseas workers jumped to $16 billion in April")
    if not image_url:
        px = fetch_pexels_image("indian rupee currency money finance")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "Indian currency notes", "Pexels"

    slug = "india-balance-of-payments-monthly-april-deficit-remittances-surge-16-billion-20260615"

    body = """In a quiet but consequential shift, the Reserve Bank of India has started publishing the country's balance of payments every month rather than every quarter \u2014 and the first monthly snapshot, released on Monday, tells a story the diaspora sits at the very centre of. India's overall balance of payments fell into a $6.6 billion deficit in April, dragged down by foreign investors pulling money out. But the very same data showed remittances from Indians working abroad surging to $16 billion, up sharply from $9.4 billion a year earlier.

In other words: as global capital fled, the diaspora's money flowed in \u2014 and increasingly, it is that money holding the line.

## What the New Data Shows

The April figures, the first under the RBI's new monthly reporting regime, capture an economy pulled in two directions. The overall balance of payments recorded a $6.6 billion deficit, compared with a $500 million surplus a year ago. The culprit was the capital account, which swung to an $11.3 billion outflow as foreign portfolio investors dumped Indian assets \u2014 a reversal from a $5.3 billion inflow in April 2025.

Yet beneath that headline, the current account actually swung into a $4.7 billion surplus, up from a $4.8 billion deficit a year earlier. The single biggest reason: net transfers, which are dominated by remittances from Indian workers overseas, jumped to $16 billion from $9.4 billion. Net foreign direct investment also strengthened, rising to $7.4 billion from $1.6 billion.

The RBI also confirmed it will now publish balance of payments data monthly, with a lag of 45 days or less \u2014 a transparency upgrade that lets markets, economists and policymakers track external flows in near-real time rather than waiting for a quarterly reveal.

## Why Remittances Are the Quiet Stabiliser

India has long been the world's largest recipient of remittances, and the April data underscores why that matters now more than ever. As foreign portfolio money proves fickle \u2014 fleeing at the first sign of geopolitical or currency stress \u2014 the steady stream of dollars from the diaspora has become a structural ballast for India's external accounts.

This is money that behaves differently from hot foreign capital. Remittances do not chase yields or panic over a weak rupee; if anything, a depreciating rupee makes each diaspora dollar translate into more rupees back home, encouraging higher transfers. That counter-cyclical quality is exactly what an economy facing record portfolio outflows needs.

The timing is notable. The surge comes against the backdrop of the Gulf conflict that has disrupted the lives of India's roughly 9-million-strong workforce in West Asia \u2014 and yet remittances rose, not fell, suggesting the diaspora's financial commitment to home has held even through regional turmoil.

## The Bigger Picture

India's balance of payments had been expected to deteriorate this financial year as the Iran war drove up crude prices and inflated the country's energy import bill. Last week, the RBI reported a surprise surplus in both the current account and overall balance of payments for the January-March quarter, helped by strong services earnings, rising remittances and central-bank forex swaps.

Now, with the RBI's aggressive push to draw dollars from non-resident Indians through subsidised deposit schemes \u2014 a programme economists estimate could pull in $35 billion to $70 billion \u2014 some now expect the balance of payments to swing back to surplus in the 2026-27 fiscal year. If that happens, it will be diaspora dollars, as much as any policy lever, that engineered the turnaround.

## Why It Matters to the Diaspora

For NRIs, the April data is a mirror held up to their own collective impact. Every wire transfer to a parent, every dollar deposit chasing the RBI's new higher rates, every remittance to a family back home adds up to a force now visibly steadying the world's fifth-largest economy. The $16 billion figure is not an abstraction \u2014 it is the aggregate of millions of individual decisions by overseas Indians to keep sending money home.

It also reframes the relationship between the diaspora and the Indian state. As New Delhi courts NRI capital with deposit incentives, expanded investment limits and a steady drumbeat of outreach, the April numbers make the underlying logic plain: when global investors lose their nerve, India's most reliable source of foreign exchange is its own people abroad. The monthly data will now make that dependence \u2014 and that contribution \u2014 visible in real time.

**Sources:** Reserve Bank of India balance of payments data, Reuters"""

    article = {
        "headline": "India's Money Is Now Tracked Monthly. The First Snapshot Shows Diaspora Remittances Surging as Foreign Investors Flee.",
        "subheadline": "The RBI's new monthly balance of payments data revealed an April deficit driven by capital outflows \u2014 even as remittances from overseas Indians jumped to $16 billion, up from $9.4 billion a year ago.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "The April data makes the diaspora's collective financial weight visible: as foreign portfolio investors pulled out $11.3 billion, remittances from overseas Indians surged to $16 billion \u2014 a counter-cyclical, rupee-stabilising flow that is increasingly the ballast holding up India's external accounts.",
        "sources": ["Reserve Bank of India", "Reuters"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# MAIN
# ========================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"VIDESHI NEWS WRITER (PM4) \u2014 {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    results = []
    results.append(("EB-2 India green card cap", write_article_1()))
    results.append(("FPI exodus + India rebound bet", write_article_2()))
    results.append(("BoP monthly + remittances surge", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
