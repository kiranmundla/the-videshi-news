#!/usr/bin/env python3
"""
The Videshi News Writer — 2026-06-12 afternoon batch
Writes 3 news articles, sources images, inserts into Supabase with status="review"
"""

import requests
import json
import os
import sys
import re
import urllib.parse
from datetime import datetime, timezone

# Load environment variables
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip()

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')

if not all([SUPABASE_URL, SUPABASE_KEY]):
    print("ERROR: Missing Supabase credentials")
    sys.exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ============================================================
# IMAGE SOURCING FUNCTIONS
# ============================================================

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
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
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
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
                imageinfo = page.get("imageinfo", [{}])[0]
                url = imageinfo.get("thumburl") or imageinfo.get("url")
                width = imageinfo.get("width", 0)
                height = imageinfo.get("height", 0)
                mime = imageinfo.get("mime", "")
                if url and "image" in mime and width >= 300:
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": width,
                        "height": height
                    })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for a relevant stock photo. Use curl-like approach."""
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            headers={"Authorization": PEXELS_API_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def validate_image_url(url):
    """Validate that an image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            return True
        # Some servers don't support HEAD, try GET
        if r.status_code in [200, 405]:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, stream=True)
            content_type = r2.headers.get("Content-Type", "")
            chunk = r2.raw.read(6000)
            r2.close()
            if r2.status_code == 200 and len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False

def insert_article(article):
    """Insert article into Supabase p2_articles table."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in [200, 201]:
        result = r.json()
        if isinstance(result, list) and len(result) > 0:
            print(f"  ✓ Inserted: {result[0].get('headline', 'unknown')[:60]}...")
            return result[0]
        print(f"  ✓ Inserted article")
        return result
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return None

# ============================================================
# ARTICLE 1: TCS-Anthropic Partnership
# ============================================================

def write_article_1():
    print("\n=== Article 1: TCS Partners with Anthropic ===")
    
    # Image sourcing — try N. Chandrasekaran (TCS Chairman) from Wikipedia
    img_url = fetch_wikipedia_person_image("N. Chandrasekaran")
    img_caption = "N. Chandrasekaran, chairman of Tata Sons and TCS, at a corporate event"
    img_attribution = "Wikimedia Commons"
    
    if not img_url or not validate_image_url(img_url):
        # Try TCS or Dario Amodei
        img_url = fetch_wikipedia_person_image("Dario Amodei")
        img_caption = "Dario Amodei, co-founder and CEO of Anthropic"
        if not img_url or not validate_image_url(img_url):
            # Try Wikimedia Commons
            commons = fetch_wikimedia_commons_images("Tata Consultancy Services")
            if commons:
                img_url = commons[0]["url"]
                img_caption = "Tata Consultancy Services headquarters"
            else:
                # Pexels fallback — generic AI/tech
                img_url = fetch_pexels_image("artificial intelligence enterprise office")
                img_caption = "An enterprise office building, representing the changing landscape of India's IT industry"
                img_attribution = "Pexels"
    
    if img_url and not validate_image_url(img_url):
        print(f"  ⚠ Image validation failed, trying Pexels fallback")
        img_url = fetch_pexels_image("artificial intelligence enterprise technology")
        img_caption = "A modern enterprise technology centre, representing the AI transformation sweeping India's IT sector"
        img_attribution = "Pexels"
    
    headline = "TCS Just Partnered with the AI Company That Wiped $63 Billion Off India's IT Sector. It Plans to Give 50,000 Workers Access to Claude."
    
    body = """In February, Anthropic released an AI agent tool that triggered a sell-off so brutal it erased more than $62.8 billion in market capitalisation from India's IT services firms in a matter of days. On Thursday, Tata Consultancy Services — the largest of those firms — announced that it was partnering with Anthropic and giving 50,000 of its own employees access to Claude.

The juxtaposition captures the strange moment India's $315-billion IT services industry finds itself in: terrified of AI's disruptive potential, yet racing to embrace the very tools that threaten its labour-intensive business model.

## What the Deal Involves

TCS will create a dedicated business unit focused on deploying Anthropic's Claude models for enterprise clients, with a particular focus on highly regulated sectors including financial services, healthcare, aviation, telecom and life sciences. The company becomes a Global Premier Partner in Anthropic's Claude Partner Network, gaining early access to new model releases.

