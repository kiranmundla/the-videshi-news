#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-29 03:00 UTC run"""
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

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# --- Image sourcing ---
print("Sourcing images...")

# Article 1: Dell — Michael Dell Wikipedia image
dell_img = fetch_wikipedia_person_image("Michael Dell")
if not dell_img:
    dell_img = "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

# Article 2: TSMC — semiconductor chip Pexels
tsmc_img = "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

# Article 3: Atlassian — Rajeev Rajan Wikipedia (unlikely), fallback to tech office
atlassian_img = fetch_wikipedia_person_image("Rajeev Rajan")
if not atlassian_img:
    atlassian_img = "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

# Verify images
for label, url in [("Dell", dell_img), ("TSMC", tsmc_img), ("Atlassian", atlassian_img)]:
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ {label} image OK ({cl} bytes)")
        else:
            print(f"  ⚠ {label} image check: status={r.status_code}, type={ct}, size={cl}")
    except Exception as e:
        print(f"  ⚠ {label} image verify error: {e}")

print()

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Dell's AI Revenue Explodes 757%. The Pentagon Just Handed It $9.7 Billion More.",
        "subheadline": "The biggest earnings surprise of the AI era raises a question for every Indian engineer at Dell's Bangalore and Hyderabad campuses: how long before AI server demand reshapes their jobs too?",
        "slug": make_slug("dell-ai-revenue-757-percent-pentagon-deal"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Dell employs over 25,000 engineers across India in Bangalore, Hyderabad, and Chennai — its largest R&D footprint outside the US. As AI server revenue explodes, the skills demanded at these centers are shifting from traditional enterprise hardware to AI infrastructure, GPU orchestration, and liquid cooling systems. NRI investors who missed the Nvidia run should note Dell's stock is up 150% since February.",
        "tags": ["dell", "ai-servers", "pentagon", "nvidia", "earnings", "india-r&d"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/dell-stock-soars-on-data-center-revenue-and-pentagon-deal-6645700b"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/dell-raises-annual-forecasts-ai-data-center-buildout-fuels-demand-2026-05-29/"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/dell-stock-soars-toward-another-record-high-as-the-ai-boom-drives-a-big-earnings-beat-2026-05-29"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/dell-stock-soars-on-blowout-earnings-2026-05-29"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "image_url": dell_img,
        "body": """Dell Technologies just posted the kind of quarter that makes Wall Street recalibrate its models.

First-quarter revenue hit $43.8 billion — an 88% surge over the prior year that left analyst estimates scattered in the dust. The headline number is startling enough. The composition is staggering: $16.1 billion came from AI-optimized servers alone, a 757% year-over-year explosion that turned Dell's Infrastructure Solutions Group into the fastest-growing division in the company's history.

Then came the Pentagon. A five-year, $9.7 billion blanket purchase agreement for Microsoft software and services across the entire Defense Department, the Coast Guard, and U.S. intelligence agencies. The contract replaces dozens of fragmented deals and is expected to save $422 million annually — the kind of consolidation play that cements Dell as an enterprise incumbent for a generation.

## The Numbers Behind the Frenzy

Dell raised its full-year AI revenue forecast to $60 billion, up from the $50 billion it guided in February — a 144% increase over the prior year. Total fiscal 2027 revenue guidance now sits at $165–169 billion, roughly $27 billion above where Wall Street had modeled it. The AI server backlog stands at $51.3 billion, a number that keeps growing faster than Dell can ship.

Shares surged nearly 40% in after-hours trading. Since February, the stock is up roughly 150%.

The engine powering this is straightforward: hyperscale cloud companies — Alphabet, Amazon, Meta, Microsoft — are spending more than $700 billion this year on AI infrastructure, and Dell's Nvidia-powered server racks are the physical backbone of that buildout. CoreWeave, Honeywell, and Samsung Electronics are among the customers driving demand.

## Why This Matters in Bangalore

Dell's India operations are not a cost center bolted onto a Texas hardware company. They are the engineering core. With over 25,000 employees across Bangalore, Hyderabad, and Chennai, India represents Dell's largest research and development footprint outside the United States. These engineers design firmware, build storage architectures, develop PowerEdge server management software, and increasingly work on the thermal and power delivery systems that AI-class hardware demands.

As AI servers grow from a third to potentially half of Dell's revenue, the skill mix at these centers is shifting. Job postings in Bangalore now emphasize GPU cluster orchestration, liquid cooling system design, and AI inference optimization — roles that didn't exist at Dell India three years ago. For the 50,000-plus Indian-origin professionals in Dell's global workforce, the message is clear: the company's center of gravity is moving, and the ones who move with it will define the next decade.

## The Political Undercurrent

There is a complicating factor. President Trump's personal accounts purchased Dell stock worth between $1 million and $5 million on February 10 — weeks before publicly praising Dell's CEO and telling a Georgia crowd to "go out and buy a Dell computer." The Pentagon contract followed shortly after.

Dell's management has not commented on any connection. But for NRI investors tracking both the company's fundamentals and Washington's increasingly entangled relationship with Big Tech, the optics bear watching.

## What Comes Next

The AI server market is not slowing. ByteDance, Oracle, and sovereign AI initiatives across the Gulf and Southeast Asia are all placing massive orders. Dell's advantage — unlike pure-play server makers — is that it bundles hardware with enterprise software, services, and financing, making it the one-stop shop for organizations that lack hyperscaler-level engineering teams.

For Indian Americans in the technology sector, Dell's quarter is a barometer. When the company that makes the physical machines behind every AI model is growing revenue at 88% a year, the infrastructure boom is not theoretical. It is the defining economic story of this decade — and a disproportionate share of the engineering talent building it sits in Indian offices and holds Indian passports."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "TSMC Is Raising Chip Prices 15%. Every AI Company Will Pay.",
        "subheadline": "The world's most important chipmaker is finally leveraging its monopoly on advanced manufacturing — and the cost increases will ripple from Nvidia's data centers to India's semiconductor ambitions.",
        "slug": make_slug("tsmc-3nm-chip-price-hike-15-percent-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian engineers at Nvidia, AMD, Broadcom, Marvell, and Qualcomm all design chips manufactured by TSMC. Price hikes directly affect their companies' margins and product roadmaps. India's own semiconductor mission — including the Tata Electronics fab in Dholera — relies heavily on TSMC-trained process engineers. And for NRI investors holding chip stocks, TSMC's pricing power is the single biggest variable in the sector's profitability calculus.",
        "tags": ["tsmc", "semiconductor", "3nm", "ai-chips", "nvidia", "pricing", "india-semiconductor"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/research/ibd-stock-of-the-day/tsmc-stock-flirts-with-buy-point-as-chip-giant-will-raise-prices/"},
            {"name": "Aroged", "url": "https://aroged.com/2026/05/28/due-to-the-ai-boom-tsmc-will-increase-prices-for-3nm-chips/"},
            {"name": "TrendForce", "url": "https://www.trendforce.com/news/2026/05/tsmc-cowos-capacity-crunch/"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/why-its-time-to-start-discussing-semiconductors-like-commodities-2026-05-28"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": tsmc_img,
        "body": """Taiwan Semiconductor Manufacturing Company has done what everyone expected and no one wanted: it is raising prices.

TSMC will increase prices on its 3-nanometer process — the technology behind Nvidia's Blackwell GPUs, Apple's latest chips, and AMD's Instinct MI355X accelerators — by 15% this year. A further 5–10% hike is expected in 2027. The Taiwan-based Commercial Times broke the news, and the market's response was telling: TSMC's stock rose on the announcement, not despite it. When your customers have no alternative, a price increase is a statement of dominance, not a risk.

## The Arithmetic of a Monopoly

TSMC fabricates more than 90% of the world's most advanced chips. Its Fab 18 complex in Tainan has expanded production capacity to 175,000 wafers per month on the 3nm node, yet demand continues to outstrip supply. Every major AI chip designer — Nvidia, AMD, Broadcom, Marvell, Amazon, Google, Meta, Microsoft — is in TSMC's queue, and the queue is long.

The bottleneck is not just transistors. It is packaging. TSMC's CoWoS (Chip-on-Wafer-on-Substrate) advanced packaging technology is what binds AI processors to the high-bandwidth memory they need to function. The company plans to quadruple CoWoS capacity to 130,000 wafers per month by late 2026, but Nvidia alone has secured roughly 60% of the 2026 allocation. AMD, Broadcom, and the rest are fighting over the remainder.

MarketWatch argued this week that semiconductors should now be discussed like commodities — subject to supercycles, supply crunches, and pricing power that mirrors oil more than electronics. The comparison is not hyperbolic. The PHLX Semiconductor Index is up nearly 80% year-to-date.

## Where Indian Engineers Sit in This Supply Chain

The price hikes will cascade. Nvidia's next-generation Blackwell Ultra and Vera Rubin architectures are manufactured on TSMC's most advanced nodes. Higher wafer costs mean higher GPU prices, which mean higher costs for every AI training run and inference query at every cloud provider. The economics of building AI just got more expensive.

For the thousands of Indian engineers at chip design companies — and the number is not small; Indians occupy senior architecture, verification, and physical design roles at Nvidia, AMD, Qualcomm, Broadcom, and Marvell — this changes the design calculus. Every additional square millimeter of silicon now costs more. Design efficiency, power optimization, and chiplet architectures that use less advanced packaging become more valuable. The engineers who can squeeze more performance per transistor dollar are the ones whose companies will maintain margins.

## The India Semiconductor Connection

India's own chip ambitions are inextricably linked to TSMC's pricing decisions. The $18.2 billion in semiconductor projects recently approved by New Delhi — including the Tata Electronics fab in Dholera, Gujarat, and Micron's assembly and test facility — are all being built with knowledge transferred from TSMC-trained process engineers. Many of those engineers are Indian diaspora professionals who spent years at TSMC's Hsinchu and Tainan facilities before returning to India or consulting for Indian projects.

TSMC's price hikes also reveal the strategic value of India's fab investments. If advanced manufacturing becomes permanently expensive, the nations that build domestic capacity — even at trailing nodes — gain leverage. India's fabs will not compete with TSMC on 3nm, but they can capture the vast market for automotive, IoT, defense, and consumer chips that do not require cutting-edge processes.

## The Investment Signal

For NRI investors, the message embedded in TSMC's pricing power is unambiguous: the AI infrastructure boom is supply-constrained, and the constraint is structural. Companies that sit closest to TSMC in the supply chain — Nvidia, AMD, Broadcom — will pass costs along and maintain margins. Companies further downstream, particularly Indian IT services firms bidding on AI projects at fixed prices, will absorb the squeeze.

TSMC's CoWoS expansion to system-on-wafer manufacturing by 2027 — integrating entire AI systems onto a single wafer — will further concentrate value at the foundry layer. The chip industry is not just booming. It is consolidating power in a single company's hands. And that company just raised its prices because it can."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Atlassian's Indian-Origin CTO Is Out. His Replacement's Job Title Says Everything.",
        "subheadline": "The Jira maker cut 1,600 jobs and replaced CTO Rajeev Rajan with AI-focused leaders — a restructuring that signals what's coming for senior Indian tech executives across Silicon Valley.",
        "slug": make_slug("atlassian-indian-cto-rajeev-rajan-ai-layoffs"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Rajeev Rajan's departure is the highest-profile exit of an Indian-origin CTO in the current AI restructuring wave. Every Indian IT company and GCC in the world uses Atlassian's tools — Jira, Confluence, Bitbucket are the operating system of Indian software development. The 250 jobs cut in India directly affect H-1B holders and Indian engineers. And the broader signal — that AI expertise now trumps traditional engineering leadership — should concern every senior Indian tech executive whose resume emphasizes scale over AI.",
        "tags": ["atlassian", "layoffs", "indian-cto", "ai-restructuring", "jira", "h1b"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "HRKatha", "url": "https://www.hrkatha.com/layoffs/atlassian-cuts-1600-jobs/"},
            {"name": "Techstrong.ai", "url": "https://techstrong.ai/articles/atlassian-cuts-1600-jobs-ai-move/"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/atlassian-layoffs-1600-jobs-ai-enterprise-growth/"},
            {"name": "AllWork", "url": "https://allwork.space/2026/05/atlassian-to-lay-off-10-percent-workforce-ai/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": atlassian_img,
        "body": """Rajeev Rajan built Atlassian's engineering organization through some of its most formative years. He oversaw the migration to cloud, scaled the platform that powers Jira and Confluence for over 300,000 customers, and held the title that every ambitious Indian engineer in Silicon Valley aspires to: Chief Technology Officer.

Now he is out. And the restructuring that accompanied his departure tells a story far larger than one company's org chart.

## The Cut

Atlassian announced 1,600 layoffs — 10% of its 13,800-person workforce. Roughly 500 positions were eliminated in Australia, where the company is headquartered. Another 250 were cut in India. The remaining 850 were spread across North America and other global offices. The restructuring will cost $225–236 million in severance and related charges.

The layoffs hit R&D particularly hard. Atlassian is not cutting costs because revenue is declining — the company recently posted its largest-ever quarter for displacing ServiceNow customers and crossed $1 billion in annual recurring revenue for its cloud platform. It is cutting to redirect.

CEO Mike Cannon-Brookes framed the move explicitly around AI. The company is "rebalancing resources" to invest in artificial intelligence capabilities and pivot toward large enterprise sales. The jobs being eliminated are concentrated in traditional engineering, quality assurance, and middle management — roles that Atlassian's leadership believes AI tools can partially automate or that are not aligned with the company's AI-first product roadmap.

## The CTO Swap

The symbolic weight of the CTO change is hard to overstate. Rajan represented a generation of Indian-origin technology leaders who rose through the ranks by building reliable, scalable systems — the kind of engineering that made India's reputation in global tech. His replacement is not one person but two: a pair of newly created CTO roles specifically focused on AI product development and AI infrastructure.

The message is blunt. The skills that built Atlassian's cloud platform are not the skills that will build its AI-powered future. Traditional engineering leadership — even at the highest levels — is being replaced by AI-native leadership. Rajan is not being fired for failure. He is being replaced by a different era.

## Why 250 Indian Jobs Matter

Atlassian's India engineering center, primarily in Bangalore, is not an outsourced support function. It is a core product development hub responsible for significant portions of Jira, Confluence, and Bitbucket. The 250 roles cut there include senior engineers and team leads — professionals who are often on H-1B or L-1 visas at Atlassian's San Francisco or Sydney offices, or who anchor the India center with a decade of institutional knowledge.

For H-1B holders affected by the cuts, the 60-day grace period to find new employment or face deportation is the immediate concern. For the broader Indian tech workforce, the concern is structural: if Atlassian — a company that built its culture around empowering developers — is cutting engineers to fund AI, what does that signal for every other company that employs Indian tech talent?

## The Jira Paradox

There is an irony that should not be lost on the Indian IT industry. Jira is arguably the single most widely used tool in Indian software development. Every TCS, Infosys, and Wipro project runs on it. Every Global Capability Center in Bangalore, Hyderabad, and Pune tracks sprints and bugs in Jira. Indian developers have effectively built their careers on Atlassian's platform.

Now that platform's maker is telling the market that the engineers who build traditional software tools — the kind of engineering that Indian IT services have excelled at for two decades — are less valuable than engineers who can build AI agents that automate software development itself. The tool that Indian engineers use every day is being rebuilt by a company that just decided it needs fewer engineers to do it.

## The Pattern

Atlassian is not an outlier. Meta cut 8,000 roles with AI cited as a factor. Standard Chartered eliminated 7,000 positions, with its CEO calling them "lower-value human capital." The tech industry shed 80,000 jobs in Q1 2026 alone, with half attributed to AI automation. In each case, senior technical roles — the positions that Indian professionals have spent decades working toward — are disproportionately affected.

The Rajan departure crystallizes a question that every Indian-origin tech executive should be asking: in a world where AI capability is the primary hiring criterion, does a career built on scaling traditional systems still lead to the C-suite? Or does it lead to a restructuring announcement?

The answer, at least at Atlassian, is already written."""
    }
]

print(f"Publishing {len(articles)} articles...")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
