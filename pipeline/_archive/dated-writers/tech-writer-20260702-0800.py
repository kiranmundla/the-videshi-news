#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-02 08:00 PT"""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ─────────────────────────────────────────────────────────────────────────
# ARTICLE 1 — Kunal Shah / WhatsApp / Meta-CRED Deal
# ─────────────────────────────────────────────────────────────────────────

art1_body = """Meta has handed the keys to WhatsApp — the messaging service used by three billion people — to an Indian founder most Americans have never heard of. Kunal Shah, who built the fintech platform CRED from a $1 million personal bet into a company valued at $4.5 billion, will replace Will Cathcart as WhatsApp's global head. The move came alongside Meta's $900 million investment in CRED for a roughly 20 per cent stake, the largest bet Mark Zuckerberg has made on an Indian startup.

Shah's appointment is not a ceremonial handover. Within days of taking the job, he announced WhatsApp's biggest identity shift in years: usernames. Starting June 29, the platform began allowing users to reserve unique handles, enabling connections without sharing phone numbers. It is a privacy play that positions WhatsApp against Telegram and Signal, and it landed with the unmistakable energy of a founder who has things to build.

## The CRED Playbook

Shah's trajectory reads like a case study in compounding bets. He co-founded FreeCharge, sold it to Snapdeal for roughly $400 million in 2015, spent three years investing and learning, then launched CRED in 2018 with a deceptively simple idea: reward people for paying their credit card bills on time. Between 2019 and 2025, the platform grew to 17 million members, expanded into lending, insurance, commerce and wealth management, and scaled annual revenue to approximately $325 million. CRED posted its first profitable quarter in 2026 — a milestone that matters because it came before Shah left, not after.

Miten Sampat, who has led strategy and finance since 2020, takes over as interim CEO. Shah remains a shareholder.

## Why Meta Wants a Fintech Brain

The strategic logic is blunt. WhatsApp has 860 million users in India alone — a market where UPI processes more than 750 million transactions a day. Despite that massive base, WhatsApp's commerce and payments ambitions have progressed in fits and starts. Meta needs someone who understands high-frequency transactions, consumer credit behaviour, and the regulatory maze of Indian fintech. Shah is that person.

"The delta between WhatsApp today and its full potential is massive," Shah wrote in his announcement. That phrasing — the language of unlocked value and unrealised TAM — tells you exactly how he sees the job.

## What NRIs Should Watch

For Indian Americans, this appointment carries a significance that extends beyond corporate musical chairs. Shah becomes one of the most powerful Indian-origin executives in Silicon Valley, running a product that virtually every NRI uses to stay connected with family back home. His fintech instincts could reshape how remittances, merchant payments and cross-border commerce work inside WhatsApp — services the diaspora would use daily.

The username feature alone matters to NRIs who share WhatsApp contacts in professional settings, community groups and neighbourhood forums without wanting to hand over personal phone numbers. No public directory will exist; users must know the exact handle to connect.

Meta has stated that its CRED investment comes with no access to member data. Whether that boundary holds as the two companies' product roadmaps inevitably converge will be worth watching closely."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "CRED's Kunal Shah Is Now Running WhatsApp. His First Move Was Killing the Phone Number.",
    "subheadline": "Meta invested $900 million in Shah's fintech startup, then put him in charge of its three-billion-user messaging app. Within days, he launched usernames.",
    "slug": make_slug("kunal-shah-whatsapp-ceo-meta-cred-usernames"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Shah becomes one of the most powerful Indian-origin tech executives globally, running the app most NRIs use daily to connect with family — and his fintech background could reshape how diaspora remittances and payments work inside WhatsApp.",
    "tags": ["whatsapp", "meta", "cred", "kunal-shah", "fintech", "indian-tech-leaders"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/22/cred-founder-kunal-shah-to-lead-whatsapp-globally/"},
        {"name": "Livemint", "url": "https://www.livemint.com/companies/news/cred-founder-kunal-shah-to-lead-whatsapp-as-meta-invests-rs-8550-crore-in-the-fintech-startup-11750613204937.html"},
        {"name": "TechRepublic", "url": "https://www.techrepublic.com/article/meta-cred-investment-kunal-shah-whatsapp/"},
        {"name": "Storyboard18", "url": "https://www.storyboard18.com/technology/kunal-shah-announces-whatsapp-usernames-as-platform-moves-beyond-phone-numbers-50942.htm"},
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/83/Kunal_Shah_in_FreeCharge_T-Shirt_%28cropped%29.jpg",
    "image_caption": "Kunal Shah, founder of CRED and new global head of WhatsApp",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}

# ─────────────────────────────────────────────────────────────────────────
# ARTICLE 2 — Nikesh Arora / Palo Alto Networks
# ─────────────────────────────────────────────────────────────────────────

art2_body = """Nikesh Arora's Palo Alto Networks just crossed $3 billion in quarterly revenue for the first time, beating Wall Street estimates by $60 million. The stock responded by hitting a new 52-week high above $358, and at least four major banks raised their price targets in a single week — Wells Fargo to $420, Arete Research to $433, BNP Paribas to $380, BTIG to $380. Over the past six months, the stock has outperformed the cybersecurity sector by nearly 14 percentage points.