Internally, TCS will roll out Claude to 50,000 associates across engineering, finance, legal, marketing and sales. The company says this will give it first-hand operational experience in transforming its own workflows — experience it then plans to sell to clients.

Dario Amodei, Anthropic's co-founder and CEO, described the partnership as deepening the AI firm's commitment to India, which he called Anthropic's second-largest market. TCS CEO K. Krithivasan said the collaboration would help clients "move faster to production, particularly in industries where trust, resilience, and regulatory discipline are critical."

## The Numbers Tell a Harder Story

The partnership announcement landed against a backdrop of relentless job cuts. TCS shed more than 12,000 positions last July alone. Over the full fiscal year ending March 2026, its net headcount fell by 23,000. Its chairman, N. Chandrasekaran, told shareholders at the company's annual general meeting on Tuesday that TCS expects to move towards having an "equal number of employees and AI agents" in its workforce.

That is not a throwaway line. It is a roadmap for a company with over 600,000 employees.

TCS is not alone. Rival Infosys struck a similar partnership with Anthropic back in February. OpenAI has roped in both Infosys and HCLTech for comparable alliances. Across India's big three IT services firms, more than 42,000 jobs have been cut in recent years, and each company has deployed over 50,000 AI licences.

## Why NRIs Should Pay Attention

For the hundreds of thousands of Indian tech workers in the United States — many of them on H-1B visas tied to IT services companies — the shift carries personal stakes. If AI agents can handle the routine coding, testing and data processing that sustained India's outsourcing boom, the demand for the roles that brought many NRIs to America in the first place starts to erode.

A recent Anthropic-authored study found that the categories of work India's IT industry runs on — programming, quality assurance, data entry — are up to 74.5 per cent exposed to AI automation. The study's own conclusion, "no crisis yet," rings hollow when laid against the 42,000 jobs already gone.

The IT index on India's National Stock Exchange has fallen 27 per cent this year. TCS shares are down 34 per cent. Infosys has lost 31 per cent. The sell-off has pushed India's overall market capitalisation below that of AI-heavy Taiwan and South Korea for the first time.

## The Bet

TCS is essentially betting that by getting closer to Anthropic, it can ride the wave rather than be drowned by it. The company's UK subsidiary Diligenta, which manages life and pension services for over 22 million customers, plans to use Claude for customer service and process automation. TCS iON, its digital learning platform, will offer training and certification programmes on Anthropic's models.

If the bet works, TCS transforms from a labour-cost arbitrage play into an AI-powered consulting firm that charges for outcomes rather than headcount. If it does not, the partnership accelerates the very displacement that triggered the February sell-off.

For India's IT workforce, the message from Chandrasekaran's AGM speech is unambiguous: the era of bodies-for-billing is ending. The firms that built the Indian outsourcing miracle are now building the tools that replace it."""
    
    article = {
        "headline": headline,
        "subheadline": "The partnership comes after Anthropic's tools triggered a $62.8 billion market-cap wipeout in Indian IT. TCS's chairman says the company is moving towards equal numbers of AI agents and human employees.",
        "body": body,
        "slug": "tcs-anthropic-partnership-claude-50000-workers-it-jobs-disruption-20260612",
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": json.dumps([
            "Reuters — India's TCS partners with Anthropic to drive enterprise AI scaling",
            "TechCrunch — Anthropic taps TCS to scale its enterprise AI deployments",
            "The Hindu BusinessLine — TCS, Anthropic partner to drive Enterprise AI scaling",
            "Outlook Business — TCS Teams Up With Anthropic, Plans Claude Access for 50,000 Employees"
        ]),
        "diaspora_angle": "Hundreds of thousands of NRI tech workers on H-1B visas at IT services firms face job uncertainty as their employers deploy AI agents to replace the very roles that brought them to America.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    
    return insert_article(article)


# ============================================================
# ARTICLE 2: Kevin Warsh's First Fed Meeting
# ============================================================

def write_article_2():
    print("\n=== Article 2: Kevin Warsh's First Fed Meeting ===")
    
    # Image sourcing — Kevin Warsh from Wikipedia
    img_url = fetch_wikipedia_person_image("Kevin Warsh")
    img_caption = "Kevin Warsh, the new chairman of the US Federal Reserve"
    img_attribution = "Wikimedia Commons"
    
    if not img_url or not validate_image_url(img_url):
        # Try Wikimedia Commons for Federal Reserve building
        commons = fetch_wikimedia_commons_images("Federal Reserve Building Washington")
        if commons:
            img_url = commons[0]["url"]
            img_caption = "The Federal Reserve headquarters in Washington, DC"
        else:
            img_url = fetch_pexels_image("federal reserve building Washington DC")
            img_caption = "The Federal Reserve headquarters in Washington, DC"
            img_attribution = "Pexels"
    
    if img_url and not validate_image_url(img_url):
        img_url = fetch_pexels_image("central bank finance building")
        img_caption = "The Federal Reserve building, where Kevin Warsh will chair his first FOMC meeting on June 16"
        img_attribution = "Pexels"
    
    headline = "Kevin Warsh Chairs His First Fed Meeting Next Week. India Has $30 Billion Worth of Reasons to Watch."

    body = """Kevin Warsh was sworn in as chairman of the Federal Reserve on May 22. On Monday and Tuesday, he will lead his first meeting of the Federal Open Market Committee — the body that sets American interest rates, moves global capital flows, and, for the past three months, has had India's markets on a knife's edge.

