#!/usr/bin/env python3
import json, os, uuid, re, requests
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

# Validate image URL before inserting
def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return url
        # Try GET if HEAD didn't return Content-Length
        r2 = requests.get(url, timeout=10, stream=True)
        chunk = r2.raw.read(6000)
        if r2.status_code == 200 and len(chunk) > 5000:
            return url
    except Exception as e:
        print(f"  ⚠️  Image validation failed: {e}")
    return None

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Sanjay Mehrotra's Micron Just Crossed $1 Trillion. He Still Can't Make Chips Fast Enough.",
        "subheadline": "The BITS Pilani graduate who co-founded SanDisk now runs the most critical memory company in the AI economy. His problem: demand for high-bandwidth memory is double what Micron can ship.",
        "slug": make_slug("sanjay-mehrotra-micron-trillion-hbm-ai-india"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Mehrotra is the latest Indian-origin CEO to lead a trillion-dollar tech company. For NRI investors with semiconductor exposure, Micron's trajectory — and its Gujarat facility — represent a rare convergence of personal heritage and portfolio relevance.",
        "tags": ["semiconductors", "micron", "sanjay-mehrotra", "hbm", "ai-chips", "indian-tech-leaders", "nri-investing"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Ad Hoc News", "url": "https://ad-hoc-news.de"},
            {"name": "TechStory India", "url": "https://techstory.in"},
            {"name": "Storyboard18", "url": "https://storyboard18.com"},
            {"name": "AInvest", "url": "https://ainvest.com"},
            {"name": "Micron Investor Relations", "url": "https://investors.micron.com"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "body": """Sanjay Mehrotra has a problem most CEOs would envy. Micron Technology, the company he has led since 2017, can satisfy barely half the demand for its most important product. The rest of his customers — including Nvidia, which needs Micron's high-bandwidth memory for every AI accelerator it ships — are waiting in line.

That scarcity has been exceptionally profitable. Micron's market capitalisation crossed $1 trillion last week after a single-day share price surge of nearly 20 per cent, making it the tenth most valuable public company in the United States. The stock is up more than 860 per cent over the past twelve months. Mehrotra himself has entered the billionaire club, with an estimated net worth of $1.2 billion, according to Forbes data tracked by Quiver Quantitative.

## The HBM Machine

The catalyst is high-bandwidth memory, or HBM — the specialised stacked DRAM that sits directly alongside AI processors inside data centre servers. Every Nvidia GPU, every AMD accelerator, every custom Google TPU requires banks of HBM to function. Without it, the chip is an expensive paperweight.

Micron's second-quarter fiscal 2026 results reflected the imbalance. Revenue hit $23.86 billion, up 196 per cent year-over-year. Gross margins reached 74.4 per cent, up from roughly 52 per cent a year earlier. The company generated $20.31 billion in operating cash flow against $11.78 billion in capital expenditure, producing $6.9 billion in adjusted free cash flow in a single quarter.

The guidance for the third quarter is even more striking: revenue of $33.5 billion, gross margins approaching 81 per cent, and earnings per share of $19.15. A single quarter is on track to exceed the company's entire prior fiscal year earnings.

Mehrotra has been characteristically blunt about the supply picture. Micron can satisfy only 50 to 65 per cent of medium-term HBM demand, he told analysts. The entire production run of its latest HBM4 generation — built specifically for Nvidia's next-generation Vera Rubin platform — is sold out through the end of fiscal 2026. HBM4 pricing is expected to rise 70 to 100 per cent in 2027 as new Korean fab capacity from Samsung and SK Hynix comes online only in the second half of that year.

UBS analyst Timothy Arcuri has tripled his price target to $1,625, arguing that Micron is no longer a cyclical memory manufacturer but a structural pillar of AI infrastructure. He projects earnings per share above $100 for the next several years and cumulative free cash flow of up to $400 billion through 2029.

## The India Bet

While Wall Street debates peak margins, Mehrotra has been quietly building something else: India's first semiconductor assembly and test facility.

Micron's plant in Sanand, Gujarat — inaugurated in February 2026 with Prime Minister Narendra Modi in attendance — converts advanced DRAM and NAND wafers from Micron's global network into finished memory products. The first phase features more than 500,000 square feet of cleanroom space, making it one of the world's largest single-floor assembly and test cleanrooms. The combined investment stands at approximately $2.75 billion from Micron and its government partners.

The facility moved from foundation to production in just 14 months, a speed that surprised global semiconductor observers. It is part of a broader Indian semiconductor push that aims to have four plants operational by the end of 2026, according to IT Minister Ashwini Vaishnaw.

## From Kanpur to a Trillion Dollars

Mehrotra's trajectory is a familiar arc in Indian tech — but one that has reached an unusual altitude. Born in India, he studied engineering at BITS Pilani before completing bachelor's and master's degrees in electrical engineering and computer science at UC Berkeley. He co-founded SanDisk in 1988, built it into a Fortune 500 company, and served as its CEO through its 2016 sale. He joined Micron the following year.

He now sits alongside Sundar Pichai (Alphabet), Satya Nadella (Microsoft), Arvind Krishna (IBM), and Shantanu Narayen (Adobe) in a small cohort of Indian-origin executives running trillion-dollar or near-trillion-dollar technology companies. But Mehrotra's company occupies a unique position: Micron does not make the software or the processors that grab headlines. It makes the memory without which none of those products work.

## What NRI Investors Should Watch

The bull case for Micron is straightforward: AI infrastructure spending is structural, HBM demand exceeds supply through at least 2027, and margins have room to expand. The bear case is equally clear: memory is historically cyclical, the stock trades at 43 times trailing earnings, and new Korean fab capacity arriving in late 2027 could compress pricing.

The signal to watch, according to multiple analysts, is the next quarterly capex guidance from Samsung and SK Hynix. If either signals aggressive total capacity expansion beyond their current 5 to 8 per cent growth trajectory, the pricing discipline that has powered Micron's ascent begins to crack.

For now, the BITS Pilani graduate who bet his career on memory chips finds himself at the centre of the AI economy's most critical bottleneck — and the market is paying a trillion dollars for his inability to solve it faster."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An Indian Startup Just Taped Out a Chip for AI Data Centres. The Power Problem Is the Opportunity.",
        "subheadline": "C2i Semiconductors, backed by Peak XV and TDK Ventures, has designed and taped out India's first AI power management chip entirely in-house. The target: the 'last-inch' energy bottleneck that hyperscalers can no longer ignore.",
        "slug": make_slug("c2i-semiconductors-india-ai-power-chip-tapeout"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "C2i represents India's shift from chip design services to original silicon IP — a transition NRI semiconductor engineers have long argued the country was capable of. The startup's success could accelerate return-to-India decisions for power electronics talent in the US.",
        "tags": ["semiconductors", "indian-startups", "deep-tech", "ai-infrastructure", "c2i-semiconductors", "peak-xv", "india-semiconductor-mission"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Communications Today India", "url": "https://communicationstoday.co.in"},
            {"name": "Incubees", "url": "https://incubees.com"},
            {"name": "Indian Startup News", "url": "https://indianstartupnews.com"},
            {"name": "Digitimes Asia", "url": "https://digitimes.com"},
            {"name": "Pulse", "url": "https://pulse.bot"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """India has designed plenty of chips. Indian engineers at Qualcomm, Intel, Texas Instruments, and Broadcom have been architecting processors for decades — working from Bengaluru offices on silicon that gets fabricated in Taiwan and sold under American brands. What India has not done, until now, is produce an original chip product from a homegrown company targeting a global market.

C2i Semiconductors, a Bengaluru-based startup founded barely eighteen months ago, has quietly changed that calculation. The company announced last week that it has taped out a smart power stage chip designed for AI data centre infrastructure — conceived, architected, and verified entirely by its Indian engineering team. The tape-out, the stage at which a finalised design is sent to a foundry for fabrication, is the semiconductor equivalent of a manuscript going to the printer. It is real, it is tangible, and it solves a problem that is getting worse by the quarter.

## The Last-Inch Problem

The issue C2i is attacking is deceptively simple: getting electricity from the power grid to the processor die without wasting too much of it as heat. In a conventional data centre, power conversion happens in several stages — from the utility feed to the rack, from the rack to the server, and from the server's voltage regulator to the chip. Each stage loses energy. At AI-infrastructure scale, those losses compound into serious money.

Nvidia's H100 accelerator draws up to 700 watts. Its forthcoming processors are projected to demand as much as 4,500 watts per chip by 2028, according to TDK Ventures, which recently invested in C2i. When a single AI training cluster contains thousands of such chips, even a two-percentage-point improvement in power conversion efficiency translates into millions of dollars in annual electricity savings and measurably cooler hardware.

C2i claims its platform achieves 96 per cent conversion efficiency — two points above incumbent solutions from established players like Monolithic Power Systems and Infineon. For a 100-megawatt AI data centre, that gap represents roughly $12 million in annual energy costs and processors running up to 4°C cooler, extending hardware lifespan and reducing cooling infrastructure.

## The Architecture

The startup's technical differentiation rests on two proprietary components. The Manas Controller is a software-defined power management unit that adapts to changing power delivery network conditions without requiring hardware redesign — a flexibility that matters as AI chip architectures evolve rapidly. The Sarayu Power Stage supports modular scalability for high-current applications, enabling what the company describes as voltage-regulator-as-a-service configurations.

The naming convention is deliberate. Manas and Sarayu are Sanskrit references — an understated nod to origin in a field where product names typically default to alphanumeric codes.

## The Money

C2i's Series A round has been extended to $16.7 million, led by Peak XV Partners (the Sequoia India successor) with participation from TDK Ventures and Yali Deeptech. The company had previously raised $4 million from Yali Capital in November 2024.

The investor profile matters. Peak XV is betting on deep tech in a market that has traditionally rewarded consumer internet and SaaS plays. TDK Ventures, the corporate venture arm of the Japanese components giant, brings validation from the power electronics supply chain. Nicolas Sauvage, president of TDK Ventures, framed the investment in infrastructure terms: "The transition to AI-scale compute is one of the most significant infrastructure build-outs of our generation, and it requires innovation at the very layer that delivers power to the silicon."

## India Semiconductor Mission's Quiet Progress

C2i's tape-out did not happen in isolation. The India Semiconductor Mission, the government body coordinating the country's chip ambitions, has financially supported 24 chip design projects across 105 companies through its Design-Linked Incentive (DLI) scheme. Amitesh Sinha, the Mission's chief executive, called C2i's milestone "a powerful demonstration that Indian innovation can extend across the technology stack, from the power grid to the chip level."

The company was founded in June 2024 by six engineers — Ram Anant, Vikram Gakhar, Preetam Tadeparthy, Dattatreya Suryanarayana, Harsha S B, and Muthusubramanian N V — several with deep experience in power electronics from stints at global semiconductor firms.

## What This Means for NRI Engineers

For the thousands of Indian power electronics engineers working at Texas Instruments, Analog Devices, Monolithic Power Systems, and Infineon in the United States, C2i represents something new: a credible Indian chip company building original products for a growing market. India's semiconductor story has historically been a services narrative — design centres doing verification and layout work for foreign companies. C2i is writing a product narrative.

AI infrastructure capital expenditure is projected to reach $500 to $600 billion over the next twelve to eighteen months and could approach $1 trillion by 2030. Power management sits at the base of that stack. If C2i can convert its tape-out into volume production, customer design wins, and follow-on products, it will have demonstrated that India can compete in semiconductor products, not just semiconductor talent.

The chip is now at the foundry. The harder part — building a sales pipeline, qualifying with hyperscaler procurement teams, and scaling manufacturing — begins next."""
    }
]

for art in articles:
    img = validate_image(art["image_url"])
    if img:
        print(f"✅ Image validated: {art['slug']}")
    else:
        print(f"⚠️  Image failed validation, removing: {art['slug']}")
        art["image_url"] = None

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ Published: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
