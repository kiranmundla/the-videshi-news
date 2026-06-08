#!/usr/bin/env python3
"""Videshi Technology Writer - 2026-06-08 06:00 UTC"""
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

def verify_image(url):
    """Verify image URL returns valid image content."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD fails
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        return r.status_code == 200 and "image" in ct and cl > 5000
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: Hyperscaler Custom Chip Race
# ═══════════════════════════════════════════════════════════════════════

art1_body = """Amazon's custom silicon business — encompassing the Graviton processor, the Trainium AI chip, and the Nitro networking chip — hit a $20 billion annual revenue run rate in Q1 2026. CEO Andy Jassy dropped an even more telling figure during the earnings call: "If our chips business was a stand-alone business and sold chips produced this year to AWS and other third parties as other leading chip companies do, our annual revenue run rate would be $50 billion."

That would make Amazon one of the top three data centre chip businesses in the world. And it is not alone. Alphabet has designed tensor processing units for over a decade, and 2026 is the year those chips moved beyond Google's own walls. Blackstone committed $5 billion to a joint venture offering TPUs as a rentable cloud service, with 500 megawatts of capacity coming online in 2027. Anthropic secured access to as many as one million TPUs. Meta reportedly has a leasing deal for them too.

Microsoft, furthest behind of the trio, has its Maia accelerator. The second-generation Maia 200 recently went live in some data centres, serving Microsoft 365 Copilot and OpenAI's models. The vast majority of AI work inside Azure still runs on Nvidia GPUs, but the direction is clear.

## The Paradox Nobody Can Explain Away

Here is the contradiction that defines the AI chip market right now: the three companies racing hardest to build their own chips are also spending record amounts on Nvidia's.

Amazon plans roughly $200 billion in capital expenditures in 2026. Microsoft expects to invest $190 billion. Add Alphabet and Meta, and the combined capex for the four hyperscalers tops $725 billion — up 77% from last year. Much of that still flows to Nvidia, whose data centre revenue surged 92% year over year to $81.6 billion in its most recent quarter.

"Demand has gone parabolic," Nvidia CEO Jensen Huang said on the earnings call, pointing to a tier of buyers — AI start-ups, enterprises, and governments — that "do not build chips, do not design their own chips."

## Where Indian Engineers Sit in This Race

This matters for Indian tech professionals in a direct, tangible way. All three hyperscalers employ thousands of Indian-origin engineers in their chip design divisions, from Austin and Cupertino to Hyderabad and Bengaluru. AWS's Annapurna Labs, the Israeli subsidiary that designs Graviton and Trainium, has expanded its India design centre. Google's TPU team in Bengaluru has grown substantially. Microsoft's Maia effort draws on its India engineering hub.

For Indian chip designers on H-1B visas in the Bay Area or Seattle, the custom silicon boom is a rare bright spot in a job market otherwise clouded by AI-driven restructuring. These are roles where hardware expertise commands a premium — and where Indian-origin engineers, who account for a disproportionate share of US semiconductor design talent, have structural advantage.

## What NRI Investors Should Watch

The investment calculus is nuanced. Custom silicon chips could erode Nvidia's pricing power over time. But the overall pool of AI spending is still expanding fast enough that Nvidia could keep growing even as it loses share at the margin. At a price-to-earnings ratio of about 32, the bigger risk may not be that in-house chips fail — it is that they succeed slowly while the market keeps pricing Nvidia for permanent dominance.

For NRI investors holding Nvidia, the hyperscaler chip race is not an immediate sell signal. It is a reason to diversify within the AI supply chain — and to pay attention to the Indian engineers quietly designing the chips that may eventually reshape it.

