#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-02 02:00 PDT run.

Writes 3 articles:
1. Silicon Valley's Indian-origin CEOs buy London Spirit cricket team
2. Microsoft consortium builds undersea cable linking India to Southeast Asia
3. UPI hits record daily average, now live in 10 countries
"""

import json, os, uuid, re, requests, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ──────────────────────────────────────────────────────────────────
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ── Image sourcing ───────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10
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


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images. Returns list of dicts."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers=UA, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for p in pages.values():
                ii = p.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                w = ii.get("width", 0)
                h = ii.get("height", 0)
                mime = ii.get("mime", "")
                if url and "image" in mime and w >= 400:
                    results.append({"url": url, "title": p.get("title", ""), "width": w, "height": h})
            return results
    except Exception as e:
        print(f"  ⚠ Commons search error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for a relevant image. Returns URL or None."""
    pexels_env = Path.home() / "workspace/.env.pexels"
    if not pexels_env.exists():
        print("  ⚠ No Pexels API key found")
        return None
    api_key = None
    for line in pexels_env.read_text().strip().splitlines():
        if "PEXELS_API_KEY" in line and "=" in line:
            api_key = line.split("=", 1)[1].strip()
    if not api_key:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 5},
            headers={"Authorization": api_key},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def verify_image(url):
    """Verify an image URL returns HTTP 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, headers=UA, timeout=10, allow_redirects=True)
        ct = r.headers.get("content-type", "")
        cl = int(r.headers.get("content-length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # HEAD can be unreliable (wikimedia returns 400); try GET
        r2 = requests.get(url, headers=UA, timeout=10, stream=True, allow_redirects=True)
        ct2 = r2.headers.get("content-type", "")
        # Read first 6KB to check size
        chunk = r2.raw.read(6000)
        r2.close()
        if r2.status_code == 200 and "image" in ct2 and len(chunk) >= 5000:
            return True
    except Exception:
        pass
    return False


# ── Source images ─────────────────────────────────────────────────────────────

print("=== Sourcing images ===")

# Article 1: Nikesh Arora (leads the consortium)
print("\n1. London Spirit — trying Nikesh Arora Wikipedia...")
img1 = fetch_wikipedia_person_image("Nikesh Arora")
img1_caption = "Nikesh Arora, CEO of Palo Alto Networks, who led the consortium of Indian-origin tech CEOs"
img1_attr = "Wikimedia Commons"
if not img1:
    print("   Trying 'Satya Nadella' as fallback...")
    img1 = fetch_wikipedia_person_image("Satya Nadella")
    img1_caption = "Satya Nadella, CEO of Microsoft, one of the consortium members who bought London Spirit"
if not img1:
    # Try Commons
    results = fetch_wikimedia_commons_images("The Hundred cricket London Spirit Lord's")
    if results:
        img1 = results[0]["url"]
        img1_caption = "Lord's Cricket Ground, home of the London Spirit franchise"

# Article 2: Undersea cable / data center
print("\n2. Undersea cable / data center — trying Commons...")
img2 = None
img2_caption = ""
img2_attr = "Wikimedia Commons"
commons_results = fetch_wikimedia_commons_images("submarine cable undersea fiber optic")
if commons_results:
    img2 = commons_results[0]["url"]
    img2_caption = "Submarine fiber optic cable infrastructure linking continents"
if not img2:
    commons_results = fetch_wikimedia_commons_images("data center India server")
    if commons_results:
        img2 = commons_results[0]["url"]
        img2_caption = "Data center server infrastructure powering India's AI ambitions"
if not img2:
    img2 = fetch_pexels_image("submarine fiber optic cable ocean")
    img2_attr = "Pexels"
    img2_caption = "Submarine cable infrastructure connecting global data networks"
if not img2:
    img2 = fetch_pexels_image("data center server room blue")
    img2_attr = "Pexels"
    img2_caption = "Server racks in a modern data center facility"

# Article 3: UPI / digital payments
print("\n3. UPI — trying Commons...")
img3 = None
img3_caption = ""
img3_attr = "Wikimedia Commons"
commons_results = fetch_wikimedia_commons_images("UPI Unified Payments Interface India")
if commons_results:
    # Filter for something relevant
    for r in commons_results:
        title_lower = r["title"].lower()
        if "upi" in title_lower or "payment" in title_lower or "bhim" in title_lower:
            img3 = r["url"]
            img3_caption = "India's UPI digital payments system, now live in 10 countries"
            break
    if not img3 and commons_results:
        img3 = commons_results[0]["url"]
        img3_caption = "India's digital payments infrastructure"
if not img3:
    img3 = fetch_pexels_image("mobile payment QR code India smartphone")
    img3_attr = "Pexels"
    img3_caption = "A customer making a mobile payment via QR code in India"

# Verify images
for label, url in [("Article 1", img1), ("Article 2", img2), ("Article 3", img3)]:
    if url:
        ok = verify_image(url)
        print(f"  {label} image verify: {'✓' if ok else '✗'} — {url[:80]}...")
    else:
        print(f"  {label}: No image found, will skip")

# ── Articles ──────────────────────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Nadella, Pichai and Arora Just Bought a Cricket Team at Lord's. The Price Tag Was £145 Million.",
        "subheadline": "A consortium of 11 Indian-origin Silicon Valley executives outbid IPL moguls to acquire a 49% stake in London Spirit — the franchise that plays at the most storied ground in cricket.",
        "slug": make_slug("nadella-pichai-arora-london-spirit-cricket-hundred"),
        "category": "technology",
        "vertical": "tech-leaders",
        "diaspora_angle": "The deal shows how deeply Indian-origin tech wealth is reshaping global sport ownership — from MLC in the US to The Hundred in England — and signals a new route for diaspora capital into cricket's commercial backbone.",
        "tags": ["indian-tech-leaders", "cricket", "silicon-valley", "the-hundred", "london-spirit"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Cricbuzz", "url": "https://www.cricbuzz.com/cricket-news/134206/microsoft-head-google-ceo-times-internet-vc-amongst-consortium-that-bags-london-spirit"},
            {"name": "Front Office Sports", "url": "https://frontofficesports.com/google-microsoft-adobe-ceos-buy-stakes-in-cricket-league/"},
            {"name": "TechRadar", "url": "https://www.techradar.com/pro/the-ceos-of-microsoft-and-alphabet-have-bought-part-of-the-london-hundred-cricket-franchise"},
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/sundar-pichai-satya-nadella-and-other-tech-ceos-bid-for-london-based-cricket-team-report-11737047050120.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img1 or "",
        "image_caption": img1_caption,
        "image_attribution": img1_attr,
        "body": """When the England and Wales Cricket Board put its eight Hundred franchises up for private investment, the smart money was on IPL owners and European football consortia. Nobody expected Silicon Valley to walk away with Lord's.

