#!/usr/bin/env python3
"""News writer for The Videshi - June 6, 2026 batch"""

import json
import os
import requests
import urllib.parse
import time
import subprocess
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    val = val.strip().strip('"').strip("'")
                    os.environ[key.strip()] = val

load_env(os.path.expanduser('~/.env.supabase'))
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

UA = 'TheVideshi/1.0 (thevideshi.com)'

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
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        'action': 'query',
        'generator': 'search',
        'gsrsearch': search_query,
        'gsrnamespace': '6',
        'gsrlimit': str(limit),
        'prop': 'imageinfo',
        'iiprop': 'url|size|mime',
        'iiurlwidth': '1200',
        'format': 'json'
    }
    try:
        r = requests.get(
            'https://commons.wikimedia.org/w/api.php',
            params=params,
            headers={"User-Agent": UA},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get('query', {}).get('pages', {})
            results = []
            for pid, page in pages.items():
                ii = page.get('imageinfo', [{}])[0]
                url = ii.get('thumburl') or ii.get('url')
                if url and ii.get('mime', '').startswith('image/'):
                    results.append({
                        'url': url,
                        'title': page.get('title', ''),
                        'width': ii.get('width', 0),
                        'height': ii.get('height', 0)
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    """Fetch an image from Pexels using curl (Python requests gets 403)."""
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        if photos:
            url = photos[0].get('src', {}).get('large2x') or photos[0].get('src', {}).get('original')
            if url:
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    """Validate that the image URL returns HTTP 200 with proper content type and size."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            ct = r.headers.get('Content-Type', '')
            cl = int(r.headers.get('Content-Length', 0))
            if 'image' in ct and cl > 5000:
                print(f"  ✓ Image validated: {ct}, {cl} bytes")
                return True
            else:
                print(f"  ⚠ Image validation failed: CT={ct}, CL={cl}")
        else:
            # Try GET for servers that don't support HEAD
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            ct = r2.headers.get('Content-Type', '')
            cl = int(r2.headers.get('Content-Length', 0))
            if r2.status_code == 200 and 'image' in ct:
                print(f"  ✓ Image validated via GET: {ct}, {cl} bytes")
                return True
            print(f"  ⚠ Image HEAD failed: {r.status_code}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=15)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('headline', 'unknown')}")
            return True
        elif isinstance(result, dict):
            print(f"  ✓ Published: {result.get('headline', 'unknown')}")
            return True
    print(f"  ✗ Insert failed: {r.status_code} - {r.text[:200]}")
    return False


# ============================================================
# ARTICLE 1: H-1B Overhaul Bill
# ============================================================
print("\n=== ARTICLE 1: H-1B Overhaul Bill ===")

art1_image = None
art1_caption = ""
art1_attribution = ""

# Try Wikipedia for Chip Roy
img = fetch_wikipedia_person_image("Chip Roy")
if img and validate_image(img):
    art1_image = img
    art1_caption = "US Congressman Chip Roy of Texas, sponsor of the American White-Collar Worker Jobs Act"
    art1_attribution = "Wikimedia Commons"

# If not, try Commons
if not art1_image:
    results = fetch_wikimedia_commons_images("H-1B visa US Congress")
    for r in results:
        if validate_image(r['url']):
            art1_image = r['url']
            art1_caption = "The US Capitol, where the H-1B overhaul bill was introduced"
            art1_attribution = "Wikimedia Commons"
            break

# Pexels fallback
if not art1_image:
    img = fetch_pexels_image("US Capitol building Washington")
    if img and validate_image(img):
        art1_image = img
        art1_caption = "The US Capitol building in Washington, D.C."
        art1_attribution = "Pexels"

art1_body = """A Republican congressman has introduced legislation that would fundamentally reshape the H-1B visa programme, ending its decades-old role as a pathway to permanent residency in the United States — a change that would upend the immigration strategy of hundreds of thousands of Indian tech workers.

Congressman Chip Roy of Texas introduced the American White-Collar Worker Jobs Act on Thursday. The bill targets several pillars of the current H-1B system that Indian workers have relied on to build lives in the United States, and it arrives at a moment when the programme is already under sustained administrative pressure from the Trump White House.

## What the bill would change

The most consequential provision is the elimination of "dual intent" — the legal doctrine that has allowed H-1B holders to simultaneously work in the US and pursue a green card. Under Roy's bill, applicants would need to prove they maintain a residence abroad and do not intend to abandon it. That would convert the H-1B from a potential stepping stone to permanent residency into a strictly temporary work visa.

The bill would also slash the maximum duration of an H-1B visa from six years to two, and repeal provisions that currently allow visa holders to extend their stay while waiting for green card processing. For the roughly 900,000 Indians in the green card backlog — some facing wait times of decades — this would eliminate the legal mechanism that keeps them in the country while they wait.

Beyond the visa itself, the legislation targets the Optional Practical Training (OPT) programme, which allows international students to work in the US for up to three years after graduation in STEM fields. Roy's bill would abolish OPT entirely, closing what has become a major pipeline for Indian students entering the American workforce.

The bill would replace the current lottery-based selection system with one that prioritises higher salaries. Employers would also face a new labour market test, administered by the Department of Labor and USCIS, to demonstrate a good-faith effort to hire American workers before turning to H-1B candidates.

## The political context

Roy's bill is co-sponsored by Arizona Republican Eli Crane and backed by US Tech Workers, the Immigration Accountability Project, and the Federation for American Immigration Reform (FAIR). Roy himself is retiring from Congress, which means the bill is less a legislative vehicle likely to pass and more a marker of where the Republican Party's immigration hawks want the debate to go.

The legislation arrives on top of a series of executive actions that have already tightened the programme. The Trump administration imposed a $100,000 fee on new H-1B petitions last September, effectively pricing out the staffing firms and mid-tier IT contractors that have been the largest sponsors of Indian workers. A weighted selection process that favours higher-wage positions took effect in February 2026, and denial rates have been climbing steadily.

The cumulative effect is already visible. In Dallas, where Indian H-1B workers once accounted for 70 percent of home sales in some suburban corridors, prices have dropped as the pipeline of new arrivals slows. FHA mortgage access for non-permanent residents has been virtually eliminated. The dynamics playing out in North Texas are beginning to appear in other tech-heavy metro areas.

## What it means for the diaspora

Roughly three-quarters of H-1B workers approved in recent years were born in India, according to Pew Research Center. The programme has been the primary legal channel through which Indian tech talent enters the American workforce, and the OPT programme has served as its feeder.

If dual intent were eliminated and visa terms shortened to two years, the calculus for an Indian engineer considering an American career would change fundamentally. The current system — arrive on an H-1B, extend while waiting for a green card, eventually settle — would cease to exist as a viable strategy.

Immigration attorneys note that the bill faces long odds in Congress, where comprehensive H-1B reform has stalled repeatedly. But the direction of travel is clear: whether through legislation or executive action, the programme that built Indian America's professional class is being systematically narrowed. The question for the hundreds of thousands of Indians already in the pipeline is whether the ground shifts under them before their paperwork clears."""

art1 = {
    "headline": "A New Bill Wants to Kill the H-1B Green Card Pipeline. Here Is What It Would Actually Do.",
    "subheadline": "Congressman Chip Roy's American White-Collar Worker Jobs Act would end dual intent, slash visa terms to two years, and abolish the OPT programme that feeds the Indian tech worker pipeline.",
    "body": art1_body.strip(),
    "slug": "chip-roy-h1b-overhaul-bill-end-dual-intent-opt-green-card-indian-workers-20260606",
    "category": "news",
    "image_url": art1_image,
    "image_caption": art1_caption,
    "image_attribution": art1_attribution,
    "sources": json.dumps(["The Hindu BusinessLine", "Daily Caller", "VisaVerge", "NY Post", "Rep. Chip Roy official press release"]),
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat()
}

if art1_image:
    insert_article(art1)
else:
    print("  ✗ No valid image found, skipping article 1")

time.sleep(2)


# ============================================================
# ARTICLE 2: AirTrunk $30B Investment
# ============================================================
print("\n=== ARTICLE 2: AirTrunk $30B Data Centre Investment ===")

art2_image = None
art2_caption = ""
art2_attribution = ""

# Try Wikimedia Commons for data centre / AI infrastructure in India
results = fetch_wikimedia_commons_images("data centre India server")
for r in results:
    if r.get('width', 0) > 400 and validate_image(r['url']):
        art2_image = r['url']
        art2_caption = "A modern data centre facility"
        art2_attribution = "Wikimedia Commons"
        break

if not art2_image:
    results = fetch_wikimedia_commons_images("cloud computing infrastructure")
    for r in results:
        if r.get('width', 0) > 400 and validate_image(r['url']):
            art2_image = r['url']
            art2_caption = "Cloud computing infrastructure"
            art2_attribution = "Wikimedia Commons"
            break

if not art2_image:
    img = fetch_pexels_image("data center servers technology")
    if img and validate_image(img):
        art2_image = img
        art2_caption = "A modern data centre with rows of server racks"
        art2_attribution = "Pexels"

art2_body = """Blackstone-backed AirTrunk has announced plans to invest roughly Rs 3 lakh crore — approximately $30 billion — in India by 2030 to build out data centre, cloud computing, and artificial intelligence infrastructure. It is one of the largest proposed investments in India's digital economy, and it signals that global capital is making a decisive bet on the country as an AI infrastructure hub.

Prime Minister Narendra Modi welcomed the announcement on X, writing that India's digital infrastructure journey is "gathering remarkable momentum." The proposed investment would develop 5 GW of data centre capacity across multiple states.

## The scale of the bet

AirTrunk, headquartered in Sydney and backed by Blackstone and the Canada Pension Plan Investment Board, entered the Indian market in April through its acquisition of Lumina CloudInfra. That deal gave it an existing pipeline of around 600 megawatts across Mumbai, Chennai, and Hyderabad — three of India's largest data centre markets.

The $30 billion commitment announced this week would expand that footprint dramatically. AirTrunk founder and CEO Robin Khuda said the company is looking to "double down" on India following meetings with government leaders in both the central government and state administrations in Maharashtra and Andhra Pradesh.

"Capital is mobile, and India is creating the conditions for it to thrive," Khuda said. "India is taking a top-down approach to AI with clear government-led initiatives, a world-class talent pool and massive availability of renewable energy."

## Why India, and why now

The investment reflects a convergence of factors that have made India increasingly attractive to hyperscale data centre operators. Global AI capital expenditure by the major cloud providers — Microsoft, Alphabet, Amazon, and Meta — is on track to exceed $400 billion in 2026, and much of that spending is flowing to markets that can offer reliable power, skilled labour, and supportive policy frameworks.

India checks several of those boxes. The government has been aggressively courting digital infrastructure investment, and the country's renewable energy capacity gives it an edge in an industry where power costs are a dominant factor. India also offers a domestic market of 1.4 billion people whose digital consumption is growing rapidly.

The discussions between AirTrunk and state governments focused on access to reliable power supply, renewable energy, sustainable water resources, talent development, and faster project approvals — the practical bottlenecks that determine whether large-scale data centre investments materialise or remain announcements.

## The broader digital infrastructure race

AirTrunk's commitment comes amid a wave of data centre investment in India. Google, Amazon Web Services, and Microsoft have all announced or expanded Indian data centre regions in the past year. India's data centre market is projected to reach $10 billion by 2027, growing at roughly 25 percent annually.

For the diaspora, the investment has implications beyond the headline number. India's growing role in global AI infrastructure could create a new category of high-skill employment that keeps Indian engineers in India rather than funnelling them abroad — or attracts NRIs back. Khuda explicitly cited India's "world-class talent pool" as a factor in the investment decision.

The investment also fits a pattern that has become familiar in Modi's economic playbook: using large, announced foreign investment commitments to signal India's arrival as a serious destination for technology capital. Whether $30 billion ultimately materialises in full will depend on execution — power availability, land acquisition, water access, and regulatory speed are all variables. But the direction of global AI capital is increasingly clear, and India is positioning itself squarely in its path."""

art2 = {
    "headline": "Blackstone-Backed AirTrunk Plans a $30 Billion Bet on India's AI Infrastructure",
    "subheadline": "The Australian data centre giant's proposed investment would build 5 GW of capacity across India, making it one of the largest digital infrastructure commitments the country has seen.",
    "body": art2_body.strip(),
    "slug": "airtrunk-30-billion-india-data-centre-ai-investment-blackstone-modi-20260606",
    "category": "news",
    "image_url": art2_image,
    "image_caption": art2_caption,
    "image_attribution": art2_attribution,
    "sources": json.dumps(["Times of India", "Reuters", "currato.com", "AirTrunk official statement"]),
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat()
}

if art2_image:
    insert_article(art2)
else:
    print("  ✗ No valid image found, skipping article 2")

time.sleep(2)


# ============================================================
# ARTICLE 3: India Exempts Foreign Investors from Bond Tax
# ============================================================
print("\n=== ARTICLE 3: India Bond Tax Exemption ===")

art3_image = None
art3_caption = ""
art3_attribution = ""

# Try Wikipedia for RBI
img = fetch_wikipedia_person_image("Reserve Bank of India")
if img and validate_image(img):
    art3_image = img
    art3_caption = "The Reserve Bank of India headquarters in Mumbai"
    art3_attribution = "Wikimedia Commons"

if not art3_image:
    results = fetch_wikimedia_commons_images("Reserve Bank of India building Mumbai")
    for r in results:
        if r.get('width', 0) > 400 and validate_image(r['url']):
            art3_image = r['url']
            art3_caption = "The Reserve Bank of India headquarters in Mumbai"
            art3_attribution = "Wikimedia Commons"
            break

if not art3_image:
    img = fetch_pexels_image("Indian rupee currency finance")
    if img and validate_image(img):
        art3_image = img
        art3_caption = "Indian currency and financial instruments"
        art3_attribution = "Pexels"

art3_body = """India has exempted foreign institutional investors from capital gains tax on government bonds, a targeted move to attract dollar inflows as the rupee continues to weaken under pressure from elevated oil prices and the Iran conflict. The announcement, made alongside the Reserve Bank of India's decision to hold interest rates steady at 5.25 percent, is part of a broader package designed to shore up the currency without resorting to a rate hike that would choke growth.

## What changed

The government announced on Friday that foreign institutional investors and the Bank for International Settlements will no longer pay capital gains tax on income from interest or the sale of government securities. Until now, foreign investors faced a 12.5 percent long-term capital gains tax on listed bonds held for more than 12 months, and a 20 percent withholding tax on interest earned from government bonds.

The tax exemption is intended to make Indian government debt more attractive to the kind of stable, long-term foreign capital that anchors a currency — pension funds, sovereign wealth funds, and central banks. The rupee has weakened over 5 percent this year, driven by equity outflows and the energy price shock from the Iran war, and the government is looking for tools that do not require tightening monetary policy.

## The RBI's balancing act

The tax move came hours after the RBI's Monetary Policy Committee voted to hold the repo rate at 5.25 percent, the third consecutive pause. The central bank raised its inflation forecast while lowering its growth projection — the kind of stagflationary setup that leaves policymakers with no good options.

Rather than hiking rates to defend the rupee — an approach that economists at the RBI itself acknowledged would be an "imprecise instrument" — the central bank announced a series of measures to improve capital flows. These include reducing hedging costs for foreign borrowers, easing overseas borrowing conditions for Indian corporates and public sector undertakings, and creating incentives for NRI dollar deposits through the FCNR channel.

"The RBI addressed the root issue," said Vikram Chhabra, senior economist at 360 ONE Asset. "We expect pressure on the rupee to ease from here. However, the growth-inflation trade-off is becoming more acute."

## What it means for NRIs

While the capital gains exemption applies specifically to foreign institutional investors rather than individual NRI investors, the broader package has direct implications for the diaspora. The RBI's measures to make FCNR (Foreign Currency Non-Resident) deposits more attractive are aimed squarely at NRIs, incentivising them to park dollars in Indian banks at a time when the central bank needs foreign currency reserves.

The move also affects NRIs who invest in Indian bonds through mutual funds or portfolio investment schemes. Lower hedging costs and improved overseas borrowing conditions could benefit Indian corporates that NRIs hold equity in, and the resulting improvement in the rupee could affect remittance calculations.

Bond market participants noted that foreign investors have already been shifting toward shorter-duration Indian government securities. Bonds with maturities under five years made up over two-thirds of top foreign purchases during March through May, as investors position for a potential rate tightening cycle while capturing attractive entry yields.

## The bigger picture

India is walking a narrow path. Growth remains among the strongest in the world at 7.8 percent in the last quarter, but inflation is rising on the back of an energy shock that is largely outside the country's control. The Iran war has driven a permanent risk premium into oil prices, and India — the world's third-largest oil importer — absorbs that cost directly.

The tax exemption and capital flow measures represent a bet that India can defend the rupee through structural attractiveness rather than rate hikes. If the measures succeed in drawing foreign capital into Indian debt, they could buy time for the monsoon outlook to clarify and for the West Asia conflict to resolve. If they do not, the RBI may face a rate hike as early as August — a move that would slow growth in an economy that, for now, remains one of the few bright spots in the global picture."""

art3 = {
    "headline": "India Just Scrapped Capital Gains Tax on Foreign Bond Investments. The Rupee Needed the Help.",
    "subheadline": "The government exempted foreign investors from bond taxes as the RBI held rates steady, betting on structural capital flows rather than a rate hike to defend a weakening rupee.",
    "body": art3_body.strip(),
    "slug": "india-capital-gains-tax-exemption-foreign-bonds-rbi-rupee-defence-nri-20260606",
    "category": "news",
    "image_url": art3_image,
    "image_caption": art3_caption,
    "image_attribution": art3_attribution,
    "sources": json.dumps(["Reuters", "The Hindu BusinessLine", "State Street Investment Management", "360 ONE Asset"]),
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat()
}

if art3_image:
    insert_article(art3)
else:
    print("  ✗ No valid image found, skipping article 3")

print("\n=== News writer complete ===")