*Sources: Motley Fool analysis of hyperscaler capex, Amazon Q1 2026 earnings call, Nvidia fiscal Q1 FY2027 earnings call, Reuters reporting on Alphabet TPU partnerships*"""

art1_img = "https://images.pexels.com/photos/5203849/pexels-photo-5203849.jpeg"
if not verify_image(art1_img):
    art1_img = "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg"

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: Perfios Unicorn
# ═══════════════════════════════════════════════════════════════════════

art2_body = """On June 4, Bengaluru-headquartered Perfios raised $80 million from Teachers' Venture Growth (TVG), the late-stage investment arm of the Ontario Teachers' Pension Plan. The round values the company at over $1 billion, making it India's latest confirmed fintech unicorn. It is the sort of announcement that barely registers in a news cycle dominated by consumer apps and IPO drama. That is exactly what makes it significant.

Perfios is not a consumer brand. You have almost certainly never heard of it. What you may not realise is that your loan application in Southeast Asia, your insurance claim in the Gulf, or your credit score check in Africa probably ran through its systems. The company operates in the infrastructure layer: credit underwriting, financial data aggregation, bank statement analysis, and fraud detection — deployed across 18 countries and serving over 1,000 financial institutions.

## The Export Nobody Noticed

Founded in 2008 by VR Govindarajan and Debasish Chakroborty — both former Aztecsoft founders — Perfios represents a category of Indian tech company that rarely makes headlines but increasingly matters. The B2B fintech infrastructure stack is quietly becoming India's most important technology export, not the consumer apps that dominate front pages.

Think of it this way: while Paytm, PhonePe, and CRED compete for Indian wallets, Perfios is building the plumbing that banks in Jakarta, Dubai, and Nairobi use to make lending decisions. Its credit decisioning, data aggregation, and compliance rails are the kind of unglamorous technology that scales without fanfare.

The $80 million from a Canadian pension fund — following a $229 million Series D from Kedaara Capital in 2025 — validates this thesis at institutional scale. TVG's investment is earmarked for global expansion and acquisition-led growth, signalling that the next phase is not about building more features but about buying companies in new markets.

## Why NRIs Should Pay Attention

For Indian Americans tracking India's startup ecosystem, Perfios is a template worth studying. The company has been profitable or near-profitable for much of its existence, a rarity among Indian unicorns. Its revenue comes from enterprise contracts with banks, not from consumer subsidies that evaporate when funding dries up.

The broader signal is structural. India has 127 unicorns as of June 2026. The ones that will matter in five years are not the ones burning through venture capital to acquire users. They are the ones like Perfios — infrastructure businesses with sticky enterprise relationships and genuine global reach.

For NRI founders considering the India market, the message is equally clear. The opportunity is not in building another consumer fintech. It is in building the rails that financial systems everywhere need — the credit scoring, compliance, and data aggregation infrastructure that the post-UPI world requires. India designed the architecture. Now Indian companies are exporting it.

## What Comes Next

Perfios's immediate roadmap involves expansion into North America and Europe — markets where regulatory complexity in banking creates exactly the kind of data-aggregation challenges that the company has spent 18 years solving. With the Ontario Teachers' backing, expect acquisitions in these geographies.

The larger question is whether Perfios will go public, and if so, where. An Indian IPO seems likely given the current market appetite for B2B SaaS companies. For NRI investors who missed the Freshworks listing and have been waiting for a profitable, enterprise-grade Indian SaaS story, Perfios may be the one worth watching.

*Sources: LinkedIn report on Perfios funding round (June 4, 2026), YourStory reporting on Kedaara Capital Series D, Inc42 Indian Startup IPO Tracker 2026, Tracxn India startup data*"""

art2_img = "https://images.pexels.com/photos/30214870/pexels-photo-30214870.jpeg"
if not verify_image(art2_img):
    art2_img = "https://images.pexels.com/photos/35638979/pexels-photo-35638979.jpeg"

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 3: Anthropic IPO
# ═══════════════════════════════════════════════════════════════════════

art3_body = """Anthropic, the maker of Claude, confidentially filed for an IPO on June 1, days after closing a $65 billion Series H round that valued the company at $965 billion. When it debuts — expected this fall — it could clear $1 trillion. That would make it the most valuable company to go public since Saudi Aramco. And the two biggest winners may not be Anthropic's own shareholders.

