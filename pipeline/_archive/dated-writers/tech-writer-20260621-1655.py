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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "UPI Just Went Live in a Paris Department Store. The Real Target Isn't Tourists — It's Visa and Mastercard.",
        "subheadline": "India's payments rail now works at Galeries Lafayette, the second country launch this month. For NRIs, the question is whether 'pay in rupees abroad' finally becomes routine.",
        "slug": make_slug("upi-france-galeries-lafayette-live-npci-lyra-nri-diaspora"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "NRIs who shuttle between India and Europe now have a path to skip card-network forex markups when paying at French retailers, and a stake in whether India's homegrown payments stack can scale outside the diaspora.",
        "tags": ["upi", "fintech", "npci", "india-france", "digital-public-infrastructure", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Whizsky — India Launches UPI in France", "url": "https://whizsky.com/india-launches-upi-in-france-expands-global-reach/"},
            {"name": "Daily Kiran — Piyush Goyal Launches UPI in France", "url": "https://dailykiran.com/piyush-goyal-launches-upi-in-france/"},
            {"name": "Frame and Share — PM Modi at VivaTech 2026", "url": "https://frameandshare.com/pm-modi-vivatech-2026-paris-upi-deep-tech/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Galeries_Lafayette_Haussmann_1.jpg/1280px-Galeries_Lafayette_Haussmann_1.jpg",
        "image_caption": "The Galeries Lafayette department store in Paris, where India's UPI payment system has gone live",
        "image_attribution": "Wikimedia Commons",
        "body": """Indians shopping at Galeries Lafayette can now pay the way they would at a Bengaluru kirana store — by scanning a QR code from a phone. Commerce Minister Piyush Goyal switched on the Unified Payments Interface at the French retailer this week, India's second country launch of the month after Cambodia went live on June 3. The optics were diplomatic; the ambition is commercial.

UPI in France is no longer a pilot. It runs at a marquee retail destination, built on a partnership between NPCI International Payments (NIPL) and Lyra Collect, a French payments processor. Foreign Secretary Vikram Misri said the system would extend to Charles de Gaulle and Nice airports within the week. For the roughly 700,000 Indians who visit France every year, the pitch is simple: no currency to preload, no card-network fee, a direct bank-to-bank transfer at a transparent rate.

## Why this is a Visa story, not a tourism story

Strip away the ceremony and what India is exporting is a challenge to the card duopoly. When an Indian pays at Galeries Lafayette with Visa or Mastercard, those networks and the issuing bank skim a cut, and the shopper eats an opaque forex spread. UPI routes around them — bank to bank, settled in seconds, at near-zero marginal cost. NPCI now processes more than 14 billion transactions a month, worth over ₹20 lakh crore (about $240 billion). That is the volume that makes merchants and acquirers willing to plug in a foreign rail.

The France launch matters because it moves UPI past its comfort zone. The earlier corridors — UAE, Singapore, Bhutan, Nepal, Mauritius — were either diaspora-heavy or neighbourhood plays. France is mainstream European retail, and the next steps are bigger still: in November 2025 the RBI flagged plans to link UPI with the European Central Bank's TARGET Instant Payment Settlement (TIPS) platform, which would open real-time transfers across the eurozone.

## What it means for the diaspora

For an NRI in London or New Jersey who travels to Europe, this is, for now, a convenience that depends on holding an Indian bank account and a UPI app. That is the catch. UPI's international rollouts have so far been built for the *traveller from India*, not for the green-card holder in Edison who wants to send money home or pay an Indian merchant from abroad. The cross-border remittance use case — the one that would genuinely move money for the diaspora — is still mostly aspirational.

But the direction of travel is unmistakable. PM Modi used his VivaTech 2026 appearance in Paris this week to frame UPI as the centrepiece of India's digital-public-infrastructure export pitch, alongside 120 deep-tech startups parked in Nice for the 'Bharat Innovates' showcase. The subtext for diaspora professionals — many of whom build payments and fintech products in the Bay Area — is that India is positioning its DPI stack as a referenceable global standard, the way it once positioned its IT services workforce.

## The hard part is acceptance, not technology

The technology works. The bottleneck is the merchant network. A single department store is a symbol; a payments rail needs millions of acceptance points to matter. Cambodia's launch covered 4.5 million KHQR merchants because India plugged into an existing national QR standard. France has no equivalent mass-deployed QR rail, which is why the rollout reads store-by-store, airport-by-airport.

For NRI investors tracking the listed proxies — and a wave of Indian fintech IPOs is queuing up — the read-through is mixed. UPI itself generates almost no direct revenue; it is public infrastructure by design. The money is in the layer above it: the apps, lending, and merchant services that ride the rail. A globalising UPI expands the addressable market for that layer, but only if acceptance scales faster than the novelty fades.

## What's next

Watch three things. First, whether the Charles de Gaulle and Nice airport rollouts actually go live on schedule — airports are where traveller spend concentrates. Second, the ECB TIPS linkage, which is the difference between a tourist gimmick and a genuine cross-border rail. Third, whether any corridor finally cracks the remittance and diaspora-payment use case, rather than just the outbound-tourist one.

Until then, the Galeries Lafayette launch is best read as what it is: a confident, well-staged proof point in a much longer campaign to make India's plumbing the world's. For the diaspora, the practical upside is still modest. The strategic signal is loud."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Tata Just Handed BigBasket to an Amazon Veteran. The Mandate: Survive the 10-Minute War.",
        "subheadline": "Amit Nanda replaces founder Hari Menon as CEO of India's online-grocery pioneer, now bleeding cash against Blinkit, Zepto and Instamart. The hire is a tell about where Indian retail is headed.",
        "slug": make_slug("bigbasket-amit-nanda-ceo-tata-quick-commerce-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRIs who order groceries for parents in India increasingly do it through quick-commerce apps, and those tracking Tata's consumer-internet bet — or weighing the coming wave of Indian tech IPOs — have a stake in whether BigBasket's reset works.",
        "tags": ["bigbasket", "quick-commerce", "tata-digital", "indian-startups", "e-commerce", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — Bigbasket names Amit Nanda as CEO", "url": "https://www.reuters.com/business/retail-consumer/indias-bigbasket-names-former-amazon-veteran-amit-nanda-ceo-2026-06-16/"},
            {"name": "The Hindu BusinessLine — Tata hands BigBasket reins to Amit Nanda", "url": "https://www.thehindubusinessline.com/companies/tata-hands-bigbasket-reins-to-former-amazon-executive-amit-nanda/"},
            {"name": "YourStory — Hari Menon steps down as bigbasket CEO", "url": "https://yourstory.com/2026/06/hari-menon-steps-down-bigbasket-ceo-amit-nanda"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4487484/pexels-photo-4487484.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A worker sorts groceries for delivery, the contested front line of India's quick-commerce market",
        "image_attribution": "Pexels",
        "body": """When a founder who built a company for fifteen years steps aside, it is rarely just a personnel note. Tata Digital this week named Amit Nanda — an eleven-year Amazon India veteran most recently running Selling Partner Services — as CEO of BigBasket, easing co-founder Hari Menon into a mentor-and-board role. The job description is brutally specific: keep India's online-grocery pioneer relevant in a market that has moved on without it.

That market is quick commerce — the 10-minute delivery model that Blinkit, Zepto and Swiggy's Instamart have turned into the default way urban Indians buy groceries. The segment has ballooned into an $11.5 billion market in roughly five years. BigBasket, which essentially invented online grocery in India in 2011 with scheduled, next-day delivery, found itself defending an older idea.

## The numbers behind the reshuffle

The financials explain the urgency. Per Tata Sons' FY25 annual report, Innovative Retail Concepts — BigBasket's consumer-facing arm — saw operating revenue *decline* 2.7% to ₹7,673 crore, while losses widened 46% year-on-year to ₹1,850 crore. Revenue falling while losses balloon is the worst possible combination: you are spending more to stand still. That is the cost of pivoting a planned-delivery business into instant delivery, which demands dense networks of dark stores, more riders, and aggressive discounting just to hold share.

Nanda is the third senior hire in months. Tata recently elevated Seshu Kumar Tirumala to COO and brought in Arpit Jaiswal as chief growth officer. The pattern is a management team rebuilt for execution and scale rather than founding vision — and the choice of an Amazon marketplace operator, rather than a logistics or grocery lifer, signals where Tata thinks the fight will be won: selection, private labels, and seller economics, not just speed.

## Why the diaspora should care

Two reasons, one personal and one financial. The personal one: a large slice of the diaspora manages life for aging parents in India remotely, and quick-commerce apps have quietly become the tool for it — ordering medicines, groceries and essentials to a parent's door in Pune or Chennai from a phone in Sunnyvale. BigBasket, with Tata's trust halo and its strength in private-label staples, has been a natural choice for that use case. Whether it stays viable affects a genuinely practical corner of NRI life.

The financial one: Tata Digital is the group's big consumer-internet bet, and BigBasket is its anchor asset. For diaspora investors who hold Tata Group exposure or are watching India's loaded IPO pipeline, BigBasket's turnaround is a live test of whether a legacy-backed incumbent can out-execute venture-funded disruptors burning cash for growth. Eternal (Blinkit's parent) and Swiggy are already public; the quick-commerce scoreboard is increasingly a public-market story.

## The strategic bind

BigBasket's dilemma is the classic incumbent's trap. Its original advantage — large baskets, planned weekly shops, strong private brands — is precisely what quick commerce disrupts. Customers conditioned to 10-minute delivery do not plan; they impulse-order small baskets, repeatedly. Serving that behaviour profitably is the unsolved problem across the entire sector, not just for BigBasket. Even the leaders are subsidising convenience.

Nanda's Amazon pedigree is relevant here. Amazon spent years proving that marketplace breadth and logistics discipline can eventually out-economics pure speed. If BigBasket's bet is that selection, supply-chain rigor and Tata's balance sheet beat a race to the fastest delivery, that is an Amazon-flavored thesis — and it will take patient capital to prove.

## What's next

Watch the dark-store count and the loss trajectory in the next reported quarter. If BigBasket can narrow losses while holding or growing order frequency, the reset is working. If it keeps spending to chase share without closing the gap on speed, the question shifts from 'can it win' to 'how long will Tata fund it.' Either way, the appointment of an outsider operator over a founder is Tata signalling that the experimentation phase is over. Now it wants results — measured in margins, not just minutes."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Raj Subramaniam Spent Four Years Rebuilding FedEx. Tuesday's Earnings Are the First Test Without a Safety Net.",
        "subheadline": "With FedEx Freight spun off and the 'One FedEx' overhaul largely done, the Indian-origin CEO's results land as a clean read on whether the bet paid off — and what AI-driven logistics means for the workforce.",
        "slug": make_slug("fedex-raj-subramaniam-earnings-one-fedex-network-2-automation-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "FedEx is run by one of the most prominent Indian-origin CEOs in corporate America and employs thousands of Indian engineers and operations professionals; its automation push is a case study in how AI reshapes — rather than simply cuts — tech-adjacent jobs.",
        "tags": ["fedex", "raj-subramaniam", "indian-origin-ceo", "logistics-tech", "automation", "ai", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Motley Fool — FedEx Reports Earnings Tuesday", "url": "https://www.fool.com/investing/2026/06/20/fedex-reports-earnings-tuesday-is-the-delivery-gia/"},
            {"name": "Barron's — Subramaniam's One FedEx Was the Answer", "url": "https://www.barrons.com/articles/fedex-stock-raj-subramaniam-one-fedex"},
            {"name": "FinancialContent — One FedEx Reorganization Deep-Dive", "url": "https://www.financialcontent.com/article/one-fedex-88-billion-reorganization"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/04/FedEx_CEO_Raj_Subramaniam_%282023%29.jpg",
        "image_caption": "FedEx CEO Raj Subramaniam, who has led the logistics giant's 'One FedEx' restructuring since 2022",
        "image_attribution": "Wikimedia Commons",
        "body": """FedEx reports earnings on Tuesday, and for the first time in Raj Subramaniam's tenure as chief executive, there is no obvious excuse waiting in the wings. The fiscal fourth-quarter numbers will be the first to land after the June 1 spin-off of FedEx Freight — the underperforming truckload unit that activist investors had long wanted gone — and after the structural overhaul Subramaniam staked his leadership on is essentially complete.

When the Chennai-born executive succeeded founder Fred Smith in June 2022, he inherited a sprawling, slumping company with two warring halves: an air-based express network and a ground-delivery business, run as separate fiefdoms with duplicate hubs, routes and trucks. His answer was 'One FedEx' — fold air, ground and services into a single operating company. Since the day before his appointment was announced, the stock has gained roughly 102%, beating the S&P 500 by 28 points. The activists at the gate have left.

## The setup for Tuesday

The recent trajectory is genuinely strong. In the fiscal third quarter reported in March, revenue rose 8% year-over-year to $24 billion and adjusted EPS climbed 16% to $5.25, with the Federal Express segment expanding operating margin for a sixth straight quarter. Crucially, nearly half the revenue growth came from higher-margin business-to-business shipping, not consumer parcels. Management guided to about $5.80 in adjusted EPS for the fourth quarter — what would be its strongest of the year — and the full-year forecast points to roughly $18-19 in adjusted EPS.

The engine underneath is cost-cutting and automation. FedEx has now banked $1 billion in transformation savings from its Network 2.0 program, on top of the earlier $4 billion 'DRIVE' target, by stripping out redundant facilities and routes. Tuesday's report is the cleanest look yet at whether that machine throws off durable margin once Freight's drag is gone for good.

## The AI-and-jobs angle the diaspora is watching

Here is where the story matters beyond the ticker. FedEx is one of the clearest real-world cases of AI reshaping work rather than simply deleting it. Packing robots from Dexterity AI have lifted trailer utilization by up to 13%. Machine learning now turns live traffic and weather data into faster routing. This is the same automation wave that is unsettling Indian engineers across the IT-services and logistics-tech world — and FedEx is a useful counter-data point, because its restructuring has so far been about doing more with the network it has, not headline layoffs of the kind that rattled Accenture's investors last week.

For the thousands of Indian-origin engineers, data scientists and operations professionals inside FedEx and its technology arms — many in Bengaluru and Hyderabad development centres — the read-through is concrete. The roles that survive and grow are the ones that build, tune and supervise the automation: the routing models, the robotics integration, the optimization layer. The roles under pressure are the manual, duplicative ones the network is engineering away. That is the shape of the AI transition for a whole tier of diaspora tech talent, made legible in a logistics company's quarterly numbers.

## The symbolism, and the substance

Subramaniam belongs to the cohort of Indian-origin chief executives — Nadella, Pichai, Narayen, Krishna — whose ascent the diaspora tracks with a particular pride. But FedEx is a different proof point than the software giants. It is a 53-year-old industrial company with planes, trucks and warehouses, and turning it around has meant cultural surgery, not just product launches. That makes Tuesday a more revealing test of management than another cloud-revenue beat: can an Indian-origin operator run a heavy, unionized, physical-world business through a technology transition and come out leaner?

## What's next

Three things to watch. First, the headline adjusted EPS against the roughly $5.80 guide — a clean beat would validate the post-Freight structure. Second, any commentary on tariff and trade exposure; FedEx's international volumes are sensitive to the same geopolitical churn weighing on global shippers. Third, what management says about the pace of automation and Network 2.0 savings into the next fiscal year, which is the real signal on how far the AI-driven efficiency story still has to run.

If the numbers hold, Subramaniam will have done the rarest thing in corporate America: finished a multi-year turnaround on schedule, and handed himself a quarter with nothing left to blame."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
