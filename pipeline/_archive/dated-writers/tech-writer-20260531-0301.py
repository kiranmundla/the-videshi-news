#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-31 03:01 UTC run"""
import json, os, uuid, re, requests, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# Load env
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

def validate_image(url):
    """Check that an image URL returns HTTP 200 with image content > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD
        if r.status_code == 200 and "image" in ct:
            return True
    except:
        pass
    return False

# ─────────────────────────────────────────────────────────
# ARTICLE 1: Apple iOS 27 Siri overhaul / WWDC 2026
# ─────────────────────────────────────────────────────────

art1_body = """Apple's most ambitious software update in years will be unveiled at WWDC 2026 on June 8 — and it comes with an irony thick enough to cut with a butter knife. The new Siri, the centrepiece of iOS 27, will be powered substantially by Google's Gemini models. Which means Sundar Pichai's AI is about to become the brain inside Tim Cook's phone.

## The Overhaul

Leaked screenshots reported by Bloomberg this week reveal a Siri that bears almost no resemblance to the voice assistant iPhone users have tolerated for over a decade. The key changes:

A **standalone Siri app** with a ChatGPT-style chat interface, conversation history, text and voice input, and the ability to upload images and documents for analysis. No more ephemeral orb that forgets everything the moment you dismiss it.

**Dynamic Island integration** that gives Siri a persistent, animated presence at the top of the screen instead of the current full-screen takeover. Swipe down from the top centre anywhere to launch a new "Search or Ask" interface combining system search, app shortcuts, and AI queries in one hub.

**Third-party AI extensions** that let users route queries to ChatGPT, Claude, and — crucially — Gemini directly from within Siri. Apple is building a plug-in architecture that could make the iPhone the first device where competing AI assistants coexist under one roof.

## The Gemini Connection

The real story is under the hood. Apple and Google have reached a deal under which Gemini models will help power Apple Intelligence features, including the more personalised version of Siri. Apple has reportedly gained full access to Google's data centres to "distil" trillion-parameter models into smaller, efficient versions that can run locally on iPhones without an internet connection.

This is the "teacher-student" approach: Google's massive Gemini serves as the teacher, training compact student models optimised for Apple's A-series silicon. The result is a hybrid system — on-device processing for privacy, cloud fallback for complex queries — that attempts to close the gap with ChatGPT and Gemini's own Android offerings.

## Why This Matters to Indian Tech Workers

Start with the builders. Apple's engineering workforce in Cupertino includes thousands of Indian-origin engineers working on Apple Intelligence, Core ML, and Siri's natural language processing stack. The Gemini integration creates a new class of cross-company collaboration roles that Indian engineers at both Apple and Google are uniquely positioned to fill.

Then there's the Indian market. Apple sold an estimated 12 million iPhones in India in 2025, its fastest-growing major market. The new Siri's ability to handle complex queries and integrate with third-party AI services will be tested against a user base that's already fluent in Google Assistant and increasingly familiar with ChatGPT. Apple Intelligence features require an iPhone 15 Pro or newer — a price point that captures exactly the urban Indian professional demographic Apple has been courting with its growing retail presence in Mumbai and Delhi.

For Indian developers, the third-party AI extensions framework opens a genuinely new surface. If you're building an AI model or chatbot that serves Indian languages or enterprise use cases — think Sarvam AI, Krutrim, or any of India's growing crop of sovereign AI startups — you could theoretically plug into Siri. That's access to over a billion active Apple devices worldwide.

And the partnership dynamics are worth watching. Pichai's Google is simultaneously Apple's largest AI supplier, its biggest search revenue partner, and a direct competitor in hardware and AI assistants. The Gemini-Siri deal adds another layer to a relationship that already involves billions in annual search licensing fees. For Indian professionals navigating roles at either company, the strategic calculus just got more interesting.

