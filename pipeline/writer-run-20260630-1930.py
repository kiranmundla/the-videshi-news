#!/usr/bin/env python3
"""
Videshi News Writer – June 30, 2026 Evening Run
Two articles:
  1. Global funds returning to Indian stocks / India reclaims #5 global market cap
  2. India's Russian oil imports hit record in June
"""

import json, os, subprocess, sys, time, urllib.parse, uuid, re
from datetime import datetime, timezone

# ---------- env ----------
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            os.environ[k.strip()] = v

load_env("~/.env.supabase")
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = "TheVideshi/1.0 (thevideshi.com)"

# ---------- helpers ----------
def curl_json(url, headers=None, method="GET"):
    cmd = ["curl", "-sS", "-X", method, url]
    for k, v in (headers or {}).items():
        cmd += ["-H", f"{k}: {v}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout) if r.stdout.strip() else {}

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    try:
        cmd = ["curl", "-sS", "-A", UA, url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout)
        img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
        if img:
            print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
            return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(query, limit=5):
    params = urllib.parse.urlencode({
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    })
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    try:
        cmd = ["curl", "-sS", "-A", UA, url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout)
        results = []
        pages = data.get("query", {}).get("pages", {})
        for pid, page in sorted(pages.items(), key=lambda x: x[1].get("index", 999)):
            info = page.get("imageinfo", [{}])[0]
            iurl = info.get("thumburl") or info.get("url")
            w = info.get("width", 0)
            h = info.get("height", 0)
            title = page.get("title", "")
            if iurl and w >= 400 and not any(bad in iurl.lower() for bad in ["flag", ".svg"]):
                results.append({"url": iurl, "title": title, "width": w, "height": h})
        return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
    return []

def commons_relevance_ok(file_title, headline, topic):
    """Gate: make sure Commons file title is actually relevant to our article."""
    STOP = {"the","a","an","is","in","on","at","to","for","of","and","or","with","by",
            "from","its","it","as","that","this","was","are","be","has","have","had",
            "will","been","not","but","they","their","all","one","two","three","new",
            "into","over","more","most","also","than","very","just","after","before",
            "about","up","out","no","so","how","what","when","where","who","which",
            "us","we","our","he","she","him","her","his","them","me","my","you","your",
            "do","did","does","can","could","would","should","may","might","shall",
            "an","each","every","some","any","few","many","much","such","own","other",
            "india","indian","global","world","market","stock","oil","gas","trade",
            "year","years","month","day","people","country","government","new","first",
            "big","last","time","since","billion","million","percent","high","low",
            "record","data","report","shows","says","said","back","still","now","here",
            "social","media","news","photo","image","file","image","picture"}
    text_words = set(re.findall(r'[a-z]{4,}', (headline + " " + topic).lower()))
    keywords = text_words - STOP
    title_lower = file_title.lower()
    hits = sum(1 for kw in keywords if kw in title_lower)
    return hits >= 1

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5"
    cmd = ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout)
        photos = data.get("photos", [])
        if photos:
            return photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("original")
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def verify_image_url(url):
    """Verify image URL returns 200 with image content type and reasonable size."""
    try:
        cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}|%{content_type}|%{size_download}", "-A", UA, "-L", url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        parts = r.stdout.strip().split("|")
        code = parts[0]
        ctype = parts[1] if len(parts) > 1 else ""
        size = float(parts[2]) if len(parts) > 2 else 0
        if code == "200" and "image" in ctype and size > 5000:
            print(f"  ✓ Image verified: {code}, {ctype}, {size:.0f} bytes")
            return True
        print(f"  ✗ Image failed: code={code}, type={ctype}, size={size}")
    except Exception as e:
        print(f"  ✗ Image verify error: {e}")
    return False

