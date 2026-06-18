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

# ---------------------------------------------------------------------------
# ARTICLE 1 — Satya Nadella "Token Capital" (Indian-origin leader / AI strategy)
# ---------------------------------------------------------------------------
body1 = """Satya Nadella has a new phrase, and he wants every company on earth to repeat it. At Microsoft's Build conference and then across a weekend of posts on X, the Hyderabad-born chief executive argued that the firms that win the AI age will not be the ones renting the smartest model. They will be the ones that own what he calls "token capital."

The word "token" has nothing to do with crypto. In Nadella's framing, every business now has two balance sheets. One is human capital — the judgment, relationships and pattern recognition of its people. The other is token capital — the AI capability a company builds and owns, the proprietary intelligence baked into systems trained on its own data and sharpened by its own feedback loops. The two, he says, compound together.

## The pitch, decoded

Strip away the elegance and the claim is older than the label. Proprietary data has been the standard explanation for a durable competitive moat since before "moat" became a boardroom cliché. What is new is who is pushing it. Microsoft sells cloud compute. If every company decides it needs its own data-powered AI capability, every company needs more Azure. The speech and the sales pitch rhyme — and Nadella, to his credit, is not subtle about putting money behind the phrase. At Build, Microsoft unveiled seven of its own AI models, a pointed signal that it is loosening its dependence on OpenAI even as both Anthropic and OpenAI march toward record IPOs.

Nadella's sharper warning is the part worth hearing. He cautioned against repeating the first era of globalisation, when entire industrial economies were hollowed out by outsourcing while headline GDP looked fine. "Let us not bring that dynamic into the AI era," he wrote, "with a small number of AI systems capturing all the economic returns, while entire industries find their knowledge commoditised right out from underneath them." A frontier without an ecosystem, he argued, is not stable.

## Why the diaspora should care

For the tens of thousands of Indian engineers inside Microsoft, Google, Amazon and the enterprise-software belt, "token capital" is not a philosophy seminar — it is a job description in transition. Nadella is explicitly arguing that human expertise becomes more valuable, not less, as AI capability grows: people set the goals, connect the dots across domains and recognise the patterns that matter. That is a far more reassuring message than the one coming out of the layoff trackers, and it lands differently for an H-1B holder watching colleagues get cut in the name of "AI-led restructuring."

It also reframes the India opportunity. The country's IT majors — TCS, Infosys, Wipro, HCLTech — have spent two years being told that agentic AI will gut the services model. Nadella's framework hands them a counter-narrative: their value is in helping clients build and own learning loops, not in renting them someone else's model. HCLTech's recent stake in Sarvam AI and Wipro's new Claude lab in Bengaluru are early bets in exactly that direction.

For the NRI investor, the tell is structural. If Nadella convinces the market that every firm needs token capital — and token capital runs on Azure — Microsoft's AI revenue stops being optional and starts being infrastructure. That is the quiet thesis underneath the buzzword.

## The catch

Even admirers note the soft spot. Capital, in the classic sense, holds its value: a factory does not require a monthly subscription. Token capital, as Nadella describes it, runs on infrastructure most companies do not own, and data has a half-life — fraud patterns evolve, regulations shift, last year's dataset goes stale. Whether proprietary data truly compounds the way he claims is the open question. For India's engineers and its IT industry, the answer will shape the next decade of work."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Satya Nadella Has a New Word for the AI Age: 'Token Capital.' It's a Warning Dressed as a Buzzword.",
    "subheadline": "Microsoft's CEO says the winners won't own the smartest model — they'll own the learning loop. For India's engineers and IT giants, that reframes the whole AI threat.",
    "slug": make_slug("satya-nadella-token-capital-ai-learning-loops-india-it-engineers"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Nadella's 'token capital' framing recasts AI as a chance for India's IT majors and the diaspora's engineers to own institutional knowledge rather than be commoditised by it — a counter-narrative to the AI-layoff panic.",
    "tags": ["satya-nadella", "microsoft", "ai", "indian-tech", "azure", "it-services"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/microsoft-ceo-calls-for-frontier-ai-ecosystem-to-ensure-broad-value-creation/article.ece"},
        {"name": "Mint", "url": "https://www.livemint.com/companies/news/microsoft-ceo-satya-nadella-issues-stark-warning-on-future-of-business-ai-firms-could-capture-all-the-value.html"},
        {"name": "Storyboard18", "url": "https://www.storyboard18.com/digital/satya-nadella-warns-against-ai-power-concentration-calls-for-firms-to-build-their-own-learning-loops.htm"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/nadella-token-capital-crypto-point/"}
    ]),
    "score_total": 80,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
    "image_caption": "Microsoft Chairman and CEO Satya Nadella, who introduced the 'token capital' framework at Build 2026",
    "image_attribution": "Wikimedia Commons",
    "body": body1,
}

# ---------------------------------------------------------------------------
# ARTICLE 2 — Adobe earnings beat + leadership vacuum (Shantanu Narayen)
# ---------------------------------------------------------------------------
body2 = """Adobe did almost everything right last quarter. Revenue hit a record $6.62 billion, up 13% and well ahead of Wall Street's $6.45 billion estimate. AI-first recurring revenue tripled past $500 million. The company raised its full-year guidance twice over. And the stock promptly fell to a seven-year low.