WWDC 2026 kicks off June 8 at 10 a.m. Pacific. iOS 27 is expected to ship in September."""

art1_image = "https://images.pexels.com/photos/5083215/pexels-photo-5083215.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

# ─────────────────────────────────────────────────────────
# ARTICLE 2: Indian startup funding drought
# ─────────────────────────────────────────────────────────

art2_body = """Here is a number that should make every Indian tech founder stare at the ceiling: between 2022 and May 2026, the entire Indian startup ecosystem raised approximately $62 billion. Last week, Anthropic — a single company, founded in 2021, with roughly 1,500 employees — raised $65 billion in one round.

One startup. One cheque. More than four years of India. That is not a funding gap. That is a geological fault line.

## The Drought

Data compiled by YourStory shows that Indian startup VC funding for the last week of May 2026 came in at just $66 million across 16 transactions — the lowest weekly total of the year, and the fifth time this year that the number has dipped below $100 million. Not a single deal crossed $15 million.

India has produced 127 unicorns. But in the AI era, the capital is flowing elsewhere at a velocity that makes those numbers look quaint. Anthropic's Series H round, led by Altimeter Capital, Dragoneer, Greenoaks, and Sequoia Capital, valued the Claude-maker at $965 billion post-money — surpassing OpenAI's $852 billion March valuation. The company's annualised revenue has rocketed from $9 billion at end of 2025 to $47 billion this month.

## Where the Money Is Going

The concentration is staggering. Three companies — SpaceX ($1.8 trillion expected IPO valuation), OpenAI ($852 billion), and Anthropic ($965 billion) — are preparing public listings that could collectively raise more than all US venture-backed IPOs in the past decade combined. SpaceX's S-1 was filed on May 20 and aims to raise up to $75 billion in the largest IPO in history.

Meanwhile, India's AI startup roster — Sarvam AI, Krutrim, BharatGPT, Sarvam — is scratching for $250-350 million rounds. Sarvam's recently closed funding at a $1.5 billion valuation is India's largest AI raise ever. It is also 0.15 per cent of Anthropic's valuation. HCL Tech's $150 million investment in Sarvam was celebrated as a landmark moment for India's sovereign AI ambitions. Anthropic raised 433 times that amount in a single transaction.

## The NRI Investor's Dilemma

For Indian Americans with capital to deploy, the arithmetic creates a painful tension. The Nasdaq has returned roughly 40 per cent over the past year. INDmoney reports that searches for SpaceX on its platform surged tenfold after the S-1 filing. Indian retail investors cannot participate directly in US IPOs but can buy shares on listing day through platforms like INDmoney, Vested, and Groww.

The pull toward US AI mega-caps is rational. But it also means capital that might have flowed into Indian startups — through angel networks, NRI-focused VC funds, or the LRS route — is being redirected toward a handful of American AI companies. The structural issue is not that Indian startups lack ideas. It is that the AI arms race demands capital at a scale that Indian venture markets simply cannot match. Training a frontier model costs billions. The compute infrastructure required runs into tens of billions. India's entire IT services industry — $315 billion in export revenue — is dwarfed by the capital requirements of a single AI lab.

## What India Does Have

The picture is not entirely bleak. Sarvam's sovereign AI models, trained from scratch in 22 Indian languages with HCL Tech backing and Nvidia participation, represent a genuine attempt to build AI infrastructure tailored to India's linguistic reality. The company has expanded to San Francisco, not to abandon India but to absorb frontier knowledge and bring it home.

India's real advantage may not be in building frontier models at all. It may be in deployment — taking global AI models and applying them at the scale and linguistic diversity that no other market demands. That is a different business, and it may be the one India wins.

But for now, the numbers are the numbers. And they are sobering."""

art2_image = "https://images.pexels.com/photos/6899393/pexels-photo-6899393.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

# ─────────────────────────────────────────────────────────
# ARTICLE 3: SpaceX IPO — the NRI investor story
# ─────────────────────────────────────────────────────────

art3_image = fetch_wikipedia_person_image("Elon Musk")
if not art3_image or not validate_image(art3_image):
    art3_image = "https://images.pexels.com/photos/586061/pexels-photo-586061.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

art3_body = """SpaceX filed its S-1 with the SEC on May 20. The company is expected to price shares as early as June 11 and begin trading on the Nasdaq under the ticker SPCX on June 12. At a target valuation of $1.8 trillion, it will be the largest initial public offering in the history of capital markets — more than double Saudi Aramco's 2019 record.