But on Friday, a consortium of 11 Indian-origin technology executives — led by Palo Alto Networks CEO Nikesh Arora — paid £145 million for a 49% stake in London Spirit, the franchise that calls the most hallowed ground in cricket its home. The deal values the team at just over £295 million and stands as the largest single-franchise bid in the ECB's privatisation process.

## The Consortium

The names read like an all-star roster of Indian-origin tech leadership. Alongside Arora sit Microsoft Chairman and CEO Satya Nadella, Alphabet CEO Sundar Pichai, Adobe CEO Shantanu Narayen, and Satyan Gajwani, vice-chairman of Times Internet and co-founder of Major League Cricket. Silver Lake co-CEO Egon Durban rounds out the most prominent members.

The consortium prevailed after a four-hour online auction that saw aggressive counter-bidding from Sanjiv Goenka, owner of IPL's Lucknow Super Giants and SA20's Durban Super Giants. Goenka, who was widely expected to add a third franchise to his portfolio, was ultimately outgunned by the collective buying power of the Valley.

The deal caps a remarkable week for the ECB. Within two days of opening the auction, it had already secured over £300 million across four teams — comfortably exceeding its initial target of £350 million for all eight. Reliance Industries, which owns the Mumbai Indians, was among the other successful bidders. Separately, Washington Freedom, an MLC team, secured Welsh Fire for £65 million.

## From MLC to Lord's