The disconnect is the story. On the same day it reported the numbers, Adobe disclosed that Chief Financial Officer Dan Durn was leaving — to become CFO of red-hot AI chipmaker Marvell Technology. That exit landed just three months after CEO Shantanu Narayen, the Hyderabad-born executive who has run Adobe for 18 years, announced he would step down once a successor is named. A double leadership vacuum on an earnings day was enough to overwhelm an upbeat report. Shares dropped as low as $196.90, down roughly 50% from their June 2025 peak.

## What the market is actually pricing

A CFO departure does not, by itself, erase half a company's value. The deeper fear is structural. For two years, the bear case on Adobe has been that generative AI would turn Photoshop and the rest of Creative Cloud into legacy software in a world moving to text-to-image prompts. Adobe's answer was Firefly, its in-house generative engine, whose annual recurring revenue is approaching $300 million and growing about 50% quarter over quarter.

The trouble is that Wall Street now worries Firefly is becoming table stakes rather than a moat. When frontier AI labs and rivals like Figma and Canva all ship competent image generation, the premium that subscription software has carried for a decade starts to look fragile. Adobe's pivot toward "freemium" AI services — growing users now, monetising later — only sharpened the anxiety about how, exactly, the money gets made. The stock now trades at under eight times forward earnings, cheap enough that some analysts see an entry point for anyone betting a fresh executive team can turn the AI narrative around.

## The diaspora angle

Narayen's exit matters symbolically for the Indian diaspora. He is one of the longest-serving Indian-origin CEOs in Silicon Valley, part of the cohort — alongside Satya Nadella, Sundar Pichai and Arvind Krishna — that turned "Indian-origin tech CEO" into a recognisable category. His successor search will be watched closely, and whoever takes over inherits both a $27 billion recurring-revenue base and a credibility problem with investors.

There is a more practical angle for Indian professionals, too. Adobe employs thousands of engineers in India, with a major presence in Noida and Bengaluru, and its India operations have been central to Firefly and Creative Cloud development. A company under this much market pressure tends to scrutinise costs and headcount, and the strategic uncertainty at the top filters down to product roadmaps and hiring plans that many H-1B and India-based staff depend on. The freemium pivot adds another wrinkle: a strategy built on giving away AI features to grow users assumes deep pockets and patient investors, neither of which a leaderless company commands easily.

## The CFO's destination is its own signal

Durn is not retiring — he is moving to Marvell, a company building custom AI chips for the data-center boom. That a marquee software CFO would jump to a semiconductor firm captures the moment neatly: capital, talent and narrative momentum are flowing toward the companies that make AI hardware, and away from the application-layer incumbents now scrambling to prove they cannot be disintermediated by it.

For NRI investors holding Adobe — long a portfolio staple — the question is no longer whether the company can execute. The quarter proved it can. The question is whether the market will ever again pay a premium for software whose output AI makes cheap to produce. Narayen's successor will spend the next year answering it."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Adobe Beat Earnings and Hit a 7-Year Low. The CFO Left for a Chip Company. That Tells You Everything.",
    "subheadline": "Shantanu Narayen's Adobe tripled its AI revenue and raised guidance — then watched its stock crater on a double leadership vacuum and a deeper fear about software's future.",
    "slug": make_slug("adobe-earnings-shantanu-narayen-cfo-exit-firefly-ai-software-moat"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Adobe's stumble matters to the diaspora: Narayen is among the longest-serving Indian-origin Silicon Valley CEOs, and the firm's large India engineering base and H-1B staff are exposed to the strategic uncertainty now hanging over the company.",
    "tags": ["adobe", "shantanu-narayen", "firefly", "ai", "indian-tech", "earnings"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/adobe-raises-annual-forecasts-cfo-exit-fans-uncertainty-2026-06-12/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/adobe-cfo-chip-firm-software-downfall"},
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/adobe-stock-adbe-fiscal-q2-2026-earnings/"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/adobe-is-losing-another-top-executive-and-investors-dont-like-it"}
    ]),
    "score_total": 75,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/01/Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg",
    "image_caption": "Shantanu Narayen, Adobe's chief executive of 18 years, who has announced he will step down once a successor is named",
    "image_attribution": "Wikimedia Commons",
    "body": body2,
}