For NRI investors in the US, this is not a spectator sport. Thirty per cent of the float is reserved for retail investors, three times the standard allocation for mega-cap IPOs. That is roughly $22.5 billion worth of shares available to individual buyers on day one, assuming the full $75 billion raise.

## What SpaceX Actually Is Now

The entity going public is no longer just a rocket company. In February 2026, SpaceX absorbed Elon Musk's AI startup xAI, creating a combined space-AI-telecommunications conglomerate valued at $1.25 trillion before the merger.

The revenue breakdown for 2025: Starlink satellite internet generated $11.4 billion (61 per cent of total revenue), achieving profitability on a GAAP basis for the first time. Launch services contributed $4.2 billion. The xAI division — Musk's answer to OpenAI — is burning roughly $2.5 billion per quarter but adds the AI narrative that investors are willing to pay a premium for.

Total 2025 revenue was $18.7 billion, but the company swung to a $4.94 billion net loss from a $791 million profit a year earlier, largely due to xAI's compute costs. The accumulated deficit stands at $41.3 billion. SpaceX completed 170 launches in 2025.

## The Indian Connection

Start with the workforce. SpaceX employs several thousand engineers of Indian origin across its Hawthorne, McGregor, and Starbase facilities. The company's propulsion, avionics, and software teams have significant Indian representation — many hired directly from US graduate programmes on OPT and H-1B visas.

Then there is Starlink. India has been one of the most contested markets for satellite broadband, with regulatory approval for Starlink delayed repeatedly over licensing requirements and data localisation rules. Jio's partnership with SES for satellite broadband and the Tata-OneWeb joint venture have created domestic alternatives. But SpaceX's global subscriber base of over 10 million — and its Direct-to-Cell technology partnership with T-Mobile — means Starlink's eventual Indian entry could reshape rural broadband economics for a country where 600 million people still lack reliable internet access.

For NRI investors, the IPO mathematics are worth examining carefully. Goldman Sachs is the lead underwriter, with Morgan Stanley, Bank of America, Citigroup, and JPMorgan Chase co-leading alongside 18 other banks. The roadshow begins June 4. SpaceX will list on both Nasdaq and Nasdaq Texas.

## The Risk Calculus

The bull case is Starlink's monopolistic positioning in satellite internet, Starship's potential to reduce launch costs by 10x, and xAI's frontier model ambitions using SpaceX's orbital data centre plans.

The bear case is historical. JPMorgan data shows that IPOs larger than $50 billion have produced median one-year losses of 31.9 per cent. The $1.8 trillion valuation implies a price-to-sales multiple of roughly 96 — making it one of the most expensive large-cap offerings ever. And xAI's quarterly burn rate threatens to offset Starlink's profitability for years.

Indian retail investors on platforms like INDmoney, Vested, and Groww can purchase shares on the listing date but cannot participate in the IPO allocation directly. The 30 per cent retail reserve applies to US-based retail investors, which includes NRIs with US brokerage accounts.

## What to Watch

The pricing window of June 11-12 coincides with Computex 2026 in Taipei, where Nvidia is expected to unveil its first Windows PC chip and detail its Vera Rubin AI platform. The convergence of SpaceX's listing with Nvidia's hardware announcements will create a week where the entire AI-and-infrastructure narrative gets repriced simultaneously.

