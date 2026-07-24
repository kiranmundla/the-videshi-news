#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-03 22:00 PT run"""

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
        "headline": "Tesla Just Had Its Best Quarter in Two Years. Wall Street Sold It Anyway.",
        "subheadline": "Record Q2 deliveries of 480,126 EVs crushed estimates by 20%. The stock dropped 7.5%. For NRI investors riding two years of declines, here's what the numbers actually say.",
        "slug": make_slug("tesla-record-q2-deliveries-stock-drop-nri-investors"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Tesla is among the most widely held stocks by Indian-American retail investors. The Q2 beat-and-drop pattern offers a case study in sell-the-news dynamics that NRIs with TSLA in their portfolios should understand.",
        "tags": ["tesla", "ev", "nri-investors", "wall-street", "electric-vehicles"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/autos-transportation/tesla-quarterly-deliveries-set-record-european-recovery-raises-hopes-annual-growth-2026-07-03/"},
            {"name": "CNN Business", "url": "https://www.cnn.com/2026/07/03/business/tesla-sales-second-quarter/index.html"},
            {"name": "Fox Business", "url": "https://www.foxbusiness.com/markets/tesla-deliveries-beat-forecasts-europe-rebound-brightens-outlook"},
            {"name": "Electrek", "url": "https://electrek.co/2026/07/03/tesla-tsla-q2-2026-deliveries/"},
            {"name": "InsideEVs", "url": "https://insideevs.com/news/byd-reclaimed-ev-sales-crown-despite-teslas-huge-quarter/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Tesla_Model_Y_Front_View.jpg/1280px-Tesla_Model_Y_Front_View.jpg",
        "image_caption": "Tesla Model Y, the company's bestselling vehicle that drove the bulk of Q2 2026 deliveries",
        "image_attribution": "Wikimedia Commons",
        "body": """Tesla delivered 480,126 electric vehicles in the second quarter of 2026 — a record for the period, up 25% from a year earlier, and roughly 78,000 units above Wall Street's consensus estimate. Then the stock fell 7.5%.

Welcome to the world's most expensive lesson in how markets actually work.

## The numbers that mattered

The headline figure is unambiguous. Tesla's Q2 deliveries smashed the 402,776-vehicle consensus tracked by Visible Alpha, and the company-compiled analyst forecast of 406,024. The Model 3 and Model Y accounted for 467,762 of those deliveries, with the remaining 12,364 spread across the Cybertruck, Model S, and Model X.

More importantly, Tesla delivered about 28,000 more vehicles than it produced — reversing a troubling Q1 trend where it built 50,000 units it could not sell. Inventory is coming down. That is the kind of signal analysts track far more closely than the delivery number itself.

The rebound was powered by Europe, where Tesla's registrations surged 77% through the first five months of the year, according to the European Automobile Manufacturers' Association. Higher fuel prices, new government EV incentives, and a measurable easing of the consumer backlash against Elon Musk's politics all contributed. "Europe is in bounce-back mode," said Dan Ives, global head of technology research at Wedbush Securities.

## So why did the stock fall?

The short answer: TSLA shares had already climbed 12% earlier in the week in anticipation of strong numbers. By the time the report landed, the good news was priced in. Traders sold into the beat — a textbook "buy the rumour, sell the news" pattern that repeats across earnings seasons.

Seth Goldstein, senior equity analyst at Morningstar, noted that while a third straight annual decline now seems "very hard to see," the stock's $1.6 trillion valuation still bakes in ambitious assumptions about robotaxis, the Optimus humanoid robot, and Tesla's AI infrastructure push, where the company plans to spend more than $25 billion in capital expenditure this year — triple the 2025 level.

Tesla also launched the six-seat Model Y L in the US on the same day, priced at $61,990. Already available in China and parts of Asia-Pacific, the longer-wheelbase variant is designed to capture buyers who might have considered the discontinued Model X.

## The BYD shadow

Even a record quarter was not enough to keep the crown. China's BYD delivered 557,090 fully electric vehicles over the same period, reclaiming the title of the world's largest EV maker by nearly 77,000 units. BYD has a full lineup across multiple price points and brands; Tesla leans on just two models for the vast majority of its volume.

When plug-in hybrids are included, BYD has sold roughly 1.8 million vehicles so far this year. The gap is structural, not cyclical.

## What NRI investors should know

Tesla remains one of the most widely held stocks among Indian-American retail investors, drawn by the company's cultural cachet and Musk's outsized presence in the tech imagination. The Q2 beat validates the car business — Tesla's core — at a time when the market was pricing in continued decline.

But the stock's valuation is not really about cars. It is about whether robotaxis in Austin scale beyond a limited pilot, whether Optimus robots become commercially viable, and whether Tesla's $25 billion AI infrastructure spend generates returns that justify a market cap nearly 100 times its trailing earnings. At Thursday's close of $393.45, TSLA is still down for the year while the S&P 500 is up nearly 10%.

For NRIs with TSLA in their portfolios, the message is straightforward: the operational turnaround is real, but the price already reflected it. The stock moves from here will depend on things that have nothing to do with how many Model Ys rolled off the line in Fremont."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Central Bank Told Parliament: Don't Legalize Crypto. Not Now, Not Yet.",
        "subheadline": "The RBI warned the Standing Committee on Finance that virtual digital assets threaten India's economy and should remain outside the formal financial system — even as the country leads the world in crypto adoption.",
        "slug": make_slug("rbi-parliament-crypto-vda-ban-nri-india"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Millions of NRIs hold crypto assets and face uncertainty over India's regulatory direction. The RBI's stance directly affects repatriation, taxation, and the viability of crypto-linked fintech investments tied to India.",
        "tags": ["cryptocurrency", "rbi", "regulation", "india-fintech", "digital-rupee", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/rbi-tells-par-panel-that-virtual-digital-assets-like-cryptocurrency-a-threat-to-economy"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/rbi-tells-parliamentary-panel-that-crypto-should-not-be-legalised-in-india/article69760082.ece"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/cryptocurrency/crypto-news-today-rbi-opposes-crypto-legalisation-over-risks-to-indias-economy"},
            {"name": "Traders Union", "url": "https://tradersunion.com/currencies/news/india-moves-to-isolate-banking-sector-from-cryptocurrencies/"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/cryptocurrency/rbi-reiterates-opposition-to-legalising-cryptocurrency-in-india-flags-risks-to-economy"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Mumbai%2C_reserve_bank_of_india_02.jpg/1280px-Mumbai%2C_reserve_bank_of_india_02.jpg",
        "image_caption": "The Reserve Bank of India headquarters in Mumbai, where the central bank's crypto stance was formulated",
        "image_attribution": "Wikimedia Commons",
        "body": """The Reserve Bank of India walked into the Parliamentary Standing Committee on Finance on July 2 and said what it has been saying for years, only louder: virtual digital assets like cryptocurrency are a threat to India's economy and should not be legalised.

The difference this time is that Parliament appears to be listening.

## What the RBI told lawmakers

The committee, chaired by BJP MP Bhartruhari Mahtab, convened three sessions dedicated to a single topic — "Virtual Digital Assets and Way Forward." The RBI's representatives used the first session to lay out a blunt case.

Cryptocurrencies, they argued, could be exploited for terror financing, narcotics smuggling, and money laundering. Offshore crypto entities operating beyond Indian regulatory reach make monitoring "very difficult," the RBI said. And legalising private digital assets at this stage could create a false sense of security among retail investors — a population the central bank has long tried to protect from speculative instruments.

The RBI pointed to China and Qatar as jurisdictions that have banned crypto outright, and to Europe's Markets in Crypto-Assets (MiCA) framework as an example of stringent regulation that allows VDAs only under heavy compliance burdens.

After the meeting, Mahtab confirmed the RBI's position to reporters: the central bank is firmly against legalisation.

## The ICAI wants a middle path

The Institute of Chartered Accountants of India, which testified in the second session, took a softer stance. The ICAI told the committee it supports a comprehensive VDA law — not a ban, but a framework that establishes clear accounting standards, financial disclosure requirements, and compliance guidelines for entities that deal in digital assets.

The distinction matters. India already taxes crypto gains at 30% (plus a 1% TDS on transactions above ₹50,000), but without a dedicated legal framework, enforcement is uneven and disputes are piling up. The ICAI essentially told Parliament: if you are going to tax it, you need to define it.

## India's crypto paradox

Here is the awkward truth the RBI did not dwell on. India ranked first in Chainalysis's 2025 Global Crypto Adoption Index. Millions of Indians — and a substantial number of NRIs — trade crypto through platforms like WazirX, CoinDCX, and Mudrex, or via global exchanges like Binance and Coinbase.

The RBI itself questioned the methodology behind private-sector adoption rankings, according to reports. But the underlying reality is difficult to dismiss: India has one of the world's largest crypto user bases, driven by a young, tech-savvy population and remittance corridors that traditional banking makes slow and expensive.

The central bank's parallel bet is the digital rupee. India continues piloting its central bank digital currency (CBDC), which would offer the speed of crypto without the decentralisation that makes regulators nervous. But the digital rupee pilot has been modest in scope, and adoption has not approached the grassroots enthusiasm that private crypto enjoys.

## What this means for NRIs

The RBI's position has immediate implications for the Indian diaspora.

NRIs who hold crypto assets face a regulatory grey zone when repatriating gains to India. The 30% flat tax on crypto income applies regardless of residency for Indian-source income, but the lack of a legal framework creates ambiguity around what constitutes "Indian-source" for an asset class that exists on a global blockchain.

For NRIs investing in India-focused crypto and Web3 startups — several of which raised significant rounds in 2025 and early 2026 — the RBI's stance signals continued regulatory headwinds. India's crypto exchanges have already seen a migration of trading volumes to offshore platforms following the TDS rules, and a formal non-legalisation stance makes that trend unlikely to reverse.

Perhaps most significantly, the RBI's recommendation to isolate the banking sector from crypto means that mainstream financial products integrating digital assets — crypto-backed lending, tokenised mutual funds, blockchain-based cross-border payments — remain effectively blocked in India. European and Singaporean regulators have moved in the opposite direction, creating a growing gap in where fintech innovation can happen.

## The road ahead

The Standing Committee will now synthesise the RBI and ICAI testimonies into a report that could shape India's first comprehensive digital asset policy. The committee has held seven meetings on the subject so far — an unusually thorough process that suggests lawmakers take the issue seriously, even if they have not yet decided how seriously to take the RBI's maximalist stance.

For the millions of Indians and NRIs who already hold crypto, the question is not whether regulation is coming. It is whether that regulation will look more like Europe's guarded permission or China's outright prohibition. After July 2, the needle has moved toward the latter."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
