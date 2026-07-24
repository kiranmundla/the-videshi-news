#!/usr/bin/env python3
"""Videshi Technology Writer — July 6, 2026 14:00 PT run"""
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

# ─────────────────────────────────────────────
# ARTICLE 1: Microsoft Layoffs
# ─────────────────────────────────────────────
art1_body = """Satya Nadella's Microsoft disclosed on Monday that it would eliminate roughly 4,800 positions — about 2.1 per cent of its global workforce — in what amounts to the company's most sweeping restructuring since the pandemic-era cuts of 2023. The largest share of the pain falls on Xbox, where new gaming chief Asha Sharma described the business as "not healthy" and announced 3,200 role eliminations through fiscal 2027, with 1,600 effective immediately.

For Indian professionals on H-1B visas — who constitute the single largest national group in Microsoft's Redmond and Hyderabad engineering ranks — the cuts trigger a familiar anxiety. Laid-off H-1B holders have just 60 days to find a new employer willing to transfer their visa, or they must leave the country. Microsoft's April buyout programme, which offered voluntary exit to roughly 7 per cent of its US staff, gave some cushion; more than 30 per cent of eligible workers took it. But Monday's cuts were involuntary, and the clock starts now.

## The AI trade-off

The layoffs arrive at a striking moment in Nadella's tenure. Microsoft's stock has slumped 23 per cent in the first half of 2026 — its worst six-month run since 2022 — even as Azure's AI business has boomed. The company plans to spend $190 billion on data-centre infrastructure this year, a sum that would exceed the GDP of most countries. Something has to give, and headcount is the relief valve.

"Microsoft has been managing down its workforce in order to pay for its AI investments," said Gil Luria, managing director at D.A. Davidson. "By keeping headcount down they have been able to accelerate revenue growth while maintaining margins."

Chief People Officer Amy Coleman insisted the eliminated roles "are not being replaced by AI," but acknowledged the technology is "changing how work gets done." That distinction is cold comfort to the engineers whose positions have been deemed non-essential in an AI-first operating model.

## Xbox's reckoning

The gaming division's restructuring is the most dramatic in Xbox's 25-year history. Four studios — Compulsion Games, Double Fine Productions, Ninja Theory, and Undead Labs — will be sold or spun off. Sharma's memo was blunt: Xbox's margins run three to ten times lower than comparable platform businesses, and years of heavy investment in content and Game Pass failed to deliver expected growth.

For Indian gaming professionals who joined Microsoft's expanding studios in the US on work visas, the studio divestitures add a layer of uncertainty beyond standard layoffs. A sale to a smaller studio may not carry the same visa-sponsorship capacity as Microsoft itself.

## The broader wave

Microsoft is far from alone. Amazon and Meta have each shed thousands this year as Big Tech redirects capital from people to GPUs. The first quarter of 2026 brought 52,050 tech layoffs industry-wide — a 40 per cent jump from the prior year — with AI restructuring cited as the leading cause. Bank of America estimates that cloud and AI spending across the sector will reach $1.5 trillion next year, a 40 to 50 per cent increase that has to be funded from somewhere.

For Indian tech workers in the US, the pattern is becoming familiar and unnerving: the same companies that sponsor the largest share of H-1B visas are the ones most aggressively cutting non-AI roles. USCIS data shows Microsoft, Amazon, and Meta among the top ten H-1B sponsors. Each round of cuts narrows the runway for workers whose immigration status is tied to continuous employment.

## What NRIs should watch

The 60-day transfer window remains the critical variable. Immigration attorneys recommend that any H-1B holder at a company undergoing restructuring keep an updated LinkedIn profile, maintain relationships with recruiters, and — crucially — begin parallel green-card processing through EB-1 or EB-2 NIW where qualifications permit. Microsoft's own internal transfer system, which allows moves between teams without a new visa petition, remains a lifeline for those whose roles are eliminated but whose skills are in demand elsewhere within the company.

Nadella built his reputation on cultural transformation and empathy. The test now is whether the AI pivot he has championed can sustain the tens of thousands of Indian-origin engineers whose careers — and legal right to remain in the United States — depend on the company he leads."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Nadella's Microsoft Cuts 4,800 Jobs. Indian H-1B Workers Have 60 Days to Figure Out What's Next.",
    "subheadline": "The biggest Xbox restructuring in history and an AI-driven headcount squeeze put thousands of visa-dependent workers on the clock.",
    "slug": make_slug("microsoft-layoffs-4800-xbox-h1b-indian-workers"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Microsoft is among the top H-1B sponsors in the US; laid-off visa holders face a 60-day window to find new sponsorship or leave the country.",
    "tags": ["microsoft", "layoffs", "h1b", "satya-nadella", "xbox", "ai", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/microsoft-cut-about-3-percent-its-workforce-2026-07-07/"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/07/07/tech/microsoft-layoffs-xbox/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/07/07/business/microsoft-lays-off-nearly-5k-workers/"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/xboxs-ceo-says-the-business-is-not-healthy/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
    "image_caption": "Satya Nadella, CEO of Microsoft, at a company event",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ─────────────────────────────────────────────
# ARTICLE 2: SK Hynix Nasdaq Listing
# ─────────────────────────────────────────────
art2_body = """South Korea's SK Hynix is set to list American depositary receipts on the Nasdaq later this week in a deal that will raise roughly $28 billion — the second-largest share sale in history, trailing only SpaceX's record $85.7 billion IPO last month. For the memory-chip maker that supplies the high-bandwidth memory powering Nvidia's AI accelerators, the listing is both a capital raise and a strategic land-grab aimed squarely at one company: Sanjay Mehrotra's Micron Technology.