The stakes for India and its diaspora are unusually high. Foreign investors have pulled a record $30 billion from Indian equities this year. The rupee has fallen six per cent. IT stocks have cratered. And the single biggest variable that could accelerate or reverse those trends sits in Warsh's hands.

## What the Market Expects

No rate change is expected at the June meeting. The federal funds rate sits at 3.75 per cent, and traders see the first potential move — a hike — not until December, with only a 43 per cent probability priced in. But the tone Warsh sets will matter far more than the decision itself.

US headline inflation came in at 4.2 per cent in May, the highest reading in three years. The labour market added its strongest monthly gains in over a year. Beth Hammack, the Cleveland Fed president and a voting FOMC member, said on June 2 that "the picture for inflation is not encouraging" and that "it may soon be appropriate to act" — widely interpreted as a call for a rate hike.

From the other side, White House senior adviser Peter Navarro warned the Fed against even thinking about raising rates.

## Warsh's Philosophy

Warsh has signalled a philosophical break from his predecessor Jerome Powell on at least two fronts. First, he is opposed to detailed forward guidance — the practice of signalling future rate moves in advance. "I want to assess the data as it comes in and reserve judgment meeting by meeting," he said during his April Congressional testimony. Markets should brace for less predictability.

Second, Warsh has argued that AI-driven productivity gains could allow the economy to grow without stoking inflation, a thesis that could justify holding rates steady even as headline numbers run hot. He has focused on "trimmed averages" — inflation measures that strip out one-off items like energy — rather than the headline rate that includes oil.

That matters enormously for India. Much of the current inflation is driven by energy costs from the Iran war — precisely the kind of "one-off" Warsh says he wants to look through.

## Why India Is Watching

The transmission mechanism from the Fed to India runs through multiple channels. Higher US rates pull capital out of emerging markets and into dollar-denominated assets, worsening the $30 billion foreign outflow India has already seen. They strengthen the dollar against the rupee, raising the cost of India's massive oil import bill. And they signal to the Reserve Bank of India that it has less room to cut its own rates to support growth.

India's IT sector — which earns the bulk of its revenue from American clients — is especially exposed. The Nifty IT index has fallen in seven straight sessions and is down 27 per cent this year. A rate hike would dampen US technology spending and deepen the rout.

On the other hand, if Warsh holds rates and strikes a dovish tone, the effect could be immediate. Oil prices have already crashed over 25 per cent from their peak on Iran deal hopes. If the Fed adds a tailwind of stable rates, the rupee could rally towards the 93-93.5 level that Kotak Mahindra Bank projects, and foreign investors could begin unwinding short positions on Indian equities.

## What NRIs Need to Know

For Indian Americans, the Fed meeting has direct personal implications. Mortgage rates, which have climbed above seven per cent this year, are unlikely to fall unless the Fed pivots. Savings rates at US banks remain attractive, but a hike could tighten credit and slow hiring in the tech sector that employs a disproportionate share of the Indian diaspora.