def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    payload = json.dumps(article)
    cmd = [
        "curl", "-sS", "-X", "POST", url,
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", payload,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    print(f"  Insert response: {r.stdout[:300]}")
    if r.returncode != 0:
        print(f"  Insert stderr: {r.stderr[:300]}")
    return r.stdout


# ========================================================================
# ARTICLE 1: Wall Street Returns to India / India Reclaims #5 Global Market Cap
# ========================================================================
def write_article_1():
    print("\n=== ARTICLE 1: Global Funds Return to India ===\n")

    headline = "Wall Street Is Buying India Again. The Market Just Overtook Taiwan and South Korea."
    subheadline = "After pulling $27 billion from Indian stocks this year, global fund managers are reversing course as oil collapses and the rupee recovers — pushing India's market cap back above $5 trillion and past two AI-boom darlings."
    slug = "global-funds-return-india-market-cap-5-trillion-overtakes-taiwan-south-korea-20260630"
    category = "news"
    vertical = "markets"
    diaspora_angle = "NRI investors who stayed in India through the selloff are seeing portfolios recover, and the rupee's rebound means dollar-denominated returns are finally turning positive again."

    # Image sourcing
    print("Sourcing hero image...")
    # Try Wikimedia Commons for Indian stock market / Bombay Stock Exchange
    commons = fetch_wikimedia_commons_images("Bombay Stock Exchange building Mumbai")
    image_url = None
    image_caption = None
    image_attribution = None

    for c in commons:
        if commons_relevance_ok(c["title"], headline, "stock market exchange India"):
            if verify_image_url(c["url"]):
                image_url = c["url"]
                image_caption = "The Bombay Stock Exchange in Mumbai, India's oldest stock exchange"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        # Try another Commons query
        commons2 = fetch_wikimedia_commons_images("National Stock Exchange India trading")
        for c in commons2:
            if verify_image_url(c["url"]):
                image_url = c["url"]
                image_caption = "India's stock market has reclaimed the $5 trillion valuation milestone"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        # Pexels fallback — generic stock market
        pxl = fetch_pexels_image("stock market trading screen India")
        if pxl and verify_image_url(pxl):
            image_url = pxl
            image_caption = "Global fund managers are reassessing their retreat from Indian equities"
            image_attribution = "Pexels"

    if not image_url:
        print("  ⚠ No suitable hero image found! Will use placeholder text.")
        return None

    body = """For the first time in over a month, money is flowing back into Indian stocks from Wall Street. And the numbers tell a story of a market that has quietly clawed its way out of one of its worst foreign-investor routs in years.

India's total equity market capitalisation has climbed back above $5 trillion, lifting the country to fifth in global rankings — overtaking both Taiwan and South Korea, the two markets that rode the AI semiconductor boom to dizzying heights earlier this year. India's market cap now stands at $5.05 trillion, compared with Taiwan's $4.97 trillion and South Korea's $4.66 trillion.

The reversal is striking. Foreign portfolio investors had pulled nearly $27 billion from Indian equities in 2026 — the largest annual outflow on record — as stretched valuations, a record-low rupee, and the oil shock triggered by the Iran conflict sent global capital fleeing. Average allocations to India among emerging market funds had dropped below 10% in April, down from a peak of 17.5% in August 2024, according to data from Copley Fund Research.

## Two Headwinds Lifted at Once

"Two key headwinds have eased," said Todd McClone, a portfolio manager at William Blair Investment Management, which oversees about $65 billion. "India is among the most oversold markets we track. This macro improvement, alongside a more attractive valuation premium, strengthens the case to act."

The first headwind was oil. Brent crude has collapsed 42% from its April peak of $126 a barrel to about $73 — falling below pre-Iran conflict levels. For India, which imports nearly 90% of its crude, this is transformative. The drop eases pressure on the current account deficit, softens the inflation outlook, and gives the Reserve Bank of India room to manoeuvre.

The second was the rupee. After hitting a record low near 97 per dollar in May, the currency has recovered to about 94.50, making it one of the best-performing Asian currencies in June. The RBI's measures to encourage dollar inflows — extending subsidised forex swap facilities for banks and broadening the pool of sovereign bonds eligible for foreign investment — have helped stabilise the currency.

## Fund Managers Are Moving

Analysis by Elara Capital shows that inflows into U.S.-listed India-focused exchange-traded funds turned positive last week for the first time in over a month. Global fund managers are starting to rotate back.

"We have gradually reduced our India underweight in the pan-Asia strategies," said Vikas Pershad, a portfolio manager at M&G, which manages roughly $450 billion. The capital was freed up by scaling back positions in South Korea and Taiwan — the two markets that had absorbed the lion's share of global tech-fuelled investment in early 2026.

Christina Woon, head of equity income at Eastspring Investments, which oversees $270 billion, said she is "incrementally more positive" on India. "Valuation opportunities have opened up over the past few months, so on a selective basis, we would be keen to engage."

## The Overtaking

During June, India's market capitalisation rose 2.75%, while South Korea and Taiwan recorded declines of 4.7% and 2.3%, respectively. The global AI enthusiasm that had powered the two East Asian markets into the $5 trillion club began cooling as investors booked profits and concerns mounted over stretched semiconductor valuations.

The Sensex and Nifty gained 3.8% and 2.8% in dollar terms for June. Banking stocks led the charge, with the Nifty Bank index surging 6.1% on the month. Foreign investors purchased nearly $1 billion in Indian equities during June — a dramatic contrast to the sustained selling of earlier months.

## The Earnings Bar

Still, not everyone is convinced the rally has legs. Several fund managers caution that improved macro conditions alone will not sustain a rerating.

"Improved currency stability and lower oil prices alone are unlikely to change investors' views on Indian equities in the near term, though they may provide a more supportive macro backdrop," said Peeyush Mittal, a portfolio manager at Matthews Asia.

India's earnings growth has been limited to single digits in the past two fiscal years. Analysts predict that will accelerate to mid-teens in the current and next fiscal year — but the proof will be in the quarterly results.

"India is not a low-growth or broken story, but it is a market where valuations remain relatively full," said Ninghui Liu, head of APAC investment strategy at State Street Investment Management, which manages $5.6 trillion. "So the bar for increasing allocation is quite clear: we need to see sustained earnings recovery coming through."

## What It Means for NRI Investors

For the millions of Indians abroad who hold Indian equities or mutual funds, the shift matters on two fronts. First, the rupee's recovery from its May lows means dollar-denominated returns have stopped haemorrhaging. Second, the $3 billion record inflow into Indian government bonds in June — fuelled by tax breaks New Delhi announced this month — signals that global institutional money is finding India attractive across asset classes, not just equities.

Goldman Sachs has raised its 2026 growth forecast for India by 30 basis points and now expects a balance-of-payments surplus of 0.7% of GDP. For NRIs considering fresh allocations, the macro backdrop is the most favourable it has been since before the Iran crisis erupted in April.

But the monsoon deficit — June rainfall is running 42% below normal — remains a domestic risk that could weigh on rural demand and food inflation in the coming months. The second half of 2026 begins tomorrow with more questions than answers, but for the first time in a while, Wall Street's questions about India are about how much to buy, not whether to stay.

*Sources: Reuters, Outlook Business, Copley Fund Research, Elara Capital, Goldman Sachs*"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": category,
        "vertical": vertical,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": diaspora_angle,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com"},
            {"name": "Copley Fund Research", "url": "https://copleyresearch.com"},
            {"name": "Elara Capital", "url": "https://elaracapital.com"},
        ]),
    }

    print(f"\nInserting article: {headline}")
    result = insert_article(article)
    return result


# ========================================================================
# ARTICLE 2: India's Russian Oil Imports Hit Record in June
# ========================================================================
def write_article_2():
    print("\n=== ARTICLE 2: India's Russian Oil Imports Hit Record ===\n")

    headline = "Russia Now Supplies More Than Half of India's Oil. June Was the Biggest Month Yet."
    subheadline = "Indian refiners imported a record 2.7 million barrels a day of Russian crude in June — more than double the level from a year ago — as the Hormuz crisis forced them to find alternatives to Middle Eastern supply."
    slug = "india-russian-oil-imports-record-june-hormuz-crisis-crude-refiners-20260630"
    category = "news"
    vertical = "energy"
    diaspora_angle = "India's deepening oil dependence on Russia shapes the geopolitical calculations that affect everything from fuel prices at home to the diplomatic tightrope NRIs watch New Delhi walk between Washington and Moscow."

    # Image sourcing
    print("Sourcing hero image...")
    # Try Commons for oil tanker or refinery
    commons = fetch_wikimedia_commons_images("oil tanker India port")
    image_url = None
    image_caption = None
    image_attribution = None

    for c in commons:
        if commons_relevance_ok(c["title"], headline, "oil tanker refinery India crude"):
            if verify_image_url(c["url"]):
                image_url = c["url"]
                image_caption = "An oil tanker at an Indian port — Russia now supplies more than half of India's crude imports"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        commons2 = fetch_wikimedia_commons_images("crude oil refinery India")
        for c in commons2:
            if commons_relevance_ok(c["title"], headline, "oil refinery crude petroleum"):
                if verify_image_url(c["url"]):
                    image_url = c["url"]
                    image_caption = "India's refineries are processing record volumes of Russian crude"
                    image_attribution = "Wikimedia Commons"
                    break

    if not image_url:
        commons3 = fetch_wikimedia_commons_images("oil tanker ship ocean crude")
        for c in commons3:
            if verify_image_url(c["url"]):
                image_url = c["url"]
                image_caption = "A crude oil tanker — India imported a record 2.7 million bpd from Russia in June"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        pxl = fetch_pexels_image("oil refinery industrial")
        if pxl and verify_image_url(pxl):
            image_url = pxl
            image_caption = "India's refiners have turned to Russian crude in record volumes"
            image_attribution = "Pexels"

    if not image_url:
        print("  ⚠ No suitable hero image found!")
        return None

    body = """When the Strait of Hormuz choked and Middle Eastern crude became harder to move, India did what it has done with increasing conviction since 2022: it called Moscow.

Ship-tracking data from LSEG and Kpler shows that Indian refiners imported approximately 2.70 million barrels per day of Russian crude oil in June — a record high that cements Russia's position as the dominant supplier to the world's third-largest oil consumer. The figure dwarfs May's imports of around 2 million bpd and marks a dramatic acceleration of a trend that began four years ago.

Russian oil now accounts for more than half of India's total crude imports, up from 36.5% in May. Total crude imports were nearly flat at 4.9 million bpd, meaning the Russian surge came almost entirely at the expense of other suppliers.

## Hormuz Forced the Shift

The immediate trigger was the Strait of Hormuz crisis. When disruptions to the critical shipping lane — through which roughly a fifth of the world's oil passes — squeezed Middle Eastern supply, Indian refiners scrambled for alternatives. Russian barrels, already flowing at steep discounts, became the path of least resistance.

But the June record is not an aberration driven solely by crisis logistics. It is the culmination of a structural pivot that began in 2022-23, when European buyers shunned Russian crude after Moscow's invasion of Ukraine and Indian refiners stepped in to fill the gap. Russian barrels arrived at persistent discounts to international benchmarks, and India's vast refining capacity — the world's fourth-largest — was perfectly positioned to absorb them.

India had never been a major buyer of Russian oil before the Ukraine war. In early 2022, Russia supplied less than 2% of India's crude. By the end of 2023, it was the largest single supplier. The June 2026 figure — more than half of all imports — would have been unthinkable five years ago.

## The Price Equation

The economics are straightforward. Russian Urals crude has traded at discounts of $5 to $15 per barrel below Brent for much of the past two years. At current levels, with Brent at roughly $73, Indian refiners are getting Russian barrels in the low-to-mid $60s — well below the levels that strain India's current account.

For Indian state-run refiners like Indian Oil Corporation, Bharat Petroleum and Hindustan Petroleum, the savings are substantial. They translate into lower fuel import bills, better refining margins, and reduced pressure on the rupee. Goldman Sachs estimates that India's current account could post a surplus this year for the first time since the pandemic, and cheap Russian crude is a significant factor.

But there is a cost that does not show up on balance sheets. India's growing dependence on a single supplier — and a geopolitically isolated one at that — creates vulnerabilities. Payment mechanisms remain complex, with transactions routed through Dubai-based intermediaries and settled in dirhams and rupees rather than dollars. Shipping logistics are stretched, with aging tankers making longer voyages through routes that avoid Western insurance regimes.

## Washington's Quiet Discomfort

The United States has not sanctioned India for buying Russian oil — Washington has been careful to avoid alienating a strategic partner it needs for everything from supply-chain diversification to Indo-Pacific security. But the scale of the June imports is likely to intensify quiet conversations between New Delhi and Washington.

U.S. Ambassador Sergio Gor, speaking at the USISPF Leadership Summit today, described the bilateral relationship as being in its best period ever and said the trade deal was in "the last 1 percent" of negotiations. Neither he nor Indian officials have publicly linked oil purchases to trade talks.

India's position has been consistent: it will buy oil from wherever it can get the best price, and energy security is non-negotiable. As External Affairs Minister S. Jaishankar has said repeatedly, India is not the only country buying Russian energy — it is just more visible about it.

## The Hormuz Factor Goes Both Ways

Paradoxically, the same Hormuz crisis that pushed India toward Russian crude may also resolve the dependency question. The preliminary U.S.-Iran peace deal and the reopening of the strait are already bringing Brent down to pre-crisis levels. As Middle Eastern barrels become available again, Indian refiners are expected to diversify back — not out of diplomatic pressure, but because geographic proximity makes Gulf crude cheaper to ship.

Iran itself has been courting India with discounted barrels, offering crude at $4 below market price. But sanctions uncertainty makes Indian refiners wary of committing to Iranian supply in volume.

## What It Means for India's Energy Future

The June record underscores a reality that Indian policymakers have been grappling with for years: India's energy security is hostage to geopolitics it does not control. The Hormuz closure, the Ukraine war, OPEC production decisions, and Western sanctions regimes all ripple directly into Indian petrol pumps and inflation figures.

For NRIs watching from abroad, the calculus is layered. The cheap Russian crude has helped keep India's fuel prices stable and its current account manageable — both positives for the economy and the rupee. But the diplomatic complexity of being Russia's largest oil customer while simultaneously deepening defence and technology ties with Washington is a tightrope that gets harder to walk with every record-breaking month.

The second half of 2026 will test whether the Russian dependency is a feature of crisis management or a permanent realignment of India's energy map.

*Sources: Reuters, LSEG, Kpler, Goldman Sachs*"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": category,
        "vertical": vertical,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": diaspora_angle,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "LSEG", "url": "https://www.lseg.com"},
            {"name": "Kpler", "url": "https://www.kpler.com"},
            {"name": "Goldman Sachs", "url": "https://www.goldmansachs.com"},
        ]),
    }

    print(f"\nInserting article: {headline}")
    result = insert_article(article)
    return result


# ---------- main ----------
if __name__ == "__main__":
    print("=" * 60)
    print("VIDESHI WRITER RUN — June 30, 2026 Evening")
    print("=" * 60)

    results = []

    r1 = write_article_1()
    if r1:
        results.append(("Article 1", r1))

    r2 = write_article_2()
    if r2:
        results.append(("Article 2", r2))

    print(f"\n{'=' * 60}")
    print(f"Done. {len(results)} article(s) inserted.")
    print(f"{'=' * 60}")