For the Indian-American executive who left Google, spent two bruising years at SoftBank, and was once written off by the tech press, the numbers amount to vindication on a scale that is hard to argue with.

## The Quarter That Changed the Math

Palo Alto's fiscal Q3 2026 results, reported on June 2, beat on every metric that matters. Revenue rose 31.1 per cent year-over-year to $3 billion. Adjusted earnings per share came in at $0.85, topping the $0.79 consensus by six cents. The company raised its full-year revenue guidance to $11.42 billion and its EPS guidance to $3.77–$3.79.

The deeper story is in next-generation security annual recurring revenue, which now stands at $8.1 billion. Prisma AIRS — the company's AI-powered security product — grew its customer base to 300, and management expects it to surpass $100 million in ARR within two quarters. Observability revenue, bolstered by a single AI frontier lab contract worth more than $200 million, crossed $300 million.

Free cash flow hit $788 million in the quarter, even as the company posted a GAAP operating loss of $183 million. Investors are choosing to look at the cash, not the accounting.

## The AI-Security Flywheel

Arora's thesis from day one has been platformisation: convince enterprises to consolidate their patchwork of security vendors onto a single Palo Alto platform. The AI boom has turbocharged that pitch. As companies deploy large language models, the attack surface expands — and so does the urgency to secure it. Palo Alto now counts two of the top five frontier AI labs as customers.

"AI-driven cyber threats are expected to accelerate enterprise cybersecurity spending," the company noted in its guidance. That is not a prediction; it is already visible in the pipeline. Analysts at Zacks described the shift as "platformisation translating into larger commitments."

## What It Means for Indian Tech Professionals

Arora's run matters beyond the stock ticker. Born in Ghaziabad, educated at IIT Varanasi, he is now running a $287 billion cybersecurity empire at a moment when the industry is one of the fastest-growing employers of Indian-origin engineers. Palo Alto Networks has significant engineering operations in India, and the broader cybersecurity sector is absorbing Indian talent at every level — from SOC analysts to AI researchers.

For NRI investors, PANW's 60 per cent year-to-date rally has already created significant wealth. The question now is whether integration risk from the CyberArk and Chronosphere acquisitions — which contributed $388 million to the quarter — will produce durable organic growth or a one-time revenue bump. Arora's track record suggests he knows the difference.

