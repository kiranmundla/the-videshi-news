#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-09 18:00 UTC batch"""

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

def validate_image(url):
    """Verify image URL returns HTTP 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image valid: {url[:80]}... ({cl} bytes)")
            return True
        else:
            print(f"  ✗ Image failed: status={r.status_code}, ct={ct}, cl={cl}")
            return False
    except Exception as e:
        print(f"  ✗ Image error: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1: TCS Chairman — AI Agents May Match Headcount
# ─────────────────────────────────────────────────────────────────────

art1_body = """\
Half a million employees. Half a million AI agents. Working side by side. That is not a sci-fi pitch from a startup demo day. It is the stated trajectory of Tata Consultancy Services, articulated by Chairman N. Chandrasekaran at the company's annual general meeting on Tuesday — and it should concentrate the mind of every Indian technologist drawing a paycheque from the IT services industry.

"If the company has half a million employees, the day is not far when the company will have half a million AI agents," Chandrasekaran told shareholders. "The company's employees and AI agents will work together, and that will be the future."

The numbers underline the scale of the shift. TCS shed more than 23,000 employees on a net basis in the fiscal year ended March 2026. Last July alone, over 12,000 positions were cut. Chandrasekaran was careful to say the company does not plan to downsize, but will simply hire less — a distinction that matters mainly to the boardroom. For the roughly 300,000 engineering graduates India produces each year who once treated a TCS offer letter as a rite of passage, the message is stark: the conveyor belt is slowing down.

## The $2.3 Billion AI Bet

The company's annualised AI revenue has crossed $2.3 billion, and Chandrasekaran predicted that 100 per cent of TCS's revenue will carry an AI component before the decade is out. What was once a line item buried in innovation slides is now the company's central business thesis.

This isn't merely a TCS story. It is the template for India's $315 billion IT sector. The industry has been the country's most reliable engine of middle-class upward mobility for two decades — minting hundreds of thousands of white-collar jobs, sponsoring H-1B visas, and fuelling property markets from Bangalore to Hyderabad. If AI agents absorb even a fraction of the testing, documentation, and maintenance work that sustains those jobs, the downstream effects ripple through real estate, education, and immigration patterns.

## What This Means for NRIs

For Indian tech professionals in the United States, Chandrasekaran's vision sharpens an already uncomfortable reality. TCS, Infosys, Wipro, and HCL collectively sponsor thousands of H-1B petitions each year. Slower hiring at the entry and mid levels could mean fewer visa slots, longer green card queues growing even longer, and increased competition for the roles that remain.

"Some of the work being done will go to AI agents. That will be the nature of the transition that we have to go through not only as a company, as an industry, and as a country," Chandrasekaran said.

The share price reflects the market's anxiety. TCS stock has dropped more than 32 per cent in 2026, outpacing even the 25 per cent slide in the broader Nifty IT index. The Nifty IT fell another 2 per cent on Monday as global tech stocks came under pressure. Wipro lost 6.5 per cent in a single session; Infosys barely held flat.

## The Emerging Playbook

The optimistic reading is that TCS is doing what it has always done — adapting early, moving capital toward the growth frontier, and forcing competitors to follow. The company recently launched a dedicated AI-native GCC business unit (GVIC) to build the very offices that poach its own engineers. It is betting that if clients will replace services contracts with in-house AI-augmented teams, TCS can at least sell the construction blueprints.

For the diaspora professional watching from Sunnyvale or Jersey City, the strategic lesson is uncomfortable but clear: the moat that protected Indian IT talent — scale, cost arbitrage, English fluency — is exactly the moat that AI agents are designed to breach. Upskilling from project delivery into AI architecture, product management, or domain consulting is no longer optional career advice. It is survival arithmetic.

