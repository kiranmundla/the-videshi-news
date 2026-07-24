#!/usr/bin/env python3
"""Technology writer for The Videshi — 2026-07-13 14:00 PT run."""

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

# ── Image sourcing helpers ──

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
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                url = ii.get("thumburl") or ii.get("url", "")
                results.append({"url": url, "title": page.get("title", ""), "width": ii.get("width", 0)})
            return sorted(results, key=lambda x: x["width"], reverse=True)
    except Exception as e:
        print(f"  ⚠ Commons search error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for a relevant image. Returns URL or None."""
    pexels_env = Path.home() / "workspace/.env.pexels"
    pexels_key = None
    if pexels_env.exists():
        for line in pexels_env.read_text().strip().splitlines():
            if "PEXELS_API_KEY" in line and "=" in line:
                pexels_key = line.split("=", 1)[1].strip()
    if not pexels_key:
        pexels_key = os.environ.get("PEXELS_API_KEY")
    if not pexels_key:
        print("  ⚠ No Pexels API key found")
        return None
    try:
        import subprocess
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5",
             "-H", f"Authorization: {pexels_key}"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("large")
                print(f"  ✓ Pexels image found: {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

# ── Source images ──

print("Sourcing images...")

# Article 1: HCLTech — try C. Vijayakumar (CEO), then HCLTech campus
img1 = fetch_wikipedia_person_image("C. Vijayakumar")
img1_caption = "C. Vijayakumar, CEO and Managing Director of HCLTech"
img1_attr = "Wikimedia Commons"
if not img1:
    img1 = fetch_wikipedia_person_image("HCL Technologies")
    img1_caption = "HCL Technologies headquarters"
    if not img1:
        commons = fetch_wikimedia_commons_images("HCL Technologies Noida")
        if commons:
            img1 = commons[0]["url"]
            img1_caption = "HCL Technologies office campus"
        else:
            img1 = fetch_pexels_image("corporate office building technology India")
            img1_caption = "Corporate technology office"
            img1_attr = "Pexels"

# Article 2: Bhavin Turakhia
img2 = fetch_wikipedia_person_image("Bhavin Turakhia")
img2_caption = "Bhavin Turakhia, serial entrepreneur and founder of Neo"
img2_attr = "Wikimedia Commons"
if not img2:
    commons2 = fetch_wikimedia_commons_images("Bhavin Turakhia entrepreneur")
    if commons2:
        img2 = commons2[0]["url"]
    else:
        img2 = fetch_pexels_image("AI workplace office futuristic technology")
        img2_caption = "AI-powered workplace technology"
        img2_attr = "Pexels"

# Article 3: Indian IT stocks rally — BSE/NSE building or stock exchange
img3 = fetch_wikipedia_person_image("Bombay Stock Exchange")
img3_caption = "The Bombay Stock Exchange building in Mumbai"
img3_attr = "Wikimedia Commons"
if not img3:
    commons3 = fetch_wikimedia_commons_images("Bombay Stock Exchange building")
    if commons3:
        img3 = commons3[0]["url"]
        img3_caption = "The Bombay Stock Exchange, home to the Sensex"
    else:
        img3 = fetch_pexels_image("Indian stock exchange financial market trading")
        img3_caption = "Financial market trading floor"
        img3_attr = "Pexels"

print(f"\nImage 1 (HCLTech): {img1}")
print(f"Image 2 (Turakhia): {img2}")
print(f"Image 3 (IT Rally): {img3}")

# ── Articles ──

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "HCLTech Just Beat Estimates on Every Metric That Matters. Its AI Revenue Hit $171 Million.",
        "subheadline": "India's third-largest IT firm posted 20% profit growth, booked $2.4 billion in new deals, and is quietly building one of the sector's fastest-growing AI practices.",
        "slug": make_slug("hcltech-q1-earnings-beat-ai-revenue-171-million"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "HCLTech employs over 220,000 people, sponsors thousands of H-1B visas in the United States, and is a bellwether for the Indian IT sector that millions of NRI investors track closely.",
        "tags": ["hcltech", "indian-it", "earnings", "ai-revenue", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-hcltech-beats-first-quarter-revenue-estimates-2026-07-13/"},
            {"name": "HCLTech Investor Relations", "url": "https://www.hcltech.com/investors"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img1 or "",
        "image_caption": img1_caption,
        "image_attribution": img1_attr,
        "body": """When HCLTech reported its April-June quarter results on Monday evening, the numbers told a story the market had been waiting to hear: India's third-largest IT services firm is not just surviving the AI upheaval — it is starting to profit from it.

Revenue rose 13.94% year-on-year to ₹345.79 billion ($3.62 billion), comfortably clearing analyst estimates of ₹343.5 billion. Net profit surged 20.3% to ₹46.24 billion, again beating the Street's ₹45.12 billion consensus. In constant currency terms — stripping out the rupee's roughly 9% depreciation against the dollar during the quarter — growth was a more modest but still respectable 2.6%.

## The AI Line Item Everyone Is Watching

The number that will draw the most scrutiny is HCLTech's "advanced AI revenue" — a metric the company uses to track income derived exclusively from services like agentic AI implementation, AI engineering, and model deployment. It climbed to $171 million for the quarter, up from $155 million in the prior three months.

That figure is smaller than TCS's annualised $2.6 billion in AI revenue, but HCLTech is measuring something narrower: only the revenue that comes from building and deploying AI systems for clients, not the broader category of "AI-influenced deals" that TCS counts. It is a cleaner metric, and the trajectory matters. A quarter-on-quarter jump of roughly 10% suggests enterprise demand for AI engineering services is accelerating, not flattening.

## Bookings Tell the Forward Story

New deal bookings came in at $2.4 billion, a sharp uptick from $1.9 billion in the prior quarter and $1.8 billion a year ago. For a company whose stock has been battered — down alongside the broader Nifty IT index, which has shed nearly 23% in 2026 — the bookings pipeline is the strongest counterargument to the bear case.

The strength was concentrated in financial services, technology, and retail, the segments where enterprises are actively spending on digital transformation and AI integration. Healthcare and manufacturing, the segments that have been sluggish across the industry, remain a drag but not a crisis.

## What It Means for Indian IT Workers

HCLTech currently employs over 220,000 people. It is one of the largest sponsors of H-1B visas in the United States and a major employer of Indian engineers in offices from Noida to New Jersey. For the tens of thousands of professionals whose careers are tied to Indian IT firms, the earnings signal matters: the company is hiring, it is winning deals, and it is investing in AI capabilities that should create new roles even as older ones get automated.

This follows TCS's own revenue beat last week, when India's largest IT firm reported 14% revenue growth and announced plans to build a team of up to 8,900 forward-deployed AI engineers. Together, the two results are the strongest evidence yet that India's $315 billion IT industry is navigating the AI transition better than the stock market has been pricing in.

## The Bigger Picture

Shares of HCLTech rose 4.9% on Monday ahead of the results, part of a broader 3.6% surge in the Nifty IT index — its best single-day performance in a month. The rally was fuelled by HCLTech's anticipated beat, TCS's new multi-million-dollar contract with Swiss-Swedish industrial giant ABB, and LTIMindtree's partnership with Anthropic to accelerate enterprise adoption of Claude.

For NRI investors, the sector presents a familiar conundrum. Indian IT stocks have been punished mercilessly in 2026 on fears that AI will cannibalise outsourcing revenues. But the earnings are telling a different story — one where AI is creating new revenue streams, not destroying old ones. The Nifty IT index is up 10.3% in July alone, its sharpest monthly recovery in over a year.

The question is whether this is a dead-cat bounce or the start of a genuine re-rating. HCLTech's $2.4 billion in new bookings and $171 million in AI revenue suggest the answer is tilting toward the latter.

*HCLTech is scheduled to report detailed segmental results and host its analyst call later this week.*"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Founder Who Built a $2 Billion Fintech Just Bet $30 Million on an AI Workplace That Could Replace Slack and Notion",
        "subheadline": "Bhavin Turakhia, the serial entrepreneur behind Zeta and Directi, has launched Neo — an AI-native platform where agents work alongside employees. It is part of a broader shift: India's most successful founders are going back to building, and this time the product is AI itself.",
        "slug": make_slug("bhavin-turakhia-neo-ai-workplace-30-million"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Turakhia is part of a growing cohort of Indian-origin entrepreneurs building globally competitive AI products. For NRI professionals, Neo represents a new class of workplace tools that could reshape how distributed teams — including the US-India corridors that define modern tech work — operate.",
        "tags": ["bhavin-turakhia", "neo", "ai-startup", "workplace-ai", "indian-entrepreneur"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inc42", "url": "https://inc42.com/features/unicorn-founders-go-ai-native/"},
            {"name": "YourStory", "url": "https://yourstory.com/2026/07/bhavin-turakhia-launches-ai-native-work-platform-neo-30m-investment"},
            {"name": "TechCircle", "url": "https://www.techcircle.in/2026/07/03/bhavin-turakhia-bets-30-mn-on-neo-says-enterprises-need-ai-native-work-platforms"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img2 or "",
        "image_caption": img2_caption,
        "image_attribution": img2_attr,
        "body": """Bhavin Turakhia does not do small bets. The 44-year-old Mumbai-born entrepreneur sold his first company, Directi's web businesses, for $160 million. He built Titan, a communications platform valued at $300 million after Automattic invested. And Zeta, the SoftBank-backed fintech he co-founded, sits at a $2 billion valuation. Now Turakhia has committed $30 million of his own money — the largest personal investment of his career — to a new venture called Neo, and his thesis is blunt: the way enterprises use AI today is fundamentally broken.

"Most organisations fail to capture the value of AI because context is fragmented, knowledge is scattered across teams, and tools remain disconnected," Turakhia said in a post announcing the launch. "Neo changes that by centralising context and making AI a first-class participant in every workflow, not a tab beside it."

## What Neo Actually Does

Neo is not another chatbot bolted onto a project management tool. The platform is built from scratch as what Turakhia calls an "AI-native" workspace — one where AI agents are not assistants summoned by a slash command, but persistent collaborators with access to the organisation's entire knowledge base.

The suite has four components. **Friday** is the AI assistant and agent layer, integrated with over 1,000 external applications. **Tasket** handles project management and allows users to delegate tasks directly to AI agents. **Studio** is a knowledge management workspace for documents, spreadsheets, and diagrams. And **Drive** is a collaborative file-sharing layer where both employees and AI agents can work on shared files.

The ambition is to replace the patchwork of Slack, Notion, Asana, and Google Drive that most companies use today — not by replicating their features with an AI wrapper, but by rebuilding the entire workflow around the assumption that AI is a co-worker, not a tool.

## Built by 20 Engineers in Three Months

What makes Neo unusual is how it was built. Turakhia told TechCircle that a team of fewer than 20 engineers built the platform in under three months — a timeline that would have been unthinkable through conventional development. The irony is deliberate: a company selling AI-powered productivity was itself built using AI-powered productivity.

Neo is currently in early access and hiring across frontend, backend, UX, and data science roles. Financial details beyond Turakhia's $30 million personal commitment have not been disclosed, and the company has not announced external fundraising.

## The Bigger Trend: Unicorn Founders Go AI-Native

Turakhia is not alone. As Inc42 documented this week, India's most successful startup founders are returning to building — and this time, the product is AI itself.

The pattern is striking. Entrepreneurs who helped India embrace smartphones, digital payments, and e-commerce over the past decade are now pivoting to AI-first ventures. The names are familiar; the businesses are not. Ola founder Bhavish Aggarwal launched Krutrim, an AI company now valued at over $1 billion. Zerodha's Nithin Kamath has been investing in AI-native financial tools. And a wave of less-visible but well-funded founders are building everything from AI coding assistants to autonomous supply chain agents.

What connects them is a shared conviction that the AI opportunity is not in adding copilots to existing software — it is in rebuilding entire product categories from the ground up, with AI as the architectural foundation rather than a feature.

## Why NRIs Should Pay Attention

For Indian-origin professionals working across US-India corridors, Neo represents something more than another SaaS product. The platform is designed for the kind of distributed, knowledge-intensive work that defines the modern NRI professional experience — teams split across time zones, context scattered across a dozen tools, institutional knowledge locked in people's heads rather than systems.

If Turakhia's thesis is correct — that AI-native platforms will eventually replace the current stack of disconnected productivity tools — then Neo and its competitors could reshape how the millions of Indian engineers, consultants, and executives who work across borders actually get their work done.

The $30 million question is whether a platform built for AI-first workflows can unseat the incumbents that most enterprises have already bought, integrated, and habituated around. Turakhia's track record suggests it is a bet worth watching."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian IT Stocks Just Posted Their Best Day in a Month. The $315 Billion Sector's AI Pivot Is Starting to Work.",
        "subheadline": "The Nifty IT index surged 3.6% on Monday as TCS, HCLTech, and LTIMindtree all rallied on a wave of AI partnership deals and better-than-expected earnings. After a brutal 23% decline in 2026, July has seen a 10.3% rebound.",
        "slug": make_slug("indian-it-stocks-rally-ai-partnerships-july"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Millions of NRI investors hold Indian IT stocks. Tens of thousands of Indian engineers work at TCS, Infosys, HCLTech, and LTIMindtree on H-1B visas. The sector's fortunes directly shape both investment portfolios and career trajectories for the diaspora.",
        "tags": ["indian-it", "nifty-it", "tcs", "hcltech", "ltimindtree", "ai-partnerships", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-shares-fall-amid-middle-east-concerns-2026-07-13/"},
            {"name": "Reuters — TCS ABB Deal", "url": "https://www.reuters.com/world/india/indias-tcs-bags-multi-million-contract-industrial-giant-abb-2026-07-13/"},
            {"name": "Reuters — HCLTech Q1", "url": "https://www.reuters.com/world/india/indias-hcltech-beats-first-quarter-revenue-estimates-2026-07-13/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img3 or "",
        "image_caption": img3_caption,
        "image_attribution": img3_attr,
        "body": """On a day when global markets were rattled by renewed hostilities between the United States and Iran — Tehran said it had again closed the Strait of Hormuz after exchanging heavy missile and drone strikes with American forces — Indian IT stocks staged their sharpest rally in a month.

The Nifty IT index surged 3.6% to a one-month high. TCS jumped 5.4%. HCLTech rose 4.9% ahead of its evening earnings release. LTIMindtree gained 2.2%. The broader benchmarks — the Nifty 50 and BSE Sensex — barely budged, recovering from a nearly 1% intraday drop to close flat. IT was the sector that saved the tape.

## What Triggered the Rally

Three catalysts converged in a single session.

First, TCS announced a multi-million-dollar contract with Swiss-Swedish industrial technology giant ABB to design and run ABB's global network ecosystem as an AI-driven service. The deal extends a 20-year partnership where TCS had previously consolidated ABB's accounting systems onto a single SAP platform. It is the kind of AI-era managed services contract that bulls have been arguing would replace the traditional outsourcing revenue that AI threatens to erode.

Second, LTIMindtree — the Larsen & Toubro subsidiary that is India's fifth-largest IT firm — announced a partnership with Anthropic to accelerate enterprise adoption of Claude, the AI model that has captured significant market share in coding and enterprise applications. The deal adds LTIMindtree to a growing list of Indian IT firms that have secured partnerships with frontier AI labs.

Third, sentiment was already improving after TCS beat quarterly revenue expectations last week, reporting 14% revenue growth and announcing plans to hire up to 8,900 forward-deployed AI engineers.

## The Scorecard: Every Major Indian IT Firm Now Has an AI Lab Partner

The LTIMindtree-Anthropic deal completes a remarkable sweep. Over the past four months, virtually every major Indian IT services company has secured a strategic partnership with a frontier AI lab:

- **TCS**: Global Premier Partner with Anthropic (June 2026). Dedicated Claude business unit, 50,000 employees licensed for Claude.
- **Infosys**: Enterprise AI collaboration with Anthropic (June 2026). Claude deployed across telecom, financial services, and manufacturing use cases.
- **HCLTech**: Partnerships with both OpenAI and Microsoft for enterprise AI deployment.
- **LTIMindtree**: Anthropic partnership to accelerate Claude adoption (July 2026).
- **Wipro**: AI partnerships with multiple labs, including integration work on Microsoft Copilot.
- **Accenture**: Dedicated Anthropic Business Group with 30,000 Claude-trained professionals.

The logic is straightforward. AI labs build models; they do not deploy them into the messy reality of enterprise IT environments with legacy systems, regulatory constraints, and thousands of users. Indian IT firms have the engineering bench strength, client relationships, and operational discipline to do that deployment work. In a world where AI adoption is moving from pilots to production, that is valuable.

## The Bear Case Is Not Dead

"What we are seeing in the IT sector is more of trading and tactical calls in beaten-down stocks rather than a structural buy call," Dharmesh Kant, head of equity research at Cholamandalam Securities, told Reuters on Monday.

The scepticism is not unfounded. Indian IT stocks are still down nearly 23% for the year. Analysts have lowered expectations for the entire $315 billion industry as clients cut non-essential tech spending and AI tools promise to shorten project timelines — meaning fewer billable hours for outsourcing firms. TCS's own annualised AI revenue of $2.6 billion, while growing, saw its sequential growth rate slow from 28% to 13% in the June quarter. The definition of "AI revenue" remains fuzzy across the industry.

And there is the existential question that no amount of partnership announcements can fully answer: if AI makes software development dramatically cheaper and faster, do enterprises really need as many IT services engineers as they did before?

## What NRI Investors Should Know

For diaspora investors, the sector presents a classic value-versus-narrative tension. On valuation, Indian IT stocks are cheaper than they have been in years. On narrative, the threat of AI disruption has not disappeared — it has just been complicated by evidence that AI is also creating new revenue streams.

The July rebound — a 10.3% gain for the Nifty IT index in just two weeks — suggests the market may have overshot to the downside. But a sustained re-rating will require more than one good quarter. Investors will be watching Infosys's results (due July 17) and Wipro's (due July 18) for confirmation that the recovery is broad-based, not a TCS-and-HCLTech anomaly.

For the tens of thousands of Indian engineers whose careers depend on these companies, the signal is more encouraging. The sector is hiring again — TCS added 9,300 employees in the June quarter, its fastest pace in three years. The new roles are increasingly in AI engineering, cloud architecture, and enterprise deployment, not the traditional application maintenance work that is most vulnerable to automation.

The AI transition is not painless. But Monday's rally is a reminder that India's IT industry has survived disruptions before — the dotcom bust, the 2008 financial crisis, the automation scare of the 2010s — and emerged larger each time."""
    },
]

# ── Insert ──
print("\nInserting articles...")
for art in articles:
    if not art["image_url"]:
        print(f"  ⚠ Skipping image for {art['slug']} (no image found)")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\nDone.")
