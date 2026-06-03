#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-03 09:00 UTC batch"""

import json, os, uuid, re, requests, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ──
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

# ── Image sourcing ──
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
            for page in pages.values():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and mime.startswith("image/"):
                    results.append(url)
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for an image. Returns URL or None."""
    pexels_env = Path.home() / "workspace" / ".env.pexels"
    api_key = None
    if pexels_env.exists():
        for line in pexels_env.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                if "PEXELS" in k.upper():
                    api_key = v.strip()
                    break
    if not api_key:
        print("  ⚠ No Pexels API key found")
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5",
            headers={"Authorization": api_key},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels API error for '{query}': {e}")
    return None

def validate_image(url):
    """Quick check that image URL returns valid image with reasonable size."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD, try GET with range
        if "image" in ct:
            return True
    except:
        pass
    return False


# ── Source images ──
print("Sourcing images...")

# Article 1: Marvell — try Jensen Huang or Matt Murphy, or a networking image
img1 = fetch_wikipedia_person_image("Jensen Huang")
if not img1 or not validate_image(img1):
    commons = fetch_wikimedia_commons_images("Jensen Huang Nvidia")
    img1 = next((u for u in commons if validate_image(u)), None)
if not img1:
    img1 = fetch_pexels_image("data center server room networking")

# Article 2: Micron / Sanjay Mehrotra
img2 = fetch_wikipedia_person_image("Sanjay Mehrotra")
if not img2 or not validate_image(img2):
    img2 = fetch_wikipedia_person_image("Micron Technology")
if not img2 or not validate_image(img2):
    commons = fetch_wikimedia_commons_images("Micron Technology semiconductor")
    img2 = next((u for u in commons if validate_image(u)), None)
if not img2:
    img2 = fetch_pexels_image("semiconductor chip memory closeup")

# Article 3: Samsung strike — try Samsung semiconductor or factory
commons3 = fetch_wikimedia_commons_images("Samsung semiconductor factory")
img3 = next((u for u in commons3 if validate_image(u)), None)
if not img3:
    img3 = fetch_pexels_image("semiconductor factory cleanroom workers")
if not img3:
    img3 = fetch_pexels_image("factory workers protest strike")

print(f"\nFinal images:")
print(f"  1. Marvell: {img1[:80] if img1 else 'NONE'}...")
print(f"  2. Micron:  {img2[:80] if img2 else 'NONE'}...")
print(f"  3. Samsung: {img3[:80] if img3 else 'NONE'}...")