The timing is deliberate. SK Hynix's stock has tripled this year on the back of insatiable AI demand for its HBM chips. Micron, led by its Indian-origin CEO, has done even better — an 855 per cent surge over twelve months that lifted its market value past $1.1 trillion. By listing on the same exchange, SK Hynix will trade side-by-side with its American rival for the first time, giving institutional investors a direct comparison they have long wanted.

## The $28 billion play

SK Hynix plans to issue 17.8 million new shares, with ten ADRs representing one common share. Pricing, trimmed from an earlier target of 45.5 trillion won to 43.1 trillion won after a recent dip in Seoul trading, is due Thursday, with trading expected to begin Friday.

The proceeds will fund the buildout of chip-fabrication facilities in South Korea and the purchase of ASML's extreme-ultraviolet lithography scanners — the $350-million-a-pop machines without which no company can manufacture cutting-edge memory. The company is also expanding its packaging capacity for HBM chips, which stack multiple layers of DRAM and require advanced interconnect technology.

Samsung Electronics, the world's largest chipmaker and SK Hynix's domestic rival, will report preliminary second-quarter earnings the same week — a result expected to show a near 20-fold increase in profits driven by AI demand. Together, Samsung and SK Hynix's combined market value now exceeds 16 times that of the third-largest stock in the KOSPI index, a concentration that underscores how thoroughly AI has reshaped the Korean economy.

## What this means for Mehrotra's Micron

Micron has been the undisputed darling of the AI memory trade in American markets, largely because US investors had no easy alternative. SK Hynix's Korean-only listing kept it out of most mutual funds and ETFs. That changes this week.

Meritz Securities analyst Kim Sun-woo notes that the listing could help SK Hynix narrow the valuation gap with Micron — and potentially earn a spot in the Philadelphia Semiconductor Index, which would trigger passive-fund buying. For Mehrotra, whose careful positioning of Micron as "the AI memory company" has driven a quadrupling in its share price this year, the arrival of a well-capitalised competitor on home turf adds pressure to sustain an already extraordinary growth rate.

## The NRI investor angle