This isn't the group's first foray into cricket ownership. Nadella and Narayen were early investors in Major League Cricket, the American T20 league that launched in 2023 and has steadily built audiences in the diaspora-heavy markets of Dallas, New York, and the San Francisco Bay Area. Gajwani is MLC's co-founder.

The Hundred represents a different proposition entirely. The 100-ball format, launched in 2021, was designed to be cricket's answer to T20's commercial explosion — shorter matches, city-based teams, and a broadcast package aimed squarely at younger, casual fans. More than two million spectators have attended matches across its eight venues.

But the London Spirit bid is as much about real estate as sport. Lord's, owned by the Marylebone Cricket Club, carries a brand cachet that no other cricket ground on earth can match. A franchise anchored there gives the consortium a permanent foothold in English cricket's commercial infrastructure.

## The Diaspora Play

The total valuation of The Hundred's eight teams now stands at £975 million. Indian-origin capital accounts for a disproportionate share of that figure, a pattern that mirrors the broader flow of diaspora wealth into global sports — from the IPL's original franchise auctions to football club acquisitions across Europe.

For Indian Americans in particular, the deal underscores how thoroughly the generation of executives who arrived in the United States on student visas and H-1B permits has reshaped not just the technology industry, but the commercial architecture of global sport. Nadella's Microsoft is worth $3.3 trillion. Pichai's Alphabet is worth $2.2 trillion. Between them, the consortium members oversee companies with a combined market capitalisation exceeding $8 trillion.

