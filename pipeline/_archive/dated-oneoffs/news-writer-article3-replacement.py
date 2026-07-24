#!/usr/bin/env python3
"""
The Videshi — Replacement Article 3: Triple IPO
"""

import os, json, subprocess, urllib.parse
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    env = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
    return env

supabase_env = load_env(os.path.expanduser('~/.env.supabase'))
pexels_env = load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = supabase_env['SUPABASE_URL']
SUPABASE_KEY = supabase_env['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_API_KEY = pexels_env['PEXELS_API_KEY']

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}


def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
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
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page_id, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                width = ii.get("width", 0)
                if url and "image" in mime and width > 200:
                    results.append({"url": url, "title": page.get("title", "")})
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_API_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("original")
                if url:
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def validate_image_url(url):
    if not url:
        return False
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes")
            return True
        r2 = requests.get(url, timeout=10, stream=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct2 = r2.headers.get('Content-Type', '')
        r2.close()
        if r2.status_code == 200 and 'image' in ct2:
            print(f"  ✓ Image validated (GET)")
            return True
    except:
        pass
    return False


headline = "Three Companies Worth $4 Trillion Are About to Go Public. Thousands of Indian Engineers Hold the Lottery Tickets."
subheadline = "SpaceX, Anthropic and OpenAI will list within weeks of each other. For Indian tech workers with ESOP stakes, this is the biggest liquidity event of a generation."
slug = "spacex-anthropic-openai-triple-ipo-4-trillion-indian-tech-workers-esop-20260610"
category = "news"
vertical = "news"

body = """Three of the most valuable private companies on the planet are about to go public in the same quarter. SpaceX is expected to list this week at a valuation of roughly $1.77 trillion. Anthropic filed confidential IPO paperwork with the SEC on June 1. OpenAI followed on Monday, though it said going public "may be a while."

Together, the three companies command private valuations approaching $4 trillion. If they all price near the top of their expected ranges, the combined capital raise could exceed $135 billion — a sum with no modern precedent.

And thousands of Indian-origin engineers, researchers and executives sit in the middle of it.

## The Numbers That Matter

SpaceX has set the stage. It plans to sell 555 million shares at $135 apiece, raising roughly $75 billion. At a $1.77 trillion valuation, it would debut as the seventh-largest publicly traded company in the United States. The company posted a net loss of $4.94 billion in 2025, but its targeted valuation is 94.5 times its sales — more than five times Tesla's price-to-sales multiple.

Anthropic, the maker of the Claude AI models, closed a private funding round in May at a $965 billion valuation. It is expected to post its first operating profit this quarter, with revenue doubling quarter-over-quarter to an annualised run rate of $47 billion. On Tuesday, it released its most capable publicly available model, Claude Fable 5, in what looked like a well-timed pre-IPO showcase.

OpenAI, valued at $852 billion after a March funding round, has engaged Goldman Sachs and Morgan Stanley as lead underwriters. It loses roughly $1.22 for every $1 of revenue it generates and expects to spend $600 billion by the end of the decade. Its CFO, Sarah Friar, has called going public "good hygiene" for a company of its scale.

## The Indian Diaspora Angle

The connection between these three companies and India's tech workforce is not abstract. Indian-origin engineers and researchers are disproportionately represented at all three firms.

At SpaceX, Indian-origin propulsion engineers, software developers and Starlink network architects hold employee stock options that could become liquid for the first time this week. At Anthropic and OpenAI, researchers recruited from IITs, Stanford and MIT hold equity stakes that were, until last month, little more than numbers on a vesting schedule.

"Their success means they'll be able to invest more into frontier model development, and every time AI gets better, Perplexity gets better," Perplexity CEO Aravind Srinivas, himself an Indian-origin AI entrepreneur, told CNBC. The ripple effects extend well beyond the three companies.

For Indian-American tech workers, the liquidity event is generational. ESOP grants that were worth six figures at the time of hire could be worth seven or eight figures at IPO prices. The capital gains tax implications alone will reshape financial planning for a cohort of high-earning NRIs.

## The Market Impact

The three listings are already rippling through global markets. Pension funds, sovereign wealth funds and large-cap growth mandates will need to fund IPO allocations by selling existing holdings. Nancy Tengler, CEO of Laffer Tengler Investments, says her firm is already selling high-flying chip stocks to free up capital.

That reallocation pressure partly explains the brutal sell-off in Asian tech stocks earlier this week. South Korea's KOSPI triggered a circuit breaker after plunging 8.3% on Monday, with Samsung Electronics and SK Hynix — the backbone of the global AI chip supply chain — leading the rout. Japan's Nikkei fell 3.9%. India's Nifty 50 dropped 1% to a two-month low.

"The first to list sets the comp for the other two," said Harrison Rolfes, senior research analyst at PitchBook. If Anthropic lists before OpenAI and reports a profitable quarter, OpenAI would have to price against a profitable competitor at a higher valuation — an unfavourable comparison.

Databricks CEO Ali Ghodsi has already pulled his company's IPO plans. "This is a terrible year to go public," he told Bloomberg Television.

## The India Question

India's absence from the AI investment boom is now impossible to ignore. Foreign investors have pulled $26.4 billion from Indian equities so far in 2026, putting the country on track to far surpass the record $18.9 billion sell-off of 2025. India's share in the MSCI Global Standard index has shrunk from a peak of 21% in September 2024 to 12.3%.

Taiwan and South Korea — home to the physical infrastructure that powers AI — have overtaken India in global market capitalisation rankings. India's stock market, once the fourth-largest in the world, is now seventh.

Without a TSMC or SK Hynix equivalent, India is watching the AI capital wave from the shore. Abhay Laijawala of Lighthouse Canton argues that India offers "picks-and-shovels" opportunity through electricity, cooling systems and data centre infrastructure. But the market is not yet pricing that in.

## What Comes Next

The next two months will determine whether the $4 trillion IPO bet pays off or collapses under its own weight. If SpaceX prices well and trades up this week, it sets a bullish framework for Anthropic and OpenAI. If it stumbles, the repricing cascades across every private AI valuation.

For the thousands of Indian engineers sitting on options at these three companies, the stakes are personal and immediate. For India's equity markets, they are structural and uncomfortable. And for the global financial system, they are a test of whether the AI trade is the real thing — or the most expensive bet in market history.

*Sources: Reuters, Barron's, Investopedia, PitchBook, Goldman Sachs, Investors Business Daily, CNBC*"""

# Image sourcing
print("Sourcing image...")
img_url = None
img_caption = None
img_attr = None

# Try Commons for stock exchange / IPO / Wall Street
results = fetch_wikimedia_commons_images("Wall Street stock exchange IPO")
for r in results:
    if validate_image_url(r["url"]):
        img_url = r["url"]
        img_caption = "Wall Street, where SpaceX, Anthropic and OpenAI will list in 2026"
        img_attr = "Wikimedia Commons"
        break

if not img_url:
    # Try Pexels for stock market / technology
    img = fetch_pexels_image("stock market technology IPO")
    if img and validate_image_url(img):
        img_url = img
        img_caption = "Stock markets brace for the largest IPO wave in history"
        img_attr = "Pexels"

if not img_url:
    img = fetch_pexels_image("wall street new york finance")
    if img and validate_image_url(img):
        img_url = img
        img_caption = "Wall Street prepares for a record-setting IPO wave"
        img_attr = "Pexels"

article = {
    "headline": headline,
    "subheadline": subheadline,
    "slug": slug,
    "body": body,
    "category": category,
    "vertical": vertical,
    "status": "review",
    "is_editorial": False,
    "image_url": img_url,
    "image_caption": img_caption or "Wall Street prepares for record IPO listings",
    "image_attribution": img_attr or "Wikimedia Commons",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["Reuters", "Barron's", "Investopedia", "PitchBook", "Goldman Sachs", "CNBC"]),
}

r = requests.post(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    headers=HEADERS,
    json=article
)
if r.status_code in (200, 201):
    data = r.json()
    if isinstance(data, list) and data:
        print(f"✓ Inserted: {data[0].get('slug', 'unknown')}")
    else:
        print(f"✓ Inserted")
else:
    print(f"✗ Insert failed ({r.status_code}): {r.text[:300]}")