Indian-American investors who loaded up on Micron — one of the most popular semiconductor trades among NRI retail investors on platforms like Robinhood and Schwab — now face a portfolio question. SK Hynix trades at a meaningful discount to Micron on a price-to-earnings basis, partly because of the Korea listing discount and partly because its product mix skews more heavily toward the commodity DRAM market. The Nasdaq listing removes the first factor. Whether the second holds depends on SK Hynix's ability to capture a larger share of the premium HBM market, where Micron currently claims roughly 25 per cent.

Both companies are also building fabrication capacity that will create thousands of engineering jobs. Micron broke ground on a $9.3 billion cleanroom expansion in Hiroshima on July 4 and continues to ramp its Gujarat, India facility — a project that has generated significant interest among Indian semiconductor engineers considering a return home. SK Hynix's expansion is concentrated in South Korea, but its design and testing operations in the US employ a growing number of Indian-origin engineers.

## What to watch

The SK Hynix listing arrives during a wobbly moment for chip stocks. The Philadelphia Semiconductor Index has fallen 16 per cent from its late-June peak, and Micron itself has slipped 7 per cent since posting blowout earnings on June 24. If SK Hynix's debut absorbs investor capital that might otherwise flow to Micron, the memory trade could fracture in ways that punish both stocks. If it broadens investor appetite for the sector, both may rise. Friday's opening price will tell the story."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "SK Hynix Lands on Nasdaq With a $28 Billion War Chest. Sanjay Mehrotra's Micron Just Got Company.",
    "subheadline": "The second-largest share sale in history brings Nvidia's biggest memory-chip supplier to American markets — right next to its Indian-origin-led rival.",
    "slug": make_slug("sk-hynix-nasdaq-28-billion-listing-micron-mehrotra"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "NRI investors heavily exposed to Micron now face a direct competitor on the same exchange; Micron's Gujarat fab is a major draw for Indian semiconductor engineers.",
    "tags": ["sk-hynix", "micron", "sanjay-mehrotra", "nasdaq", "memory-chips", "ai", "semiconductor", "ipo"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/sk-hynix-us-listing-2026-07-06/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/samsung-earnings-sk-hynix-listing-ai-chip-rally/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/business/sk-hynix-trims-fundraising-target-for-us-listing/"},
        {"name": "Motley Fool", "url": "https://www.fool.com/investing/2026/07/06/sk-hynix-enters-us-chip-race/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Close-up of a microprocessor circuit board with intricate semiconductor components",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}

# ─────────────────────────────────────────────
# ARTICLE 3: Broadcom-Apple Edge AI Deal
# ─────────────────────────────────────────────
art3_body = """Apple and Broadcom have extended their chip-supply partnership through 2031 in a deal that locks in the world's most valuable company as a long-term customer for custom-designed artificial-intelligence silicon. The agreement, disclosed in a securities filing on Monday, expands well beyond the wireless-connectivity chips that have defined the relationship since 2010 — and positions Broadcom as the quiet architect of Apple's belated push into edge AI.

Broadcom shares jumped 4.1 per cent on the news, recovering some of a 25 per cent slide from their June highs. Apple, which has lagged every other member of the Magnificent Seven in articulating an AI strategy, is now locking in the silicon supply it needs to run AI models directly on iPhones, MacBooks, iPads, and Apple Watches — what the industry calls "edge inference."

## Beyond wireless: the ASIC pivot

The original Broadcom-Apple agreement, struck in 2023, focused on 5G radio-frequency components. Monday's extension covers a far broader portfolio of application-specific integrated circuits, or ASICs. JPMorgan analyst Harlan Sur identified touch-controller ASICs for iPhone, iPad, and MacBook; a wireless-charging ASIC for the iPhone; and likely a new power-management ASIC for both iPhone and Apple Watch.

More consequentially, Sur noted that Broadcom is co-designing a central processing unit for Apple's AI data-centre servers. "We believe that at some point, Apple will work with Broadcom on a full-blown AI XPU ASIC," he wrote, using the industry shorthand for a custom AI accelerator.

That would place Broadcom's Apple business alongside its existing custom-chip relationships with Google, Meta, and OpenAI — the last of which revealed its Broadcom-designed "Jalapeño" chip last month. Broadcom is building a franchise as the go-to designer for companies that want bespoke AI silicon without the years-long investment of developing it in-house.

## Why edge AI matters for Indian engineers

Broadcom's global engineering workforce includes a substantial contingent of Indian-origin chip designers, concentrated in its Bangalore, Hyderabad, and San Jose offices. The company's ASIC design methodology — which involves customising silicon for specific workloads rather than building general-purpose processors — is a discipline where Indian semiconductor engineers have historically excelled, particularly graduates of the IITs and BITS Pilani.

The expansion of the Apple partnership means more design work, more verification engineers, and more tape-outs — the industry term for finalising a chip design for manufacturing. For Indian engineers at Broadcom, the deal is job security and career growth wrapped in a five-year annuity.

"For Broadcom, it's a five-year annuity from the world's most demanding customer, stacked on top of the hyperscaler XPU ramp," said Daniel Newman, CEO of tech research firm Futurum Group. "Broadcom wins either way the AI cycle breaks."

## The supply-chain ripple

The deal also intersects with Apple's expanding manufacturing footprint in India. Tata Electronics and Foxconn now assemble a growing share of iPhones in India, and Broadcom's chips will sit inside those devices. As Apple pushes more AI processing to the device itself — reducing dependence on cloud-based inference — the quality and capability of the on-device silicon becomes critical.

Apple was forced to raise MacBook and iPad prices in June after memory-chip costs surged as much as 98 per cent in early 2026, driven by AI data-centre demand. Locking in Broadcom through 2031 gives Apple pricing predictability on a key component category at a time when chip costs are the most volatile they have been in a decade.

Meanwhile, the Broadcom-Apple relationship highlights a competitive dynamic with Qualcomm, which also supplies wireless chips to Apple but has been steadily losing share as Apple develops its own modem. Loop Capital analyst John Donovan speculated Monday that Broadcom might eventually sell its RF chip business, with Apple as a likely buyer — a move that would further consolidate Apple's control over its supply chain.

## The NRI portfolio read

For NRI investors, the Broadcom-Apple extension is a signal that the AI hardware trade is broadening beyond the obvious names. Broadcom stock, at $375, trades at a significant discount to its June highs and carries a diversified revenue base spanning data-centre AI, enterprise networking, and now a deepened Apple annuity. It is, in many ways, the "picks and shovels" play in edge AI — the layer beneath the device brands that consumers see.

Apple's own stock, meanwhile, faces a different question: whether pushing AI to the edge can generate the kind of revenue growth that cloud-first competitors like Google and Microsoft have delivered. The Broadcom deal suggests Apple is betting it can — and is willing to commit through the end of the decade to find out."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Apple Just Locked In Broadcom Through 2031. The Edge AI Race Has Its First Long-Term Bet.",
    "subheadline": "A sweeping custom-chip deal positions Broadcom as the silicon backbone of Apple's on-device AI strategy — and creates years of design work for Indian engineers.",
    "slug": make_slug("apple-broadcom-edge-ai-asic-deal-2031-indian-engineers"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Broadcom's large Indian engineering workforce in Bangalore, Hyderabad, and San Jose will drive the expanded ASIC design pipeline; NRI investors track AVGO as a diversified AI play.",
    "tags": ["apple", "broadcom", "edge-ai", "semiconductor", "asic", "chip-design", "indian-engineers"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/broadcom-apple-extend-chip-supply-deal-through-2031/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/broadcom-stock-jumps-apple-edge-ai/"},
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/broadcom-stock-rises-apple-supply-deal/"},
        {"name": "JPMorgan Research (via IBD)", "url": "https://www.investors.com/news/technology/broadcom-stock-rises-apple-supply-deal/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/28215391/pexels-photo-28215391.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Close-up of a patterned silicon wafer used in semiconductor chip manufacturing",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}

# ─────────────────────────────────────────────
# Insert all articles
# ─────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
