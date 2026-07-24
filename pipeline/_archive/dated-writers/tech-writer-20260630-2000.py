#!/usr/bin/env python3
"""
Videshi Technology Writer — 2026-06-30 20:00 PT
Three articles:
  1. Microsoft layoffs 2.5% + Xbox devastation
  2. Open USD stablecoin launch (Visa, Mastercard, Google, 140+ companies)
  3. Tata Communications management overhaul after data center fire
"""
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
    return slug[:70].rstrip('-') + "-20260701"

articles = [
    # ─────────────────────────────────────────────────────────────────────
    # ARTICLE 1: Microsoft Layoffs 2.5% + Xbox Devastation
    # ─────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Nadella's Microsoft Is About to Cut 5,700 Jobs. Xbox May Never Recover.",
        "subheadline": "A 2.5% workforce reduction across sales, consulting, and gaming is expected as early as next week — with the Xbox division bracing for what insiders call the largest single layoff event in gaming history.",
        "slug": make_slug("microsoft-5700-layoffs-xbox-gaming-nadella-h1b"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Microsoft is one of the largest H-1B employers in the US. Thousands of Indian engineers in Redmond, Hyderabad, and Bangalore face an uncertain July as the company restructures around AI — and the 60-day visa clock starts ticking for anyone caught in the cuts.",
        "tags": ["microsoft", "layoffs", "xbox", "satya-nadella", "h1b", "ai-restructuring"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/microsoft-cut-under-25-workforce-latest-layoffs-business-insider-reports-2026-07-01/"},
            {"name": "Business Insider", "url": "https://www.businessinsider.com/microsoft-layoffs-2026"},
            {"name": "Screen Rant", "url": "https://screenrant.com/xbox-largest-single-layoff-event-gaming-history/"},
            {"name": "GameSpot", "url": "https://www.gamespot.com/articles/amid-xbox-reset-microsoft-is-having-its-worst-month-in-26-years/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Microsoft CEO Satya Nadella at a company event",
        "image_attribution": "Wikimedia Commons",
        "body": """Microsoft is preparing to cut under 2.5% of its global workforce — roughly 5,700 jobs from its 228,000-strong headcount — in a fresh round of layoffs that could be announced as early as next week, Business Insider reported on Tuesday, citing people familiar with the plans.

The cuts will hit sales, consulting, and the Xbox gaming division, where insiders describe the looming restructuring as potentially "the largest single layoff event in gaming history." Several Xbox-backed studios are reportedly set to close, and the layoff decisions are expected to be finalised around the end of Microsoft's fiscal year on June 30, with execution beginning in the first week of July.

## The Xbox Reckoning

The gaming division is taking the heaviest blow. Asha Sharma, the Indian-American executive installed as Xbox's new CEO earlier this year, has publicly declared the unit's 3% profit margin unsustainable after Microsoft spent close to $100 billion on studio acquisitions — including the $69 billion Activision Blizzard King purchase in 2023 and the $7.5 billion ZeniMax deal in 2021.

CFO Amy Hood has reportedly "demanded a variety of savings at Xbox to offset losses," according to Windows Central. Studios including Arkane, Double Fine, Compulsion Games, and Ninja Theory are reportedly fighting for survival, with some potentially closing outright and others seeking to buy back their independence.

The scale would surpass Xbox's previous worst — 1,900 gaming-specific cuts in January 2024 — by a significant margin. Veteran game developer George Broussard warned that "Xbox is going to be supremely unpopular for a very long time and the devastation is going to reverberate like the meteor that took out the dinosaurs."

## A Broader Pattern

Microsoft's cuts are part of an accelerating industry trend. The company laid off nearly 4% of its workforce in July 2025. Meta announced plans this year to cut 10% of its staff. Amazon has eliminated roughly 16,000 positions. Oracle quietly shed 21,000 employees — 13% of its workforce — and blamed AI.

The common thread: every one of these companies is simultaneously pouring billions into AI infrastructure while slashing the human workforce that built their existing businesses.

## What This Means for Indian Workers

For the Indian tech diaspora, Microsoft's cuts carry particular weight. The company is consistently one of the top H-1B visa sponsors in the United States, with thousands of Indian engineers working across its Redmond campus, cloud operations, and enterprise services divisions.

Under USCIS rules, H-1B workers who lose their jobs get a 60-day grace period to find a new sponsoring employer, switch visa categories, or leave the country. With 185,000 tech layoffs already recorded in 2026 according to Layoffs.fyi, the job market for displaced visa holders is thinning rapidly.

The sales and consulting roles being cut are precisely the functions where Indian IT services firms like TCS, Infosys, and Wipro have historically placed large numbers of employees at Microsoft as vendors and subcontractors. Any contraction in Microsoft's enterprise operations sends ripples through India's entire IT services ecosystem.

Microsoft's stock has already had its worst month in 26 years, falling significantly as investors weigh the cost of its AI pivot against the return so far. For NRI investors with significant Microsoft holdings — and the company is one of the most widely held stocks among Indian-American tech workers — the coming weeks will test whether Nadella's bet on AI infrastructure can outrun the mounting human and financial costs of getting there.

The restructuring also raises a harder question: if a company led by one of the most prominent Indian-origin CEOs in the world is cutting at this pace, what does that signal about the broader tech employment landscape that has been the engine of Indian professional immigration to America for three decades?"""
    },

    # ─────────────────────────────────────────────────────────────────────
    # ARTICLE 2: Open USD Stablecoin Launch
    # ─────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Visa, Mastercard, and Google Just Launched a Stablecoin. It Has 140 Partners and Zero Fees.",
        "subheadline": "Open USD, backed by a consortium that includes BlackRock, Stripe, and Coinbase, is designed to become the default digital dollar for global payments — and it could reshape how NRIs send money home.",
        "slug": make_slug("open-usd-stablecoin-visa-mastercard-google-nri-remittances"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "Indian Americans send over $100 billion in remittances annually. A zero-fee, consortium-backed stablecoin endorsed by the payment networks they already use could dramatically lower the cost of moving money between the US and India — if RBI regulations allow it.",
        "tags": ["stablecoin", "open-usd", "visa", "mastercard", "crypto", "nri-remittances", "fintech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/consortium-including-visa-mastercard-jointly-launch-new-global-stablecoin-2026-06-30/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/finance/currencies/blackrock-google-join-banks-and-crypto-firms-in-backing-new-stablecoin-e4c5c901"},
            {"name": "The Block", "url": "https://www.theblock.co/post/open-usd-stablecoin-launch"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/circle-internet-sinks-open-usd-stablecoin-rival-ba8d1cc3"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/34067360/pexels-photo-34067360.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A Bitcoin coin alongside financial data and credit cards on a desk",
        "image_attribution": "Pexels",
        "body": """A consortium of more than 140 companies — including Visa, Mastercard, Google, BlackRock, Stripe, and Coinbase — on Tuesday launched Open USD, a new U.S.-dollar-pegged stablecoin designed to become the default digital currency for global payments.

The venture, operated by a new company called Open Standard, represents the most significant institutional push yet to bring stablecoins into mainstream commerce. Unlike existing stablecoins controlled by a single issuer, Open USD will be governed by an independent board drawn from its partner companies, with reserve earnings shared among participants after a management fee.

"Existing stablecoins have great strengths, but to use them at scale, businesses need something that's open, low-cost, high-throughput, broadly accessible, and aligned to their interests," said Open Standard CEO Zach Abrams, who previously co-founded a stablecoin startup acquired by Stripe.

## The Partner List Is the Story

The breadth of the consortium is what sets Open USD apart. The payment networks — Visa, Mastercard, American Express, and Discover — are joined by banks including BNY, U.S. Bank, BBVA, and Standard Chartered. Technology firms such as Google, IBM, Samsung, and Shopify sit alongside crypto-native companies including Coinbase, Ripple, OKX, and MetaMask.

Even DoorDash is in. "What sets Open USD apart is that it's genuinely open: no single company controls it, and the partners building on it have a seat at the table," said DoorDash co-founder Andy Fang.

Stripe's president of technology, Will Gaybrick, indicated that Open USD is intended to become the default stablecoin for businesses using Stripe's payment infrastructure — a signal that could push rapid adoption across the millions of merchants on Stripe's platform.

## The USDC Threat

The announcement sent Circle Internet Group's stock plunging 18% on Tuesday. Circle, which co-founded the USDC stablecoin with Coinbase, has long dominated the U.S. stablecoin market with about $73.6 billion in outstanding USDC. Coinbase's own shares fell 6%, despite the company being both an Open USD partner and a USDC co-founder — a potentially awkward straddling of two competing ecosystems.

The combined stablecoin market currently stands at roughly $260 billion, dominated by Tether's USDT and Circle's USDC. Open USD's zero-fee minting and redemption model, combined with the revenue-sharing structure, could undercut both incumbents by offering partners direct economic incentives to integrate and promote OUSD.

## Why NRIs Should Be Watching

India is the world's largest remittance recipient, with Indians abroad sending over $100 billion home annually. The current system — wire transfers through banks, services like Wise or Remitly, or hawala networks — typically costs between 1% and 5% per transaction.

A zero-fee, dollar-pegged stablecoin backed by the payment networks that already process most global transactions could fundamentally alter this equation. If Visa and Mastercard route remittance flows through Open USD rails instead of traditional correspondent banking, the cost savings for the diaspora could be substantial.

The obstacle, as always, is regulation. The Reserve Bank of India has maintained a cautious stance on private cryptocurrencies, even as it develops its own digital rupee (e-₹). Whether Open USD — essentially a digital dollar backed by BlackRock and the world's largest payment networks — receives different treatment than speculative crypto tokens remains an open question.

The GENIUS Act, signed into law by President Trump last year, established the first federal framework for stablecoins in the U.S. That regulatory clarity is precisely what enabled this consortium to form. India has no equivalent framework yet.

For NRI investors, the immediate market impact is already visible: Circle's 18% stock drop is a reminder that even in crypto, incumbency offers no protection when the world's largest financial institutions decide to build their own. The longer-term question — whether Open USD becomes the payments layer that makes sending money to India as cheap as sending a WhatsApp message — will take longer to answer."""
    },

    # ─────────────────────────────────────────────────────────────────────
    # ARTICLE 3: Tata Communications Management Overhaul
    # ─────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Tata Communications Has Replaced Its CEO, CFO, and CTO in Five Months. A Data Centre Fire Explains Why.",
        "subheadline": "The Indian telecom giant's third C-suite appointment of 2026 brings in an Akamai and AT&T veteran as CTO, as the company races to rebuild credibility after a devastating fire at its New Delhi data centre and accelerate its AI infrastructure push.",
        "slug": make_slug("tata-communications-cto-chokshi-management-overhaul-data-centre"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Tata Communications runs the backbone infrastructure that connects India's digital economy to the world — and its data centres are where many NRI-facing services actually live. A leadership reset of this scale at a Tata Group company signals both crisis and ambition.",
        "tags": ["tata-communications", "tata-group", "data-centre", "cto", "leadership", "ai-infrastructure", "india-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-tata-communications-names-new-chief-technology-officer-2026-06-30/"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/indias-tata-communications-appoints-rupesh-chokshi-as-new-cto"},
            {"name": "Light Reading", "url": "https://www.lightreading.com/data-center/tata-comms-bets-on-high-end-data-centers-as-ai-demand-surges"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/tata-communications-tcs-data-centre-investment"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Server racks in a modern data centre highlighting network infrastructure",
        "image_attribution": "Pexels",
        "body": """Tata Communications on Tuesday appointed Rupesh Chokshi as its new chief technology officer, the company's third C-suite change in five months — a pace of executive turnover that underscores both the urgency of its recovery from a catastrophic data centre fire and the scale of its ambitions in AI infrastructure.

Chokshi, who most recently served as senior vice president and general manager of application security at Akamai Technologies, also held senior leadership roles at AT&T. He replaces Genius Wong, who resigned citing personal reasons. Alongside Chokshi, the company named Vivek Srivastava as Executive Vice President and Business Head for Cloud and Cyber Security Services.

## A Company in Transition

The CTO appointment follows a pattern that would be unusual for any company, let alone one in the Tata Group. In February, Tata Communications installed a new chief financial officer. In May, it named Ganesh Lakshminarayanan as CEO. Now, in June, the CTO slot has turned over as well.

Three C-suite replacements in 150 days is not normal corporate succession planning. It is a deliberate reset — and the June 5 data centre fire in New Delhi helps explain why.

## The Fire That Changed Everything

Earlier this month, a fire broke out at a New Delhi data centre jointly owned by Tata Communications and Singapore's ST Telemedia Global Data Centres. Reuters reported that the blaze caused extensive damage to parts of the facility and made data recovery challenging — a diplomatically worded way of saying that customer data may have been permanently lost.

For a company whose core business is enterprise connectivity and data infrastructure, a data centre fire is not a routine operational incident. It is an existential reputational event. Enterprises trust Tata Communications with their most critical workloads precisely because of the Tata name and the assumption of world-class facility management. A fire that compromises data recovery undermines that trust at its foundation.

The management overhaul, viewed in this light, is as much about signalling renewed accountability as it is about bringing in fresh technical leadership.

## The AI Infrastructure Bet

The leadership changes also coincide with Tata Communications' most aggressive infrastructure expansion in years. The company is accelerating its AI-digital infrastructure, cloud connectivity, and subsea network expansion — positioning itself as the connectivity backbone for India's rapidly growing data centre ecosystem.

In partnership with sister company TCS, Tata Communications is part of a $6.5 billion initiative to build one gigawatt of new data centre capacity across India. The collaboration, announced earlier this year, represents a "One Tata" strategy to create an integrated digital infrastructure stack — combining TCS's enterprise AI and managed services capabilities with Tata Communications' network and connectivity strengths.

The company has also been expanding its partnerships with global hyperscalers. A collaboration with AWS to jointly design connectivity architectures for AI and cloud workloads across Mumbai, Hyderabad, and Chennai was described as one of India's largest-ever network deployments.

Chokshi's background in application security at Akamai — one of the world's largest content delivery and cybersecurity companies — is a pointed choice for a company that just suffered a facility-level security failure. His AT&T experience adds deep knowledge of carrier-grade network operations at scale.

## Why It Matters to the Diaspora

Tata Communications may not have the consumer visibility of a TCS or a Tata Motors, but its infrastructure runs underneath much of India's digital economy. It operates one of the world's largest subsea cable networks, carries a significant share of India's international internet traffic, and provides the data centre and connectivity services that power banking, e-commerce, and government digital platforms.

For NRI investors, the stock tells part of the story: Tata Communications shares have pulled back from their 52-week high of ₹2,110 to around ₹1,970, reflecting the overhang from the fire and management uncertainty. The question now is whether the leadership reset — combined with the massive AI infrastructure buildout — can restore both operational confidence and investor sentiment.

The deeper signal is about India's readiness for the AI infrastructure boom. Global tech companies are pouring tens of billions into Indian data centres, and Tata Communications wants to be the connectivity layer that ties it all together. Whether a company still recovering from a burning building can credibly lead that charge is the test Chokshi and his new colleagues now face."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