# ---------------------------------------------------------------------------
# ARTICLE 3 — Indian brokerages cleared to offer US stocks via GIFT City
# ---------------------------------------------------------------------------
body3 = """For years, the easiest way for an Indian to buy a share of Apple or Nvidia was to route money through a fintech intermediary and accept the fees, the friction and the foreign-exchange paperwork. That is about to change. India's four largest retail brokerages — Zerodha, Groww, Angel One and Upstox — have received regulatory approval to offer direct access to US and international stocks through GIFT City, the country's offshore financial hub in Gujarat.

The clearance, granted by the International Financial Services Centres Authority (IFSCA), splits the firms into two camps. Zerodha and Upstox will operate as broker-dealers, routing trades through international clearing partners such as Interactive Brokers, ViewTrade and Alpaca Securities. Groww and Angel One will work under the newer Global Access Provider framework, which connects directly to US brokers for settlement. The platforms expect to launch the service within two to three months, once technology integration and compliance testing are done.

## Why this is bigger than it looks

The demand has been building for a while. Indian retail investors have grown hungry for exposure to exactly the names the diaspora knows best — AI, semiconductors, EVs and space tech — and US equity trading on Indian platforms reportedly jumped about 20% in a single day on excitement around SpaceX's anticipated public debut. Until now, that appetite was served mainly by specialists like Vested Finance and INDmoney. Putting US stocks inside the apps that already hold the brokerage accounts of tens of millions of Indians changes the scale entirely.

The GIFT City route also fixes a quiet pain point: the Global Access Provider model allows zero withdrawal fees when investors bring money back to India, and the whole structure sits inside an India-based regulatory wrapper rather than an offshore one. Under the Reserve Bank of India's Liberalised Remittance Scheme, individuals can already send up to $250,000 a year abroad, so the legal headroom for this has long existed. What was missing was a frictionless, trusted pipe.

## The NRI angle

For the diaspora, this is a two-way street worth watching. Many NRIs maintain financial lives on both sides of the ocean — a brokerage account in the US, family wealth and property in India. A cheaper, regulated channel for cross-border equity investing makes it easier for relatives in India to participate in the US market that NRIs already inhabit, and it deepens the financial bridge between the two countries. It also signals where India's capital markets are heading: GIFT City is quietly becoming the on-ramp for everything from global equities to wallet-based cross-border payments, with several payment companies now evaluating it for international fund transfers.

There is a strategic read here, too. As Indian households gain easy exposure to US tech megacaps, the fortunes of Silicon Valley — where so much of the diaspora works — become directly woven into the savings of the Indian middle class. An engineer at Nvidia in Santa Clara and her cousin in Pune may soon own the same stock, bought through the same kind of app. That alignment cuts both ways: a correction in US tech valuations would now ripple straight into Indian retail portfolios, not just NRI ones, broadening the country's exposure to the volatility the diaspora already lives with.

## The caveats

This is still early. The approvals are in hand, but the launches are months away, and the brokerages must finish the unglamorous work of clearing integration, compliance and testing. Currency risk, US tax-withholding rules and the LRS reporting burden do not disappear. And the established players — Vested, INDmoney, Smallcase — will not surrender the market quietly. Still, the direction is unmistakable: the wall between Indian retail savers and Wall Street is coming down, one brokerage app at a time."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Biggest Brokerages Just Got Cleared to Sell You Apple and Nvidia. The Gateway Is a City in Gujarat.",
    "subheadline": "Zerodha, Groww, Angel One and Upstox have IFSCA approval to offer direct US-stock access through GIFT City — collapsing the wall between Indian retail savers and Wall Street.",
    "slug": make_slug("india-brokerages-gift-city-us-stocks-zerodha-groww-nri-investors"),
    "category": "technology",
    "vertical": "fintech",
    "diaspora_angle": "A cheaper, regulated channel for Indians to buy US stocks deepens the financial bridge NRIs straddle daily — and ties the Indian middle class directly to the Silicon Valley fortunes the diaspora helps build.",
    "tags": ["fintech", "zerodha", "groww", "gift-city", "nri-investors", "us-stocks"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Inc42", "url": "https://inc42.com/buzz/zerodha-groww-angel-one-upstox-get-nod-enabling-users-to-buy-us-stocks-report/"},
        {"name": "Mint", "url": "https://www.livemint.com/money/personal-finance/want-to-invest-in-us-stocks-zerodha-groww-upstox-and-angel-one-get-key-approval.html"},
        {"name": "Traders Union", "url": "https://tradersunion.com/news/indian-traders-can-now-access-us-stocks-directly/"}
    ]),
    "score_total": 72,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16594725/pexels-photo-16594725.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A financial trading screen showing market charts and data",
    "image_attribution": "Pexels",
    "body": body3,
}

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