The next earnings report lands August 17. By then, the market will expect proof that the platform thesis generates recurring growth, not just recurring headlines."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Nikesh Arora's Palo Alto Networks Just Hit $3 Billion in Quarterly Revenue. Four Banks Raised Their Targets in a Week.",
    "subheadline": "The Indian-American CEO's cybersecurity company posted a 31% revenue jump, hit a 52-week high, and is now valued at $287 billion. AI threats are the tailwind.",
    "slug": make_slug("nikesh-arora-palo-alto-networks-3b-revenue-ai-security"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Arora — IIT Varanasi, ex-Google — is running a $287B cybersecurity empire at a time when the sector is one of the fastest-growing employers of Indian-origin engineers, and the stock's 60% YTD rally has created significant wealth for NRI investors.",
    "tags": ["palo-alto-networks", "nikesh-arora", "cybersecurity", "ai-security", "indian-tech-leaders", "earnings"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/PANW/earnings/"},
        {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/palo-alto-networks-panw-gains-momentum-in-ai-security-and-observability-1476931/"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/palo-alto-and-tenable-are-soaring-heres-the-11-4-billion-ai-cyber-bet-investors-need-to-understand/"},
        {"name": "Zacks", "url": "https://www.zacks.com/stock/news/2441389/the-zacks-analyst-blog-highlights-caterpillar-palo-alto-networks-toyota-motor-and-precipio"},
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
    "image_caption": "Nikesh Arora, chairman and CEO of Palo Alto Networks, at TechCrunch Disrupt",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}

# ─────────────────────────────────────────────────────────────────────────
# ARTICLE 3 — Indian Startup Funding H1 2026
# ─────────────────────────────────────────────────────────────────────────

art3_body = """India's startups raised $5.2 billion across 501 deals in the first half of 2026, according to Inc42's latest funding report. The total is down 9 per cent from the $5.7 billion raised in H1 2025 — but the headline number obscures a more interesting story. Deal volume actually rose 7 per cent year-over-year, and the ecosystem minted five new unicorns: AI startup Sarvam, payments firm JusPay, digital lender KreditBee, proptech major Square Yards, and rocket maker Skyroot Aerospace. A separate tally by Entrackr, which includes CRED's $900 million Meta investment, puts the half-year total closer to $7.4 billion.

The divergence between fewer mega-rounds and more overall deals is the defining pattern. Only four funding rounds exceeded $100 million — down from 11 in H1 2025 — while median ticket sizes held steady at $3 million. This is what maturation looks like, not retreat.

## AI Takes the Crown

If H1 2025 belonged to fintech, H1 2026 belonged to artificial intelligence. AI startups pulled in $676 million across 57 deals, a 317 per cent year-over-year surge in funding and a near-doubling in deal volume. Sarvam's $234 million Series B, led by HCLTech at a $1.5 billion valuation, was the marquee transaction — and a signal that India's sovereign AI ambitions have real institutional backing. The government's IndiaAI Mission, which supports compute infrastructure and indigenous model development, has stiffened investor confidence.

Deeptech followed closely, with $365 million raised across 66 deals, up 17 per cent and 53 per cent respectively. Skyroot's $60 million unicorn round underlined the expanding definition of what counts as an investable Indian tech company.

## Bengaluru Dominates, Late-Stage Shrinks

Bengaluru attracted $2.7 billion — more than half the country's total startup funding — across 165 deals. Delhi NCR came second at $917 million despite a 39 per cent year-over-year correction, while Mumbai raised $587 million.

The sharpest correction came at the late stage. Funding for mature startups fell 27 per cent to $2.2 billion, and the median late-stage cheque dropped 68 per cent to $10 million. Investors are writing smaller, more disciplined tickets. Growth-stage startups were the beneficiaries: Series A and B funding climbed 15 per cent to $2.3 billion across 190 transactions. Seed-stage funding bucked the broader trend entirely, rising 18 per cent to $478 million.

"The decline in overall funding quantum reflects a genuine macro-driven recalibration — a higher cost of capital globally, LP caution on emerging markets, and a natural correction after the exuberance of 2021–22," said Vikram Gupta, managing partner at IvyCap Ventures. "But beneath that, the rise in deal volume tells a different story."

## M&A Over IPOs

Indian startups recorded 52 M&A deals in H1 2026, broadly in line with last year but significantly above H2 2025. Meanwhile, IPO activity stayed subdued. According to Inc42's investor survey, secondary buyouts and strategic M&A are expected to dominate startup exits for the next two years. This is particularly relevant for cross-border acquisitions, where Indian AI and deeptech firms are increasingly attractive targets.

The listed startup ecosystem offered one bright spot: 75 per cent of India's publicly traded startups are now profitable, and the New Age Tech Index outperformed the Nifty 50 by 8.5 percentage points.

## Why NRIs Should Care

For diaspora investors tracking India's tech scene, the numbers suggest a market that has shed the 2021 froth without losing its engine. AI and deeptech are absorbing the capital that once chased food delivery and ed-tech. Five new unicorns in six months — at a pace that could yield eight to ten for the full year — tell a story of sustained, if more selective, momentum. The question is whether the IPO pipeline (OYO, Zepto, Razorpay, Zetwerk are all reportedly preparing) will open in H2 and provide the liquidity events that VCs and their LPs are demanding."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India Minted Five Unicorns in Six Months. The Money Is Moving to AI.",
    "subheadline": "Indian startups raised $5.2 billion in H1 2026. Overall funding fell 9%, but AI investment surged 317% and deal volume hit a new high.",
    "slug": make_slug("india-startup-funding-h1-2026-unicorns-ai-surge"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI investors tracking India's tech market will find a maturing ecosystem: five new unicorns, AI absorbing the capital that once chased food delivery, and an IPO pipeline (OYO, Zepto, Razorpay) that could unlock diaspora investment opportunities in H2.",
    "tags": ["indian-startups", "unicorns", "ai-funding", "venture-capital", "bengaluru", "sarvam-ai"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Inc42", "url": "https://inc42.com/buzz/indian-startup-funding-slips-9-to-5-2-bn-in-h1-2026/"},
        {"name": "Entrackr", "url": "https://entrackr.com/2026/07/indian-startups-raise-7-4-bn-in-h1-2026-as-cred-meta-deal-lifts-funding/"},
        {"name": "Inc42 Unicorn Tracker", "url": "https://inc42.com/indian-startup-unicorns/"},
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/1b/ITPL-Whitefield-Bangalore1.jpg",
    "image_caption": "International Tech Park in Whitefield, Bengaluru — India's startup capital attracted over half of H1 2026 funding",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip(),
}

# ─────────────────────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