Amazon and Alphabet — companies led by Andy Jassy and Sundar Pichai respectively — hold substantial equity stakes in Anthropic. More importantly, they hold the infrastructure contracts. Anthropic has committed to spending more than $100 billion with Amazon Web Services over the next decade, securing up to 5 gigawatts of AI compute capacity. Separate agreements with Google lock in another 5 gigawatts. That is 10 gigawatts of contracted demand from a single company, before the IPO even happens.

## The Numbers That Explain the Frenzy

Anthropic's annualised recurring revenue hit $47 billion by late May — roughly five times the levels seen in December. Growth at that pace explains why investors flooded the latest round. Altimeter Capital, Dragoneer, Greenoaks, and Sequoia led the Series H. Capital Group, Blackstone, Fidelity, and Temasek joined as major participants.

For context, OpenAI's most recent private valuation was lower. Anthropic has, at least on paper, overtaken its rival as the most valuable AI lab in the world. The company has differentiated itself through safety-focused AI development and strong enterprise adoption — Claude for coding and complex analytical tasks has found particular traction in corporate settings.

## The Sundar Pichai Connection

For the Indian diaspora, the Anthropic story is inseparable from the story of Indian-origin tech leadership.

Sundar Pichai's Alphabet is not just an investor. Google Cloud provides the TPU infrastructure that Anthropic uses for training. The Blackstone-Google TPU joint venture announced in May — with its $5 billion initial commitment — is partly designed to serve exactly this kind of AI lab demand. When Anthropic goes public at a trillion-dollar valuation, Google's equity stake and infrastructure revenue both appreciate.

Alphabet's investment in Anthropic sits alongside its broader AI strategy: keep the most important AI labs dependent on Google infrastructure, even as they compete with Google's own models. It is a strategic bet that Pichai has executed more deftly than most observers expected.

## The $4 Trillion IPO Wave

Anthropic is not the only mega-IPO on the horizon. SpaceX is expected to debut on June 12 at a $1.77 trillion valuation. OpenAI is also expected to go public before year-end. The trio could raise $240 billion at a combined valuation exceeding $4 trillion.

For NRI investors, the sheer scale demands caution. Anthropic's $47 billion in ARR on a $1 trillion valuation implies a roughly 21x revenue multiple — rich by any standard, though cheaper than SpaceX's 95x. The real question is whether AI revenue can sustain this trajectory once enterprise contracts mature and competition from open-source models intensifies.

The safer play may be the infrastructure beneficiaries rather than the AI labs themselves. Nvidia, whose GPUs Anthropic still uses alongside custom silicon, generated $81.6 billion in data centre revenue last quarter. Micron, led by Indian-origin CEO Sanjay Mehrotra, makes the high-bandwidth memory that every AI accelerator requires. And Broadcom, whose custom chips power Google's TPU alternatives, booked $30 billion in AI chip orders in a single quarter.

## What Indian AI Founders Should Learn

Anthropic was founded in 2021 by former OpenAI executives, including CEO Dario Amodei. In five years, it went from zero to a potential trillion-dollar valuation. The playbook — safety-first positioning, deep hyperscaler partnerships, enterprise focus over consumer hype — offers lessons for Indian AI startups like Sarvam AI and Krutrim.

But the clearest lesson is about infrastructure. Anthropic's value is inseparable from its compute agreements. Without 10 gigawatts of contracted capacity from Amazon and Google, the models do not exist. For Indian AI founders, the implication is stark: building a frontier AI company requires infrastructure partnerships at a scale that few Indian companies can currently access. AirTrunk's recently announced $30 billion India data centre investment may begin to change that equation.