Chandrasekaran, characteristically, framed it as opportunity. The market, characteristically, is not so sure.
"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "TCS Chairman Says AI Agents Will Match Its 500,000 Headcount. Hiring Will Slow.",
    "subheadline": "N. Chandrasekaran's AGM declaration crystallises what Indian IT has feared — the sector's labour-intensive model is being rewritten by AI, and entry-level hiring is the first casualty.",
    "slug": make_slug("tcs-chandrasekaran-ai-agents-headcount-hiring-slows"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "TCS and its peers sponsor thousands of H-1B visas annually. Slower hiring means fewer visa slots, and AI agents absorbing testing and maintenance work directly threatens the roles that brought hundreds of thousands of Indian engineers to America.",
    "tags": ["tcs", "ai-agents", "indian-it", "h1b", "hiring", "chandrasekaran"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-tcs-chairman-expects-ai-agents-equal-employee-count-2026-06-09/"},
        {"name": "Livemint", "url": "https://www.livemint.com/market/stock-market-news/tcs-wipro-to-infosys-it-stocks-bleed-on-ai-and-tech-stocks-selloff-in-global-markets-nifty-it-dips-2-11749375050143.html"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/data-news/tata-consultancy-services-slips-tuesday-underperforms-competitors-e58dcc27-ef39988f7fc4"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/46/Natarajan_Chandrasekaran_-_India_Economic_Summit_2011.jpg",
    "image_caption": "TCS Chairman N. Chandrasekaran at the India Economic Summit",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: US Senators Push to Close TSMC Chip Loophole
# ─────────────────────────────────────────────────────────────────────

art2_body = """\
Washington's chip blockade against China has a hole in it, and two senators from opposite sides of the aisle want it plugged — fast. The fix, if it comes, could hand India's nascent semiconductor ambitions an unexpected tailwind.

On Monday, Senator Jim Banks (R-Indiana) and Senator Andy Kim (D-New Jersey) sent a letter to Jeffrey Kessler, head of the Bureau of Industry and Security, demanding tighter rules on contract chipmakers — most notably Taiwan Semiconductor Manufacturing Co — to prevent them from fabricating advanced AI chips for overseas subsidiaries of Chinese companies. The loophole is simple and dangerous: a Chinese firm sets up a shell entity in Malaysia or Singapore, places a custom chip order with TSMC, and the most powerful AI silicon in the world arrives without ever triggering a US export licence.

"Should this gap remain unaddressed, it would substantially undermine every other restriction the United States has imposed on China's access to advanced computing capability," the senators wrote. "Export controls that can be circumvented through fabrication orders placed at the world's most advanced foundry offer no meaningful protection to American national security."

## How the Gap Opened

The loophole emerged from the Trump administration's decision last year not to enforce Biden-era rules governing global access to US-designed chips. The Bureau of Industry and Security recently clarified that sales to Chinese company subsidiaries in third countries do require a licence. But as former State Department official Chris McGuire pointed out, the guidance never addressed the scenario where front companies order custom chips directly from a foundry. That distinction matters because TSMC fabricates roughly 90 per cent of the world's most advanced processors — including nearly all of Nvidia's AI GPUs.

The bipartisan push signals that chip export enforcement is one of the few areas of genuine congressional consensus. Both parties agree that allowing China backdoor access to AI-grade silicon defeats the purpose of every other restriction Washington has imposed, from entity list designations to the CHIPS Act's guardrails.

## India's Quiet Opportunity

For India's semiconductor ecosystem, the tightening of foundry-level controls adds momentum to an argument that was already gaining force: the world needs more places to make chips, and India is building the foundations. The India Semiconductor Mission now has 12 approved projects, including the Micron fab in Gujarat and Tata Electronics' facility in Dholera. Union IT Minister Ashwini Vaishnaw recently noted that two commercial semiconductor facilities are already operational.

The strategic logic is straightforward. Every new restriction on TSMC's ability to serve certain customers increases the premium on alternative manufacturing capacity. India is not going to rival Taiwan's advanced nodes this decade, but it can carve a meaningful position in mature-node fabrication, compound semiconductors, and advanced packaging — precisely the segments where diversification demand is strongest.

## The NRI Angle

For Indian-American semiconductor professionals — and there are tens of thousands of them across Intel, Qualcomm, Broadcom, Texas Instruments, and AMD — the export control tightening has both career and investment implications. Stricter rules accelerate reshoring and friend-shoring of chip supply chains, which means more design and process engineering work in the US and allied nations. Intel's stock jumped 12 per cent on Monday on reports of foundry deals with Google and Nvidia — a direct beneficiary of the shift away from TSMC concentration.

Meanwhile, the Indian government's semiconductor push is creating a reverse pipeline. Engineers who spent a decade at TSMC or GlobalFoundries are being courted to return and lead India's fab buildout. The combination of US restrictions and Indian incentives is producing a gravitational pull that did not exist five years ago.

The senators' letter is unlikely to produce overnight policy change. But it draws a line around the last major loophole in America's chip strategy, and every line drawn in Washington is a line that runs through Hsinchu, Bangalore, and the career plans of thousands of Indian engineers.
"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "US Senators Want to Plug the Last Hole in America's Chip Blockade. India Stands to Gain.",
    "subheadline": "A bipartisan push to stop TSMC from making AI chips for Chinese shell companies accelerates the case for alternative fab capacity — and India's semiconductor mission is first in line.",
    "slug": make_slug("us-senators-tsmc-loophole-china-chip-india-semiconductor"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Tens of thousands of Indian-American semiconductor engineers work at Intel, Qualcomm, and AMD. Tighter TSMC rules accelerate reshoring, creating more US-based chip jobs, while India's fab buildout is luring experienced NRI engineers back.",
    "tags": ["semiconductor", "tsmc", "china-chip-ban", "india-semiconductor-mission", "export-controls", "geopolitics"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/litigation/us-lawmakers-urge-tighter-rules-contract-chipmakers-supplying-chinese-firms-2026-06-09/"},
        {"name": "Reuters (India File)", "url": "https://www.reuters.com/world/india/"},
        {"name": "Ainvest", "url": "https://www.ainvest.com/news/indias-semiconductor-growth-navigating-ai-adoption-and-global-competition/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/TSMC_Fab5.JPG/1280px-TSMC_Fab5.JPG",
    "image_caption": "TSMC semiconductor fabrication facility in Hsinchu, Taiwan",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 3: Intel Lands Google and Nvidia Foundry Contracts
# ─────────────────────────────────────────────────────────────────────

art3_body = """\
Fourteen months ago, Intel was a cautionary tale — a former titan whose stock had been cut in half, whose fabs were bleeding money, and whose CEO had just been replaced by a venture capitalist with zero experience running a semiconductor manufacturer. On Monday, Intel's shares surged 12 per cent after The Information reported that Google has contracted the company to manufacture more than three million specialised AI chips, with an Nvidia deal potentially next in line.

That is not a sympathy rally. It is validation of the foundry-first thesis that CEO Lip-Bu Tan has been selling since he took the helm in March 2025 — and it carries significant implications for the thousands of Indian engineers who design, verify, and tape out chips at Intel's facilities in Bangalore, Hyderabad, and Hillsboro.

## Three Million Chips for Google

The deal, which Intel declined to confirm, reportedly involves Google ordering custom AI accelerators to be fabricated at Intel's foundries. This follows weeks of reports that Apple may also be considering Intel as a manufacturing partner — a twist that would have seemed unthinkable when Apple dumped Intel's processors from its Mac lineup in 2020.

Intel stock has roughly tripled since January, making it one of the best-performing names in the S&P 500 for 2026. But Wall Street remains divided: of seven analysts tracked by Visible Alpha, three recommend buying, three are neutral, and one says sell. The concern is whether Intel can reliably deliver on its 18A process node, the technology that underpins its pitch to external customers.

"We are just getting started on our journey to build a new Intel," Tan wrote on social media over the weekend, days before the Google deal surfaced.

## Why India Matters to Intel's Foundry Bet

Intel's India operations are not peripheral to this story. The company's design centres in Bangalore and Hyderabad employ thousands of engineers working on chip verification, physical design, and process development — exactly the disciplines that determine whether Intel can deliver on foundry contracts at scale. When Google or Nvidia hands Intel a custom chip specification, a significant share of the design-for-manufacturing work flows through Indian teams.

The foundry pivot also creates a different kind of career gravity. Under the old Intel, the India centres were largely captive — designing chips for Intel's own product lines. Under the foundry model, those same engineers work on designs from multiple customers across AI, networking, and automotive. The skill set broadens, the client exposure deepens, and the career trajectories shift from "Intel chip designer" to "fab-agnostic process engineer" — a profile that is increasingly portable across the industry.

## The Competitive Chessboard

Monday's news lands in the middle of a semiconductor market still reeling from a $1.3 trillion rout last Friday, when the Philadelphia Semiconductor Index posted its worst single-day drop in six years. Broadcom's quarterly results, despite a 143 per cent surge in AI chip revenue, missed sky-high expectations. TSMC, which fabricates roughly 90 per cent of the world's most advanced AI chips, fell 6 per cent even as Nvidia CEO Jensen Huang pledged to invest $150 billion annually in Taiwan.

Intel's proposition is simple: the world cannot afford to have all its advanced chips made in one place by one company. The US CHIPS Act has poured billions into domestic fab construction, and Intel is the primary American beneficiary. If Google and Nvidia sign on as external customers, it lends credibility to an alternative that Washington is desperate to fund and the market is desperate to believe.

## The NRI Calculus

For Indian-origin chip professionals, Intel's foundry renaissance creates both pull and push. In the US, a successful Intel foundry means more process engineering and EDA roles in Oregon and Arizona — positions that carry strong H-1B sponsorship prospects. In India, the expanding Bangalore design centre is absorbing experienced engineers who might once have looked exclusively at TSMC or Samsung.

The stock's trajectory will depend on execution, not announcements. But for the first time in years, Intel is a company that the best semiconductor engineers in the world — many of them Indian — are willing to bet their careers on again.
"""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Google Just Ordered Three Million AI Chips From Intel. The Foundry Bet Is Paying Off.",
    "subheadline": "Reports of a landmark manufacturing deal with Google — and a potential Nvidia contract — sent Intel shares up 12 per cent. Thousands of Indian engineers in Bangalore and Hyderabad are at the centre of the foundry pivot.",
    "slug": make_slug("intel-foundry-google-nvidia-chips-india-engineers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Intel's Bangalore and Hyderabad centres employ thousands of Indian engineers doing chip verification and physical design — the exact work that scales with foundry contracts. The pivot also creates new H-1B-eligible process engineering roles in Oregon and Arizona.",
    "tags": ["intel", "foundry", "google", "nvidia", "semiconductor", "indian-engineers", "lip-bu-tan"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Investopedia", "url": "https://www.investopedia.com/intel-s-stock-is-soaring-hopes-of-chipmaking-deals-with-google-and-nvidia-are-lifting-the-shares-intc-nvda-goog-11993112"},
        {"name": "The Information", "url": "https://www.theinformation.com"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/alphabet-taps-intel-to-make-three-million-in-house-chips-the-information-reports-2026-06-09/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/10/Howard_Lutnick_with_Intel_CEO_Lip-Bu_Tan_%282025%29_%28cropped3%29.jpg",
    "image_caption": "Intel CEO Lip-Bu Tan, who has led the company's foundry pivot since March 2025",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}


# ─────────────────────────────────────────────────────────────────────
# Validate images & insert
# ─────────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    print(f"\n{'='*60}")
    print(f"Processing: {art['headline'][:70]}...")
    print(f"Slug: {art['slug']}")

    # Validate image
    if art.get("image_url"):
        if not validate_image(art["image_url"]):
            print("  ⚠ Image validation failed — clearing image_url")
            art["image_url"] = None
            art["image_caption"] = None
            art["image_attribution"] = None

    try:
        sb_post("p2_articles", art)
        print(f"  ✅ Inserted successfully")
    except Exception as e:
        print(f"  ❌ Insert failed: {e}")