Whether they will exercise their option to acquire a majority stake remains unclear. For now, the ECB has achieved its immediate goal: turning The Hundred into a viable commercial product with deep-pocketed, long-term owners. The fact that the deepest pockets belong to Hyderabad and Chennai natives running American technology companies is the most Indian story in English cricket since the IPL began poaching its best players."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Microsoft Is Building a 3,600-Km Undersea Cable From India to Singapore. Tata Communications Is Helping.",
        "subheadline": "The I-2SEA cable consortium — which also includes Singtel and Japan's NEC — will land in the same Indian port city where Meta and Google are building data centers. It could be operational by late 2029.",
        "slug": make_slug("microsoft-tata-i2sea-undersea-cable-india-singapore"),
        "category": "technology",
        "vertical": "infrastructure",
        "diaspora_angle": "The undersea cable and the $80 billion data center buildout behind it are creating a massive new demand center for Indian engineering talent — and making India-origin cloud services viable at a scale that could eventually rival the US for NRI-run enterprises.",
        "tags": ["microsoft", "tata-communications", "undersea-cable", "data-center", "india-infrastructure", "ai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/media-telecom/microsoft-partners-with-singapores-lightstorm-build-india-southeast-asia-2026-07-02/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/ai-data-centers-india-75425e19"},
            {"name": "Barron's / Amazon", "url": "https://www.barrons.com/articles/amazon-ai-data-centers-india-d9a0f2c3"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img2 or "",
        "image_caption": img2_caption,
        "image_attribution": img2_attr,
        "body": """A consortium led by Microsoft announced on Wednesday that it will build I-2SEA, a 3,600-kilometre submarine cable connecting India to Malaysia and Singapore — the latest and most concrete sign that global tech infrastructure is pivoting hard toward South Asia.

The cable's partners include Tata Communications, Singapore Telecommunications (Singtel), Japan's NEC Corporation, and Singapore-based telecom startup Lightstorm Group, which connects 19 AI and cloud zones across India through its existing terrestrial fibre network. The project is designed to support AI, cloud, and hyperscale workloads, and is expected to be operational in the fourth quarter of 2029.

## Landing at the Centre of India's AI Map

The cable's Indian landing station will be in Machilipatnam, a port city in Andhra Pradesh — the same state where Meta and Alphabet have separately announced data centre campuses. Google's $15 billion investment in the region is centred on nearby Visakhapatnam. The geographic convergence is not coincidental: Andhra Pradesh's coastline offers both cheap land and direct access to the subsea routes that carry 95% of the world's internet traffic.

India currently operates 17 active submarine cables with a combined potential capacity of 960 terabits per second. At least 10 more have been publicly announced, according to telecommunications research firm TeleGeography. I-2SEA will link the Indian network directly to Singapore's data centre cluster, one of Asia's most critical digital infrastructure nodes.

Lightstorm, which is backed by infrastructure investor I Squared Capital, is planning an Indian IPO by mid-2027 at a valuation of up to $1.5 billion, CEO Amajit Gupta told Reuters. The I-2SEA cable will expand its network reach from 19 to 29 AI and cloud zones across India.

## The Numbers Behind the Boom

The cable lands amid an extraordinary wave of capital flowing into Indian data infrastructure. Microsoft has committed $17.5 billion — its largest investment in Asia. Alphabet's Google has pledged $15 billion for three data centre campuses. Amazon, which this week brought CEO Andy Jassy to New Delhi for meetings with Prime Minister Modi, has raised its total planned India investment to $48 billion through 2030, including a fresh $13 billion earmarked for AI capacity in Mumbai and Hyderabad.

Together, these three hyperscalers alone account for more than $80 billion in committed India spending. And they are not alone: Yotta Data Services is building a $2 billion AI hub with Nvidia's Blackwell chips, and Reliance Jio has partnered with Nvidia on data centres that could eventually reach 2,000 megawatts.

Nomura estimates India's data centre capacity will grow tenfold over the next decade. Synergy Research Group projects India's share of global capacity will rise from 1.3% to 3% — numbers that sound modest until you consider the base: global data centre capacity is measured in tens of gigawatts.

## Why India, Why Now

Three forces are converging. First, latency: data centres need to be geographically close to users, and Indians are the second-largest users of both ChatGPT and Claude globally. Second, incentives: in February, India declared zero taxes until 2047 on overseas services by foreign companies operating data centres in the country. Third, regulatory ease: unlike in the United States, where community opposition has slowed or blocked data centre projects, Indian approvals move through without public hearings.

That last point cuts both ways. Barron's reported this week that Indian communities near proposed data centre sites have little formal mechanism to object — a contrast to the fierce local battles playing out in Virginia, Georgia, and Arizona. For US tech companies, India offers speed and scale. For the communities adjacent to these projects, the trade-off is less clear.

## The NRI Calculus

For Indian Americans in technology, the infrastructure surge creates two distinct opportunities. The first is professional: Microsoft alone employs more than 22,000 people in India, and the new data centres will generate demand for cloud architects, AI engineers, and infrastructure specialists — roles that feed the cross-border talent pipeline NRIs navigate daily.

The second is financial. Lightstorm's planned IPO, Yotta's pre-IPO fundraising, and the growing ecosystem of Indian data infrastructure companies represent an emerging asset class for diaspora investors who have long been limited to IT services stocks and domestic real estate as their primary India exposure. The undersea cable may carry data, but the capital flowing through it is just as significant."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "UPI Now Processes 757 Million Transactions a Day. Greece Just Became Its 10th Country.",
        "subheadline": "India's digital payments juggernaut hit a new daily record in June even as monthly volumes pulled back from May's all-time high. Meanwhile, SBI-backed Cashfree is betting on cross-border travel and investment payments.",
        "slug": make_slug("upi-757-million-daily-record-greece-10th-country"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "For the millions of NRIs who send money home, shop on Indian e-commerce platforms, or invest in Indian markets, UPI's international expansion and the fintech cross-border push directly reduce the friction and cost of staying financially connected to India.",
        "tags": ["upi", "digital-payments", "fintech", "india", "cashfree", "cross-border", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/personal-finance/upi-transactions-ease-from-record-high-to-rs-289-lakh-cr-in-june"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/finance/indias-sbi-backed-cashfree-payments-bets-cross-border-push-with-travel-investment-2026-06-30/"},
            {"name": "Impressive Times", "url": "https://www.impressivetimes.com/news/digital-india-11-years-upi-poshan-tracker-online-markets-transform-lives/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/money-and-banking/fintechs-bet-on-upi-led-engagement-to-build-lending-commerce-business/article69752330.ece"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img3 or "",
        "image_caption": img3_caption,
        "image_attribution": img3_attr,
        "body": """India's Unified Payments Interface processed a daily average of 757 million transactions in June — the highest figure ever recorded since UPI launched a decade ago. That is roughly 8,750 transactions every second, every day, for 30 straight days.

The June numbers, released by the National Payments Corporation of India on Wednesday, tell a deceptively simple story. Monthly transaction value came in at ₹28.9 lakh crore ($305 billion), a modest step back from May's record of ₹29.9 lakh crore. Monthly volume dipped too, from 23.2 billion transactions to 22.72 billion. But the daily average — the figure that actually reveals behavioural penetration — climbed to a new peak.

"The daily averages tell a very interesting story of how UPI has become the default mode of payment for low-value transactions," said Reeju Datta, co-founder of Cashfree Payments. Year-on-year, UPI volumes grew by over 4.3 billion transactions and nearly ₹5 lakh crore in value.

## Ten Countries and Counting

While the domestic story is one of deepening saturation — a street vendor in Varanasi and a Starbucks in Gurgaon now share the same payment rail — the international narrative is accelerating. UPI is now live in 10 countries: the UAE, Singapore, Bhutan, Nepal, Sri Lanka, France, Mauritius, Qatar, and, most recently, Greece. In each market, Indian travellers and NRIs can pay using their Indian bank-linked UPI apps at participating merchants.

Greece became the 10th nation to adopt UPI-based services, extending a pattern that started with Singapore and the UAE — countries with large Indian expatriate populations — and has since moved into tourist-heavy European markets where Indian arrivals are climbing.

For the Indian diaspora, the practical impact is straightforward: an NRI visiting Paris or Doha can pay with PhonePe or Google Pay at select merchants without converting currency in advance. The rails are still narrow — acceptance depends on the local partner network — but the direction is clear.

## Cashfree's Cross-Border Bet

The most ambitious play on UPI's international expansion is coming from Cashfree Payments, the Bengaluru-based fintech backed by State Bank of India. The company, which processes $80 billion in annual transactions for more than one million businesses, told Reuters this week that it plans to expand its cross-border services well beyond e-commerce.

CEO Akash Sinha said the company will pilot overseas investment payments, travel payments, and business-to-business transaction services this year. Cross-border currently accounts for 10% of Cashfree's revenue — roughly ₹1,000 crore on a base of nearly ₹10 billion in FY2026 revenue. Sinha expects it to reach 25% within three to four years.

The bet rests on a structural advantage: unlike domestic UPI processing, where intense competition has squeezed margins to near zero, cross-border transactions carry better economics because they involve foreign exchange conversion and regulatory compliance overhead. In other words, the harder the payment is to execute, the more a specialist intermediary can charge.

## From Payments to Platform

Domestically, the UPI story is shifting from volume growth to monetisation. Fintechs such as Flipkart-backed super.money, Navi, and Kiwi are using UPI as a customer acquisition layer, then cross-selling credit, secured cards, and financial products to the user base they have built.

Prakash Sikaria, founder of super.money, described the company's model as three pillars: UPI for engagement, credit for monetisation, and commerce for lifetime value. Nearly 40 to 45% of super.money's users are first-time formal credit customers, and over 75% belong to Gen Z — the cohort that has never known an India without digital payments.

## What NRIs Should Watch

The regulatory scaffolding around UPI is also evolving. The Reserve Bank of India's Payments Vision 2028 framework includes a proposal for bank account portability — a central switching system that would let consumers change banks while keeping the same account number, with automatic transfer of standing orders and recurring payments. If implemented, it would make UPI even stickier as the default financial interface.

For NRIs, the intersection of UPI's international expansion, Cashfree's cross-border push, and the RBI's portability framework points toward a future in which managing Indian finances from abroad is genuinely seamless — paying Indian bills, investing in Indian markets, and receiving rupee income, all on rails that were built for a vegetable vendor's QR code and have since scaled to a $305 billion monthly throughput."""
    },
]

# ── Insert ────────────────────────────────────────────────────────────────────

print("\n=== Inserting articles ===")
for art in articles:
    if not art["image_url"]:
        print(f"  ⚠ Skipping image for {art['slug']} — no image found")
    try:
        result = sb_post("p2_articles", art)
        print(f"  ✅ {art['slug']}")
    except Exception as e:
        print(f"  ❌ {art['slug']}: {e}")

print("\nDone.")