# ── Articles ──

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Jensen Huang Just Told Marvell It Will Be the Next Trillion-Dollar Company. The Stock Jumped 32%.",
        "subheadline": "At Computex 2026, the Nvidia CEO pointed to networking as the hidden bottleneck in AI infrastructure — and anointed Marvell as its solution. Indian engineers building the data centre stack should pay attention.",
        "slug": make_slug("marvell-jensen-huang-trillion-dollar-networking-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Marvell employs significant Indian engineering talent in its Santa Clara operations and design centres. For NRI investors, the stock has quadrupled in 12 months. For Indian engineers at data centre companies, this signals that networking and optical interconnect roles are the next frontier of AI hiring.",
        "tags": ["marvell", "nvidia", "computex", "ai-infrastructure", "semiconductors", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/marvell-technology-surges-after-nvidias-huang-calls-it-next-trillion-dollar-2026-06-03/"},
            {"name": "Investopedia", "url": "https://www.investopedia.com/nvidia-jensen-huang-marvell-trillion-dollar-club-12290107"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/business/marvell-stock-soars-after-nvidias-huang-says-it-could-be-next-1-trillion-company"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/marvell-stock-nvidia-ceo-trillion-dollar/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": img1 or "",
        "body": """Jensen Huang does not hand out compliments lightly. So when the Nvidia CEO turned to Marvell Technology's Matt Murphy at the Computex 2026 stage in Taipei and said, "That's why you're going to be the next trillion-dollar company," the market took it as something closer to a business forecast than a pleasantry.

Marvell's stock surged 32.5% in a single session on Tuesday, closing at a record $290.79 and adding roughly $62 billion in market capitalisation. The company is now valued at approximately $254 billion — still a long way from the trillion-dollar mark, but quadrupled from where it traded twelve months ago.

## The Bottleneck No One Saw Coming

Huang's thesis is simple and, increasingly, shared across the AI infrastructure industry: the hardest problem in scaling AI data centres is no longer the GPU itself. It is getting data to and from the GPU fast enough.

"The most expensive idle asset in the world right now is a GPU waiting on the network," DriveNets CEO Ido Susan said in a separate statement this week — articulating the same problem Huang highlighted on stage. As AI clusters grow from thousands to hundreds of thousands of accelerators, the networking fabric connecting them becomes the critical constraint.

Marvell sits at the centre of this bottleneck. The company makes the digital signal processors inside optical transceivers — the components that convert electrical signals into light to transfer data efficiently across sprawling AI data centres. At Computex, Marvell announced the Teralynx T100, the industry's first 102.4 terabits-per-second switch silicon purpose-built for AI and cloud infrastructure, with 25% lower power consumption and the industry's lowest latency for AI training and inference workloads.

## A $2 Billion Vote of Confidence

Nvidia is not just talking. In March, the company invested $2 billion in Marvell and expanded their partnership to bundle Marvell's custom silicon with Nvidia's networking gear and CPUs for data centre customers. Marvell's custom chips business is projected to exceed $10 billion in annual revenue by fiscal 2029.

Barclays analyst Tom O'Malley projects Marvell's optical-networking revenue could grow by as much as 90% this year and next. The company's co-packaged optics technology — which integrates optical components directly into switch silicon, eliminating the copper interconnects that are hitting physical limits — is increasingly viewed as the only viable path for next-generation AI clusters.

"Copper is hitting a wall inside the rack," Murphy said at Computex. "Co-packaged optics is the only way through."

## What This Means for Indian Engineers

Marvell's engineering operations are heavily concentrated in Santa Clara and across semiconductor design centres that employ significant Indian talent. The company's rise signals a broader shift in where AI-era hiring is heading: away from pure GPU design and toward networking, optical interconnects, and custom silicon integration.

For the thousands of Indian engineers working across the data centre stack at companies like Broadcom, Cisco, Arista Networks, and Marvell itself, Huang's endorsement is a validation that their domain — long considered less glamorous than GPU architecture — has become strategically indispensable.

For NRI investors, Marvell's trajectory is worth watching closely. The stock has quadrupled in twelve months, and while the trillion-dollar valuation Huang prophesied would require nearly another quadrupling, the fundamentals — surging AI networking demand, deep Nvidia integration, and technological moats in co-packaged optics — suggest the story is far from over.

J.P. Morgan analysts put it bluntly this week: "The real winners will be those who own the bottleneck." Marvell, by Huang's reckoning, owns the one that matters most."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "How Jensen Huang Convinced Sanjay Mehrotra to Abandon Frugality. Now Micron Is Worth a Trillion Dollars.",
        "subheadline": "A private meeting three years ago between the Nvidia CEO and Micron's Indian-origin boss reshaped the memory chip industry. Micron's stock has risen tenfold since, and its first India fab just started producing chips.",
        "slug": make_slug("micron-sanjay-mehrotra-trillion-nvidia-ai-memory"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Sanjay Mehrotra, born in Kanpur, is the Indian-origin CEO who has led Micron to a $1 trillion valuation. Micron's Sanand, Gujarat facility — India's first semiconductor assembly and test plant — opened in February 2026 with a $2.75 billion investment. NRI investors holding MU stock have seen 200%+ returns in 2026 alone.",
        "tags": ["micron", "sanjay-mehrotra", "nvidia", "semiconductors", "ai-memory", "india-fab", "hbm"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/how-nudge-nvidia-propelled-frugal-micron-into-ai-boom-1-trillion-market-cap-2026-06-03/"},
            {"name": "Barron's / J.P. Morgan", "url": "https://www.barrons.com/articles/micron-ai-bottleneck-stocks-jp-morgan-2026"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/originals/mu-ssnlf-and-sk-hynix-stocks-rally-as-hbm-shortage-builds-concentration-risk/"},
            {"name": "Micron Investor Relations", "url": "https://investors.micron.com/news-releases/news-release-details/micron-celebrates-opening-indias-first-semiconductor-assembly-and"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": img2 or "",
        "body": """Three years ago, Jensen Huang sat across from Sanjay Mehrotra and outlined a future that the Micron CEO had not quite imagined. Memory chips, Huang argued, were about to stop being commodities. They would become custom-engineered components, co-designed for specific AI processors, sold on long-term contracts with margins that would have been unthinkable in the old boom-bust DRAM cycle.

It was a polite but pointed challenge to the way Mehrotra had run Micron for decades — the frugality, the used equipment, the commodity mindset that had helped the Idaho company outlast rivals but left it perpetually undervalued.

"I was really grateful that Micron and Nvidia really lined up all of our roadmap," Huang said in a media interview last month, acknowledging the conversation that set Micron's transformation in motion.

The result: Micron's stock has risen roughly tenfold from its 2024 lows. The company's market capitalisation crossed $1 trillion in recent weeks, joining Samsung Electronics and SK Hynix in an exclusive club of memory manufacturers that have been catapulted into the stratosphere by AI demand.

## The HBM Bottleneck

The specific technology driving this surge is high-bandwidth memory, or HBM — stacked memory chips bonded directly to AI processors that feed data to GPUs at speeds impossible with conventional DRAM. Every Nvidia data centre GPU, from the current Blackwell generation to the upcoming Vera Rubin platform, requires HBM chips that are co-designed with the processor.

Only three companies in the world can make them: SK Hynix, Samsung, and Micron. The supply gap, according to industry analysts, stretches beyond 2028, with cloud infrastructure capital expenditure now exceeding $725 billion annually.

J.P. Morgan analysts this week called the HBM shortage the single most important theme in the stock market. "These companies are not just suppliers," they wrote. "They are critical to the next phase of AI growth, with market power and technical barriers that are not easily overcome."

Micron stock closed Tuesday at $1,064.10, up 2.76%. SK Hynix shares have surged past 200% gains in 2026. Samsung, despite separate challenges, has also entered the trillion-dollar club.

## The Kanpur-Born CEO at the Centre

Mehrotra, born in Kanpur and educated at the Birla Institute of Technology and Science, Pilani, before moving to the United States, co-founded SanDisk in 1988 and led it through its acquisition by Western Digital. He took the Micron CEO role in 2017, inheriting a company known for surviving cycles rather than capitalising on them.

The transformation required abandoning the commodity playbook. Micron's HBM chips for Nvidia are now distinct from those it sells to AMD or others — each version tailored to a specific customer's processor architecture. That shift from interchangeable product to bespoke engineering has reshaped Micron's margin structure and investor confidence.

## India's First Chip Plant

In February 2026, Mehrotra stood alongside Prime Minister Narendra Modi to inaugurate Micron's semiconductor assembly and test facility in Sanand, Gujarat — India's first operational chip plant. The $2.75 billion facility, featuring more than 500,000 square feet of cleanroom space, converts advanced DRAM and NAND wafers into finished memory products for global customers.

The plant is not fabricating chips from scratch — that capability remains concentrated in South Korea, Japan, and the United States. But it represents a meaningful step in India's semiconductor ambitions and has created thousands of engineering and manufacturing jobs in Gujarat.

For NRI investors, the Micron story is personal in a way few tech stocks are. An Indian-origin CEO leading a trillion-dollar American semiconductor company, with India's first chip plant producing components for the AI revolution — the narrative practically writes itself.

## What Comes Next

The memory supply crisis is not easing. AMD's David McAfee said at Computex this week that the industry is "on the undersupplied side" and it will take years for capacity to catch up. TrendForce projects HBM demand in 2026 will be driven by custom AI chips, with Nvidia's Rubin Ultra platform sustaining demand into 2027.

Mehrotra's challenge now is execution — ramping India operations, expanding HBM capacity, and maintaining the customer relationships that Huang's nudge helped forge. The frugal company from Boise is not frugal anymore. It cannot afford to be."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Samsung Workers Are Threatening a Nationwide Strike. The AI Chip Shortage Could Get Worse.",
        "subheadline": "Samsung Electronics has begun cutting chip production ahead of a planned labour action. With memory supply already stretched beyond 2028, the timing could not be worse for the AI industry — or for Indian semiconductor professionals watching the supply chain.",
        "slug": make_slug("samsung-strike-chip-production-memory-shortage-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian semiconductor professionals work across the memory supply chain — at Micron's India fab, at Samsung and SK Hynix design centres, and at AI companies dependent on stable memory supply. A Samsung production disruption would tighten the market for Indian chip engineers and affect NRI investors with semiconductor exposure.",
        "tags": ["samsung", "semiconductor", "memory-chips", "ai-infrastructure", "supply-chain", "labour-strike"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "KED Global", "url": "https://www.kedglobal.com/semiconductor/samsung-cuts-chip-output-ahead-of-strike/"},
            {"name": "KED Global", "url": "https://www.kedglobal.com/semiconductor/samsung-expects-tighter-memory-supply-in-2027/"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/originals/mu-ssnlf-and-sk-hynix-stocks-rally-as-hbm-shortage-builds-concentration-risk/"},
            {"name": "Barron's / J.P. Morgan", "url": "https://www.barrons.com/articles/micron-ai-bottleneck-stocks-jp-morgan-2026"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": img3 or "",
        "body": """The world's largest memory chipmaker has begun scaling back semiconductor production ahead of a planned nationwide labour strike, and the potential disruption is measured not in days lost but in tens of billions of dollars.

Samsung Electronics' union has rejected management's latest overture for talks, setting the stage for a work stoppage that analysts estimate could cause over $67 billion in economic disruption. The company has preemptively cut output at its semiconductor facilities, a move that ripples through the entire AI supply chain at a moment when memory chips are already in critically short supply.

## A Crisis of Timing

The strike threat arrives against what may be the tightest memory market in a generation. All three global memory manufacturers — Samsung, SK Hynix, and Micron Technology — have recently approached or crossed the $1 trillion market capitalisation threshold, propelled by insatiable AI demand for high-bandwidth memory chips.

A senior Samsung executive said this week that on-device AI and data centre expansion will drive a "prolonged memory shortage." The company has separately warned that memory supply will tighten further in 2027 as AI infrastructure absorbs capacity faster than new fabs can be built.

Samsung is simultaneously accelerating construction of a new mega-fab at its Pyeongtaek semiconductor complex, moving the timeline forward by at least six months in what has become an outright capacity race with SK Hynix. The irony is not lost on industry observers: the company is racing to build more capacity while its existing workforce threatens to walk off the production floor.

## The Rift Within

The labour dynamics are more complex than a simple management-versus-union narrative. A rift has emerged between Samsung's chip division workers and employees in other divisions. Workers in the semiconductor unit — who have benefited from massive AI-driven demand and associated bonuses — have different interests than those in the consumer electronics or display divisions, where margins are thinner and job security feels more precarious.

This internal division complicates union negotiations and raises the prospect of a prolonged standoff. The union has rejected initial management proposals, and neither side appears eager to compromise quickly.

## Why Indian Professionals Should Care

The Samsung disruption matters to the Indian tech ecosystem on multiple levels.

First, supply chain exposure. India's Micron facility in Sanand, Gujarat, assembles and tests memory chips using wafers sourced from the global manufacturing network. A Samsung production cut tightens the overall supply of DRAM and NAND globally, which affects pricing and availability for every company in the chain — including those sourcing from Micron and SK Hynix.

Second, hiring dynamics. Indian semiconductor professionals are spread across all three memory giants. Samsung's R&D centres employ Indian engineers in chip design and process engineering. A production slowdown does not eliminate design work, but it creates uncertainty that can slow hiring pipelines and visa sponsorship decisions.

Third, investor exposure. NRI investors with positions in semiconductor ETFs or individual memory stocks are directly affected by Samsung's production decisions. Memory chip stocks have been the single best-performing sector in 2026 — Micron and SK Hynix are up over 200% — and any supply shock that further tightens the market could push prices higher, while a prolonged strike creates downside risk through execution uncertainty.

## The Bigger Picture

J.P. Morgan analysts this week identified the memory chip shortage as the most important investment theme in the current market, calling companies like Micron, SK Hynix, and Samsung "bottleneck owners" with pricing power that is "not easily overcome."

The logic cuts both ways. If Samsung's production disruption is brief, it may actually benefit the memory sector by tightening supply further and pushing prices higher. Memory manufacturers already have leverage in HBM pricing negotiations — TrendForce reports that HBM per-wafer revenue has dipped below DDR5 RDIMM modules, giving manufacturers incentive to demand higher prices from AI chip buyers.

But a prolonged strike would introduce a variable the AI industry cannot easily model: uncertainty in the supply of a component for which there are literally only three suppliers on the planet. SK Hynix is doubling capacity over the next five years. Micron is ramping its India facility. But neither can absorb a significant Samsung shortfall overnight.

For Indian engineers and investors watching the AI boom from Silicon Valley, Bangalore, or Hyderabad, the Samsung strike is a reminder that the AI revolution runs on physical infrastructure with very human constraints. The most advanced chips in the world are still made by people who want better working conditions. That tension is not going away."""
    }
]

# ── Insert ──
print("\nPublishing articles...")
for art in articles:
    if not art["image_url"]:
        print(f"  ⚠ No image for: {art['slug']} — publishing without image")
    try:
        sb_post("p2_articles", art)
        print(f"  ✅ {art['slug']}")
    except Exception as e:
        print(f"  ❌ {art['slug']}: {e}")

print("\nDone.")