*Sources: Motley Fool reporting on Anthropic IPO and infrastructure beneficiaries, FXStreet analysis of SpaceX and Anthropic IPOs, WebProNews analysis of Anthropic valuation, Reuters reporting*"""

art3_img = "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg"
if not verify_image(art3_img):
    art3_img = "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg"


# ═══════════════════════════════════════════════════════════════════════
# ASSEMBLE ARTICLES
# ═══════════════════════════════════════════════════════════════════════

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Amazon's Chip Business Just Hit $20 Billion. Three Hyperscalers Are Quietly Building the Post-Nvidia World.",
        "subheadline": "Amazon, Alphabet, and Microsoft are designing their own AI processors — while still spending $725 billion on Nvidia's. Indian engineers are at the centre of both sides of that bet.",
        "slug": make_slug("amazon-chip-business-20-billion-hyperscaler-custom-silicon"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Thousands of Indian-origin chip designers at AWS Annapurna Labs, Google TPU Bengaluru, and Microsoft Maia teams are leading the custom silicon revolution. For H-1B chip designers, this boom is a rare bright spot. NRI investors holding Nvidia should watch the diversification signal.",
        "tags": ["ai-chips", "amazon", "google", "microsoft", "nvidia", "custom-silicon", "indian-engineers", "semiconductor"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Motley Fool", "url": "https://www.fool.com/investing/2026/06/07/amazon-alphabet-and-microsoft-are-all-racing-to-de/"},
            {"name": "Amazon Q1 2026 Earnings Call", "url": "https://ir.aboutamazon.com/"},
            {"name": "Nvidia Q1 FY2027 Earnings", "url": "https://investor.nvidia.com/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": art1_img,
        "image_caption": "Server racks in a modern data centre — the new battleground for custom AI chip design",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": art1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Perfios Just Hit Unicorn Status. It Proves India's Biggest Fintech Export Isn't an App.",
        "subheadline": "A Bengaluru company you have never heard of processes credit decisions for banks in 18 countries. A Canadian pension fund just valued it at over $1 billion.",
        "slug": make_slug("perfios-unicorn-india-fintech-infrastructure-export"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Perfios represents the Indian B2B fintech infrastructure stack becoming a global export — the credit decisioning and compliance rails that banks in Southeast Asia, the Gulf, and Africa are building on. For NRI founders and investors, it signals that infrastructure beats consumer branding.",
        "tags": ["fintech", "perfios", "unicorn", "india-startups", "b2b-saas", "banking-infrastructure", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "LinkedIn/Crypto & Fintech Weekly", "url": "https://www.linkedin.com/"},
            {"name": "YourStory", "url": "https://yourstory.com/2023/09/fintech-unicorn-perfios-raises-229m-from-kedaara-capital"},
            {"name": "Inc42", "url": "https://inc42.com/features/indian-startup-ipo-tracker-2026/"},
            {"name": "Tracxn", "url": "https://tracxn.com/d/trending-themes/startups-in-india"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": art2_img,
        "image_caption": "Financial analytics dashboard showing data-driven decision tools — the kind of infrastructure Perfios builds for banks worldwide",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": art2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Anthropic Just Filed for a Trillion-Dollar IPO. The Biggest Winners Are Already in Sundar Pichai's Orbit.",
        "subheadline": "The Claude maker's $965 billion valuation makes it the most valuable AI lab on paper. But the real money flows to the infrastructure providers — two of them run by Indian-origin leadership.",
        "slug": make_slug("anthropic-ipo-trillion-dollar-sundar-pichai-google-amazon"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Sundar Pichai's Alphabet holds equity in Anthropic and provides TPU infrastructure for training. Anthropic has $100B+ in compute agreements with Amazon and Google. For NRI investors, the infrastructure beneficiaries — including Micron (Sanjay Mehrotra) and Broadcom — may be the smarter play.",
        "tags": ["anthropic", "ipo", "ai", "sundar-pichai", "google", "amazon", "claude", "nri-investors", "trillion-dollar"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Motley Fool", "url": "https://www.fool.com/investing/2026/06/07/anthropic-ipo-ai-stocks-winners/"},
            {"name": "FXStreet", "url": "https://www.fxstreet.com/analysis/spacex-and-anthropic-the-most-exciting-ipos-ever-202606042342"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/anthropics-looming-trillion-dollar-debut/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": art3_img,
        "image_caption": "Dario Amodei, CEO and co-founder of Anthropic, at TechCrunch Disrupt",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": art3_body
    },
]


for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