For NRI tech workers sitting on RSUs from their FAANG employers and weighing whether to deploy capital into SpaceX, the decision comes down to a single question: do you believe Elon Musk can turn a money-losing AI lab and a rocket company into a $3 trillion integrated platform? The market is betting yes. History suggests caution."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple's Siri Is Getting a Brain Transplant. The Donor Is Sundar Pichai's Google.",
        "subheadline": "iOS 27 will feature a standalone Siri app, third-party AI extensions, and Gemini-powered intelligence. For Indian engineers at both companies, the partnership creates new territory.",
        "slug": make_slug("apple-siri-ios-27-gemini-google-wwdc-indian-engineers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Thousands of Indian engineers at Apple and Google are building the AI systems behind this partnership. The third-party extensions framework opens a new surface for Indian AI startups like Sarvam and Krutrim. Apple's fastest-growing market is India.",
        "tags": ["apple", "google", "gemini", "siri", "wwdc", "ios-27", "ai", "indian-engineers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg via MacRumors", "url": "https://www.macrumors.com/2026/05/29/ios-27-features-leaked/"},
            {"name": "Engadget", "url": "https://www.engadget.com/2026/05/28/apple-siri-overhaul-ios-27-wwdc/"},
            {"name": "Android Authority", "url": "https://www.androidauthority.com/apple-ios-27-gemini-siri/"},
            {"name": "LatestLY", "url": "https://www.latestly.com/technology/apple-gemini-iphone-siri-ios-27-wwdc-2026/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": art1_image,
        "body": art1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Startups Raised $62 Billion in Four Years. Anthropic Just Raised $65 Billion in One Round.",
        "subheadline": "Weekly VC funding into Indian startups hit its lowest point of 2026 at $66 million — as America's AI labs raise capital at a scale that makes India's entire ecosystem look like a rounding error.",
        "slug": make_slug("india-startup-funding-drought-anthropic-65-billion"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI investors are redirecting capital toward US AI mega-caps via INDmoney, Vested, and Groww. The funding gap raises hard questions about whether India can build frontier AI companies or should focus on deployment and application at scale.",
        "tags": ["indian-startups", "anthropic", "venture-capital", "funding", "ai", "sarvam-ai", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "YourStory", "url": "https://yourstory.com/2026/05/weekly-funding-roundup-may-2026-vc-lowest/"},
            {"name": "Investopedia", "url": "https://www.investopedia.com/anthropic-valuation-trillion-ipo-market/"},
            {"name": "Storyboard18", "url": "https://storyboard18.com/anthropic-world-most-valuable-ai-startup-965-billion/"},
            {"name": "LiveMint", "url": "https://www.livemint.com/companies/anthropic-965-billion-valuation-openai/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": art2_image,
        "body": art2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "SpaceX Is About to Stage the Largest IPO in History. Here's What NRI Investors Need to Know.",
        "subheadline": "A $1.8 trillion valuation, $75 billion raise, 30 per cent retail allocation, and a June 12 Nasdaq debut. The numbers are staggering — and so are the risks.",
        "slug": make_slug("spacex-ipo-largest-history-nri-investors-starlink"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "SpaceX employs thousands of Indian-origin engineers. NRIs with US brokerage accounts can access the 30% retail allocation. Starlink's eventual Indian entry could reshape rural broadband. INDmoney searches for SpaceX surged 10x after the S-1 filing.",
        "tags": ["spacex", "ipo", "elon-musk", "starlink", "nri-investors", "nasdaq", "xai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/spacex-ipo-explainer/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/spacex-ipo-valuation-1-8-trillion/"},
            {"name": "Motley Fool", "url": "https://www.fool.com/investing/2026/05/28/spacex-worth-more-than-tesla-ipo/"},
            {"name": "Inshorts", "url": "https://inshorts.com/spacex-openai-anthropic-ipo-indian-retail-investment/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": art3_image,
        "body": art3_body
    }
]

# Validate images
for art in articles:
    img = art.get("image_url", "")
    if img:
        valid = validate_image(img)
        print(f"Image validation for {art['slug']}: {'✓' if valid else '✗'} — {img[:60]}...")
    else:
        print(f"No image for {art['slug']}")

print()

# Insert articles
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
