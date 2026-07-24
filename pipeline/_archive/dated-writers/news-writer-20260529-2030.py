#!/usr/bin/env python3
"""News writer - 2026-05-29 20:30 UTC batch
Publishes 3 news articles with Wikipedia-first image sourcing.
"""

import json, os, sys, time, uuid, subprocess, urllib.parse, re
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────
def load_env(path):
    kv = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                kv[k.strip()] = v.strip().strip('"').strip("'")
    return kv

supabase_env = load_env(os.path.expanduser("~/.env.supabase"))
SUPABASE_URL = supabase_env.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", ""))
SUPABASE_KEY = supabase_env.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""))

pexels_env = load_env(os.path.expanduser("~/workspace/.env.pexels"))
PEXELS_KEY = pexels_env.get("PEXELS_API_KEY", "")

import requests

# ── Image sourcing ───────────────────────────────────────────────
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

def fetch_wikipedia_topic_image(topic):
    """Fetch image for a topic/concept from Wikipedia."""
    encoded = urllib.parse.quote(topic.replace(' ', '_'))
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
                print(f"  ✓ Wikipedia topic image for '{topic}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia topic API error for '{topic}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Use curl to avoid 403."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                photos = data.get("photos", [])
                if photos:
                    url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 with image content type and > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0") or "0")
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD; try GET
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            r2.close()
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def is_banned_url(url):
    """Check if URL is from a banned source."""
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com"]
    banned_params = ["_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            return True
    for p in banned_params:
        if p in url:
            return True
    return False

# ── Supabase publishing ──────────────────────────────────────────
def publish_article(article):
    """Publish an article to Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=headers,
        json=article,
        timeout=30
    )
    if r.status_code in [200, 201]:
        data = r.json()
        aid = data[0]["id"] if isinstance(data, list) and data else data.get("id", "unknown")
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {aid})")
        return True
    else:
        print(f"  ✗ Failed to publish: {r.status_code} — {r.text[:200]}")
        return False

# ── Articles ─────────────────────────────────────────────────────

def write_articles():
    now = datetime.now(timezone.utc).isoformat()
    articles = []

    # ═══════════════════════════════════════════════════════════════
    # ARTICLE 1: Delhi HC Google AdWords Trademark Ruling
    # ═══════════════════════════════════════════════════════════════
    print("\n📰 Article 1: Delhi HC Google AdWords Trademark Ruling")

    # Image: Try Google logo from Wikipedia, or Hindware, or Delhi High Court
    img1 = fetch_wikipedia_topic_image("Delhi High Court")
    if not img1 or not validate_image(img1):
        img1 = fetch_wikipedia_topic_image("Google Ads")
    if not img1 or not validate_image(img1):
        img1 = fetch_pexels_image("Delhi court building India", "Indian high court")
    if img1 and is_banned_url(img1):
        img1 = None
    if img1 and not validate_image(img1):
        img1 = None

    body1 = """A Delhi High Court ruling that found Google liable for trademark infringement by auctioning brand names as advertising keywords has set off a firestorm across India's business community — and the implications reach far beyond one bathroom fittings company.

Justice Mini Pushkarna's judgment, delivered on May 22 and now rippling through boardrooms and startup Slack channels alike, permanently restrained Google from using "Hindware" as an advertising keyword. The court ordered Google to pay nominal damages of Rs 30 lakh (roughly $31,600). The amount is small. The principle is enormous.

## What Google Was Doing

When someone in India typed "Hindware" into Google, the search giant's AdWords platform allowed rival companies — Cera Sanitaryware and Grohe India — to bid on that trademarked term as a keyword. Their ads would appear above or alongside Hindware's own results. Google earned pay-per-click revenue each time a consumer searching for Hindware was redirected to a competitor.

The court identified three specific ways Google actively participated: its Keyword Planner tool recommended competitors' trademarked terms to advertisers; it ran a real-time auction of those keywords; and it profited from every click that diverted traffic from the trademark owner.

## Why the Court Said This Is Not Just Facilitation

Google's primary defense was that keywords are invisible backend triggers — consumers never see the trademarked term in the ad itself — and therefore no trademark "use" occurs. The court rejected this comprehensively.

Under Section 29(6)(d) of the Trade Marks Act, 1999, use of a registered mark "in advertising" without consent constitutes infringement. The court held that diverting search traffic itself qualifies as advertising use, regardless of whether the mark visually appears in the ad. Justice Pushkarna drew an analogy to meta-tags — hidden HTML code used to hijack search traffic in earlier cases — and applied the same legal logic.

More significantly, the court ruled that Google is not a passive intermediary entitled to safe harbour protection under Section 79 of the Information Technology Act. The judge found that Google's algorithm "selects the receiver of the transmission" and has "aided and abetted" the infringement through its Keyword Planner and auction infrastructure.

## The Double Standard

Perhaps the most damning finding: Google's own witness confirmed in cross-examination that until 2009, the company did not permit trademarked terms as keywords at all. When it changed its global policy, it continued to investigate trademark complaints in the European Union and the European Economic Area — but explicitly declined to do so in India.

The court found this to be a deliberate, revenue-driven deviation. Google estimated in 2009 that allowing trademark keyword bidding would generate at least $100 million in incremental revenue globally. India's trademark owners were, in effect, subsidizing that growth without their consent.

## Why Indian Business Leaders Are Celebrating

The response from India's tech and startup ecosystem has been swift. Nithin Kamath, founder of Zerodha, India's largest brokerage, said his brand had suffered from this practice for years and that the ruling "now opens up a route for legal recourse."

Anupam Mittal, founder of Shaadi.com, framed it bluntly: "You create the brand. Someone else bids on it. Google takes the fee. This ruling could change the economics of online advertising for millions of businesses."

## What This Means for NRI-Founded Businesses

For the Indian diaspora running brands with Indian market exposure, this ruling has immediate practical implications. Any NRI entrepreneur whose registered Indian trademark is being bid on by competitors as a Google Ads keyword now has legal standing to sue both the competitor and Google.

The ruling effectively forces Google to adopt its EU-standard trademark protection policies in India — something it had refused to do voluntarily for over a decade. Until now, Indian trademark owners had to outbid competitors for their own brand names just to appear first in search results for their own products.

## What Happens Next

Google has not responded to requests for comment. The company counts India as one of its most critical markets. An appeal is likely, but the immediate precedent is set: platforms that algorithmically determine who receives information and profit from that determination cannot claim they are merely passive pipes.

The ruling's reasoning — that Section 79 safe harbour does not protect platforms that actively shape commercial outcomes — could extend well beyond keyword advertising to ad targeting, content recommendation, sponsored posts, and search ranking across India's digital economy."""

    article1 = {
        "headline": "Delhi High Court Just Ruled That Google Cannot Sell Your Brand Name to Your Competitors",
        "subheadline": "The Hindware judgment strips Google of safe harbour protection and establishes that auctioning trademarks as ad keywords constitutes infringement — a ruling that Indian founders from Zerodha to Shaadi.com are calling a turning point.",
        "body": body1,
        "slug": "delhi-hc-google-hindware-trademark-keyword-ads-ruling-infringement-20260529",
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": now,
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "MediaNama", "url": "https://www.medianama.com/2026/05/223-delhi-hc-google-hindware-trademark-keywords/"},
            {"name": "Bar and Bench", "url": "https://www.barandbench.com"},
            {"name": "LiveLaw", "url": "https://www.livelaw.in"}
        ]),
        "image_url": img1 or "",
        "image_attribution": "Wikimedia Commons" if img1 and "wikimedia" in (img1 or "").lower() else ("Pexels" if img1 and "pexels" in (img1 or "").lower() else "")
    }
    articles.append(article1)

    # ═══════════════════════════════════════════════════════════════
    # ARTICLE 2: RBI Digital Rupee Expansion
    # ═══════════════════════════════════════════════════════════════
    print("\n📰 Article 2: RBI Digital Rupee Expansion")

    img2 = fetch_wikipedia_topic_image("Reserve Bank of India")
    if not img2 or not validate_image(img2):
        img2 = fetch_wikipedia_topic_image("Indian rupee")
    if not img2 or not validate_image(img2):
        img2 = fetch_pexels_image("Reserve Bank of India building Mumbai", "Indian currency digital")
    if img2 and is_banned_url(img2):
        img2 = None
    if img2 and not validate_image(img2):
        img2 = None

    body2 = """The Reserve Bank of India just revealed plans to expand the digital rupee into welfare payments and cross-border transactions with Singapore and the UAE — two countries where millions of Indians live and work. The announcement, buried in the RBI's 2025-26 annual report released on Friday, could reshape how Indian families send and receive money across borders.

## What the RBI Is Actually Building

The central bank has been running digital rupee pilots across multiple states during the fiscal year that ended in March. In Gujarat, Puducherry, and Chandigarh, welfare beneficiaries received food subsidies through the digital rupee — a direct government-to-citizen payment that bypasses the banking intermediaries that typically slow down or tax these transfers.

"Multiple government agencies commenced pilots in various direct benefit transfer schemes leveraging programmability feature of CBDC to ensure productive utilisation of public funds," the RBI stated.

The keyword is "programmability." Unlike a regular UPI payment, a digital rupee can be coded to work only for specific purposes — food, medicine, education — ensuring welfare payments reach their intended use. This is not theoretical anymore. It is running in at least ten pilot programs across India.

## The Cross-Border Play That Matters for NRIs

For the 18 million Indians living in the Gulf and Southeast Asia, the more consequential news is the cross-border piece. The RBI has signed a digital assets pact with Singapore's Monetary Authority and is in active discussions for pilot projects with both Singapore and the UAE.

If these pilots succeed, the implications for remittances are profound. India received $129 billion in remittances in fiscal year 2025, making it the world's largest recipient. Currently, sending money from Dubai or Singapore to India involves correspondent banking chains that charge 3-7% in fees and take one to three days. A CBDC-to-CBDC settlement could theoretically happen in seconds at near-zero cost.

The UAE connection is particularly significant. The Emirates are home to roughly 3.5 million Indian expatriates who collectively send billions of dollars home each year. A direct digital rupee-to-digital dirham settlement mechanism would cut out Western Union, Wise, and every middleman in between.

## The Paradox: Usage Is Falling

Here is the awkward part the RBI would rather you did not notice. Retail digital rupee circulation actually fell during the year — dropping to Rs 771 crore (roughly $81 million) as of March 31, 2026, down from Rs 1,016 crore a year earlier. That is a 24% decline.

The drop suggests that despite the pilot programs, everyday Indians are not adopting the e-rupee for regular transactions. UPI, which processed 16.6 billion transactions in March 2026 alone, remains the dominant digital payment rail. The digital rupee has to offer something UPI cannot — and cross-border payments may be exactly that differentiator.

## India's Cloud-First Central Bank

Separately, the RBI disclosed that its cloud platform for financial firms went live in beta mode with nine users — making it among the first central banks globally to offer cloud infrastructure to regulated entities. The Indian Financial Sector (IFS) cloud's Phase I covers basic services, with Phase II planned for advanced capabilities.

This is the less glamorous but potentially more impactful development. If India's banks and financial institutions migrate to an RBI-operated cloud, it creates a unified infrastructure layer that makes CBDC interoperability, real-time fraud detection, and cross-border settlement far more feasible at scale.

## The BRICS Angle

The digital rupee expansion does not exist in isolation. Earlier this year, the RBI recommended placing a BRICS-wide CBDC bridge on the formal agenda for the 2026 BRICS summit, which India is hosting. The proposal envisions linking sovereign digital currencies — including the digital rupee and China's digital yuan — within a shared multilateral framework, enabling direct trade settlements without routing through dollar-based correspondent banking.

## What This Means in Practice

For NRIs in the Gulf and Singapore, the practical impact is still a year or more away. Pilot projects need to scale, regulatory frameworks need alignment across jurisdictions, and the legacy banking industry has every incentive to slow-walk adoption.

But the direction is unmistakable. India's central bank is building the plumbing for a world where sending money home from Abu Dhabi or Singapore costs almost nothing and arrives instantly. In a country that runs on remittances, that is not a minor upgrade. It is a structural change in how the diaspora's money moves."""

    article2 = {
        "headline": "The RBI Just Revealed Plans to Let NRIs Send Money Home Through the Digital Rupee",
        "subheadline": "India's central bank has signed pacts with Singapore and the UAE to pilot cross-border digital rupee payments — a move that could eliminate the fees and delays that cost the diaspora billions every year.",
        "body": body2,
        "slug": "rbi-digital-rupee-cbdc-cross-border-singapore-uae-nri-remittances-20260529",
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": now,
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
            {"name": "RBI Annual Report 2025-26", "url": "https://www.rbi.org.in"},
            {"name": "Crypto.news", "url": "https://crypto.news"}
        ]),
        "image_url": img2 or "",
        "image_attribution": "Wikimedia Commons" if img2 and "wikimedia" in (img2 or "").lower() else ("Pexels" if img2 and "pexels" in (img2 or "").lower() else "")
    }
    articles.append(article2)

    # ═══════════════════════════════════════════════════════════════
    # ARTICLE 3: Pernod Ricard Blocked from Delhi
    # ═══════════════════════════════════════════════════════════════
    print("\n📰 Article 3: Pernod Ricard Blocked from Delhi")

    img3 = fetch_wikipedia_person_image("Pernod Ricard")
    if not img3 or not validate_image(img3):
        img3 = fetch_wikipedia_topic_image("Chivas Regal")
    if not img3 or not validate_image(img3):
        img3 = fetch_wikipedia_topic_image("Absolut Vodka")
    if not img3 or not validate_image(img3):
        img3 = fetch_pexels_image("whisky bottles bar Delhi", "liquor store India")
    if img3 and is_banned_url(img3):
        img3 = None
    if img3 and not validate_image(img3):
        img3 = None

    body3 = """If you have tried to buy a bottle of Absolut Vodka or Chivas Regal in New Delhi recently, you already know something is wrong. You cannot find them. You have not been able to find them for three years. And after Friday's Delhi High Court ruling, you still will not.

Justice Purushaindra Kumar Kaurav dismissed French liquor giant Pernod Ricard's plea to resume sales in the national capital, ruling that the company's "criminal background" — stemming from an ongoing investigation, not a conviction — makes it ineligible for a licence under Delhi's excise rules.

## The Three-Year Exile

Pernod Ricard has not sold a single bottle in Delhi since 2023. The ban traces back to the now-scrapped 2021 Delhi liquor policy — the same case that sent former Deputy Chief Minister Manish Sisodia to jail and became one of the most politically charged investigations in recent Indian history.

The Enforcement Directorate, India's federal financial crime agency, accuses Pernod of colluding with certain Delhi retailers to illegally boost its market share during the 2021 policy period. The company denies the allegations. No charges have been framed. No trial has begun. No conviction exists.

Pernod argued before the court that it has an unblemished three-decade track record in India and that denying a licence based on a pending investigation — without even charges being framed — "inverts the presumption of innocence."

The court disagreed. Justice Kaurav held that the pendency of the investigation itself gives Pernod a "criminal background" under the applicable New Delhi municipal regulations, which is sufficient grounds to deny a licence.

## India Is Pernod's Biggest Market

This is not a peripheral market problem for Pernod Ricard. India is the French company's largest market globally by volume, with sales of approximately $2.9 billion last year. Delhi alone used to contribute roughly 5% of countrywide sales before the ban — a significant chunk for a single city.

The Delhi market is also a showcase. It is where diplomats, politicians, and the business elite shop. Being absent from Delhi's shelves for three years is not just a revenue problem; it is a brand visibility problem in India's most politically connected city.

## The $314 Million Tax Bomb

The licence rejection is not Pernod's only Indian headache. The company is simultaneously battling a demand from Indian tax authorities to pay $314 million in back taxes on some of its Scotch whisky imports.

Investigators concluded that Pernod understated the value of certain Scotch imports by not fully disclosing age and composition details, leading to lower import duties. With penalties, the total exposure could exceed $600 million if the company loses.

Meanwhile, Pernod also faces antitrust scrutiny in India. The combination of a three-year sales ban in the capital, a $314 million tax dispute, and antitrust proceedings represents an unprecedented regulatory assault on a single foreign company in India's alcohol market.

## What This Means for NRIs Visiting Delhi

For diaspora Indians who return to Delhi for family visits, weddings, or business, the practical impact is visible: walk into any liquor store in Delhi and you will notice the gaps. No Absolut. No Chivas. No Glenlivet. No Jameson. No Beefeater. The entire Pernod Ricard portfolio — which also includes Royal Salute, Ballantine's, and Malibu — is simply unavailable.

Delhi's estimated $65 billion alcohol industry is India's most lucrative, and the absence of one of the world's two largest spirits companies (the other being Diageo, whose Indian arm United Spirits operates unimpeded) has created an unusual market distortion.

## The Bigger Picture

The Pernod case has become a test of how India's regulatory apparatus treats foreign companies caught in domestic political investigations. The company was not the primary target of the Delhi liquor policy probe — that distinction belongs to political figures. But it has borne the commercial consequences more heavily than any other party.

For global businesses watching India, the message is complicated. On one hand, India's courts enforce rules impartially, applying the same eligibility criteria regardless of a company's size or origin. On the other, a company can lose access to a market worth hundreds of millions in annual revenue based on an investigation where charges have not even been framed.

Pernod Ricard has not yet commented on the ruling. An appeal to a higher court is expected. But as the ban enters its fourth year, the question is no longer just legal — it is whether one of the world's largest spirits companies can afford to keep waiting."""

    article3 = {
        "headline": "Absolut Vodka and Chivas Regal Are Banned in Delhi. The Court Just Said They Will Stay Banned.",
        "subheadline": "Delhi High Court rejected Pernod Ricard's plea to resume sales in the capital, extending a three-year exile rooted in a liquor policy investigation where charges have never been framed.",
        "body": body3,
        "slug": "pernod-ricard-delhi-hc-licence-rejected-absolut-chivas-banned-20260529",
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": now,
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "LiveLaw", "url": "https://www.livelaw.in"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
            {"name": "IANS", "url": "https://ianslive.in"}
        ]),
        "image_url": img3 or "",
        "image_attribution": "Wikimedia Commons" if img3 and "wikimedia" in (img3 or "").lower() else ("Pexels" if img3 and "pexels" in (img3 or "").lower() else "")
    }
    articles.append(article3)

    return articles

# ── Main ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — News Writer (2026-05-29 20:30 UTC)")
    print("=" * 60)

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("✗ Missing Supabase credentials")
        sys.exit(1)

    articles = write_articles()

    print(f"\n{'=' * 60}")
    print(f"Publishing {len(articles)} articles...")
    print(f"{'=' * 60}")

    success = 0
    for i, article in enumerate(articles, 1):
        print(f"\n[{i}/{len(articles)}] {article['headline'][:60]}...")
        if article.get("image_url"):
            print(f"  Image: {article['image_url'][:80]}...")
        else:
            print("  ⚠ No image — publishing without image")
        if publish_article(article):
            success += 1

    print(f"\n{'=' * 60}")
    print(f"Done: {success}/{len(articles)} articles published successfully")
    print(f"{'=' * 60}")
