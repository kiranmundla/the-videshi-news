#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-30 10:55 PT run. Three fresh articles across beats."""

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


# ─────────────────────────────────────────────────────────────────────────────
# ARTICLE 1: UPI Goes Live in Greece
# Beat: Digital Public Infrastructure
# ─────────────────────────────────────────────────────────────────────────────

article_1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's UPI Just Went Live in Athens. The Payment System That Replaced Cash Now Works in 10 Countries.",
    "subheadline": "Greece becomes the latest country to accept India's real-time payment rails, in a Eurobank partnership witnessed by Commerce Minister Piyush Goyal — and NRI travellers are the immediate beneficiaries.",
    "slug": make_slug("upi-live-greece-10-countries-eurobank-nri-payments"),
    "category": "technology",
    "vertical": "fintech",
    "diaspora_angle": "NRI travellers to Greece, Singapore, France, UAE, and six other countries can now pay with the same UPI apps they use at home — no currency conversion fees, no card surcharges, no cash anxiety.",
    "tags": ["upi", "digital-payments", "fintech", "nri-travel", "india-tech", "greece"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/india-launches-upi-in-greece/article69758000.ece"},
        {"name": "Outlook Business", "url": "https://business.outlookindia.com/news/upi-goes-live-in-greece-check-full-list-of-countries-accepting-indian-payments-abroad"},
        {"name": "Reuters", "url": "https://www.reuters.com/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/12935064/pexels-photo-12935064.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A person scanning a QR code with a smartphone for digital payment",
    "image_attribution": "Pexels",
    "body": """India's Unified Payments Interface went live in Greece on Tuesday, adding Athens to a list of cities where an Indian traveller can tap a phone, scan a QR code, and pay for a taverna lunch without fumbling for euros. Commerce Minister Piyush Goyal, in Athens for an official visit, watched a live demonstration of the Eurobank-NPCI International Payments Limited partnership at Eurobank's headquarters — and promptly declared it "another important milestone" for India's digital payments ecosystem.

He is not wrong, even if the phrasing is boilerplate. With Greece on board, UPI now functions in ten countries: Singapore, the United Arab Emirates, France, Mauritius, Nepal, Bhutan, Qatar, Sri Lanka, Cambodia, and Greece. For a system that processed its first transaction in 2016, the international footprint has expanded with striking speed. France's Galeries Lafayette in Nice accepted UPI just weeks ago. The Eiffel Tower has had it since 2024.

## The plumbing behind the Athens deal

The Greece rollout is built on a partnership between Eurobank, one of the country's four systemic lenders, and NPCI International Payments Limited (NIPL), the global arm of the National Payments Corporation of India. Fairfax Digital Services, led by CEO Sanjay Tugnait, facilitated the integration. The system works through merchant QR codes: Indian travellers scan, authenticate on their UPI app — Google Pay, PhonePe, Paytm, or any of the dozens of licensed providers — and the rupee-to-euro conversion happens on the backend.

Transaction costs, Goyal said, are "a fraction of conventional transfer costs." That matters. A typical Visa or Mastercard cross-border transaction carries a 1.5-3% foreign exchange markup plus a potential dynamic currency conversion surcharge. UPI's interbank settlement avoids much of that overhead, though exact merchant discount rates in Greece have not been publicly disclosed.

## Why NRIs should pay attention

Greece is not a random addition. It ranks among the top European holiday destinations for Indian tourists, with Athens, Santorini, and Mykonos drawing an estimated 150,000 Indian visitors in 2025. For the Bay Area professional planning a Mediterranean summer, or the London-based NRI booking an island-hopping itinerary, UPI availability means one fewer card to worry about and a lower currency conversion bill.

The ten-country footprint also tracks the Indian diaspora's travel and remittance corridors. Singapore and the UAE are the largest, but smaller markets like Nepal and Sri Lanka matter for the hundreds of thousands of families who send money home. Cambodia, with a growing Indian business presence, fills a Southeast Asian gap.

## The bigger picture: digital public infrastructure as export

India's government has been explicit about treating UPI as a geopolitical asset — a demonstration that a developing country can build digital infrastructure rivalling anything Silicon Valley offers. The stack underneath UPI (Aadhaar identity, the India Stack APIs, the ONDC commerce protocol) is being pitched to governments in Africa, Latin America, and Southeast Asia as a template.

Japan explored adopting UPI last year. Saudi Arabia and Turkey are in various stages of discussion. NIPL has signed agreements with payment networks in over 20 countries, though not all have gone live.

For Indian technology companies — from Infosys and TCS, which build banking software worldwide, to PhonePe and Razorpay, which run on UPI rails domestically — the protocol's international expansion creates a widening addressable market. If UPI becomes the default cross-border payment layer between India and a dozen tourist destinations, the fintech companies that build on those rails will follow.

## What comes next

The immediate question is depth. UPI's international presence is wide but shallow. In most of the ten countries, acceptance is limited to specific merchants, tourist corridors, or pilot zones. Singapore is the most mature market, with PayNow-UPI integration enabling person-to-person transfers. Everywhere else, it is primarily merchant QR-based.

Goyal's rhetoric — "technology-led solutions that create value beyond borders" — is aspirational. The proof will be in whether Indian travellers can reliably use UPI at a random Athens taxi stand, not just at Eurobank's headquarters during a ministerial demonstration. But the trajectory is clear: India is building a payment rail that works in ten countries today and, if NIPL's pipeline holds, could work in twenty within two years. For NRIs who never carry cash at home, the world is slowly catching up."""
}


# ─────────────────────────────────────────────────────────────────────────────
# ARTICLE 2: India Inc Under Ransomware Siege
# Beat: Cybersecurity
# ─────────────────────────────────────────────────────────────────────────────

article_2 = {
    "id": str(uuid.uuid4()),
    "headline": "Bajaj Got Ransomware. Tata Got Hacked. Then a Data Centre Burned Down. India Inc Had a Terrible June.",
    "subheadline": "Three cybersecurity incidents at major Indian conglomerates in three weeks have exposed the gap between India's manufacturing ambitions and its ability to protect the systems that underpin them.",
    "slug": make_slug("bajaj-tata-ransomware-data-centre-fire-india-cybersecurity"),
    "category": "technology",
    "vertical": "cybersecurity",
    "diaspora_angle": "NRI investors hold billions in Tata and Bajaj stock. NRIs working at Apple, Tesla, and Qualcomm — all Tata Electronics clients — now have to wonder whether their employer's supplier can protect their work product.",
    "tags": ["cybersecurity", "ransomware", "tata", "bajaj-auto", "data-breach", "indian-industry"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters — Bajaj Auto ransomware", "url": "https://www.reuters.com/technology/cybersecurity/indias-bajaj-auto-says-ransomware-attack-hits-systems-2026-06-23/"},
        {"name": "Reuters — Tata Electronics breach", "url": "https://www.reuters.com/technology/cybersecurity/apple-supplier-tata-tightens-internal-controls-after-data-breach-sources-say-2026-06-26/"},
        {"name": "Reuters — Tata Comms data centre fire", "url": "https://www.reuters.com/technology/stt-tata-delhi-data-centre-fire-leaves-clients-fearing-decades-data-lost-google-2026-06-24/"},
        {"name": "Medianama", "url": "https://www.medianama.com/2026/06/223-bajaj-auto-ransomware-cert-in-sebi/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5380603/pexels-photo-5380603.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A cybersecurity professional monitoring systems on a computer screen in low light",
    "image_attribution": "Pexels",
    "body": """June has been a month Indian conglomerates would rather forget. In the span of three weeks, a ransomware group hit Bajaj Auto, another dumped 200,000 files from Tata Electronics onto the dark web, and a fire at a Tata Communications data centre in Delhi threatened to destroy decades of client data. Separately, each incident is a headline. Together, they paint a picture of India Inc's cybersecurity infrastructure buckling under the weight of its own ambitions.

## The Bajaj hit

On June 23, at approximately 8 a.m. IST, Bajaj Auto detected a ransomware attack across its own systems and those of its wholly owned subsidiary, Bajaj Auto Technology Ltd (BATL). The company activated response protocols, notified CERT-In (India's Computer Emergency Response Team), and filed a disclosure with SEBI under listing regulations.

What Bajaj did not disclose: whether data was stolen, which systems were compromised, whether a ransom demand was made, or whether production lines were affected. By June 26, the company said manufacturing, sales, and dealer operations were "functioning normally" — but the investigation remains open.

Bajaj is the world's largest manufacturer of three-wheeled auto-rickshaws and India's second-largest motorcycle maker. It is not, by any stretch, a technology company. But its factory floors, supply chains, and dealer networks run on enterprise software that ransomware groups find irresistible. Production disruptions translate directly into financial losses — the exact leverage attackers seek.

## The Tata double blow

The Bajaj attack arrived days after a far more damaging disclosure from Tata Electronics, the Tata Group's electronics manufacturing arm and a key supplier to Apple. Ransomware group World Leaks claimed it had breached the company and published more than 200,000 files — totalling over 630 GB — on the dark web.

Reuters reviewed portions of the leaked data and found purported component design papers from Apple and Tesla, both Tata Electronics clients. At least 16 files and folders appeared linked to TSMC and 23 to Qualcomm, both of which make parts used in iPhones. Several files carried Apple's "confidential" watermark and internal code-names consistent with the iPhone 18 Pro generation.

Tata Electronics responded by restricting remote access to sensitive internal tools — purchase-order systems, supplier databases — to a select group of employees. It hired a global consultant for a forensic audit and reported the breach to the Indian government and its clients. But the damage was done. For Apple, whose entire India manufacturing strategy rests on Tata as its newest major assembler, the breach cuts at the foundation of trust.

India is on track to produce 26 percent of the world's iPhones in 2026, up from 6 percent four years ago, according to Counterpoint Research. That bet hinges on suppliers like Tata Electronics protecting Apple's most sensitive intellectual property. A 630 GB dark web dump is not a reassuring data point.

## When fire meets data

As if ransomware were not enough, a June 5 fire at a Delhi data centre jointly owned by Tata Communications and Singapore's ST Telemedia caused extensive damage to parts of the facility. Clients told Reuters they feared decades of data had been lost. Google was among the affected parties, though the extent of its exposure remains unclear.

The joint venture operates 30 data centres across 10 Indian cities and claims 300 Fortune 500 companies as clients. The fire prompted at least two clients — Matrix Cellular and Novamesh — to disclose operational disruptions and invoke force majeure provisions.

Tata Communications, navigating the fallout, has reshuffled its leadership. On Tuesday, the company named Rupesh Chokshi — formerly a senior vice president at Akamai Technologies and a veteran of AT&T — as its new CTO. It also appointed Vivek Srivastava as Executive Vice President for Cloud and Cyber Security Services. Both appointments follow the naming of a new CEO in May and a new finance chief in February.

## The pattern that should worry NRIs

For Indian-American investors who hold Tata and Bajaj stock — directly or through mutual funds with Indian exposure — the cluster of incidents raises uncomfortable questions about cybersecurity governance at India's largest industrial groups. PwC's 2026 Global Digital Trust Insights report found that 25 percent of Indian businesses suffered cyber breaches costing over $1 million in the past three years. Eighty-seven percent said they planned to increase cybersecurity spending, but the gap between intent and execution is evident.

For NRIs working at Apple, Tesla, Qualcomm, or TSMC, the Tata breach is personal. If your employer's Indian supplier cannot protect design documents for the next iPhone, that is a supply chain vulnerability that eventually reaches Cupertino's boardroom — and may influence where Apple places its next factory.

India's manufacturing ambitions are enormous: semiconductor fabs, iPhone assembly, EV production, defence electronics. All of it runs on digital infrastructure. June's triple blow is a warning that the cybersecurity layer has not kept pace with the industrial one. The new CTO at Tata Communications has his work cut out."""
}


# ─────────────────────────────────────────────────────────────────────────────
# ARTICLE 3: Indian IT Stocks Hit Multi-Year Lows
# Beat: Indian IT / NRI Investors
# ─────────────────────────────────────────────────────────────────────────────

article_3 = {
    "id": str(uuid.uuid4()),
    "headline": "Infosys Just Touched ₹1,000. TCS Lost ₹2,050. The Worst IT Selloff Since Covid Has a Familiar Villain.",
    "subheadline": "Every major Indian IT stock fell 2-3.5% on Tuesday as AI deflation, weak guidance, and a global spending freeze converge. NRI investors who held through the pandemic may be staring at round-trip returns.",
    "slug": make_slug("infosys-1000-tcs-2050-indian-it-selloff-ai-deflation"),
    "category": "technology",
    "vertical": "indian-it",
    "diaspora_angle": "Indian IT stocks are among the most widely held equities by NRI investors. TCS and Infosys are also among the largest employers of H-1B workers in the US — when their stock craters, hiring freezes follow.",
    "tags": ["indian-it", "infosys", "tcs", "wipro", "hcltech", "stock-market", "ai-deflation", "nri-investors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "MarketWatch — TCS falls below Rs 2,050", "url": "https://www.marketwatch.com/investing/stock/tcs?countrycode=in"},
        {"name": "Analytics Insight — TCS selloff", "url": "https://www.analyticsinsight.net/stock-market/tcs-falls-below-rs-2050-as-it-stocks-extend-decline"},
        {"name": "People Matters — JP Morgan on Indian IT", "url": "https://www.peoplematters.in/article/technology/as-ai-slows-it-growth-jp-morgan-expects-tcs-and-infosys-to-outperform-wipro-hcl-tech-46207"},
        {"name": "Trade Brains — Infosys analysis", "url": "https://tradebrains.in/infosys-shares-crashed-can-it-reach-2000/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/35118208/pexels-photo-35118208.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A stock market chart displaying a bearish trend with red candlesticks",
    "image_attribution": "Pexels",
    "body": """On Tuesday, Infosys shares closed at ₹1,000.60 — a number that carries more symbolism than any quarterly earnings report. The stock has now fallen 42 percent from its 52-week high of ₹1,727.85, reached barely five months ago. It is back to levels not seen since the depths of the pandemic sell-off.

It had company. TCS dropped 3.17 percent to ₹2,034, breaching the ₹2,050 level and sitting 42 percent below its own peak of ₹3,489.85. Wipro fell 2.91 percent. HCLTech shed 2.78 percent. Tech Mahindra declined 2.08 percent. The Nifty IT index, already the worst-performing sector of 2026, extended its losses on a day when the broader Sensex dipped just 0.33 percent. This is not a market-wide rout. This is an IT-specific problem.

## AI giveth, AI taketh away

The culprit is not a surprise. Artificial intelligence is simultaneously the sector's biggest opportunity and its most immediate threat — and right now, the threat is winning.

JP Morgan's latest analysis, released this week, describes Indian IT as stuck in the "deflation phase" of AI adoption: productivity gains from AI tools are reducing demand for traditional IT services faster than new AI-related revenue is materialising. The brokerage expects large Indian IT firms to deliver only 3-4 percent medium-term revenue growth, well below the mid-single-digit rates the industry has historically targeted.

The math is straightforward. When AI tools can generate code, automate testing, and accelerate deployment, clients need fewer billable hours from their IT vendors. An enterprise that once engaged a 200-person offshore team for a system migration might now need 140. The project still happens; the revenue shrinks.

JP Morgan expects Infosys, HCLTech, and Wipro to either lower or soften their FY27 revenue guidance, following weaker numbers from Accenture — the bellwether for global IT spending trends. The brokerage favours TCS and Infosys over HCLTech and Wipro, but even the preferred names are under pressure.

## The numbers behind the carnage

The scale of the decline is striking. Indian IT stocks have collectively shed roughly $26 billion in market value in 2026. TCS, which posted its first annual revenue decline in more than two decades last quarter, is now trading at its lowest point in over a year. Infosys, despite winning large deals and investing heavily in AI consulting capabilities, has seen its stock halve.

Wipro, at ₹170, is 38 percent below its 52-week high. HCLTech, at ₹1,072, is down 39 percent. Even Persistent Systems, which briefly surged on the back of its ₹8,300-crore Nagarro acquisition, gave back 11.2 percent in a single session this week as analysts flagged integration risks.

The sector employs approximately 5.9 million people in India, with hundreds of thousands more on H-1B and L-1 visas in the United States. When these companies freeze hiring or restructure, the downstream effects reach visa holders in New Jersey, Sunnyvale, and Plano.

## Why NRI portfolios are bleeding

Indian IT stocks are among the most popular holdings for NRI investors, particularly those in the US technology sector. The logic was always intuitive: buy what you know, invest in the companies that employ your friends and former classmates, benefit from rupee-dollar dynamics.

That logic has inverted. The falling rupee, which should boost IT revenues (denominated in dollars but reported in rupees), has not been enough to offset volume declines. And for NRIs holding these stocks in rupee-denominated demat accounts, the dollar-adjusted returns are even worse.

Institutional investors, meanwhile, are rotating out. Domestic mutual funds and foreign institutional investors are moving capital toward banking, defence, capital goods, and infrastructure — sectors with greater visibility on domestic earnings. Technology, with its export dependency and AI uncertainty, is being left behind.

## The case for patience — and the case against

Bulls argue that valuations have corrected enough to make the sector interesting. TCS trades at roughly 22 times forward earnings, down from 30-plus earlier in the year. Infosys, at around 18 times, is approaching levels that historically attracted value buyers.

But valuation floors are meaningless without a catalyst. The June-quarter earnings season, set to begin in mid-July, will be critical. If managements offer conservative guidance for a third consecutive quarter, the selloff could deepen. If discretionary spending shows any signs of recovery — particularly in banking and financial services, the largest revenue vertical — the bottom could form.

For the Indian engineer at Google watching her demat account, the question is not whether Indian IT will survive AI. It will. The question is whether the transition from labour arbitrage to AI-powered services happens fast enough to justify current prices, or whether the market is correctly pricing in a prolonged structural reset. Tuesday's closing prices suggest the market has chosen the bleaker interpretation."""
}


# ─────────────────────────────────────────────────────────────────────────────
# Insert all articles
# ─────────────────────────────────────────────────────────────────────────────

articles = [article_1, article_2, article_3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