Meanwhile, the RBI has just launched an aggressive campaign to attract NRI dollars. Banks have hiked FCNR(B) deposit rates by up to 300 basis points — SBI is now offering up to six per cent, ICICI 6.5 per cent, and AU Small Finance Bank 7.1 per cent on three-to-five-year dollar deposits. The RBI is absorbing the full hedging cost, making these deposits risk-free in dollar terms. Experts estimate the scheme could pull in $60-70 billion.

The calculus for NRIs becomes: park money in a US savings account earning 4-5 per cent, or lock it in an Indian bank at 6-7 per cent with the central bank bearing the currency risk. The answer depends, in part, on what Warsh says next Wednesday."""
    
    article = {
        "headline": headline,
        "subheadline": "The new Fed chairman leads his first FOMC meeting on June 16 with US inflation at a three-year high, a possible Iran deal reshaping oil markets, and India's financial system hanging on every word.",
        "body": body,
        "slug": "kevin-warsh-first-fed-meeting-india-nri-impact-rates-inflation-20260612",
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": json.dumps([
            "Reuters — Wall St Week Ahead: Newly led Fed poses markets wildcard",
            "Barron's — Fed Chairman Warsh Gets Cover From the Bond Market",
            "FXStreet — U.S. economic outlook: The Warsh era starts with a great debate",
            "MarketWatch — Why a Fed communications blackout isn't coming under Warsh"
        ]),
        "diaspora_angle": "NRIs face a direct trade-off between US and Indian deposit rates, while the Fed's decision on rates will affect everything from mortgage costs and tech-sector hiring in America to the rupee and foreign outflows from India.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    
    return insert_article(article)

# ============================================================
# ARTICLE 3: BlackRock Says India Over-Punished
# ============================================================

def write_article_3():
    print("\n=== Article 3: BlackRock Says India Over-Punished ===")
    
    # Image sourcing — try Bombay Stock Exchange / NSE from Wikimedia
    commons = fetch_wikimedia_commons_images("Bombay Stock Exchange building Mumbai")
    img_url = None
    img_caption = "The Bombay Stock Exchange in Mumbai, where Indian benchmarks have fallen sharply in 2026"
    img_attribution = "Wikimedia Commons"
    
    if commons:
        for c in commons:
            if validate_image_url(c["url"]):
                img_url = c["url"]
                break
    
    if not img_url:
        # Try Wikipedia
        img_url = fetch_wikipedia_person_image("Bombay Stock Exchange")
        if img_url and validate_image_url(img_url):
            img_caption = "The Bombay Stock Exchange building in Mumbai"
        else:
            img_url = fetch_pexels_image("India stock market Mumbai financial district")
            img_caption = "India's financial district, where foreign investors have withdrawn a record $30 billion this year"
            img_attribution = "Pexels"
    
    headline = "Foreign Investors Have Pulled $30 Billion From India This Year. BlackRock Says the Selling Has Gone Too Far."

    body = """The numbers are hard to argue with. Foreign investors have yanked a record $30 billion out of Indian equities in 2026. The Sensex is down 13 per cent. The Nifty 50 has lost 11 per cent. India's total stock market capitalisation has slipped below that of Taiwan and South Korea for the first time — overtaken by two economies riding the AI semiconductor boom.

But the world's largest asset manager, which oversees more than $14 trillion, thinks the market has overcorrected.

## BlackRock's Thesis

In an interview with Reuters this week, Natasha Sarkaria, BlackRock's EMEA investment strategy lead, said India's equity market had been "over-punished" for two things: lacking a direct AI play and being exposed to higher oil prices from the Iran war.

Neither, she argued, changes India's medium-to-long-term investment case.

"As long as India's GDP grows between six and seven per cent, that's a nice sweet spot for the economy to keep growing, keep expanding," Sarkaria said. India's economy grew a stronger-than-expected 7.8 per cent in the March quarter.

BlackRock calls India one of its "highest-conviction, medium- to long-term emerging-market trades," supported by demographics, infrastructure investment, financial sector deepening, and what Sarkaria described as indirect AI-linked opportunities. The firm is "positioned constructively" on India, though not yet at an outright overweight.

## The Picks and Shovels Argument

The contrarian case is gaining allies. Abhay Laijawala, chief investment officer for India at Lighthouse Canton — a global wealth management firm with over $5 billion in assets — told Reuters on Friday that India's lack of direct AI exposure could prove to be an "advantage of absence."

His logic: Taiwan and South Korea have soared on semiconductor bets, but when sector concentration reaches extreme levels, investors tend to "fatally underprice" the risk of a disruption from outside the core business model. Both markets have already started logging foreign outflows in June as investors begin trimming crowded positions.

India, by contrast, offers what Laijawala calls "picks and shovels" — a listed universe of companies tied to the physical infrastructure that AI requires. Power generation, data centre construction, electrical equipment, cooling systems, engineering and capital goods. These are the companies that will build the server farms and supply the electricity, regardless of which AI model wins.

"We have plenty of picks and shovels," Laijawala said.

## The Other Side

The bulls have to contend with real headwinds. India's equity mutual fund inflows dropped 40 per cent month-on-month to $2.4 billion in May — the lowest in a year — as the Iran war and $100 oil crushed retail investor confidence. Small-cap, mid-cap and large-cap fund inflows all fell by roughly a third.

The IT sector, which accounts for a significant share of India's market weight, remains under severe pressure. The Nifty IT index has dropped 10.6 per cent in just seven sessions, battered by the dual threat of AI disruption and hot US inflation data that raises the prospect of a Fed rate hike later this year.

Brent crude, while down sharply on Friday to $87 on Iran deal hopes, has averaged well above $90 for most of 2026. If the proposed US-Iran memorandum falls through, oil could spike again, pushing India's import bill higher and widening its already-fragile current account deficit.

India is projected to post a balance-of-payments deficit for a record third consecutive year.

## What Could Turn It Around

Three catalysts could reverse the outflow tide. First, a signed Iran peace deal and the reopening of the Strait of Hormuz would slash oil prices and instantly improve India's fiscal and external balances. Markets rallied 2.3 per cent on Friday on deal hopes alone.

Second, the Reserve Bank of India has launched an aggressive dollar-attraction campaign, offering subsidised hedging on NRI deposits and easing overseas borrowing rules for banks. Analysts estimate the measures could draw in $60-70 billion.

Third, if the AI trade in Taiwan and South Korea begins to correct — and there are early signs it already is — global fund managers will need somewhere to redeploy capital. India, with its 7.8 per cent GDP growth and deep, diversified market, is the obvious candidate.

## The Diaspora Angle

For NRI investors with Indian equity portfolios, the question is straightforward: is this a bottom, or a trap? BlackRock and Lighthouse Canton are betting on the former. The record SIP inflows — $3.25 billion in May, essentially unchanged from April despite the carnage — suggest Indian retail investors agree.

The coming weeks will test the thesis. If the Iran deal holds and the Fed holds rates, the pieces are in place for a meaningful recovery. If either breaks, the $30 billion outflow becomes the floor, not the ceiling."""

    article = {
        "headline": headline,
        "subheadline": "India has lost more foreign investment in six months than in any full year on record. The world's largest asset manager says the AI panic and oil fear have masked the real story.",
        "body": body,
        "slug": "blackrock-india-over-punished-foreign-outflows-30-billion-ai-oil-20260612",
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": json.dumps([
            "Reuters — AI, oil worries have over-punished India, masked long-term investment case, BlackRock says",
            "Reuters — India likely past peak outflows, AI gap its advantage, Lighthouse Canton says",
            "Reuters — Iran war drags India equity mutual fund flows to one-year low in May",
            "Reuters — Indian shares post best day in two months on Mideast peace hopes"
        ]),
        "diaspora_angle": "NRI investors with Indian equity exposure face the core question: have markets bottomed after a record $30 billion outflow, or is more pain ahead? BlackRock's contrarian call and the RBI's NRI deposit sweeteners could shape the answer.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    
    return insert_article(article)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print(f"=== The Videshi News Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} ===")
    
    results = []
    for writer_fn in [write_article_1, write_article_2, write_article_3]:
        try:
            result = writer_fn()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            results.append(None)
    
    print(f"\n=== Summary ===")
    success = sum(1 for r in results if r is not None)
    print(f"Inserted {success}/{len(results)} articles with status='review'")
    
    if success == 0:
        sys.exit(1)
